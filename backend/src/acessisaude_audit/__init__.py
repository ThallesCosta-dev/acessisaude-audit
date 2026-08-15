"""AcessiSaúde-Audit — auditoria contínua de acessibilidade em saúde pública.

Ferramenta computacional que audita plataformas digitais de saúde pública
brasileiras contra a WCAG 2.1 (níveis A e AA) e converte cada falha técnica em
uma proposição jurídica fundamentada na Lei Brasileira de Inclusão (Lei
13.146/2015) e no arcabouço normativo correlato.

Camadas (ver ``docs/arquitetura/visao-geral.md``)::

    domain/       normas, direito, modelos, índices        [puro, sem I/O]
    catalog/      desenho amostral em YAML
    auditor/      navegador, axe-core, sondas, conduta      → produz ScanResult
    persistence/  SQLite + repositórios                     → guarda ScanResult
    reporting/    HTML, CSV, JSON                           → publica ScanResult
    analysis/     pandas, estatística, figuras do artigo    → analisa ScanResult
    api/          FastAPI, consumida pelo dashboard React

A direção das dependências é sempre para dentro, em direção a ``domain``.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
