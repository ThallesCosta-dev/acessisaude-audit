"""Gestão do navegador e coleta de métricas de rede.

Encapsula o Playwright para que o restante do motor lide com uma abstração
estável (:class:`LoadedPage`) em vez de com a API do navegador. Duas
responsabilidades:

1. Abrir contextos de navegação **reprodutíveis** — locale, fuso, viewport e
   User-Agent fixados, para que a mesma página produza o mesmo resultado em
   máquinas diferentes.
2. Contabilizar o tráfego de rede por requisição, alimentando a dimensão de
   custo para o usuário periférico (:class:`~acessisaude_audit.domain.models.NetworkMetrics`).

Nota sobre a medida de bytes
----------------------------
Usa-se ``request.sizes()`` do Playwright, que reporta os bytes efetivamente
transferidos pelo fio (corpo comprimido + cabeçalhos), e não o tamanho do
recurso descomprimido. É a medida correta para estimar consumo de franquia de
dados — que é o que o usuário paga. Recursos servidos do cache do navegador não
são contabilizados; por isso cada página é auditada em contexto novo, simulando
o primeiro acesso, que é o cenário de pior caso e o mais frequente entre
usuários que limpam dados para liberar espaço no aparelho.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    Request,
    Response,
    async_playwright,
)
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeout

from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import NetworkMetrics, PageStatus, Viewport
from acessisaude_audit.logging_setup import get_logger

__all__ = ["BrowserPool", "LoadedPage", "NetworkRecorder", "registrable_domain"]

logger = get_logger(__name__)


def registrable_domain(host: str) -> str:
    """Aproxima o domínio registrável de um host.

    Heurística: os dois últimos rótulos, com correção para sufixos compostos
    brasileiros (``gov.br``, ``com.br``, ``org.br``, ...), em que os três
    últimos são necessários. Não é uma implementação da Public Suffix List —
    é suficiente e auditável para o recorte deste estudo, que trabalha
    majoritariamente com domínios ``.gov.br``.

    Args:
        host: Host de uma URL, ex. ``"www.saude.rj.gov.br"``.

    Returns:
        O domínio registrável aproximado, ex. ``"rj.gov.br"``.
    """
    labels = host.lower().split(".")
    if len(labels) <= 2:
        return host.lower()
    compound = {"gov.br", "com.br", "org.br", "net.br", "edu.br", "co.uk", "gov.uk"}
    if ".".join(labels[-2:]) in compound and len(labels) >= 3:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


@dataclass
class NetworkRecorder:
    """Acumula o tráfego observado durante o carregamento de uma página.

    Instanciado por página e desligado assim que a auditoria daquela página
    termina, para não contabilizar requisições disparadas por sondas
    subsequentes (que injetam scripts, mas não recursos de rede do portal).

    .. note::
       Esta classe **não** usa ``slots=True``, ao contrário das demais
       dataclasses do módulo. O Playwright memoiza o handler embrulhado
       gravando um atributo no objeto que o expõe
       (``_pw_impl_instance_on_request_finished``); com ``__slots__``, essa
       gravação levanta ``AttributeError`` e o registro de tráfego falha em
       toda página. A economia de memória não compensa: há um recorder por
       página, vivo por segundos.
    """

    origin_domain: str
    total_bytes: int = 0
    request_count: int = 0
    third_party_bytes: int = 0
    blocked_requests: int = 0
    bytes_by_type: dict[str, int] = field(default_factory=dict)
    third_party_domains: set[str] = field(default_factory=set)
    active: bool = True

    async def on_request_finished(self, request: Request) -> None:
        """Handler de ``requestfinished``: soma os bytes transferidos."""
        if not self.active:
            return
        try:
            sizes = await request.sizes()
        except PlaywrightError:
            # A requisição pode ter sido descartada com o fechamento da página.
            # Perder uma medição é preferível a derrubar a auditoria inteira.
            return

        # Bytes efetivamente trafegados: corpo comprimido + cabeçalhos. É a
        # medida que corresponde ao consumo de franquia do usuário.
        transferred = (sizes.get("responseBodySize") or 0) + (sizes.get("responseHeadersSize") or 0)

        self.request_count += 1
        self.total_bytes += transferred

        rtype = request.resource_type or "other"
        self.bytes_by_type[rtype] = self.bytes_by_type.get(rtype, 0) + transferred

        host = _host_of(request.url)
        if host:
            domain = registrable_domain(host)
            if domain != self.origin_domain:
                self.third_party_bytes += transferred
                self.third_party_domains.add(domain)

    def on_request_failed(self, request: Request) -> None:
        """Handler de ``requestfailed``: registra recursos que não carregaram.

        Requisições falhas importam para a análise: um portal que depende de um
        CDN indisponível degrada silenciosamente para o usuário.
        """
        if self.active:
            self.blocked_requests += 1

    def stop(self) -> None:
        """Encerra a coleta."""
        self.active = False

    def to_metrics(self, timings: dict[str, float | None]) -> NetworkMetrics:
        """Materializa o modelo de domínio a partir do que foi acumulado."""
        return NetworkMetrics(
            total_bytes=self.total_bytes,
            request_count=self.request_count,
            bytes_by_type=dict(sorted(self.bytes_by_type.items())),
            third_party_bytes=self.third_party_bytes,
            third_party_domains=sorted(self.third_party_domains),
            blocked_requests=self.blocked_requests,
            dom_content_loaded_ms=timings.get("dom_content_loaded_ms"),
            load_complete_ms=timings.get("load_complete_ms"),
            largest_contentful_paint_ms=timings.get("largest_contentful_paint_ms"),
        )


def _host_of(url: str) -> str:
    from urllib.parse import urlparse

    try:
        return urlparse(url).netloc.split("@")[-1].split(":")[0]
    except ValueError:  # pragma: no cover - URL exótica
        return ""


@dataclass(slots=True)
class LoadedPage:
    """Uma página carregada e pronta para inspeção.

    Attributes:
        page: Handle do Playwright, usado pelas sondas.
        url: URL solicitada.
        final_url: URL após redirecionamentos.
        status: Resultado do carregamento.
        http_status: Código HTTP da resposta principal.
        network: Métricas de tráfego coletadas.
        error: Mensagem, quando ``status`` não é ``OK``.
    """

    page: Page
    url: str
    final_url: str
    status: PageStatus
    http_status: int | None
    network: NetworkMetrics
    error: str | None = None

    @property
    def ok(self) -> bool:
        """``True`` se a página carregou e pode ser auditada."""
        return self.status is PageStatus.OK


#: JavaScript de coleta de tempos, executado no contexto da página.
#:
#: Usa a Navigation Timing API (nível 2) e o PerformanceObserver de LCP. Retorna
#: ``null`` nos campos indisponíveis em vez de zero, para que "não medido" não
#: se confunda com "instantâneo" na análise.
_TIMINGS_SCRIPT = """
() => {
  const nav = performance.getEntriesByType('navigation')[0];
  const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
  const lcp = lcpEntries.length ? lcpEntries[lcpEntries.length - 1].startTime : null;
  return {
    dom_content_loaded_ms: nav ? nav.domContentLoadedEventEnd : null,
    load_complete_ms: nav ? nav.loadEventEnd : null,
    largest_contentful_paint_ms: lcp,
  };
}
"""


class BrowserPool:
    """Ciclo de vida do Playwright e fábrica de contextos de navegação.

    Um único navegador é reutilizado por varredura (barato), mas cada página é
    auditada em um **contexto novo** (isolado). O isolamento é metodológico:
    contextos compartilhados acumulam cache e cookies, o que subestimaria o
    custo de dados e mascararia banners de consentimento que só aparecem no
    primeiro acesso.

    Uso::

        async with BrowserPool(settings) as pool:
            loaded = await pool.open(url, viewport)
            ...
            await pool.close_page(loaded)
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._recorders: dict[int, NetworkRecorder] = {}
        self._contexts: dict[int, BrowserContext] = {}

    async def __aenter__(self) -> Self:
        self._playwright = await async_playwright().start()
        launcher = getattr(self._playwright, self._settings.browser)
        self._browser = await launcher.launch(
            headless=self._settings.headless,
            args=["--disable-dev-shm-usage"] if self._settings.browser == "chromium" else [],
        )
        logger.info("navegador iniciado", extra={"browser": self.browser_signature})
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        for context in list(self._contexts.values()):
            with contextlib.suppress(PlaywrightError):
                await context.close()
        self._contexts.clear()
        if self._browser is not None:
            with contextlib.suppress(PlaywrightError):
                await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()
        logger.info("navegador encerrado")

    @property
    def browser_signature(self) -> str:
        """Identificação do navegador para o registro da varredura."""
        if self._browser is None:
            return self._settings.browser
        return f"{self._settings.browser} {self._browser.version}"

    async def open(self, url: str, viewport: Viewport) -> LoadedPage:
        """Carrega uma URL em contexto isolado e devolve a página pronta.

        Nunca levanta exceção por falha de navegação: erros viram
        :class:`~acessisaude_audit.domain.models.PageStatus` no resultado, para
        que uma página inacessível por indisponibilidade não interrompa a
        varredura das demais — e para que a taxa de perda seja mensurável.

        Args:
            url: Endereço a carregar.
            viewport: Perfil de dispositivo a simular.

        Returns:
            :class:`LoadedPage`, com ``ok == False`` em caso de falha.
        """
        if self._browser is None:  # pragma: no cover - erro de uso
            raise RuntimeError("BrowserPool deve ser usado como context manager")

        s = self._settings
        base_ua = viewport.user_agent
        user_agent = f"{base_ua} {s.user_agent_suffix}" if base_ua else None

        context = await self._browser.new_context(
            viewport={"width": viewport.width, "height": viewport.height},
            device_scale_factor=viewport.device_scale_factor,
            is_mobile=viewport.is_mobile,
            has_touch=viewport.is_mobile,
            locale=s.locale,
            timezone_id=s.timezone_id,
            user_agent=user_agent,
            # Reduz falso-negativo de contraste: o axe-core avalia as cores
            # efetivamente computadas, então o esquema precisa ser determinado.
            color_scheme="light",
            reduced_motion="no-preference",
        )
        if user_agent is None:
            # Sem UA customizado (perfil desktop), ainda assim nos identificamos.
            await context.set_extra_http_headers({"X-Audit-Agent": s.user_agent_suffix})

        page = await context.new_page()
        page.set_default_navigation_timeout(s.navigation_timeout_ms)
        page.set_default_timeout(s.navigation_timeout_ms)

        recorder = NetworkRecorder(origin_domain=registrable_domain(_host_of(url)))
        page.on("requestfinished", recorder.on_request_finished)
        page.on("requestfailed", recorder.on_request_failed)

        key = id(page)
        self._recorders[key] = recorder
        self._contexts[key] = context

        status = PageStatus.OK
        error: str | None = None
        http_status: int | None = None
        response: Response | None = None

        try:
            response = await page.goto(url, wait_until="domcontentloaded")
            # 'networkidle' é intencionalmente tolerante a falha: portais com
            # polling permanente nunca ficam ociosos, e esperar até o timeout
            # apenas desperdiça tempo sem melhorar a medição.
            with contextlib.suppress(PlaywrightTimeout):
                await page.wait_for_load_state("networkidle", timeout=s.navigation_timeout_ms)
            if s.settle_delay_ms:
                await asyncio.sleep(s.settle_delay_ms / 1000)
            http_status = response.status if response else None
            if http_status is not None and http_status >= 400:
                status = PageStatus.HTTP_ERROR
                error = f"HTTP {http_status}"
        except PlaywrightTimeout as exc:
            status = PageStatus.TIMEOUT
            error = f"Timeout de navegação após {s.navigation_timeout_ms} ms: {exc}"
        except PlaywrightError as exc:
            status = PageStatus.NAVIGATION_ERROR
            error = str(exc)

        timings: dict[str, float | None] = {}
        if status is PageStatus.OK:
            with contextlib.suppress(PlaywrightError):
                timings = await page.evaluate(_TIMINGS_SCRIPT)

        recorder.stop()

        return LoadedPage(
            page=page,
            url=url,
            final_url=page.url if status is not PageStatus.NAVIGATION_ERROR else url,
            status=status,
            http_status=http_status,
            network=recorder.to_metrics(timings),
            error=error,
        )

    async def close_page(self, loaded: LoadedPage) -> None:
        """Fecha a página e descarta seu contexto isolado."""
        key = id(loaded.page)
        self._recorders.pop(key, None)
        context = self._contexts.pop(key, None)
        with contextlib.suppress(PlaywrightError):
            await loaded.page.close()
        if context is not None:
            with contextlib.suppress(PlaywrightError):
                await context.close()

    async def evaluate(self, page: Page, script: str, arg: Any = None) -> Any:
        """Executa JavaScript na página com tratamento uniforme de erro.

        Sondas usam este atalho para que uma exceção em uma verificação isolada
        não derrube a auditoria da página inteira.
        """
        try:
            return await page.evaluate(script, arg)
        except PlaywrightError as exc:
            logger.warning("falha ao avaliar script na página", extra={"erro": str(exc)})
            return None
