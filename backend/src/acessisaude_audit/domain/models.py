"""Modelos de dados do domínio de auditoria.

Todos os modelos são Pydantic v2, o que dá simultaneamente: validação na
fronteira do sistema, serialização estável para o JSON persistido em
``data/scans/`` e geração automática do schema OpenAPI consumido pelo frontend.

Contrato de estabilidade
------------------------
O JSON produzido por :class:`ScanResult` é o **artefato de pesquisa** do
projeto: é ele que sustenta a reprodutibilidade das análises do artigo. Alterar
a forma desses modelos quebra datasets já coletados. Toda mudança
incompatível exige incremento de :data:`SCHEMA_VERSION` e uma entrada em
``docs/adr/``. Ver ``docs/metodologia/reprodutibilidade.md``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field

from acessisaude_audit.domain.mapping import LegalRisk, mapping_for
from acessisaude_audit.domain.wcag import DeficiencyGroup

__all__ = [
    "SCHEMA_VERSION",
    "EvidenceNode",
    "Finding",
    "FindingSource",
    "Impact",
    "NetworkMetrics",
    "Outcome",
    "PageAudit",
    "PageStatus",
    "ScanResult",
    "ScanStatus",
    "Viewport",
    "utcnow",
]

#: Versão do esquema de dados persistido. Incrementar em toda mudança incompatível.
SCHEMA_VERSION = "1.0.0"


def utcnow() -> datetime:
    """Instante atual em UTC, com fuso explícito.

    Centralizado para que os testes possam congelar o tempo em um único ponto e
    para garantir que nenhum ``datetime`` ingênuo entre no dataset.
    """
    return datetime.now(UTC)


class Impact(StrEnum):
    """Gravidade **técnica** da falha, na escala do axe-core.

    Mantida separada de :class:`~acessisaude_audit.domain.mapping.LegalRisk`
    (gravidade jurídica) de propósito: uma falha tecnicamente 'minor' pode ser
    juridicamente crítica se ocorrer no botão de confirmação de uma consulta.
    """

    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"

    @property
    def weight(self) -> float:
        """Peso técnico usado nos índices agregados."""
        return {
            Impact.CRITICAL: 10.0,
            Impact.SERIOUS: 6.0,
            Impact.MODERATE: 3.0,
            Impact.MINOR: 1.0,
        }[self]


class Outcome(StrEnum):
    """Veredito de uma verificação, alinhado ao vocabulário EARL do W3C."""

    PASS = "pass"
    FAIL = "fail"
    INCOMPLETE = "incomplete"
    """Requer revisão humana: a máquina detectou indício, não violação."""
    INAPPLICABLE = "inapplicable"


class FindingSource(StrEnum):
    """Origem da verificação — essencial para a seção de Métodos do artigo."""

    AXE_CORE = "axe-core"
    """Regra determinística do axe-core (Deque Systems)."""
    PROBE = "probe"
    """Sonda própria deste projeto (ver ``auditor/probes/``)."""
    HEURISTIC = "heuristic"
    """Indício estatístico ou heurístico: sempre gera ``INCOMPLETE``."""
    MANUAL = "manual"
    """Registro inserido por avaliador humano na revisão assistida."""


class ScanStatus(StrEnum):
    """Ciclo de vida de uma varredura."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    """Concluída, mas com uma ou mais páginas em erro — o dataset é utilizável
    desde que a taxa de perda seja reportada."""


class PageStatus(StrEnum):
    """Resultado do carregamento de uma página."""

    OK = "ok"
    HTTP_ERROR = "http_error"
    TIMEOUT = "timeout"
    BLOCKED_BY_ROBOTS = "blocked_by_robots"
    NAVIGATION_ERROR = "navigation_error"


class Viewport(BaseModel):
    """Dimensões e características do dispositivo simulado.

    A auditoria roda em ao menos dois perfis (ver ``config.py``): um desktop
    padrão e um celular de baixo custo em 320 CSS px, este último indispensável
    para avaliar o critério 1.4.10 (Refluxo) e o custo em dados móveis.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Rótulo do perfil, ex. 'mobile-320'.")
    width: int = Field(gt=0, description="Largura em CSS px.")
    height: int = Field(gt=0, description="Altura em CSS px.")
    device_scale_factor: float = Field(default=1.0, gt=0)
    is_mobile: bool = False
    user_agent: str | None = None

    def __str__(self) -> str:
        return f"{self.name} ({self.width}x{self.height})"


class EvidenceNode(BaseModel):
    """O elemento concreto do DOM em que a falha foi observada.

    É a prova material do achado. Sem ela, o relatório é uma alegação; com ela,
    o gestor consegue localizar e corrigir o defeito.
    """

    selector: str = Field(description="Seletor CSS até o elemento.")
    html: str = Field(
        default="",
        description="Trecho do HTML do elemento, truncado para não inflar o dataset.",
    )
    failure_summary: str = Field(
        default="", description="Explicação do axe-core sobre por que o nó falhou."
    )
    target_frame: list[str] = Field(
        default_factory=list,
        description="Cadeia de iframes até o elemento, quando aninhado.",
    )
    measured: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Valores medidos que embasam o veredito, ex. "
            "{'contrast_ratio': 2.91, 'required': 4.5, 'fg': '#8a8a8a', 'bg': '#ffffff'}."
        ),
    )


class Finding(BaseModel):
    """Um achado de auditoria: a unidade fundamental de análise do projeto.

    Cada instância une três camadas — técnica (``rule_id``, ``impact``),
    normativa (``criteria``) e jurídica (``legal_risk``, ``legal_thesis``) — de
    modo que nenhum resultado do artigo precise reconstruir esse vínculo a
    posteriori.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: UUID = Field(default_factory=uuid4)
    rule_id: str = Field(
        description="Identificador da regra, ex. 'color-contrast' ou 'probe.reflow-320'."
    )
    source: FindingSource
    outcome: Outcome
    impact: Impact | None = Field(default=None, description="Nulo quando o resultado não é FAIL.")
    criteria: list[str] = Field(
        default_factory=list,
        description="Critérios WCAG 2.1 violados, ex. ['1.4.3'].",
    )
    summary: str = Field(description="Uma frase: o que está errado.")
    description: str = Field(
        default="", description="Explicação estendida, em linguagem de gestor público."
    )
    remediation: str = Field(default="", description="Conduta corretiva esperada.")
    help_url: str | None = None
    affects: list[DeficiencyGroup] = Field(
        default_factory=list, description="Grupos impactados pela barreira."
    )
    nodes: list[EvidenceNode] = Field(
        default_factory=list, description="Elementos em que a falha foi observada."
    )
    page_url: str = Field(default="", description="URL em que o achado ocorreu.")
    viewport: str = Field(default="", description="Perfil de dispositivo usado.")
    detected_at: datetime = Field(default_factory=utcnow)

    # ------------------------------------------------------------------------
    # Camada jurídica explícita.
    #
    # Normalmente a fundamentação é *derivada* dos critérios WCAG violados, via
    # `domain.mapping`. Os campos abaixo existem para o caso — real neste
    # projeto — de barreiras que não correspondem a nenhum critério WCAG mas
    # que ainda assim obstruem o acesso ao serviço de saúde: o custo em dados
    # móveis, por exemplo, exclui o usuário periférico sem violar critério
    # técnico algum. Sem esses campos, a ferramenta só saberia falar de
    # deficiência, e o recorte de direitos digitais ficaria de fora.
    # ------------------------------------------------------------------------
    legal_risk_override: LegalRisk | None = Field(
        default=None,
        description="Risco jurídico declarado pela sonda, quando não derivável de critério.",
    )
    extra_provisions: list[str] = Field(
        default_factory=list,
        description="Chaves de dispositivos normativos adicionais (ver domain.lbi).",
    )
    legal_thesis_override: str | None = Field(
        default=None, description="Proposição jurídica específica deste achado."
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def occurrences(self) -> int:
        """Quantos elementos distintos apresentam esta falha na página.

        Reportar ocorrências separadamente do número de achados evita o viés
        clássico de contagem: uma página com 400 links sem texto acessível não
        é 400 vezes pior do que uma com 4 — é o mesmo defeito de template.
        """
        return len(self.nodes)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def legal_risk(self) -> LegalRisk | None:
        """Maior risco jurídico entre o override da sonda e os critérios violados."""
        risks = [m.legal_risk for c in self.criteria if (m := mapping_for(c))]
        if self.legal_risk_override is not None:
            risks.append(self.legal_risk_override)
        if not risks:
            return None
        return max(risks, key=lambda r: r.weight)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def legal_provisions(self) -> list[str]:
        """Chaves dos dispositivos normativos invocáveis, sem repetição."""
        seen: dict[str, None] = {}
        for c in self.criteria:
            if (m := mapping_for(c)) is not None:
                for key in m.provision_keys:
                    seen.setdefault(key, None)
        for key in self.extra_provisions:
            seen.setdefault(key, None)
        return list(seen)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def legal_thesis(self) -> str | None:
        """Proposição jurídica de maior peso aplicável ao achado.

        A tese declarada pela sonda tem precedência sobre a derivada do
        mapeamento: quando a sonda escreve uma tese, ela conhece o contexto
        específico da barreira, ao passo que o mapeamento só conhece o critério.
        """
        if self.legal_thesis_override:
            return self.legal_thesis_override
        best: tuple[float, str] | None = None
        for c in self.criteria:
            if (m := mapping_for(c)) is not None:
                candidate = (m.legal_risk.weight, m.thesis)
                if best is None or candidate[0] > best[0]:
                    best = candidate
        return best[1] if best else None

    @property
    def is_violation(self) -> bool:
        """``True`` apenas para vereditos de falha confirmada."""
        return self.outcome is Outcome.FAIL


class NetworkMetrics(BaseModel):
    """Custo de rede da página — a dimensão do *usuário periférico*.

    Motivação: no recorte deste projeto, a barreira de acesso ao serviço público
    de saúde não é apenas sensorial. Um portal que exige 6 MB para exibir a tela
    de agendamento consome, em um plano pré-pago típico, uma fração relevante da
    franquia mensal. A ferramenta quantifica isso para que o argumento jurídico
    de restrição de acesso (art. 196, CF/88) tenha lastro empírico.
    """

    total_bytes: int = Field(default=0, ge=0, description="Bytes transferidos (comprimidos).")
    total_uncompressed_bytes: int = Field(default=0, ge=0)
    request_count: int = Field(default=0, ge=0)
    bytes_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="Bytes por tipo de recurso (document, script, image, font, ...).",
    )
    third_party_bytes: int = Field(
        default=0,
        ge=0,
        description=(
            "Bytes provenientes de domínios distintos do alvo. Relevante porque "
            "trackers de terceiros oneram o usuário sem lhe entregar serviço."
        ),
    )
    third_party_domains: list[str] = Field(default_factory=list)
    dom_content_loaded_ms: float | None = Field(default=None, ge=0)
    load_complete_ms: float | None = Field(default=None, ge=0)
    largest_contentful_paint_ms: float | None = Field(default=None, ge=0)
    blocked_requests: int = Field(default=0, ge=0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_mb(self) -> float:
        """Peso total em megabytes (base 1024), arredondado a 3 casas."""
        return round(self.total_bytes / (1024 * 1024), 3)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def third_party_share(self) -> float:
        """Fração do tráfego atribuível a terceiros, em [0, 1]."""
        if self.total_bytes == 0:
            return 0.0
        return round(self.third_party_bytes / self.total_bytes, 4)

    def data_cost_brl(self, price_per_mb_brl: float) -> float:
        """Custo estimado, em reais, para carregar a página uma vez.

        Args:
            price_per_mb_brl: Preço do megabyte no plano de referência. O valor
                usado no estudo e sua fonte estão em ``config.py`` e são
                declarados na seção de Métodos do artigo — nunca embutidos aqui.

        Returns:
            Custo em BRL, arredondado a 4 casas decimais.
        """
        return round(self.total_mb * price_per_mb_brl, 4)

    def franchise_share(self, franchise_mb: float) -> float:
        """Fração da franquia mensal de dados consumida em um único acesso."""
        if franchise_mb <= 0:
            return 0.0
        return round(self.total_mb / franchise_mb, 6)


class PageAudit(BaseModel):
    """Resultado da auditoria de uma única página em um único viewport."""

    url: str
    final_url: str = Field(default="", description="URL após redirecionamentos.")
    status: PageStatus = PageStatus.OK
    http_status: int | None = None
    title: str | None = None
    lang: str | None = None
    viewport: Viewport
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None
    findings: list[Finding] = Field(default_factory=list)
    network: NetworkMetrics = Field(default_factory=NetworkMetrics)
    error: str | None = Field(default=None, description="Mensagem em caso de falha.")
    axe_version: str | None = None
    screenshot_path: str | None = None
    is_critical_path: bool = Field(
        default=False,
        description=(
            "Página pertencente a um fluxo essencial declarado no catálogo "
            "(login, agendamento, resultado de exame). Eleva o risco jurídico."
        ),
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_ms(self) -> float | None:
        """Duração da auditoria da página, em milissegundos."""
        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds() * 1000

    @property
    def violations(self) -> list[Finding]:
        """Apenas os achados com veredito de falha."""
        return [f for f in self.findings if f.is_violation]

    @property
    def incomplete(self) -> list[Finding]:
        """Achados que exigem revisão humana."""
        return [f for f in self.findings if f.outcome is Outcome.INCOMPLETE]

    @property
    def violated_criteria(self) -> set[str]:
        """Conjunto de critérios WCAG efetivamente violados na página."""
        return {c for f in self.violations for c in f.criteria}


class ScanResult(BaseModel):
    """Uma varredura completa de um alvo: a unidade de persistência e de análise.

    O objeto serializado em JSON é o dado bruto do estudo. Ele carrega a
    configuração usada (``config_snapshot``) para que qualquer resultado do
    artigo possa ser reexecutado com os mesmos parâmetros.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: UUID = Field(default_factory=uuid4)
    schema_version: str = SCHEMA_VERSION
    target_id: str = Field(description="Identificador do alvo no catálogo.")
    target_name: str = ""
    base_url: str = ""
    status: ScanStatus = ScanStatus.PENDING
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None
    pages: list[PageAudit] = Field(default_factory=list)
    engine_version: str = Field(default="", description="Versão do AcessiSaúde-Audit.")
    axe_version: str | None = None
    browser: str = Field(default="", description="Navegador e versão usados.")
    config_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Parâmetros de execução, para reprodutibilidade.",
    )
    errors: list[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def page_count(self) -> int:
        """Quantidade de auditorias de página (URL × viewport)."""
        return len(self.pages)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def violation_count(self) -> int:
        """Total de achados com veredito de falha em toda a varredura."""
        return sum(len(p.violations) for p in self.pages)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def occurrence_count(self) -> int:
        """Total de elementos do DOM em situação de falha."""
        return sum(f.occurrences for p in self.pages for f in p.violations)

    @property
    def successful_pages(self) -> list[PageAudit]:
        """Páginas efetivamente auditadas (exclui timeouts e erros de navegação)."""
        return [p for p in self.pages if p.status is PageStatus.OK]

    @property
    def loss_rate(self) -> float:
        """Fração de páginas perdidas por erro — deve ser reportada no artigo."""
        if not self.pages:
            return 0.0
        return round(1 - len(self.successful_pages) / len(self.pages), 4)


#: Alias com validação de URL, usado nas fronteiras da API onde a origem é externa.
ValidatedUrl = Annotated[HttpUrl, Field(description="URL absoluta com esquema http(s).")]
