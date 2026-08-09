import { useEffect, useState } from 'react';

/**
 * Shared debounced-search hook.
 *
 * Mirrors the AJAX-style pattern currently used across Customers, Suppliers,
 * ProductManager, and Sale: a 250 ms debounce on the text input plus an
 * `isPending` flag so callers can render a spinner during the wait. Centralising
 * the implementation here keeps the four pages in lockstep and makes the
 * behaviour unit-testable.
 *
 * @param options.delayMs   ms to wait after the last keystroke before flushing
 *                          the debounced value. Defaults to 250.
 * @param options.initial   starting value (defaults to `''`).
 *
 * @returns
 *   - `query`           — current input value (immediate, controlled)
 *   - `setQuery`        — setter for `query`
 *   - `debouncedQuery`  — input value, updated after `delayMs` of idle time
 *   - `isPending`       — `true` while the debounce timer is armed
 *
 * The hook is stable across renders: `setQuery` keeps the same identity unless
 * the component re-creates the hook.
 */
export interface UseDebouncedSearchOptions {
  delayMs?: number;
  initial?: string;
}

export interface UseDebouncedSearchResult {
  query: string;
  setQuery: (value: string) => void;
  debouncedQuery: string;
  isPending: boolean;
}

export function useDebouncedSearch(
  options: UseDebouncedSearchOptions = {},
): UseDebouncedSearchResult {
  const { delayMs = 250, initial = '' } = options;

  const [query, setQuery] = useState<string>(initial);
  const [debouncedQuery, setDebouncedQuery] = useState<string>(initial);
  const [isPending, setIsPending] = useState<boolean>(false);

  useEffect(() => {
    // No work if the value has not changed since the last flush; the timer
    // itself is responsible for clearing `isPending` once it fires.
    if (query === debouncedQuery) return;
    setIsPending(true);
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
      setIsPending(false);
    }, delayMs);
    return () => clearTimeout(timer);
  }, [query, debouncedQuery, delayMs]);

  return { query, setQuery, debouncedQuery, isPending };
}
