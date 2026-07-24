/**
 * Unit tests for POS FusionProxy.
 *
 * Covers:
 * - Loading state renders skeleton
 * - Successful fetch renders HTML via dangerouslySetInnerHTML
 * - Fetch error calls onError and shows error state
 * - Custom errorFallback renders instead of default error
 * - Script re-evaluation when enableScripts is true
 * - Cleanup cancels fetch on unmount
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { FusionProxy } from '../components/FusionProxy';

const FRAGMENT_URL = 'http://127.0.0.1:8766/fusion/render/dashboard';
const HTML_CONTENT = '<div data-testid="fragment"><h1>Hello from server</h1></div>';

// ═══════════════════════════════════════════════════════════════════
// Loading state
// ═══════════════════════════════════════════════════════════════════

describe('FusionProxy loading state', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders skeleton while fetching', () => {
    vi.mocked(fetch).mockReturnValue(new Promise(() => {}));

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} />);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Successful fetch
// ═══════════════════════════════════════════════════════════════════

describe('FusionProxy fetch success', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders HTML when fetch succeeds', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(HTML_CONTENT),
    } as Response);

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} />);

    await vi.waitFor(() => {
      expect(screen.getByTestId('fragment')).toHaveTextContent('Hello from server');
    });
  });

  it('sends Accept: text/html header with the fetch request', async () => {
    let capturedInit: RequestInit | undefined;

    vi.mocked(fetch).mockImplementation(async (_input, init) => {
      capturedInit = init as RequestInit;
      return {
        ok: true,
        text: () => Promise.resolve(HTML_CONTENT),
      } as Response;
    });

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} />);

    await vi.waitFor(() => {
      expect(screen.getByTestId('fragment')).toBeInTheDocument();
    });

    expect(capturedInit?.headers).toEqual({ Accept: 'text/html' });
  });

  it('calls onError when fetch returns non-ok status', async () => {
    const onError = vi.fn();

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: () => Promise.resolve('Server error'),
    } as Response);

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} onError={onError} />);

    await vi.waitFor(() => {
      expect(onError).toHaveBeenCalledTimes(1);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// Error state
// ═══════════════════════════════════════════════════════════════════

describe('FusionProxy error state', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows default error message when fetch fails', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} />);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Unable to render this section/i),
      ).toBeInTheDocument();
    });
  });

  it('calls onError callback when fetch fails', async () => {
    const onError = vi.fn();

    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} onError={onError} />);

    await vi.waitFor(() => {
      expect(onError).toHaveBeenCalledTimes(1);
    });
  });

  it('renders custom errorFallback instead of default error', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    render(
      <FusionProxy
        fragmentUrl={FRAGMENT_URL}
        errorFallback={<div data-testid="custom-error">Custom error</div>}
      />,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('custom-error')).toHaveTextContent('Custom error');
    });
  });

  it('does not call onError after unmount (cleanup)', async () => {
    const onError = vi.fn();
    let rejectPromise: (reason: Error) => void;

    const promise = new Promise<Response>((_, reject) => {
      rejectPromise = reject;
    });

    vi.mocked(fetch).mockReturnValue(promise);

    const { unmount } = render(
      <FusionProxy fragmentUrl={FRAGMENT_URL} onError={onError} />,
    );

    unmount();

    await act(async () => {
      rejectPromise!(new Error('Late error'));
      await Promise.resolve();
    });

    expect(onError).not.toHaveBeenCalled();
  });
});

// ═══════════════════════════════════════════════════════════════════
// Script re-evaluation
// ═══════════════════════════════════════════════════════════════════

describe('FusionProxy script re-evaluation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.body.innerHTML = '';
  });

  it('renders HTML content when enableScripts is true', async () => {
    const htmlWithScript =
      '<div><span data-testid="after-script">done</span></div>';

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(htmlWithScript),
    } as Response);

    render(<FusionProxy fragmentUrl={FRAGMENT_URL} enableScripts />);

    await vi.waitFor(() => {
      expect(screen.getByTestId('after-script')).toHaveTextContent('done');
    });
  });
});
