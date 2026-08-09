import type { FormintsClient } from './core';

export interface MonitorStatus {
  database: 'ok' | 'error';
  last_backup: { filename: string; status: string; size_bytes: number | null; started_at: string } | null;
  sync_queue_depth: number;
}

export async function getMonitorStatus(client: FormintsClient): Promise<MonitorStatus> {
  return client.request('/monitor/status');
}
