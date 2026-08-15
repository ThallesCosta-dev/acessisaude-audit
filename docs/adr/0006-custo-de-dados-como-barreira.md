# ADR 0006 — Tratar o custo de acesso como barreira auditável

**Estado:** aceita

---

## Contexto

A WCAG pressupõe um usuário que **já chegou** à página: pergunta se ele consegue percebê-la e
operá-la. Não pergunta quanto custou chegar.

No recorte deste projeto — plataformas públicas de saúde acessadas por população periférica
—, essa pergunta é decisiva. Um portal que exige 6 MB para exibir a tela de agendamento
consome, em plano pré-pago típico, fração relevante da franquia mensal. Para quem precisa
consultar repetidamente o andamento de um agendamento ou o resultado de um exame, o custo se
multiplica a cada tentativa.

O título do projeto anuncia auditoria de "acessibilidade **e direitos digitais**". Restringir
o escopo à WCAG entregaria só a primeira metade.

---

## Decisão

Medir o custo de acesso como dimensão de primeira classe, com **fundamentação jurídica
própria**, e não como métrica de desempenho.

### O que se mede

Bytes efetivamente trafegados (corpo comprimido + cabeçalhos), em contexto de navegação novo
— o cenário do primeiro acesso, e também o de quem limpa dados do aparelho por falta de
espaço. Convertidos em:

- custo em reais por acesso, sob preço de referência declarado;
- fração da franquia mensal consumida;
- **fração destinada a domínios de terceiros**.

### Por que a fração de terceiros é reportada em separado

É a métrica juridicamente mais relevante: ali há **transferência de custo ao cidadão sem
contrapartida no serviço público prestado**. O usuário custeia, da própria franquia,
analítica e recursos que não lhe entregam o serviço solicitado.

O motor distingue as duas causas — peso próprio e tráfego de terceiros — em vez de somá-las,
porque têm correções e fundamentos distintos. O golden set verifica essa distinção.

### Como o achado se sustenta juridicamente

`Finding` recebeu três campos para achados sem critério WCAG correspondente:
`legal_risk_override`, `extra_provisions` e `legal_thesis_override`. A tese:

> O custo de dados exigido para acessar o serviço digital de saúde transfere ao cidadão um
> ônus econômico como condição de exercício de direito fundamental. Quando esse ônus recai
> desproporcionalmente sobre a população de menor renda — a mesma que depende exclusivamente
> do SUS —, o acesso deixa de ser universal e igualitário, em desacordo com o art. 196 da
> CF/88 e com o dever de informação adequada do art. 18, § 4º da Lei 13.146/2015.

Dispositivos: CF/88 art. 196; LBI art. 18; Lei 13.460/2017 art. 5º; CF/88 art. 5º, XIV.

O grupo afetado é modelado como `DeficiencyGroup.LOW_BANDWIDTH` — que não é uma deficiência,
e está no mesmo enum deliberadamente: o projeto trata exclusão digital e exclusão por
deficiência como barreiras de mesma natureza jurídica, porque ambas obstruem o acesso ao
direito à saúde.

---

## Consequências

**Positivas**

- O projeto audita o que anuncia auditar.
- A barreira econômica ganha número: "R$ 0,60 por acesso, 0,29% da franquia mensal" é
  argumento; "o site é pesado" não é.
- O perfil de exclusão passa a incluir o usuário periférico ao lado dos grupos de deficiência.

**Negativas assumidas**

- **O preço de referência é uma premissa, não um dado medido.** Os valores padrão
  (`R$ 0,10/MB`, franquia de 2048 MB) são ilustrativos e estão marcados como tal no código,
  na configuração e na documentação. Publicar sem substituí-los por valores coletados, com
  fonte e data, seria erro grave.
- A medição depende do momento da coleta: portais mudam de peso. Mitigado pelo registro de
  data e pela proposta de auditoria **contínua**.
- Um achado sem critério WCAG pode ser lido como "invenção do autor". Mitigado pela tese
  jurídica explícita, que declara exatamente qual dever se considera violado e por quê.

---

## Alternativa descartada

**Reportar o peso apenas como métrica de desempenho, sem qualificação jurídica.** Seria a
escolha segura e esvaziaria a contribuição: o peso da página já é medido por dezenas de
ferramentas. O que este projeto acrescenta é a leitura de que ele constitui barreira de
acesso a direito — e essa leitura precisa ser afirmada, com fundamento, para ser discutida.
