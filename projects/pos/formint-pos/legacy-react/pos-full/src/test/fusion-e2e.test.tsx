/**
 * End-to-end test: full fragment-rendering flow.
 *
 * Tests the complete chain end-to-end with realistic mock data matching
 * the sidecar template format:
 *
 *   sidecar (/fusion/health + /fusion/render/*)
 *   → FusionStore (caching preference)
 *   → FusionMiddleware (mode context)
 *   → FusionPage (fragment vs data decision)
 *   → FusionProxy (fetch & render HTML via dangerouslySetInnerHTML)
 *
 * Coverage:
 *   - Fragment mode: health check → fragment fetch → HTML render
 *   - Data mode: health check → false → children with data
 *   - Fragment failure → fallbackToData → data mode
 *   - Standalone mode (no middleware)
 *   - FusionProxy directly with realistic template HTML
 *   - Unmount cleanup prevents state updates
 */
import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fusionStore } from '../lib/fusion-store';
import { FusionMiddleware } from '../components/FusionMiddleware';
import { FusionPage } from '../components/FusionPage';
import { FusionProxy } from '../components/FusionProxy';

// ═══════════════════════════════════════════════════════════════════
// Realistic mock fragment HTML — mirrors sidecar template format
// ═══════════════════════════════════════════════════════════════════

/** Dashboard fragment replicating ``fusion_fragments.py:_DASHBOARD_FRAGMENT_TEMPLATE`` output. */
const DASHBOARD_FRAGMENT_HTML = [
  '<div class="fusion-fragment" data-fragment-name="dashboard">',
  '  <div class="flex items-center gap-3 mb-6">',
  '    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold">F</div>',
  '    <div>',
  '      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Forge POS</h1>',
  '      <p class="text-sm text-slate-500 dark:text-slate-400">Dashboard</p>',
  '    </div>',
  '  </div>',
  '  <div class="grid grid-cols-4 gap-4">',
  '    <div class="card--glass rounded-xl p-4 text-center">',
  '      <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400" data-testid="e2e-product-count">42</div>',
  '      <div class="text-xs text-slate-500 mt-1">Products</div>',
  '    </div>',
  '    <div class="card--glass rounded-xl p-4 text-center">',
  '      <div class="text-2xl font-bold text-emerald-600 dark:text-emerald-400" data-testid="e2e-customer-count">128</div>',
  '      <div class="text-xs text-slate-500 mt-1">Customers</div>',
  '    </div>',
  '    <div class="card--glass rounded-xl p-4 text-center">',
  '      <div class="text-2xl font-bold text-amber-600 dark:text-amber-400" data-testid="e2e-employee-count">15</div>',
  '      <div class="text-xs text-slate-500 mt-1">Employees</div>',
  '    </div>',
  '    <div class="card--glass rounded-xl p-4 text-center">',
  '      <div class="text-2xl font-bold text-rose-600 dark:text-rose-400" data-testid="e2e-sale-count">890</div>',
  '      <div class="text-xs text-slate-500 mt-1">Sales</div>',
  '    </div>',
  '  </div>',
  '</div>',
].join('\n');

/** Suppliers fragment replicating ``fusion_fragments.py:_SUPPLIERS_FRAGMENT_TEMPLATE`` output. */
const SUPPLIERS_FRAGMENT_HTML = [
  '<div class="fusion-fragment" data-fragment-name="suppliers">',
  '  <h2 class="text-lg font-semibold mb-3" data-testid="e2e-suppliers-count">Suppliers (3)</h2>',
  '  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">',
  '    <div class="card--glass rounded-xl p-3 flex items-start gap-3">',
  '      <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 text-lg font-bold">A</div>',
  '      <div class="min-w-0">',
  '        <div class="font-semibold text-slate-900 dark:text-white text-sm truncate" data-testid="e2e-supplier-name">Acme Foods</div>',
  '        <div class="text-xs text-slate-500 truncate">John Acme</div>',
  '        <div class="text-xs text-slate-400 truncate">+1-555-0100</div>',
  '      </div>',
  '    </div>',
  '    <div class="card--glass rounded-xl p-3 flex items-start gap-3">',
  '      <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 text-lg font-bold">B</div>',
  '      <div class="min-w-0">',
  '        <div class="font-semibold text-slate-900 dark:text-white text-sm truncate">Best Produce</div>',
  '        <div class="text-xs text-slate-500 truncate">Sarah Best</div>',
  '      </div>',
  '    </div>',
  '  </div>',
  '</div>',
].join('\n');

// ═══════════════════════════════════════════════════════════════════
// Mock health-check responses matching sidecar JSON format
// ═══════════════════════════════════════════════════════════════════

const HEALTH_CHECK_TRUE = {
  fusion_render_first: true,
  reason: 'device_role: admin',
  token_present: true,
};

const HEALTH_CHECK_FALSE = {
  fusion_render_first: false,
  reason: 'device_role: cashier',
  token_present: true,
};

// ═══════════════════════════════════════════════════════════════════
// Shared test fixtures
// ═══════════════════════════════════════════════════════════════════

const TEST_DATA = { page: 'dashboard', stats: { products: 42 } };
const FRAGMENT_URL = 'http://127.0.0.1:8766/fusion/render/dashboard';

function TestChild({ data }: { data: unknown }) {
  return <div data-testid="e2e-data-content">{data ? 'Data mode rendered' : 'No data'}</div>;
}

// ═══════════════════════════════════════════════════════════════════
// E2E: Full fragment-rendering flow
// ═══════════════════════════════════════════════════════════════════

describe('E2E: Full fragment-rendering flow', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    await fusionStore.clearSession();
  });

  // ── 1. Fragment mode full chain ──────────────────────────────────

  describe('1. Fragment mode — health check → fragment → HTML render', () => {
    it('renders dashboard stats from server-rendered fragment HTML', async () => {
      // Step 1: Health check returns true (fragment mode enabled)
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(HEALTH_CHECK_TRUE),
      } as Response);

      // Step 2: Fragment endpoint returns realistic HTML
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(DASHBOARD_FRAGMENT_HTML),
      } as Response);

      // Simulate startup health check (as done in main.tsx)
      await fusionStore.initFromHealthCheck();

      // Verify preference was cached
      const pref = await fusionStore.getSessionPreference();
      expect(pref).toBe(true);

      // Render the full component chain
      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL} data={TEST_DATA}>
            {(data, _fb) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );

      // Assert fragment HTML is rendered with correct data values
      await waitFor(() => {
        expect(screen.getByTestId('e2e-product-count')).toHaveTextContent('42');
        expect(screen.getByTestId('e2e-customer-count')).toHaveTextContent('128');
        expect(screen.getByTestId('e2e-employee-count')).toHaveTextContent('15');
        expect(screen.getByTestId('e2e-sale-count')).toHaveTextContent('890');
      });
    });

    it('wraps fragment in fusion-fragment div with correct data-fragment-name', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(HEALTH_CHECK_TRUE),
      } as Response);

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(DASHBOARD_FRAGMENT_HTML),
      } as Response);

      await fusionStore.initFromHealthCheck();

      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL} data={TEST_DATA}>
            {(data, _fb) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );

      await waitFor(() => {
        const el = document.querySelector('.fusion-fragment');
        expect(el).toBeInTheDocument();
        expect(el).toHaveAttribute('data-fragment-name', 'dashboard');
      });
    });

    it('sends Accept: text/html header when fetching fragment', async () => {
      let capturedInit: RequestInit | undefined;

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(HEALTH_CHECK_TRUE),
      } as Response);

      vi.mocked(fetch).mockImplementationOnce(async (_input, init) => {
        capturedInit = init as RequestInit;
        return {
          ok: true,
          text: () => Promise.resolve(DASHBOARD_FRAGMENT_HTML),
        } as Response;
      });

      await fusionStore.initFromHealthCheck();

      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL} data={TEST_DATA}>
            {(data, _fb) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );

      await waitFor(() => {
        expect(screen.getByTestId('e2e-product-count')).toBeInTheDocument();
      });

      expect(capturedInit?.headers).toEqual({ Accept: 'text/html' });
    });
  });

  // ── 2. Data mode full chain ──────────────────────────────────────

  describe('2. Data mode — health check returns false', () => {
    it('renders children with data when fragment mode is disabled', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(HEALTH_CHECK_FALSE),
      } as Response);

      await fusionStore.initFromHealthCheck();

      const pref = await fusionStore.getSessionPreference();
      expect(pref).toBe(false);

      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL} data={TEST_DATA}>
            {(data, _fb) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );

      await waitFor(() => {
        expect(screen.getByTestId('e2e-data-content')).toHaveTextContent('Data mode rendered');
      });
    });
  });

  // ── 3. Fragment failure → fallback ───────────────────────────────

  describe('3. Fragment failure — error → fallback to data mode', () => {
    it('falls back to data mode when fragment fetch fails with network error', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(HEALTH_CHECK_TRUE),
      } as Response);

      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

      await fusionStore.initFromHealthCheck();

      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL} data={TEST_DATA}>
            {(data, _fb) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );

      // FusionProxy should show error state first, then fallbackToData
      // switches to data mode which renders the TestChild
      await waitFor(() => {
        expect(screen.getByTestId('e2e-data-content')).toHaveTextContent('Data mode rendered');
      });
    });

    it('falls back to data mode when fragment returns 500 status', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(HEALTH_CHECK_TRUE),
      } as Response);

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: () => Promise.resolve('Internal server error'),
      } as Response);

      await fusionStore.initFromHealthCheck();

      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL} data={TEST_DATA}>
            {(data, _fb) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );

      await waitFor(() => {
        expect(screen.getByTestId('e2e-data-content')).toHaveTextContent('Data mode rendered');
      });
    });
  });

  // ── 4. Standalone mode ───────────────────────────────────────────

  describe('4. Standalone mode — direct data rendering', () => {
    it('renders children with data in standalone mode', () => {
      render(
        <FusionPage standalone data={TEST_DATA}>
          {(data, _fb) => <TestChild data={data} />}
        </FusionPage>,
      );

      expect(screen.getByTestId('e2e-data-content')).toHaveTextContent('Data mode rendered');
    });

    it('renders error state when error is provided', () => {
      render(
        <FusionPage standalone data={undefined} error={new Error('Failed')}>
          {(data, _fb) => <TestChild data={data} />}
        </FusionPage>,
      );

      expect(screen.getByText(/Unable to load page content/i)).toBeInTheDocument();
    });

    it('renders loading skeleton when isLoading is true', () => {
      const { container } = render(
        <FusionPage standalone data={undefined} isLoading skeletonVariant="card">
          {(data, _fb) => <TestChild data={data} />}
        </FusionPage>,
      );

      expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
    });
  });

  // ── 5. FusionProxy directly with supplier HTML ───────────────────

  describe('5. FusionProxy — renders supplier HTML from sidecar format', () => {
    it('renders supplier names and contact info from fragment HTML', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(SUPPLIERS_FRAGMENT_HTML),
      } as Response);

      render(
        <FusionProxy
          fragmentUrl="http://127.0.0.1:8766/fusion/render/suppliers"
          onError={() => {}}
        />,
      );

      await waitFor(() => {
        expect(screen.getByTestId('e2e-suppliers-count')).toHaveTextContent('Suppliers (3)');
        expect(screen.getByTestId('e2e-supplier-name')).toHaveTextContent('Acme Foods');
      });
    });
  });

  // ── 6. Unmount cleanup ───────────────────────────────────────────

  describe('6. Unmount — cleanup prevents state updates', () => {
    it('does not set state after unmount while fetch is in flight', async () => {
      let resolvePromise!: (value: Response) => void;
      const delayedPromise = new Promise<Response>((resolve) => {
        resolvePromise = resolve;
      });

      vi.mocked(fetch).mockReturnValue(delayedPromise);

      const { unmount } = render(
        <FusionProxy fragmentUrl={FRAGMENT_URL} onError={vi.fn()} />,
      );

      // Unmount while fetch is in flight
      unmount();

      // Resolve the fetch after unmount
      await act(async () => {
        resolvePromise!({
          ok: true,
          text: () => Promise.resolve(DASHBOARD_FRAGMENT_HTML),
        } as Response);
        // Wait for microtasks
        await new Promise((r) => setTimeout(r, 10));
      });

      // Fragment HTML should NOT appear since component was unmounted
      expect(screen.queryByTestId('e2e-product-count')).not.toBeInTheDocument();
    });
  });

  // ── 7. FusionStore initFromHealthCheck failure ───────────────────

  describe('7. Health check — fetch failures handled gracefully', () => {
    it('returns false when /fusion/health returns non-ok status', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response);

      const result = await fusionStore.initFromHealthCheck();
      expect(result).toBe(false);
    });

    it('returns false when /fusion/health network request fails', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Connection refused'));

      const result = await fusionStore.initFromHealthCheck();
      expect(result).toBe(false);
    });
  });
});
