"""Interface de linha de comando — a via principal da coleta de pesquisa.

O dashboard serve à leitura dos resultados; a coleta acontece aqui. A razão é
metodológica: uma varredura precisa ser um comando registrável, repetível e
citável no artigo ("os dados foram obtidos com
``acessisaude varrer fixtures-local --viewport mobile-320``"), e não uma
sequência de cliques que ninguém consegue reproduzir.

Comandos::

    acessisaude alvos                    lista o catálogo
    acessisaude criterios                lista os critérios WCAG com vínculo jurídico
    acessisaude matriz                   verifica a integridade da matriz WCAG↔LBI
    acessisaude varrer ALVO              executa uma auditoria
    acessisaude relatorio ARQUIVO        gera o relatório HTML de um JSON
    acessisaude exportar                 exporta CSV de várias varreduras
    acessisaude servir                   sobe a API
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from acessisaude_audit import __version__
from acessisaude_audit.auditor.engine import AuditEngine
from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import get_settings
from acessisaude_audit.domain.mapping import mapping_for, unmapped_criteria
from acessisaude_audit.domain.models import ScanResult
from acessisaude_audit.domain.scoring import score_scan, summarize_by_group
from acessisaude_audit.domain.wcag import WCAG_CRITERIA
from acessisaude_audit.logging_setup import configure_logging
from acessisaude_audit.persistence.database import (
    create_database_engine,
    init_database,
    make_session_factory,
    session_scope,
)
from acessisaude_audit.persistence.repositories import JsonScanStore, ScanRepository
from acessisaude_audit.reporting.exports import export_findings_csv, export_pages_csv
from acessisaude_audit.reporting.html import formatar_reais, write_report

app = typer.Typer(
    name="acessisaude",
    help="Auditoria contínua de acessibilidade (WCAG 2.1 / LBI) em saúde pública.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"AcessiSaúde-Audit {__version__}")
        raise typer.Exit


@app.callback()
def main(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Registro em nível DEBUG.")
    ] = False,
    json_log: Annotated[
        bool, typer.Option("--json-log", help="Registro em JSONL, para execuções em CI.")
    ] = False,
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Versão."),
    ] = False,
) -> None:
    """Configura o registro antes de qualquer comando."""
    configure_logging("DEBUG" if verbose else get_settings().log_level, json_output=json_log)


# ---------------------------------------------------------------------------
# Catálogo e referência normativa
# ---------------------------------------------------------------------------


@app.command("alvos")
def list_targets(
    esfera: Annotated[str | None, typer.Option(help="Filtra por esfera federativa.")] = None,
) -> None:
    """Lista as plataformas do catálogo e o estado de habilitação de cada uma."""
    catalog = load_catalog(get_settings().catalog_path)
    table = Table(
        title=f"Catálogo de alvos — janela: {catalog.collection_window or 'não definida'}"
    )
    table.add_column("id", style="bold")
    table.add_column("nome")
    table.add_column("esfera")
    table.add_column("páginas", justify="right")
    table.add_column("lacunas", justify="right")
    table.add_column("estado")

    for target in catalog.targets:
        if esfera and target.sphere.value != esfera:
            continue
        table.add_row(
            target.id,
            target.name,
            target.sphere.value,
            str(len(target.auditable_seeds)),
            str(len(target.declared_gaps)),
            "[green]habilitado[/]" if target.enabled else "[yellow]desabilitado[/]",
        )

    console.print(table)
    console.print(
        "[dim]Alvos de produção nascem desabilitados por conduta de coleta. "
        "Habilitar é decisão consciente do pesquisador — ver "
        "docs/metodologia/etica-e-conduta-de-coleta.md[/]"
    )


@app.command("criterios")
def list_criteria(
    apenas_automatizaveis: Annotated[
        bool, typer.Option(help="Somente critérios com veredito automático.")
    ] = False,
) -> None:
    """Lista os 50 critérios WCAG 2.1 A/AA com risco jurídico e cobertura."""
    table = Table(title="Critérios WCAG 2.1 (A/AA) e vínculo jurídico")
    table.add_column("id", style="bold")
    table.add_column("critério")
    table.add_column("nív.")
    table.add_column("automático")
    table.add_column("risco jurídico")

    cores = {"critico": "red", "alto": "dark_orange", "moderado": "yellow", "baixo": "cyan"}
    automated = 0
    for sc in WCAG_CRITERIA:
        if apenas_automatizaveis and not sc.automatable:
            continue
        automated += int(sc.automatable)
        m = mapping_for(sc.id)
        risk = m.legal_risk.value if m else "—"
        table.add_row(
            sc.id,
            sc.title_pt,
            sc.level.value,
            "[green]sim[/]" if sc.automatable else "[dim]manual[/]",
            f"[{cores.get(risk, 'white')}]{risk}[/]",
        )

    console.print(table)
    total_auto = sum(1 for c in WCAG_CRITERIA if c.automatable)
    console.print(
        f"[bold]Cobertura automática:[/] {total_auto}/{len(WCAG_CRITERIA)} critérios "
        f"({total_auto / len(WCAG_CRITERIA):.0%}). "
        "Os demais exigem julgamento humano — ausência de achado não é conformidade."
    )


@app.command("matriz")
def check_matrix() -> None:
    """Verifica se todo critério do escopo possui fundamentação jurídica."""
    orphans = unmapped_criteria()
    if orphans:
        console.print(
            Panel(
                "\n".join(f"• {c}" for c in orphans),
                title="[red]Critérios sem mapeamento jurídico[/]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)
    console.print(
        Panel(
            f"Todos os {len(WCAG_CRITERIA)} critérios A/AA possuem mapeamento jurídico.",
            title="[green]Matriz WCAG↔LBI íntegra[/]",
            border_style="green",
        )
    )


# ---------------------------------------------------------------------------
# Varredura
# ---------------------------------------------------------------------------


@app.command("varrer")
def scan(
    target_id: Annotated[str, typer.Argument(help="Identificador do alvo no catálogo.")],
    viewport: Annotated[
        list[str] | None,
        typer.Option("--viewport", help="Perfil de dispositivo (repetível)."),
    ] = None,
    descobrir: Annotated[
        bool,
        typer.Option(
            "--descobrir",
            help=(
                "Complementa as sementes com links da primeira página. Reduz a "
                "reprodutibilidade da amostra — usar com parcimônia."
            ),
        ),
    ] = False,
    relatorio: Annotated[
        bool, typer.Option("--relatorio/--sem-relatorio", help="Gera o HTML ao final.")
    ] = True,
    persistir: Annotated[
        bool, typer.Option("--persistir/--sem-persistir", help="Grava no banco.")
    ] = True,
) -> None:
    """Executa uma auditoria completa de um alvo do catálogo."""
    settings = get_settings()
    catalog = load_catalog(settings.catalog_path)

    try:
        target = catalog.get(target_id)
    except KeyError:
        console.print(f"[red]Alvo não encontrado:[/] {target_id}")
        console.print("Use [bold]acessisaude alvos[/] para ver os disponíveis.")
        raise typer.Exit(code=1) from None

    if not target.enabled:
        console.print(
            Panel(
                f"O alvo [bold]{target.id}[/] está desabilitado no catálogo.\n\n"
                "Alvos de produção nascem desabilitados por conduta de coleta. Habilitá-lo "
                "significa assumir: respeito ao robots.txt, intervalo mínimo entre "
                "requisições, identificação no User-Agent e ausência de qualquer "
                "interação com formulários ou autenticação.\n\n"
                "Edite [bold]enabled: true[/] em targets.yaml para prosseguir.",
                title="[yellow]Varredura não executada[/]",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=2)

    viewports = settings.viewports()
    if viewport:
        wanted = set(viewport)
        viewports = tuple(v for v in viewports if v.name in wanted)
        if not viewports:
            known = ", ".join(v.name for v in settings.viewports())
            console.print(f"[red]Perfil desconhecido.[/] Disponíveis: {known}")
            raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold]{target.name}[/]\n{target.base_url}\n\n"
            f"Páginas auditáveis: {len(target.auditable_seeds)}\n"
            f"Lacunas declaradas (exigem autenticação): {len(target.declared_gaps)}\n"
            f"Perfis: {', '.join(v.name for v in viewports)}\n"
            f"Intervalo entre requisições: {settings.request_delay_ms} ms\n"
            f"robots.txt: {'respeitado' if settings.respect_robots_txt else 'IGNORADO'}",
            title="Varredura",
        )
    )

    result = asyncio.run(_run_scan(target, settings, list(viewports), descobrir))
    _print_summary(result)

    store = JsonScanStore(settings.scans_dir)
    json_path = store.save(result)
    console.print(f"[green]JSON:[/] {json_path}")

    if persistir:
        engine = create_database_engine(settings.resolved_database_url())
        init_database(engine)
        with session_scope(make_session_factory(engine)) as session:
            ScanRepository(session, params=settings.scoring_parameters()).save(
                result, json_path=json_path, sphere=target.sphere.value
            )
        console.print(f"[green]Banco:[/] {settings.resolved_database_url()}")

    if relatorio:
        path = write_report(result, settings.exports_dir, params=settings.scoring_parameters())
        console.print(f"[green]Relatório:[/] {path}")


async def _run_scan(
    target: object, settings: object, viewports: list, discover: bool
) -> ScanResult:
    """Executa a varredura exibindo progresso."""
    engine = AuditEngine(settings)  # type: ignore[arg-type]
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Auditando…", total=None)

        def on_progress(done: int, total: int, url: str) -> None:
            progress.update(task, completed=done, total=total, description=url[:70])

        return await engine.run(
            target,  # type: ignore[arg-type]
            viewports=viewports,
            discover=discover,
            on_progress=on_progress,
        )


def _print_summary(scan: ScanResult) -> None:
    """Imprime os índices e o perfil de exclusão da varredura."""
    score = score_scan(scan, get_settings().scoring_parameters())

    if not score.observed:
        console.print(
            Panel(
                "Nenhuma página desta varredura carregou, de modo que não há observação "
                "sobre a qual emitir juízo. Os índices aparecem como traços: isso "
                "[bold]não é conformidade nem não conformidade[/].\n\n"
                "Se a falha atingiu todos os alvos da coleta, suspeite primeiro da rede "
                "de quem audita, e não dos portais auditados.",
                title="[yellow]Sem veredito[/]",
                border_style="yellow",
            )
        )

    if score.absolute_barrier:
        console.print(
            Panel(
                "Foram detectadas violações de risco jurídico [bold]crítico[/]: barreiras "
                "que impedem completamente o uso por um grupo identificável, sem rota "
                "alternativa. Os demais índices descrevem a dificuldade de um serviço "
                "que, para essas pessoas, está indisponível.",
                title="[red]Barreira absoluta[/]",
                border_style="red",
            )
        )

    table = Table(title="Índices agregados")
    table.add_column("indicador")
    table.add_column("valor", justify="right")
    table.add_column("leitura")

    def _indice(valor: float | None) -> str:
        """Traço quando não houve observação — nunca um número inventado."""
        return f"{valor:.1f}" if valor is not None else "—"

    table.add_row("ICA — Conformidade", _indice(score.conformance_index), "0–100, maior é melhor")
    table.add_row("IAN — Atrito", _indice(score.friction_index), "0–100, menor é melhor")
    table.add_row(
        "IEJ — Exposição jurídica",
        _indice(score.legal_exposure_index),
        "0–100, menor é melhor",
    )
    table.add_row("Violações", str(score.violations), f"{score.occurrences} ocorrências")
    table.add_row("Revisão humana", str(score.incomplete), "achados indeterminados")
    table.add_row("Cobertura", f"{score.coverage:.0%}", f"{score.criteria_evaluated}/50 critérios")
    table.add_row("Perda de páginas", f"{scan.loss_rate:.1%}", "erros de navegação")
    if score.data_cost:
        custo = score.data_cost
        table.add_row(
            "Peso médio",
            f"{custo.total_mb:.2f} MB",
            f"{formatar_reais(custo.cost_brl)} por acesso, "
            f"{custo.franchise_share_pct:.3f}% da franquia mensal",
        )
        # Quatro acessos mensais: acompanhar um agendamento ou um resultado de
        # exame não é ato único, e é na repetição que o custo deixa de ser
        # desprezível. Sem esta linha, o custo real pareceria irrelevante.
        table.add_row(
            "Custo da jornada",
            formatar_reais(custo.monthly_cost_brl_at_4_visits),
            f"4 acessos/mês · {custo.franchise_share_pct * 4:.2f}% da franquia",
        )
        if custo.third_party_share_pct > 0:
            table.add_row(
                "Tráfego de terceiros",
                f"{custo.third_party_share_pct:.0f}%",
                "custo transferido ao usuário sem contrapartida no serviço",
            )
    console.print(table)

    grupos = summarize_by_group(score)
    if grupos:
        gt = Table(title="Quem é excluído (ocorrências por grupo)")
        gt.add_column("grupo")
        gt.add_column("ocorrências", justify="right")
        for grupo, total in grupos:
            gt.add_row(grupo.value, str(total))
        console.print(gt)

    console.print(
        "[dim]A verificação automática cobre parte dos critérios A/AA. "
        "Ausência de achado não equivale a conformidade.[/]"
    )


# ---------------------------------------------------------------------------
# Pós-processamento
# ---------------------------------------------------------------------------


@app.command("relatorio")
def report(
    arquivo: Annotated[Path, typer.Argument(help="JSON de varredura em data/scans/.")],
    saida: Annotated[Path | None, typer.Option(help="Diretório de destino.")] = None,
) -> None:
    """Gera o relatório HTML a partir de um JSON de varredura já coletado."""
    settings = get_settings()
    if not arquivo.is_file():
        console.print(f"[red]Arquivo não encontrado:[/] {arquivo}")
        raise typer.Exit(code=1)

    scan = ScanResult.model_validate_json(arquivo.read_text(encoding="utf-8"))
    path = write_report(scan, saida or settings.exports_dir, params=settings.scoring_parameters())
    console.print(f"[green]Relatório gerado:[/] {path}")


@app.command("exportar")
def export(
    diretorio: Annotated[
        Path | None, typer.Option(help="Diretório com os JSON. Padrão: data/scans/.")
    ] = None,
    saida: Annotated[Path | None, typer.Option(help="Diretório de destino.")] = None,
    separador: Annotated[str, typer.Option(help="Separador do CSV.")] = ";",
) -> None:
    """Exporta todas as varreduras para CSV — o dataset da análise e do artigo."""
    settings = get_settings()
    store = JsonScanStore(diretorio or settings.scans_dir)
    files = store.list_files()
    if not files:
        console.print("[yellow]Nenhuma varredura encontrada.[/]")
        raise typer.Exit(code=1)

    scans = [store.load(f) for f in files]
    out = saida or settings.exports_dir
    findings_path = export_findings_csv(scans, out / "achados.csv", delimiter=separador)
    pages_path = export_pages_csv(
        scans, out / "paginas.csv", delimiter=separador, params=settings.scoring_parameters()
    )

    console.print(f"[green]Varreduras processadas:[/] {len(scans)}")
    console.print(f"[green]Achados:[/] {findings_path}")
    console.print(f"[green]Páginas:[/] {pages_path}")


@app.command("reindexar")
def reindex(
    diretorio: Annotated[
        Path | None, typer.Option(help="Diretório com os JSON. Padrão: data/scans/.")
    ] = None,
) -> None:
    """Reconstrói o índice relacional a partir dos JSON já coletados.

    Torna operacional a promessa da ADR 0003: o documento JSON é a fonte da
    verdade e o banco é índice derivável. Quando o cálculo de um índice muda —
    ou quando uma coluna nova aparece, como ``observed`` na ADR 0010 — as
    varreduras já coletadas se atualizam sem que nenhum portal seja varrido de
    novo. É a diferença entre corrigir um erro de método e refazer o campo.

    Reindexar é idempotente e substitui integralmente cada linha de mesmo ``id``.
    """
    settings = get_settings()
    settings.ensure_directories()

    store = JsonScanStore(diretorio or settings.scans_dir)
    files = store.list_files()
    if not files:
        console.print("[yellow]Nenhuma varredura encontrada.[/]")
        raise typer.Exit(code=1)

    engine = create_database_engine(settings.resolved_database_url())
    init_database(engine)
    factory = make_session_factory(engine)

    catalogo = {alvo.id: alvo for alvo in load_catalog(settings.catalog_path).targets}
    reindexadas = 0
    sem_veredito = 0
    falhas: list[tuple[Path, str]] = []

    with session_scope(factory) as session:
        repo = ScanRepository(session, params=settings.scoring_parameters())
        for arquivo in files:
            try:
                scan = store.load(arquivo)
            # Um arquivo ilegível é sinal de dataset de versão anterior; ele
            # é reportado ao final, mas não interrompe o lote — reindexar
            # parcialmente é melhor do que não reindexar.
            except Exception as exc:
                falhas.append((arquivo, str(exc)))
                continue

            alvo = catalogo.get(scan.target_id)
            repo.save(scan, json_path=arquivo, sphere=alvo.sphere if alvo else None)
            reindexadas += 1
            if not scan.successful_pages:
                sem_veredito += 1

    console.print(f"[green]Varreduras reindexadas:[/] {reindexadas}")
    if sem_veredito:
        # Contagem explícita: são exatamente as varreduras que, sob o contrato
        # anterior, apareciam como conformidade perfeita.
        console.print(f"[yellow]Sem veredito (nenhuma página auditada):[/] {sem_veredito}")
    for arquivo, erro in falhas:
        console.print(f"[red]Ilegível:[/] {arquivo.name} — {erro}")
    if falhas:
        raise typer.Exit(code=1)


@app.command("servir")
def serve(
    host: Annotated[str | None, typer.Option(help="Interface de escuta.")] = None,
    port: Annotated[int | None, typer.Option(help="Porta.")] = None,
    reload: Annotated[bool, typer.Option(help="Recarga automática (desenvolvimento).")] = False,
) -> None:
    """Sobe a API que serve o dashboard."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "acessisaude_audit.api.app:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=reload,
    )


if __name__ == "__main__":  # pragma: no cover
    app()
