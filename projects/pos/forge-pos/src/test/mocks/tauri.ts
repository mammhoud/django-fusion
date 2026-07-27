/**
 * Tauri invoke mock utility.
 *
 * Supports multiple simultaneous command registrations.
 *
 * Usage:
 *   import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
 *   beforeEach(() => resetInvokeMocks());
 *   it('works', async () => {
 *     mockInvokeSuccess('get_products', []);
 *     mockInvokeSuccess('get_settings', {});
 *     const result = await invoke('get_products');
 *     expect(result).toEqual([]);
 *   });
 */

type MockImpl = (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;

const handlers = new Map<string, MockImpl>();

function defaultMock(cmd: string): Promise<unknown> {
  // AuthContext calls these on mount — provide sane defaults so pages wrapped
  // in AuthProvider don't error out unless a test explicitly mocks them.
  if (cmd === 'check_auth_required' || cmd === 'has_users') {
    return Promise.resolve(false);
  }
  return Promise.reject(new Error(`No mock configured for command: ${cmd}`));
}

/**
 * Reset all command mocks.
 */
export function resetInvokeMocks() {
  handlers.clear();
}

/**
 * Configure `invoke` to resolve successfully for a specific command.
 */
export function mockInvokeSuccess<T>(command: string, result: T) {
  handlers.set(command, () => Promise.resolve(result));
}

/**
 * Configure `invoke` to reject with a specific error for a command.
 */
export function mockInvokeError(command: string, errorMessage: string) {
  handlers.set(command, () => Promise.reject(new Error(errorMessage)));
}

/**
 * Configure `invoke` to resolve for all commands (no registered handler) with a default result.
 */
export function mockInvokeSuccessAll<T>(result: T) {
  handlers.clear();
  handlers.set('*', () => Promise.resolve(result));
}

/**
 * Configure `invoke` to reject for all commands.
 */
export function mockInvokeFatalError(errorMessage: string) {
  handlers.clear();
  handlers.set('*', () => Promise.reject(new Error(errorMessage)));
}

/**
 * Get the current mock implementation lookup (for use in setup.ts).
 */
export function getMockInvokeHandler(cmd: string): MockImpl {
  const handler = handlers.get(cmd) || handlers.get('*') || defaultMock;
  return handler;
}

/**
 * Simulate an invoke call through the mock (same signature as real invoke).
 * Returns { data } on success or { error } on failure.
 */
export async function safeInvoke<T>(
  command: string,
  args?: Record<string, unknown>,
): Promise<{ data?: T; error?: string }> {
  try {
    const handler = getMockInvokeHandler(command);
    const data = await handler(command, args);
    return { data: data as T };
  } catch (err) {
    return { error: err instanceof Error ? err.message : String(err) };
  }
}
