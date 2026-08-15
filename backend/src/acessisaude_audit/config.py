"""Configuração da aplicação, carregada de ambiente e de ``.env``.

Princípio adotado: **nenhum parâmetro que afete um resultado publicável fica
implícito no código**. Tudo que altera um número do artigo — perfis de
dispositivo, limites de tempo, preço do megabyte, sementes — está aqui, é
serializável e viaja no ``config_snapshot`` de cada varredura.

Precedência: variáveis de ambiente > arquivo ``.env`` > padrões deste módulo.
Todas as variáveis usam o prefixo ``ACESSISAUDE_``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from acessisaude_audit.domain.models import Viewport
from acessisaude_audit.domain.scoring import ScoringParameters

__all__ = ["DEFAULT_VIEWPORTS", "Settings", "get_settings"]

#: Raiz do repositório (…/backend/src/acessisaude_audit/config.py → 4 níveis acima).
PROJECT_ROOT = Path(__file__).resolve().parents[3]

#: Perfis de dispositivo padrão da auditoria.
#:
#: A escolha dos dois perfis é metodológica, não técnica:
#:
#: - ``mobile-320`` é o mínimo exigido pelo critério 1.4.10 (Refluxo) e
#:   aproxima o aparelho de entrada predominante entre usuários de baixa renda.
#: - ``desktop-1366`` é a resolução de desktop mais comum no Brasil e o
#:   ambiente em que os portais costumam ser homologados — o contraste entre os
#:   dois perfis é, por si só, um achado do estudo.
DEFAULT_VIEWPORTS: tuple[Viewport, ...] = (
    Viewport(
        name="mobile-320",
        width=320,
        height=640,
        device_scale_factor=2.0,
        is_mobile=True,
        user_agent=(
            "Mozilla/5.0 (Linux; Android 10; SM-A105M) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ),
    ),
    Viewport(name="desktop-1366", width=1366, height=768, device_scale_factor=1.0),
)


class Settings(BaseSettings):
    """Parâmetros de execução da ferramenta."""

    model_config = SettingsConfigDict(
        env_prefix="ACESSISAUDE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ------------------------------------------------------------------ Caminhos
    project_root: Path = PROJECT_ROOT
    data_dir: Path = Field(
        default=PROJECT_ROOT / "data",
        description="Raiz dos artefatos gerados (varreduras, exportações).",
    )
    catalog_path: Path = Field(
        default=Path(__file__).resolve().parent / "catalog" / "targets.yaml",
        description="Catálogo YAML de alvos auditáveis.",
    )
    database_url: str = Field(
        default="",
        description=(
            "URL SQLAlchemy. Vazio resolve para SQLite em "
            "``data/acessisaude.sqlite`` — ver :meth:`resolved_database_url`."
        ),
    )

    # ---------------------------------------------------------------- Navegador
    browser: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description=(
            "Chromium é o padrão por ser o motor sobre o qual o axe-core é "
            "homologado e por permitir coleta de métricas de rede via CDP."
        ),
    )
    headless: bool = True
    navigation_timeout_ms: int = Field(
        default=30_000,
        ge=1_000,
        description="Tempo máximo de carregamento por página.",
    )
    settle_delay_ms: int = Field(
        default=1_500,
        ge=0,
        description=(
            "Espera após 'networkidle' para que scripts de hidratação terminem. "
            "Sem ela, SPAs são auditadas antes de renderizar e o resultado "
            "subestima as falhas."
        ),
    )
    locale: str = "pt-BR"
    timezone_id: str = "America/Sao_Paulo"

    # ---------------------------------------------------------------- Varredura
    max_pages_per_target: int = Field(
        default=25,
        ge=1,
        description=(
            "Teto de páginas por alvo. Limita a carga imposta a servidores "
            "públicos e mantém a amostra comparável entre portais de tamanhos "
            "muito diferentes."
        ),
    )
    max_crawl_depth: int = Field(default=2, ge=0)
    request_delay_ms: int = Field(
        default=2_000,
        ge=0,
        description=(
            "Intervalo mínimo entre requisições ao mesmo host. Conduta ética "
            "obrigatória ao auditar infraestrutura pública em produção — ver "
            "``docs/metodologia/etica-e-conduta-de-coleta.md``."
        ),
    )
    concurrency: int = Field(
        default=1,
        ge=1,
        le=8,
        description=(
            "Páginas auditadas em paralelo. O padrão 1 é conservador por "
            "escolha ética; elevar apenas contra fixtures locais."
        ),
    )
    respect_robots_txt: bool = Field(
        default=True,
        description=(
            "Desativar exige justificativa registrada. A ferramenta se recusa a "
            "ignorar robots.txt sem que ``robots_override_reason`` seja informado."
        ),
    )
    robots_override_reason: str = ""
    user_agent_suffix: str = Field(
        default=(
            "AcessiSaudeAudit/0.1 (+pesquisa academica; contato: thalles.costa@ioc.fiocruz.br)"
        ),
        description=(
            "Identificação anexada ao User-Agent. Auditar sem se identificar "
            "seria conduta de coleta inaceitável em pesquisa."
        ),
    )
    capture_screenshots: bool = True
    max_html_snippet_chars: int = Field(
        default=400,
        ge=80,
        description="Truncamento do HTML de evidência, para conter o tamanho do dataset.",
    )

    # ----------------------------------------------------------------- axe-core
    axe_tags: tuple[str, ...] = Field(
        default=("wcag2a", "wcag2aa", "wcag21a", "wcag21aa"),
        description=(
            "Conjuntos de regras do axe-core. Exclui 'best-practice' de "
            "propósito: recomendações sem lastro normativo não podem sustentar "
            "afirmação de violação legal."
        ),
    )
    axe_script_path: Path | None = Field(
        default=None,
        description="Caminho para axe.min.js. Nulo usa a cópia vendorizada.",
    )

    # ------------------------------------------------------------------ Índices
    friction_kappa: float = Field(
        default=150.0,
        gt=0,
        description=(
            "Constante de saturação do IAN, calibrada empiricamente sobre o "
            "conjunto de validação. Ver ScoringParameters.friction_kappa: "
            "alterá-la muda todos os índices publicados e exige recalibração "
            "documentada."
        ),
    )
    critical_path_multiplier: float = 1.5
    price_per_mb_brl: float = Field(
        default=0.10,
        gt=0,
        description=(
            "Preço de referência do MB em plano pré-pago brasileiro. Valor "
            "padrão é ilustrativo: substituir pelo preço coletado e citar a "
            "fonte na seção de Métodos antes de publicar."
        ),
    )
    franchise_mb: float = Field(default=2048.0, gt=0)
    heavy_page_mb: float = Field(default=2.0, gt=0)

    # ---------------------------------------------------------------------- API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    # -------------------------------------------------------------------- Outros
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    random_seed: int = Field(
        default=42,
        description="Semente para qualquer amostragem — requisito de reprodutibilidade.",
    )

    @field_validator("robots_override_reason")
    @classmethod
    def _require_reason_when_ignoring_robots(cls, v: str, info: Any) -> str:
        """Impede desativar ``robots.txt`` sem justificativa registrada."""
        respect = info.data.get("respect_robots_txt", True)
        if not respect and not v.strip():
            raise ValueError(
                "respect_robots_txt=False exige ACESSISAUDE_ROBOTS_OVERRIDE_REASON "
                "com a justificativa da coleta (será registrada no dataset)."
            )
        return v

    @property
    def scans_dir(self) -> Path:
        """Diretório dos JSON de varredura."""
        return self.data_dir / "scans"

    @property
    def exports_dir(self) -> Path:
        """Diretório de relatórios e exportações."""
        return self.data_dir / "exports"

    @property
    def screenshots_dir(self) -> Path:
        """Diretório de capturas de tela de evidência."""
        return self.data_dir / "screenshots"

    def resolved_database_url(self) -> str:
        """URL de banco efetiva, com SQLite local como padrão."""
        if self.database_url:
            return self.database_url
        return f"sqlite:///{(self.data_dir / 'acessisaude.sqlite').as_posix()}"

    def scoring_parameters(self) -> ScoringParameters:
        """Constrói os parâmetros de índice a partir da configuração."""
        return ScoringParameters(
            friction_kappa=self.friction_kappa,
            critical_path_multiplier=self.critical_path_multiplier,
            price_per_mb_brl=self.price_per_mb_brl,
            franchise_mb=self.franchise_mb,
            heavy_page_mb=self.heavy_page_mb,
        )

    def viewports(self) -> tuple[Viewport, ...]:
        """Perfis de dispositivo da auditoria."""
        return DEFAULT_VIEWPORTS

    def ensure_directories(self) -> None:
        """Cria os diretórios de saída, se necessário."""
        for path in (self.data_dir, self.scans_dir, self.exports_dir, self.screenshots_dir):
            path.mkdir(parents=True, exist_ok=True)

    def snapshot(self) -> dict[str, Any]:
        """Parâmetros que afetam resultados, para gravar junto da varredura.

        Deliberadamente **não** inclui caminhos locais nem host/porta da API:
        esses não alteram nenhum número e só poluiriam o dataset com dados do
        ambiente do pesquisador.
        """
        return {
            "browser": self.browser,
            "headless": self.headless,
            "navigation_timeout_ms": self.navigation_timeout_ms,
            "settle_delay_ms": self.settle_delay_ms,
            "locale": self.locale,
            "timezone_id": self.timezone_id,
            "max_pages_per_target": self.max_pages_per_target,
            "max_crawl_depth": self.max_crawl_depth,
            "request_delay_ms": self.request_delay_ms,
            "concurrency": self.concurrency,
            "respect_robots_txt": self.respect_robots_txt,
            "robots_override_reason": self.robots_override_reason,
            "axe_tags": list(self.axe_tags),
            "viewports": [v.model_dump() for v in self.viewports()],
            "scoring": self.scoring_parameters().as_dict(),
            "random_seed": self.random_seed,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instância única de configuração (memoizada).

    Testes que precisem de outra configuração devem instanciar :class:`Settings`
    diretamente em vez de limpar este cache.
    """
    return Settings()
