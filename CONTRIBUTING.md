# Como contribuir

---

## Antes de tudo: o que este projeto protege

É um instrumento de medição que sustenta afirmações publicáveis. Três invariantes valem mais
que qualquer funcionalidade nova, e cada uma é verificada por teste:

1. **Violação e indício não se confundem.** Sondas heurísticas não podem reprovar.
2. **A cobertura é declarada.** Ausência de achado nunca vira conformidade.
3. **Nenhum número circula sem seus parâmetros.**

Uma contribuição que quebre qualquer uma delas será recusada, ainda que o teste correspondente
passe por acaso.

---

## Preparar o ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e "backend[analysis,dev]"
playwright install chromium

cd frontend && npm install && cd ..
```

---

## Antes de abrir um pull request

```powershell
# Backend
ruff check backend\src backend\tests
ruff format --check backend\src backend\tests
mypy backend\src
pytest backend\tests\unit
pytest backend\tests\integration      # exige Chromium

# Frontend
cd frontend
npm run typecheck
npm run test:a11y
```

---

## Regras que a suíte impõe

### Arquitetura

`tests/unit/test_arquitetura.py` verifica, por análise estática:

- **direção das dependências** — sempre para dentro, em direção a `domain`;
- **pureza do domínio** — sem Playwright, SQLAlchemy, FastAPI, pandas ou YAML;
- **domínio sem I/O de arquivo**;
- **docstring em todo módulo** e em toda definição pública de nível de módulo.

### Sondas

`tests/unit/test_contrato_sondas.py` verifica:

- `id` prefixado por `probe.`;
- descrição substantiva (> 30 caracteres);
- critérios declarados existentes no escopo A/AA;
- **sondas `HEURISTIC` não produzem `FAIL`** — a classe base rebaixa automaticamente.

### Matriz jurídica

`tests/unit/test_dominio_normativo.py` verifica:

- todo critério do escopo tem mapeamento (**completude**);
- toda chave de dispositivo existe;
- toda tese jurídica tem ≥ 80 caracteres;
- toda conduta corretiva tem ≥ 30 caracteres.

Os dois últimos protegem a **qualidade**, e não apenas a existência: a tese vai literalmente
para o relatório entregue ao gestor e para o artigo.

---

## Como fazer cada tipo de mudança

### Acrescentar uma sonda

1. Escolher o módulo por classe de barreira (`viewport`, `keyboard`, `structure`, `forms`,
   `media`, `digital_rights`).
2. Herdar de `Probe`; declarar `id`, `criteria`, `confidence`, `description`.
3. **Documentar qual lacuna ela cobre** — se o axe já cobre, a sonda não deve existir, porque
   duplicaria o achado e inflaria a contagem.
4. Registrar em `ALL_PROBES`.
5. Acrescentar a barreira correspondente a uma fixture e declarar no manifesto.
6. Rodar a integração: o golden set precisa continuar sem falso positivo.
7. **Reaferir κ** se o conjunto de achados mudar — ver
   [índices](docs/metodologia/indices.md#calibracao).

### Alterar a matriz jurídica

1. Editar `CRITERION_MAPPINGS`, com a tese revisada.
2. Registrar em `docs/adr/`, com a justificativa doutrinária.
3. Reindexar as varreduras existentes (`ScanRepository.reindex`) — o JSON permanece intacto.

### Atualizar o axe-core

Não é atualização de dependência, é **mudança metodológica**. Procedimento obrigatório em
[`backend/vendor/README.md`](backend/vendor/README.md): ADR, reexecução do golden set,
possível reaferição de κ, nota de descontinuidade se a coleta atravessar duas versões.

### Alterar índices ou parâmetros

1. ADR obrigatória.
2. Atualizar `docs/metodologia/indices.md` com a **tabela empírica**, não com estimativa.
3. Atualizar `TestCalibracaoDoAtrito`.
4. Declarar descontinuidade em qualquer série temporal afetada.

### Alterar o esquema de dados

1. Incrementar `SCHEMA_VERSION`.
2. ADR obrigatória.
3. Documentar em `docs/api/dicionario-de-dados.md`.

---

## Estilo

**Python** — Ruff (linha de 100), tipagem completa (mypy `strict`), docstrings no estilo
Google, em **português**.

**TypeScript** — modo estrito, `noUncheckedIndexedAccess`, sem `any`.

**Comentários** explicam **por quê**, não o quê. O código já diz o quê.

```python
# Bom
# 'networkidle' é intencionalmente tolerante a falha: portais com polling
# permanente nunca ficam ociosos, e esperar até o timeout apenas desperdiça
# tempo sem melhorar a medição.

# Ruim
# Espera o carregamento da rede.
```

### Documente as armadilhas onde elas moram

Quando um defeito custar tempo para ser diagnosticado, a explicação fica **no código**, no
ponto exato. Exemplos já no repositório:

- `NetworkRecorder` sem `slots=True`, porque o Playwright grava um atributo no handler;
- `logger.error(exc_info=...)` em vez de `logger.exception`, porque não há exceção ativa após
  `gather`;
- `TituloDePagina` que só move o foco em troca de rota, não na carga inicial.

Um documento separado não seria consultado no momento certo.

---

## Commits

Formato convencional, em português:

```
feat(sondas): detecta placeholder como único rótulo de campo
fix(motor): registra traceback de falha capturada por gather
docs(adr): registra recalibração empírica de kappa
test(golden): cobre distinção entre peso próprio e tráfego de terceiros
```

Escopos: `dominio`, `motor`, `sondas`, `api`, `painel`, `docs`, `adr`, `golden`, `analise`.

---

## Contato

Thalles Costa — thalles.costa@ioc.fiocruz.br
