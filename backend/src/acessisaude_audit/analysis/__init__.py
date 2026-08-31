"""Camada de análise: do dado coletado aos resultados do artigo.

Exige o extra ``analysis`` (pandas, numpy, scipy, matplotlib). A ferramenta de
coleta funciona sem ele — separação deliberada, para que rodar auditorias não
imponha a pilha científica a quem só quer o relatório.

Fluxo típico::

    from pathlib import Path
    from acessisaude_audit.analysis import (
        build_findings_frame, build_pages_frame, build_scans_frame,
        criterion_prevalence, load_scans, save_all,
    )
    from acessisaude_audit.catalog.loader import load_catalog
    from acessisaude_audit.config import get_settings

    s = get_settings()
    scans = load_scans(s.scans_dir)
    catalogo = load_catalog(s.catalog_path)

    achados = build_findings_frame(scans, catalog=catalogo)
    paginas = build_pages_frame(scans, catalog=catalogo)
    varreduras = build_scans_frame(scans, catalog=catalogo)

    print(criterion_prevalence(achados).head(15))
    save_all(achados, paginas, Path("docs/artigo/figuras"), scans=varreduras)
"""

from acessisaude_audit.analysis.dataset import (
    build_findings_frame,
    build_pages_frame,
    build_scans_frame,
    criterion_prevalence,
    exclusion_profile,
    load_scans,
)
from acessisaude_audit.analysis.figures import (
    apply_style,
    figure_criterion_prevalence,
    figure_daily_series,
    figure_data_cost,
    figure_exclusion_profile,
    figure_index_by_sphere,
    save_all,
)
from acessisaude_audit.analysis.statistics import (
    TestResult,
    bootstrap_ci,
    cliffs_delta,
    compare_groups,
    describe,
)

__all__ = [
    "TestResult",
    "apply_style",
    "bootstrap_ci",
    "build_findings_frame",
    "build_pages_frame",
    "build_scans_frame",
    "cliffs_delta",
    "compare_groups",
    "criterion_prevalence",
    "describe",
    "exclusion_profile",
    "figure_criterion_prevalence",
    "figure_daily_series",
    "figure_data_cost",
    "figure_exclusion_profile",
    "figure_index_by_sphere",
    "load_scans",
    "save_all",
]
