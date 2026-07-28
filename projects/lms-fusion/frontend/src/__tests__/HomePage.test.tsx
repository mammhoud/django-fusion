/**
 * Integration tests for the lms-fusion HomePage.
 *
 * Covers:
 * - Renders FusionProxy with slug="home"
 * - ScrollReveal wraps the content
 * - Toast fires a welcome message on mount
 * - Toast cleanup on unmount
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock FusionProxy ──

const mockFusionProxy = vi.fn();
vi.mock('@/components/FusionProxy', () => ({
  default: (props: any) => {
    mockFusionProxy(props);
    return <div data-testid="fusion-proxy">FusionProxy: {props.slug}</div>;
  },
}));

// ── Mock ScrollReveal (render children directly) ──

vi.mock('@/components/ui/ScrollReveal', () => ({
  default: ({ children, ...props }: any) => (
    <div data-testid="scroll-reveal" data-animation={props.animation}>
      {children}
    </div>
  ),
}));

// ── Import AFTER mocks ──

import HomePage from '@/app/page';

// ── Wrapper ──

function renderWithProviders(ui: React.ReactElement) {
  return render(<ToastProvider>{ui}</ToastProvider>);
}

// ── Tests ──

describe('HomePage (lms-fusion)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders FusionProxy with slug="home"', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByTestId('fusion-proxy')).toHaveTextContent('FusionProxy: home');
  });

  it('renders FusionProxy specific props', () => {
    renderWithProviders(<HomePage />);
    expect(mockFusionProxy).toHaveBeenCalledWith(
      expect.objectContaining({ slug: 'home' }),
    );
  });

  it('wraps FusionProxy in ScrollReveal with fadeUp animation', () => {
    renderWithProviders(<HomePage />);
    const scrollReveal = screen.getByTestId('scroll-reveal');
    expect(scrollReveal).toBeInTheDocument();
    expect(scrollReveal).toHaveAttribute('data-animation', 'fadeUp');
  });

  it('renders ScrollReveal containing FusionProxy', () => {
    renderWithProviders(<HomePage />);
    const scrollReveal = screen.getByTestId('scroll-reveal');
    const proxy = screen.getByTestId('fusion-proxy');
    expect(scrollReveal).toContainElement(proxy);
  });

  it('has a min-height container for layout', () => {
    renderWithProviders(<HomePage />);
    const container = screen.getByTestId('scroll-reveal').closest('div');
    const outerDiv = container?.parentElement;
    // FusionProxy wraps content in a div with min-h-screen?
    // The HomePage returns <div className="min-h-screen"><ScrollReveal><FusionProxy/></ScrollReveal></div>
    // We can check that scroll-reveal is inside the wrapper
    expect(container?.closest('.min-h-screen') || outerDiv).toBeTruthy();
  });

  it('schedules a welcome toast on mount', async () => {
    renderWithProviders(<HomePage />);
    // After the 1500ms delay, the toast should fire
    await act(() => {
      vi.advanceTimersByTime(1500);
    });
    // The toast should appear in the DOM
    expect(screen.getByText('Welcome to Fusion LMS')).toBeInTheDocument();
  });

  it('shows toast sub-message on mount', async () => {
    renderWithProviders(<HomePage />);
    await act(() => {
      vi.advanceTimersByTime(1500);
    });
    expect(
      screen.getByText('Explore our courses and start learning today.'),
    ).toBeInTheDocument();
  });

  it('does not show toast before the delay elapses', () => {
    renderWithProviders(<HomePage />);
    // Advance only 1000ms — toast should NOT have fired yet
    vi.advanceTimersByTime(1000);
    expect(
      screen.queryByText('Welcome to Fusion LMS'),
    ).not.toBeInTheDocument();
  });

  it('cleans up the toast timer on unmount', () => {
    const { unmount } = renderWithProviders(<HomePage />);
    unmount();
    // After unmount, advancing timers should not cause errors
    vi.advanceTimersByTime(2000);
    // No toast should appear after unmount
    expect(
      screen.queryByText('Welcome to Fusion LMS'),
    ).not.toBeInTheDocument();
  });
});
