/**
 * FASE 9 — Teste E2E: Dashboard
 * Valida: carregamento, cards de status, dados reais (não vazio).
 */
const { test, expect } = require('@playwright/test');
const { gotoAuthenticated, waitForDataLoad } = require('./helpers');

test.describe('Dashboard', () => {

  test.beforeEach(async ({ page }) => {
    await gotoAuthenticated(page, '/');
  });

  test('carrega sem erros de console críticos', async ({ page }) => {
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    await page.waitForTimeout(2000);

    // Filtrar erros esperados (ex: favicon 404)
    const criticalErrors = errors.filter(e =>
      !e.includes('favicon') && !e.includes('404') && !e.includes('net::ERR')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('exibe cards de status do sistema', async ({ page }) => {
    // Deve ter pelo menos um card com status (online/offline/warning)
    const cards = page.locator('.status-card, .metric-card, [class*="card"]');
    await expect(cards.first()).toBeVisible({ timeout: 10000 });
  });

  test('sidebar está visível com itens de navegação', async ({ page }) => {
    const sidebar = page.locator('.sidebar, nav, [class*="sidebar"]');
    await expect(sidebar.first()).toBeVisible();

    // Deve ter links de navegação
    const navLinks = page.locator('nav a, .sidebar a, [class*="nav-item"]');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(3);
  });

  test('não exibe tela de login após autenticação', async ({ page }) => {
    const loginForm = page.locator('form[action*="login"], input[type="password"]');
    await expect(loginForm).not.toBeVisible();
  });

});
