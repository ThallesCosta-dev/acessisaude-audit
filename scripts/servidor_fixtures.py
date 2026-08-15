"""Servidor HTTP do conjunto de validação.

Serve ``fixtures/`` em ``http://127.0.0.1:8080`` e sintetiza, sob demanda, os
recursos volumosos usados pela fixture de custo de dados. Sintetizar em vez de
versionar mantém o repositório enxuto (nenhum binário de megabytes no git) sem
abrir mão de um teste realista de peso de página.

Uso::

    python scripts/servidor_fixtures.py            # porta 8080
    python scripts/servidor_fixtures.py --porta 9000

Recursos sintéticos::

    /assets/peso.png?bytes=920000&n=1   → 920 000 bytes de conteúdo incompressível
    /assets/peso.js?bytes=400000&n=2    → 400 000 bytes de JavaScript inerte

O conteúdo é **pseudoaleatório com semente fixa**, portanto incompressível pelo
gzip e idêntico entre execuções. Ambas as propriedades importam: conteúdo
compressível faria o peso medido variar conforme a configuração do servidor, e
conteúdo não determinístico impediria comparar duas execuções do teste.
"""

from __future__ import annotations

import argparse
import functools
import random
import struct
import sys
import zlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

#: Teto de bytes por recurso sintético — evita que um parâmetro errado na URL
#: consuma memória sem limite.
MAX_SYNTHETIC_BYTES = 8 * 1024 * 1024

#: Largura, em pixels, das imagens sintéticas.
_PNG_WIDTH = 600


@functools.lru_cache(maxsize=32)
def _filler(size: int, seed: int) -> bytes:
    """Gera ``size`` bytes pseudoaleatórios determinísticos.

    Memoizado: a mesma combinação (tamanho, semente) é gerada uma única vez por
    processo, o que mantém o servidor responsivo mesmo com várias requisições
    simultâneas de recursos grandes.
    """
    rng = random.Random(seed)
    return bytes(rng.getrandbits(8) for _ in range(size))


def _chunk(kind: bytes, payload: bytes) -> bytes:
    """Monta um bloco PNG com comprimento e CRC."""
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


@functools.lru_cache(maxsize=32)
def _png(size: int, seed: int) -> bytes:
    """Gera um PNG **válido** de aproximadamente ``size`` bytes.

    Por que um PNG de verdade, e não bytes aleatórios com Content-Type de imagem:
    o Chromium examina os primeiros quilobytes de todo recurso declarado como
    imagem e **cancela a transferência** ao não reconhecer o formato. Com
    conteúdo inválido, cada "imagem de 900 KB" chegava truncada em cerca de
    64 KB, e a fixture de custo de dados media um peso quatro vezes menor que o
    declarado — um falso negativo silencioso no próprio conjunto de validação.

    Construção: pixels RGB pseudoaleatórios, comprimidos em nível 0 (modo
    *stored* do zlib). O ruído garante que o peso na rede corresponda ao peso
    dos dados, como ocorre com fotografias reais — o caso que interessa medir.
    """
    row_bytes = 1 + _PNG_WIDTH * 3  # byte de filtro + RGB por pixel
    height = max(1, size // row_bytes)

    rng = random.Random(seed)
    raw = bytearray()
    for _ in range(height):
        raw.append(0)  # filtro "None"
        raw.extend(rng.getrandbits(8) for _ in range(_PNG_WIDTH * 3))

    ihdr = struct.pack(">IIBBBBB", _PNG_WIDTH, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 0))
        + _chunk(b"IEND", b"")
    )


class FixtureHandler(SimpleHTTPRequestHandler):
    """Serve arquivos estáticos e recursos sintéticos de peso controlado."""

    def do_GET(self) -> None:  # noqa: N802 - assinatura da biblioteca padrão
        parsed = urlparse(self.path)
        if parsed.path in ("/assets/peso.png", "/assets/peso.js"):
            self._serve_synthetic(parsed.path, parse_qs(parsed.query))
            return
        super().do_GET()

    def _serve_synthetic(self, path: str, query: dict[str, list[str]]) -> None:
        try:
            size = int(query.get("bytes", ["100000"])[0])
            seed = int(query.get("n", ["1"])[0])
        except ValueError:
            self.send_error(400, "Parâmetros 'bytes' e 'n' devem ser inteiros")
            return

        size = max(0, min(size, MAX_SYNTHETIC_BYTES))
        if path.endswith(".png"):
            payload = _png(size, seed)
            content_type = "image/png"
        else:
            payload = _filler(size, seed)
            content_type = "application/javascript"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        # Sem cache: cada auditoria mede o custo do primeiro acesso, que é o
        # cenário relevante para o usuário que limpa dados por falta de espaço.
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def end_headers(self) -> None:
        # A fixture de custo de dados carrega recursos de "localhost" a partir
        # de uma página em "127.0.0.1": hosts distintos, logo requisição de
        # origem cruzada. Sem este cabeçalho, o navegador as bloquearia e o
        # cenário de terceiros não se reproduziria.
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Registro conciso, para não poluir a saída dos testes."""
        sys.stderr.write(f"[fixtures] {self.address_string()} {format % args}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Servidor do conjunto de validação.")
    parser.add_argument("--porta", type=int, default=8080)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    if not FIXTURES_DIR.is_dir():
        print(f"Diretório de fixtures não encontrado: {FIXTURES_DIR}", file=sys.stderr)
        return 1

    handler = functools.partial(FixtureHandler, directory=str(FIXTURES_DIR))
    with ThreadingHTTPServer((args.host, args.porta), handler) as server:
        print(f"Fixtures em http://{args.host}:{args.porta}/pages/")
        print("Ctrl+C para encerrar.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
