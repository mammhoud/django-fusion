import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderWithRouter, screen, waitFor, within } from '../test-utils';
import CloudDashboard from '../../app/pages/analytics/CloudDashboard';

// ── WS client is best-effort — stub it so tests never open a socket ──────
vi.mock('../../../api', async importOriginal => {
  const actual = await importOriginal<typeof import('../../api')>();
  return {
    ...actual,
    createSyncEventsWs: () => ({
      open: false,
      send: () => true,
      close: () => undefined,
    }),
  };
});

// ── Fixtures ──────────────────────────────────────────────────────────────
const QUEUE_SUMMARY = { pending: 1, failed: 1, total: 3, estimated_backlog_seconds: 2 };
const QUEUE_ITEMS = [
  {
    id: 1, branch: 'Downtown', branch_code: 'BR001', entity_type: 'products',
    operation: 'update', status: 'pending', attempt_count: 0, max_attempts: 5,
    last_error: '', created_at: '2026-08-15T00:00:00Z', next_retry_at: null,
  },
  {
    id: 2, branch: 'Harbor', branch_code: 'BR002', entity_type: 'sales',
    operation: 'sync_request', status: 'failed', attempt_count: 5, max_attempts: 5,
    last_error: 'Max attempts exceeded', created_at: '2026-08-15T00:00:00Z', next_retry_at: null,
  },
];
const CONFLICTS = [
  {
    id: 10, branch: 'Downtown', branch_code: 'BR001', node_id: 'N-A1',
    entity_type: 'products', entity_id: 'p1', resolver_used: 'auto',
    reason: 'price mismatch',
    conflict_fields: [{ field: 'price', local_value: 10, remote_value: 12 }],
    local_data: { price: 10 }, remote_data: { price: 12 },
    created_at: '2026-08-15T00:00:00Z',
  },
];
const ACTIVITY = [
  {
    id: 100, branch: 'Downtown', branch_code: 'BR001', node_id: 'N-A1',
    entity_type: 'products', entity_count: 3, status: 'processed',
    error_message: '', received_at: '2026-08-15T00:00:00Z',
  },
];

const mockFetch = vi.fn();

function jsonOk(body: unknown): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

function stubEndpoints(overrides: { queueItems?: typeof QUEUE_ITEMS; conflicts?: typeof CONFLICTS } = {}) {
  const { queueItems = QUEUE_ITEMS, conflicts = CONFLICTS } = overrides;
  mockFetch.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = (init?.method ?? 'GET').toUpperCase();

    if (url.endsWith('/api/dashboard/queue/summary')) return jsonOk(QUEUE_SUMMARY);
    if (url.endsWith('/api/dashboard/queue/list/pending')) return jsonOk({ items: queueItems, count: queueItems.length });
    if (url.endsWith('/api/dashboard/conflicts')) return jsonOk({ conflicts, count: conflicts.length });
    if (url.startsWith('/api/dashboard/activity')) return jsonOk({ entries: ACTIVITY });

    // Mutation endpoints (retry/cancel/resolve/dismiss) return success.
    if (method === 'POST') {
      if (url.includes('/resolve')) return jsonOk({ status: 'resolved', conflict_id: 10, resolution: 'use_remote' });
      if (url.includes('/dismiss')) return jsonOk({ status: 'dismissed', conflict_id: 10 });
      if (url.includes('/retry')) return jsonOk({ status: 'retry_scheduled', item_id: 2, next_retry_at: null });
      if (url.includes('/cancel')) return jsonOk({ status: 'cancelled', item_id: 1 });
    }
    return jsonOk({});
  });
}

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch);
  stubEndpoints();
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

describe('CloudDashboard page', () => {
  it('renders the header and summary strip', async () => {
    renderWithRouter(<CloudDashboard />);

    await waitFor(() => {
      expect(screen.getByText('[ CLOUD DASHBOARD ]')).toBeInTheDocument();
    });
    expect(screen.getByText('[ SYNC QUEUE ]')).toBeInTheDocument();
    expect(screen.getByText('[ CONFLICTS ]')).toBeInTheDocument();
    expect(screen.getByText('[ RECENT ACTIVITY ]')).toBeInTheDocument();
  });

  it('renders queue items with status and the right actions', async () => {
    renderWithRouter(<CloudDashboard />);

    const queue = await screen.findByTestId('cloud-queue');
    await waitFor(() => {
      expect(within(queue).getByText(/products \/ update/i)).toBeInTheDocument();
      expect(within(queue).getByText('PENDING')).toBeInTheDocument();
      expect(within(queue).getByText('FAILED')).toBeInTheDocument();
    });
    // Failed → retry; pending → cancel.
    expect(within(queue).getByTestId('retry-2')).toBeInTheDocument();
    expect(within(queue).getByTestId('cancel-1')).toBeInTheDocument();
  });

  it('renders conflicts with resolve + dismiss actions', async () => {
    renderWithRouter(<CloudDashboard />);

    const conflicts = await screen.findByTestId('cloud-conflicts');
    await waitFor(() => {
      expect(within(conflicts).getByText(/products#p1/i)).toBeInTheDocument();
      expect(within(conflicts).getByText(/price: 10 → 12/)).toBeInTheDocument();
    });
    expect(within(conflicts).getByTestId('resolve-local-10')).toBeInTheDocument();
    expect(within(conflicts).getByTestId('resolve-remote-10')).toBeInTheDocument();
    expect(within(conflicts).getByTestId('resolve-merge-10')).toBeInTheDocument();
    expect(within(conflicts).getByTestId('dismiss-10')).toBeInTheDocument();
  });

  it('renders the activity feed', async () => {
    renderWithRouter(<CloudDashboard />);

    const activity = await screen.findByTestId('cloud-activity');
    await waitFor(() => {
      expect(within(activity).getByText(/products × 3/i)).toBeInTheDocument();
      expect(within(activity).getByText(/processed/)).toBeInTheDocument();
    });
  });

  it('POSTs a retry when the retry button is clicked', async () => {
    renderWithRouter(<CloudDashboard />);

    const retry = await screen.findByTestId('retry-2');
    retry.click();

    await waitFor(() => {
      const retryCalls = mockFetch.mock.calls.filter(
        ([input]) => String(input).endsWith('/api/dashboard/queue/retry/2'),
      );
      expect(retryCalls.length).toBeGreaterThan(0);
      expect((retryCalls[0][1] as RequestInit).method).toBe('POST');
    });
  });

  it('POSTs a dismiss when the dismiss button is clicked', async () => {
    renderWithRouter(<CloudDashboard />);

    const dismiss = await screen.findByTestId('dismiss-10');
    dismiss.click();

    await waitFor(() => {
      const dismissCalls = mockFetch.mock.calls.filter(
        ([input]) => String(input).endsWith('/api/dashboard/conflicts/10/dismiss'),
      );
      expect(dismissCalls.length).toBeGreaterThan(0);
      expect((dismissCalls[0][1] as RequestInit).method).toBe('POST');
    });
  });

  it('shows empty states when there is nothing to manage', async () => {
    stubEndpoints({ queueItems: [], conflicts: [] });
    renderWithRouter(<CloudDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/NO PENDING ITEMS/)).toBeInTheDocument();
      expect(screen.getByText(/NO PENDING CONFLICTS/)).toBeInTheDocument();
    });
  });
});
