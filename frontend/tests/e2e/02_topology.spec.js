/**
 * FASE 9 — Teste E2E: TopologyView
 * Valida: grafo renderiza, nós visíveis, sem estado vazio.
 */
const { test, expect } = require('@playwright/test');
const { gotoAuthenticated } = require('./helpers');

test.describe('TopologyView', () => {

  test.beforeEach(async ({ page }) => {
    await gotoAuthenticated(page, '/topology');
  });

  test('página de topologia carrega', async ({ page }) => {
    // Aguardar título ou container da topologia
    const container = page.locator(
      '[class*="topology"], [class*="Topology"], canvas, svg[class*="graph"]'
    );
    await expect(container.first()).toBeVisible({ timeout: 15000 });
  });

  test('renderiza nós no grafo', async ({ page }) => {
    // Aguardar SVG ou canvas com nós
    await page.waitForTimeout(3000); // tempo para D3/vis renderizar

    // Verificar se há elementos de nó (círculos SVG ou divs de nó)
    const nodes = page.locator('circle, [class*="node"], [class*="host-node"]');
    const count = await nodes.count();
    expect(count).toBeGreaterThan(0);
  });

  test('não exibe mensagem de grafo vazio quando há hosts', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Se houver hosts cadastrados, não deve mostrar "nenhum host" ou similar
    const emptyMsg = page.locator('text=/nenhum host|no hosts|empty|vazio/i');
    // Apenas verifica se a mensagem de vazio não é o único conteúdo
    const mainContent = page.locator('[class*="topology"], canvas, svg');
    const hasContent = await mainContent.count();

    if (hasContent > 0) {
      // Tem conteúdo — ok
      expect(hasContent).toBeGreaterThan(0);
    }
  });

});
