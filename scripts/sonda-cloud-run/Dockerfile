# Sonda de vantagem em posicao brasileira — imagem minima.
#
# Deliberadamente SEM navegador. Esta imagem nao audita: mede se o endereco
# responde. Sem Chromium, sao ~60 MB em vez de ~1,5 GB, o job sobe em segundos
# e o custo por execucao fica em fracao de centavo.
#
# Construir a partir da RAIZ do repositorio:
#   docker build -f scripts/sonda-cloud-run/Dockerfile -t sonda .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CATALOGO=/app/targets.yaml

WORKDIR /app

RUN pip install --no-cache-dir "httpx>=0.27" "pyyaml>=6.0"

# O catalogo e copiado, e nao duplicado em codigo: se as sementes mudarem, a
# sonda muda junto na proxima construcao. E a fragilidade que a sonda do Apps
# Script tem por nao conseguir ler o repositorio.
COPY backend/src/acessisaude_audit/catalog/targets.yaml /app/targets.yaml
COPY scripts/sonda-cloud-run/sonda.py /app/sonda.py

CMD ["python", "/app/sonda.py"]
