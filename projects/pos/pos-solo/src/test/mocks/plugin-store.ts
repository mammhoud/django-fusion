// Mock for @tauri-apps/plugin-store (used by fusion-store.ts)
// Uses a real Map so values persist across set → get calls.
const _data = new Map<string, unknown>();

export const Store = {
  load: async () => ({
    get: async (key: string) => _data.get(key) ?? null,
    set: async (key: string, value: unknown) => { _data.set(key, value); },
    save: async () => {},
    delete: async (key: string) => { _data.delete(key); },
  }),
};
