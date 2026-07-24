/**
 * Unit tests for POS FusionPage.
 *
 * Covers:
 * - Middleware mode: renders FusionProxy when mode=fragment
 * - Middleware mode: renders data content when mode=data
 * - Middleware mode: loading state shows skeleton
 * - Standalone mode: renders data content (no fragment fetching)
 * - Error state shows error message
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { FusionPage } from '../components/FusionPage';
import { FusionMiddleware } from '../components/FusionMiddleware';

// ═══════════════════════════════════════════════════════════════════
// Mock fusionStore
// ═══════════════════════════════════════════════════════════════════

const mockGetSessionPreference = vi.fn();
const mockInitSession = vi.fn();

vi.mock('../lib/fusion-store', () => ({
  fusionStore: {
    getSessionPreference: (...args: unknown[]) => mockGetSessionPreference(...args),
    initSession: (...args: unknown[]) => mockInitSession(...args),
    clearSession: vi.fn().mockResolvedValue(undefined),
  },
}));

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

const FRAGMENT_URL = 'http://127.0.0.1:8766/fusion/render/dashboard';

function TestChild({ data }: { data: unknown }) {
  return (
    <div data-testid="page-content">
      {data ? 'Page data loaded' : 'No data'}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Middleware mode
// ═══════════════════════════════════════════════════════════════════

describe('FusionPage — middleware mode', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders FusionProxy in fragment mode', async () => {
    mockGetSessionPreference.mockResolvedValue(true);

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () =>
        Promise.resolve('<div data-testid="fragment-html">Server rendered</div>'),
    } as Response);

    await act(async () => {
      render(
        <FusionMiddleware>
          <FusionPage fragmentUrl={FRAGMENT_URL}>
            {(data, _fallback) => <TestChild data={data} />}
          </FusionPage>
        </FusionMiddleware>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('fragment-html')).toHaveTextContent(
        'Server rendered',
      );
    });
  });

  it('renders data content when mode=data', async () => {
    mockGetSessionPreference.mockResolvedValue(false);

    await act(async () => {
      render(
        <FusionMiddleware>
          <FusionPage data={{ test: true }}>
            {(data, _fallback) => <TestChild data={data} />}
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
  });

  it('renders data content when no fragment URL is provided', async () => {
    render(
      <FusionPage standalone data={{ test: true }}>
        {(data, _fallback) => <TestChild data={data} />}
      </FusionPage>,
    );

    expect(screen.getByTestId('page-content')).toHaveTextContent(
      'Page data loaded',
    );
  });
});

// ═══════════════════════════════════════════════════════════════════
// Edge cases
// ═══════════════════════════════════════════════════════════════════

describe('FusionPage — edge cases', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders error state when data fetch fails', async () => {
    const error = new Error('Failed to load');

    render(
      <FusionPage standalone data={undefined} isLoading={false} error={error}>
        {(data, fallback) => <TestChild data={data} />}
      </FusionPage>,
    );

    expect(
      screen.getByText(/Unable to load page content/i),
    ).toBeInTheDocument();
  });

  it('renders loading skeleton when isLoading is true', () => {
    const { container } = render(
      <FusionPage
        fragmentUrl={FRAGMENT_URL}
        data={undefined}
        isLoading
        skeletonVariant="text"
      >
        {(data, fallback) => <TestChild data={data} />}
      </FusionPage>,
    );

    // Should show skeleton with animate-pulse
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });
});
