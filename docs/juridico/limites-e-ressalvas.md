# Limites e ressalvas da qualificação jurídica

> Leia antes de usar qualquer relatório deste sistema em contexto que produza efeito jurídico.

---

## 1. O que este sistema não é

**Não é parecer jurídico.** As proposições são geradas por correspondência automática entre
critério técnico e dispositivo normativo, segundo uma matriz documentada. Não há análise do
caso concreto, das circunstâncias do órgão auditado, de eventuais justificativas ou de
jurisprudência aplicável.

**Não é prova pericial.** Perícia exige perito nomeado, submissão ao contraditório e
metodologia validada no processo. Um relatório automatizado pode, no máximo, instruir uma
petição inicial ou uma representação — jamais substituir a prova técnica.

**Não é atestado de conformidade.** A ferramenta produz um piso de não conformidade. Ausência
de achado não equivale a conformidade, e a afirmação aparece em toda saída do sistema.

**Não avalia intenção nem culpa.** Detecta o estado da interface em um instante. Não diz se o
órgão sabia, se tentou corrigir, se dispunha de recursos ou se há causa excludente.

---

## 2. Do que a qualificação depende

A afirmação "há violação do art. 63 da LBI" pressupõe quatro elementos, dos quais a ferramenta
verifica **um e meio**:

| Elemento | Quem verifica |
|---|---|
| O sítio é mantido por órgão de governo ou empresa com sede no país | **Humano** — declarado no catálogo, não verificado |
| Há barreira de acessibilidade | **Ferramenta** |
| A barreira contraria as melhores práticas adotadas internacionalmente | **Ferramenta**, com as limitações de cobertura declaradas |
| Não incide excludente | **Humano** — não avaliado |

A ferramenta é forte no segundo elemento e parcial no terceiro. O primeiro é premissa
declarada; o quarto é inteiramente jurídico.

---

## 3. A gradação de risco é interpretativa

A escala `LegalRisk` combina três vetores — essencialidade do serviço, existência de rota
alternativa, reversibilidade do dano — e **envolve juízo de valor**. Não decorre de norma nem
de jurisprudência consolidada.

Discordâncias legítimas são esperadas, sobretudo quanto a:

- **O que é serviço essencial.** Classificar o agendamento como essencial e a página
  institucional como não essencial é defensável, mas contestável.
- **O que conta como rota alternativa.** O atendimento telefônico ou presencial é rota
  alternativa suficiente para afastar o risco crítico? O projeto entende que **não**, quando
  o canal digital é oferecido como via de acesso — mas é uma posição, não um dado.

Cada mapeamento declara a tese que sustenta sua classificação, e a matriz é consultável pela
API para que a discordância seja possível e informada.

---

## 4. Norma em branco e a indeterminação que ela cria

O art. 63 da LBI remete às "melhores práticas e diretrizes de acessibilidade adotadas
internacionalmente" sem nomeá-las. A remissão é operacionalizada, no Brasil, pelo eMAG 3.1 e
pelo art. 47 do Decreto 5.296/2004 — mas isso é **construção interpretativa**, e não texto
expresso de lei.

Consequências práticas, que o artigo deve discutir:

1. Uma atualização do padrão técnico altera o conteúdo do dever **sem alteração legislativa**.
2. A divergência entre WCAG 2.1 e 2.2 cria zona de indeterminação. O critério 4.1.1, removido
   na 2.2 e mantido no escopo deste projeto, é exemplo concreto: viola-se ou não um dever
   jurídico ao descumprir um critério que a versão mais recente da norma técnica abandonou?
3. Não há regulamentação do selo de acessibilidade digital previsto no art. 63, § 1º, o que
   priva o sistema de um mecanismo oficial de aferição.

---

## 5. Sujeito obrigado nem sempre é evidente

A ferramenta reporta o dispositivo e seu destinatário genérico. Em arranjos reais, identificar
**quem** responde exige análise:

- Portal mantido por empresa contratada, sob especificação do órgão — a responsabilidade é do
  contratante, do contratado, ou solidária?
- Sistema federal utilizado por município (e-SUS APS, por exemplo) — quem responde pela
  interface?
- Consórcio intermunicipal de saúde.
- Prestador privado conveniado, executando serviço público por delegação.

O catálogo modela a esfera federativa e a natureza do prestador, o que orienta a análise —
mas não a substitui.

---

## 6. Achados sem critério WCAG

Duas dimensões — custo de acesso e legibilidade — não correspondem a critério algum e recebem
fundamentação jurídica própria, declarada em `legal_thesis_override`.

Essas teses são **mais frágeis** que as ancoradas em critério WCAG, e a diferença precisa ser
explícita:

- A tese sobre custo de dados articula art. 196 da CF/88 com art. 18 da LBI. É defensável, e é
  a contribuição mais original do projeto. Mas **não há norma que fixe limite de peso de
  página**, e o argumento é de princípio, não de regra.
- A tese sobre legibilidade é ainda mais indireta, e por isso a sonda é declarada heurística e
  **nunca produz veredito de violação** — apenas sinaliza revisão editorial.

---

## 7. Uso responsável

**Adequado**

- Instruir representação ao Ministério Público ou ao órgão de controle, com revisão jurídica.
- Fundamentar recomendação técnica a gestor público.
- Produzir evidência empírica para pesquisa acadêmica.
- Monitoramento contínuo interno pelo próprio órgão.

**Inadequado**

- Afirmar publicamente que um órgão "viola a LBI" com base apenas na saída automática, sem
  revisão jurídica.
- Usar o índice de conformidade como nota ou ranking sem declarar a cobertura.
- Anexar o relatório a processo como se fosse laudo pericial.
- Interpretar ausência de achado como conformidade.

---

## 8. Ressalva reproduzida em toda saída

O texto abaixo aparece no rodapé do relatório HTML, no rodapé do painel e na descrição da API:

> Este relatório é instrumento de auditoria técnica e de pesquisa acadêmica. Não constitui
> parecer jurídico nem prova pericial. As proposições jurídicas apresentadas indicam
> fundamentos normativos aplicáveis segundo a matriz documentada do projeto, e sua adequação
> ao caso concreto depende de análise profissional.

A repetição é deliberada. Ressalvas que aparecem só na documentação não são lidas por quem
recebe o relatório.
