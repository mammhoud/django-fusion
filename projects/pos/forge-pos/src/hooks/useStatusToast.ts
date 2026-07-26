import { useState, useEffect, useCallback } from 'react';

/**
 * Shared status-toast hook.
 *
 * Mirrors the AJAX-style error-surfacing pattern (previously inline boilerplate
 * in each page). Returns the current toast entry plus typed helpers that pages
 * call from catch blocks. The toast auto-dismisses after `durationMs` (default
 * 4 s) and can also be dismissed manually via the returned `dismiss` callback,
 * which is wired to the toast's click handler.
 *
 * Each page still renders `StatusToast` (from `src/components/StatusToast.tsx`)
 * directly with the returned `status` and `dismiss`. The component handles
 * enter/exit animation via framer-motion AnimatePresence.
 *
 * Usage:
 *   const { status, showSuccess, showError, dismiss } = useStatusToast();
 *   // ... in a catch:
 *   showError(t('sale.errorCompleteSale'));
 *   // ... in JSX:
 *   <StatusToast
 *     type={status?.type ?? 'success'}
 *     message={status?.message ?? ''}
 *     visible={!!status}
 *     onDismiss={dismiss}
 *   />
 */
export type StatusToastType = 'success' | 'error';

export interface StatusToastEntry {
  type: StatusToastType;
  message: string;
}

export interface UseStatusToastOptions {
  /** Auto-dismiss duration in milliseconds. Defaults to 4000. */
  durationMs?: number;
}

export interface UseStatusToastResult {
  status: StatusToastEntry | null;
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  dismiss: () => void;
}

const DEFAULT_DURATION_MS = 4000;

export function useStatusToast(
  options: UseStatusToastOptions = {},
): UseStatusToastResult {
  const { durationMs = DEFAULT_DURATION_MS } = options;
  const [status, setStatus] = useState<StatusToastEntry | null>(null);

  const dismiss = useCallback(() => setStatus(null), []);

  const showSuccess = useCallback(
    (message: string) => setStatus({ type: 'success', message }),
    [],
  );
  const showError = useCallback(
    (message: string) => setStatus({ type: 'error', message }),
    [],
  );

  useEffect(() => {
    if (!status) return;
    const timer = setTimeout(() => setStatus(null), durationMs);
    return () => clearTimeout(timer);
  }, [status, durationMs]);

  return { status, showSuccess, showError, dismiss };
}
