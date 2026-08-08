import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderWithRouter, screen, waitFor, within } from '../test-utils';
import BranchOverview, {
  deriveBranchStatus,
  fleetSyncRate,
} from '../../app/pages/analytics/BranchOverview';
import type { BranchHealth } from '../../api';

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
const branch = (overrides: Partial<BranchHealth>): BranchHealth => ({
  id: 1,
  name: 'Downtown',
  code: 'BR001',
  node_id: 'N-A1',
  pos_type: 'pro',
  sync_enabled: true,
  online: true,
  connected_terminals: 2,
  ...overrides,
});

const BRANCHES: BranchHealth[] = [
  branch({ id: 1, name: 'Downtown', code: 'BR001', online: true, connected_terminals: 2 }),
  branch({ id: 2, name: 'Harbor', code: 'BR002', online: true, connected_terminals: 0 }),
  branch({ id: 3, name: 'Airport', code: 'BR003', online: false, connected_terminals: 0 }),
  branch({ id: 4, name: 'Mall', code: 'BR004', online: true, connected_terminals: 3 }),
];

const QUEUE = { pending: 12, failed: 3, total: 20, estimated_backlog_seconds: 24 };
const CONFLICTS = {
  pending: 2,
  resolved: 5,
  dismissed: 1,
  total: 8,
  by_entity_type: { sale: 2 },
};

const mockFetch = vi.fn();

function jsonOk(body: unknown): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

function stubEndpoints(overrides: {
  branches?: BranchHealth[];
  queue?: typeof QUEUE;
  conflicts?: typeof CONFLICTS;
  failBranches?: boolean;
} = {}) {
  const {
    branches = BRANCHES,
    queue = QUEUE,
    conflicts = CONFLICTS,
    failBranches = false,
  } = overrides;

  mockFetch.mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith('/api/dashboard/branches/health')) {
      if (failBranches) {
        return Promise.resolve(
          new Response(JSON.stringify({ error: 'Signal lost' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
          }),
        );
      }
      return jsonOk({ branches, total: branches.length });
    }
    if (url.endsWith('/api/dashboard/queue/summary')) return jsonOk(queue);
    if (url.endsWith('/api/dashboard/conflicts/stats')) return jsonOk(conflicts);
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

// ── Pure derivation helpers ──────────────────────────────────────────────

describe('deriveBranchStatus', () => {
  it('returns ONLINE for a connected branch with terminals', () => {
    expect(deriveBranchStatus(branch({ online: true, connected_terminals: 2 }))).toBe('ONLINE');
  });

  it('returns DEGRADED when connected but zero terminals', () => {
    expect(deriveBranchStatus(branch({ online: true, connected_terminals: 0 }))).toBe('DEGRADED');
  });

  it('returns DEGRADED when sync is disabled', () => {
    expect(
      deriveBranchStatus(branch({ online: true, connected_terminals: 2, sync_enabled: false })),
    ).toBe('DEGRADED');
  });

  it('returns OFFLINE when not connected', () => {
    expect(deriveBranchStatus(branch({ online: false }))).toBe('OFFLINE');
  });
});

describe('fleetSyncRate', () => {
  it('computes the online percentage', () => {
    expect(fleetSyncRate(BRANCHES)).toBeCloseTo(75.0, 1);
  });

  it('returns 0 for an empty fleet', () => {
    expect(fleetSyncRate([])).toBe(0);
  });
});

// ── Page rendering ────────────────────────────────────────────────────────

describe('BranchOverview page', () => {
  it('renders the ASCII header and roster states', async () => {
    renderWithRouter(<BranchOverview />);

    await waitFor(() => {
      expect(screen.getByText('[ BRANCH OVERVIEW ]')).toBeInTheDocument();
    });

    const roster = await screen.findByTestId('telemetry-roster');
    await waitFor(() => {
      expect(within(roster).getAllByText('ONLINE')).toHaveLength(2);
      expect(within(roster).getByText('DEGRADED')).toBeInTheDocument();
      expect(within(roster).getByText('OFFLINE')).toBeInTheDocument();
    });
    expect(within(roster).getByText(/BR001/)).toBeInTheDocument();
    expect(within(roster).getByText(/BR004/)).toBeInTheDocument();
  });

  it('renders the fleet sync-rate hero', async () => {
    renderWithRouter(<BranchOverview />);

    const rate = await screen.findByTestId('telemetry-rate');
    await waitFor(() => {
      // 3 of 4 branches online → 75.0
      expect(rate).toHaveTextContent('75.0');
    });
  });

  it('renders the stat strip from queue + conflict endpoints', async () => {
    renderWithRouter(<BranchOverview />);

    const stats = await screen.findByTestId('telemetry-stats');
    await waitFor(() => {
      expect(within(stats).getByText('QUEUED')).toBeInTheDocument();
      expect(within(stats).getByText('12')).toBeInTheDocument();
      expect(within(stats).getByText('CONFLICTS')).toBeInTheDocument();
      expect(within(stats).getByText('2')).toBeInTheDocument();
      expect(within(stats).getByText('OFFLINE')).toBeInTheDocument();
      expect(within(stats).getByText('1')).toBeInTheDocument();
    });
  });

  it('filters the roster to ONLINE only', async () => {
    renderWithRouter(<BranchOverview />);

    const onlineTab = await screen.findByRole('tab', { name: /ONLINE/ });
    onlineTab.click();

    const roster = await screen.findByTestId('telemetry-roster');
    await waitFor(() => {
      expect(within(roster).getAllByText('ONLINE')).toHaveLength(2);
      expect(within(roster).queryByText('DEGRADED')).not.toBeInTheDocument();
      expect(within(roster).queryByText('OFFLINE')).not.toBeInTheDocument();
    });
  });

  it('filters the roster to ALERT (degraded + offline)', async () => {
    renderWithRouter(<BranchOverview />);

    const alertTab = await screen.findByRole('tab', { name: /ALERT/ });
    alertTab.click();

    const roster = await screen.findByTestId('telemetry-roster');
    await waitFor(() => {
      expect(within(roster).queryByText('ONLINE')).not.toBeInTheDocument();
      expect(within(roster).getByText('DEGRADED')).toBeInTheDocument();
      expect(within(roster).getByText('OFFLINE')).toBeInTheDocument();
    });
  });

  it('shows the empty state when no branches are registered', async () => {
    stubEndpoints({ branches: [] });
    renderWithRouter(<BranchOverview />);

    await waitFor(() => {
      expect(screen.getByText(/NO BRANCHES REGISTERED/)).toBeInTheDocument();
    });
  });

  it('shows the link-error banner with a retry when health fails', async () => {
    stubEndpoints({ failBranches: true });
    renderWithRouter(<BranchOverview />);

    await waitFor(() => {
      expect(screen.getByText(/LINK ERROR/)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /RETRY LINK/ })).toBeInTheDocument();
    });
  });
});
