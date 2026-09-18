/**
 * Mock for @tauri-apps/plugin-dialog — used in vitest tests running in jsdom.
 * Provides stub functions for native file dialogs.
 */

export async function open(_options?: Record<string, unknown>): Promise<string | string[] | null> {
  console.warn('[tauri-mock] dialog.open() called — returning null in test environment');
  return null;
}

export async function save(_options?: Record<string, unknown>): Promise<string | null> {
  console.warn('[tauri-mock] dialog.save() called — returning null in test environment');
  return null;
}

export async function message(_message: string, _options?: Record<string, unknown>): Promise<void> {
  // No-op in test environment
}

export async function ask(_message: string, _options?: Record<string, unknown>): Promise<boolean> {
  return true;
}

export async function confirm(_message: string, _options?: Record<string, unknown>): Promise<boolean> {
  return true;
}
