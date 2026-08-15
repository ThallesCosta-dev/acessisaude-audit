"""Configuração de log estruturado.

A auditoria é uma coleta de dados de pesquisa: o log é o registro de campo. Ele
precisa dizer, sem ambiguidade, qual URL foi acessada, quando, com qual perfil
de dispositivo e com que resultado — inclusive quando algo falha. Um log
solto em ``print`` inviabilizaria auditar a própria auditoria.

Saída em JSON por linha (JSONL), o que permite analisar a execução com as mesmas
ferramentas usadas para analisar os resultados.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

__all__ = ["configure_logging", "get_logger"]

#: Campos padrão de :class:`logging.LogRecord`, excluídos do bloco de contexto.
_RESERVED = frozenset(
    [
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    ]
)


class JsonLineFormatter(logging.Formatter):
    """Formata cada registro como um objeto JSON em uma linha."""

    def format(self, record: logging.LogRecord) -> str:
        """Serializa o registro como um objeto JSON de linha única."""
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "nivel": record.levelname,
            "origem": record.name,
            "mensagem": record.getMessage(),
        }
        # Qualquer chave passada via `extra=` entra como contexto do evento.
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["excecao"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class HumanFormatter(logging.Formatter):
    """Formato legível para uso interativo no terminal."""

    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro em uma linha legível, com o contexto ao final."""
        ts = datetime.fromtimestamp(record.created, tz=UTC).strftime("%H:%M:%S")
        context = {
            k: v for k, v in record.__dict__.items() if k not in _RESERVED and not k.startswith("_")
        }
        suffix = f"  {context}" if context else ""
        base = f"{ts} {record.levelname:<7} {record.name:<38} {record.getMessage()}{suffix}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def configure_logging(level: str = "INFO", *, json_output: bool = False) -> None:
    """Instala o handler raiz da aplicação.

    Idempotente: chamadas repetidas substituem os handlers em vez de duplicá-los,
    o que evita linhas triplicadas quando a CLI e a API são carregadas juntas.

    Args:
        level: Nível mínimo (``"DEBUG"``, ``"INFO"``, ...).
        json_output: ``True`` para JSONL (execuções não interativas e CI),
            ``False`` para o formato legível.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonLineFormatter() if json_output else HumanFormatter())

    root = logging.getLogger("acessisaude_audit")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False

    # O Playwright é verboso em DEBUG e afogaria o registro de campo.
    logging.getLogger("playwright").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Logger nomeado sob a hierarquia da aplicação."""
    return logging.getLogger(name)
