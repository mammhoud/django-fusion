import { Page } from '@playwright/test';

/**
 * Shared test utilities for all E2E tests.
 */

/**
 * Capture console errors during a test, filtering out known benign warnings.
 * Call at the start of a test and assert at the end.
 *
 * ```ts
 * const errors = captureConsoleErrors(page);
 * // ... test actions ...
 * expect(errors.getFiltered()).toHaveLength(0);
 * ```
 */
export function captureConsoleErrors(page: Page) {
  const allErrors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      allErrors.push(msg.text());
    }
  });

  return {
    getAll: () => allErrors,
    getFiltered: () =>
      allErrors.filter(
        (e) =>
          !e.includes('hydration') &&
          !e.includes('Warning:') &&
          !e.includes('React does not recognize') &&
          !e.includes('Fusion') &&
          !e.includes('WebSocket')
      ),
  };
}

/**
 * Wait for a FusionPage fragment to finish loading.
 * After the initial page load, FusionPage may fetch a fragment
 * from the sidecar. This waits for that to complete.
 */
export async function waitForFusionFragment(page: Page, timeout: number = 10000): Promise<void> {
  try {
    await page.waitForFunction(
      () => {
        const skeletons = document.querySelectorAll('.skeleton, [data-testid="loading-skeleton"]');
        return skeletons.length === 0;
      },
      { timeout }
    );
  } catch {
    // Fusion fragment may not be present (data mode) — that's fine
  }
}
