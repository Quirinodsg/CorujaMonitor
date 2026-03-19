/**
 * Helpers compartilhados para testes Playwright — Coruja Monitor v3.0
 */

const API_URL = process.env.API_URL || 'http://localhost:8000';

/**
 * Faz login e retorna o token JWT.
 * Armazena no localStorage para uso nos testes.
 */
async function loginAndGetToken(page, username = 'admin', password = 'admin123') {
  const response = await page.request.post(`${API_URL}/api/v1/auth/login`, {
    data: { username, password },
  });

  if (!response.ok()) {
    throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
  }

  const body = await response.json();
  const token = body.access_token;

  // Injetar token no localStorage antes de navegar
  await page.addInitScript((t) => {
    window.localStorage.setItem('token', t);
  }, token);

  return token;
}

/**
 * Navega para a app já autenticado.
 */
async function gotoAuthenticated(page, path = '/') {
  await loginAndGetToken(page);
  await page.goto(path);
  // Aguardar app carregar (sidebar visível)
  await page.waitForSelector('[data-testid="sidebar"], .sidebar, nav', { timeout: 10000 });
}

/**
 * Aguarda que um elemento não mostre "loading" ou spinner.
 */
async function waitForDataLoad(page, selector, timeout = 10000) {
  await page.waitForSelector(selector, { timeout });
  // Aguardar spinner sumir se existir
  try {
    await page.waitForSelector('.loading, .spinner, [data-loading="true"]', {
      state: 'hidden',
      timeout: 5000,
    });
  } catch {
    // Sem spinner — ok
  }
}

module.exports = { loginAndGetToken, gotoAuthenticated, waitForDataLoad, API_URL };
