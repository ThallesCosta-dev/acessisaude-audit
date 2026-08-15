"""Conexão com o banco e criação do esquema.

SQLite é o padrão e a escolha é metodológica, não de conveniência: o banco
inteiro é um arquivo único, versionável e transportável junto do artigo. Um
revisor que receba ``data/acessisaude.sqlite`` consegue reexecutar todas as
consultas sem provisionar servidor algum — condição prática para que a
reprodutibilidade seja real e não apenas declarada.

A camada usa SQLAlchemy Core/ORM sem Alembic no fluxo padrão: as tabelas são
criadas por :func:`init_database`. Migrações versionadas só se tornam
necessárias quando houver base em produção compartilhada; até lá, o caminho de
evolução é reconstruir o índice a partir dos documentos JSON, que são a fonte
da verdade.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from acessisaude_audit.logging_setup import get_logger
from acessisaude_audit.persistence.orm import Base

__all__ = ["create_database_engine", "init_database", "make_session_factory", "session_scope"]

logger = get_logger(__name__)


def create_database_engine(url: str, *, echo: bool = False) -> Engine:
    """Cria o engine SQLAlchemy com ajustes específicos de SQLite.

    Ajustes aplicados a SQLite:

    - ``PRAGMA foreign_keys=ON`` — sem isso, o SQLite ignora silenciosamente as
      chaves estrangeiras e a exclusão em cascata de achados não funciona.
    - ``PRAGMA journal_mode=WAL`` — permite que o dashboard leia enquanto uma
      varredura grava, evitando bloqueio durante coletas longas.

    Args:
        url: URL SQLAlchemy.
        echo: ``True`` registra todo SQL emitido (depuração).
    """
    is_sqlite = url.startswith("sqlite")
    if is_sqlite:
        path = url.replace("sqlite:///", "")
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        url,
        echo=echo,
        future=True,
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragmas(dbapi_connection: object, _record: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine


def init_database(engine: Engine) -> None:
    """Cria as tabelas ausentes. Idempotente."""
    Base.metadata.create_all(engine)
    logger.info("esquema do banco verificado", extra={"url": str(engine.url)})


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Fábrica de sessões vinculada ao engine."""
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Sessão transacional: confirma no sucesso, desfaz no erro.

    Uso::

        with session_scope(factory) as session:
            repo = ScanRepository(session)
            repo.save(scan)
    """
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
