"""Aplicação FastAPI que serve o dashboard.

A API é uma casca fina sobre o domínio: ela não calcula índice, não interpreta
norma e não decide o que é violação. Sua responsabilidade é expor, com contrato
estável e documentado, o que as demais camadas produzem.

O OpenAPI gerado aqui é a fonte de tipos do frontend (ver
``frontend/src/lib/api.ts``), o que elimina a divergência entre o que o servidor
envia e o que o cliente espera.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from acessisaude_audit import __version__
from acessisaude_audit.api.routers import reference, scans, targets
from acessisaude_audit.config import get_settings
from acessisaude_audit.logging_setup import configure_logging, get_logger
from acessisaude_audit.persistence.database import create_database_engine, init_database

__all__ = ["create_app"]

logger = get_logger(__name__)

_DESCRIPTION = """
Auditoria contínua de acessibilidade web em plataformas públicas de saúde,
avaliada contra a **WCAG 2.1 (A e AA)** e vinculada ao ordenamento jurídico
brasileiro — **Lei 13.146/2015 (LBI)**, Constituição Federal, Convenção da ONU
sobre os Direitos das Pessoas com Deficiência, LAI, Decreto 5.296/2004 e eMAG.

### O que esta API entrega

* **`/referencia`** — a matriz WCAG↔LBI como dado consultável: cada critério
  com seu risco jurídico, sua tese e os dispositivos invocáveis.
* **`/alvos`** — o desenho amostral do estudo, com a justificativa de seleção de
  cada plataforma e as lacunas declaradas da amostra.
* **`/varreduras`** — execução, resultados, índices, relatório HTML acessível e
  exportação tabular.

### Limites que a API declara em toda resposta

A verificação automática cobre parte dos 50 critérios A/AA; os demais exigem
julgamento humano. **Ausência de achado não é conformidade.** O campo
`coverage` acompanha todo conjunto de índices, e achados indeterminados são
devolvidos como `incomplete`, jamais convertidos em violação.

Os relatórios são instrumento de auditoria técnica e de pesquisa. Não
constituem parecer jurídico nem prova pericial.
"""


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Prepara diretórios e esquema de banco na subida do servidor."""
    settings = get_settings()
    configure_logging(settings.log_level)
    settings.ensure_directories()
    engine = create_database_engine(settings.resolved_database_url())
    init_database(engine)
    logger.info(
        "API iniciada",
        extra={"versao": __version__, "banco": settings.resolved_database_url()},
    )
    yield
    engine.dispose()
    logger.info("API encerrada")


def create_app() -> FastAPI:
    """Constrói a aplicação com rotas, CORS e metadados."""
    settings = get_settings()

    app = FastAPI(
        title="AcessiSaúde-Audit",
        version=__version__,
        description=_DESCRIPTION,
        summary=(
            "Auditoria algorítmica de acessibilidade e direitos digitais em "
            "plataformas públicas de saúde."
        ),
        lifespan=_lifespan,
        contact={
            "name": "Thalles Costa",
            "email": "thalles.costa@ioc.fiocruz.br",
        },
        license_info={"name": "AGPL-3.0-or-later"},
        openapi_tags=[
            {
                "name": "referência normativa",
                "description": (
                    "Critérios WCAG 2.1, dispositivos legais brasileiros e a matriz "
                    "de correspondência entre eles."
                ),
            },
            {
                "name": "alvos",
                "description": "Catálogo de plataformas auditáveis e desenho amostral.",
            },
            {
                "name": "varreduras",
                "description": "Execução de auditorias, resultados, índices e relatórios.",
            },
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
    )

    app.include_router(reference.router)
    app.include_router(targets.router)
    app.include_router(scans.router)

    @app.get("/saude", tags=["operação"], summary="Verificação de disponibilidade")
    def health() -> dict[str, object]:
        """Estado do serviço e das dependências que a coleta exige.

        Reporta explicitamente se o ``axe.min.js`` vendorizado está presente:
        sem ele, a API sobe normalmente mas toda varredura produziria resultado
        vazio — falha silenciosa que este endpoint torna visível.
        """
        from acessisaude_audit.auditor.axe_runner import vendored_axe_path

        try:
            axe_ok = vendored_axe_path().is_file()
            axe_erro = None
        except FileNotFoundError as exc:
            axe_ok, axe_erro = False, str(exc)

        return {
            "status": "ok" if axe_ok else "degradado",
            "versao": __version__,
            "axe_core_disponivel": axe_ok,
            "axe_core_erro": axe_erro,
            "navegador": settings.browser,
            "respeita_robots_txt": settings.respect_robots_txt,
        }

    return app


#: Instância usada por ``uvicorn acessisaude_audit.api.app:app``.
app = create_app()
