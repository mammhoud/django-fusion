/**
 * POS Cloud — Sync Dashboard API
 * ===============================
 * Typed client for the Django dashboard contract (`/api/dashboard/*`),
 * served by `apps.handlers.sync_dashboard` on the Formint Cloud backend
 * (:8767). The Astro dev server proxies `/api` to the backend, so these
 * calls use same-origin relative paths and work from the browser without
 * CORS or absolute URLs.
 *
 * Usage:
 *   import { dashboard } from './dashboard';
 *
 *   const { branches, total } = await dashboard.getBranchesHealth();
 *   const conflict = await dashboard.resolveConflict(3, 'use_remote');
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

/** One branch in the detailed health view, from GET /api/dashboard/branches/{code}/health. */
export interface BranchHealthDetail {
  id: number;
  name: string;
  code: string;
  node_id: string;
  pos_type: string;
  is_active: boolean;
  sync_enabled: boolean;
  sync_interval: number;
}

export interface BranchHealthDetailResponse {
  branch: BranchHealthDetail;
  websocket: {
    online: boolean;
    connected_terminals: number;
    branch_code: string;
  };
}

/** Aggregate queue status, from GET /api/dashboard/queue/summary. */
export interface QueueSummary {
  pending: number;
  failed: number;
  total: number;
  estimated_backlog_seconds: number;
}

/** Per-branch queue entry, from GET /api/dashboard/queue/by-branch. */
export interface QueueByBranch {
  branch: string;
  code: string;
  pending: number;
  failed: number;
}

export interface QueueByBranchResponse {
  branches: QueueByBranch[];
}

/** One queue item, from GET /api/dashboard/queue/list/{status}. */
export interface QueueItem {
  id: number;
  branch: string;
  branch_code: string;
  entity_type: string;
  operation: string;
  status: string;
  attempt_count: number;
  max_attempts: number;
  last_error: string;
  created_at: string | null;
  next_retry_at: string | null;
}

export interface QueueListResponse {
  items: QueueItem[];
  count: number;
}

/** One pending sync conflict, from GET /api/dashboard/conflicts. */
export interface SyncConflict {
  id: number;
  branch: string;
  branch_code: string;
  node_id: string;
  entity_type: string;
  entity_id: string;
  resolver_used: string;
  reason: string;
  conflict_fields: Array<{
    field: string;
    local_value: unknown;
    remote_value: unknown;
  }>;
  local_data: Record<string, unknown>;
  remote_data: Record<string, unknown>;
  created_at: string | null;
}

export interface ConflictListResponse {
  conflicts: SyncConflict[];
  count: number;
}

/** Aggregate conflict status, from GET /api/dashboard/conflicts/stats. */
export interface ConflictStats {
  pending: number;
  resolved: number;
  dismissed: number;
  total: number;
  by_entity_type: Record<string, number>;
}

/** One sync activity log entry, from GET /api/dashboard/activity. */
export interface ActivityEntry {
  id: number;
  branch: string;
  branch_code: string;
  node_id: string;
  entity_type: string;
  entity_count: number;
  status: string;
  error_message: string;
  received_at: string | null;
}

export interface ActivityResponse {
  entries: ActivityEntry[];
}

/** Resolution choices accepted by POST /api/dashboard/conflicts/{id}/resolve. */
export type ConflictResolution = 'use_local' | 'use_remote' | 'merge';

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

  /** GET /api/dashboard/branches/{code}/health — detailed health for one branch. */
  getBranchHealth: (branchCode: string) =>
    request<BranchHealthDetailResponse>(
      `/api/dashboard/branches/${encodeURIComponent(branchCode)}/health`,
    ),

  /** GET /api/dashboard/queue/summary — aggregate sync queue counts. */
  getQueueSummary: () => request<QueueSummary>('/api/dashboard/queue/summary'),

  /** GET /api/dashboard/queue/by-branch — per-branch pending/failed counts. */
  getQueueByBranch: () =>
    request<QueueByBranchResponse>('/api/dashboard/queue/by-branch'),

  /** GET /api/dashboard/queue/list/{status} — queue items by status (default pending). */
  getQueueList: (status: string = 'pending') =>
    request<QueueListResponse>(
      `/api/dashboard/queue/list/${encodeURIComponent(status)}`,
    ),

  /** POST /api/dashboard/queue/retry/{id} — reset a failed item for retry. */
  retryQueueItem: (itemId: number) =>
    request<{ status: string; item_id: number; next_retry_at: string | null }>(
      `/api/dashboard/queue/retry/${itemId}`,
      { method: 'POST' },
    ),

  /** POST /api/dashboard/queue/cancel/{id} — cancel a pending item. */
  cancelQueueItem: (itemId: number) =>
    request<{ status: string; item_id: number }>(
      `/api/dashboard/queue/cancel/${itemId}`,
      { method: 'POST' },
    ),

  /** GET /api/dashboard/conflicts — pending conflicts needing review. */
  getConflicts: () => request<ConflictListResponse>('/api/dashboard/conflicts'),

  /** GET /api/dashboard/conflicts/stats — aggregate conflict counts. */
  getConflictStats: () => request<ConflictStats>('/api/dashboard/conflicts/stats'),

  /** POST /api/dashboard/conflicts/{id}/resolve — keep one version or merge. */
  resolveConflict: (
    conflictId: number,
    resolution: ConflictResolution,
    opts: { mergedData?: Record<string, unknown>; notes?: string } = {},
  ) =>
    request<{ status: string; conflict_id: number; resolution: string }>(
      `/api/dashboard/conflicts/${conflictId}/resolve`,
      {
        method: 'POST',
        body: JSON.stringify({
          resolution,
          merged_data: opts.mergedData,
          notes: opts.notes ?? '',
        }),
      },
    ),

  /** POST /api/dashboard/conflicts/{id}/dismiss — dismiss without applying. */
  dismissConflict: (conflictId: number) =>
    request<{ status: string; conflict_id: number }>(
      `/api/dashboard/conflicts/${conflictId}/dismiss`,
      { method: 'POST' },
    ),

  /** GET /api/dashboard/activity?limit=N — recent sync activity. */
  getActivity: (limit: number = 20) =>
    request<ActivityResponse>(`/api/dashboard/activity?limit=${limit}`),
};

export default dashboard;
