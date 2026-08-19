"""Sonda de vantagem — posição de rede brasileira, em nuvem.

Mesma função da sonda do Apps Script: perguntar a cada endereço do catálogo
"você responde?", a partir de uma posição de rede declarada. **Não audita
acessibilidade** — não há navegador aqui, e sem navegador não há árvore de
acessibilidade, cor computada nem layout.

O que muda em relação à sonda do Apps Script é a posição e a procedência:

* **posição** — executa em ``southamerica-east1``, datacenter brasileiro. Serve
  para responder à pergunta que decide a infraestrutura da coleta contínua: um
  IP brasileiro *de datacenter* é tratado como o residencial, que recebe 200 em
  todos os alvos, ou como as nuvens estrangeiras, que recebem 403 e 500?

* **procedência** — lê a lista de endereços do próprio ``targets.yaml``, em vez
  de duplicá-la. A sonda do Apps Script precisa duplicar, porque o Apps Script
  não lê o repositório, e essa duplicação é a sua fragilidade conhecida. Aqui
  não existe: se o catálogo mudar, a sonda muda junto.

Conduta de coleta: identificação obrigatória no ``User-Agent``, intervalo entre
requisições, apenas GET a páginas públicas. Sem identificação, recusa executar.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml

#: Caminho do catálogo dentro da imagem.
CATALOGO = Path(os.environ.get("CATALOGO", "/app/targets.yaml"))

#: Rótulo da posição de rede, gravado em cada observação. Sem ele, duas fontes
#: com o mesmo carimbo de tempo seriam indistinguíveis na análise — e comparar
#: posições é a única razão de a sonda existir.
VANTAGEM = os.environ.get("VANTAGEM", "cloud-run-southamerica-east1")

INTERVALO_S = float(os.environ.get("INTERVALO_S", "2"))
TIMEOUT_S = float(os.environ.get("TIMEOUT_S", "30"))

GITHUB_REPO = os.environ.get("GITHUB_REPO", "ThallesCosta-dev/acessisaude-audit")
GITHUB_RAMO = os.environ.get("GITHUB_RAMO", "serie-temporal")


def alvos_do_catalogo(caminho: Path) -> list[tuple[str, str]]:
    """Sementes auditáveis dos alvos habilitados, exceto o conjunto sintético.

    Replica a regra de ``TargetSpec.auditable_seeds``: exclui sementes marcadas
    com ``requires_auth``, que são lacunas declaradas da amostra e não devem
    receber requisição alguma.
    """
    bruto = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    saida: list[tuple[str, str]] = []

    for alvo in bruto.get("targets", []):
        if not alvo.get("enabled") or alvo.get("id") == "fixtures-local":
            continue
        for semente in alvo.get("seeds", []):
            if semente.get("requires_auth"):
                continue
            saida.append((alvo["id"], semente["url"]))

    return saida


def observar_um(cliente: httpx.Client, alvo: str, url: str, carimbo: str) -> dict[str, Any]:
    """Observa um endereço.

    Falha de rede vira registro com o campo ``erro`` preenchido, e não exceção:
    interromper a rodada produziria lacuna silenciosa, que é o modo de falhar
    que este projeto evita em toda parte.
    """
    inicio = time.monotonic()
    base: dict[str, Any] = {
        "observado_em": carimbo,
        "vantagem": VANTAGEM,
        "alvo": alvo,
        "url": url,
    }

    try:
        r = cliente.get(url)
        return {
            **base,
            "status_http": r.status_code,
            "bytes": len(r.content),
            "duracao_ms": round((time.monotonic() - inicio) * 1000),
            "url_final": str(r.url) if str(r.url) != url else "",
            "erro": "",
        }
    except Exception as e:  # noqa: BLE001 - qualquer falha de rede é dado
        return {
            **base,
            "status_http": None,
            "bytes": None,
            "duracao_ms": round((time.monotonic() - inicio) * 1000),
            "url_final": "",
            "erro": f"{type(e).__name__}: {e}"[:250],
        }


def publicar(documento: dict[str, Any], carimbo_arquivo: str) -> None:
    """Publica no ramo da série temporal, se houver token.

    Um arquivo por execução, e não um agregado atualizado: o coletor empurra
    para o mesmo ramo três vezes ao dia, e criar arquivo novo dispensa ler o
    SHA anterior e elimina a janela em que duas escritas se sobrepõem.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[sonda] GITHUB_TOKEN ausente — publicação ignorada.", file=sys.stderr)
        return

    caminho = f"observacoes/{VANTAGEM}__{carimbo_arquivo}.json"
    corpo = json.dumps(documento, ensure_ascii=False, indent=2).encode("utf-8")

    import base64

    resposta = httpx.put(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/{caminho}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "message": f"Sonda de vantagem ({VANTAGEM}) — {carimbo_arquivo}",
            "content": base64.b64encode(corpo).decode("ascii"),
            "branch": GITHUB_RAMO,
        },
        timeout=30,
    )

    if resposta.status_code == 201:
        print(f"[sonda] Publicado em {caminho} ({GITHUB_RAMO}).")
    else:
        print(
            f"[sonda] Falha ao publicar (HTTP {resposta.status_code}): "
            f"{resposta.text[:300]}",
            file=sys.stderr,
        )


def main() -> int:
    contato = os.environ.get("ACESSISAUDE_USER_AGENT_SUFFIX", "")
    if not contato:
        print(
            "[sonda] ACESSISAUDE_USER_AGENT_SUFFIX não definida.\n\n"
            "A conduta de coleta do projeto exige identificação da pesquisa no\n"
            "User-Agent. Um portal público precisa poder saber quem o acessa e a\n"
            "quem reclamar.",
            file=sys.stderr,
        )
        return 2

    if not CATALOGO.is_file():
        print(f"[sonda] Catálogo não encontrado em {CATALOGO}.", file=sys.stderr)
        return 2

    alvos = alvos_do_catalogo(CATALOGO)
    agora = datetime.now(timezone.utc)
    carimbo = agora.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    observacoes: list[dict[str, Any]] = []
    with httpx.Client(
        headers={"User-Agent": contato},
        timeout=TIMEOUT_S,
        follow_redirects=True,
    ) as cliente:
        for i, (alvo, url) in enumerate(alvos):
            if i:
                time.sleep(INTERVALO_S)
            observacoes.append(observar_um(cliente, alvo, url, carimbo))

    print(f"\nvantagem: {VANTAGEM}   |   {carimbo}\n")
    print(f"{'alvo':20s} {'status':>7s} {'bytes':>9s} {'ms':>6s}  url")
    for o in observacoes:
        status = str(o["status_http"]) if o["status_http"] is not None else "ERRO"
        tamanho = str(o["bytes"]) if o["bytes"] is not None else "-"
        print(
            f"{o['alvo']:20s} {status:>7s} {tamanho:>9s} "
            f"{o['duracao_ms']:>6d}  {o['url'].replace('https://', '')[:52]}"
        )
        if o["erro"]:
            print(f"{'':20s} {o['erro'][:88]}")

    ok = sum(1 for o in observacoes if o["status_http"] == 200)
    print(f"\n{ok} de {len(observacoes)} responderam 200.\n")

    publicar(
        {
            "vantagem": VANTAGEM,
            "observado_em": carimbo,
            "agente": contato,
            "instrumento": "sonda-de-vantagem/cloud-run",
            "nota": (
                "Controle de rede. Nao e auditoria de acessibilidade: mede apenas "
                "se o endereco responde, sem navegador."
            ),
            "observacoes": observacoes,
        },
        agora.strftime("%Y%m%d-%H%M%S"),
    )

    # Sempre 0: uma sonda que encontra falhas não falhou — ela mediu.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
