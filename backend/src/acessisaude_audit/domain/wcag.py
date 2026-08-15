"""Taxonomia normativa da WCAG 2.1 (níveis A e AA).

Este módulo é a *fonte única de verdade* sobre os critérios de sucesso avaliados
pela ferramenta. Ele não executa nenhuma verificação: apenas descreve o universo
normativo contra o qual as verificações (``auditor.probes`` e ``axe-core``) são
posteriormente mapeadas.

Escopo — decisão registrada em ``docs/adr/0003-escopo-wcag-a-aa.md``:
    Somente os 50 critérios de sucesso de níveis **A** e **AA** da WCAG 2.1 são
    modelados. O nível AAA é deliberadamente excluído porque o Decreto
    5.296/2004, o eMAG 3.1 e a jurisprudência administrativa brasileira tomam
    A/AA como patamar exigível para sítios da administração pública.

Referência normativa: W3C. *Web Content Accessibility Guidelines (WCAG) 2.1*.
W3C Recommendation, 05 jun. 2018. Disponível em https://www.w3.org/TR/WCAG21/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from functools import cache

__all__ = [
    "WCAG_CRITERIA",
    "ConformanceLevel",
    "DeficiencyGroup",
    "Principle",
    "SuccessCriterion",
    "criteria_by_level",
    "criterion",
    "criterion_from_axe_tag",
    "principle_of",
]


class Principle(StrEnum):
    """Os quatro princípios fundacionais da WCAG (POUR)."""

    PERCEIVABLE = "perceptivel"
    OPERABLE = "operavel"
    UNDERSTANDABLE = "compreensivel"
    ROBUST = "robusto"

    @property
    def label(self) -> str:
        """Nome do princípio em português, para exibição em relatórios."""
        return {
            Principle.PERCEIVABLE: "Perceptível",
            Principle.OPERABLE: "Operável",
            Principle.UNDERSTANDABLE: "Compreensível",
            Principle.ROBUST: "Robusto",
        }[self]


class ConformanceLevel(StrEnum):
    """Nível de conformidade exigido pelo critério."""

    A = "A"
    AA = "AA"
    AAA = "AAA"


class DeficiencyGroup(StrEnum):
    """Grupos de pessoas com deficiência afetados por uma barreira.

    A segmentação segue a lógica do art. 3º, IV da Lei 13.146/2015 ("barreiras
    nas comunicações e na informação") combinada com a categorização funcional
    usada pelo W3C em *How People with Disabilities Use the Web*. Ela permite
    responder, no artigo, à pergunta "quem exatamente é excluído por esta
    falha?" — e não apenas "quantas falhas existem".
    """

    BLINDNESS = "cegueira"
    LOW_VISION = "baixa_visao"
    COLOR_VISION = "visao_de_cores"
    DEAFNESS = "surdez"
    MOTOR = "motora"
    COGNITIVE = "cognitiva_neurodivergencia"
    SPEECH = "fala"
    PHOTOSENSITIVITY = "fotossensibilidade"
    LOW_BANDWIDTH = "baixa_conectividade"
    """Não é uma deficiência: é a condição do *usuário periférico* (plano de
    dados pré-pago, aparelho antigo, rede instável). Modelada aqui porque o
    projeto trata exclusão digital e exclusão por deficiência como barreiras de
    mesma natureza jurídica — ambas obstruem o acesso ao direito à saúde."""


@dataclass(frozen=True, slots=True)
class SuccessCriterion:
    """Um critério de sucesso da WCAG 2.1.

    Attributes:
        id: Numeração oficial, ex. ``"1.4.3"``.
        title_en: Título original em inglês (facilita rastreio na norma).
        title_pt: Tradução adotada no projeto, alinhada ao eMAG 3.1.
        level: Nível de conformidade (A ou AA neste escopo).
        principle: Princípio POUR ao qual pertence.
        guideline: Diretriz-mãe, ex. ``"1.4"``.
        rationale: Por que o critério existe, em uma frase — usado nos
            relatórios para que gestores públicos não-técnicos entendam o dano.
        affects: Grupos impactados quando o critério é violado.
        axe_tag: Tag correspondente na taxonomia do axe-core (``wcag143``),
            quando existir. ``None`` indica critério sem cobertura automática
            possível — exige verificação manual assistida.
        automatable: ``True`` se a ferramenta consegue emitir veredito
            determinístico para **ao menos um modo de falha** do critério.

            A leitura precisa importa e precisa ser declarada no artigo: marcar
            1.1.1 como automatizável significa que a *ausência* de ``alt`` é
            detectável, **não** que a adequação da descrição o seja. Um portal
            que preencha todos os ``alt`` com "imagem" passa na verificação
            automática e continua inacessível.

            Portanto :attr:`~acessisaude_audit.domain.scoring.AccessibilityScore.coverage`
            é um **limite superior otimista** da cobertura real: ele mede a
            fração de critérios em que a ferramenta pode dizer algo, não a
            fração de barreiras que ela encontra. Nenhuma formulação que
            confunda as duas coisas deve aparecer nos resultados.
    """

    id: str
    title_en: str
    title_pt: str
    level: ConformanceLevel
    principle: Principle
    rationale: str
    affects: frozenset[DeficiencyGroup] = field(default_factory=frozenset)
    axe_tag: str | None = None
    automatable: bool = False

    @property
    def guideline(self) -> str:
        """Diretriz-mãe do critério, ex. ``"1.4"`` para o critério ``1.4.3``."""
        major, minor, _ = self.id.split(".")
        return f"{major}.{minor}"

    @property
    def url(self) -> str:
        """URL do critério no *Understanding WCAG 2.1*."""
        slug = self.title_en.lower()
        for ch in "(),.":
            slug = slug.replace(ch, "")
        slug = slug.replace(" ", "-")
        return f"https://www.w3.org/WAI/WCAG21/Understanding/{slug}.html"

    def __str__(self) -> str:
        return f"{self.id} {self.title_pt} ({self.level})"


def _sc(
    id_: str,
    title_en: str,
    title_pt: str,
    level: ConformanceLevel,
    principle: Principle,
    rationale: str,
    affects: tuple[DeficiencyGroup, ...],
    axe_tag: str | None = None,
    automatable: bool = False,
) -> SuccessCriterion:
    """Construtor abreviado — mantém a tabela abaixo legível."""
    return SuccessCriterion(
        id=id_,
        title_en=title_en,
        title_pt=title_pt,
        level=level,
        principle=principle,
        rationale=rationale,
        affects=frozenset(affects),
        axe_tag=axe_tag,
        automatable=automatable,
    )


_A = ConformanceLevel.A
_AA = ConformanceLevel.AA
_P = Principle.PERCEIVABLE
_O = Principle.OPERABLE
_U = Principle.UNDERSTANDABLE
_R = Principle.ROBUST

_G = DeficiencyGroup
_BLIND = _G.BLINDNESS
_LOW = _G.LOW_VISION
_COLOR = _G.COLOR_VISION
_DEAF = _G.DEAFNESS
_MOTOR = _G.MOTOR
_COG = _G.COGNITIVE
_PHOTO = _G.PHOTOSENSITIVITY
_BAND = _G.LOW_BANDWIDTH


#: Registro imutável dos 50 critérios de sucesso A/AA da WCAG 2.1.
WCAG_CRITERIA: tuple[SuccessCriterion, ...] = (
    # ---------------------------------------------------------------- 1. Perceptível
    _sc(
        "1.1.1",
        "Non-text Content",
        "Conteúdo não textual",
        _A,
        _P,
        "Imagens sem alternativa textual são invisíveis para leitores de tela: o "
        "usuário cego não sabe se o ícone é 'agendar consulta' ou 'cancelar'.",
        (_BLIND, _LOW, _COG, _BAND),
        "wcag111",
        True,
    ),
    _sc(
        "1.2.1",
        "Audio-only and Video-only (Prerecorded)",
        "Apenas áudio e apenas vídeo (pré-gravado)",
        _A,
        _P,
        "Vídeos institucionais de campanhas de saúde sem transcrição excluem "
        "pessoas surdas e pessoas em conexões lentas que não conseguem carregá-los.",
        (_DEAF, _BLIND, _BAND),
        "wcag121",
    ),
    _sc(
        "1.2.2",
        "Captions (Prerecorded)",
        "Legendas (pré-gravado)",
        _A,
        _P,
        "Orientações clínicas em vídeo sem legenda tornam a informação de saúde "
        "inacessível a pessoas surdas.",
        (_DEAF,),
        "wcag122",
    ),
    _sc(
        "1.2.3",
        "Audio Description or Media Alternative (Prerecorded)",
        "Audiodescrição ou alternativa de mídia (pré-gravado)",
        _A,
        _P,
        "Sem audiodescrição, demonstrações visuais (ex.: como aplicar insulina) "
        "não chegam a quem não enxerga.",
        (_BLIND, _LOW),
        "wcag123",
    ),
    _sc(
        "1.2.4",
        "Captions (Live)",
        "Legendas (ao vivo)",
        _AA,
        _P,
        "Transmissões ao vivo de boletins epidemiológicos sem legenda em tempo "
        "real excluem pessoas surdas justamente em situação de emergência.",
        (_DEAF,),
        "wcag124",
    ),
    _sc(
        "1.2.5",
        "Audio Description (Prerecorded)",
        "Audiodescrição (pré-gravado)",
        _AA,
        _P,
        "Reforça 1.2.3 exigindo audiodescrição plena, não apenas alternativa textual.",
        (_BLIND, _LOW),
        "wcag125",
    ),
    _sc(
        "1.3.1",
        "Info and Relationships",
        "Informações e relações",
        _A,
        _P,
        "Estrutura semântica ausente (tabelas sem cabeçalho, formulários sem "
        "rótulo) faz o leitor de tela ler dados clínicos fora de contexto.",
        (_BLIND, _LOW, _COG),
        "wcag131",
        True,
    ),
    _sc(
        "1.3.2",
        "Meaningful Sequence",
        "Sequência com significado",
        _A,
        _P,
        "Ordem de leitura incoerente embaralha o passo a passo de um agendamento.",
        (_BLIND, _COG),
        "wcag132",
        True,
    ),
    _sc(
        "1.3.3",
        "Sensory Characteristics",
        "Características sensoriais",
        _A,
        _P,
        "Instruções do tipo 'clique no botão verde à direita' são inúteis para "
        "quem não vê ou não distingue cores.",
        (_BLIND, _LOW, _COLOR, _COG),
        "wcag133",
    ),
    _sc(
        "1.3.4",
        "Orientation",
        "Orientação",
        _AA,
        _P,
        "Travar a tela em paisagem inviabiliza o uso por quem tem o aparelho "
        "fixado a uma cadeira de rodas.",
        (_MOTOR, _LOW),
        "wcag134",
        True,
    ),
    _sc(
        "1.3.5",
        "Identify Input Purpose",
        "Identificar o propósito da entrada",
        _AA,
        _P,
        "Sem 'autocomplete', o preenchimento do CPF/CNS precisa ser refeito "
        "manualmente a cada acesso — barreira motora e cognitiva.",
        (_MOTOR, _COG, _LOW),
        "wcag135",
        True,
    ),
    _sc(
        "1.4.1",
        "Use of Color",
        "Uso de cor",
        _A,
        _P,
        "Sinalizar 'consulta cancelada' apenas pela cor vermelha oculta a "
        "informação de quem tem daltonismo.",
        (_COLOR, _BLIND, _LOW),
        "wcag141",
    ),
    _sc(
        "1.4.2",
        "Audio Control",
        "Controle de áudio",
        _A,
        _P,
        "Áudio automático compete com o leitor de tela e torna a página inutilizável.",
        (_BLIND, _COG),
        "wcag142",
    ),
    _sc(
        "1.4.3",
        "Contrast (Minimum)",
        "Contraste (mínimo)",
        _AA,
        _P,
        "Contraste abaixo de 4.5:1 inviabiliza a leitura sob luz solar, em telas "
        "antigas ou por pessoas com baixa visão — perfil majoritário entre idosos "
        "usuários do SUS.",
        (_LOW, _COLOR, _COG),
        "wcag143",
        True,
    ),
    _sc(
        "1.4.4",
        "Resize Text",
        "Redimensionar texto",
        _AA,
        _P,
        "Se o zoom em 200% quebra o layout, o usuário com baixa visão perde conteúdo ou controles.",
        (_LOW, _COG),
        "wcag144",
        True,
    ),
    _sc(
        "1.4.5",
        "Images of Text",
        "Imagens de texto",
        _AA,
        _P,
        "Cartazes em JPEG com o calendário de vacinação não podem ser lidos por "
        "leitor de tela nem ampliados sem perda — e pesam megabytes.",
        (_BLIND, _LOW, _BAND),
        "wcag145",
    ),
    _sc(
        "1.4.10",
        "Reflow",
        "Refluxo",
        _AA,
        _P,
        "Rolagem horizontal em telas de 320px é a falha mais comum em portais "
        "públicos acessados majoritariamente por celular.",
        (_LOW, _MOTOR, _COG),
        "wcag1410",
        True,
    ),
    _sc(
        "1.4.11",
        "Non-text Contrast",
        "Contraste não textual",
        _AA,
        _P,
        "Bordas de campo de formulário sem contraste escondem onde digitar o CNS.",
        (_LOW, _COLOR),
        "wcag1411",
        True,
    ),
    _sc(
        "1.4.12",
        "Text Spacing",
        "Espaçamento de texto",
        _AA,
        _P,
        "Impedir o ajuste de entrelinhas bloqueia adaptações usadas por pessoas com dislexia.",
        (_COG, _LOW),
        "wcag1412",
        True,
    ),
    _sc(
        "1.4.13",
        "Content on Hover or Focus",
        "Conteúdo em foco ou ao passar o mouse",
        _AA,
        _P,
        "Tooltips que somem ao mover o cursor impedem a leitura por quem usa ampliador de tela.",
        (_LOW, _MOTOR, _COG),
        "wcag1413",
    ),
    # ------------------------------------------------------------------- 2. Operável
    _sc(
        "2.1.1",
        "Keyboard",
        "Teclado",
        _A,
        _O,
        "Controles inacessíveis por teclado excluem quem não usa mouse: "
        "tetraplégicos, usuários de switch, cegos.",
        (_MOTOR, _BLIND),
        "wcag211",
        True,
    ),
    _sc(
        "2.1.2",
        "No Keyboard Trap",
        "Sem bloqueio do teclado",
        _A,
        _O,
        "Uma armadilha de foco em um modal de login prende o usuário fora do serviço.",
        (_MOTOR, _BLIND),
        "wcag212",
        True,
    ),
    _sc(
        "2.1.4",
        "Character Key Shortcuts",
        "Atalhos de caractere",
        _A,
        _O,
        "Atalhos de tecla única disparam ações por engano em quem usa reconhecimento de voz.",
        (_MOTOR, _G.SPEECH),
        "wcag214",
    ),
    _sc(
        "2.2.1",
        "Timing Adjustable",
        "Tempo ajustável",
        _A,
        _O,
        "Sessões que expiram em 2 minutos derrubam idosos no meio do agendamento.",
        (_COG, _MOTOR, _LOW, _BAND),
        "wcag221",
    ),
    _sc(
        "2.2.2",
        "Pause, Stop, Hide",
        "Pausar, parar, ocultar",
        _A,
        _O,
        "Carrosséis automáticos impedem a leitura e consomem dados em segundo plano.",
        (_COG, _LOW, _BAND),
        "wcag222",
        True,
    ),
    _sc(
        "2.3.1",
        "Three Flashes or Below Threshold",
        "Três flashes ou abaixo do limite",
        _A,
        _O,
        "Conteúdo piscante pode desencadear crises em pessoas com epilepsia fotossensível.",
        (_PHOTO,),
        "wcag231",
    ),
    _sc(
        "2.4.1",
        "Bypass Blocks",
        "Ignorar blocos",
        _A,
        _O,
        "Sem link 'pular para o conteúdo', o leitor de tela relê 60 itens de menu a cada página.",
        (_BLIND, _MOTOR, _COG),
        "wcag241",
        True,
    ),
    _sc(
        "2.4.2",
        "Page Titled",
        "Página com título",
        _A,
        _O,
        "Títulos genéricos ('Documento sem título') impedem localizar a aba certa "
        "entre várias abertas.",
        (_BLIND, _COG),
        "wcag242",
        True,
    ),
    _sc(
        "2.4.3",
        "Focus Order",
        "Ordem de foco",
        _A,
        _O,
        "Ordem de tabulação ilógica faz o usuário submeter o formulário antes de preenchê-lo.",
        (_MOTOR, _BLIND, _COG),
        "wcag243",
        True,
    ),
    _sc(
        "2.4.4",
        "Link Purpose (In Context)",
        "Finalidade do link (no contexto)",
        _A,
        _O,
        "Dezenas de links 'clique aqui' formam uma lista sem sentido no leitor de tela.",
        (_BLIND, _COG),
        "wcag244",
        True,
    ),
    _sc(
        "2.4.5",
        "Multiple Ways",
        "Várias formas",
        _AA,
        _O,
        "Sem busca nem mapa do site, encontrar 'segunda via do cartão SUS' vira tentativa e erro.",
        (_COG, _BLIND),
        "wcag245",
    ),
    _sc(
        "2.4.6",
        "Headings and Labels",
        "Cabeçalhos e rótulos",
        _AA,
        _O,
        "Cabeçalhos vazios ou rótulos genéricos destroem a navegação por títulos, "
        "principal atalho de quem usa leitor de tela.",
        (_BLIND, _COG),
        "wcag246",
        True,
    ),
    _sc(
        "2.4.7",
        "Focus Visible",
        "Foco visível",
        _AA,
        _O,
        "Remover o contorno de foco (``outline: none``) cega o usuário de teclado "
        "sobre onde ele está na página.",
        (_MOTOR, _LOW, _COG),
        "wcag247",
        True,
    ),
    _sc(
        "2.5.1",
        "Pointer Gestures",
        "Gestos do ponteiro",
        _A,
        _O,
        "Exigir pinça ou arrasto exclui quem tem tremor ou usa um único dedo.",
        (_MOTOR,),
        "wcag251",
    ),
    _sc(
        "2.5.2",
        "Pointer Cancellation",
        "Cancelamento do ponteiro",
        _A,
        _O,
        "Ação disparada no ``mousedown`` impede desistir de um toque acidental.",
        (_MOTOR, _COG),
        "wcag252",
    ),
    _sc(
        "2.5.3",
        "Label in Name",
        "Rótulo no nome",
        _A,
        _O,
        "Se o nome acessível difere do texto visível, comandos de voz falham "
        "('clicar em Agendar' não encontra o botão).",
        (_G.SPEECH, _MOTOR, _LOW),
        "wcag253",
        True,
    ),
    _sc(
        "2.5.4",
        "Motion Actuation",
        "Acionamento por movimento",
        _A,
        _O,
        "Funções que exigem chacoalhar o aparelho excluem quem o mantém fixo em suporte.",
        (_MOTOR,),
        "wcag254",
    ),
    # ------------------------------------------------------------- 3. Compreensível
    _sc(
        "3.1.1",
        "Language of Page",
        "Idioma da página",
        _A,
        _U,
        "Sem ``lang='pt-BR'``, o leitor de tela pronuncia 'agendamento' com fonemas "
        "ingleses — o conteúdo vira ruído.",
        (_BLIND, _COG),
        "wcag311",
        True,
    ),
    _sc(
        "3.1.2",
        "Language of Parts",
        "Idioma de partes",
        _AA,
        _U,
        "Trechos em outro idioma sem marcação quebram a pronúncia sintética.",
        (_BLIND, _COG),
        "wcag312",
        True,
    ),
    _sc(
        "3.2.1",
        "On Focus",
        "Em foco",
        _A,
        _U,
        "Mudanças de contexto ao focar um campo desorientam quem navega por teclado.",
        (_BLIND, _COG, _MOTOR),
        "wcag321",
    ),
    _sc(
        "3.2.2",
        "On Input",
        "Na entrada",
        _A,
        _U,
        "Submeter o formulário automaticamente ao escolher uma opção impede revisão.",
        (_COG, _BLIND, _MOTOR),
        "wcag322",
    ),
    _sc(
        "3.2.3",
        "Consistent Navigation",
        "Navegação consistente",
        _AA,
        _U,
        "Menus que mudam de posição entre páginas do mesmo portal aumentam a carga cognitiva.",
        (_COG, _BLIND, _LOW),
        "wcag323",
    ),
    _sc(
        "3.2.4",
        "Consistent Identification",
        "Identificação consistente",
        _AA,
        _U,
        "O mesmo ícone significando coisas diferentes em páginas distintas induz erro clínico.",
        (_COG, _BLIND),
        "wcag324",
    ),
    _sc(
        "3.3.1",
        "Error Identification",
        "Identificação de erro",
        _A,
        _U,
        "Erro sinalizado só por borda vermelha não é comunicado ao leitor de tela: "
        "o usuário reenvia o formulário indefinidamente.",
        (_BLIND, _COLOR, _COG),
        "wcag331",
        True,
    ),
    _sc(
        "3.3.2",
        "Labels or Instructions",
        "Rótulos ou instruções",
        _A,
        _U,
        "Campo sem rótulo é anunciado como 'caixa de edição em branco' — impossível "
        "saber se pede CPF ou cartão SUS.",
        (_BLIND, _COG, _LOW),
        "wcag332",
        True,
    ),
    _sc(
        "3.3.3",
        "Error Suggestion",
        "Sugestão de erro",
        _AA,
        _U,
        "Informar que há erro sem dizer qual é o formato esperado bloqueia o atendimento.",
        (_COG, _BLIND),
        "wcag333",
    ),
    _sc(
        "3.3.4",
        "Error Prevention (Legal, Financial, Data)",
        "Prevenção de erro (jurídico, financeiro, dados)",
        _AA,
        _U,
        "Cancelar uma consulta sem confirmação é irreversível e pode custar meses de espera.",
        (_COG, _MOTOR, _BLIND),
        "wcag334",
    ),
    # ------------------------------------------------------------------- 4. Robusto
    _sc(
        "4.1.1",
        "Parsing",
        "Análise",
        _A,
        _R,
        "IDs duplicados e marcação malformada quebram tecnologias assistivas de "
        "forma imprevisível. (Critério obsoleto na WCAG 2.2, mantido aqui porque "
        "a referência normativa brasileira ainda é a 2.1.)",
        (_BLIND, _MOTOR, _COG),
        "wcag411",
        True,
    ),
    _sc(
        "4.1.2",
        "Name, Role, Value",
        "Nome, função, valor",
        _A,
        _R,
        "Widgets construídos com ``<div>`` sem ARIA não existem para o leitor de "
        "tela: o botão 'Confirmar' simplesmente não é anunciado.",
        (_BLIND, _MOTOR, _G.SPEECH),
        "wcag412",
        True,
    ),
    _sc(
        "4.1.3",
        "Status Messages",
        "Mensagens de status",
        _AA,
        _R,
        "'Agendamento confirmado' exibido sem ``aria-live`` nunca chega a quem não vê a tela.",
        (_BLIND, _LOW, _COG),
        "wcag413",
        True,
    ),
)


@cache
def _index_by_id() -> dict[str, SuccessCriterion]:
    return {c.id: c for c in WCAG_CRITERIA}


@cache
def _index_by_axe_tag() -> dict[str, SuccessCriterion]:
    return {c.axe_tag: c for c in WCAG_CRITERIA if c.axe_tag}


def criterion(criterion_id: str) -> SuccessCriterion:
    """Recupera um critério pelo identificador oficial.

    Args:
        criterion_id: Numeração WCAG, ex. ``"1.4.3"``.

    Returns:
        O :class:`SuccessCriterion` correspondente.

    Raises:
        KeyError: Se o identificador não pertencer ao escopo A/AA modelado.
    """
    try:
        return _index_by_id()[criterion_id]
    except KeyError as exc:  # pragma: no cover - caminho de erro trivial
        raise KeyError(
            f"Critério WCAG desconhecido ou fora do escopo A/AA: {criterion_id!r}"
        ) from exc


def criterion_from_axe_tag(tag: str) -> SuccessCriterion | None:
    """Traduz uma tag do axe-core (``"wcag143"``) para o critério correspondente.

    Retorna ``None`` para tags que não denotam critério (``"cat.forms"``,
    ``"best-practice"``, ``"wcag2aa"``, ``"EN-301-549"``, ...). O chamador deve
    tratar ``None`` como "esta tag não contribui para o mapeamento normativo".
    """
    return _index_by_axe_tag().get(tag)


def criteria_by_level(level: ConformanceLevel) -> tuple[SuccessCriterion, ...]:
    """Todos os critérios de um dado nível de conformidade."""
    return tuple(c for c in WCAG_CRITERIA if c.level is level)


def principle_of(criterion_id: str) -> Principle:
    """Princípio POUR a que pertence o critério informado."""
    return criterion(criterion_id).principle
