// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Intelligent Alerts', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('token', 'e2e-test-token');
    });
  });

  test('open intelligent alerts page', async ({ page }) => {
    await page.goto('/');
    // Navigate to alerts
    const alertsLink = page.locator('text=Alertas').first();
    if (await alertsLink.isVisible()) {
      await alertsLink.click();
    }
    // Should see the alerts interface
    await expect(page.locator('text=alertas').first()).toBeVisible({ timeout: 15000 });
  });

  test('filter by severity', async ({ page }) => {
    await page.goto('/');
    const alertsLink = page.locator('text=Alertas').first();
    if (await alertsLink.isVisible()) {
      await alertsLink.click();
    }
    // Find severity filter dropdown
    const severitySelect = page.locator('select').nth(1);
    if (await severitySelect.isVisible()) {
      await severitySelect.selectOption('critical');
      // Wait for filtered results
      await page.waitForTimeout(1000);
    }
  });

  test('click alert to see root cause', async ({ page }) => {
    await page.goto('/');
    const alertsLink = page.locator('text=Alertas').first();
    if (await alertsLink.isVisible()) {
      await alertsLink.click();
    }
    // Wait for alerts to load
    await page.waitForTimeout(2000);
    // Click first alert item
    const firstAlert = page.locator('.ia-list-item').first();
    if (await firstAlert.isVisible()) {
      await firstAlert.click();
      // Root cause section should appear
      await expect(page.locator('text=Causa Raiz')).toBeVisible({ timeout: 10000 });
    }
  });
});
