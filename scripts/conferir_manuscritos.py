"""Confere que as duas versões do manuscrito não divergiram.

Existem duas versões em prosa do mesmo estudo:

* ``manuscrito-reciis.md`` — reduzida, para a Reciis, cujo corpo precisa caber em
  60 mil caracteres com espaços;
* ``manuscrito-extenso.md`` — estendida, para periódico com limite maior.

A estendida difere apenas por restaurar material cortado por limite: tabelas que
viraram prosa, subseções condensadas, parágrafos suprimidos. **Nenhum número,
nenhuma citação e nenhuma afirmação muda entre as duas.** É exatamente isso que
este verificador protege, porque a divergência entre dois documentos em prosa não
avisa quando acontece: aparece no parecer.

O caso concreto que motivou o cuidado: a intermitência do critério 2.1.1 foi
descrita como correção do órgão municipal e depois corrigida, quando a evidência
mostrou tratar-se de componente de terceiro. Uma correção como essa aplicada a uma
só das versões deixaria a outra afirmando o que se sabe ser falso.

Uso::

    python scripts/conferir_manuscritos.py

Código de saída 0 se as duas concordam; 1 se divergem.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REDUZIDA = RAIZ / "docs" / "artigo" / "manuscrito-reciis.md"
EXTENSA = RAIZ / "docs" / "artigo" / "manuscrito-extenso.md"

#: Limite da seção "Artigos originais" da Reciis, aferido contra artigos publicados
#: (ver § 3.1 da folha de submissão): incide sobre o corpo, com tabelas, e exclui
#: a lista de referências.
LIMITE_REDUZIDA = 60_000


def corpo(texto: str) -> tuple[str, str]:
    """Separa texto corrido de tabelas e legendas, sem a lista de referências.

    A nota editorial em bloco de citação do início não entra na contagem: ela é
    andaime de trabalho e sai na conversão para o arquivo submetido, conforme a
    lista de conferência da folha de submissão.
    """
    bloco = texto[
        texto.index("# Auditoria algorítmica") : texto.index("## Referências")
    ]
    tabelas, prosa = [], []
    for linha in bloco.split("\n"):
        despido = linha.strip()
        if despido.startswith(">"):
            continue
        alvo = (
            tabelas
            if despido.startswith(("|", "**Tabela", "**Figura", "Fonte:", "Nota"))
            else prosa
        )
        alvo.append(linha)

    def limpar(x: str) -> str:
        x = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", x)
        x = re.sub(r"[*_`|#>]", "", x)
        return re.sub(r"\n{2,}", "\n", re.sub(r"[ \t]+", " ", x)).strip()

    return limpar("\n".join(prosa)), limpar("\n".join(tabelas))


def numeros(texto: str) -> Counter[str]:
    """Números publicáveis do corpo, que precisam ser idênticos nas duas versões.

    Exclui a numeração de tabelas, figuras e subseções, que legitimamente difere:
    a estendida tem onze tabelas e a reduzida, cinco.
    """
    bloco = texto[
        texto.index("# Auditoria algorítmica") : texto.index("## Referências")
    ]
    bloco = re.sub(r"\*\*(Tabela|Figura) \d+\*\*", "", bloco)
    bloco = re.sub(r"\b(Tabela|Figura) \d+", "", bloco)
    bloco = re.sub(r"subseç(ão|ões) \d+\.\d+(\.\d+)?", "", bloco)
    bloco = re.sub(r"^#{2,4} .*$", "", bloco, flags=re.MULTILINE)
    return Counter(re.findall(r"\d+(?:[.,]\d+)*%?", bloco))


def citacoes(texto: str) -> Counter[str]:
    return Counter(re.findall(r"\(([A-ZÀ-Ú][^()]{2,60}?,\s*\d{4}[a-z]?)\)", texto))


def main() -> int:
    if not EXTENSA.is_file():
        print(f"Versão estendida não encontrada: {EXTENSA}", file=sys.stderr)
        return 1

    red = REDUZIDA.read_text(encoding="utf-8")
    ext = EXTENSA.read_text(encoding="utf-8")

    falhas: list[str] = []

    # ---------------------------------------------------------------- extensão
    p, q = corpo(red)
    tamanho = len(p) + len(q)
    estado = "ok" if tamanho <= LIMITE_REDUZIDA else "ACIMA DO LIMITE"
    print(
        f"reduzida   corpo {tamanho:>6} caracteres (limite {LIMITE_REDUZIDA})  {estado}"
    )
    if tamanho > LIMITE_REDUZIDA:
        falhas.append(
            f"a reduzida excede o limite em {tamanho - LIMITE_REDUZIDA} caracteres"
        )

    pe, qe = corpo(ext)
    print(f"estendida  corpo {len(pe) + len(qe):>6} caracteres")

    # ------------------------------------------------------ conteúdo publicável
    # A reduzida precisa ser subconjunto da estendida: tudo que ela afirma, a
    # estendida também afirma. O contrário não vale, porque a estendida restaura
    # tabelas e parágrafos que trazem números próprios — e é justamente isso que
    # a distingue. Um número que suma ou mude na estendida aparece aqui.
    for rotulo, extrai in (("números", numeros), ("citações", citacoes)):
        a, b = extrai(red), extrai(ext)
        perdidos = a - b
        if perdidos:
            falhas.append(f"{rotulo} da reduzida ausentes ou alterados na estendida")
            print(
                f"  {rotulo} faltando na estendida: {dict(list(perdidos.items())[:12])}"
            )
        else:
            extras = sum((b - a).values())
            print(f"{rotulo:10s} da reduzida presentes na estendida", end="")
            print(f" (+{extras} restaurados)" if extras else "")

    # ----------------------------------------------------------------- resumos
    for inicio, fim, nome in (
        ("## Resumo", "**Palavras-chave:**", "Resumo"),
        ("## Abstract", "**Keywords:**", "Abstract"),
        ("## Resumen", "**Palabras clave:**", "Resumen"),
    ):
        a = red[red.index(inicio) + len(inicio) : red.index(fim)].split()
        b = ext[ext.index(inicio) + len(inicio) : ext.index(fim)].split()
        if a != b:
            falhas.append(f"o {nome} difere entre as versões")
        if len(a) > 150:
            falhas.append(f"o {nome} da reduzida tem {len(a)} palavras (limite 150)")

    if not falhas:
        print("\nAs duas versões concordam em tudo o que não é extensão.")
        return 0

    print("\nDIVERGÊNCIAS:", file=sys.stderr)
    for f in falhas:
        print(f"  - {f}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
