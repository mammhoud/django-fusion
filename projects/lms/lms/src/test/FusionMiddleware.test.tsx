/**
 * Unit tests for FusionMiddleware.
 *
 * Covers:
 * - Initialisation from sessionStorage (true → fragment, false → data, undefined → data)
 * - fallbackToData() flips mode and clears session
 * - enableFragments() flips mode and sets session
 * - custom initialMode prop overrides sessionStorage
 * - useFusionMode() hook returns context values
 * - Provider renders children
 */
import { render, screen, renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  FusionMiddleware,
  useFusionMode,
} from '@/components/FusionMiddleware';

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

/** Render a component that uses useFusionMode to display the current context values. */
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
    sessionStorage.clear();
  });

  it('resolves to data mode when sessionStorage is empty', async () => {
    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    // Effect resolves to 'data' (no session pref set → defaults to data mode)
    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });
  });

  it('resolves to fragment mode when sessionStorage has true', async () => {
    sessionStorage.setItem('fusion_render_first', 'true');

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('fragment');
    });
  });

  it('resolves to data mode when sessionStorage has false', async () => {
    sessionStorage.setItem('fusion_render_first', 'false');

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });
  });

  it('respects initialMode prop and skips sessionStorage', async () => {
    // Set a conflicting session value — should be ignored
    sessionStorage.setItem('fusion_render_first', 'true');

    render(
      <FusionMiddleware initialMode="data">
        <TestConsumer />
      </FusionMiddleware>,
    );

    // Should be data immediately (no effect needed)
    // Wait for render to settle
    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('data');
    });

    // Confirming the session value was NOT read
    expect(sessionStorage.getItem('fusion_render_first')).toBe('true');
  });
});

// ═══════════════════════════════════════════════════════════════════
// fallbackToData
// ═══════════════════════════════════════════════════════════════════

describe('fallbackToData', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('flips mode from data to data (no-op when already data)', async () => {
    render(
      <FusionMiddleware initialMode="data">
        <TestConsumer />
      </FusionMiddleware>,
    );

    const fallbackBtn = screen.getByTestId('fallback');

    await act(async () => {
      fallbackBtn.click();
    });

    expect(screen.getByTestId('mode').textContent).toBe('data');
    expect(sessionStorage.getItem('fusion_render_first')).toBe('false');
  });

  it('flips mode from fragment to data and clears session', async () => {
    sessionStorage.setItem('fusion_render_first', 'true');

    render(
      <FusionMiddleware>
        <TestConsumer />
      </FusionMiddleware>,
    );

    // Wait for fragment mode
    await vi.waitFor(() => {
      expect(screen.getByTestId('mode').textContent).toBe('fragment');
    });

    const fallbackBtn = screen.getByTestId('fallback');
    await act(async () => {
      fallbackBtn.click();
    });

    expect(screen.getByTestId('mode').textContent).toBe('data');
    // Session should be cleared and set to false
    expect(sessionStorage.getItem('fusion_render_first')).toBe('false');
  });
});

// ═══════════════════════════════════════════════════════════════════
// enableFragments
// ═══════════════════════════════════════════════════════════════════

describe('enableFragments', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('flips mode from data to fragment', async () => {
    render(
      <FusionMiddleware initialMode="data">
        <TestConsumer />
      </FusionMiddleware>,
    );

    const enableBtn = screen.getByTestId('enable');
    await act(async () => {
      enableBtn.click();
    });

    expect(screen.getByTestId('mode').textContent).toBe('fragment');
    expect(sessionStorage.getItem('fusion_render_first')).toBe('true');
  });
});

// ═══════════════════════════════════════════════════════════════════
// useFusionMode hook in isolation
// ═══════════════════════════════════════════════════════════════════

describe('useFusionMode hook', () => {
  it('returns default values when no provider is present', () => {
    const { result } = renderHook(() => useFusionMode());

    expect(result.current.mode).toBe('loading');
    // noop callbacks should not throw
    expect(() => result.current.fallbackToData()).not.toThrow();
    expect(() => result.current.enableFragments()).not.toThrow();
  });

  it('returns provider values from context', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <FusionMiddleware initialMode="fragment">{children}</FusionMiddleware>
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
    render(
      <FusionMiddleware>
        <div data-testid="child">Hello</div>
      </FusionMiddleware>,
    );

    expect(screen.getByTestId('child')).toHaveTextContent('Hello');
  });
});
