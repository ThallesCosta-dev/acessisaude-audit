"""Gera as figuras do artigo, cada uma a partir do bloco de coleta que lhe cabe.

Existe porque o estudo tem **dois blocos de coleta com significados distintos**, e
misturá-los produz figuras que não correspondem às tabelas do manuscrito — erro
silencioso, porque o gráfico sai bonito e errado.

* **Bloco transversal** — 04/09/2026, único dia de cobertura integral nas cinco
  plataformas: 20 tentativas de auditoria de página, 20 válidas. Sustenta as Tabelas 1 e 3 a 7 e as **Figuras 1 a 4**.
* **Bloco longitudinal** — a série diária de 19 a 31/08/2026, definida pela
  cadência agendada das 12h20 UTC. Sustenta a Tabela 8 e a **Figura 5**.

As figuras não são versionadas (ver ``.gitignore``); este script é a receita que
as reconstrói. Os dados de origem estão em ``data/scans/`` e são versionados.

Uso::

    python scripts/gerar_figuras.py
    python scripts/gerar_figuras.py --saida docs/artigo/figuras

Exige o extra ``analysis``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

#: Data do bloco transversal: o dia de cobertura integral nas cinco plataformas
#: (20 de 20 auditorias de página). Fixado explicitamente porque a escolha é
#: metodológica, e não "o dia mais recente": ver a subseção 2.2 do manuscrito.
DIA_TRANSVERSAL = "2026-09-04"

#: A série é definida pela cadência agendada, não pela data: em 19/08 houve duas
#: execuções manuais de manhã, que não integram a série.
CORTE_DA_SERIE = "12:00"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--saida",
        type=Path,
        default=REPO_ROOT / "docs" / "artigo" / "figuras",
        help="Diretório de destino das figuras.",
    )
    parser.add_argument(
        "--banco",
        type=Path,
        default=REPO_ROOT / "data" / "acessisaude.sqlite",
        help="Índice relacional. Reconstruível com `acessisaude reindexar`.",
    )
    args = parser.parse_args()

    from acessisaude_audit.analysis import (
        build_findings_frame,
        build_pages_frame,
        build_scans_frame,
        save_all,
    )
    from acessisaude_audit.analysis.figures import figure_daily_series
    from acessisaude_audit.catalog.loader import load_catalog
    from acessisaude_audit.config import get_settings
    from acessisaude_audit.domain.models import ScanResult

    if not args.banco.is_file():
        print(f"Índice não encontrado: {args.banco}", file=sys.stderr)
        print("Execute `acessisaude reindexar` antes.", file=sys.stderr)
        return 1

    catalogo = load_catalog(get_settings().catalog_path)
    conexao = sqlite3.connect(args.banco)

    def carregar(sql: str, params: tuple[str, ...] = ()) -> list[ScanResult]:
        linhas = conexao.execute(sql, params).fetchall()
        return [ScanResult.model_validate(json.loads(linha[0])) for linha in linhas]

    transversal = carregar(
        """SELECT document FROM scans
             WHERE target_id <> 'fixtures-local'
               AND date(started_at) = ?
               AND time(started_at) >= '12:00'
             ORDER BY target_id""",
        (DIA_TRANSVERSAL,),
    )
    serie = carregar(
        """SELECT document FROM scans
            WHERE target_id <> 'fixtures-local'
              AND time(started_at) >= ?
            ORDER BY started_at""",
        (CORTE_DA_SERIE,),
    )

    if len(transversal) != 5:
        print(
            f"Bloco transversal incompleto: {len(transversal)} de 5 varreduras "
            f"em {DIA_TRANSVERSAL}. Reindexe antes.",
            file=sys.stderr,
        )
        return 1

    tentativas = sum(len(s.pages) for s in transversal)
    validas = sum(len(s.successful_pages) for s in transversal)
    print(f"Bloco transversal: {tentativas} tentativas, {validas} auditorias válidas.")
    if (tentativas, validas) != (20, 20):
        # Não é erro fatal, mas o manuscrito afirma esses números: divergir sem
        # aviso faria a figura contradizer o texto.
        print(
            "  AVISO: divergente dos 20/16 declarados no manuscrito.", file=sys.stderr
        )

    args.saida.mkdir(parents=True, exist_ok=True)
    escritas = save_all(
        build_findings_frame(transversal, catalog=catalogo),
        build_pages_frame(transversal, catalog=catalogo),
        args.saida,
    )
    for caminho in escritas:
        print(f"  {caminho.name}")

    dias = {s.started_at.date() for s in serie}
    print(f"Série diária: {len(serie)} varreduras em {len(dias)} dias.")
    if len(dias) < 2:
        print("  Menos de dois dias: figura 5 não gerada.", file=sys.stderr)
        return 0

    figura = figure_daily_series(
        build_scans_frame(serie, catalog=catalogo), index="ica"
    )
    for extensao in ("png", "svg"):
        caminho = args.saida / f"fig5-serie-diaria-ica.{extensao}"
        figura.savefig(caminho)
        print(f"  {caminho.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
