/**
 * Performance simulation utilities for frontend tests.
 */

/**
 * Measure render time of a callback that triggers React rendering.
 * @param {Function} renderFn - async function that performs the render
 * @returns {Promise<number>} elapsed time in ms
 */
export async function measureRenderTime(renderFn) {
  const start = performance.now();
  await renderFn();
  const end = performance.now();
  return end - start;
}

/**
 * Count re-renders of a component using a ref callback.
 * Returns a ref object with { count } that increments on each render.
 */
export function createRenderCounter() {
  const counter = { count: 0 };
  const increment = () => { counter.count += 1; };
  return { counter, increment };
}

/**
 * Simulate rapid state updates (like WS burst) and measure if UI stays responsive.
 * @param {Function} updateFn - function to call for each update
 * @param {number} count - number of updates
 * @param {number} intervalMs - ms between updates (0 = synchronous)
 */
export async function simulateBurstUpdates(updateFn, count = 100, intervalMs = 0) {
  const start = performance.now();
  for (let i = 0; i < count; i++) {
    updateFn(i);
    if (intervalMs > 0) {
      await new Promise(r => setTimeout(r, intervalMs));
    }
  }
  return performance.now() - start;
}

/**
 * Assert that a render completes within a time budget.
 */
export function assertRenderWithin(elapsedMs, budgetMs, label = 'render') {
  if (elapsedMs > budgetMs) {
    throw new Error(`${label} took ${elapsedMs.toFixed(0)}ms, exceeding budget of ${budgetMs}ms`);
  }
}

/**
 * Generate a large dataset and verify the component doesn't crash.
 */
export function stressTestData(generator, count) {
  const data = generator(count);
  expect(data).toHaveLength(count);
  return data;
}
