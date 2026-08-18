"""Portão de aferição do instrumento, para execução automatizada.

Existe por uma razão metodológica, não operacional: **nenhuma afirmação sobre
portal real deve ser produzida por um instrumento que não acabou de ser
aferido.** Em coleta manual, o pesquisador roda o conjunto de validação e olha o
resultado. Em coleta agendada, ninguém está olhando — então o portão precisa ser
executável e precisa falhar ruidosamente.

Verifica duas propriedades sobre a varredura mais recente do conjunto de
validação sintético:

* **Especificidade** — a página construída em conformidade não pode produzir
  nenhuma violação. Um único falso positivo aqui invalida toda a coleta do dia,
  porque significa que o motor passou a reprovar o que é correto.
* **Sensibilidade** — a página de controle positivo precisa continuar detectando
  ao menos ``--minimo-criterios`` critérios distintos. O piso é deliberadamente
  inferior aos 18 aferidos no estudo: o objetivo é detectar **regressão** do
  motor (uma atualização do axe-core que deixe de reportar uma classe inteira de
  falha), não reproduzir a validação, que é feita com o manifesto e revisada por
  humano.

Uso::

    python scripts/aferir_instrumento.py
    python scripts/aferir_instrumento.py --minimo-criterios 18

Código de saída 0 se o instrumento passou; 1 se falhou ou se não há varredura do
conjunto de validação para aferir.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

#: Nomes de arquivo das duas fixtures usadas como controle.
#:
#: A comparação é por nome exato, e não por substring, porque
#: ``"acessivel-agendamento.html"`` é substring de
#: ``"inacessivel-agendamento.html"``: um teste de contenção classificaria o
#: controle positivo — que tem 20 barreiras plantadas — como o controle
#: negativo, e o portão reprovaria toda coleta com um "falso positivo" que é,
#: ele próprio, um falso positivo.
CONTROLE_NEGATIVO = "acessivel-agendamento.html"
CONTROLE_POSITIVO = "inacessivel-agendamento.html"


def _arquivo(url: str) -> str:
    """Último segmento do caminho da URL, sem query nem fragmento."""
    return urlparse(url).path.rsplit("/", 1)[-1]

#: Piso de sensibilidade. Ver a nota do módulo sobre por que é menor que 18.
MINIMO_CRITERIOS_PADRAO = 15


def _varredura_mais_recente(scans_dir: Path) -> Path | None:
    """Devolve o JSON mais recente do conjunto de validação, ou ``None``."""
    candidatos = sorted(scans_dir.glob("fixtures-local__*.json"))
    return candidatos[-1] if candidatos else None


def aferir(caminho: Path, minimo_criterios: int) -> list[str]:
    """Afere uma varredura do conjunto de validação.

    Args:
        caminho: JSON produzido por ``acessisaude varrer fixtures-local``.
        minimo_criterios: Piso de critérios distintos no controle positivo.

    Returns:
        Lista de falhas em linguagem natural. Vazia significa aprovado.
    """
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    falhas: list[str] = []

    negativo_visto = False
    positivo_visto = False

    for pagina in dados.get("pages", []):
        arquivo = _arquivo(pagina.get("url", ""))
        violacoes = [f for f in pagina.get("findings", []) if f.get("outcome") == "fail"]

        if arquivo == CONTROLE_NEGATIVO:
            negativo_visto = True
            if violacoes:
                regras = sorted({f.get("rule_id", "?") for f in violacoes})
                falhas.append(
                    f"Especificidade: a página conforme ({pagina.get('viewport', {}).get('name', '?')}) "
                    f"produziu {len(violacoes)} violação(ões) — {', '.join(regras)}. "
                    "Falso positivo no controle negativo."
                )

        if arquivo == CONTROLE_POSITIVO:
            positivo_visto = True
            criterios = {c for f in violacoes for c in f.get("criteria", [])}
            if len(criterios) < minimo_criterios:
                falhas.append(
                    f"Sensibilidade: o controle positivo "
                    f"({pagina.get('viewport', {}).get('name', '?')}) detectou "
                    f"{len(criterios)} critérios distintos, abaixo do piso de {minimo_criterios}. "
                    "Possível regressão do motor de regras."
                )

    if not negativo_visto:
        falhas.append(f"Controle negativo ausente da varredura ({CONTROLE_NEGATIVO}).")
    if not positivo_visto:
        falhas.append(f"Controle positivo ausente da varredura ({CONTROLE_POSITIVO}).")

    return falhas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--scans-dir",
        type=Path,
        default=Path("data/scans"),
        help="Diretório dos JSON de varredura. Padrão: data/scans.",
    )
    parser.add_argument(
        "--minimo-criterios",
        type=int,
        default=MINIMO_CRITERIOS_PADRAO,
        help=f"Piso de critérios distintos no controle positivo. Padrão: {MINIMO_CRITERIOS_PADRAO}.",
    )
    args = parser.parse_args()

    caminho = _varredura_mais_recente(args.scans_dir)
    if caminho is None:
        print(
            f"[aferição] Nenhuma varredura do conjunto de validação em {args.scans_dir}. "
            "Execute 'acessisaude varrer fixtures-local' antes.",
            file=sys.stderr,
        )
        return 1

    falhas = aferir(caminho, args.minimo_criterios)
    if falhas:
        print(f"[aferição] REPROVADO — {caminho.name}", file=sys.stderr)
        for f in falhas:
            print(f"  · {f}", file=sys.stderr)
        print(
            "\nA coleta em portais reais NÃO deve prosseguir: um instrumento não aferido "
            "produz número, não resultado.",
            file=sys.stderr,
        )
        return 1

    print(f"[aferição] Aprovado — {caminho.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
