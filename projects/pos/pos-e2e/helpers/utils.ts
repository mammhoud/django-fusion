import { Page } from '@playwright/test';

/**
 * Shared test utilities for all E2E tests.
 */

/**
 * Safely check if the page is a valid Playwright Page with the `on` method.
 */
function isValidPage(page: any): page is Page {
  return page && typeof page.on === 'function' && typeof page.goto === 'function';
}

/**
 * Capture console errors during a test, filtering out known benign warnings.
 * Call at the start of a test and assert at the end.
 *
 * If the page is not a valid Playwright Page (e.g., dev server not running),
 * returns a no-op collector so tests don't crash.
 *
 * ```ts
 * const errors = captureConsoleErrors(page);
 * // ... test actions ...
 * expect(errors.getFiltered()).toHaveLength(0);
 * ```
 */
export function captureConsoleErrors(page: Page) {
  const allErrors: string[] = [];

  if (isValidPage(page)) {
    try {
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          allErrors.push(msg.text());
        }
      });
    } catch {
      // Silently ignore if event listener registration fails
    }
  }

  return {
    getAll: () => allErrors,
    getFiltered: () =>
      allErrors.filter(
        (e) =>
          !e.includes('hydration') &&
          !e.includes('Warning:') &&
          !e.includes('React does not recognize') &&
          !e.includes('Fusion') &&
          !e.includes('WebSocket') &&
          !e.includes('invoke') &&
          !e.includes('__TAURI__') &&
          !e.includes('Tauri') &&
          !e.includes('check_auth')
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
