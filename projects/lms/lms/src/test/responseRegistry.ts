/**
 * Shared mock response registry — used by both mockApi.ts (the base query)
 * and test-utils.tsx (the test helper API).
 *
 * Centralizes all mock response configuration so the mock base query can
 * read what each test registers.
 */

interface MockResponse {
  data?: any;
  error?: { status: number; data: any };
  delay?: number;
}

const responseRegistry = new Map<string, MockResponse>();

/**
 * Register a mock API response for a given method + URL pattern.
 */
export function mockApiResponse(method: string, urlPattern: string, data: any) {
  const key = `${method}:${urlPattern}`;
  responseRegistry.set(key, { data, delay: 0 });
}

/**
 * Register a mock API error response.
 */
export function mockApiError(method: string, urlPattern: string, errorData: any, status = 400) {
  const key = `${method}:${urlPattern}`;
  responseRegistry.set(key, { error: { status, data: errorData }, delay: 0 });
}

/**
 * Clear all registered mock responses.
 */
export function clearApiResponses() {
  responseRegistry.clear();
}

/**
 * Look up a mock response for a given method + URL.
 * Used by the mock base query in mockApi.ts.
 */
export function findMockResponse(method: string, url: string): MockResponse | undefined {
  const exactKey = `${method}:${url}`;
  if (responseRegistry.has(exactKey)) {
    return responseRegistry.get(exactKey);
  }

  // Fall back to segment-aware prefix matching (e.g., '/apis/enrollments' matches '/apis/enrollments/1'
  // but NOT '/apis/enrollments/1/payment/init')
  var found: MockResponse | undefined;
  responseRegistry.forEach(function (response, key) {
    var parts = key.split(':');
    var regMethod = parts[0];
    var regUrl = parts.slice(1).join(':');
    if (regMethod !== method) return;
    if (url === regUrl || url.startsWith(regUrl + '/')) {
      found = response;
    }
  });
  return found;
}
