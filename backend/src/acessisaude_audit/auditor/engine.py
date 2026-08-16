"""Orquestração da varredura: do catálogo ao :class:`ScanResult`.

O motor é deliberadamente burro. Ele não decide o que é violação (isso é do
axe-core e das sondas), não decide o que é ilegal (isso é de ``domain.mapping``)
e não decide como pontuar (isso é de ``domain.scoring``). Ele decide **o que
visitar, em que ordem, sob quais restrições de conduta**, e monta o registro do
que aconteceu — inclusive do que deu errado.

Essa modéstia é arquitetural: as três decisões que o motor não toma são
exatamente as que precisam ser defendidas no artigo, e mantê-las fora do código
de coleta permite discuti-las, testá-las e alterá-las sem tocar no navegador.

Fluxo de uma varredura::

    catálogo → lista de URLs (sementes + descoberta opcional)
             → para cada URL × viewport:
                   conduta (robots + intervalo)
                   carregar (browser)
                   axe-core  ─┐
                   sondas    ─┴→ achados
                   métricas de rede
             → ScanResult (+ erros e lacunas declaradas)
"""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from urllib.parse import urlparse

from acessisaude_audit import __version__
from acessisaude_audit.auditor.axe_runner import AxeRunner
from acessisaude_audit.auditor.browser import BrowserPool, LoadedPage
from acessisaude_audit.auditor.crawler import (
    HostRateLimiter,
    RobotsGate,
    discover_links,
    normalize_url,
)
from acessisaude_audit.auditor.probes import Probe, ProbeContext, default_probes
from acessisaude_audit.catalog.loader import SeedPage, Target
from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import (
    Finding,
    PageAudit,
    PageStatus,
    ScanResult,
    ScanStatus,
    Viewport,
    utcnow,
)
from acessisaude_audit.logging_setup import get_logger

__all__ = ["AuditEngine", "PageTask", "ScanPlan"]

logger = get_logger(__name__)

#: Assinatura do callback de progresso: (concluídas, total, url corrente).
ProgressCallback = Callable[[int, int, str], None]


@dataclass(frozen=True, slots=True)
class PageTask:
    """Uma unidade de trabalho: uma URL em um perfil de dispositivo."""

    url: str
    viewport: Viewport
    label: str = ""
    is_critical_path: bool = False

    def __str__(self) -> str:
        return f"{self.url} [{self.viewport.name}]"


@dataclass(frozen=True, slots=True)
class ScanPlan:
    """O que será auditado, decidido antes de abrir o navegador.

    Materializar o plano antes da execução tem duas consequências desejáveis:
    o total de tarefas é conhecido (permitindo barra de progresso e estimativa),
    e o plano pode ser inspecionado, registrado e reexecutado — é ele que torna
    a coleta reprodutível.
    """

    target: Target
    tasks: tuple[PageTask, ...]
    declared_gaps: tuple[SeedPage, ...]

    @property
    def total(self) -> int:
        """Número de auditorias de página a executar."""
        return len(self.tasks)

    @property
    def unique_urls(self) -> int:
        """Número de URLs distintas no plano."""
        return len({t.url for t in self.tasks})


class AuditEngine:
    """Executa varreduras de acessibilidade sobre alvos do catálogo."""

    def __init__(
        self,
        settings: Settings,
        *,
        probes: Sequence[Probe] | None = None,
    ) -> None:
        """
        Args:
            settings: Configuração de execução.
            probes: Sondas a executar. ``None`` usa o conjunto padrão. Injetar
                a lista permite testar o motor com uma única sonda e permite
                que o artigo relate execuções com subconjuntos diferentes.
        """
        self._settings = settings
        self._probes = list(probes) if probes is not None else default_probes()
        self._axe = AxeRunner(
            settings.axe_tags,
            script_path=settings.axe_script_path,
            max_html_chars=settings.max_html_snippet_chars,
        )
        self._robots = RobotsGate(settings.user_agent_suffix, enabled=settings.respect_robots_txt)
        self._limiter = HostRateLimiter(settings.request_delay_ms / 1000)

    # ------------------------------------------------------------------ plano

    def plan(self, target: Target, *, viewports: Sequence[Viewport] | None = None) -> ScanPlan:
        """Monta o plano de varredura a partir das sementes do alvo.

        Sementes que exigem autenticação são excluídas e registradas como
        lacunas declaradas — não como páginas ausentes.
        """
        vps = tuple(viewports) if viewports is not None else self._settings.viewports()
        tasks: list[PageTask] = []
        seen: set[tuple[str, str]] = set()

        for seed in target.auditable_seeds:
            url = normalize_url(seed.url)
            for viewport in vps:
                key = (url, viewport.name)
                if key in seen:
                    continue
                seen.add(key)
                tasks.append(
                    PageTask(
                        url=url,
                        viewport=viewport,
                        label=seed.label,
                        is_critical_path=seed.critical,
                    )
                )
                if len(tasks) >= self._settings.max_pages_per_target * len(vps):
                    break

        return ScanPlan(
            target=target,
            tasks=tuple(tasks),
            declared_gaps=tuple(target.declared_gaps),
        )

    # -------------------------------------------------------------- execução

    async def run(
        self,
        target: Target,
        *,
        viewports: Sequence[Viewport] | None = None,
        discover: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> ScanResult:
        """Executa a varredura completa de um alvo.

        Args:
            target: Alvo do catálogo.
            viewports: Perfis a usar. ``None`` usa os padrões.
            discover: Se ``True``, complementa as sementes com links internos
                descobertos na primeira página. Desligado por padrão: descoberta
                automática produz amostra não reproduzível, porque o conjunto de
                links muda a cada publicação de conteúdo.
            on_progress: Chamado a cada página concluída.

        Returns:
            :class:`ScanResult` completo. Nunca levanta exceção por falha de
            página: erros viram registro, e a varredura é marcada como
            ``PARTIAL``.
        """
        plan = self.plan(target, viewports=viewports)
        scan = ScanResult(
            target_id=target.id,
            target_name=target.name,
            base_url=target.base_url,
            status=ScanStatus.RUNNING,
            engine_version=__version__,
            config_snapshot={
                **self._settings.snapshot(),
                "plan": {
                    "total_tasks": plan.total,
                    "unique_urls": plan.unique_urls,
                    "discover_enabled": discover,
                    "declared_gaps": [
                        {"url": g.url, "label": g.label, "motivo": g.notes or "exige autenticação"}
                        for g in plan.declared_gaps
                    ],
                },
                "probes": [p.id for p in self._probes],
            },
        )

        logger.info(
            "varredura iniciada",
            extra={
                "alvo": target.id,
                "tarefas": plan.total,
                "urls": plan.unique_urls,
                "lacunas_declaradas": len(plan.declared_gaps),
            },
        )

        self._settings.ensure_directories()

        async with BrowserPool(self._settings) as pool:
            scan.browser = pool.browser_signature
            tasks = list(plan.tasks)

            if discover and tasks:
                tasks = await self._expand_with_discovery(pool, target, tasks)

            semaphore = asyncio.Semaphore(self._settings.concurrency)
            completed = 0

            async def audit(task: PageTask) -> PageAudit:
                nonlocal completed
                async with semaphore:
                    audit_result = await self._audit_page(pool, task)
                    completed += 1
                    if on_progress is not None:
                        on_progress(completed, len(tasks), task.url)
                    return audit_result

            results = await asyncio.gather(*(audit(t) for t in tasks), return_exceptions=True)

        for task, outcome in zip(tasks, results, strict=True):
            if isinstance(outcome, BaseException):
                # Falha não prevista: registra e segue. Uma varredura que morre
                # na página 12 de 40 perde as 28 seguintes; uma que registra o
                # erro mantém o dataset utilizável com perda mensurável.
                #
                # `exc_info=outcome` em vez de `logger.exception`: aqui não há
                # exceção ativa (ela foi capturada por `gather`), e
                # `logger.exception` gravaria "NoneType: None" no lugar do
                # traceback — escondendo justamente o defeito que precisa ser
                # diagnosticado.
                logger.error(
                    "falha inesperada ao auditar página",
                    exc_info=outcome,
                    extra={"url": task.url, "viewport": task.viewport.name},
                )
                scan.errors.append(f"{task.url} [{task.viewport.name}]: {outcome!r}")
                scan.pages.append(
                    PageAudit(
                        url=task.url,
                        viewport=task.viewport,
                        status=PageStatus.NAVIGATION_ERROR,
                        error=repr(outcome),
                        finished_at=utcnow(),
                        is_critical_path=task.is_critical_path,
                    )
                )
            else:
                scan.pages.append(outcome)

        scan.axe_version = next((p.axe_version for p in scan.pages if p.axe_version), None)
        scan.finished_at = utcnow()
        failed = [p for p in scan.pages if p.status is not PageStatus.OK]
        if not scan.pages:
            scan.status = ScanStatus.FAILED
        elif failed:
            scan.status = ScanStatus.PARTIAL
        else:
            scan.status = ScanStatus.COMPLETED

        logger.info(
            "varredura concluída",
            extra={
                "alvo": target.id,
                "status": scan.status.value,
                "paginas": scan.page_count,
                "violacoes": scan.violation_count,
                "perda": scan.loss_rate,
            },
        )
        return scan

    async def _expand_with_discovery(
        self, pool: BrowserPool, target: Target, tasks: list[PageTask]
    ) -> list[PageTask]:
        """Acrescenta ao plano links internos descobertos na primeira semente."""
        first = tasks[0]
        await self._await_politeness(first.url)
        loaded = await pool.open(first.url, first.viewport)
        try:
            if not loaded.ok:
                logger.warning(
                    "descoberta ignorada: primeira semente não carregou",
                    extra={"url": first.url, "status": loaded.status.value},
                )
                return tasks
            budget = self._settings.max_pages_per_target - len({t.url for t in tasks})
            if budget <= 0:
                return tasks
            links = await discover_links(loaded.page, target.base_url, limit=budget)
        finally:
            await pool.close_page(loaded)

        known = {t.url for t in tasks}
        viewports = {t.viewport.name: t.viewport for t in tasks}.values()
        added = 0
        for link in links:
            if link in known:
                continue
            known.add(link)
            for viewport in viewports:
                tasks.append(PageTask(url=link, viewport=viewport, label="descoberta"))
            added += 1

        logger.info("descoberta concluída", extra={"urls_novas": added})
        return tasks

    async def _await_politeness(self, url: str) -> None:
        """Aplica o intervalo de cortesia, respeitando ``Crawl-delay`` do host."""
        declared = await self._robots.crawl_delay(url)
        if declared is not None and declared > self._limiter.min_interval_s:
            logger.info(
                "adotando Crawl-delay declarado pelo host",
                extra={"url": url, "crawl_delay_s": declared},
            )
            await asyncio.sleep(declared - self._limiter.min_interval_s)
        await self._limiter.acquire(url)

    async def _audit_page(self, pool: BrowserPool, task: PageTask) -> PageAudit:
        """Audita uma única página em um único viewport."""
        started = utcnow()

        if not await self._robots.allows(task.url):
            logger.info("página bloqueada por robots.txt", extra={"url": task.url})
            return PageAudit(
                url=task.url,
                viewport=task.viewport,
                status=PageStatus.BLOCKED_BY_ROBOTS,
                started_at=started,
                finished_at=utcnow(),
                error="Coleta não permitida pelo robots.txt do host.",
                is_critical_path=task.is_critical_path,
            )

        await self._await_politeness(task.url)
        loaded = await pool.open(task.url, task.viewport)

        try:
            if not loaded.ok:
                return PageAudit(
                    url=task.url,
                    final_url=loaded.final_url,
                    viewport=task.viewport,
                    status=loaded.status,
                    http_status=loaded.http_status,
                    network=loaded.network,
                    started_at=started,
                    finished_at=utcnow(),
                    error=loaded.error,
                    is_critical_path=task.is_critical_path,
                )

            findings, axe_version = await self._collect_findings(loaded, task)
            title, lang = await self._page_identity(loaded)
            screenshot = await self._capture_screenshot(loaded, task)

            return PageAudit(
                url=task.url,
                final_url=loaded.final_url,
                viewport=task.viewport,
                status=PageStatus.OK,
                http_status=loaded.http_status,
                title=title,
                lang=lang,
                findings=findings,
                network=loaded.network,
                started_at=started,
                finished_at=utcnow(),
                axe_version=axe_version,
                screenshot_path=screenshot,
                is_critical_path=task.is_critical_path,
            )
        finally:
            await pool.close_page(loaded)

    async def _collect_findings(
        self, loaded: LoadedPage, task: PageTask
    ) -> tuple[list[Finding], str | None]:
        """Executa axe-core e sondas, reunindo todos os achados da página."""
        findings: list[Finding] = []
        axe_version: str | None = None

        result = await self._axe.run(loaded.page)
        if result is not None:
            axe_version = result.engine_version
            findings.extend(
                self._axe.to_findings(
                    result, page_url=loaded.final_url, viewport_name=task.viewport.name
                )
            )

        context = ProbeContext(
            page=loaded.page,
            url=loaded.final_url,
            viewport=task.viewport,
            is_critical_path=task.is_critical_path,
            network=loaded.network,
            scoring=self._settings.scoring_parameters(),
        )
        for probe in self._probes:
            findings.extend(await probe.run(context))

        return findings, axe_version

    async def _page_identity(self, loaded: LoadedPage) -> tuple[str | None, str | None]:
        """Título e idioma declarado da página."""
        data = await loaded.page.evaluate(
            "() => ({ title: document.title || null, "
            "lang: document.documentElement.getAttribute('lang') })"
        )
        if not isinstance(data, dict):
            return None, None
        return data.get("title"), data.get("lang")

    async def _capture_screenshot(self, loaded: LoadedPage, task: PageTask) -> str | None:
        """Salva captura de tela de evidência, se habilitado.

        A captura serve ao relatório entregue ao gestor: um achado de contraste
        acompanhado da imagem é imediatamente verificável por quem não lê CSS.

        Nome do arquivo: host abreviado + resumo criptográfico curto da URL. A
        primeira versão derivava o nome da URL inteira, o que produziu caminhos
        que excedem o limite do Windows em portais com rota longa — o arquivo
        era gravado, mas ficava inutilizável para qualquer ferramenta que o
        percorresse. O resumo mantém o nome curto e estável entre execuções, e o
        host preserva a legibilidade; a URL completa continua no JSON.
        """
        if not self._settings.capture_screenshots:
            return None

        normalizada = normalize_url(task.url)
        host = urlparse(normalizada).netloc.replace(":", "-")[:40] or "sem-host"
        resumo = hashlib.sha1(normalizada.encode("utf-8")).hexdigest()[:10]
        path = self._settings.screenshots_dir / f"{host}__{resumo}__{task.viewport.name}.png"
        try:
            await loaded.page.screenshot(path=str(path), full_page=False)
        except Exception as exc:
            logger.debug("falha ao capturar tela", extra={"url": task.url, "erro": str(exc)})
            return None
        return str(path)
