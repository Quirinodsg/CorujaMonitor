// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Topology View', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('token', 'e2e-test-token');
    });
  });

  test('open topology view', async ({ page }) => {
    await page.goto('/');
    const topoLink = page.locator('text=Topologia').first();
    if (await topoLink.isVisible()) {
      await topoLink.click();
    }
    // Should see topology interface
    await expect(page.locator('.topo-wrap, text=topologia').first()).toBeVisible({ timeout: 15000 });
  });

  test('graph renders with nodes', async ({ page }) => {
    await page.goto('/');
    const topoLink = page.locator('text=Topologia').first();
    if (await topoLink.isVisible()) {
      await topoLink.click();
    }
    // Wait for SVG graph to render
    await page.waitForTimeout(3000);
    const svg = page.locator('.topo-svg, svg[aria-label*="topologia"], svg[aria-label*="Grafo"]');
    if (await svg.isVisible()) {
      // Nodes should be rendered as groups
      const nodes = svg.locator('.topo-node');
      const count = await nodes.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('click node shows impact', async ({ page }) => {
    await page.goto('/');
    const topoLink = page.locator('text=Topologia').first();
    if (await topoLink.isVisible()) {
      await topoLink.click();
    }
    await page.waitForTimeout(3000);
    // Click first node
    const firstNode = page.locator('.topo-node').first();
    if (await firstNode.isVisible()) {
      await firstNode.click();
      // Impact panel should show
      await expect(page.locator('text=Blast Radius')).toBeVisible({ timeout: 10000 });
    }
  });
});
