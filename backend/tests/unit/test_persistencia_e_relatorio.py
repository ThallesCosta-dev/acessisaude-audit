"""Persistência, exportação e relatório.

O foco é a propriedade que sustenta a reprodutibilidade do estudo: **o
documento JSON é a fonte da verdade, e o índice relacional é integralmente
derivável dele**. Se isso deixar de valer, mudar o cálculo de um índice passaria
a exigir revarrer os portais.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import ScanResult
from acessisaude_audit.domain.scoring import score_scan
from acessisaude_audit.persistence.database import (
    create_database_engine,
    init_database,
    make_session_factory,
    session_scope,
)
from acessisaude_audit.persistence.repositories import JsonScanStore, ScanRepository
from acessisaude_audit.reporting.exports import export_findings_csv, export_pages_csv
from acessisaude_audit.reporting.html import render_report


@pytest.fixture
def repositorio(settings: Settings):
    """Repositório sobre banco temporário."""
    settings.ensure_directories()
    engine = create_database_engine(settings.resolved_database_url())
    init_database(engine)
    factory = make_session_factory(engine)
    with session_scope(factory) as session:
        yield ScanRepository(session, params=settings.scoring_parameters())
    engine.dispose()


class TestArmazenamentoJson:
    def test_ida_e_volta_preserva_o_documento(
        self, sample_scan: ScanResult, tmp_path: Path
    ) -> None:
        """O JSON é o artefato de pesquisa: nada pode se perder na serialização."""
        store = JsonScanStore(tmp_path)
        path = store.save(sample_scan)
        recarregado = store.load(path)

        assert recarregado.id == sample_scan.id
        assert recarregado.page_count == sample_scan.page_count
        assert recarregado.violation_count == sample_scan.violation_count
        assert recarregado.pages[0].network.total_bytes == sample_scan.pages[0].network.total_bytes

    def test_indices_sao_estaveis_apos_recarga(
        self, sample_scan: ScanResult, tmp_path: Path
    ) -> None:
        """Um número publicado precisa sobreviver a um ciclo de gravação e leitura."""
        store = JsonScanStore(tmp_path)
        recarregado = store.load(store.save(sample_scan))
        assert score_scan(recarregado).model_dump() == score_scan(sample_scan).model_dump()

    def test_nome_de_arquivo_e_ordenavel_e_legivel(
        self, sample_scan: ScanResult, tmp_path: Path
    ) -> None:
        path = JsonScanStore(tmp_path).path_for(sample_scan)
        assert path.name.startswith("alvo-teste__")
        assert path.suffix == ".json"


class TestRepositorio:
    def test_grava_e_recupera(self, repositorio: ScanRepository, sample_scan: ScanResult) -> None:
        repositorio.save(sample_scan, sphere="municipal")
        recuperado = repositorio.get(str(sample_scan.id))
        assert recuperado is not None
        assert recuperado.target_id == sample_scan.target_id

    def test_indice_achatado_e_consistente_com_o_documento(
        self, repositorio: ScanRepository, sample_scan: ScanResult
    ) -> None:
        row = repositorio.save(sample_scan, sphere="municipal")
        score = score_scan(sample_scan)

        assert row.violation_count == sample_scan.violation_count
        assert row.conformance_index == score.conformance_index
        assert row.absolute_barrier == score.absolute_barrier
        assert row.loss_rate == sample_scan.loss_rate

    def test_reindexacao_reconstroi_a_partir_do_documento(
        self, repositorio: ScanRepository, sample_scan: ScanResult
    ) -> None:
        """A propriedade que torna operacional a promessa de fonte única da verdade.

        Se o cálculo de índices mudar, basta reindexar — nenhum portal precisa
        ser varrido de novo.
        """
        original = repositorio.save(sample_scan, sphere="municipal")
        indice_original = original.conformance_index

        reindexado = repositorio.reindex(str(sample_scan.id))
        assert reindexado is not None
        assert reindexado.conformance_index == indice_original
        assert reindexado.violation_count == original.violation_count

    def test_frequencia_de_criterios(
        self, repositorio: ScanRepository, sample_scan: ScanResult
    ) -> None:
        repositorio.save(sample_scan, sphere="municipal")
        frequencia = dict(repositorio.criterion_frequency())
        assert "1.4.3" in frequencia
        assert "2.1.1" in frequencia

    def test_exclusao_remove_do_indice(
        self, repositorio: ScanRepository, sample_scan: ScanResult
    ) -> None:
        repositorio.save(sample_scan)
        assert repositorio.delete(str(sample_scan.id)) is True
        assert repositorio.get(str(sample_scan.id)) is None

    def test_exclusao_de_inexistente_retorna_falso(self, repositorio: ScanRepository) -> None:
        assert repositorio.delete("00000000-0000-0000-0000-000000000000") is False


class TestExportacaoCsv:
    def test_achados_produzem_uma_linha_por_achado(
        self, sample_scan: ScanResult, tmp_path: Path
    ) -> None:
        path = export_findings_csv([sample_scan], tmp_path / "achados.csv")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            linhas = list(csv.DictReader(handle, delimiter=";"))

        esperado = sum(len(p.findings) for p in sample_scan.pages)
        assert len(linhas) == esperado

    def test_colunas_juridicas_estao_presentes(
        self, sample_scan: ScanResult, tmp_path: Path
    ) -> None:
        """O CSV precisa carregar as três camadas — sem elas, a análise não fecha."""
        path = export_findings_csv([sample_scan], tmp_path / "achados.csv")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            linhas = list(csv.DictReader(handle, delimiter=";"))

        violacao = next(linha for linha in linhas if linha["veredito"] == "fail")
        assert violacao["risco_juridico"]
        assert violacao["dispositivos_normativos"]
        assert violacao["tese_juridica"]

    def test_filtro_de_incompletos(self, sample_scan: ScanResult, tmp_path: Path) -> None:
        path = export_findings_csv(
            [sample_scan], tmp_path / "so-violacoes.csv", include_incomplete=False
        )
        with path.open(encoding="utf-8-sig", newline="") as handle:
            linhas = list(csv.DictReader(handle, delimiter=";"))
        assert all(linha["veredito"] == "fail" for linha in linhas)

    def test_medicao_ausente_fica_vazia_nao_zero(
        self, sample_scan: ScanResult, tmp_path: Path
    ) -> None:
        """Zero é uma medição; vazio é a ausência dela. Confundi-los inventa dado."""
        path = export_pages_csv([sample_scan], tmp_path / "paginas.csv")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            linhas = list(csv.DictReader(handle, delimiter=";"))

        # O LCP não foi medido em nenhuma página sintética.
        assert all(linha["lcp_ms"] == "" for linha in linhas)

    def test_codificacao_com_bom_para_excel(self, sample_scan: ScanResult, tmp_path: Path) -> None:
        """O público inclui gestores públicos que abrirão o arquivo no Excel."""
        path = export_pages_csv([sample_scan], tmp_path / "paginas.csv")
        assert path.read_bytes().startswith(b"\xef\xbb\xbf")


class TestRelatorioHtml:
    def test_declara_idioma_e_tem_um_unico_h1(self, sample_scan: ScanResult) -> None:
        """O relatório obedece às regras que audita — do contrário se desqualifica."""
        html = render_report(sample_scan)
        assert 'lang="pt-BR"' in html
        assert html.count("<h1>") == 1

    def test_tem_link_de_salto_e_marco_principal(self, sample_scan: ScanResult) -> None:
        html = render_report(sample_scan)
        assert 'href="#conteudo"' in html
        assert 'id="conteudo"' in html
        assert "<main" in html

    def test_declara_a_cobertura_parcial_no_corpo(self, sample_scan: ScanResult) -> None:
        """O limite vem no corpo, não em nota de rodapé — para não ser lido seletivamente."""
        # Normaliza espaços: a frase atravessa quebras de linha no template.
        texto = " ".join(render_report(sample_scan).split())
        assert "Ausência de achado não equivale a conformidade." in texto
        assert "dependem de julgamento humano" in texto

    def test_alerta_de_barreira_absoluta_aparece(self, sample_scan: ScanResult) -> None:
        html = render_report(sample_scan)
        assert 'role="alert"' in html
        assert "Barreira absoluta" in html

    def test_exibe_tese_juridica_e_dispositivos(self, sample_scan: ScanResult) -> None:
        html = render_report(sample_scan)
        assert "Fundamentação jurídica" in html
        assert "LBI, art. 63, caput" in html

    def test_taxa_de_perda_e_reportada(self, sample_scan: ScanResult) -> None:
        """Metade das páginas falhou; omitir isso tornaria os índices enganosos."""
        html = render_report(sample_scan)
        assert "Taxa de perda de páginas" in html
        assert "50.0%" in html

    def test_html_de_evidencia_e_escapado(self, sample_scan: ScanResult) -> None:
        """Evidência vem de portais de terceiros: marcação hostil não pode injetar."""
        scan = sample_scan.model_copy(deep=True)
        scan.pages[0].findings[0].nodes[0].html = "<script>alert('xss')</script>"
        html = render_report(scan)
        assert "<script>alert('xss')</script>" not in html
        assert "&lt;script&gt;" in html

    def test_relatorio_e_autocontido(self, sample_scan: ScanResult) -> None:
        """Sem recursos externos: pode ser arquivado como evidência estável."""
        html = render_report(sample_scan)
        assert "<script" not in html.replace("&lt;script", "")
        assert 'src="http' not in html


class TestCatalogo:
    def test_catalogo_do_projeto_e_valido(self) -> None:
        catalogo = load_catalog(Settings().catalog_path)
        assert catalogo.targets
        assert any(t.id == "fixtures-local" for t in catalogo.targets)

    def test_alvos_de_producao_nascem_desabilitados(self) -> None:
        """Conduta de coleta: habilitar é decisão consciente do pesquisador."""
        catalogo = load_catalog(Settings().catalog_path)
        producao = [t for t in catalogo.targets if t.id != "fixtures-local"]
        assert producao, "O catálogo precisa conter alvos reais documentados."
        assert all(not t.enabled for t in producao)

    def test_todo_alvo_justifica_sua_inclusao_na_amostra(self) -> None:
        """Sem justificativa, a seção de Métodos fica sem desenho amostral."""
        catalogo = load_catalog(Settings().catalog_path)
        sem_justificativa = [t.id for t in catalogo.targets if len(t.selection_rationale) < 60]
        assert not sem_justificativa, f"Alvos sem justificativa: {sem_justificativa}"

    def test_paginas_autenticadas_sao_lacunas_declaradas(self) -> None:
        """Áreas autenticadas não são varridas — e sua ausência precisa ser visível."""
        catalogo = load_catalog(Settings().catalog_path)
        conecte = catalogo.get("conecte-sus-web")
        assert conecte.declared_gaps
        assert all(s.requires_auth for s in conecte.declared_gaps)
        assert all(not s.requires_auth for s in conecte.auditable_seeds)
