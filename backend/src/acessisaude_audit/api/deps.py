"""Dependências injetáveis da API.

Recursos caros — engine de banco, catálogo YAML — são construídos uma única vez
por processo e injetados nas rotas. O catálogo em particular é lido do disco a
cada requisição *apenas* em modo de desenvolvimento: em produção, recarregá-lo a
cada chamada tornaria o desenho amostral mutável durante uma coleta em curso,
o que é exatamente o que a reprodutibilidade proíbe.
"""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from acessisaude_audit.catalog.loader import TargetCatalog, load_catalog
from acessisaude_audit.config import Settings, get_settings
from acessisaude_audit.persistence.database import (
    create_database_engine,
    init_database,
    make_session_factory,
)
from acessisaude_audit.persistence.repositories import JsonScanStore, ScanRepository

__all__ = [
    "get_catalog",
    "get_repository",
    "get_session",
    "get_settings_dep",
    "get_store",
    "require_target",
]


def get_settings_dep() -> Settings:
    """Configuração da aplicação."""
    return get_settings()


@lru_cache(maxsize=1)
def _session_factory() -> object:
    """Fábrica de sessões, criada e memoizada no primeiro uso."""
    settings = get_settings()
    settings.ensure_directories()
    engine = create_database_engine(settings.resolved_database_url())
    init_database(engine)
    return make_session_factory(engine)


def get_session() -> Iterator[Session]:
    """Sessão de banco por requisição, com confirmação ao final.

    A confirmação acontece aqui, e não nas rotas, para que nenhuma rota possa
    esquecer de confirmar e devolver 200 sobre uma transação descartada.
    """
    factory = _session_factory()
    session: Session = factory()  # type: ignore[operator]
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_repository(session: Session = Depends(get_session)) -> ScanRepository:
    """Repositório de varreduras vinculado à sessão da requisição."""
    return ScanRepository(session, params=get_settings().scoring_parameters())


@lru_cache(maxsize=1)
def get_catalog() -> TargetCatalog:
    """Catálogo de alvos, lido uma vez por processo."""
    return load_catalog(get_settings().catalog_path)


def get_store() -> JsonScanStore:
    """Armazenamento de varreduras em JSON."""
    return JsonScanStore(get_settings().scans_dir)


def require_target(target_id: str) -> object:
    """Resolve um alvo do catálogo ou devolve 404.

    Raises:
        HTTPException: 404 se o alvo não existir.
    """
    try:
        return get_catalog().get(target_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alvo não encontrado no catálogo: {target_id}",
        ) from exc
