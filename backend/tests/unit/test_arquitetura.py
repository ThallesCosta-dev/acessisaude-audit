"""Invariantes arquiteturais, verificadas por análise estática do código-fonte.

Documentação de arquitetura envelhece; teste, não. Estes testes falham quando a
regra de dependência é violada, no commit que a viola, e não meses depois
quando alguém tenta reusar o domínio.

Regra única: **as dependências apontam para dentro, em direção a ``domain``.**

    api → auditor → catalog → domain
    persistence ─┘        ↑
    reporting ────────────┘
    analysis ─────────────┘

``domain`` não importa nada das demais camadas. Isso é o que permite citar,
testar e reusar a matriz WCAG↔LBI independentemente da implementação de coleta.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "acessisaude_audit"

#: Camadas que cada pacote pode importar. Ausência da chave = sem restrição.
CAMADAS_PERMITIDAS: dict[str, set[str]] = {
    "domain": set(),
    "catalog": {"domain"},
    "auditor": {"domain", "catalog", "config", "logging_setup"},
    "persistence": {"domain", "config", "logging_setup"},
    "reporting": {"domain", "config", "logging_setup"},
    "analysis": {"domain", "catalog", "config", "logging_setup"},
}

#: Bibliotecas de infraestrutura que a camada de domínio não pode tocar.
INFRAESTRUTURA_PROIBIDA_NO_DOMINIO = {
    "playwright",
    "sqlalchemy",
    "fastapi",
    "httpx",
    "jinja2",
    "uvicorn",
    "typer",
    "yaml",
    "pandas",
    "matplotlib",
    "scipy",
}


def _modulos_de(pacote: str) -> list[Path]:
    return sorted((SRC / pacote).rglob("*.py"))


def _imports(path: Path) -> set[str]:
    """Todos os módulos importados por um arquivo, em nome pontilhado completo."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    nomes: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            nomes.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            nomes.add(node.module)
    return nomes


@pytest.mark.parametrize("pacote", sorted(CAMADAS_PERMITIDAS))
def test_direcao_das_dependencias(pacote: str) -> None:
    """Cada camada importa apenas as camadas permitidas."""
    permitidas = CAMADAS_PERMITIDAS[pacote]
    violacoes: list[str] = []

    for arquivo in _modulos_de(pacote):
        for nome in _imports(arquivo):
            if not nome.startswith("acessisaude_audit."):
                continue
            partes = nome.split(".")
            if len(partes) < 2:
                continue
            alvo = partes[1]
            if alvo == pacote or alvo in permitidas:
                continue
            relativo = arquivo.relative_to(SRC)
            violacoes.append(f"{relativo} importa {nome}")

    assert not violacoes, (
        f"A camada {pacote!r} só pode importar {sorted(permitidas) or 'nada'}. "
        f"Violações:\n  " + "\n  ".join(violacoes)
    )


def test_dominio_nao_toca_infraestrutura() -> None:
    """O domínio é puro: sem navegador, banco, HTTP ou pilha científica.

    A pureza não é estética. Ela é o que permite que a matriz WCAG↔LBI e os
    índices sejam avaliados por um revisor sem instalar Chromium.
    """
    violacoes: list[str] = []
    for arquivo in _modulos_de("domain"):
        for nome in _imports(arquivo):
            raiz = nome.split(".")[0]
            if raiz in INFRAESTRUTURA_PROIBIDA_NO_DOMINIO:
                violacoes.append(f"{arquivo.relative_to(SRC)} importa {nome}")

    assert not violacoes, "Domínio contaminado por infraestrutura:\n  " + "\n  ".join(violacoes)


def test_dominio_nao_faz_io_de_arquivo() -> None:
    """Nenhum módulo do domínio lê ou escreve arquivos.

    Um domínio que lesse configuração de disco produziria resultados
    dependentes do ambiente — e índices irreprodutíveis.
    """
    proibidos = {"open", "input"}
    violacoes: list[str] = []

    for arquivo in _modulos_de("domain"):
        tree = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in proibidos
            ):
                violacoes.append(f"{arquivo.relative_to(SRC)}:{node.lineno} chama {node.func.id}()")

    assert not violacoes, "I/O no domínio:\n  " + "\n  ".join(violacoes)


def test_todo_modulo_publico_tem_docstring() -> None:
    """A documentação é requisito do projeto, não cortesia.

    O artigo descreverá o software; módulos sem docstring seriam trechos do
    sistema que ninguém consegue explicar sem ler a implementação.
    """
    sem_doc: list[str] = []
    for arquivo in SRC.rglob("*.py"):
        if arquivo.name.startswith("_") and arquivo.name != "__init__.py":
            continue
        tree = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
        if not ast.get_docstring(tree):
            sem_doc.append(str(arquivo.relative_to(SRC)))

    assert not sem_doc, "Módulos sem docstring:\n  " + "\n  ".join(sem_doc)


def test_toda_definicao_publica_tem_docstring() -> None:
    """Funções e classes públicas precisam explicar o que fazem e por quê.

    Escopo verificado: definições de nível de módulo e métodos de classes de
    nível de módulo. Funções **aninhadas** (callbacks de progresso, corrotinas
    internas de orquestração) ficam de fora deliberadamente: são detalhe de
    implementação, invisíveis fora da função que as define, e exigir docstring
    delas produziria ruído sem melhorar a compreensão do sistema.
    """
    sem_doc: list[str] = []

    def verificar(node: ast.AST, arquivo: Path) -> None:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if node.name.startswith("_") or ast.get_docstring(node):
            return
        sem_doc.append(f"{arquivo.relative_to(SRC)}:{node.lineno} {node.name}")

    for arquivo in SRC.rglob("*.py"):
        tree = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
        for node in tree.body:
            verificar(node, arquivo)
            if isinstance(node, ast.ClassDef):
                for membro in node.body:
                    verificar(membro, arquivo)

    assert not sem_doc, "Definições públicas sem docstring:\n  " + "\n  ".join(sem_doc)
