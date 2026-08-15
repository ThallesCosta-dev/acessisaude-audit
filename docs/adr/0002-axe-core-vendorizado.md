# ADR 0002 — Vendorizar o axe-core em vez de baixá-lo em execução

**Estado:** aceita

---

## Contexto

O motor de regras determinístico do projeto é o axe-core, distribuído como pacote npm. Há
três formas de obtê-lo: baixar em tempo de execução, declarar como dependência npm com
intervalo de versão, ou vendorizar o arquivo no repositório.

O resultado de uma auditoria depende da **versão exata** do motor: entre versões menores, o
axe-core altera limiares, adiciona regras e reclassifica impactos.

---

## Decisão

Vendorizar `axe.min.js` em `backend/vendor/`, na versão **4.13.0**, com a licença MPL-2.0
junto, e resolver o caminho em tempo de execução com falha alta e imediata se o arquivo
faltar.

Tratar a atualização do axe-core como **mudança metodológica**, não como atualização de
dependência.

---

## Consequências

**Positivas**

- Séries temporais comparáveis: uma variação no índice reflete mudança no portal, não no
  detector.
- A versão viaja em cada `ScanResult` (`axe_version`), tornando todo número rastreável até o
  motor que o produziu.
- Coleta funciona sem rede além dos alvos, e sem Node instalado.

**Negativas assumidas**

- Correções de bug e regras novas não chegam automaticamente. É o preço da comparabilidade.
- 580 KB de JavaScript minificado no repositório.
- Atualizar exige procedimento: ADR, reexecução do golden set, possível reaferição de κ e
  nota de descontinuidade se a coleta atravessar duas versões.

---

## Alternativas descartadas

**`npm install axe-core` com intervalo de versão.** Duas execuções em máquinas diferentes
poderiam usar versões diferentes sem que ninguém percebesse — exatamente o cenário que
invalida um estudo comparativo.

**Baixar de CDN em tempo de execução.** Acrescentaria dependência de rede a cada varredura e
tornaria o resultado dependente do que o CDN servisse naquele instante.

**Reimplementar as regras.** Custo proibitivo e ganho negativo: o axe-core é mais bem testado
que qualquer reimplementação viável, e usar o motor de referência da área fortalece a
validade do estudo perante revisores.
