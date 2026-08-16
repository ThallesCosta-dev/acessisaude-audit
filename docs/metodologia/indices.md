# Índices: construção, justificativa e calibração

> Implementação: [`backend/src/acessisaude_audit/domain/scoring.py`](../../backend/src/acessisaude_audit/domain/scoring.py)
> Testes que travam as propriedades: [`backend/tests/unit/test_indices.py`](../../backend/tests/unit/test_indices.py)

---

## 1. Por que não contar violações

Contar violações é a métrica ingênua da área e produz três vieses conhecidos. Os três são
suficientes para invalidar comparações entre portais, que é justamente o que este estudo faz.

### Viés de template

Uma página com 400 links sem nome acessível recebe 400 ocorrências. Mas é *um* defeito: o
componente de link do sistema de design. Corrigi-lo em um lugar resolve os 400. Contagem
bruta pune portais grandes por serem grandes.

### Viés de equivalência

Somar uma falha de `lang` ausente com uma armadilha de teclado supõe que ambas pesam igual.
A primeira degrada a pronúncia sintética; a segunda prende o usuário fora do serviço. Um
índice que as trate como uma unidade cada não serve para priorizar correção.

### Viés de cobertura

Ferramentas automáticas verificam parte dos critérios. Relatar "97% de conformidade" sobre
esse subconjunto, sem declarar o denominador, é metodologicamente indefensável — e é a
prática mais comum na literatura da área.

---

## 2. Os quatro indicadores

Nenhum deve ser lido isoladamente. Juntos respondem a perguntas diferentes:

| Indicador | Pergunta que responde | Escala |
|---|---|---|
| **ICA** — Conformidade | Quanto do exigível foi cumprido? | 0–100, maior é melhor |
| **IAN** — Atrito de navegação | Quanto custa usar mesmo assim? | 0–100, menor é melhor |
| **IEJ** — Exposição jurídica | Qual o tamanho do passivo? | 0–100, menor é melhor |
| **Barreira absoluta** | É possível usar? | booleano |

O último não é um índice, e é o mais importante. Um portal pode ter ICA de 85 e ser
inutilizável por uma única armadilha de teclado. **Nenhum índice contínuo captura a diferença
entre "difícil" e "impossível"** — daí o sinalizador booleano, exibido antes de qualquer
número em toda saída do sistema.

---

## 3. ICA — Índice de Conformidade de Acessibilidade

```
ICA = 100 · ( 1 − Σ_{c ∈ V} w(c) / Σ_{c ∈ A} w(c) )
```

onde:

- `A` = critérios com veredito automático possível (**27 dos 50**);
- `V ⊆ A` = critérios efetivamente violados;
- `w(c)` = peso do risco jurídico do critério.

### Duas decisões embutidas

**O denominador é honesto.** Critérios sem verificação automática possível não entram no
cálculo. A razão `|A|/50 = 0,54` é reportada como `coverage` ao lado de todo índice.

**A ponderação é jurídica, não técnica.** Violar 2.1.1 (teclado, risco crítico, peso 12)
derruba o índice doze vezes mais que violar 3.1.2 (idioma de partes, risco baixo, peso 1).
A alternativa — tratar critérios como equivalentes — produziria o resultado absurdo de um
portal operável por teclado e um portal inoperável pontuando igual por terem o mesmo número
de critérios violados.

### Pesos por faixa de risco

| Risco | Peso | Critérios | Definição |
|---|---|---|---|
| Crítico | 12 | 4 | Impede acesso a serviço essencial, sem rota alternativa |
| Alto | 7 | 18 | Impede a conclusão da tarefa por grupo identificável |
| Moderado | 3 | 19 | Exige esforço desproporcional ou auxílio de terceiro |
| Baixo | 1 | 9 | Dificulta, mas há rota alternativa |

Os quatro critérios de risco crítico são **2.1.1** (Teclado), **2.1.2** (Sem bloqueio do
teclado), **2.3.1** (Três flashes) e **4.1.2** (Nome, função, valor). Três impedem o uso;
o quarto pode causar crise epiléptica — dano à integridade física, e não apenas ao acesso.

---

## 4. IAN — Índice de Atrito de Navegação

```
atrito_bruto  =  Σ_f  peso_técnico(f) · peso_jurídico(f) · log₂(1 + ocorrências_f) · φ

IAN  =  100 · ( 1 − e^{ −atrito_bruto / κ } )
```

com `φ = 1,5` para páginas de fluxo essencial declarado no catálogo, e `φ = 1` nas demais.

### Amortecimento logarítmico

`log₂(1 + n)` corrige o viés de template. A segunda ocorrência do mesmo defeito informa
muito menos que a primeira:

| Ocorrências | Fator | Ganho sobre a linha anterior |
|---|---|---|
| 1 | 1,00 | — |
| 10 | 3,46 | +2,46 |
| 100 | 6,66 | +3,20 |
| 400 | 8,65 | +1,99 |

Cem elementos com o mesmo defeito pesam 6,7 vezes um — não cem vezes.

### Saturação exponencial

Uma soma linear tornaria o índice ilimitado e incomparável entre portais de tamanhos
diferentes. Um corte simples em 100 achataria toda a faixa alta, impedindo distinguir "ruim"
de "inutilizável". A saturação exponencial resolve as duas coisas.

### Multiplicador de fluxo essencial

A mesma barreira tem consequência distinta na página institucional e na tela de confirmação
de consulta. O catálogo declara quais páginas integram fluxo essencial
(`critical: true` em `targets.yaml`), e o atrito dessas páginas é multiplicado por 1,5.

---

## 5. Calibração de κ

<a id="calibracao"></a>

O valor `κ = 150` **não foi escolhido, foi medido.** O procedimento:

1. Executar a varredura de referência contra o conjunto de validação.
2. Calcular o atrito bruto de cada página.
3. Escolher κ de modo que a escala discrimine na faixa de interesse.

### Atrito bruto medido (axe-core 4.13.0 + 16 sondas)

| Página do conjunto de validação | Perfil | Violações | Atrito bruto |
|---|---|---|---|
| `acessivel-agendamento.html` | ambos | 0 | 0,0 |
| `pagina-pesada.html` | desktop | 1 | 9,0 |
| `contraste-e-cor.html` | desktop | 1 | 84,0 |
| `pagina-pesada.html` | mobile-320 | 2 | 164,4 |
| `contraste-e-cor.html` | mobile-320 | 2 | 239,4 |
| `formulario-sem-rotulos.html` | desktop | 2 | 306,0 |
| `formulario-sem-rotulos.html` | mobile-320 | 3 | 432,0 |
| `inacessivel-agendamento.html` | desktop | 19 | 1810,8 |
| `inacessivel-agendamento.html` | mobile-320 | 20 | 2044,0 |

### Por que 150 e não 40

O valor inicialmente adotado (`κ = 40`) foi **descartado por falhar na aferição**. Com ele:

| Atrito bruto | IAN com κ=40 | IAN com κ=150 |
|---|---|---|
| 9,0 | 20,1 | **5,8** |
| 42,0 (uma falha séria de risco alto) | 65,0 | **24,4** |
| 84,0 | 87,8 | **42,9** |
| 306,0 | 100,0 | **87,0** |
| 1810,8 | 100,0 | **100,0** |

Com κ=40, quatro das cinco fixtures marcavam acima de 98 e uma única falha séria já pontuava
65: o índice deixava de distinguir "ruim" de "inutilizável", que é exatamente a distinção
que ele existe para fazer.

A correção está registrada porque importa metodologicamente: **a docstring afirmava uma
calibração que os dados não sustentavam.** A aferição foi feita, a afirmação estava errada,
o parâmetro foi corrigido e o comportamento foi travado em teste
(`TestCalibracaoDoAtrito`), de modo que alterá-lo exija alterar o teste — e portanto assumir
a mudança.

### Recalibração

Quando o conjunto de sondas mudar, o atrito bruto muda e κ precisa ser reaferido:

```powershell
acessisaude varrer fixtures-local
# medir o atrito bruto por página e reajustar κ
# atualizar esta tabela, a docstring de ScoringParameters e TestCalibracaoDoAtrito
```

Registrar a recalibração em `docs/adr/` é obrigatório: séries temporais coletadas com κ
diferentes não são comparáveis.

---

## 6. IEJ — Índice de Exposição Jurídica

Mesma forma funcional do IAN, com duas diferenças:

- **Ignora o peso técnico.** Interessa a gravidade jurídica, não a do axe-core.
- **Descarta o risco baixo.** Passivo jurídico não se mede por irregularidade formal, e sim
  por obstrução efetiva de direito. Um portal cujas únicas falhas sejam de risco baixo tem
  IEJ zero — e isso é uma afirmação deliberada, não um efeito colateral.

---

## 7. Custo de acesso

Dimensão sem correspondência na WCAG, medida em bytes efetivamente trafegados (corpo
comprimido + cabeçalhos), em contexto de navegação novo — o cenário do primeiro acesso, e
também o de quem limpa dados do aparelho por falta de espaço.

```
custo_BRL          = peso_MiB × preço_por_MiB
fração_da_franquia = peso_MiB / franquia_mensal_MiB
```

### Parâmetros coletados

| Parâmetro | Valor | Fonte |
|---|---|---|
| Preço do MiB | R$ 0,0029296875 (**R$ 3,00/GiB**) | Claro Prezão R$ 15,00 / 5 GB / 15 dias, consulta em 10/08/2026 |
| Franquia mensal | 10 240 MiB (10 GiB) | Duas recargas do mesmo plano |
| Limiar de página onerosa | 2,5 MiB | Peso mediano móvel, HTTP Archive Web Almanac 2025 |

Procedência completa, valores corroborantes da Anatel e critérios de reavaliação em
[parâmetros de custo](parametros-de-custo.md).

Os três são **conservadores por construção**: a Anatel reporta preço efetivo de R$ 5,46/GB
(82% acima do adotado) e ARPU pré-pago de R$ 12,12/mês (franquia real menor que a de
referência). A estimativa erra para menos, nunca para mais.

### O custo de um acesso isolado é pequeno — e o artigo precisa dizer isso

Com os valores reais, uma página de 3 MiB custa R$ 0,0088 por acesso. O parâmetro anterior,
ilustrativo, superestimava o custo em **34 vezes**. Inflá-lo seria fabricar evidência.

A força do argumento econômico está em três lugares, todos mensurados:

1. **A jornada completa** — acompanhar um agendamento não é ato único; a sonda reporta o
   consumo em quatro acessos mensais.
2. **A tentativa frustrada** — cada barreira de acessibilidade que obriga a repetir o fluxo
   soma-se à conta. As duas dimensões auditadas **agravam-se mutuamente**, e essa interação é
   a contribuição original da medida.
3. **O tráfego de terceiros** — a parcela que não presta serviço algum ao usuário. É a métrica
   com fundamento jurídico mais direto, porque ali há transferência de custo sem contrapartida.

O motor distingue peso próprio de tráfego de terceiros em vez de somá-los, porque têm
correções e fundamentos distintos, e o conjunto de validação verifica essa distinção.

---

## 8. Perfil de exclusão

Converte contagem de defeitos em população impactada, agregando ocorrências por grupo
afetado (derivado de `SuccessCriterion.affects`).

É a leitura que sustenta o argumento jurídico: o dano juridicamente relevante é o da pessoa
excluída, não o do elemento HTML malformado. Um relatório que diz "107 ocorrências afetam
pessoas com deficiência intelectual" comunica algo que "50 violações" não comunica.

---

## 9. Todos os parâmetros viajam com o dado

Nenhuma constante que afete um número publicável está implícita no código. Todas estão em
`ScoringParameters`, são serializadas em `config_snapshot` de cada varredura e aparecem na
tela de detalhe do painel e no relatório HTML.

```json
"scoring": {
  "friction_kappa": 150.0,
  "critical_path_multiplier": 1.5,
  "price_per_mb_brl": 0.0029296875,
  "franchise_mb": 10240.0,
  "heavy_page_mb": 2.5
}
```

Sem isso, nenhum número seria reexecutável — e um resultado não reexecutável não é um
resultado.
