# ADR 0003 — JSON como fonte da verdade, SQL como índice

**Estado:** aceita

---

## Contexto

Os resultados precisam ser (a) consultáveis com agilidade pelo painel e pelas análises, e
(b) preservados integralmente como dado primário de pesquisa.

Normalizar dados de pesquisa cedo demais é um erro clássico: descobre-se, na fase de análise,
que um campo descartado na modelagem era essencial — e não há como recuperá-lo sem recoletar.

---

## Decisão

**Duplicação deliberada, com direção da verdade explícita.**

| Artefato | Papel |
|---|---|
| JSON em `data/scans/` e na coluna `scans.document` | **Fonte da verdade.** `ScanResult` completo, com evidência, medições e `config_snapshot` |
| Tabelas `scans` e `findings` | Índice achatado para consulta e agregação |

Em qualquer divergência, o JSON prevalece. `ScanRepository.reindex(scan_id)` reconstrói o
índice inteiramente a partir do documento.

O JSON é gravado com indentação de 2 espaços — legível e diffável, porque acompanha o artigo
como material suplementar.

---

## Consequências

**Positivas**

- Mudar o cálculo de um índice, ou a interpretação jurídica de um critério, **não exige
  revarrer portal algum**: basta reindexar.
- Um revisor recebe `data/scans/*.json` e `data/acessisaude.sqlite` e reexecuta todas as
  consultas sem provisionar servidor.
- Nenhuma informação se perde na modelagem relacional.

**Negativas assumidas**

- Redundância de armazenamento (o documento existe duas vezes). Irrelevante na escala do
  estudo: uma varredura de 10 páginas ocupa cerca de 240 KB.
- O índice pode ficar defasado se alguém editar o JSON manualmente. Mitigado por `reindex()`
  e pela imutabilidade das varreduras.

---

## Alternativas descartadas

**Só SQL, normalizado.** Perderia a evidência bruta e os campos não modelados. Qualquer
pergunta nova exigiria recoleta.

**Só JSON.** Agregações do painel exigiriam ler todos os arquivos a cada requisição.

**Banco de documentos (MongoDB).** Acrescentaria infraestrutura que ninguém precisa manter e
dificultaria a reprodução do estudo por terceiros — SQLite é um arquivo que se envia por
e-mail.

---

## Nota sobre migração de esquema

`SCHEMA_VERSION` em `domain/models.py` é incrementada em toda mudança incompatível, com
entrada em `docs/adr/`. A leitura de um JSON antigo **falha explicitamente** em vez de tolerar
divergências: um dataset de versão anterior exige migração declarada, não leitura permissiva
que produziria dados silenciosamente errados.
