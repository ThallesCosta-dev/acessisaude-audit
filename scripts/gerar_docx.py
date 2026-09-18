"""Converte um Markdown do projeto em .docx no modelo do "Resumo de compreensão".

O modelo é o próprio arquivo entregue na disciplina
(docs/referencias/Resumo de compreensão - Submissão à revista RECIIS.docx): Calibri 10,5 pt
em verde-escuro, título em verde 20 pt com subtítulo, seções "1." em Heading 1, tabelas com
bordas verdes, primeira coluna sombreada e rótulos em negrito, cabeçalho com o nome do
documento e rodapé com número de página. Exige o pandoc no PATH.

Uso:
    python scripts/gerar_docx.py ENTRADA.md [SAIDA.docx] [--modelo MODELO.docx]

Convenções do Markdown de entrada:
    - a primeira linha "# ..." vira o título e o texto do cabeçalho;
    - se o parágrafo seguinte estiver inteiro em **negrito**, vira o subtítulo;
    - "## ..." vira Heading 1, "### ..." Heading 2, "#### ..." Heading 3;
    - tabelas cujo cabeçalho está vazio ("| | |") viram tabelas rótulo/valor, como a de
      identificação do modelo; as demais recebem cabeçalho em negrito sombreado.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

MODELO_PADRAO = Path("docs/referencias/Resumo de compreensão - Submissão à revista RECIIS.docx")

VERDE = "4A6741"
TEXTO = "2E352E"
TEXTO_CLARO = "55604F"
SOMBRA = "EFF4ED"
LINHA = "D8E0D4"

ESTILOS_EXTRA = f"""
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
  <w:pPr><w:spacing w:before="0" w:after="120"/><w:jc w:val="left"/></w:pPr>
  <w:rPr><w:b/><w:color w:val="{VERDE}"/><w:sz w:val="40"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/>
  <w:pPr><w:spacing w:before="0" w:after="480"/><w:jc w:val="left"/></w:pPr>
  <w:rPr><w:color w:val="{TEXTO_CLARO}"/><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Heading2"/>
  <w:pPr><w:spacing w:before="240" w:after="100"/><w:outlineLvl w:val="2"/></w:pPr>
  <w:rPr><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="BodyText"><w:name w:val="Body Text"/><w:basedOn w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="FirstParagraph"><w:name w:val="First Paragraph"/><w:basedOn w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Compact"><w:name w:val="Compact"/><w:basedOn w:val="Normal"/>
  <w:pPr><w:spacing w:before="60" w:after="60" w:line="276" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>
  <w:rPr><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableCaption"><w:name w:val="Table Caption"/><w:basedOn w:val="Normal"/>
  <w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/></w:pPr><w:rPr><w:i/><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="SourceCode"><w:name w:val="Source Code"/><w:basedOn w:val="Normal"/>
  <w:pPr><w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/><w:shd w:val="clear" w:fill="{SOMBRA}"/></w:pPr>
  <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="VerbatimChar"><w:name w:val="Verbatim Char"/>
  <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="19"/></w:rPr></w:style>
<w:style w:type="table" w:styleId="Table"><w:name w:val="Table"/>
  <w:tblPr><w:tblW w:w="5000" w:type="pct"/>
    <w:tblBorders><w:top w:val="single" w:color="{VERDE}" w:sz="12"/><w:bottom w:val="single" w:color="{VERDE}" w:sz="12"/><w:insideH w:val="single" w:color="{LINHA}" w:sz="4"/></w:tblBorders>
    <w:tblCellMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
"""


def _separar_titulo(md: str) -> tuple[str, str, str]:
    """Extrai título (primeiro '# ') e subtítulo (parágrafo em negrito logo abaixo)."""
    linhas = md.splitlines()
    titulo, subtitulo, i = "", "", 0
    while i < len(linhas) and not linhas[i].strip():
        i += 1
    if i < len(linhas) and linhas[i].startswith("# "):
        titulo = linhas[i][2:].strip()
        i += 1
        while i < len(linhas) and not linhas[i].strip():
            i += 1
        if i < len(linhas) and re.fullmatch(r"\*\*.+\*\*", linhas[i].strip()):
            subtitulo = linhas[i].strip()[2:-2]
            i += 1
    return titulo, subtitulo, "\n".join(linhas[i:])


def _patch_styles(xml: str) -> str:
    # Remove definições homônimas do modelo, se houver, e insere as do projeto.
    for sid in re.findall(r'w:styleId="([^"]+)"', ESTILOS_EXTRA):
        xml = re.sub(r'<w:style [^>]*w:styleId="%s".*?</w:style>' % re.escape(sid), "", xml, flags=re.S)
    return xml.replace("</w:styles>", ESTILOS_EXTRA + "</w:styles>")


def _run_props(run: str, extra: str) -> str:
    """Acrescenta propriedades a um <w:r>, respeitando um <w:rPr> existente."""
    if "<w:rPr>" in run:
        return run.replace("<w:rPr>", "<w:rPr>" + extra, 1)
    if "<w:rPr/>" in run:
        return run.replace("<w:rPr/>", "<w:rPr>" + extra + "</w:rPr>", 1)
    return re.sub(r"(<w:r>|<w:r [^>]*>)", lambda m: m.group(1) + "<w:rPr>" + extra + "</w:rPr>", run, count=1)


def _formatar_celula(celula: str, *, rotulo: bool) -> str:
    cor = TEXTO if rotulo else TEXTO_CLARO
    extra = ("<w:b/>" if rotulo else "") + f'<w:color w:val="{cor}"/><w:sz w:val="20"/>'
    celula = re.sub(r"<w:r>.*?</w:r>|<w:r [^>]*>.*?</w:r>", lambda m: _run_props(m.group(0), extra), celula, flags=re.S)
    if rotulo:
        sombra = f'<w:shd w:val="clear" w:fill="{SOMBRA}"/>'
        if re.search(r"<w:tcPr\s*/>", celula):
            celula = re.sub(r"<w:tcPr\s*/>", "<w:tcPr>" + sombra + "</w:tcPr>", celula, count=1)
        elif "<w:tcPr>" in celula:
            celula = celula.replace("<w:tcPr>", "<w:tcPr>" + sombra, 1)
        else:
            celula = re.sub(r"(<w:tc>|<w:tc [^>]*>)", lambda m: m.group(1) + "<w:tcPr>" + sombra + "</w:tcPr>", celula, count=1)
    return celula


def _formatar_tabela(tabela: str) -> str:
    def linha(m: re.Match[str]) -> str:
        tr = m.group(0)
        cabecalho = "<w:tblHeader" in tr
        celulas = re.findall(r"<w:tc>.*?</w:tc>|<w:tc [^>]*>.*?</w:tc>", tr, flags=re.S)
        novas = [_formatar_celula(c, rotulo=cabecalho or i == 0) for i, c in enumerate(celulas)]
        for velha, nova in zip(celulas, novas):
            tr = tr.replace(velha, nova, 1)
        return tr
    return re.sub(r"<w:tr>.*?</w:tr>|<w:tr [^>]*>.*?</w:tr>", linha, tabela, flags=re.S)


def _patch_document(xml: str) -> str:
    return re.sub(r"<w:tbl>.*?</w:tbl>", lambda m: _formatar_tabela(m.group(0)), xml, flags=re.S)


def _patch_header(xml: str, titulo: str) -> str:
    return re.sub(r"(<w:t(?: [^>]*)?>)[^<]*(</w:t>)", lambda m: m.group(1) + escape(titulo) + m.group(2), xml, count=1)


def _reescrever_zip(caminho: Path, transformacoes: dict) -> None:
    temporario = caminho.with_suffix(".tmp")
    with zipfile.ZipFile(caminho) as origem, zipfile.ZipFile(temporario, "w", zipfile.ZIP_DEFLATED) as destino:
        for item in origem.infolist():
            conteudo = origem.read(item.filename)
            if item.filename in transformacoes:
                conteudo = transformacoes[item.filename](conteudo.decode("utf-8")).encode("utf-8")
            destino.writestr(item, conteudo)
    shutil.move(temporario, caminho)


def gerar(entrada: Path, saida: Path, modelo: Path = MODELO_PADRAO) -> None:
    if not modelo.exists():
        sys.exit(f"modelo não encontrado: {modelo}")
    titulo, subtitulo, corpo = _separar_titulo(entrada.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as pasta:
        referencia = Path(pasta) / "modelo.docx"
        shutil.copy(modelo, referencia)
        _reescrever_zip(referencia, {"word/styles.xml": _patch_styles})
        corpo_md = Path(pasta) / "corpo.md"
        corpo_md.write_text(corpo, encoding="utf-8")
        comando = [
            "pandoc", str(corpo_md), "-o", str(saida),
            "--reference-doc", str(referencia),
            "--from", "markdown+pipe_tables+smart", "--wrap", "none",
            "--shift-heading-level-by=-1",
        ]
        if titulo:
            comando += ["--metadata", f"title={titulo}"]
        if subtitulo:
            comando += ["--metadata", f"subtitle={subtitulo}"]
        subprocess.run(comando, check=True)
        _reescrever_zip(saida, {
            "word/document.xml": _patch_document,
            "word/header1.xml": lambda x: _patch_header(x, titulo or saida.stem),
        })
    print(f"gerado: {saida}")


if __name__ == "__main__":
    args = sys.argv[1:]
    modelo = MODELO_PADRAO
    if "--modelo" in args:
        i = args.index("--modelo")
        modelo = Path(args[i + 1])
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    entrada = Path(args[0])
    saida = Path(args[1]) if len(args) > 1 else entrada.with_suffix(".docx")
    gerar(entrada, saida, modelo)
