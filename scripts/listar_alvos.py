"""Lista os identificadores dos alvos que a coleta deve varrer.

Existe para ser chamado por scripts de automação — o de coleta contínua em
Bash, o de coleta diária em PowerShell — em vez de cada um embutir a mesma
consulta ao catálogo. Regra embutida em um lugar só: **alvos habilitados,
exceto o conjunto de validação sintético**, que depende do servidor local e é
varrido em etapa própria, antes da aferição.

Uso::

    python scripts/listar_alvos.py
    python scripts/listar_alvos.py --separador '\\n'
"""

from __future__ import annotations

import argparse
import sys

from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import get_settings


def alvos_habilitados() -> list[str]:
    """Identificadores dos alvos de produção habilitados no catálogo."""
    catalogo = load_catalog(get_settings().catalog_path)
    return [
        alvo.id
        for alvo in catalogo.targets
        if alvo.enabled and alvo.id != "fixtures-local"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--separador",
        default=" ",
        help="Separador entre identificadores. Padrão: espaço.",
    )
    args = parser.parse_args()

    alvos = alvos_habilitados()
    if not alvos:
        print(
            "Nenhum alvo habilitado no catálogo. Alvos de produção nascem "
            "desabilitados por conduta de coleta.",
            file=sys.stderr,
        )
        return 1

    print(args.separador.join(alvos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
