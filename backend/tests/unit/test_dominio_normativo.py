"""Integridade do domínio normativo e jurídico.

Estes testes protegem afirmações que o artigo fará. Se um deles falhar, não é
um bug de implementação: é uma afirmação do texto que deixou de ser verdadeira.
"""

from __future__ import annotations

import pytest

from acessisaude_audit.domain.lbi import LEGAL_PROVISIONS, provision
from acessisaude_audit.domain.mapping import (
    BASE_PROVISIONS,
    CRITERION_MAPPINGS,
    HEALTH_PROVISIONS,
    LegalRisk,
    mapping_for,
    unmapped_criteria,
)
from acessisaude_audit.domain.wcag import (
    WCAG_CRITERIA,
    ConformanceLevel,
    criterion,
    criterion_from_axe_tag,
)


class TestTaxonomiaWCAG:
    def test_escopo_tem_exatamente_os_50_criterios_a_e_aa(self) -> None:
        """A WCAG 2.1 tem 30 critérios de nível A e 20 de nível AA."""
        assert len(WCAG_CRITERIA) == 50
        assert sum(1 for c in WCAG_CRITERIA if c.level is ConformanceLevel.A) == 30
        assert sum(1 for c in WCAG_CRITERIA if c.level is ConformanceLevel.AA) == 20

    def test_nenhum_criterio_aaa_no_escopo(self) -> None:
        """AAA está fora por decisão registrada em ADR — não por esquecimento."""
        assert all(c.level is not ConformanceLevel.AAA for c in WCAG_CRITERIA)

    def test_identificadores_sao_unicos(self) -> None:
        ids = [c.id for c in WCAG_CRITERIA]
        assert len(ids) == len(set(ids))

    def test_todo_criterio_declara_grupo_afetado(self) -> None:
        """Sem grupo afetado, o relatório não consegue responder 'quem é excluído'."""
        sem_grupo = [c.id for c in WCAG_CRITERIA if not c.affects]
        assert not sem_grupo, f"Critérios sem grupo afetado: {sem_grupo}"

    def test_todo_criterio_tem_justificativa_substantiva(self) -> None:
        """A justificativa aparece no relatório entregue ao gestor público."""
        curtos = [c.id for c in WCAG_CRITERIA if len(c.rationale) < 40]
        assert not curtos, f"Justificativa insuficiente em: {curtos}"

    @pytest.mark.parametrize(
        ("tag", "esperado"),
        [
            ("wcag143", "1.4.3"),
            ("wcag111", "1.1.1"),
            ("wcag412", "4.1.2"),
            ("wcag1410", "1.4.10"),
        ],
    )
    def test_traducao_de_tag_do_axe(self, tag: str, esperado: str) -> None:
        sc = criterion_from_axe_tag(tag)
        assert sc is not None
        assert sc.id == esperado

    @pytest.mark.parametrize("tag", ["best-practice", "cat.forms", "wcag2aa", "EN-301-549", "ACT"])
    def test_tags_sem_criterio_retornam_none(self, tag: str) -> None:
        """Tags de categoria e de conjunto não denotam critério individual."""
        assert criterion_from_axe_tag(tag) is None

    def test_criterio_desconhecido_levanta_erro(self) -> None:
        with pytest.raises(KeyError, match="fora do escopo"):
            criterion("9.9.9")


class TestDispositivosNormativos:
    def test_chaves_unicas(self) -> None:
        chaves = [p.key for p in LEGAL_PROVISIONS]
        assert len(chaves) == len(set(chaves))

    def test_art63_da_lbi_esta_registrado(self) -> None:
        """É o dispositivo que juridiciza a WCAG no ordenamento brasileiro."""
        art63 = provision("lbi.art63.caput")
        assert "melhores práticas" in art63.summary
        assert "órgãos de governo" in art63.addressee.lower()

    def test_todo_dispositivo_tem_citacao_completa(self) -> None:
        """Sem citação ABNT, o dispositivo não pode ir para o artigo."""
        incompletos = [p.key for p in LEGAL_PROVISIONS if "BRASIL" not in p.citation]
        assert not incompletos, f"Citação incompleta em: {incompletos}"

    def test_todo_dispositivo_declara_destinatario(self) -> None:
        """Norma sem sujeito obrigado não fundamenta exigência."""
        assert all(p.addressee.strip() for p in LEGAL_PROVISIONS)


class TestMatrizWcagLbi:
    def test_matriz_e_completa(self) -> None:
        """Nenhum critério do escopo pode ficar sem fundamentação jurídica.

        Este é o teste que sustenta a alegação de completude feita no artigo e
        exposta na rota /referencia/integridade-da-matriz.
        """
        orfaos = unmapped_criteria()
        assert not orfaos, f"Critérios sem mapeamento jurídico: {orfaos}"

    def test_um_mapeamento_por_criterio(self) -> None:
        ids = [m.criterion_id for m in CRITERION_MAPPINGS]
        assert len(ids) == len(set(ids)) == len(WCAG_CRITERIA)

    def test_todo_mapeamento_referencia_dispositivos_existentes(self) -> None:
        """Uma chave inválida produziria uma tese jurídica sem norma por trás."""
        for m in CRITERION_MAPPINGS:
            for chave in m.provision_keys:
                provision(chave)  # levanta KeyError se não existir

    def test_dispositivos_base_e_de_saude_incidem_sobre_todos(self) -> None:
        """Toda barreira em portal público de saúde aciona o núcleo comum."""
        for m in CRITERION_MAPPINGS:
            chaves = set(m.provision_keys)
            assert set(BASE_PROVISIONS) <= chaves, m.criterion_id
            assert set(HEALTH_PROVISIONS) <= chaves, m.criterion_id

    def test_barreiras_sem_rota_alternativa_sao_criticas(self) -> None:
        """Teclado e nome/função/valor impedem o uso, não apenas o dificultam."""
        for criterion_id in ("2.1.1", "2.1.2", "4.1.2"):
            m = mapping_for(criterion_id)
            assert m is not None
            assert m.legal_risk is LegalRisk.CRITICO, criterion_id

    def test_toda_tese_e_substantiva(self) -> None:
        """A tese vai literalmente para o relatório e para o artigo."""
        curtas = [m.criterion_id for m in CRITERION_MAPPINGS if len(m.thesis) < 80]
        assert not curtas, f"Tese jurídica insuficiente em: {curtas}"

    def test_toda_conduta_corretiva_e_acionavel(self) -> None:
        """Recomendação vaga não corrige nada; exige-se orientação concreta."""
        vagas = [m.criterion_id for m in CRITERION_MAPPINGS if len(m.remediation) < 30]
        assert not vagas, f"Conduta corretiva insuficiente em: {vagas}"

    def test_pesos_de_risco_sao_estritamente_crescentes(self) -> None:
        pesos = [
            r.weight
            for r in (LegalRisk.BAIXO, LegalRisk.MODERADO, LegalRisk.ALTO, LegalRisk.CRITICO)
        ]
        assert pesos == sorted(pesos)
        assert len(set(pesos)) == 4
