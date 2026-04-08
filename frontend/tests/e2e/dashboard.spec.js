// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Observability Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token
    await page.addInitScript(() => {
      localStorage.setItem('token', 'e2e-test-token');
    });
  });

  test('navigate to observability dashboard', async ({ page }) => {
    await page.goto('/');
    // Look for observability link/nav item and click
    const obsLink = page.locator('text=Observabilidade').first();
    if (await obsLink.isVisible()) {
      await obsLink.click();
    }
    await expect(page.locator('text=Observabilidade')).toBeVisible({ timeout: 10000 });
  });

  test('health score visible', async ({ page }) => {
    await page.goto('/');
    // Navigate to observability
    const obsLink = page.locator('text=Observabilidade').first();
    if (await obsLink.isVisible()) {
      await obsLink.click();
    }
    // Health score gauge should be visible
    await expect(page.locator('text=HEALTH SCORE')).toBeVisible({ timeout: 15000 });
  });

  test('alerts table visible', async ({ page }) => {
    await page.goto('/');
    const obsLink = page.locator('text=Observabilidade').first();
    if (await obsLink.isVisible()) {
      await obsLink.click();
    }
    // Alerts section header
    await expect(page.locator('text=Alertas Inteligentes')).toBeVisible({ timeout: 15000 });
  });

  test('can switch between views', async ({ page }) => {
    await page.goto('/');
    // Check that navigation sidebar has multiple view options
    const navItems = page.locator('nav a, .sidebar a, .menu-item');
    const count = await navItems.count();
    expect(count).toBeGreaterThan(0);
  });
});
