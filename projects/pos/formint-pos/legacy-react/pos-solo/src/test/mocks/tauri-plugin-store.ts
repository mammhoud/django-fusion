/**
 * Vitest mock for @tauri-apps/plugin-store.
 *
 * This file is aliased in vitest.config.ts to replace the real Tauri plugin-store
 * module, which is not available in the jsdom test environment.
 *
 * Uses a real Map so get() returns previously set values across the test lifecycle.
 */

const _data = new Map<string, unknown>();

export const Store = {
  load: async (/* _name: string */) => ({
    get: async (key: string) => _data.get(key) ?? null,
    set: async (key: string, value: unknown) => { _data.set(key, value); },
    save: async () => {},
    delete: async (key: string) => { _data.delete(key); },
  }),
};
