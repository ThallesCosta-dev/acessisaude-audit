"""Gera as figuras do artigo, cada uma a partir do bloco de coleta que lhe cabe.

Existe porque o estudo tem **dois blocos de coleta com significados distintos**, e
misturá-los produz figuras que não correspondem às tabelas do manuscrito — erro
silencioso, porque o gráfico sai bonito e errado.

* **Bloco transversal** — a última rodada completa de 16/08/2026, posterior à
  correção do agente de usuário (ADR 0008). É o dataset primário declarado em
  ``docs/metodologia/registro-de-coleta.md``: 20 tentativas de auditoria de
  página, 16 válidas. Sustenta as Tabelas 3, 6, 8 e as **Figuras 1 a 4**.
* **Bloco longitudinal** — a série diária de 19 a 31/08/2026, definida pela
  cadência agendada das 12h20 UTC. Sustenta as Tabelas 12 e 13 e a **Figura 5**.

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

#: Horários (UTC) da rodada transversal primária de 16/08/2026, uma por alvo.
#: Fixados explicitamente, e não derivados por "última do dia": derivar tornaria
#: a figura dependente de qualquer varredura futura gravada naquela data.
RODADA_TRANSVERSAL = (
    "01:39:35",  # Meu SUS Digital
    "01:39:53",  # gov.br/saúde, já com o agente corrigido
    "01:40:31",  # SES-RJ
    "01:40:48",  # SMS Rio
    "01:41:03",  # Carioca Digital
)

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

    marcadores = ",".join("?" * len(RODADA_TRANSVERSAL))
    transversal = carregar(
        f"""SELECT document FROM scans
             WHERE date(started_at) = '2026-08-16'
               AND time(started_at) IN ({marcadores})
             ORDER BY started_at""",
        RODADA_TRANSVERSAL,
    )
    serie = carregar(
        """SELECT document FROM scans
            WHERE target_id <> 'fixtures-local'
              AND time(started_at) >= ?
            ORDER BY started_at""",
        (CORTE_DA_SERIE,),
    )

    if len(transversal) != len(RODADA_TRANSVERSAL):
        print(
            f"Bloco transversal incompleto: {len(transversal)} de "
            f"{len(RODADA_TRANSVERSAL)} varreduras. Reindexe antes.",
            file=sys.stderr,
        )
        return 1

    tentativas = sum(len(s.pages) for s in transversal)
    validas = sum(len(s.successful_pages) for s in transversal)
    print(f"Bloco transversal: {tentativas} tentativas, {validas} auditorias válidas.")
    if (tentativas, validas) != (20, 16):
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
