/**
 * Unit tests for POS Solo FusionMiddleware.
 *
 * Covers:
 * - Initialisation from fusionStore (true → fragment, false → data, undefined → data)
 * - fallbackToData() flips mode and clears session
 * - enableFragments() flips mode and sets session
 * - custom initialMode prop overrides session
 * - useFusionMode() hook returns context values
 * - Provider renders children
 */
import { render, screen, renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  FusionMiddleware,
  useFusionMode,
} from '../components/FusionMiddleware';

// ═══════════════════════════════════════════════════════════════════
// Mock the fusionStore module
// ═══════════════════════════════════════════════════════════════════

const mockGetSessionPreference = vi.fn();
const mockInitSession = vi.fn();
const mockClearSession = vi.fn();

vi.mock('../lib/fusion-store', () => ({
  fusionStore: {
    getSessionPreference: (...args: unknown[]) => mockGetSessionPreference(...args),
    initSession: (...args: unknown[]) => mockInitSession(...args),
    clearSession: (...args: unknown[]) => mockClearSession(...args),
  },
}));

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function TestConsumer() {
  const { mode, fallbackToData, enableFragments } = useFusionMode();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <button data-testid="fallback" onClick={fallbackToData}>
        fallback
      </button>
      <button data-testid="enable" onClick={enableFragments}>
        enable
      </button>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Initialisation
// ═══════════════════════════════════════════════════════════════════

describe('FusionMiddleware initialisation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('resolves to data mode when fusionStore is empty', async () => {
    mockGetSessionPreference.mockResolvedValue(undefined);

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });
  });

  it('resolves to fragment mode when fusionStore has true', async () => {
    mockGetSessionPreference.mockResolvedValue(true);

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('fragment');
    });
  });

  it('resolves to data mode when fusionStore has false', async () => {
    mockGetSessionPreference.mockResolvedValue(false);

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });
  });

  it('respects initialMode prop and skips fusionStore', async () => {
    mockGetSessionPreference.mockResolvedValue(true);

    render(
      <FusionMiddleware initialMode="data">
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });

    expect(mockGetSessionPreference).not.toHaveBeenCalled();
  });
});

// ═══════════════════════════════════════════════════════════════════
// fallbackToData
// ═══════════════════════════════════════════════════════════════════

describe('fallbackToData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('flips mode from fragment to data', async () => {
    mockGetSessionPreference.mockResolvedValue(true);
    mockInitSession.mockResolvedValue(undefined);

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('fragment');
    });

    const fallbackBtn = screen.getByTestId('fallback');
    await act(async () => {
      fallbackBtn.click();
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });
    expect(mockInitSession).toHaveBeenCalledWith(false);
  });
});

// ═══════════════════════════════════════════════════════════════════
// enableFragments
// ═══════════════════════════════════════════════════════════════════

describe('enableFragments', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('flips mode from data to fragment', async () => {
    mockGetSessionPreference.mockResolvedValue(undefined);
    mockInitSession.mockResolvedValue(undefined);

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });

    const enableBtn = screen.getByTestId('enable');
    await act(async () => {
      enableBtn.click();
    });

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('fragment');
    });
    expect(mockInitSession).toHaveBeenCalledWith(true);
  });
});

// ═══════════════════════════════════════════════════════════════════
// useFusionMode hook in isolation
// ═══════════════════════════════════════════════════════════════════

describe('useFusionMode hook', () => {
  it('returns default values when no provider is present', () => {
    const { result } = renderHook(() => useFusionMode());

    expect(result.current.mode).toBe('loading');
    expect(() => result.current.fallbackToData()).not.toThrow();
    expect(() => result.current.enableFragments()).not.toThrow();
  });

  it('returns provider values from context', async () => {
    mockGetSessionPreference.mockResolvedValue(true);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <FusionMiddleware>{children}</FusionMiddleware>
    );

    const { result } = renderHook(() => useFusionMode(), { wrapper });

    await vi.waitFor(() => {
      expect(result.current.mode).toBe('fragment');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// Children rendering
// ═══════════════════════════════════════════════════════════════════

describe('FusionMiddleware renders children', () => {
  it('renders children inside the provider', () => {
    mockGetSessionPreference.mockResolvedValue(undefined);

    render(
      <FusionMiddleware>
        <div data-testid="child">Hello</div>
      </FusionMiddleware>,
    );

    expect(screen.getByTestId('child')).toHaveTextContent('Hello');
  });
});
