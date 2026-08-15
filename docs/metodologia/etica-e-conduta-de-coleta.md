# Ética e conduta de coleta

> Regras implementadas em código, não apenas declaradas aqui.
> Ver [`auditor/crawler.py`](../../backend/src/acessisaude_audit/auditor/crawler.py) e
> [`config.py`](../../backend/src/acessisaude_audit/config.py).

---

## Premissa

Auditar infraestrutura pública em produção impõe deveres que uma ferramenta de teste interno
não tem. O objeto do estudo é um serviço de saúde em funcionamento: degradar seu desempenho
para medir sua acessibilidade seria autocontraditório, e coletar dados de área autenticada
sem autorização seria inadmissível em pesquisa.

As regras abaixo estão concentradas em um único módulo e validadas na configuração, para que
sejam auditáveis — e não espalhadas por condicionais no motor, onde ninguém as encontraria.

---

## 1. A ferramenta não interage

A ferramenta **lê o DOM renderizado de páginas públicas**. Nada além disso.

Ela **nunca**:

- preenche formulário;
- submete dado de qualquer natureza;
- autentica, nem tenta credenciais;
- explora vulnerabilidade;
- contorna proteção contra automação;
- coleta dado pessoal de terceiros.

O único ato de interação executado é a **pressão da tecla Tab**, usada pela sonda de foco
visível. Ela não dispara ação alguma: percorre a ordem de tabulação e lê o estilo computado
do elemento focado. É necessária porque navegadores só aplicam `:focus-visible` quando a
modalidade de entrada corrente é o teclado — um `element.focus()` programático produziria
falsos positivos em massa.

---

## 2. Áreas autenticadas não são auditadas

Páginas que exigem credenciais são declaradas no catálogo com `requires_auth: true`,
**excluídas da varredura** e reportadas como **lacunas declaradas da amostra**.

```yaml
- url: "https://meususdigital.saude.gov.br/login"
  label: "Autenticação gov.br"
  requires_auth: true
  notes: >-
    Excluída da varredura. A área autenticada concentra as telas de maior
    risco (resultado de exame, carteira de vacinação) e sua ausência é uma
    limitação declarada do estudo — não uma omissão.
```

A distinção importa: a lacuna aparece no relatório HTML, na API (`/alvos/{id}/paginas`) e no
painel, sempre com a advertência de que **os índices podem estar otimistas**, porque as telas
mais críticas do fluxo assistencial ficaram de fora.

Omitir essa informação enviesaria a conclusão para melhor — e seria a forma mais fácil de
produzir um resultado favorável sem mentir explicitamente.

---

## 3. `robots.txt` é respeitado

Não por obrigação legal — o arquivo não é norma jurídica — mas porque ignorá-lo em pesquisa
acadêmica sobre serviço público é conduta indefensável perante um comitê de ética.

Desativar a checagem **exige justificativa registrada**, validada na configuração:

```python
@field_validator("robots_override_reason")
def _require_reason_when_ignoring_robots(cls, v, info):
    if not info.data.get("respect_robots_txt", True) and not v.strip():
        raise ValueError(
            "respect_robots_txt=False exige ACESSISAUDE_ROBOTS_OVERRIDE_REASON "
            "com a justificativa da coleta (será registrada no dataset)."
        )
```

A justificativa viaja no `config_snapshot` da varredura. Quem ler o dataset saberá que a
checagem foi desativada e por quê.

**Política em caso de indisponibilidade:** um `robots.txt` ausente ou com erro 5xx é tratado
como **permissão**. Ausência não expressa proibição, e tratá-la como negativa impediria
auditar exatamente os portais mais precários — enviesando a amostra na direção contrária ao
objeto do estudo.

---

## 4. Intervalo entre requisições

Padrão: **2000 ms** entre requisições ao mesmo host, com concorrência **1**.

O valor é conservador por escolha, não por limitação técnica. Elevar a concorrência é
admissível contra o conjunto de validação local; contra portais em produção, não.

Quando o host declara `Crawl-delay` maior que o intervalo configurado, **o valor do host
prevalece**: a cortesia declarada pelo administrador tem precedência sobre a nossa.

---

## 5. Identificação no `User-Agent`

Auditar sem se identificar seria conduta de coleta inaceitável em pesquisa. Toda requisição
carrega:

```
AcessiSaudeAudit/0.1 (+pesquisa academica; contato: thalles.costa@ioc.fiocruz.br)
```

O administrador do portal auditado consegue identificar a origem do tráfego e entrar em
contato.

---

## 6. Teto de páginas por alvo

Padrão: **25 páginas**. Duas razões:

- **Ética.** Limita a carga imposta a servidores públicos.
- **Metodológica.** Mantém a amostra comparável entre portais de tamanhos muito diferentes.
  Sem teto, um portal com 4 000 páginas dominaria qualquer agregação.

---

## 7. Descoberta automática de links é desligada por padrão

A opção `--descobrir` existe, mas o padrão é **não usá-la**. Descoberta automática produz
amostra não reproduzível: o conjunto de links muda a cada publicação de conteúdo, e duas
execuções do mesmo comando em semanas diferentes auditariam páginas diferentes.

Sementes explícitas no catálogo tornam a amostra reproduzível e permitem justificar, no
artigo, por que cada página entrou no estudo.

---

## 8. Alvos de produção nascem desabilitados

Toda plataforma real em `targets.yaml` tem `enabled: false`. A CLI recusa a varredura e
explica o que habilitar significa:

```
┌──────────────── Varredura não executada ────────────────┐
│ O alvo conecte-sus-web está desabilitado no catálogo.   │
│                                                          │
│ Alvos de produção nascem desabilitados por conduta de    │
│ coleta. Habilitá-lo significa assumir: respeito ao       │
│ robots.txt, intervalo mínimo entre requisições,          │
│ identificação no User-Agent e ausência de qualquer       │
│ interação com formulários ou autenticação.               │
└──────────────────────────────────────────────────────────┘
```

A API responde `409 Conflict` com a mesma explicação. Habilitar é uma decisão consciente,
registrada em commit, e não um efeito colateral de rodar um comando.

---

## 9. Dados pessoais

A ferramenta não coleta dados pessoais. As capturas de tela e os trechos de HTML retidos como
evidência vêm de **páginas públicas não autenticadas**, e o HTML é truncado em 400 caracteres
por elemento.

Ainda assim, antes de publicar o dataset como material suplementar:

- revisar as capturas em `data/screenshots/` — portais podem exibir dado de exemplo que
  pareça real;
- verificar se algum trecho de HTML retido contém identificador incidental.

---

## 10. Antes de coletar em produção

Lista de verificação:

- [ ] URLs do catálogo conferidas manualmente (endereços de portais públicos mudam).
- [ ] `robots.txt` de cada host lido.
- [ ] Janela de coleta declarada em `collection_window` no catálogo.
- [ ] Preço do MB e franquia de referência substituídos pelos valores reais, com fonte e data.
- [ ] Coleta agendada fora do horário de pico do serviço.
- [ ] Comitê de ética consultado, se o desenho do estudo o exigir na instituição.
- [ ] Justificativa de seleção preenchida para cada alvo (`selection_rationale`).

---

## 11. Divulgação responsável dos achados

Este projeto audita acessibilidade, não segurança — os achados não são vulnerabilidades
exploráveis e não há risco em publicá-los.

Ainda assim, a conduta recomendada antes da publicação do artigo é **comunicar previamente os
órgãos auditados**, encaminhando o relatório HTML de cada plataforma. Duas razões:

1. É o que dá utilidade prática à pesquisa: o relatório traz a conduta corretiva esperada
   para cada achado, em linguagem de ação.
2. Preserva a relação institucional necessária para que o estudo tenha continuidade — a
   proposta é de auditoria **contínua**, não de fotografia única.
