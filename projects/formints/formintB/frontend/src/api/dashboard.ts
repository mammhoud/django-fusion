/**
 * POS Cloud — Sync Dashboard API
 * ===============================
 * Typed client for the Django dashboard contract (`/api/dashboard/*`),
 * served by `apps.handlers.sync_dashboard` on the pos-cloud backend
 * (:8767). The Astro dev server proxies `/api` to the backend, so these
 * calls use same-origin relative paths and work from the browser without
 * CORS or absolute URLs.
 *
 * Usage:
 *   import { getBranchesHealth, getQueueSummary, getConflictStats } from './dashboard';
 *
 *   const { branches, total } = await getBranchesHealth();
 */

// ---- Types ----------------------------------------------------------------

/** One branch in the fleet roster, from GET /api/dashboard/branches/health. */
export interface BranchHealth {
  id: number;
  name: string;
  code: string;
  node_id: string;
  pos_type: string;
  sync_enabled: boolean;
  online: boolean;
  connected_terminals: number;
}

export interface BranchesHealthResponse {
  branches: BranchHealth[];
  total: number;
}

/** Aggregate queue status, from GET /api/dashboard/queue/summary. */
export interface QueueSummary {
  pending: number;
  failed: number;
  total: number;
  estimated_backlog_seconds: number;
}

/** Aggregate conflict status, from GET /api/dashboard/conflicts/stats. */
export interface ConflictStats {
  pending: number;
  resolved: number;
  dismissed: number;
  total: number;
  by_entity_type: Record<string, number>;
}

/** Uniform envelope returned by the dashboard contract. */
export interface DashboardResponse<T> {
  data: T | null;
  error: string | null;
  ok: boolean;
  status: number;
}

// ---- Fetch wrapper (same-origin, error-envelope aware) ---------------------

const DEFAULT_TIMEOUT_MS = 10_000;

async function request<T = unknown>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<DashboardResponse<T>> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(path, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });

    const contentType = res.headers.get('content-type') || '';
    let data: T | null = null;

    if (contentType.includes('application/json')) {
      data = (await res.json()) as T;
    } else {
      data = ((await res.text()) as unknown) as T;
    }

    return {
      data: res.ok ? data : null,
      error: res.ok
        ? null
        : ((data as Record<string, unknown>)?.error as string | undefined) ||
          `HTTP ${res.status}`,
      ok: res.ok,
      status: res.status,
    };
  } catch (err) {
    const message =
      err instanceof DOMException && err.name === 'AbortError'
        ? 'Request timed out'
        : err instanceof Error
          ? err.message
          : 'Unknown error';
    return { data: null, error: message, ok: false, status: 0 };
  } finally {
    clearTimeout(timer);
  }
}

// ---- Public API ------------------------------------------------------------

export const dashboard = {
  /**
   * GET /api/dashboard/branches/health — live health for every active branch
   * (online flag + connected terminal count per branch).
   */
  getBranchesHealth: () =>
    request<BranchesHealthResponse>('/api/dashboard/branches/health'),

  /** GET /api/dashboard/queue/summary — aggregate sync queue counts. */
  getQueueSummary: () => request<QueueSummary>('/api/dashboard/queue/summary'),

  /** GET /api/dashboard/conflicts/stats — aggregate conflict counts. */
  getConflictStats: () => request<ConflictStats>('/api/dashboard/conflicts/stats'),
};

export default dashboard;
