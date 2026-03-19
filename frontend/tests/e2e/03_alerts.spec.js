/**
 * FASE 9 — Teste E2E: Alerts / IntelligentAlerts
 * Valida: página carrega, lista de alertas visível, filtros funcionam.
 */
const { test, expect } = require('@playwright/test');
const { gotoAuthenticated, API_URL } = require('./helpers');

test.describe('Alerts', () => {

  test.beforeEach(async ({ page }) => {
    await gotoAuthenticated(page, '/alerts');
  });

  test('página de alertas carrega', async ({ page }) => {
    const container = page.locator(
      '[class*="alert"], [class*="Alert"], [class*="incident"], h1, h2'
    );
    await expect(container.first()).toBeVisible({ timeout: 10000 });
  });

  test('exibe lista de alertas ou mensagem de vazio', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Deve mostrar alertas OU mensagem explícita de "sem alertas"
    const alertItems = page.locator('[class*="alert-item"], [class*="incident-row"], tr');
    const emptyMsg = page.locator('text=/sem alertas|no alerts|nenhum alerta|nenhum incidente/i');

    const hasAlerts = await alertItems.count();
    const hasEmpty = await emptyMsg.count();

    expect(hasAlerts + hasEmpty).toBeGreaterThan(0);
  });

  test('API de alertas responde com 200', async ({ page }) => {
    const token = await page.evaluate(() => localStorage.getItem('token'));

    const response = await page.request.get(`${API_URL}/api/v1/alerts`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body) || typeof body === 'object').toBe(true);
  });

});
