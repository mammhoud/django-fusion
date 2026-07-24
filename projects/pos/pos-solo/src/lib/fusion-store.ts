/**
 * FusionStore — Tauri-compatible session preference storage adapter.
 *
 * Provides the same ``getSessionPreference`` / ``initSession`` / ``clearSession``
 * API as ``FusionDecoder`` but supports both browser ``sessionStorage`` and
 * ``@tauri-apps/plugin-store`` for persistent storage in Tauri webviews.
 *
 * Usage::
 *
 *     import { fusionStore } from '@/lib/fusion-store';
 *
 *     // On app startup, fetch the health-check preference
 *     const pref = await fusionStore.initFromHealthCheck();
 *     if (pref) enableFragments();
 *
 *     // In components
 *     const shouldUseFragments = await fusionStore.getSessionPreference();
 */

const SESSION_KEY = 'fusion_render_first';

type StoreAdapter = {
  getItem(key: string): string | null | Promise<string | null>;
  setItem(key: string, value: string): void | Promise<void>;
  removeItem(key: string): void | Promise<void>;
};

/**
 * Attempt to load the Tauri store plugin; falls back to in-memory map.
 */
async function createTauriStoreAdapter(): Promise<StoreAdapter | null> {
  try {
    // @ts-expect-error — @tauri-apps/plugin-store may not be installed in dev
    const { Store } = await import('@tauri-apps/plugin-store');
    const store = await Store.load('fusion-prefs.json');
    return {
      async getItem(key: string): Promise<string | null> {
        const val: unknown = await store.get(key);
        return typeof val === 'string' ? val : null;
      },
      async setItem(key: string, value: string): Promise<void> {
        await store.set(key, value);
        await store.save();
      },
      async removeItem(key: string): Promise<void> {
        await store.delete(key);
        await store.save();
      },
    };
  } catch {
    return null;
  }
}

let _adapter: StoreAdapter | null = null;

async function getAdapter(): Promise<StoreAdapter> {
  if (_adapter) return _adapter;

  // Try Tauri Store first
  const tauriStore = await createTauriStoreAdapter();
  if (tauriStore) {
    _adapter = tauriStore;
    return _adapter;
  }

  // Fall back to in-memory map
  const memory = new Map<string, string>();
  _adapter = {
    getItem(key: string): string | null {
      return memory.get(key) ?? null;
    },
    setItem(key: string, value: string): void {
      memory.set(key, value);
    },
    removeItem(key: string): void {
      memory.delete(key);
    },
  };
  return _adapter;
}

export const fusionStore = {
  async initSession(value: boolean): Promise<void> {
    const adapter = await getAdapter();
    await adapter.setItem(SESSION_KEY, String(value));
  },

  async getSessionPreference(): Promise<boolean | undefined> {
    const adapter = await getAdapter();
    const raw = await adapter.getItem(SESSION_KEY);
    if (raw === null) return undefined;
    return raw === 'true';
  },

  async clearSession(): Promise<void> {
    const adapter = await getAdapter();
    await adapter.removeItem(SESSION_KEY);
  },

  async initFromHealthCheck(sidecarUrl: string = 'http://localhost:8766'): Promise<boolean> {
    try {
      const res = await fetch(`${sidecarUrl}/fusion/health`);
      if (!res.ok) return false;
      const body = await res.json();
      const pref = body.fusion_render_first === true;
      await this.initSession(pref);
      return pref;
    } catch {
      return false;
    }
  },
};

export default fusionStore;
