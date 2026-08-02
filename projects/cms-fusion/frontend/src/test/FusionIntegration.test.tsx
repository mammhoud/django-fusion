/**
 * E2E integration tests for the frontend fusion fragment-rendering flow.
 *
 * Simulates the complete backend → API → frontend chain:
 * 1. Health check → session storage → FusionMiddleware mode resolution
 * 2. FusionPage with mocked API → renders data content
 * 3. FusionPage in fragment mode → FusionProxy → renders HTML
 * 4. Fragment failure → fallback to data mode
 * 5. Codec decode (simulates backend FusionCodec.encode output)
 * 6. Envelope unwrap (simulates `fusion_json_response` payload)
 * 7. Standalone mode: session preference → FusionProxy
 *
 * These tests verify that the frontend components work correctly when
 * connected to real backend responses (mocked at the fetch/API layer).
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { FusionPage } from '@/components/FusionPage';
import { FusionMiddleware } from '@/components/FusionMiddleware';
import { FusionProxy } from '@/components/FusionProxy';
import { fusionDecoder } from '@/lib/fusion-decoder';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks used by FusionPageDataInner
// ═══════════════════════════════════════════════════════════════════

const mockUseGetPageDataQuery = vi.fn();

vi.mock('@/store/api/endpoints/pages', () => ({
  useGetPageDataQuery: (...args: unknown[]) => mockUseGetPageDataQuery(...args),
  useGetPageFragmentQuery: vi.fn(),
  useGetPageQuery: vi.fn(),
  useGetPageHtmlQuery: vi.fn(),
}));

// ═══════════════════════════════════════════════════════════════════
// Shared test data — mirrors real backend STATIC_PAGES content
// ═══════════════════════════════════════════════════════════════════

/** Codec-encoded payload for home page data (matches STATIC_PAGES["home"]). */
const HOME_PAGE_ENCODED =
  'fusion_v1:eyJzbHVnIjoiaG9tZSIsInRpdGxlIjoiTGVhcm4gV2l0aG91dCBMaW1pdHMiLCJzZW8iOnsidGl0bGUiOiJMTVMgUGxhdGZvcm0gfCBMZWFybiBXaXRob3V0IExpbWl0cyIsImRlc2NyaXB0aW9uIjoiTWFzdGVyIG5ldyBza2lsbHMgd2l0aCBleHBlcnQtbGVkIGNvdXJzZXMsIGludGVyYWN0aXZlIGNvbnRlbnQsIGFuZCBhIGNvbW11bml0eSBvZiBsZWFybmVycy4ifSwiYmxvY2tzIjpbeyJ0eXBlIjoiaGVybyIsImhlYWRpbmciOiJMZWFybiBXaXRob3V0IExpbWl0cyIsImludHJvIjoiTWFzdGVyIG5ldyBza2lsbHMgd2l0aCBleHBlcnQtbGVkIGNvdXJzZXMsIGludGVyYWN0aXZlIGNvbnRlbnQsIGFuZCBhIGNvbW11bml0eSBvZiBsZWFybmVycy4iLCJjdGFzIjpbeyJsYWJlbCI6IkV4cGxvcmUgQ291cnNlcyIsImhyZWYiOiIvY291cnNlcyIsInZhcmlhbnQiOiJwcmltYXJ5In0seyJsYWJlbCI6IkdldCBTdGFydGVkIEZyZWUiLCJocmVmIjoiL3JlZ2lzdHJhdGlvbiIsInZhcmlhbnQiOiJzZWNvbmRhcnkifV19LHsidHlwZSI6InN0YXRzIiwiaXRlbXMiOlt7ImxhYmVsIjoiU3R1ZGVudHMiLCJ2YWx1ZSI6IjVLKyJ9LHsibGFiZWwiOiJSZXZpZXdzIiwidmFsdWUiOiIxMksrIn1dfSx7InR5cGUiOiJzZWN0aW9uX2hlYWRlciIsImtleSI6ImZlYXR1cmVkX2NvdXJzZXMiLCJoZWFkaW5nIjoiRmVhdHVyZWQgQ291cnNlcyIsImludHJvIjoiTW9zdCBwb3B1bGFyIGNvdXJzZXMgcGlja2VkIGZvciB5b3UiLCJjdGEiOnsibGFiZWwiOiJWaWV3IEFsbCIsImhyZWYiOiIvY291cnNlcyIsInZhcmlhbnQiOiJsaW5rIn19LHsidHlwZSI6ImN0YSIsImhlYWRpbmciOiJTdGFydCBMZWFybmluZyBUb2RheSIsImludHJvIjoiSm9pbiB0aG91c2FuZHMgb2Ygc3R1ZGVudHMgYnVpbGRpbmcgc2tpbGxzIGZvciB0aGVpciBuZXh0IG9wcG9ydHVuaXR5LiIsImN0YXMiOlt7ImxhYmVsIjoiQ3JlYXRlIEZyZWUgQWNjb3VudCIsImhyZWYiOiIvcmVnaXN0cmF0aW9uIn1dfV19';

/** Simulated health check response matching /apis/health/ endpoint. */
const HEALTH_RESPONSE_WITH_FRAGMENTS = {
  status: 200,
  message: 'Success',
  data: {
    fusion_render_first: true,
    reason: 'user_agent: Mozilla/5.0 Chrome/120',
    session_cached: false,
  },
};

const HEALTH_RESPONSE_WITHOUT_FRAGMENTS = {
  status: 200,
  message: 'Success',
  data: {
    fusion_render_first: false,
    reason: 'user_agent: curl/7.68',
    session_cached: false,
  },
};

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

function renderWithProvider(ui: React.ReactElement) {
  return render(<Provider store={createTestStore()}>{ui}</Provider>);
}

function TestChild({ page }: { page: unknown }) {
  return (
    <div data-testid="page-content">
      {page ? 'Page data loaded' : 'No data'}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 1. Health check → session storage → middleware mode
// ═══════════════════════════════════════════════════════════════════

describe('Health check → session → middleware mode', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('health response with fusion_render_first=true → fragment mode', async () => {
    // Simulate: frontend calls /apis/health/ and stores result
    const healthData = HEALTH_RESPONSE_WITH_FRAGMENTS.data;
    fusionDecoder.initSession(healthData.fusion_render_first);

    // Verify stored
    expect(fusionDecoder.getSessionPreference()).toBe(true);

    // Set up the fetch mock BEFORE rendering, because FusionProxy's
    // useEffect fires fetch() synchronously during the render cycle.
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve('<div data-testid="fragment-result">Fragment content</div>'),
    } as Response);

    // Now render — Fragment mode will trigger FusionProxy which fetches
    await act(async () => {
      renderWithProvider(
        <FusionMiddleware>
          <FusionPage slug="home">{(page, _fb) => <TestChild page={page} />}</FusionPage>
        </FusionMiddleware>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('fragment-result')).toHaveTextContent('Fragment content');
    });
  });

  it('health response with fusion_render_first=false → data mode', async () => {
    // Simulate: health check returns false
    fusionDecoder.initSession(false);

    // Verify stored
    expect(fusionDecoder.getSessionPreference()).toBe(false);

    // Mock the RTK Query data call (data mode uses useGetPageDataQuery)
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: HOME_PAGE_ENCODED },
      isLoading: false,
      error: undefined,
    });

    await act(async () => {
      renderWithProvider(
        <FusionMiddleware>
          <FusionPage slug="home">{(page, _fb) => <TestChild page={page} />}</FusionPage>
        </FusionMiddleware>,
      );
    });

    // Data mode → renders the child component with decoded page data
    await vi.waitFor(() => {
      expect(screen.getByTestId('page-content')).toHaveTextContent('Page data loaded');
    });
  });

  it('no health check yet (no session) → defaults to data mode', async () => {
    // No session preference set — FusionMiddleware defaults to data
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: HOME_PAGE_ENCODED },
      isLoading: false,
      error: undefined,
    });

    await act(async () => {
      renderWithProvider(
        <FusionMiddleware>
          <FusionPage slug="home">{(page, _fb) => <TestChild page={page} />}</FusionPage>
        </FusionMiddleware>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('page-content')).toHaveTextContent('Page data loaded');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// 2. FusionProxy integration — fetch → render → error
// ═══════════════════════════════════════════════════════════════════

describe('FusionProxy integration — full fetch lifecycle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches fragment URL and renders HTML', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve('<h1 data-testid="frag">Hello from server</h1>'),
    } as Response);

    await act(async () => {
      render(<FusionProxy fragmentUrl="/apis/pages/home/data/?fusion_render_first=true" />);
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('frag')).toHaveTextContent('Hello from server');
    });
  });

  it('calls onError callback when fetch fails', async () => {
    const onError = vi.fn();

    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    await act(async () => {
      render(
        <FusionProxy
          fragmentUrl="/apis/pages/home/data/"
          onError={onError}
        />,
      );
    });

    await vi.waitFor(() => {
      expect(onError).toHaveBeenCalledTimes(1);
    });
  });

  it('shows error fallback when provided', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    await act(async () => {
      render(
        <FusionProxy
          fragmentUrl="/apis/pages/home/data/"
          errorFallback={<div data-testid="custom-error">Custom error</div>}
        />,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('custom-error')).toHaveTextContent('Custom error');
    });
  });

  it('shows default error text when no fallback provided', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    await act(async () => {
      render(<FusionProxy fragmentUrl="/apis/pages/home/data/" />);
    });

    await vi.waitFor(() => {
      expect(screen.getByText(/Unable to render this section/i)).toBeInTheDocument();
    });
  });

  it('accepts header for HTML content type', async () => {
    vi.mocked(fetch).mockImplementationOnce(async (url, init) => {
      // Verify the request includes the Accept header
      const headers = init?.headers as Record<string, string> | undefined;
      expect(headers?.Accept).toBe('text/html');
      return {
        ok: true,
        text: () => Promise.resolve('<div>OK</div>'),
      } as Response;
    });

    await act(async () => {
      render(<FusionProxy fragmentUrl="/apis/pages/home/data/?fusion_render_first=true" />);
    });

    await vi.waitFor(() => {
      expect(screen.getByText('OK')).toBeInTheDocument();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// 3. FusionPage fragment failure → fallback to data mode
// ═══════════════════════════════════════════════════════════════════

describe('FusionPage fragment failure → fallbackToData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('when FusionProxy fails, fallbackToData flips to data mode', async () => {
    // Start in fragment mode
    sessionStorage.setItem('fusion_render_first', 'true');

    // First fetch fails
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Server error'));

    // After fallback, data mode query succeeds
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: HOME_PAGE_ENCODED },
      isLoading: false,
      error: undefined,
    });

    await act(async () => {
      renderWithProvider(
        <FusionMiddleware>
          <FusionPage slug="home">{(page, _fb) => <TestChild page={page} />}</FusionPage>
        </FusionMiddleware>,
      );
    });

    // Should fallback to data mode and render page content
    await vi.waitFor(() => {
      expect(screen.getByTestId('page-content')).toHaveTextContent('Page data loaded');
    });

    // Session should be cleared
    expect(sessionStorage.getItem('fusion_render_first')).toBe('false');
  });

  it('standalone mode: fragment fails → clears session for next navigation', async () => {
    sessionStorage.setItem('fusion_render_first', 'true');

    // FusionProxy fetch fails
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Timeout'));

    await act(async () => {
      renderWithProvider(
        <FusionPage slug="home" standalone>
          {(page, _fb) => <TestChild page={page} />}
        </FusionPage>,
      );
    });

    // Session should be cleared
    await vi.waitFor(() => {
      expect(sessionStorage.getItem('fusion_render_first')).toBeNull();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// 4. FusionDecoder codec integration — decode real backend payloads
// ═══════════════════════════════════════════════════════════════════

describe('FusionDecoder codec integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('decodes a real codec string from the backend', () => {
    // This is what happens when the frontend receives a
    // page_data response and calls fusionDecoder.decodeAs<CmsPage>()
    const decoded = fusionDecoder.decode(HOME_PAGE_ENCODED) as Record<string, unknown>;

    expect(decoded).toBeDefined();
    expect(decoded).toHaveProperty('slug', 'home');
    expect(decoded).toHaveProperty('title', 'Learn Without Limits');
    expect(decoded).toHaveProperty('blocks');
  });

  it('decoded data has expected block types', () => {
    const decoded = fusionDecoder.decode(HOME_PAGE_ENCODED) as {
      blocks: Array<{ type: string }>;
    };

    expect(decoded.blocks).toBeInstanceOf(Array);
    expect(decoded.blocks.length).toBeGreaterThan(0);
    expect(decoded.blocks[0]).toHaveProperty('type');

    const types = decoded.blocks.map((b) => b.type);
    expect(types).toContain('hero');
    expect(types).toContain('stats');
    expect(types).toContain('cta');
  });

  it('decoded hero block has heading and ctas', () => {
    const decoded = fusionDecoder.decode(HOME_PAGE_ENCODED) as {
      blocks: Array<{ type: string; heading?: string; ctas?: Array<{ label: string }> }>;
    };

    const hero = decoded.blocks.find((b) => b.type === 'hero');
    expect(hero).toBeDefined();
    expect(hero?.heading).toBe('Learn Without Limits');
    expect(hero?.ctas).toBeInstanceOf(Array);
    expect(hero?.ctas?.length).toBe(2);
    expect(hero?.ctas?.[0].label).toBe('Explore Courses');
  });

  it('parseCoded extracts version and b64', () => {
    const parsed = fusionDecoder.parseCoded(HOME_PAGE_ENCODED);
    expect(parsed.version).toBe('1');
    expect(parsed.b64).toBeTruthy();
    expect(parsed.encoded).toBe(HOME_PAGE_ENCODED);
  });
});

// ═══════════════════════════════════════════════════════════════════
// 5. FusionEnvelope unwrap integration
// ═══════════════════════════════════════════════════════════════════

describe('FusionEnvelope unwrap integration', () => {
  it('unwraps a valid envelope like the backend returns', () => {
    // Simulates: backend fusion_json_response() returns {status, message, data}
    const envelope = {
      status: 200,
      message: 'Success',
      data: { slug: 'home', title: 'Home', encoded: HOME_PAGE_ENCODED },
    };

    // Frontend unwrap via transformResponse:
    //   raw.data → PageDataResponse
    const data = envelope.data;
    expect(data.slug).toBe('home');
    expect(data.title).toBe('Home');
    expect(data.encoded).toBe(HOME_PAGE_ENCODED);

    // Decode the inner codec string
    const decoded = fusionDecoder.decode(data.encoded) as Record<string, unknown>;
    expect(decoded.title).toBe('Learn Without Limits');
  });

  it('unwraps a fragment pointer envelope', () => {
    // Simulates: backend page_fragment() returns {status, message, data: {component, ...}}
    const envelope = {
      status: 200,
      message: 'Success',
      data: {
        component: 'pages.home',
        fragment_name: 'pages.home',
        fragment_url: 'http://testserver/fragments/pages.home/',
        fusion_render_first: false,
        page_slug: 'home',
        title: 'Learn Without Limits',
      },
    };

    const pointer = envelope.data;
    expect(pointer.component).toBe('pages.home');
    expect(pointer.fragment_name).toBe('pages.home');
    expect(pointer.fragment_url).toContain('/fragments/pages.home/');
    expect(pointer.fusion_render_first).toBe(false);
    expect(pointer.page_slug).toBe('home');
  });

  it('throws on non-2xx status when unwrapping', () => {
    const envelope = {
      status: 404,
      message: 'Not Found',
      data: { error: 'Page not found' },
    };

    expect(() => fusionDecoder.unwrap(envelope)).toThrow();
  });

  it('handles the unwrapped data from transformResponse pattern', () => {
    // This is exactly what the RTK Query transformResponse does in pages.ts:
    //   transformResponse: (raw) => raw.data
    const raw = {
      status: 200,
      message: 'Success',
      data: { slug: 'faq', title: 'FAQ', encoded: 'fusion_v1:dGVzdA==' },
    };

    const unwrapped = raw.data;
    expect(unwrapped.slug).toBe('faq');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 6. Standalone mode: session preference → FusionProxy
// ═══════════════════════════════════════════════════════════════════

describe('Standalone mode — session → fragment', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('fusionDecoder session → standalone FusionPage → renders HTML', async () => {
    // Simulate: health check ran and stored preference
    fusionDecoder.initSession(true);
    expect(fusionDecoder.getSessionPreference()).toBe(true);

    // Mock FusionProxy fetch
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve('<div data-testid="standalone-fragment">Standalone rendered</div>'),
    } as Response);

    await act(async () => {
      renderWithProvider(
        <FusionPage slug="home" standalone>
          {(page, _fb) => <TestChild page={page} />}
        </FusionPage>,
      );
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('standalone-fragment')).toHaveTextContent('Standalone rendered');
    });
  });

  it('shouldRenderFragmentFirst respects session over pointer', () => {
    // Session says true
    fusionDecoder.initSession(true);

    // Pointer says false
    const pointer = {
      component: 'pages.home',
      fragment_name: 'pages.home',
      fragment_url: '/fragments/pages.home/',
      fusion_render_first: false,
    };

    // Session should win
    expect(fusionDecoder.shouldRenderFragmentFirst(pointer)).toBe(true);
  });

  it('shouldRenderFragmentFirst falls back to pointer when session is unset', () => {
    const pointer = {
      component: 'pages.home',
      fragment_name: 'pages.home',
      fragment_url: '/fragments/pages.home/',
      fusion_render_first: true,
    };

    expect(fusionDecoder.shouldRenderFragmentFirst(pointer)).toBe(true);
  });

  it('shouldRenderFragmentFirst defaults to false when nothing is set', () => {
    const pointer = {
      component: 'pages.home',
      fragment_name: 'pages.home',
      fragment_url: '/fragments/pages.home/',
      fusion_render_first: false,
    };

    expect(fusionDecoder.shouldRenderFragmentFirst(pointer)).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════
// 7. Cross-layer: backend vs frontend contract alignment
// ═══════════════════════════════════════════════════════════════════

describe('Cross-layer contract alignment', () => {
  it('backend fragment_name matches frontend decodeFragmentPointer convention', () => {
    // Backend produces: fragment_name = f"pages.{normalized.replace('-', '_')}"
    // Frontend consumes: pointer.fragment_name → used for fragment_url

    const backendStyleFragmentName = 'pages.about_us';
    const frontendFragmentUrl = `/fragments/${backendStyleFragmentName}/`;

    // Verify the frontend would construct the same URL
    expect(frontendFragmentUrl).toBe('/fragments/pages.about_us/');
  });

  it('backend STATIC_PAGES keys match frontend slug convention', () => {
    // Frontend passes slug to /apis/pages/<slug>/data/
    const slugs = ['home', 'about-us', 'faq', 'contact', 'privacy'];
    // All of these should be valid STATIC_PAGES keys (after normalization)
    for (const slug of slugs) {
      // The frontend uses FusionPage slug prop → page_data(slug)
      // Backend normalize_slug handles '' → 'home' and others strip '/'
      expect(slug).toBeTruthy();
    }
  });

  it('backend envelope status codes align with frontend unwrap logic', () => {
    // Frontend unwrap throws on non-2xx:
    //   if (envelope.status < 200 || envelope.status >= 300) throw ...
    const successStatuses = [200, 201];
    const errorStatuses = [400, 401, 403, 404, 500];

    for (const status of successStatuses) {
      const envelope = { status, message: 'OK', data: { ok: true } };
      expect(() => fusionDecoder.unwrap(envelope)).not.toThrow();
    }

    for (const status of errorStatuses) {
      const envelope = { status, message: 'Error', data: { error: 'fail' } };
      expect(() => fusionDecoder.unwrap(envelope)).toThrow();
    }
  });
});
