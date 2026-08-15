import { useEffect, useState } from 'react';
import { createClient, getMonitorStatus, type MonitorStatus } from '@formints/client';

/** Health state the hook returns after the on-mount probe. */
export interface HealthState {
  /** The probe has not yet completed. */
  idle: boolean;
  /** The server responded successfully. */
  healthy: boolean;
  /** The last-known MonitorStatus payload, if the probe succeeded. */
  status: MonitorStatus | null;
  /** Error message if the probe failed. */
  error: string | null;
}

/**
 * Probe a Formints API server on mount using ``@formints/client``.
 *
 * Community is offline-first — the probe fails gracefully and reports
 * ``healthy: false`` when no server is reachable.  Pass ``baseUrl`` to
 * target a Standard or Cloud instance; omit it (or pass an empty string)
 * to skip the HTTP probe entirely (idle-only, no fetch).
 *
 * Usage in AppShell::
 *
 *   const health = useHealthCheck('http://127.0.0.1:8767');
 */
export function useHealthCheck(baseUrl?: string): HealthState {
  const [state, setState] = useState<HealthState>({
    idle: true,
    healthy: false,
    status: null,
    error: null,
  });

  useEffect(() => {
    if (!baseUrl) {
      setState({ idle: false, healthy: false, status: null, error: null });
      return;
    }

    let cancelled = false;
    const client = createClient(baseUrl);

    getMonitorStatus(client)
      .then((status) => {
        if (!cancelled) {
          setState({ idle: false, healthy: true, status, error: null });
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setState({
            idle: false,
            healthy: false,
            status: null,
            error: err instanceof Error ? err.message : String(err),
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [baseUrl]);

  return state;
}
