# Desenho amostral

> Materializado em
> [`catalog/targets.yaml`](../../backend/src/acessisaude_audit/catalog/targets.yaml).
> O catálogo **não é arquivo de configuração**: é o desenho amostral do estudo, versionado e
> validado.

---

## Estratégia

**Amostragem intencional, estratificada por esfera federativa e por natureza do serviço.**

Amostragem probabilística seria inadequada: a população de plataformas digitais de saúde
pública com incidência no Rio de Janeiro é pequena, conhecida e heterogênea. O interesse é
**comparar estratos de gestão**, não estimar parâmetro populacional.

A consequência precisa ser declarada no artigo: **os resultados não são generalizáveis** para
o universo de portais públicos brasileiros.

---

## Estratificação

### Por esfera federativa

Testa a hipótese H1 — gradiente de conformidade entre níveis de gestão. A hipótese é
**testada, não presumida**: supor que o município tem menor capacidade técnica é exatamente o
tipo de presunção que um estudo empírico deve verificar.

A esfera também determina o órgão de controle competente (TCU para federal, TCE para
estadual e municipal), o que torna o achado operacionalmente útil.

### Por natureza do serviço

| Categoria | Exemplos | Hipótese |
|---|---|---|
| Informacional | Página de campanha, calendário de vacinação | Menor atrito |
| Transacional | Agendamento, cadastro, ouvidoria | Maior atrito (H2) |
| Prontuário / resultado | Meu SUS Digital | Maior risco jurídico; majoritariamente autenticado |

A hipótese H2 tem fundamento: interfaces transacionais têm mais controles interativos, e é aí
que se concentram as barreiras sem rota alternativa (teclado, nome/função/valor).

---

## Sementes explícitas, não descoberta automática

Cada página auditada é declarada no catálogo, com rótulo do passo no fluxo do usuário e
marcação de fluxo essencial.

Descoberta automática (`--descobrir`) existe, mas está **desligada por padrão**. Ela produz
amostra não reproduzível: o conjunto de links muda a cada publicação de conteúdo, e duas
execuções do mesmo comando em semanas diferentes auditariam páginas diferentes — o que
inviabilizaria a série temporal que a proposta de auditoria **contínua** pressupõe.

---

## Justificativa de inclusão obrigatória

Todo alvo declara `selection_rationale`. O campo é verificado em teste automatizado
(mínimo de 60 caracteres), o que impede que o desenho amostral seja construído por
conveniência e justificado depois.

Exemplo:

```yaml
- id: sms-rio
  selection_rationale: >-
    Porta de entrada da atenção primária na capital, onde se concentra a
    população periférica que constitui o objeto central do estudo. É também
    o nível de gestão com menor capacidade técnica instalada, hipótese a ser
    testada e não presumida.
```

---

## Lacunas declaradas

Páginas que exigem autenticação são marcadas `requires_auth: true`, **excluídas da varredura**
e reportadas como lacunas — no relatório HTML, na API e no painel, sempre com a advertência de
que os índices podem estar otimistas.

A distinção entre "não auditado" e "sem achados" é o ponto mais sensível do desenho. As telas
autenticadas concentram o núcleo do fluxo assistencial: resultado de exame, carteira de
vacinação, agendamento confirmado. Omitir a lacuna enviesaria a conclusão para melhor.

---

## Teto de páginas

25 por plataforma. Duas razões, ambas relevantes:

- **Ética:** limita a carga imposta a servidores de saúde pública em produção.
- **Metodológica:** mantém a amostra comparável. Sem teto, um portal com 4 000 páginas
  dominaria qualquer agregação, e o "gradiente entre esferas" mediria tamanho de portal, não
  qualidade de implementação.

---

## Janela temporal

O campo `collection_window` é obrigatório antes da coleta. Portais mudam; sem a janela, o dado
não é interpretável e a comparação entre plataformas coletadas em momentos distintos fica
comprometida.

Recomendação: coletar todas as plataformas na menor janela possível, preferencialmente na
mesma semana, e declarar a data de cada varredura individualmente (o campo `started_at` já o
faz por varredura).

---

## Alvos de produção nascem desabilitados

Todo alvo real tem `enabled: false`. A CLI recusa a varredura e a API responde 409, ambas com
a explicação do que habilitar significa. Habilitar é decisão consciente, registrada em commit.

O único alvo habilitado por padrão é `fixtures-local`, o conjunto de validação sintético.

---

## Composição atual do catálogo

| Alvo | Esfera | Serviços | Páginas | Lacunas |
|---|---|---|---|---|
| `fixtures-local` | — | validação | 5 | 0 |
| `conecte-sus-web` | federal | prontuário, resultado, cadastro | 1 | **1** |
| `gov-br-saude` | federal | informacional, transparência | 3 | 0 |
| `ses-rj` | estadual | informacional, ouvidoria | 2 | 0 |
| `sms-rio` | municipal | informacional, agendamento | 2 | 0 |
| `subpav-rio` | municipal | informacional, agendamento | 2 | 0 |

⚠️ **As URLs devem ser conferidas manualmente antes de qualquer coleta.** Endereços de portais
públicos mudam com frequência, e uma URL desatualizada produz erro de navegação — não um
achado de acessibilidade.

O catálogo está deliberadamente enxuto: ampliá-lo é trabalho de campo, e cada alvo novo exige
justificativa de inclusão, conferência de URL e leitura do `robots.txt`.
