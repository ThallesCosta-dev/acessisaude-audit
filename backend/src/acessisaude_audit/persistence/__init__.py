"""Camada de persistência: documento JSON como verdade, SQL como índice."""

from acessisaude_audit.persistence.database import (
    create_database_engine,
    init_database,
    make_session_factory,
    session_scope,
)
from acessisaude_audit.persistence.orm import Base, FindingRow, ScanRow
from acessisaude_audit.persistence.repositories import JsonScanStore, ScanRepository

__all__ = [
    "Base",
    "FindingRow",
    "JsonScanStore",
    "ScanRepository",
    "ScanRow",
    "create_database_engine",
    "init_database",
    "make_session_factory",
    "session_scope",
]
