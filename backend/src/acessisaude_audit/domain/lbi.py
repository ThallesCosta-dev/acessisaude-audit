"""Camada normativa brasileira: LBI, Constituição, decretos e convenções.

Enquanto :mod:`~acessisaude_audit.domain.wcag` descreve *o padrão técnico*, este
módulo descreve *o dever jurídico*. A separação é deliberada: uma falha técnica
só se converte em violação de direito quando existe uma norma que a proíbe e um
sujeito obrigado a cumpri-la. O cruzamento entre as duas camadas é feito em
:mod:`~acessisaude_audit.domain.mapping`.

O texto dos dispositivos foi resumido — nunca reescrito — para caber no relatório.
O campo :attr:`LegalProvision.citation` traz a referência completa para citação
acadêmica e o :attr:`LegalProvision.url` aponta para o texto oficial no Planalto.

.. warning::
   Este módulo estrutura fundamentação jurídica para fins de pesquisa e de
   auditoria técnica. Ele **não** substitui parecer jurídico, nem os relatórios
   gerados constituem prova pericial. Ver ``docs/juridico/limites-e-ressalvas.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from functools import cache

__all__ = [
    "LEGAL_PROVISIONS",
    "EnforcementRoute",
    "LegalProvision",
    "NormativeSource",
    "ObligationStrength",
    "provision",
    "provisions_by_source",
]


class NormativeSource(StrEnum):
    """Diploma normativo de origem, em ordem decrescente de hierarquia."""

    CONSTITUICAO = "constituicao_federal_1988"
    CONVENCAO_ONU = "convencao_onu_decreto_6949_2009"
    LBI = "lei_13146_2015"
    LAI = "lei_12527_2011"
    CODIGO_USUARIO = "lei_13460_2017"
    DECRETO_ACESSIBILIDADE = "decreto_5296_2004"
    DECRETO_LIBRAS = "decreto_5626_2005"
    EMAG = "emag_3_1"


class ObligationStrength(StrEnum):
    """Força vinculante do dispositivo sobre o gestor público.

    Distinção necessária para o artigo: nem toda norma citada gera dever
    imediatamente exigível. Confundir princípio com regra enfraquece o argumento.
    """

    PRINCIPIO = "principio"
    """Norma-princípio: orienta a interpretação, não impõe conduta específica."""

    REGRA_VINCULANTE = "regra_vinculante"
    """Regra de conduta com destinatário e obrigação determinados."""

    NORMA_TECNICA_REFERENCIADA = "norma_tecnica_referenciada"
    """Padrão técnico que a lei incorpora por remissão (art. 63 → 'melhores
    práticas e diretrizes de acessibilidade adotadas internacionalmente')."""


class EnforcementRoute(StrEnum):
    """Via de exigibilidade típica em caso de descumprimento."""

    MINISTERIO_PUBLICO = "ministerio_publico"
    ACAO_CIVIL_PUBLICA = "acao_civil_publica"
    CONTROLE_INTERNO_TCU_TCE = "controle_interno_tcu_tce"
    OUVIDORIA_SUS = "ouvidoria_sus"
    CONSELHO_DIREITOS_PCD = "conselho_direitos_pcd"
    ACAO_INDIVIDUAL = "acao_individual"


@dataclass(frozen=True, slots=True)
class LegalProvision:
    """Um dispositivo normativo invocável em um achado de auditoria.

    Attributes:
        key: Identificador estável usado nas matrizes de mapeamento,
            ex. ``"lbi.art63.caput"``.
        source: Diploma de origem.
        label: Rótulo curto para exibição, ex. ``"LBI, art. 63, caput"``.
        summary: Síntese do comando normativo em linguagem acessível ao gestor.
        strength: Força vinculante — ver :class:`ObligationStrength`.
        addressee: Quem é o sujeito obrigado.
        routes: Vias de exigibilidade típicas.
        citation: Referência completa em formato ABNT para o artigo.
        url: Texto oficial.
    """

    key: str
    source: NormativeSource
    label: str
    summary: str
    strength: ObligationStrength
    addressee: str
    citation: str
    url: str
    routes: frozenset[EnforcementRoute] = field(default_factory=frozenset)

    def __str__(self) -> str:
        return self.label


_PLANALTO = "https://www.planalto.gov.br/ccivil_03"
_LBI_URL = f"{_PLANALTO}/_ato2015-2018/2015/lei/l13146.htm"
_CF_URL = f"{_PLANALTO}/constituicao/constituicao.htm"

_CIT_LBI = (
    "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Institui a Lei Brasileira de "
    "Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência). "
    "Diário Oficial da União, Brasília, DF, 7 jul. 2015."
)
_CIT_CF = (
    "BRASIL. Constituição da República Federativa do Brasil de 1988. "
    "Brasília, DF: Senado Federal, 1988."
)
_CIT_DEC5296 = (
    "BRASIL. Decreto nº 5.296, de 2 de dezembro de 2004. Regulamenta as Leis nº "
    "10.048/2000 e nº 10.098/2000. Diário Oficial da União, Brasília, DF, 3 dez. 2004."
)


def _p(
    key: str,
    source: NormativeSource,
    label: str,
    summary: str,
    strength: ObligationStrength,
    addressee: str,
    citation: str,
    url: str,
    routes: tuple[EnforcementRoute, ...] = (),
) -> LegalProvision:
    return LegalProvision(
        key=key,
        source=source,
        label=label,
        summary=summary,
        strength=strength,
        addressee=addressee,
        citation=citation,
        url=url,
        routes=frozenset(routes),
    )


_MP = EnforcementRoute.MINISTERIO_PUBLICO
_ACP = EnforcementRoute.ACAO_CIVIL_PUBLICA
_TC = EnforcementRoute.CONTROLE_INTERNO_TCU_TCE
_OUV = EnforcementRoute.OUVIDORIA_SUS
_CONS = EnforcementRoute.CONSELHO_DIREITOS_PCD
_IND = EnforcementRoute.ACAO_INDIVIDUAL

_REGRA = ObligationStrength.REGRA_VINCULANTE
_PRINC = ObligationStrength.PRINCIPIO
_TEC = ObligationStrength.NORMA_TECNICA_REFERENCIADA


#: Registro dos dispositivos normativos usados pela ferramenta.
LEGAL_PROVISIONS: tuple[LegalProvision, ...] = (
    # ------------------------------------------------------------- Constituição
    _p(
        "cf.art5.xiv",
        NormativeSource.CONSTITUICAO,
        "CF/88, art. 5º, XIV",
        "Assegura a todos o acesso à informação. Uma barreira técnica que impede "
        "o cidadão de ler a informação pública é restrição de direito fundamental.",
        _PRINC,
        "Estado e particulares",
        _CIT_CF,
        _CF_URL,
        (_MP, _ACP, _IND),
    ),
    _p(
        "cf.art196",
        NormativeSource.CONSTITUICAO,
        "CF/88, art. 196",
        "A saúde é direito de todos e dever do Estado, garantida por políticas que "
        "assegurem acesso universal e igualitário. Se o canal de acesso ao serviço "
        "é digital e o canal é inacessível, o acesso deixa de ser universal.",
        _PRINC,
        "União, Estados, Distrito Federal e Municípios",
        _CIT_CF,
        _CF_URL,
        (_MP, _ACP, _OUV),
    ),
    _p(
        "cf.art227.par2",
        NormativeSource.CONSTITUICAO,
        "CF/88, art. 227, § 2º",
        "Determina normas de construção e adaptação para garantir acesso adequado "
        "às pessoas com deficiência — fundamento constitucional da acessibilidade.",
        _PRINC,
        "Legislador e administração pública",
        _CIT_CF,
        _CF_URL,
        (_MP, _ACP),
    ),
    # ------------------------------------------------------------ Convenção ONU
    _p(
        "onu.art9",
        NormativeSource.CONVENCAO_ONU,
        "Convenção sobre os Direitos das PcD, art. 9 (Decreto 6.949/2009)",
        "Obriga os Estados-Parte a assegurar acesso a sistemas e tecnologias de "
        "informação e comunicação, inclusive à Internet. Tem status de emenda "
        "constitucional no Brasil (art. 5º, § 3º, CF).",
        _REGRA,
        "Estado brasileiro",
        "BRASIL. Decreto nº 6.949, de 25 de agosto de 2009. Promulga a Convenção "
        "Internacional sobre os Direitos das Pessoas com Deficiência. Diário Oficial "
        "da União, Brasília, DF, 26 ago. 2009.",
        f"{_PLANALTO}/_ato2007-2010/2009/decreto/d6949.htm",
        (_MP, _ACP, _CONS),
    ),
    _p(
        "onu.art25",
        NormativeSource.CONVENCAO_ONU,
        "Convenção sobre os Direitos das PcD, art. 25 (Decreto 6.949/2009)",
        "Reconhece o direito da pessoa com deficiência ao mais elevado padrão de "
        "saúde, sem discriminação, incluindo serviços de saúde acessíveis.",
        _REGRA,
        "Estado brasileiro",
        "BRASIL. Decreto nº 6.949, de 25 de agosto de 2009. Diário Oficial da "
        "União, Brasília, DF, 26 ago. 2009.",
        f"{_PLANALTO}/_ato2007-2010/2009/decreto/d6949.htm",
        (_MP, _ACP, _OUV),
    ),
    # ---------------------------------------------------------------------- LBI
    _p(
        "lbi.art3.i",
        NormativeSource.LBI,
        "LBI, art. 3º, I",
        "Define acessibilidade como possibilidade de uso, com segurança e "
        "autonomia, de sistemas e meios de comunicação e informação. Autonomia é "
        "o núcleo: depender de terceiro para agendar consulta já é falha.",
        _REGRA,
        "Poder público e particulares",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP),
    ),
    _p(
        "lbi.art3.iv.d",
        NormativeSource.LBI,
        "LBI, art. 3º, IV, 'd'",
        "Tipifica as 'barreiras nas comunicações e na informação' — inclusive as "
        "tecnológicas — como obstáculo que dificulta a recepção de mensagens e "
        "informações por meio de sistemas de comunicação e tecnologia da informação.",
        _REGRA,
        "Poder público e particulares",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP, _IND),
    ),
    _p(
        "lbi.art4",
        NormativeSource.LBI,
        "LBI, art. 4º",
        "Toda pessoa com deficiência tem direito à igualdade de oportunidades e não "
        "sofrerá discriminação. O § 1º define como discriminação toda distinção que "
        "prejudique o exercício de direitos, incluindo a recusa de adaptações "
        "razoáveis — omissão em acessibilizar é conduta discriminatória.",
        _REGRA,
        "Poder público e particulares",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP, _IND),
    ),
    _p(
        "lbi.art8",
        NormativeSource.LBI,
        "LBI, art. 8º",
        "Impõe ao Estado, à sociedade e à família o dever de assegurar, com "
        "prioridade, os direitos à saúde e à informação da pessoa com deficiência.",
        _REGRA,
        "Estado, sociedade e família",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP, _OUV),
    ),
    _p(
        "lbi.art9.v",
        NormativeSource.LBI,
        "LBI, art. 9º, V",
        "Garante atendimento prioritário com disponibilização de recursos, humanos "
        "e tecnológicos, que assegurem atendimento em igualdade de condições.",
        _REGRA,
        "Prestadores de serviço público e privado",
        _CIT_LBI,
        _LBI_URL,
        (_OUV, _MP),
    ),
    _p(
        "lbi.art18",
        NormativeSource.LBI,
        "LBI, art. 18",
        "Assegura atenção integral à saúde da pessoa com deficiência em todos os "
        "níveis de complexidade, por intermédio do SUS. O § 4º, IV determina "
        "oferta de comunicação e informação adequadas.",
        _REGRA,
        "SUS — gestores federal, estadual e municipal",
        _CIT_LBI,
        _LBI_URL,
        (_OUV, _MP, _ACP),
    ),
    _p(
        "lbi.art63.caput",
        NormativeSource.LBI,
        "LBI, art. 63, caput",
        "Núcleo do dever auditado por esta ferramenta: é obrigatória a "
        "acessibilidade nos sítios da internet mantidos por órgãos de governo, "
        "garantindo acesso às informações disponíveis, 'conforme as melhores "
        "práticas e diretrizes de acessibilidade adotadas internacionalmente'. "
        "A remissão às 'melhores práticas' é o que juridiciza a WCAG.",
        _REGRA,
        "Órgãos de governo e empresas com sede ou representação no país",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP, _TC, _IND),
    ),
    _p(
        "lbi.art63.par1",
        NormativeSource.LBI,
        "LBI, art. 63, § 1º",
        "Prevê o selo nacional de acessibilidade digital, a ser concedido a sítios "
        "que cumpram as regras de acessibilidade — instrumento de indução e de "
        "publicidade do descumprimento.",
        _TEC,
        "Poder Executivo federal",
        _CIT_LBI,
        _LBI_URL,
        (_TC,),
    ),
    _p(
        "lbi.art63.par2",
        NormativeSource.LBI,
        "LBI, art. 63, § 2º",
        "Estende a exigência a telecentros comunitários e lan houses, que devem "
        "manter ao menos 10% dos computadores com recursos de acessibilidade.",
        _REGRA,
        "Telecentros e estabelecimentos de acesso à internet",
        _CIT_LBI,
        _LBI_URL,
        (_MP,),
    ),
    _p(
        "lbi.art64",
        NormativeSource.LBI,
        "LBI, art. 64",
        "Torna a acessibilidade nos sítios requisito de instrumentos de aprovação "
        "de projetos e de financiamento com recursos públicos — permite atacar a "
        "irregularidade pela via orçamentária, não só pela judicial.",
        _REGRA,
        "Órgãos financiadores e de aprovação de projetos",
        _CIT_LBI,
        _LBI_URL,
        (_TC, _MP),
    ),
    _p(
        "lbi.art74",
        NormativeSource.LBI,
        "LBI, art. 74",
        "Garante à pessoa com deficiência o acesso a produtos, recursos e "
        "tecnologias assistivas que ampliem sua autonomia — inclui a compatibilidade "
        "do serviço digital com leitores de tela e demais TA.",
        _REGRA,
        "Poder público",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP),
    ),
    _p(
        "lbi.art76",
        NormativeSource.LBI,
        "LBI, art. 76",
        "Assegura participação plena na vida pública e política, com sítios "
        "eletrônicos e materiais informativos acessíveis.",
        _REGRA,
        "Poder público",
        _CIT_LBI,
        _LBI_URL,
        (_MP, _ACP),
    ),
    # ------------------------------------------------------ Transparência e usuário
    _p(
        "lai.art8.par3.viii",
        NormativeSource.LAI,
        "LAI, art. 8º, § 3º, VIII",
        "Obriga os sítios oficiais a adotar medidas para garantir acessibilidade "
        "de conteúdo para pessoas com deficiência — dever de transparência ativa.",
        _REGRA,
        "Órgãos e entidades públicas",
        "BRASIL. Lei nº 12.527, de 18 de novembro de 2011. Regula o acesso a "
        "informações. Diário Oficial da União, Brasília, DF, 18 nov. 2011.",
        f"{_PLANALTO}/_ato2011-2014/2011/lei/l12527.htm",
        (_MP, _TC),
    ),
    _p(
        "lei13460.art5",
        NormativeSource.CODIGO_USUARIO,
        "Lei 13.460/2017, art. 5º",
        "Direito do usuário de serviço público a atendimento com adequação, "
        "eficiência e acessibilidade, inclusive nos canais digitais.",
        _REGRA,
        "Administração pública direta e indireta",
        "BRASIL. Lei nº 13.460, de 26 de junho de 2017. Dispõe sobre participação, "
        "proteção e defesa dos direitos do usuário dos serviços públicos. Diário "
        "Oficial da União, Brasília, DF, 27 jun. 2017.",
        f"{_PLANALTO}/_ato2015-2018/2017/lei/l13460.htm",
        (_OUV, _MP),
    ),
    # ------------------------------------------------------------------ Decretos
    _p(
        "dec5296.art47",
        NormativeSource.DECRETO_ACESSIBILIDADE,
        "Decreto 5.296/2004, art. 47",
        "Determina acessibilidade obrigatória nos portais e sítios eletrônicos da "
        "administração pública para o uso das pessoas com deficiência visual. É a "
        "norma que, na prática administrativa brasileira, incorporou o eMAG.",
        _REGRA,
        "Administração pública na rede mundial de computadores",
        _CIT_DEC5296,
        f"{_PLANALTO}/_ato2004-2006/2004/decreto/d5296.htm",
        (_MP, _TC, _ACP),
    ),
    _p(
        "dec5626.art26",
        NormativeSource.DECRETO_LIBRAS,
        "Decreto 5.626/2005, art. 26",
        "Obriga o poder público a garantir atendimento e tratamento adequado às "
        "pessoas surdas, incluindo acesso à informação em Libras — fundamento para "
        "exigir janela de Libras e legendas em conteúdo audiovisual de saúde.",
        _REGRA,
        "Órgãos da administração pública federal",
        "BRASIL. Decreto nº 5.626, de 22 de dezembro de 2005. Regulamenta a Lei nº "
        "10.436/2002. Diário Oficial da União, Brasília, DF, 23 dez. 2005.",
        f"{_PLANALTO}/_ato2004-2006/2005/decreto/d5626.htm",
        (_MP, _CONS),
    ),
    # ---------------------------------------------------------------------- eMAG
    _p(
        "emag.3.1",
        NormativeSource.EMAG,
        "eMAG 3.1",
        "Modelo de Acessibilidade em Governo Eletrônico: padrão técnico oficial da "
        "administração pública federal, alinhado à WCAG. É o vetor concreto pelo "
        "qual a remissão do art. 63 da LBI às 'melhores práticas' se materializa "
        "no ordenamento brasileiro.",
        _TEC,
        "Sítios do governo federal (referência para estados e municípios)",
        "BRASIL. Ministério do Planejamento. eMAG — Modelo de Acessibilidade em "
        "Governo Eletrônico. Versão 3.1. Brasília, DF, 2014.",
        "https://emag.governoeletronico.gov.br/",
        (_TC, _MP),
    ),
)


@cache
def _index() -> dict[str, LegalProvision]:
    return {p.key: p for p in LEGAL_PROVISIONS}


def provision(key: str) -> LegalProvision:
    """Recupera um dispositivo pelo :attr:`LegalProvision.key`.

    Raises:
        KeyError: Se a chave não estiver registrada.
    """
    try:
        return _index()[key]
    except KeyError as exc:  # pragma: no cover
        raise KeyError(f"Dispositivo normativo não registrado: {key!r}") from exc


def provisions_by_source(source: NormativeSource) -> tuple[LegalProvision, ...]:
    """Todos os dispositivos de um mesmo diploma normativo."""
    return tuple(p for p in LEGAL_PROVISIONS if p.source is source)
