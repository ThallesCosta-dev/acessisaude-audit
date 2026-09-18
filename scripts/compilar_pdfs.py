"""Junta os PDF de uma pasta em um único arquivo, com sumário, e comprime o resultado.

Uso:
    pip install pypdf
    python scripts/compilar_pdfs.py PASTA_COM_PDFS SAIDA.pdf

Os arquivos entram em ordem alfabética do nome, por isso a lista de artigos sugere um
prefixo numérico. Cada artigo vira um marcador (bookmark) no PDF final, o que serve de
sumário navegável. A compressão é a dos fluxos de conteúdo do pypdf, sem perda; para
reduzir imagens use o Ghostscript, como indicado em docs/entregas/.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pragma: no cover
    sys.exit("Instale a dependência: pip install pypdf")


def compilar(pasta: Path, saida: Path) -> None:
    arquivos = sorted(p for p in pasta.glob("*.pdf") if p.resolve() != saida.resolve())
    if not arquivos:
        sys.exit(f"Nenhum PDF encontrado em {pasta}")

    escritor = PdfWriter()
    for arquivo in arquivos:
        leitor = PdfReader(str(arquivo))
        if leitor.is_encrypted:
            leitor.decrypt("")
        primeira_pagina = len(escritor.pages)
        for pagina in leitor.pages:
            escritor.add_page(pagina)
        escritor.add_outline_item(arquivo.stem, primeira_pagina)
        print(f"  + {arquivo.name}: {len(leitor.pages)} páginas")

    for pagina in escritor.pages:
        pagina.compress_content_streams()
    escritor.add_metadata({"/Title": "Artigos compilados", "/Producer": "compilar_pdfs.py"})

    with saida.open("wb") as destino:
        escritor.write(destino)
    tamanho = saida.stat().st_size / 1_048_576
    print(f"gerado: {saida} ({len(escritor.pages)} páginas, {tamanho:.1f} MiB)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    compilar(Path(sys.argv[1]), Path(sys.argv[2]))
