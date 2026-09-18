import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderWithRouter, screen, waitFor } from '../test-utils';
import CloudMonitorTile, { deriveDatabaseState } from '../../app/pages/analytics/CloudMonitorTile';
import type { MonitorStatus } from '@formints/client';

// ── fetch stub ─────────────────────────────────────────────────────────────

const mockFetch = vi.fn();
const jsonOk = (body: unknown) =>
  Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  );

const MONITOR: MonitorStatus = {
  database: 'ok',
  last_backup: {
    filename: 'pos_cloud-20260809-120000.db',
    status: 'success',
    size_bytes: 128,
    started_at: '2026-08-09T12:00:00Z',
  },
  sync_queue_depth: 2,
};

function stubMonitor(payload: unknown) {
  mockFetch.mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith('/monitor/status')) return jsonOk(payload);
    return jsonOk({});
  });
}

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

// ── Pure derivation helper ────────────────────────────────────────────────

describe('deriveDatabaseState', () => {
  it('returns OK for a healthy database', () => {
    expect(deriveDatabaseState({ database: 'ok', last_backup: null, sync_queue_depth: 0 })).toBe('OK');
  });

  it('returns ERROR for an unreachable database', () => {
    expect(
      deriveDatabaseState({ database: 'error', last_backup: null, sync_queue_depth: 0 }),
    ).toBe('ERROR');
  });

  it('returns AWAITING before any response', () => {
    expect(deriveDatabaseState(null)).toBe('AWAITING');
  });
});

// ── Component ──────────────────────────────────────────────────────────────

describe('CloudMonitorTile', () => {
  it('renders db status, last backup, and queue depth', async () => {
    stubMonitor(MONITOR);
    renderWithRouter(<CloudMonitorTile />);

    await waitFor(() => {
      expect(screen.getByText('OK')).toBeTruthy();
    });
    expect(screen.getByText('pos_cloud-20260809-120000.db')).toBeTruthy();
    expect(screen.getByTestId('cloud-monitor-queue').textContent).toContain('2');
  });

  it('renders an empty state when no backups exist', async () => {
    stubMonitor({ database: 'ok', last_backup: null, sync_queue_depth: 0 });
    renderWithRouter(<CloudMonitorTile />);

    await waitFor(() => {
      expect(screen.getByText(/NONE \/ NOT RECORDED/)).toBeTruthy();
    });
    expect(screen.getByTestId('cloud-monitor-queue').textContent).toContain('0');
  });

  it('renders NO SIGNAL when the monitor endpoint fails', async () => {
    mockFetch.mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/monitor/status')) {
        return Promise.resolve(
          new Response(JSON.stringify({ error: 'down' }), { status: 503 }),
        );
      }
      return jsonOk({});
    });
    renderWithRouter(<CloudMonitorTile />);

    await waitFor(() => {
      expect(screen.getByText(/NO SIGNAL/)).toBeTruthy();
    });
    expect(screen.getByText(/LINK ERROR/)).toBeTruthy();
  });
});
