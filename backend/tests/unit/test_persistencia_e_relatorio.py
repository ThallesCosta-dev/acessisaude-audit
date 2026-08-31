"""Persistência, exportação e relatório.

O foco é a propriedade que sustenta a reprodutibilidade do estudo: **o
documento JSON é a fonte da verdade, e o índice relacional é integralmente
derivável dele**. Se isso deixar de valer, mudar o cálculo de um índice passaria
a exigir revarrer os portais.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import PageAudit, PageStatus, ScanResult, Viewport
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

    def test_habilitar_alvo_exige_verificacao_documentada(self) -> None:
        """Conduta de coleta: habilitar é ato consciente e registrado.

        A invariante original era "alvos de produção nascem desabilitados", o
        que valia enquanto nenhuma coleta de campo havia ocorrido. Depois da
        coleta, essa formulação passaria a exigir desabilitar o que se acabou de
        auditar — protegendo a letra e perdendo o propósito.

        O que precisa continuar valendo é a substância: nenhum alvo é varrido
        sem que sua URL e seu ``robots.txt`` tenham sido conferidos, e o
        registro dessa conferência é o campo ``robots_note``.
        """
        catalogo = load_catalog(Settings().catalog_path)
        producao = [t for t in catalogo.targets if t.id != "fixtures-local"]
        assert producao, "O catálogo precisa conter alvos reais documentados."

        sem_verificacao = [t.id for t in producao if t.enabled and len(t.robots_note.strip()) < 40]
        assert not sem_verificacao, (
            f"Alvos habilitados sem registro de verificação de robots.txt: {sem_verificacao}"
        )

    def test_janela_de_coleta_esta_declarada(self) -> None:
        """Portais mudam; sem a janela, o dado não é interpretável."""
        catalogo = load_catalog(Settings().catalog_path)
        janela = catalogo.collection_window.strip()
        assert janela, "collection_window vazio."
        assert "a definir" not in janela.lower(), (
            "collection_window ainda contém o texto de espaço reservado."
        )

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


class TestVarreduraSemObservacao:
    """A ausência de veredito precisa atravessar índice, CSV e relatório.

    Corrigir apenas o cálculo não bastaria: se o índice relacional gravasse
    zero, o CSV escrevesse ``0,0`` ou o relatório imprimisse ``0``, a leitura
    enganosa reapareceria na saída — e é a saída que circula. O contrato só
    vale se o nulo sobreviver às três travessias.
    """

    @pytest.fixture
    def scan_perdido(self) -> ScanResult:
        """Varredura em que nenhuma página carregou — o caso de 25/08/2026."""
        return ScanResult(
            target_id="alvo-teste",
            target_name="Alvo de teste",
            base_url="http://exemplo.test/",
            pages=[
                PageAudit(
                    url=f"http://exemplo.test/{i}",
                    viewport=Viewport(name="desktop-1366", width=1366, height=768),
                    status=PageStatus.NAVIGATION_ERROR,
                    error="net::ERR_NAME_NOT_RESOLVED",
                )
                for i in range(4)
            ],
        )

    def test_indice_relacional_grava_nulo(
        self, repositorio: ScanRepository, scan_perdido: ScanResult
    ) -> None:
        row = repositorio.save(scan_perdido, sphere="federal")
        assert row.observed is False
        assert row.conformance_index is None
        assert row.friction_index is None
        assert row.legal_exposure_index is None
        assert row.absolute_barrier is None
        assert row.loss_rate == 1.0

    def test_reindexacao_preserva_a_ausencia(
        self, repositorio: ScanRepository, scan_perdido: ScanResult
    ) -> None:
        """Reindexar uma coleta perdida não pode fabricar um veredito."""
        repositorio.save(scan_perdido, sphere="federal")
        reindexado = repositorio.reindex(str(scan_perdido.id))
        assert reindexado is not None
        assert reindexado.observed is False
        assert reindexado.conformance_index is None

    def test_csv_de_paginas_marca_a_pagina_como_nao_auditada(
        self, scan_perdido: ScanResult, tmp_path: Path
    ) -> None:
        path = export_pages_csv([scan_perdido], tmp_path / "paginas.csv")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            linhas = list(csv.DictReader(handle, delimiter=";"))

        assert linhas
        assert all(linha["observado"] == "0" for linha in linhas)
        # Vazio, e não zero: não há índice, e "0,0" seria um veredito inventado.
        assert all(linha["indice_conformidade"] == "" for linha in linhas)
        assert all(linha["barreira_absoluta"] == "" for linha in linhas)

    def test_relatorio_anuncia_a_ausencia_de_veredito(self, scan_perdido: ScanResult) -> None:
        """O leitor precisa saber disso antes de interpretar qualquer número."""
        html = render_report(scan_perdido)
        assert "Sem veredito" in html
        assert "não significa conformidade nem não conformidade" in html

    def test_relatorio_nao_exibe_conformidade_perfeita(self, scan_perdido: ScanResult) -> None:
        """A regressão que motivou o contrato: 100,0 impresso sobre zero observação.

        A asserção mira os cartões de índice, e não o documento inteiro: a taxa
        de perda desta varredura é legitimamente 100%, e proibir a cadeia em
        qualquer posição confundiria o número que descreve a falha com o número
        que a esconderia.
        """
        html = render_report(scan_perdido)
        valores = re.findall(r'class="valor">([^<]*)<', html)
        assert valores[:3] == ["—", "—", "—"]
