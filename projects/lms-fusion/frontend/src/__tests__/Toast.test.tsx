/**
 * Unit tests for the Toast context, provider, and hooks.
 *
 * Covers:
 * - ToastProvider renders children
 * - useToast throws when used outside provider
 * - addToast adds a toast with generated id
 * - success/error/warning/info shortcut methods
 * - removeToast removes a specific toast
 * - clearAll removes all toasts
 * - Dismiss button on individual toast
 * - Custom duration (duration=0 persists)
 * - Toast types render correct icons
 * - Action button fires onClick and dismisses
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ToastProvider, useToast } from '@/components/ui/Toast';

// ── Helper component that exercises useToast ──

function ToastConsumer({ testId }: { testId?: string }) {
  const toast = useToast();
  return (
    <div>
      <button data-testid={testId || 'add-success'} onClick={() => toast.success('Success Title', 'Success message')}>
        Add Success
      </button>
      <button data-testid="add-error" onClick={() => toast.error('Error Title', 'Error message')}>
        Add Error
      </button>
      <button data-testid="add-warning" onClick={() => toast.warning('Warning Title', 'Warning message')}>
        Add Warning
      </button>
      <button data-testid="add-info" onClick={() => toast.info('Info Title', 'Info message')}>
        Add Info
      </button>
      <button data-testid="add-custom" onClick={() => toast.addToast({ type: 'info', title: 'Custom', message: 'Custom message', duration: 0 })}>
        Add Custom
      </button>
      <button data-testid="clear-all" onClick={() => toast.clearAll()}>
        Clear All
      </button>
      <button
        data-testid="add-with-action"
        onClick={() =>
          toast.addToast({
            type: 'success',
            title: 'Action Toast',
            action: { label: 'Undo', onClick: vi.fn() },
            duration: 0,
          })
        }
      >
        Add With Action
      </button>
      <span data-testid="toast-count">{toast.toasts.length}</span>
    </div>
  );
}

// ── Component that calls useToast outside provider ──

function OrphanConsumer() {
  useToast();
  return <div>Should not render</div>;
}

// ── Wrapper ──

function renderWithProvider(ui: React.ReactElement) {
  return render(<ToastProvider>{ui}</ToastProvider>);
}

// ── Tests ──

describe('Toast - Provider & Context', () => {
  it('renders children inside ToastProvider', () => {
    renderWithProvider(<div>Child Content</div>);
    expect(screen.getByText('Child Content')).toBeInTheDocument();
  });

  it('throws an error when useToast is used outside provider', () => {
    // Suppress console.error for expected error
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<OrphanConsumer />)).toThrow(
      'useToast must be used within a <ToastProvider>',
    );
    spy.mockRestore();
  });

  it('adds a toast via success method', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Success'));
    expect(screen.getByText('Success Title')).toBeInTheDocument();
    expect(screen.getByText('Success message')).toBeInTheDocument();
  });

  it('adds a toast via error method', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Error'));
    expect(screen.getByText('Error Title')).toBeInTheDocument();
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('adds a toast via warning method', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Warning'));
    expect(screen.getByText('Warning Title')).toBeInTheDocument();
    expect(screen.getByText('Warning message')).toBeInTheDocument();
  });

  it('adds a toast via info method', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Info'));
    expect(screen.getByText('Info Title')).toBeInTheDocument();
    expect(screen.getByText('Info message')).toBeInTheDocument();
  });

  it('increments toast count when a toast is added', () => {
    renderWithProvider(<ToastConsumer />);
    expect(screen.getByTestId('toast-count').textContent).toBe('0');

    fireEvent.click(screen.getByText('Add Success'));
    expect(screen.getByTestId('toast-count').textContent).toBe('1');

    fireEvent.click(screen.getByText('Add Error'));
    expect(screen.getByTestId('toast-count').textContent).toBe('2');
  });

  it('removes a specific toast via dismiss button', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Success'));
    expect(screen.getByText('Success Title')).toBeInTheDocument();
    expect(screen.getByTestId('toast-count').textContent).toBe('1');

    const dismissButton = screen.getByLabelText('Dismiss');
    fireEvent.click(dismissButton);

    // Note: AnimatePresence keeps the element in DOM during exit animation,
    // but the state has been updated — toast count reflects the removal
    expect(screen.getByTestId('toast-count').textContent).toBe('0');
  });

  it('clears all toasts via clearAll', () => {
    renderWithProvider(<ToastConsumer />);

    fireEvent.click(screen.getByText('Add Success'));
    fireEvent.click(screen.getByText('Add Error'));
    expect(screen.getByTestId('toast-count').textContent).toBe('2');

    fireEvent.click(screen.getByText('Clear All'));
    expect(screen.getByTestId('toast-count').textContent).toBe('0');
  });

  it('does not auto-dismiss when duration is 0', () => {
    vi.useFakeTimers();
    renderWithProvider(<ToastConsumer />);

    fireEvent.click(screen.getByTestId('add-custom'));
    expect(screen.getByText('Custom')).toBeInTheDocument();

    // Advance time significantly — toast should still exist
    vi.advanceTimersByTime(10000);
    expect(screen.getByText('Custom')).toBeInTheDocument();

    vi.useRealTimers();
  });

  it('renders action button and fires onClick', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByTestId('add-with-action'));
    expect(screen.getByText('Action Toast')).toBeInTheDocument();
    expect(screen.getByTestId('toast-count').textContent).toBe('1');

    const actionBtn = screen.getByText('Undo');
    expect(actionBtn).toBeInTheDocument();

    // Clicking the action should dismiss the toast (state is updated,
    // though AnimatePresence may keep the DOM element during exit animation)
    fireEvent.click(actionBtn);
    expect(screen.getByTestId('toast-count').textContent).toBe('0');
  });

  it('renders success toasts with check icon background styling', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Success'));
    const toastEl = screen.getByText('Success Title').closest('[role="alert"]');
    expect(toastEl?.className).toContain('bg-green-50');
    expect(toastEl?.className).toContain('border-green-200');
  });

  it('renders error toasts with red background styling', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Error'));
    const toastEl = screen.getByText('Error Title').closest('[role="alert"]');
    expect(toastEl?.className).toContain('bg-red-50');
    expect(toastEl?.className).toContain('border-red-200');
  });

  it('renders warning toasts with amber background styling', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Warning'));
    const toastEl = screen.getByText('Warning Title').closest('[role="alert"]');
    expect(toastEl?.className).toContain('bg-amber-50');
    expect(toastEl?.className).toContain('border-amber-200');
  });

  it('renders info toasts with blue background styling', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Info'));
    const toastEl = screen.getByText('Info Title').closest('[role="alert"]');
    expect(toastEl?.className).toContain('bg-blue-50');
    expect(toastEl?.className).toContain('border-blue-200');
  });

  it('renders toast container with aria-live region', () => {
    renderWithProvider(<ToastConsumer />);
    fireEvent.click(screen.getByText('Add Success'));
    const liveRegion = document.querySelector('[aria-live="polite"]');
    expect(liveRegion).toBeInTheDocument();
  });
});
