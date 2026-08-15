# Dependências vendorizadas

## `axe.min.js` — axe-core 4.13.0

Motor de regras de acessibilidade da Deque Systems, licenciado sob
**Mozilla Public License 2.0** (texto integral em `AXE-CORE-LICENSE.txt`).

### Por que vendorizar em vez de baixar em tempo de execução

Reprodutibilidade. O resultado de uma auditoria depende da versão exata do
motor de regras: entre versões menores, o axe-core altera limiares, adiciona
regras e reclassifica impactos. Um estudo que baixasse "a última versão" a cada
execução produziria séries temporais não comparáveis — uma variação no índice
poderia refletir mudança no detector, e não no portal auditado.

A versão fica registrada em cada `ScanResult` (campo `axe_version`), de modo que
qualquer número publicado possa ser rastreado até o motor que o produziu.

### Como atualizar

```powershell
cd backend/vendor
npm pack axe-core@<versão>
tar -xzf axe-core-<versão>.tgz
Copy-Item package/axe.min.js axe.min.js -Force
Copy-Item package/LICENSE AXE-CORE-LICENSE.txt -Force
Remove-Item package -Recurse -Force; Remove-Item axe-core-<versão>.tgz
```

Atualizar o axe-core é uma **mudança metodológica**, não uma atualização de
dependência. Exige:

1. Registro em `docs/adr/` justificando a troca.
2. Reexecução da suíte contra `fixtures/pages/` para verificar se o golden set
   ainda produz os mesmos vereditos.
3. Nota na seção de Métodos do artigo, se a coleta atravessar as duas versões.

### Cobertura — limite conhecido e declarado

O axe-core detecta de forma determinística cerca de **um terço** dos critérios
de sucesso WCAG. Os demais dependem de julgamento humano (a alternativa textual
existe, mas descreve corretamente a imagem?). O projeto trata isso explicitamente:
`domain.wcag.SuccessCriterion.automatable` marca quais critérios admitem veredito
automático, e `domain.scoring` reporta a `coverage` junto de todo índice.
