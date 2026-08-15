# Painel — AcessiSaúde-Audit

React + Vite + TypeScript. Consome a API do backend.

```powershell
npm install
npm run dev        # http://127.0.0.1:5173  (requer `acessisaude servir`)
npm run build
npm run typecheck
npm run test:a11y  # auditoria do próprio painel
```

---

## A ferramenta obedece às regras que aplica

Este painel é auditado pelo **mesmo axe-core**, com o **mesmo recorte de tags**
(`wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`) e nos **mesmos dois perfis de dispositivo** que
o motor aplica aos portais públicos. A suíte falha se houver qualquer violação de nível A ou
AA.

Não é zelo decorativo. O argumento do artigo — de que a conformidade é alcançável com decisões
de implementação ordinárias, e não com investimento extraordinário — precisa de demonstração,
não de afirmação.

### Duas correções que a própria suíte encontrou

Ambas estão documentadas no código, no ponto em que ocorreram:

**1. O alerta de erro roubava o foco.** O componente `Erro` chamava `focus()` ao ser montado.
Parecia boa prática. Na verdade arrancava o usuário de teclado de onde ele estava e tornava o
link de salto inalcançável na primeira tabulação — anulando o mecanismo de bypass do critério
2.4.1 justamente quando a API estava fora do ar. Corrigido: `role="alert"` já implica
`aria-live="assertive"` e anuncia sozinho; o foco não é movido.

**2. O título de página fazia o mesmo na carga inicial.** Mover o foco para o `h1` é a técnica
recomendada em **troca de rota** de aplicações de página única, onde nada é anunciado. Na
carga inicial é incorreto: o navegador já posiciona o usuário no início do documento. A
distinção usa `useLocation().key`, que o react-router define como `'default'` na entrada
inicial do histórico.

Nenhuma das duas apareceria em revisão manual apressada, e ambas quebravam o mesmo critério.

---

## Decisões de acessibilidade

| Critério | Implementação |
|---|---|
| 1.3.1 | Marcos ARIA (`banner`, `navigation`, `main`, `contentinfo`); tabelas com `<caption>` e `<th scope>` |
| 1.4.1 | **Nenhuma informação só por cor.** Toda escala cromática tem rótulo textual em `lib/format.ts`; a cor é reforço |
| 1.4.3 / 1.4.11 | Todas as combinações ≥ 4,5:1 (texto) e ≥ 3:1 (componentes), nos temas claro e escuro. Razões medidas anotadas ao lado de cada token em `styles/global.css` |
| 1.4.4 / 1.4.12 | `rem` em toda tipografia; nenhuma altura fixa em bloco de texto |
| 1.4.10 | Grade fluida; tabelas com rolagem confinada (`role="region"` + `tabindex={0}`, para ser alcançável por teclado) |
| 2.3.1 | Nenhuma animação piscante; `prefers-reduced-motion` respeitado |
| 2.4.1 | Link de salto para o conteúdo principal |
| 2.4.7 | Indicador de foco reforçado, jamais removido |
| 3.1.1 | `lang="pt-BR"` |
| 4.1.3 | Estados de carregamento e erro em regiões `aria-live` |

O destaque da página corrente na navegação é derivado do próprio `[aria-current='page']` em
CSS, o que impede que o sinal visual e o sinal semântico divirjam.

---

## Estrutura

```
src/
  lib/
    types.ts     contrato com a API (espelha os esquemas Pydantic)
    api.ts       cliente HTTP + useRecurso
    format.ts    formatação pt-BR e rótulos textuais das escalas
  components/
    ui.tsx       Selo, Indicador, Erro, Tabela, TituloDePagina, avisos
  pages/
    Dashboard.tsx           varreduras e barreiras estruturais
    DetalheDaVarredura.tsx  índices, perfil de exclusão, achados por risco jurídico
    Alvos.tsx               desenho amostral e lacunas declaradas
    Referencia.tsx          matriz WCAG↔LBI consultável
    NaoEncontrada.tsx
  styles/global.css
tests/acessibilidade.spec.ts
```

---

## Duas decisões de projeto

**Sem biblioteca de dados.** O painel faz poucas requisições, todas disparadas por navegação
explícita. React Query ou SWR trariam cache e invalidação que ninguém precisa. `useRecurso`
cobre o caso em ~40 linhas e mantém a superfície pequena o bastante para ser lida inteira.

**Nenhuma regra de negócio em TypeScript.** Rótulos jurídicos, risco por critério e a matriz
WCAG↔LBI vêm do endpoint `/referencia`. Reimplementá-los aqui criaria duas versões da matriz,
e elas divergiriam.

---

## Erro é estado de primeira classe

`useRecurso` devolve `erro`, e cada tela é obrigada a renderizá-lo em uma região `role="alert"`.
Um painel que falha em branco é, para o usuário de leitor de tela, indistinguível de um painel
vazio.

A suíte de acessibilidade roda **com a API fora do ar** por padrão: o estado de erro precisa
ser tão acessível quanto o estado com dados.
