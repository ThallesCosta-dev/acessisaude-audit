# Referência da API

> Especificação viva: `http://127.0.0.1:8000/docs` (Swagger UI) e `/openapi.json`.
> O OpenAPI é a fonte de tipos do painel React.

Base: `http://127.0.0.1:8000` · Todas as respostas em JSON, salvo indicação.

---

## Operação

### `GET /saude`

Estado do serviço e das dependências que a coleta exige.

```json
{
  "status": "ok",
  "versao": "0.1.0",
  "axe_core_disponivel": true,
  "axe_core_erro": null,
  "navegador": "chromium",
  "respeita_robots_txt": true
}
```

`status` é `degradado` quando `axe_core_disponivel` é falso. A distinção importa: sem o motor
de regras, a API sobe normalmente e toda varredura produziria resultado vazio — falha
silenciosa que este endpoint torna visível.

---

## Referência normativa

Não dependem de varredura alguma. Existem para que o painel explique um achado sem duplicar,
em TypeScript, a matriz jurídica modelada em Python — e para tornar a contribuição do projeto
inspecionável como dado, não apenas como texto de artigo.

### `GET /referencia/criterios`

Os 50 critérios WCAG 2.1 A/AA com vínculo jurídico.

**Parâmetros:** `nivel` (`A` \| `AA`), `apenas_automatizaveis` (bool).

```json
{
  "id": "1.4.3",
  "title_pt": "Contraste (mínimo)",
  "level": "AA",
  "principle": "perceptivel",
  "rationale": "Contraste abaixo de 4.5:1 inviabiliza a leitura sob luz solar…",
  "automatable": true,
  "affects": ["baixa_visao", "cognitiva_neurodivergencia", "visao_de_cores"],
  "legal_risk": "alto",
  "legal_thesis": "O contraste insuficiente é a barreira de comunicação mais prevalente…",
  "remediation": "Ajustar a paleta para razão mínima de 4.5:1…",
  "provisions": ["lbi.art63.caput", "lbi.art3.iv.d", "..."]
}
```

### `GET /referencia/criterios/{id}` · `GET /referencia/dispositivos` · `GET /referencia/dispositivos/{chave}`

Detalhe de critério; lista e detalhe dos 22 dispositivos normativos, com citação ABNT, sujeito
obrigado e vias de exigibilidade.

### `GET /referencia/integridade-da-matriz`

```json
{
  "criterios_no_escopo": 50,
  "criterios_sem_mapeamento": [],
  "matriz_completa": true,
  "dispositivos_registrados": 22
}
```

Exposto como rota — e não apenas como teste — porque a completude é uma afirmação do artigo.
Um revisor pode conferi-la sem ler código.

---

## Alvos

### `GET /alvos`

**Parâmetros:** `esfera`, `apenas_habilitados` (bool).

Retorna, entre outros campos, `selection_rationale` (por que o alvo integra a amostra),
`auditable_pages` e `declared_gaps`.

### `GET /alvos/{id}` · `GET /alvos/{id}/paginas`

O segundo separa `auditaveis` de `lacunas_declaradas`. A separação é substantiva: as lacunas
correspondem a áreas autenticadas que a ferramenta se recusa a varrer, e exibi-las evita que
o painel sugira cobertura integral de um serviço cuja parte mais crítica não foi examinada.

---

## Varreduras

### `POST /varreduras` → `202 Accepted`

```json
{ "target_id": "fixtures-local", "discover": false, "viewports": ["mobile-320"] }
```

Resposta: `{ "job_id": "...", "status": "pendente", "alvo": "fixtures-local" }`.

Retorna 202 porque a varredura leva de segundos a minutos por página: manter a requisição
aberta produziria timeout no cliente e interromperia a coleta ao menor soluço de rede.

**`409 Conflict`** se o alvo estiver desabilitado, com a explicação do que habilitar significa.

### `GET /varreduras/trabalhos/{job_id}`

```json
{
  "status": "executando",
  "concluidas": 4, "total": 10,
  "url_corrente": "http://…/agendamento",
  "scan_id": null, "erro": null
}
```

O registro de execuções é mantido **em memória** e se perde ao reiniciar o servidor —
limitação deliberada, documentada no código: uma varredura é operação de pesquisa iniciada
manualmente por quem acompanha o resultado, e introduzir fila durável adicionaria
infraestrutura que dificultaria a reprodução do estudo por terceiros. Varreduras concluídas
estão em disco e no banco.

### `GET /varreduras` · `GET /varreduras/{id}`

Lista paginada de resumos; documento completo da varredura (o artefato primário de pesquisa).

### `GET /varreduras/{id}/indices`

```json
{
  "indices": { "conformance_index": 30.82, "friction_index": 96.64, "...": "..." },
  "grupos_excluidos": [ { "grupo": "cognitiva_neurodivergencia", "ocorrencias": 107 } ],
  "parametros": { "friction_kappa": 150.0, "price_per_mb_brl": 0.1, "...": "..." },
  "taxa_de_perda": 0.0,
  "lacunas_declaradas": []
}
```

`parametros` acompanha sempre os índices: **nenhum número deste projeto circula dissociado das
constantes que o produziram.**

### `GET /varreduras/{id}/relatorio` → `text/html`

Relatório completo, autocontido, sem JavaScript, conforme WCAG 2.1 AA. Pode ser arquivado
como evidência estável ou anexado a um processo.

### `GET /varreduras/{id}/achados.csv` → `text/csv`

Formato longo, UTF-8 com BOM, separador `;`. Ver
[dicionário de dados](dicionario-de-dados.md).

### `GET /varreduras/agregados/criterios`

Frequência de critérios violados em todas as varreduras — a consulta que alimenta a figura
principal do artigo.

### `DELETE /varreduras/{id}` → `204`

Remove do índice relacional. **O arquivo JSON não é removido**: é o registro primário da
pesquisa, e sua exclusão precisa ser ato deliberado no sistema de arquivos, nunca efeito
colateral de uma chamada de API.

---

## Convenções

**Erros** seguem o padrão do FastAPI: `{"detail": "mensagem em português"}`, com 404 para
recurso inexistente, 409 para conflito de estado (alvo desabilitado) e 400 para parâmetro
inválido.

**CORS** restrito a `localhost:5173` e `127.0.0.1:5173` por padrão, configurável em
`ACESSISAUDE_CORS_ORIGINS`.

**Autenticação:** não há. A API é de uso local, em ambiente de pesquisa. Expô-la em rede
pública exigiria autenticação e limitação de taxa — a rota `POST /varreduras` inicia tráfego
contra terceiros, e um endpoint aberto seria abusável como amplificador.
