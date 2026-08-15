/**
 * Auditoria do próprio painel.
 *
 * A ferramenta é submetida à regra que aplica. Um painel de acessibilidade que
 * violasse os critérios que verifica não teria autoridade alguma sobre o que
 * reporta — e o argumento do artigo, de que a conformidade é alcançável com
 * decisões de implementação ordinárias, precisa de demonstração, não de
 * afirmação.
 *
 * Estes testes usam o mesmo axe-core e o mesmo recorte de tags (`wcag2a`,
 * `wcag2aa`, `wcag21a`, `wcag21aa`) do motor de auditoria, de modo que o
 * painel é medido exatamente pela régua que aplica aos portais públicos.
 *
 * Executar com: `npm run test:a11y`
 */

import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

/** Mesmo recorte normativo usado pelo motor (ver config.py, `axe_tags`). */
const TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'];

const TELAS = [
  { caminho: '/', nome: 'Painel de auditorias' },
  { caminho: '/alvos', nome: 'Plataformas do estudo' },
  { caminho: '/referencia', nome: 'Matriz WCAG e LBI' },
  { caminho: '/rota-inexistente', nome: 'Endereço não encontrado' },
];

/**
 * A tela de detalhe exige uma varredura existente e, portanto, a API no ar.
 * É a tela mais densa do painel — tabelas, blocos expansíveis, listas de
 * definição aninhadas — e por isso a que mais precisa ser auditada.
 *
 * Inclui-se apenas quando `ROTA_VARREDURA` estiver definida:
 *
 *     $env:ROTA_VARREDURA = "/varreduras/<id>"; npm run test:a11y
 *
 * Sem a variável, a suíte roda sem ela em vez de falhar — o painel precisa ser
 * auditável mesmo em ambiente sem banco populado (integração contínua, por
 * exemplo), e um teste que só passa com dados locais não é um teste.
 */
const rotaDaVarredura = process.env.ROTA_VARREDURA;
if (rotaDaVarredura) {
  TELAS.push({ caminho: rotaDaVarredura, nome: 'Detalhe da varredura' });
}

for (const tela of TELAS) {
  test(`${tela.nome} não tem violações WCAG 2.1 A/AA`, async ({ page }) => {
    await page.goto(tela.caminho);
    // Aguarda o conteúdo assíncrono: auditar antes da hidratação mediria uma
    // casca vazia e passaria trivialmente.
    await page.waitForLoadState('networkidle');

    const resultado = await new AxeBuilder({ page }).withTags(TAGS).analyze();

    // Mensagem detalhada: um teste que falha dizendo apenas "esperado 0" não
    // ajuda ninguém a corrigir.
    const detalhes = resultado.violations
      .map(
        (v) =>
          `${v.id} (${v.impact}): ${v.help}\n` +
          v.nodes.map((n) => `    ${n.target.join(' ')}`).join('\n'),
      )
      .join('\n');

    expect(resultado.violations, `Violações em ${tela.caminho}:\n${detalhes}`).toEqual([]);
  });
}

test('o link de salto leva ao conteúdo principal', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');

  const focado = page.locator(':focus');
  await expect(focado).toHaveText(/Pular para o conteúdo principal/);

  await focado.press('Enter');
  await expect(page).toHaveURL(/#conteudo$/);
});

test('a navegação é integralmente alcançável por teclado', async ({ page }) => {
  await page.goto('/');

  const alcancados: string[] = [];
  for (let i = 0; i < 12; i += 1) {
    await page.keyboard.press('Tab');
    const texto = await page.evaluate(() =>
      (document.activeElement?.textContent ?? '').trim().slice(0, 40),
    );
    if (texto) alcancados.push(texto);
  }

  expect(alcancados.some((t) => t.includes('Alvos auditados'))).toBe(true);
  expect(alcancados.some((t) => t.includes('Matriz WCAG'))).toBe(true);
});

test('a página corrente é anunciada por aria-current', async ({ page }) => {
  await page.goto('/alvos');
  const atual = page.locator('nav[aria-label="Navegação principal"] a[aria-current="page"]');
  await expect(atual).toHaveCount(1);
  await expect(atual).toHaveText('Alvos auditados');
});

test('todo foco de teclado produz mudança visual perceptível', async ({ page }) => {
  // Verifica o critério 2.4.7 pela mesma técnica da sonda do backend
  // (probe.focus-visible): tabulação real, e não .focus() programático, porque
  // navegadores só aplicam :focus-visible quando a modalidade é o teclado.
  await page.goto('/');

  for (let i = 0; i < 8; i += 1) {
    await page.keyboard.press('Tab');
    const temIndicador = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return true;
      const cs = getComputedStyle(el);
      const temOutline = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0;
      const temSombra = cs.boxShadow !== 'none';
      return temOutline || temSombra;
    });
    expect(temIndicador, `Elemento na parada de tabulação ${i + 1} sem indicador de foco`).toBe(
      true,
    );
  }
});
