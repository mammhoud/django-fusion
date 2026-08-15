// Formint POS — Fusion Transport (API-first with Tauri-invoke fallback)
//
// Single source of truth for every data round-trip in the app. All pages use
// `fusionFetch()` instead of raw `fetch()` so the app degrades gracefully:
//
//   1. API path    — fetch `/api/v1/…` from the server backend (HTTP).
//   2. Invoke path — if the API is unreachable, call Tauri commands to
//                    (re)start the server, wait for it, and retry once.
//   3. Native path — if the server still cannot start, fall back to
//                    `native_capabilities` (Rust) + a localStorage snapshot
//                    cache so the UI never hard-crashes offline.
//
// The transport is transport-agnostic at the call site: `fusionFetch(path)`
// returns `{ ok, status, data }` with the fusion envelope unwrapped, and
// `data` falling back to the snapshot cache when the backend is down.

export interface FusionEnvelope<T = any> {
  status?: number;
  message?: string;
  data?: T;
  [key: string]: any;
}

export interface NativeCapabilities {
  printing: boolean;
  scanning: boolean;
  filesystem: boolean;
  device_events: boolean;
}

const API_BASE = '';
const SNAPSHOT_KEY = 'formint-offline-snapshot';
const START_RETRIES = 2;
const START_RETRY_DELAY_MS = 1500;

let capabilitiesCache: NativeCapabilities | null = null;

// ── Tauri invoke bridge (graceful when running in a plain browser) ────────

interface TauriBridge {
  invoke(cmd: string, args?: Record<string, unknown>): Promise<unknown>;
}

function tauriBridge(): TauriBridge | null {
  const w = window as any;
  const api = w.__TAURI__?.core ?? w.__TAURI_INVOKE__ ?? null;
  if (api?.invoke) return api;
  if (typeof w.__TAURI_INVOKE__ === 'function') {
    return { invoke: (cmd: string, args?: Record<string, unknown>) => w.__TAURI_INVOKE__(cmd, args) };
  }
  return null;
}

export function isTauri(): boolean {
  return tauriBridge() !== null;
}

// ── Native capabilities (Rust) ─────────────────────────────────────────────

export async function nativeCapabilities(): Promise<NativeCapabilities | null> {
  if (capabilitiesCache) return capabilitiesCache;
  const bridge = tauriBridge();
  if (!bridge) return null;
  try {
    const caps = (await bridge.invoke('native_capabilities')) as NativeCapabilities;
    capabilitiesCache = caps;
    return caps;
  } catch {
    return null;
  }
}

// ── Server lifecycle via Tauri invokes ────────────────────────────────────

export async function serverStatus(): Promise<string | null> {
  const bridge = tauriBridge();
  if (!bridge) return null;
  try {
    return (await bridge.invoke('formint_server_status')) as string;
  } catch {
    return null;
  }
}

export async function startServer(): Promise<boolean> {
  const bridge = tauriBridge();
  if (!bridge) return false;
  try {
    const res = (await bridge.invoke('start_formint_server')) as string;
    return res === 'started' || res === 'already-running';
  } catch {
    return false;
  }
}

// ── Offline snapshot cache ─────────────────────────────────────────────────

export function readSnapshot<T = any>(key: string): T | null {
  try {
    const raw = localStorage.getItem(SNAPSHOT_KEY);
    if (!raw) return null;
    const snap = JSON.parse(raw);
    return (snap?.[key] as T) ?? null;
  } catch {
    return null;
  }
}

export function writeSnapshot(key: string, value: unknown): void {
  try {
    const raw = localStorage.getItem(SNAPSHOT_KEY);
    const snap = raw ? JSON.parse(raw) : {};
    snap[key] = value;
    localStorage.setItem(SNAPSHOT_KEY, JSON.stringify(snap));
  } catch {
    /* storage unavailable — non-fatal */
  }
}

// ── Core request helper ────────────────────────────────────────────────────

export interface FusionResponse<T = any> {
  ok: boolean;
  status: number;
  data: T | null;
  source: 'api' | 'invoke' | 'snapshot';
}

async function httpRequest<T = any>(
  path: string,
  init?: RequestInit,
): Promise<FusionResponse<T>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        'Accept': 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...(init?.headers || {}),
      },
    });
    let body: FusionEnvelope<T> | null = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    const data = body && 'data' in body ? body.data : body;
    return { ok: res.ok, status: res.status, data: data as T, source: 'api' };
  } catch {
    return { ok: false, status: 0, data: null, source: 'api' };
  }
}

/**
 * Resolve a path against the API when the server is reachable; otherwise
 * attempt to start it via Tauri and retry. Returns the transport source so
 * the UI can show "live API" vs "offline snapshot".
 */
export async function fusionFetch<T = any>(
  path: string,
  init?: RequestInit,
  opts: { allowSnapshot?: boolean; snapshotKey?: string } = {},
): Promise<FusionResponse<T>> {
  const { allowSnapshot = true, snapshotKey = path } = opts;

  // 1. Fast path — API is up.
  const first = await httpRequest<T>(path, init);
  if (first.ok) {
    if (allowSnapshot && first.data != null) writeSnapshot(snapshotKey, first.data);
    return first;
  }

  // 2. Invoke path — server may be down: ask Tauri to (re)start it.
  const bridge = tauriBridge();
  if (bridge) {
    for (let attempt = 0; attempt < START_RETRIES; attempt++) {
      await startServer();
      await new Promise((r) => setTimeout(r, START_RETRY_DELAY_MS));
      const retry = await httpRequest<T>(path, init);
      if (retry.ok) {
        if (allowSnapshot && retry.data != null) writeSnapshot(snapshotKey, retry.data);
        return retry;
      }
    }
  }

  // 3. Native path — offline snapshot fallback.
  if (allowSnapshot) {
    const cached = readSnapshot<T>(snapshotKey);
    if (cached != null) {
      return { ok: true, status: 200, data: cached, source: 'snapshot' };
    }
  }
  return first;
}

// ── Typed helpers (used by pages) ──────────────────────────────────────────

export async function fusionHealth() {
  return fusionFetch<{ status: string; models: number }>('/api/v1/health/', undefined, {
    allowSnapshot: false,
  });
}

export async function fusionStats() {
  return fusionFetch<Record<string, number>>('/api/v1/stats/', undefined, {
    snapshotKey: 'stats',
  });
}

export async function fusionNavigation() {
  return fusionFetch<{ brand: any; modules: any[] }>('/api/v1/navigation/', undefined, {
    snapshotKey: 'navigation',
  });
}

export async function fusionComponents() {
  return fusionFetch<{ tables: string[]; forms: string[]; fragments: string[] }>(
    '/api/v1/components/',
    undefined,
    { snapshotKey: 'components' },
  );
}

export async function fusionTable(resource: string) {
  return fusionFetch(`/api/v1/components/tables/${resource}/`, undefined, {
    snapshotKey: `table:${resource}`,
  });
}

export async function fusionForm(resource: string) {
  return fusionFetch(`/api/v1/components/forms/${resource}/`, undefined, {
    snapshotKey: `form:${resource}`,
  });
}

export async function fusionFragment(name: string) {
  return fusionFetch(`/api/v1/components/fragments/${name}/`, undefined, {
    snapshotKey: `fragment:${name}`,
  });
}

export async function syncStatus() {
  return fusionFetch('/api/v1/sync/status/', undefined, { snapshotKey: 'sync-status' });
}

export async function syncPushProducts(payload: unknown) {
  return fusionFetch<{ synced: number; errors: number; approvals_created: number }>(
    '/api/v1/sync/push-products/',
    { method: 'POST', body: JSON.stringify(payload) },
    { allowSnapshot: false },
  );
}

export async function syncReceiveSales(payload: unknown) {
  return fusionFetch<{ synced: number; approvals_created: number }>(
    '/api/v1/sync/receive-sales/',
    { method: 'POST', body: JSON.stringify(payload) },
    { allowSnapshot: false },
  );
}

export async function syncApprovals() {
  return fusionFetch<{ count: number; items: any[] }>('/api/v1/sync/approvals/', undefined, {
    snapshotKey: 'approvals',
  });
}

// ── Transport status report (for the settings/status UI) ───────────────────

export async function transportStatus(): Promise<{
  transport: 'api' | 'invoke' | 'snapshot';
  tauri: boolean;
  server: string | null;
  capabilities: NativeCapabilities | null;
  health: { status: string; models: number } | null;
}> {
  const [health, caps, server] = await Promise.all([
    fusionHealth().then((r) => r.data).catch(() => null),
    nativeCapabilities(),
    serverStatus(),
  ]);
  return {
    transport: health ? 'api' : isTauri() ? 'invoke' : 'snapshot',
    tauri: isTauri(),
    server,
    capabilities: caps,
    health,
  };
}
