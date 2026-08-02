/**
 * Unit tests for the FusionAssets component.
 *
 * Covers:
 * - Fetches asset manifest from /apis/assets/manifest
 * - Renders JS script tags with `defer` attribute
 * - Renders inline JS via `dangerouslySetInnerHTML`
 * - Graceful degradation on fetch failure (renders null)
 * - Server-side hydration from `window.__FUSION_ASSETS__`
 * - Handles empty manifest arrays (renders null)
 * - Handles manifest with only inline_js
 * - Handles manifest with only JS URLs
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import FusionAssets from '@/components/FusionAssets';
import { fusionApi } from '@/lib/api-client';

// ═══════════════════════════════════════════════════════════════════
// Mock the API client
// ═══════════════════════════════════════════════════════════════════

vi.mock('@/lib/api-client', () => ({
  fusionApi: {
    fetchJson: vi.fn(),
  },
}));

// ═══════════════════════════════════════════════════════════════════
// Mock fetch for window.__FUSION_ASSETS__ tests (not used via API)
// ═══════════════════════════════════════════════════════════════════

const mockFetchJson = fusionApi.fetchJson as ReturnType<typeof vi.fn>;

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const FULL_MANIFEST = {
  status: 200,
  message: 'Success',
  data: {
    top: {
      css: ['/static/css/fusion.css'],
      fonts: ['/static/fonts/remixicon/remixicon.css'],
      preconnect: ['https://fonts.googleapis.com'],
      inline_css: [':root{--fu-primary:#7c3aed}'],
    },
    bottom: {
      js: ['/static/js/fusion-bridge.js', '/static/js/analytics.js'],
      inline_js: ['console.log("loaded");', 'window.ready=true;'],
    },
  },
};

const JS_ONLY_MANIFEST = {
  status: 200,
  message: 'Success',
  data: {
    top: { css: [], fonts: [], preconnect: [], inline_css: [] },
    bottom: {
      js: ['/static/js/fusion-bridge.js'],
      inline_js: [],
    },
  },
};

const INLINE_ONLY_MANIFEST = {
  status: 200,
  message: 'Success',
  data: {
    top: { css: [], fonts: [], preconnect: [], inline_css: [] },
    bottom: {
      js: [],
      inline_js: ['console.log("inline only");'],
    },
  },
};

const EMPTY_MANIFEST = {
  status: 200,
  message: 'Success',
  data: {
    top: { css: [], fonts: [], preconnect: [], inline_css: [] },
    bottom: { js: [], inline_js: [] },
  },
};

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function mockManifestResponse(manifest: typeof FULL_MANIFEST) {
  mockFetchJson.mockResolvedValueOnce(manifest);
}

function mockFetchFailure(errorMessage = 'Network error') {
  mockFetchJson.mockRejectedValueOnce(new Error(errorMessage));
}

function mockFetchPending() {
  mockFetchJson.mockReturnValueOnce(new Promise(() => {}));
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('FusionAssets — manifest fetch and render', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Remove server-side hydration global
    delete (window as any).__FUSION_ASSETS__;
  });

  afterEach(() => {
    delete (window as any).__FUSION_ASSETS__;
  });

  // ── Success cases ──

  it('fetches the asset manifest from the correct API path', async () => {
    mockManifestResponse(FULL_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    expect(mockFetchJson).toHaveBeenCalledTimes(1);
    expect(mockFetchJson).toHaveBeenCalledWith('/apis/assets/manifest');
  });

  it('renders JS script tags with defer attribute from manifest', async () => {
    mockManifestResponse(FULL_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    // Wait for useEffect to resolve
    await vi.waitFor(() => {
      const bridgeScript = document.querySelector(
        'script[src="/static/js/fusion-bridge.js"]',
      );
      expect(bridgeScript).toBeInTheDocument();
      expect(bridgeScript).toHaveAttribute('defer');
    });

    const analyticsScript = document.querySelector(
      'script[src="/static/js/analytics.js"]',
    );
    expect(analyticsScript).toBeInTheDocument();
    expect(analyticsScript).toHaveAttribute('defer');
  });

  it('renders inline JS scripts via dangerouslySetInnerHTML', async () => {
    mockManifestResponse(FULL_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      // Find scripts that don't have a src attribute (inline scripts)
      const inlineScripts = Array.from(
        document.querySelectorAll('script:not([src])'),
      );
      expect(inlineScripts.length).toBeGreaterThanOrEqual(2);
    });
  });

  it('renders only JS URLs when manifest has no inline_js', async () => {
    mockManifestResponse(JS_ONLY_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      const bridgeScript = document.querySelector(
        'script[src="/static/js/fusion-bridge.js"]',
      );
      expect(bridgeScript).toBeInTheDocument();
      expect(bridgeScript).toHaveAttribute('defer');
    });

    // No inline scripts since inline_js is empty
    const inlineScripts = Array.from(
      document.querySelectorAll('script:not([src])'),
    );
    expect(inlineScripts.length).toBe(0);
  });

  it('renders only inline JS when manifest has no JS URLs', async () => {
    mockManifestResponse(INLINE_ONLY_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      const jsScripts = document.querySelectorAll('script[src]');
      expect(jsScripts.length).toBe(0);

      const inlineScripts = Array.from(
        document.querySelectorAll('script:not([src])'),
      );
      expect(inlineScripts.length).toBeGreaterThanOrEqual(1);
    });
  });

  // ── Graceful degradation ──

  it('renders null when fetch fails (graceful degradation)', async () => {
    const consoleWarnSpy = vi
      .spyOn(console, 'warn')
      .mockImplementation(() => {});

    mockFetchFailure('API error 500');

    const { container } = await act(async () => {
      return render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        '[FusionAssets] Failed to fetch asset manifest:',
        expect.any(Error),
      );
    });

    // Component should render nothing on error
    expect(container.innerHTML).toBe('');

    consoleWarnSpy.mockRestore();
  });

  it('renders null when manifest has empty arrays', async () => {
    mockManifestResponse(EMPTY_MANIFEST);

    const { container } = await act(async () => {
      return render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      const scripts = container.querySelectorAll('script');
      expect(scripts.length).toBe(0);
    });
  });

  it('renders null while fetch is pending', async () => {
    mockFetchPending();

    const { container } = await act(async () => {
      return render(<FusionAssets />);
    });

    // While loading, component renders null (no flash of content)
    expect(container.innerHTML).toBe('');
  });

  // ── Server-side hydration ──

  it('hydrates from window.__FUSION_ASSETS__ and skips API call', async () => {
    // Simulate server-injected manifest
    (window as any).__FUSION_ASSETS__ = FULL_MANIFEST.data;

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      const bridgeScript = document.querySelector(
        'script[src="/static/js/fusion-bridge.js"]',
      );
      expect(bridgeScript).toBeInTheDocument();
    });

    // API should NOT be called — hydration from window global
    expect(mockFetchJson).not.toHaveBeenCalled();
  });

  it('hydrates only bottom assets from server manifest (ignores top)', async () => {
    // Server manifest has both top and bottom, but component only renders bottom
    (window as any).__FUSION_ASSETS__ = FULL_MANIFEST.data;

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      // Bottom JS scripts should be present
      const bridgeScript = document.querySelector(
        'script[src="/static/js/fusion-bridge.js"]',
      );
      expect(bridgeScript).toBeInTheDocument();

      // Top assets (CSS links) should NOT be rendered by this component
      const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
      expect(cssLinks.length).toBe(0);
    });
  });

  // ── Edge cases ──

  it('handles manifest with missing bottom key gracefully', async () => {
    mockFetchJson.mockResolvedValueOnce({
      status: 200,
      message: 'Success',
      data: { top: { css: [], fonts: [], preconnect: [], inline_css: [] } },
      // No bottom key
    });

    const { container } = await act(async () => {
      return render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      const scripts = container.querySelectorAll('script');
      expect(scripts.length).toBe(0);
    });
  });

  it('uses unique keys for each script and inline_js entry', async () => {
    mockManifestResponse(FULL_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      // Each JS script should have a unique key via src
      const jsScripts = document.querySelectorAll('script[src]');
      const srcs = Array.from(jsScripts).map((s) => s.getAttribute('src'));
      const uniqueSrcs = new Set(srcs);
      expect(uniqueSrcs.size).toBe(srcs.length);
    });
  });

  it('does not render CSS links or font preloads (top assets are build-time)', async () => {
    mockManifestResponse(FULL_MANIFEST);

    await act(async () => {
      render(<FusionAssets />);
    });

    await vi.waitFor(() => {
      const cssLinks = document.querySelectorAll('link');
      expect(cssLinks.length).toBe(0);
    });
  });
});
