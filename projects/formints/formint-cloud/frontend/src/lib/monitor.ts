/**
 * Cloud Backup Monitor API
 * =========================
 * Typed wrapper over the `@formints/client` monitor module
 * (`createClient` + `getMonitorStatus`). Produces a small
 * `monitorApi(baseUrl)` surface used by the telemetry page to render
 * database status, last backup, and sync-queue depth.
 *
 * Usage:
 *   import { monitorApi } from '../lib/monitor';
 *
 *   const api = monitorApi('http://127.0.0.1:8767');
 *   const status = await api.status();
 *   // → { database: 'ok', last_backup: {...} | null, sync_queue_depth: 2 }
 */

import { createClient, getMonitorStatus } from '@formints/client';
import type { MonitorStatus } from '@formints/client';

/** Default sidecar/monitor base URL — same default as the sidecar client. */
export const MONITOR_BASE =
  (import.meta.env?.VITE_SIDECAR_URL as string | undefined) || 'http://127.0.0.1:8767';

export interface MonitorApi {
  /** GET /monitor/status — db reachability, last backup, queue depth. */
  status: () => Promise<MonitorStatus>;
}

/** Build a typed monitor API client for *baseUrl*. */
export function monitorApi(baseUrl: string = MONITOR_BASE): MonitorApi {
  const client = createClient(baseUrl);
  return {
    status: () => getMonitorStatus(client),
  };
}
