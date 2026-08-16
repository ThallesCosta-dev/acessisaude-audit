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

- **O custo monetário de um acesso isolado é pequeno.** Com os parâmetros coletados
  (R$ 3,00/GiB), uma página de 3 MiB custa R$ 0,0088. O argumento econômico não se sustenta
  no acesso único, e sim na jornada completa, na tentativa frustrada por barreira de
  acessibilidade e na parcela do tráfego destinada a terceiros. Ver
  [parâmetros de custo](../metodologia/parametros-de-custo.md), § 5.
- A medição depende do momento da coleta: portais mudam de peso, e as ofertas das operadoras
  também. Mitigado pelo registro de data, pela cadência de reavaliação declarada e pela
  proposta de auditoria **contínua**.
- Um achado sem critério WCAG pode ser lido como "invenção do autor". Mitigado pela tese
  jurídica explícita, que declara exatamente qual dever se considera violado e por quê.

---

## Atualização — 15/08/2026: parâmetros substituídos por valores coletados

Os valores padrão originais eram declaradamente ilustrativos. Foram substituídos por dados
publicados, datados e verificáveis:

| Parâmetro | Antes | Agora | Razão |
|---|---|---|---|
| Preço por MiB | R$ 0,10 | R$ 0,0029296875 | **34× menor** |
| Franquia | 2 048 MiB | 10 240 MiB | 5× maior |
| Limiar de peso | 2,0 MiB | 2,5 MiB | 1,25× maior |

O preço ilustrativo superestimava o custo em trinta e quatro vezes. A correção **enfraquece
numericamente** o argumento do acesso isolado, e é justamente por isso que precisava ser
feita: manter o valor inflado produziria uma conclusão favorável construída sobre uma premissa
inventada.

Duas observações substantivas emergiram da coleta e serão exploradas no artigo:

1. **A penalidade da pobreza.** A mesma operadora cobra 50% a mais por gigabyte de quem
   fraciona a recarga (R$ 3,00/GB contra R$ 2,00/GB) — e fracionar não é escolha, é restrição
   de fluxo de caixa.
2. **A assimetria do zero-rating.** O aplicativo de mensagens privado não consome franquia; o
   portal público de saúde consome. Para o usuário de menor renda, o Estado é o único serviço
   que cobra pelo acesso. Isso sugere via de correção regulatória, e não apenas técnica.

Consequência operacional: a apresentação foi ajustada (valores abaixo de R$ 0,01 exibidos em
centavos; persistência com seis casas decimais) para que a grandeza real não colapse em
"R$ 0,00".

---

## Alternativa descartada

**Reportar o peso apenas como métrica de desempenho, sem qualificação jurídica.** Seria a
escolha segura e esvaziaria a contribuição: o peso da página já é medido por dezenas de
ferramentas. O que este projeto acrescenta é a leitura de que ele constitui barreira de
acesso a direito — e essa leitura precisa ser afirmada, com fundamento, para ser discutida.
