"""Confere se a sonda de vantagem observa os mesmos endereços que o coletor audita.

A lista ``ALVOS`` do ``Codigo.gs`` duplica as sementes do catálogo, porque o
Apps Script não tem como ler o YAML do repositório. A duplicação é deliberada e
**frágil**: se o catálogo mudar e a sonda não, ela passa a observar endereços
diferentes dos auditados e deixa de servir como controle — silenciosamente, que
é o pior modo de falhar.

Este verificador existe para que a divergência apareça. Rode-o depois de
qualquer alteração em ``targets.yaml``.

Uso::

    python scripts/sonda-de-vantagem/conferir_alvos.py

Código de saída 0 se as duas listas coincidem; 1 se divergem.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SONDA = RAIZ / "scripts" / "sonda-de-vantagem" / "Codigo.gs"


def urls_do_catalogo() -> set[str]:
    """Sementes auditáveis dos alvos habilitados, exceto o conjunto sintético."""
    sys.path.insert(0, str(RAIZ / "backend" / "src"))
    from acessisaude_audit.catalog.loader import load_catalog
    from acessisaude_audit.config import get_settings

    catalogo = load_catalog(get_settings().catalog_path)
    return {
        str(semente.url)
        for alvo in catalogo.targets
        if alvo.enabled and alvo.id != "fixtures-local"
        for semente in alvo.auditable_seeds
    }


def urls_da_sonda(caminho: Path = SONDA) -> set[str]:
    """Endereços declarados no bloco ``ALVOS`` do script."""
    texto = caminho.read_text(encoding="utf-8")
    try:
        bloco = texto.split("var ALVOS = [")[1].split("];")[0]
    except IndexError:
        raise ValueError(f"Bloco 'var ALVOS = [' não encontrado em {caminho}") from None
    return set(re.findall(r'"(https://[^"]+)"', bloco))


def main() -> int:
    catalogo = urls_do_catalogo()
    sonda = urls_da_sonda()

    faltando = catalogo - sonda
    sobrando = sonda - catalogo

    if not faltando and not sobrando:
        print(f"[sonda] Conferem — {len(catalogo)} endereços em comum.")
        return 0

    print("[sonda] DIVERGEM", file=sys.stderr)
    for url in sorted(faltando):
        print(f"  auditado e não observado: {url}", file=sys.stderr)
    for url in sorted(sobrando):
        print(f"  observado e não auditado: {url}", file=sys.stderr)
    print(
        "\nAtualize a lista ALVOS em Codigo.gs. Uma sonda que observa endereços "
        "diferentes dos auditados não serve como controle.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
