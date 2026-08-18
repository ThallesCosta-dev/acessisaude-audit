"""Portão de aferição usado pela coleta agendada.

O portão existe porque, em coleta automatizada, ninguém está olhando o resultado
do conjunto de validação antes de o instrumento tocar em portal público. Os
testes abaixo fixam o comportamento de que a coleta depende — e um deles trava
um defeito real, cometido na primeira versão do script.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]
CAMINHO = RAIZ / "scripts" / "aferir_instrumento.py"


def _carregar_modulo():
    """Importa o script, que vive fora do pacote instalável."""
    spec = importlib.util.spec_from_file_location("aferir_instrumento", CAMINHO)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["aferir_instrumento"] = modulo
    spec.loader.exec_module(modulo)
    return modulo


aferir_instrumento = _carregar_modulo()


def _pagina(url: str, regras: list[str], criterios: list[str]) -> dict:
    return {
        "url": url,
        "viewport": {"name": "mobile-320"},
        "findings": [
            {"rule_id": r, "outcome": "fail", "criteria": criterios} for r in regras
        ],
    }


def _escrever(tmp_path: Path, paginas: list[dict]) -> Path:
    caminho = tmp_path / "varredura.json"
    caminho.write_text(json.dumps({"pages": paginas}), encoding="utf-8")
    return caminho


BASE = "http://127.0.0.1:8080/pages/"
CONFORME = f"{BASE}acessivel-agendamento.html"
COM_BARREIRAS = f"{BASE}inacessivel-agendamento.html"

VINTE_CRITERIOS = [f"1.{i}.1" for i in range(1, 21)]


def test_aprova_quando_conforme_esta_limpa_e_positivo_detecta(tmp_path):
    caminho = _escrever(
        tmp_path,
        [
            _pagina(CONFORME, [], []),
            _pagina(COM_BARREIRAS, ["button-name"], VINTE_CRITERIOS),
        ],
    )
    assert aferir_instrumento.aferir(caminho, minimo_criterios=15) == []


def test_controle_positivo_nao_e_confundido_com_o_negativo(tmp_path):
    """Regressão: ``acessivel-`` é substring de ``inacessivel-``.

    A primeira versão do portão testava contenção de substring na URL. Como o
    nome do controle negativo está inteiramente contido no do positivo, a página
    com 20 barreiras plantadas era classificada também como controle negativo, e
    suas violações — que são o resultado esperado — eram reportadas como falso
    positivo. O efeito prático: o portão reprovava toda coleta, sempre, por um
    falso positivo que era ele próprio um falso positivo.
    """
    caminho = _escrever(
        tmp_path,
        [
            _pagina(CONFORME, [], []),
            _pagina(COM_BARREIRAS, ["button-name", "link-name"], VINTE_CRITERIOS),
        ],
    )
    assert aferir_instrumento.aferir(caminho, minimo_criterios=15) == []


def test_reprova_falso_positivo_no_controle_negativo(tmp_path):
    caminho = _escrever(
        tmp_path,
        [
            _pagina(CONFORME, ["color-contrast"], ["1.4.3"]),
            _pagina(COM_BARREIRAS, ["button-name"], VINTE_CRITERIOS),
        ],
    )
    falhas = aferir_instrumento.aferir(caminho, minimo_criterios=15)
    assert len(falhas) == 1
    assert "Especificidade" in falhas[0]


def test_reprova_queda_de_sensibilidade(tmp_path):
    caminho = _escrever(
        tmp_path,
        [
            _pagina(CONFORME, [], []),
            _pagina(COM_BARREIRAS, ["button-name"], ["4.1.2", "1.1.1"]),
        ],
    )
    falhas = aferir_instrumento.aferir(caminho, minimo_criterios=15)
    assert len(falhas) == 1
    assert "Sensibilidade" in falhas[0]


@pytest.mark.parametrize(
    ("paginas", "esperado"),
    [
        ([], 2),  # nenhum dos dois controles
        ([_pagina(CONFORME, [], [])], 1),  # falta o positivo
    ],
)
def test_reprova_quando_falta_controle(tmp_path, paginas, esperado):
    """Varredura incompleta não pode passar por varredura aprovada.

    O caso ocorre de verdade: se o servidor de fixtures não subir a tempo, a
    varredura termina com menos páginas e sem violação alguma — que é
    indistinguível de "tudo certo" para quem só conta falhas.
    """
    caminho = _escrever(tmp_path, paginas)
    assert len(aferir_instrumento.aferir(caminho, minimo_criterios=15)) == esperado
