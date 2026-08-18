#!/usr/bin/env bash
# =============================================================================
# Coleta contínua — um ponto da série temporal
# =============================================================================
# Executa, nesta ordem:
#
#   1. varredura do conjunto de validação sintético;
#   2. aferição do instrumento contra essa varredura (portão de qualidade);
#   3. varredura dos alvos habilitados no catálogo;
#   4. exportação do dataset acumulado em CSV.
#
# A ordem não é arbitrária. Se o passo 2 falhar, o script encerra ANTES de tocar
# em qualquer portal público: um instrumento não aferido produz número, não
# resultado — e ainda impõe carga a servidor de terceiro sem contrapartida.
#
# Uso:
#   scripts/coleta-continua.sh                     # todos os alvos habilitados
#   scripts/coleta-continua.sh ses-rj sms-rio      # alvos específicos
#
# Variáveis de ambiente:
#   ACESSISAUDE_USER_AGENT_SUFFIX  OBRIGATÓRIA. Identificação da pesquisa e
#                                  contato, anexada ao User-Agent. Sem ela o
#                                  script recusa executar — ver a conduta de
#                                  coleta em docs/metodologia/.
#   ACESSISAUDE_DATA_DIR           Destino dos artefatos. Padrão: ./data
#   ACESSISAUDE_REQUEST_DELAY_MS   Intervalo entre requisições. Padrão: 2000
#   COLETA_RELATORIO               "1" para gerar o HTML por varredura. Padrão:
#                                  desligado — em coleta agendada o HTML cresce
#                                  sem ser lido; o JSON é a fonte da verdade.
# =============================================================================
set -euo pipefail

if [ -z "${ACESSISAUDE_USER_AGENT_SUFFIX:-}" ]; then
  cat >&2 <<'FIM'
[coleta] ACESSISAUDE_USER_AGENT_SUFFIX não definida.

A conduta de coleta do projeto exige identificação da pesquisa no User-Agent.
Não é formalidade: um portal público precisa poder saber quem o está acessando
e a quem reclamar. Defina, por exemplo:

  ACESSISAUDE_USER_AGENT_SUFFIX="AcessiSaude-Audit/pesquisa (+contato@instituicao.br)"
FIM
  exit 2
fi

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

RELATORIO_FLAG="--sem-relatorio"
if [ "${COLETA_RELATORIO:-0}" = "1" ]; then
  RELATORIO_FLAG="--relatorio"
fi

# -----------------------------------------------------------------------------
# 1. Conjunto de validação
# -----------------------------------------------------------------------------
echo "[coleta] Subindo o servidor do conjunto de validação…"
python scripts/servidor_fixtures.py --porta 8080 >/tmp/fixtures.log 2>&1 &
FIXTURES_PID=$!
trap 'kill "$FIXTURES_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  if python -c "
import socket,sys
s=socket.socket()
s.settimeout(0.5)
sys.exit(0 if s.connect_ex(('127.0.0.1',8080))==0 else 1)
" 2>/dev/null; then
    break
  fi
  sleep 0.5
done

echo "[coleta] Varrendo o conjunto de validação…"
acessisaude varrer fixtures-local --sem-relatorio

# -----------------------------------------------------------------------------
# 2. Portão de aferição
# -----------------------------------------------------------------------------
echo "[coleta] Aferindo o instrumento…"
python scripts/aferir_instrumento.py --scans-dir "${ACESSISAUDE_DATA_DIR:-data}/scans"

kill "$FIXTURES_PID" 2>/dev/null || true
trap - EXIT

# -----------------------------------------------------------------------------
# 3. Alvos de produção
# -----------------------------------------------------------------------------
if [ "$#" -gt 0 ]; then
  ALVOS="$*"
else
  ALVOS="$(python - <<'PY'
from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import get_settings

catalogo = load_catalog(get_settings().catalog_path)
# fixtures-local já foi varrido no passo 1 e depende do servidor local.
print(" ".join(t.id for t in catalogo.targets if t.enabled and t.id != "fixtures-local"))
PY
)"
fi

if [ -z "${ALVOS// /}" ]; then
  echo "[coleta] Nenhum alvo habilitado no catálogo. Nada a fazer." >&2
  exit 0
fi

echo "[coleta] Alvos: $ALVOS"

FALHAS=0
for alvo in $ALVOS; do
  echo "[coleta] --- $alvo ---"
  # Um alvo indisponível não interrompe a série: a perda é dado, e o motor já a
  # reporta como taxa de perda. Interromper produziria lacuna silenciosa.
  if ! acessisaude varrer "$alvo" $RELATORIO_FLAG; then
    echo "[coleta] Falha ao varrer $alvo — prosseguindo." >&2
    FALHAS=$((FALHAS + 1))
  fi
done

# -----------------------------------------------------------------------------
# 4. Dataset acumulado
# -----------------------------------------------------------------------------
echo "[coleta] Exportando o dataset acumulado…"
acessisaude exportar

echo "[coleta] Concluído. Alvos com falha de execução: $FALHAS"
