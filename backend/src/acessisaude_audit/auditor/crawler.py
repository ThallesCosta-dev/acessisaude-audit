"""Conduta de coleta: ``robots.txt``, controle de taxa e descoberta de páginas.

Auditar infraestrutura pública em produção impõe deveres que uma ferramenta de
teste interno não tem. Este módulo concentra esses deveres em um único lugar,
para que sejam auditáveis e não fiquem espalhados por condicionais no motor:

1. **Respeitar ``robots.txt``.** Não por obrigação legal — o arquivo não é norma
   jurídica — mas porque ignorá-lo em pesquisa acadêmica sobre serviço público
   é conduta indefensável perante um comitê de ética.
2. **Espaçar requisições.** O alvo é um servidor de saúde pública; degradar seu
   desempenho para medir sua acessibilidade seria autocontraditório.
3. **Identificar-se.** O ``User-Agent`` declara a pesquisa e um contato.
4. **Nunca interagir.** A ferramenta lê o DOM renderizado. Não autentica, não
   preenche formulário, não submete dado algum.

Ver ``docs/metodologia/etica-e-conduta-de-coleta.md``.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import httpx

from acessisaude_audit.logging_setup import get_logger

__all__ = ["HostRateLimiter", "RobotsGate", "discover_links", "normalize_url", "same_site"]

logger = get_logger(__name__)


def normalize_url(url: str) -> str:
    """Normaliza a URL para deduplicação estável.

    Remove fragmento (``#secao`` não identifica outro recurso), normaliza o
    host para minúsculas e elimina a barra final de caminhos não vazios. Não
    remove parâmetros de consulta: em portais públicos, ``?id=123`` costuma ser
    o que distingue duas páginas inteiramente diferentes.
    """
    parsed = urlparse(url)
    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            parsed.query,
            "",  # fragmento descartado
        )
    )


def same_site(url: str, base_url: str) -> bool:
    """Se a URL pertence ao mesmo host do alvo.

    Comparação estrita por host, e não por domínio registrável: subdomínios
    distintos de um mesmo órgão costumam ser sistemas diferentes, com equipes e
    níveis de conformidade diferentes, e misturá-los na mesma amostra
    comprometeria a atribuição dos achados.
    """
    return urlparse(url).netloc.lower() == urlparse(base_url).netloc.lower()


@dataclass(slots=True)
class HostRateLimiter:
    """Garante intervalo mínimo entre requisições ao mesmo host.

    Implementação simples e propositalmente conservadora: uma trava por host,
    com espera até que o intervalo mínimo desde a última liberação tenha
    decorrido. Não há rajada permitida.
    """

    min_interval_s: float
    _last: dict[str, float] = field(default_factory=dict)
    _locks: dict[str, asyncio.Lock] = field(default_factory=dict)

    async def acquire(self, url: str) -> None:
        """Bloqueia até que seja admissível requisitar o host desta URL."""
        host = urlparse(url).netloc.lower()
        lock = self._locks.setdefault(host, asyncio.Lock())
        async with lock:
            last = self._last.get(host)
            now = time.monotonic()
            if last is not None:
                wait = self.min_interval_s - (now - last)
                if wait > 0:
                    logger.debug(
                        "aguardando intervalo de cortesia",
                        extra={"host": host, "espera_s": round(wait, 2)},
                    )
                    await asyncio.sleep(wait)
            self._last[host] = time.monotonic()


class RobotsGate:
    """Consulta e memoiza o ``robots.txt`` de cada host.

    Política em caso de indisponibilidade do arquivo: **permitir**. Um
    ``robots.txt`` ausente ou com erro 5xx não expressa proibição; tratá-lo como
    negativa impediria auditar exatamente os portais mais precários, enviesando
    a amostra na direção contrária ao objeto do estudo.
    """

    def __init__(self, user_agent: str, *, enabled: bool = True, timeout_s: float = 10.0) -> None:
        """
        Args:
            user_agent: Agente sob o qual as regras são avaliadas.
            enabled: ``False`` desativa a checagem — exige justificativa
                registrada em :class:`~acessisaude_audit.config.Settings`.
            timeout_s: Tempo máximo de espera pelo arquivo.
        """
        self._user_agent = user_agent
        self._enabled = enabled
        self._timeout = timeout_s
        self._cache: dict[str, RobotFileParser | None] = {}

    async def allows(self, url: str) -> bool:
        """Se a coleta desta URL é permitida pelo ``robots.txt`` do host."""
        if not self._enabled:
            return True
        parser = await self._parser_for(url)
        if parser is None:
            return True
        return parser.can_fetch(self._user_agent, url)

    async def crawl_delay(self, url: str) -> float | None:
        """Atraso declarado pelo host, em segundos, se houver.

        Quando o host declara um ``Crawl-delay`` maior que o intervalo
        configurado, o valor do host prevalece — a cortesia declarada pelo
        administrador tem precedência sobre a nossa.
        """
        if not self._enabled:
            return None
        parser = await self._parser_for(url)
        if parser is None:
            return None
        try:
            value = parser.crawl_delay(self._user_agent)
        except (AttributeError, ValueError):  # pragma: no cover
            return None
        return float(value) if value is not None else None

    async def _parser_for(self, url: str) -> RobotFileParser | None:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin in self._cache:
            return self._cache[origin]

        robots_url = urljoin(origin, "/robots.txt")
        parser: RobotFileParser | None = None
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": self._user_agent},
            ) as client:
                response = await client.get(robots_url)
            if response.status_code == 200:
                parser = RobotFileParser()
                parser.parse(response.text.splitlines())
                logger.info("robots.txt carregado", extra={"origem": origin})
            else:
                logger.info(
                    "robots.txt indisponível — coleta permitida",
                    extra={"origem": origin, "http": response.status_code},
                )
        except httpx.HTTPError as exc:
            logger.info(
                "falha ao obter robots.txt — coleta permitida",
                extra={"origem": origin, "erro": str(exc)},
            )

        self._cache[origin] = parser
        return parser


#: JavaScript de extração de links internos da página renderizada.
#:
#: A extração ocorre **após** a renderização porque portais construídos como SPA
#: só materializam a navegação em tempo de execução; ler o HTML servido pelo
#: servidor encontraria uma casca vazia.
_LINKS_SCRIPT = """
() => Array.from(document.querySelectorAll('a[href]'))
  .map(a => a.href)
  .filter(href => href.startsWith('http'))
  .slice(0, 500)
"""


async def discover_links(page: object, base_url: str, *, limit: int = 50) -> list[str]:
    """Extrai links internos da página renderizada, normalizados e sem repetição.

    Args:
        page: Página do Playwright (tipada como ``object`` para manter este
            módulo independente do navegador e testável isoladamente).
        base_url: URL base do alvo, para o filtro de mesmo host.
        limit: Teto de links retornados.

    Returns:
        Lista de URLs internas, na ordem em que aparecem no documento — que
        aproxima a ordem de importância percebida pelo usuário.
    """
    evaluate = getattr(page, "evaluate", None)
    if evaluate is None:  # pragma: no cover - uso indevido
        return []
    raw = await evaluate(_LINKS_SCRIPT)
    if not raw:
        return []

    seen: dict[str, None] = {}
    for href in raw:
        url = normalize_url(str(href))
        if not same_site(url, base_url):
            continue
        # Recursos para download não são páginas: auditá-los produziria erro de
        # navegação, não achado de acessibilidade.
        if (
            urlparse(url)
            .path.lower()
            .endswith((".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png", ".mp4"))
        ):
            continue
        seen.setdefault(url, None)
        if len(seen) >= limit:
            break
    return list(seen)
