import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';

// ── Types ────────────────────────────────────────────────────────────────

export interface UseApiOptions {
  /** Whether to auto-fetch on mount. Default `true`. */
  enabled?: boolean;
  /** Tauri event name to listen to for auto-refresh. */
  listenTo?: string;
  /** Called with data after a successful fetch (stable via ref). */
  onSuccess?: (data: unknown) => void;
  /** Called with the Error after a failed fetch (stable via ref). */
  onError?: (error: Error) => void;
  /** Initial value to use before the first fetch resolves. */
  initial?: unknown;
}

export interface UseApiResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface QueryConfig {
  command: string;
  params?: Record<string, unknown>;
}

export interface UseApiQueriesResult {
  data: unknown[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

// ── Internal helper: stable callback refs ──

function useStableRef<T>(value: T | undefined): React.MutableRefObject<T | undefined> {
  const ref = useRef(value);
  ref.current = value;
  return ref;
}

// ── Single-query hook ──────────────────────────────────────────────────

/**
 * Fetch a single Tauri backend resource with loading/error state.
 *
 * ```ts
 * const { data: settings, isLoading } = useApi<Settings>('get_settings');
 * const { data: products, refetch } = useApi<Product[]>('get_products',
 *   { includeInactive: false },
 *   { listenTo: 'product-updated' }
 * );
 * ```
 */
export function useApi<T = unknown>(
  command: string,
  params?: Record<string, unknown>,
  options?: UseApiOptions,
): UseApiResult<T> {
  const {
    enabled = true,
    listenTo,
    onSuccess,
    onError,
    initial = null,
  } = options ?? {};

  const [data, setData] = useState<T | null>(initial as T | null);
  const [isLoading, setIsLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);

  // Stable refs for callbacks so they don't cause re-fetch
  const onSuccessRef = useStableRef(onSuccess);
  const onErrorRef = useStableRef(onError);

  // Stable params key to avoid infinite loops when params object is re-created
  const paramsKey = useMemo(() => JSON.stringify(params ?? {}), [params]);

  const refetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await invoke<T>(command, params);
      setData(result);
      onSuccessRef.current?.(result);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
      onErrorRef.current?.(err instanceof Error ? err : new Error(msg));
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [command, paramsKey]);

  // Auto-fetch on mount (and when enabled flips from false → true)
  useEffect(() => {
    if (enabled) refetch();
  }, [enabled, refetch]);

  // Real-time event listener for auto-refresh
  useEffect(() => {
    if (!listenTo) return;
    let cancelled = false;
    const setup = async () => {
      const unlisten = await listen(listenTo, () => {
        if (!cancelled) refetch();
      });
      if (cancelled) unlisten();
      else return unlisten;
    };
    const unlistenPromise = setup();
    return () => {
      cancelled = true;
      unlistenPromise.then(fn => fn?.());
    };
  }, [listenTo, refetch]);

  return { data, isLoading, error, refetch };
}

// ── Batch query hook ──────────────────────────────────────────────────

/**
 * Fetch multiple Tauri backend resources in parallel with a combined
 * loading state and ordered results.
 *
 * ```ts
 * const { data: [settings, sales, ingredients], isLoading } = useApiQueries([
 *   { command: 'get_settings' },
 *   { command: 'get_sales' },
 *   { command: 'get_ingredients', params: { includeInactive: false } },
 * ]);
 * ```
 */
export function useApiQueries(
  queries: QueryConfig[],
  options?: {
    enabled?: boolean;
    listenTo?: string;
  },
): UseApiQueriesResult {
  const { enabled = true, listenTo } = options ?? {};

  const [data, setData] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(enabled && queries.length > 0);
  const [error, setError] = useState<string | null>(null);

  // Stable serialised queries key to avoid re-fetch loops
  const queriesKey = useMemo(
    () => JSON.stringify(queries.map(q => ({ command: q.command, params: q.params ?? {} }))),
    [queries],
  );

  const refetch = useCallback(async () => {
    if (queries.length === 0) {
      setData([]);
      setIsLoading(false);
      setError(null);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const parsed = JSON.parse(queriesKey) as { command: string; params: Record<string, unknown> }[];
      // Catch individual query rejections so one failing endpoint
      // (e.g. get_analytics on a fresh DB) doesn't crash the entire batch.
      // Failed queries return null — callers can check the data values.
      const results = await Promise.all(
        parsed.map(q =>
          invoke<unknown>(q.command, Object.keys(q.params).length > 0 ? q.params : undefined)
            .catch(() => null),
        ),
      );
      setData(results);
      setError(null);
    } catch (err) {
      // This should never fire since individual queries are caught above,
      // but keep it as a safety net for unexpected Promise.all failures.
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queriesKey]);

  // Auto-fetch on mount
  useEffect(() => {
    if (enabled && queries.length > 0) refetch();
  }, [enabled, refetch, queries.length]);

  // Real-time event listener for auto-refresh
  useEffect(() => {
    if (!listenTo) return;
    let cancelled = false;
    const setup = async () => {
      const unlisten = await listen(listenTo, () => {
        if (!cancelled) refetch();
      });
      if (cancelled) unlisten();
      else return unlisten;
    };
    const unlistenPromise = setup();
    return () => {
      cancelled = true;
      unlistenPromise.then(fn => fn?.());
    };
  }, [listenTo, refetch]);

  return { data, isLoading, error, refetch };
}
