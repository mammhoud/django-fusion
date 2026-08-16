/**
 * Server API Client
 * ==================
 * Base HTTP client for communicating with the POS Python/Sanic server.
 * All API modules use this client for typed, error-handled requests.
 *
 * Usage:
 *   import server from '../api/server';
 *   const health = await server.get('/health');
 */

// ---- Constants -------------------------------------------------------------

/** Base URL of the Sanic server (always runs locally). Override with VITE_SERVER_URL (.env). */
export const SERVER_BASE =
  (import.meta.env?.VITE_SERVER_URL as string | undefined) || 'http://127.0.0.1:8765';

/** WebSocket base URL. Override with VITE_SERVER_WS_URL (.env). */
export const SERVER_WS_BASE =
  (import.meta.env?.VITE_SERVER_WS_URL as string | undefined) ||
  SERVER_BASE.replace(/^http/, 'ws');

/** Default request timeout in ms */
const DEFAULT_TIMEOUT_MS = 10_000;

// ---- Types ----------------------------------------------------------------

export interface ServerResponse<T = unknown> {
  data: T | null;
  error: string | null;
  ok: boolean;
  status: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
  db_available?: boolean;
}

// ---- Fetch wrapper ---------------------------------------------------------

async function request<T = unknown>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<ServerResponse<T>> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const url = `${SERVER_BASE}${path}`;
    const res = await fetch(url, {
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
      data = await res.json();
    } else {
      const text = await res.text();
      data = text as unknown as T;
    }

    return {
      data: res.ok ? data : null,
      error: res.ok ? null : (data as Record<string, unknown>)?.error as string || `HTTP ${res.status}`,
      ok: res.ok,
      status: res.status,
    };
  } catch (err) {
    const message = err instanceof DOMException && err.name === 'AbortError'
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

export const server = {
  /** Base URL of the server */
  base: SERVER_BASE,

  /** WebSocket base URL */
  wsBase: SERVER_WS_BASE,

  /** Send a GET request to the server */
  get: <T = unknown>(path: string) => request<T>(path),

  /** Send a POST request to the server */
  post: <T = unknown>(path: string, body: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  /** Send a PATCH request to the server */
  patch: <T = unknown>(path: string, body: unknown) =>
    request<T>(path, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  /**
   * Check if the server is running and healthy.
   * Returns true if the /health endpoint responds with status "ok".
   */
  healthCheck: async (): Promise<boolean> => {
    const { data, ok } = await request<HealthResponse>('/health');
    return ok && data?.status === 'ok';
  },

  /**
   * Get the server health status with full details.
   */
  getHealth: () => request<HealthResponse>('/health'),
};

export default server;
