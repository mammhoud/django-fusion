/**
 * Unit tests for FusionPage.
 *
 * Covers:
 * - Middleware mode: renders FusionProxy when mode=fragment
 * - Middleware mode: renders data content when mode=data
 * - Standalone mode: reads session preference directly and renders FusionProxy
 * - Standalone mode: renders data content when no session pref
 * - RTK Query error state shows ErrorState
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { FusionPage } from '@/components/FusionPage';
import { FusionMiddleware } from '@/components/FusionMiddleware';

// ═══════════════════════════════════════════════════════════════════
// Mock the RTK Query hooks used by FusionPage
// ═══════════════════════════════════════════════════════════════════

const mockUseGetPageDataQuery = vi.fn();

vi.mock('@/store/api/endpoints/pages', () => ({
  useGetPageDataQuery: (...args: unknown[]) => mockUseGetPageDataQuery(...args),
  useGetPageFragmentQuery: vi.fn(),
  useGetPageQuery: vi.fn(),
  useGetPageHtmlQuery: vi.fn(),
}));

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <Provider store={createTestStore()}>
      {ui}
    </Provider>,
  );
}

function TestChild({ page }: { page: unknown }) {
  return (
    <div data-testid="page-content">
      {page ? 'Page data loaded' : 'No data'}
    </div>
  );
}

// Valid codec-encoded payload that decodes to: {"blocks":[],"title":"Test","slug":"home"}
const VALID_ENCODED =
  'fusion_v1:eyJibG9ja3MiOltdLCJ0aXRsZSI6IlRlc3QiLCJzbHVnIjoiaG9tZSJ9';

// Encoded payload for a page with a title (used as CmsPage mock)
const PAGE_ENCODED =
  'fusion_v1:eyJibG9ja3MiOltdLCJ0aXRsZSI6IkhvbWUgUGFnZSIsInNsdWciOiJob21lIn0';

// Valid encoded payload where the decoded result is truthy
const TRUTHY_ENCODED =
  'fusion_v1:eyJ0ZXN0Ijp0cnVlfQ';

// ═══════════════════════════════════════════════════════════════════
// Middleware mode
// ═══════════════════════════════════════════════════════════════════

describe('FusionPage — middleware mode', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('renders FusionProxy in fragment mode when wrapped with middleware in fragment mode', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () =>
        Promise.resolve('<div data-testid="fragment-html">Server rendered</div>'),
    } as Response);

    sessionStorage.setItem('fusion_render_first', 'true');

    await act(async () => {
      renderWithProviders(
        <FusionMiddleware>
          <FusionPage slug="home">
            {(page, _fallback) => <TestChild page={page} />}
          </FusionPage>
        </FusionMiddleware>,
      );
    });

    // Wait for FusionProxy to fetch and render
    await vi.waitFor(() => {
      expect(screen.getByTestId('fragment-html')).toHaveTextContent(
        'Server rendered',
      );
    });
  });

  it('renders data content when middleware mode=data', async () => {
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: VALID_ENCODED },
      isLoading: false,
      error: undefined,
    });

    await act(async () => {
      renderWithProviders(
        <FusionMiddleware initialMode="data">
          <FusionPage slug="home">
            {(page, _fallback) => <TestChild page={page} />}
          </FusionPage>
        </FusionMiddleware>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('page-content')).toHaveTextContent(
        'Page data loaded',
      );
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// Standalone mode
// ═══════════════════════════════════════════════════════════════════

describe('FusionPage — standalone mode', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('renders data content when no session pref is set', async () => {
    // FusionPageStandalone goes to data mode → FusionPageDataInner → useGetPageDataQuery
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: PAGE_ENCODED },
      isLoading: false,
      error: undefined,
    });

    await act(async () => {
      renderWithProviders(
        <FusionPage slug="home" standalone>
          {(page, _fallback) => <TestChild page={page} />}
        </FusionPage>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('page-content')).toHaveTextContent(
        'Page data loaded',
      );
    });
  });

  it('renders FusionProxy when session pref is true', async () => {
    sessionStorage.setItem('fusion_render_first', 'true');

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () =>
        Promise.resolve('<div data-testid="standalone-fragment">Standalone fragment</div>'),
    } as Response);

    await act(async () => {
      renderWithProviders(
        <FusionPage slug="home" standalone>
          {(page, _fallback) => <TestChild page={page} />}
        </FusionPage>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('standalone-fragment')).toHaveTextContent(
        'Standalone fragment',
      );
    });
  });

  it('renders data content when session pref is false', async () => {
    sessionStorage.setItem('fusion_render_first', 'false');

    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: TRUTHY_ENCODED },
      isLoading: false,
      error: undefined,
    });

    await act(async () => {
      renderWithProviders(
        <FusionPage slug="home" standalone>
          {(page, _fallback) => <TestChild page={page} />}
        </FusionPage>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('page-content')).toHaveTextContent(
        'Page data loaded',
      );
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// Edge cases
// ═══════════════════════════════════════════════════════════════════

describe('FusionPage — edge cases', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('renders ErrorState when query has an error (standalone mode)', async () => {
    mockUseGetPageDataQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    });

    await act(async () => {
      renderWithProviders(
        <FusionPage slug="home" standalone>
          {(page, _fallback) => <TestChild page={page} />}
        </FusionPage>,
      );
    });

    expect(
      screen.getByText(/Unable to load page content/i),
    ).toBeInTheDocument();
  });
});
