"""Roteadores da API, agrupados por recurso."""

from acessisaude_audit.api.routers import reference, scans, targets

__all__ = ["reference", "scans", "targets"]
