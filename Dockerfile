# =============================================================================
# AcessiSaúde-Audit — imagem única para coleta agendada e para a API
# =============================================================================
# Uma imagem, dois usos, porque a auditoria e o painel precisam da MESMA versão
# do motor e do axe-core vendorizado. Imagens separadas abririam a possibilidade
# de o painel exibir números produzidos por uma versão que ele não conhece — e a
# procedência é requisito do projeto, não detalhe de implantação.
#
#   Coleta:  CMD padrão (scripts/coleta-continua.sh)
#   API:     sobrescreva com  acessisaude servir --host 0.0.0.0 --port $PORT
# =============================================================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    ACESSISAUDE_DATA_DIR=/app/data \
    TZ=America/Sao_Paulo

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates tzdata \
 && rm -rf /var/lib/apt/lists/*

# Dependências antes do código: a camada só é reconstruída quando o pyproject
# muda, e não a cada ajuste de uma sonda.
COPY backend/pyproject.toml backend/README.md ./backend/
COPY backend/src ./backend/src
# O axe-core vendorizado é resolvido em backend/vendor/ — é o que garante que
# duas execuções separadas por semanas apliquem exatamente as mesmas regras.
COPY backend/vendor ./backend/vendor

RUN pip install --upgrade pip \
 && pip install -e "./backend[analysis]" \
 # Driver PostgreSQL: necessário apenas quando ACESSISAUDE_DATABASE_URL aponta
 # para Postgres (implantação sem disco persistente, como o cron do Render).
 # Instalado sempre porque é pequeno e evita duas variantes de imagem.
 && pip install "psycopg[binary]>=3.2"

# --with-deps instala as bibliotecas de sistema do Chromium. Precisa vir depois
# do pip install, que traz o próprio playwright.
RUN playwright install --with-deps chromium

COPY scripts ./scripts
COPY fixtures ./fixtures

RUN chmod +x scripts/coleta-continua.sh && mkdir -p /app/data

CMD ["scripts/coleta-continua.sh"]
