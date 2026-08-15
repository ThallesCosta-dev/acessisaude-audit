"""Catálogo de alvos auditáveis.

O catálogo é um artefato **de pesquisa**, não de configuração: ele materializa
o desenho amostral do estudo. Por isso mora em YAML versionado, com campos que
respondem às perguntas que um revisor fará — qual a esfera de governo, qual o
serviço prestado, por que estas páginas e não outras, o alvo exige autenticação
(e portanto restringe o que pode ser auditado sem viés).

Ver ``docs/metodologia/amostragem.md`` para o critério de seleção e
``docs/metodologia/etica-e-conduta-de-coleta.md`` para as regras de conduta.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = [
    "GovernmentSphere",
    "SeedPage",
    "ServiceCategory",
    "Target",
    "TargetCatalog",
    "load_catalog",
]


class GovernmentSphere(StrEnum):
    """Esfera federativa responsável pelo serviço.

    Determina quem é o sujeito obrigado no achado jurídico e qual órgão de
    controle é competente (TCU para federal, TCE para estadual/municipal).
    """

    FEDERAL = "federal"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"
    CONSORCIO = "consorcio"
    PRIVADO_CONVENIADO = "privado_conveniado"
    """Prestador privado que executa serviço público de saúde — alcançado pelo
    art. 63 da LBI por atuar como delegatário."""


class ServiceCategory(StrEnum):
    """Natureza do serviço digital oferecido.

    Usada para estratificar a análise: espera-se que serviços transacionais
    (agendamento) apresentem perfil de barreira distinto do informacional.
    """

    INFORMACIONAL = "informacional"
    AGENDAMENTO = "agendamento"
    RESULTADO_EXAME = "resultado_exame"
    PRONTUARIO = "prontuario"
    CADASTRO = "cadastro"
    TELEATENDIMENTO = "teleatendimento"
    MEDICAMENTOS = "medicamentos"
    OUVIDORIA = "ouvidoria"
    TRANSPARENCIA = "transparencia"


class SeedPage(BaseModel):
    """Uma URL de partida declarada explicitamente no catálogo.

    Sementes explícitas são preferíveis à descoberta automática: elas tornam a
    amostra reproduzível e permitem justificar, no artigo, por que cada página
    entrou no estudo.
    """

    model_config = ConfigDict(frozen=True)

    url: str
    label: str = Field(description="Nome do passo no fluxo do usuário.")
    critical: bool = Field(
        default=False,
        description=(
            "Página de fluxo essencial (login, agendamento, resultado). Eleva o "
            "peso do atrito e o risco jurídico dos achados."
        ),
    )
    requires_auth: bool = Field(
        default=False,
        description=(
            "Exige credenciais. Páginas assim **não** são varridas: auditar "
            "área autenticada de sistema público sem autorização formal é "
            "inadmissível. Ficam registradas como lacuna declarada da amostra."
        ),
    )
    notes: str = ""

    @field_validator("url")
    @classmethod
    def _must_be_absolute_http(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Semente deve ser URL http(s) absoluta: {v!r}")
        return v


class Target(BaseModel):
    """Uma plataforma digital de saúde sob auditoria."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(description="Identificador estável, ex. 'conecte-sus-web'.")
    name: str
    organization: str = Field(description="Órgão ou entidade mantenedora.")
    sphere: GovernmentSphere
    categories: list[ServiceCategory] = Field(default_factory=list)
    base_url: str
    seeds: list[SeedPage] = Field(default_factory=list)
    enabled: bool = Field(
        default=True,
        description="Alvos desabilitados permanecem documentados, mas não são varridos.",
    )
    territory: str = Field(default="", description="Recorte territorial, ex. 'RJ/Capital'.")
    population_served: int | None = Field(
        default=None,
        description=(
            "População de referência atendida. Permite ponderar o impacto do "
            "achado — a mesma falha atinge escalas distintas."
        ),
    )
    selection_rationale: str = Field(
        default="",
        description="Por que este alvo integra a amostra. Obrigatório para o artigo.",
    )
    robots_note: str = ""
    tags: list[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _slug(cls, v: str) -> str:
        if not v or not all(ch.isalnum() or ch in "-_" for ch in v):
            raise ValueError(f"id deve ser um slug alfanumérico com - ou _: {v!r}")
        return v

    @field_validator("base_url")
    @classmethod
    def _absolute(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"base_url deve ser URL http(s) absoluta: {v!r}")
        return v.rstrip("/")

    @model_validator(mode="after")
    def _at_least_one_auditable_seed(self) -> Target:
        if self.enabled and not self.auditable_seeds:
            raise ValueError(
                f"Alvo {self.id!r} está habilitado mas não tem semente auditável "
                "(todas exigem autenticação ou a lista está vazia)."
            )
        return self

    @property
    def host(self) -> str:
        """Host do ``base_url``, usado no controle de taxa por domínio."""
        return urlparse(self.base_url).netloc

    @property
    def auditable_seeds(self) -> list[SeedPage]:
        """Sementes efetivamente varríveis (exclui as que exigem autenticação)."""
        return [s for s in self.seeds if not s.requires_auth]

    @property
    def declared_gaps(self) -> list[SeedPage]:
        """Sementes excluídas por exigirem autenticação — lacunas da amostra.

        Reportá-las é obrigatório: o portal pode ter suas piores barreiras
        exatamente atrás do login, e omitir isso enviesaria a conclusão para
        melhor.
        """
        return [s for s in self.seeds if s.requires_auth]


class TargetCatalog(BaseModel):
    """Coleção de alvos com metadados do desenho amostral."""

    model_config = ConfigDict(frozen=True)

    version: str = "1"
    description: str = ""
    collection_window: str = Field(
        default="",
        description=(
            "Janela temporal de coleta declarada, ex. '2026-08-01 a 2026-08-31'. "
            "Portais mudam; sem a janela, o dado não é interpretável."
        ),
    )
    targets: list[Target] = Field(default_factory=list)

    @property
    def enabled_targets(self) -> list[Target]:
        """Alvos habilitados para varredura."""
        return [t for t in self.targets if t.enabled]

    def get(self, target_id: str) -> Target:
        """Recupera um alvo pelo identificador.

        Raises:
            KeyError: Se o alvo não existir no catálogo.
        """
        for t in self.targets:
            if t.id == target_id:
                return t
        raise KeyError(f"Alvo não encontrado no catálogo: {target_id!r}")

    @model_validator(mode="after")
    def _unique_ids(self) -> TargetCatalog:
        seen: set[str] = set()
        for t in self.targets:
            if t.id in seen:
                raise ValueError(f"id de alvo duplicado no catálogo: {t.id!r}")
            seen.add(t.id)
        return self


def load_catalog(path: str | Path) -> TargetCatalog:
    """Carrega e valida o catálogo YAML.

    Args:
        path: Caminho do arquivo ``targets.yaml``.

    Returns:
        O catálogo validado.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se o YAML for inválido ou violar as regras do modelo.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Catálogo de alvos não encontrado: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Catálogo deve ser um mapeamento YAML: {p}")
    return TargetCatalog.model_validate(raw)
