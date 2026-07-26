/**
 * Unit tests for the Withdraw Page (instructor withdrawal/payout workflow).
 *
 * Covers:
 * - Loading state (profile skeleton)
 * - Non-instructor access denied (error state)
 * - Balance cards display (current balance, pending, total earned)
 * - Withdraw form UI (amount input, payment method selection)
 * - Withdrawal history list rendering with status badges
 * - Create withdrawal flow (success and error)
 * - Cancel withdrawal action
 * - Error and success message displays
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetProfileQuery = vi.fn();
const mockUseGetWithdrawalSummaryQuery = vi.fn();
const mockUseCreateWithdrawalMutation = vi.fn();
const mockUseCancelWithdrawalMutation = vi.fn();

// Shared mutable state for mutation hooks (matches RTK Query tuple pattern)
const createMutationState = { isLoading: false };

vi.mock('@/store/api/endpoints/auth', () => ({
  useGetProfileQuery: (...args: unknown[]) => mockUseGetProfileQuery(...args),
}));

vi.mock('@/store/api/endpoints/withdrawals', () => ({
  useGetWithdrawalSummaryQuery: (...args: unknown[]) =>
    mockUseGetWithdrawalSummaryQuery(...args),
  useCreateWithdrawalMutation: () => [mockUseCreateWithdrawalMutation, createMutationState],
  useCancelWithdrawalMutation: () => [mockUseCancelWithdrawalMutation],
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const MOCK_INSTRUCTOR_PROFILE = {
  id: 1,
  username: 'instructor1',
  first_name: 'Jane',
  role: 'instructor',
};

const MOCK_STUDENT_PROFILE = {
  id: 2,
  username: 'student1',
  first_name: 'Bob',
  role: 'student',
};

const MOCK_WITHDRAWAL_SUMMARY = {
  current_balance: 1250.00,
  pending_amount: 200.00,
  total_withdrawn: 450.00,
  total_earned: 1900.00,
  pending_count: 1,
  recent_withdrawals: [
    {
      id: 3,
      instructor: 1,
      instructor_name: 'Jane',
      amount: 200.00,
      current_balance: 1450.00,
      status: 'pending' as const,
      status_display: 'Pending',
      payment_method: 'paypal',
      payment_method_display: 'PayPal',
      payment_details: {},
      notes: '',
      reference: '',
      processed_by: null,
      created_at: '2026-07-20T10:00:00Z',
      updated_at: '2026-07-20T10:00:00Z',
      processed_at: null,
      can_cancel: true,
      is_completed: false,
      is_pending: true,
    },
    {
      id: 2,
      instructor: 1,
      instructor_name: 'Jane',
      amount: 150.00,
      current_balance: 1650.00,
      status: 'completed' as const,
      status_display: 'Completed',
      payment_method: 'paypal',
      payment_method_display: 'PayPal',
      payment_details: {},
      notes: '',
      reference: 'PP-123456',
      processed_by: 5,
      created_at: '2026-07-15T08:00:00Z',
      updated_at: '2026-07-16T12:00:00Z',
      processed_at: '2026-07-16T12:00:00Z',
      can_cancel: false,
      is_completed: true,
      is_pending: false,
    },
    {
      id: 1,
      instructor: 1,
      instructor_name: 'Jane',
      amount: 300.00,
      current_balance: 1800.00,
      status: 'rejected' as const,
      status_display: 'Rejected',
      payment_method: 'bank_transfer',
      payment_method_display: 'Bank Transfer',
      payment_details: {},
      notes: 'Invalid account details provided',
      reference: '',
      processed_by: 5,
      created_at: '2026-07-10T14:00:00Z',
      updated_at: '2026-07-12T09:00:00Z',
      processed_at: '2026-07-12T09:00:00Z',
      can_cancel: false,
      is_completed: false,
      is_pending: false,
    },
  ],
};

const EMPTY_SUMMARY = {
  current_balance: 0,
  pending_amount: 0,
  total_withdrawn: 0,
  total_earned: 0,
  pending_count: 0,
  recent_withdrawals: [],
};

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import DashboardWithdrawPage from '@/app/dashboard/withdraw/page';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <DashboardWithdrawPage />
    </Provider>,
  );
}

function setupInstructorMocks(summaryData = MOCK_WITHDRAWAL_SUMMARY) {
  mockUseGetProfileQuery.mockReturnValue({
    data: MOCK_INSTRUCTOR_PROFILE,
    isLoading: false,
    error: undefined,
  });
  mockUseGetWithdrawalSummaryQuery.mockReturnValue({
    data: summaryData,
    isLoading: false,
    error: undefined,
    refetch: vi.fn(),
  });
  const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 99 } });
  mockUseCreateWithdrawalMutation.mockReturnValue({ unwrap: unwrapFn });
  // Default cancel mock — returns a no-op unwrap so the component doesn't crash
  mockUseCancelWithdrawalMutation.mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) });
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('Withdraw Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── Loading State ──

  it('shows loading skeleton while profile is loading', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: undefined,
    });

    const { container } = renderPage();

    expect(screen.queryByText('Withdrawals & Payouts')).not.toBeInTheDocument();
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  // ── Auth / Role Check ──

  it('shows error state when user is not signed in', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Not authenticated'),
    });

    renderPage();

    expect(
      screen.getByText(/This page is only available for instructors/i),
    ).toBeInTheDocument();
  });

  it('shows error state when user is a student (not instructor)', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_STUDENT_PROFILE,
      isLoading: false,
      error: undefined,
    });

    renderPage();

    expect(
      screen.getByText(/This page is only available for instructors/i),
    ).toBeInTheDocument();
  });

  it('shows error state when no profile data exists', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: undefined,
    });

    renderPage();

    expect(
      screen.getByText(/This page is only available for instructors/i),
    ).toBeInTheDocument();
  });

  // ── Page Header ──

  it('renders the page heading and description for instructors', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('Withdrawals & Payouts')).toBeInTheDocument();
    expect(
      screen.getByText('Manage your earnings and withdrawal requests'),
    ).toBeInTheDocument();
  });

  // ── Balance Cards ──

  it('displays current balance from summary', () => {
    setupInstructorMocks();
    renderPage();

    // Current balance is $1,250 — use getAllByText since $1,250 also appears in the form submit button label
    const balanceAmounts = screen.getAllByText(/\$1,250/);
    expect(balanceAmounts.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Available for withdrawal')).toBeInTheDocument();
  });

  it('displays pending payout amount', () => {
    setupInstructorMocks();
    renderPage();

    // $200 appears in both the pending payout card and the history list
    const pendingAmounts = screen.getAllByText('$200');
    expect(pendingAmounts.length).toBeGreaterThanOrEqual(1);
  });

  it('displays total earned amount', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('$1,900')).toBeInTheDocument();
  });

  it('shows loading skeleton in balance cards while summary loads', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: undefined,
    });

    const { container } = renderPage();

    // Balance card should show skeleton
    const skeletonDivs = container.querySelectorAll('.animate-pulse');
    expect(skeletonDivs.length).toBeGreaterThanOrEqual(1);
  });

  it('shows zero balances when summary has no data', () => {
    setupInstructorMocks(EMPTY_SUMMARY);
    renderPage();

    // $0 appears in multiple balance cards when there's no data
    const zeroAmounts = screen.getAllByText('$0');
    expect(zeroAmounts.length).toBeGreaterThanOrEqual(1);
  });

  // ── Withdraw Form ──

  it('renders the withdraw form section', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('Request Withdrawal')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('0.00')).toBeInTheDocument();
  });

  it('shows minimum withdrawal amount hint', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('Minimum withdrawal: $50.00')).toBeInTheDocument();
  });

  it('renders payment method selection (PayPal and Bank Transfer)', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('PayPal')).toBeInTheDocument();
    expect(screen.getByText('Bank Transfer')).toBeInTheDocument();
  });

  it('defaults to PayPal as selected payment method', () => {
    setupInstructorMocks();
    renderPage();

    const paypalBtn = screen.getByText('PayPal').closest('button');
    expect(paypalBtn).toHaveClass('border-[rgb(var(--ctc-primary))]');
  });

  it('switches payment method when Bank Transfer is clicked', () => {
    setupInstructorMocks();
    renderPage();

    const bankBtn = screen.getByText('Bank Transfer').closest('button');
    fireEvent.click(bankBtn!);

    expect(bankBtn).toHaveClass('border-[rgb(var(--ctc-primary))]');

    const paypalBtn = screen.getByText('PayPal').closest('button');
    expect(paypalBtn).not.toHaveClass('border-[rgb(var(--ctc-primary))]');
  });

  it('disables submit button when amount is empty', () => {
    setupInstructorMocks();
    renderPage();

    const submitBtn = screen.getByRole('button', { name: /withdraw/i });
    expect(submitBtn).toBeDisabled();
  });

  it('disables submit button when amount is below minimum ($50)', () => {
    setupInstructorMocks();
    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '20' } });

    const submitBtn = screen.getByRole('button', { name: /withdraw/i });
    expect(submitBtn).toBeDisabled();
  });

  it('disables submit button when amount exceeds current balance', () => {
    setupInstructorMocks();
    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '5000' } });

    const submitBtn = screen.getByRole('button', { name: /withdraw/i });
    expect(submitBtn).toBeDisabled();
  });

  it('enables submit button when a valid amount is entered', () => {
    setupInstructorMocks();
    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '100' } });

    const submitBtn = screen.getByText(/withdraw.*100/i);
    expect(submitBtn).toBeEnabled();
  });

  it('shows Processing... state when creating withdrawal', () => {
    createMutationState.isLoading = true;
    setupInstructorMocks();
    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '100' } });

    expect(screen.getByText('Processing...')).toBeInTheDocument();
    createMutationState.isLoading = false;
  });

  // ── Create Withdrawal ──

  it('calls createWithdrawal when form is submitted', async () => {
    const refetchFn = vi.fn();
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 99 } });
    mockUseCreateWithdrawalMutation.mockReturnValue({ unwrap: unwrapFn });
    createMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: MOCK_WITHDRAWAL_SUMMARY,
      isLoading: false,
      error: undefined,
      refetch: refetchFn,
    });

    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '100' } });

    const submitBtn = screen.getByText(/withdraw.*100/i);
    fireEvent.click(submitBtn);

    await vi.waitFor(() => {
      expect(mockUseCreateWithdrawalMutation).toHaveBeenCalledWith({
        amount: 100,
        payment_method: 'paypal',
        payment_details: {},
      });
      expect(refetchFn).toHaveBeenCalled();
    });
  });

  it('shows success message after successful withdrawal', async () => {
    const refetchFn = vi.fn();
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 99 } });
    mockUseCreateWithdrawalMutation.mockReturnValue({ unwrap: unwrapFn });
    createMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: MOCK_WITHDRAWAL_SUMMARY,
      isLoading: false,
      error: undefined,
      refetch: refetchFn,
    });

    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '100' } });
    fireEvent.click(screen.getByText(/withdraw.*100/i));

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Withdrawal of \$100 requested successfully!/i),
      ).toBeInTheDocument();
    });
  });

  it('shows error message when withdrawal fails', async () => {
    const refetchFn = vi.fn();
    const unwrapFn = vi.fn().mockRejectedValue({
      data: { message: 'Insufficient balance. Available: $0.00' },
    });
    mockUseCreateWithdrawalMutation.mockReturnValue({ unwrap: unwrapFn });
    createMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: MOCK_WITHDRAWAL_SUMMARY,
      isLoading: false,
      error: undefined,
      refetch: refetchFn,
    });

    renderPage();

    const input = screen.getByPlaceholderText('0.00');
    fireEvent.change(input, { target: { value: '100' } });
    fireEvent.click(screen.getByText(/withdraw.*100/i));

    await vi.waitFor(() => {
      expect(
        screen.getByText('Insufficient balance. Available: $0.00'),
      ).toBeInTheDocument();
    });
  });

  // ── Client-Side Validation ──
  // The submit button is disabled when amount is < $50 or > balance.
  // This IS the client-side validation — React ignores click events on
  // disabled buttons, so clicking the button cannot trigger handleWithdraw.
  // Button-disabled tests above ("disables submit button when amount is
  // below minimum" and "disables submit button when amount exceeds balance")
  // already validate this behavior.

  // ── Withdrawal History ──

  it('renders the withdrawal history section', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('Withdrawal History')).toBeInTheDocument();
  });

  it('shows withdrawal count in history header', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('(3)')).toBeInTheDocument();
  });

  it('renders all withdrawal amounts in the history list', () => {
    setupInstructorMocks();
    renderPage();

    // $200 appears in both the pending payout card and the history — use getAllByText
    expect(screen.getByText('$150')).toBeInTheDocument();
    expect(screen.getByText('$300')).toBeInTheDocument();
    // $200 appears in the pending payout card AND the history entry — both should be present
    const twoHundreds = screen.getAllByText('$200');
    expect(twoHundreds.length).toBeGreaterThanOrEqual(1);
  });

  it('renders status badges for each withdrawal', () => {
    setupInstructorMocks();
    renderPage();

    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Rejected')).toBeInTheDocument();
  });

  it('shows payment method display for each withdrawal', () => {
    setupInstructorMocks();
    renderPage();

    // PayPal appears in the form button AND history items (pending + completed)
    const paypalLabels = screen.getAllByText('PayPal');
    expect(paypalLabels.length).toBeGreaterThanOrEqual(1);
    // Bank Transfer for the third (rejected)
    expect(screen.getByText('Bank Transfer')).toBeInTheDocument();
  });

  it('shows Cancel button only for pending withdrawals', () => {
    setupInstructorMocks();
    renderPage();

    const cancelButtons = screen.getAllByText('Cancel');
    // Only the pending withdrawal (id: 3) should have a Cancel button
    expect(cancelButtons.length).toBe(1);
  });

  it('shows empty state when no withdrawals exist', () => {
    setupInstructorMocks(EMPTY_SUMMARY);
    renderPage();

    expect(screen.getByText('No withdrawals yet')).toBeInTheDocument();
    expect(
      screen.getByText('Your payout requests will appear here'),
    ).toBeInTheDocument();
  });

  // ── Cancel Withdrawal ──

  it('calls cancelWithdrawal when Cancel button is clicked', async () => {
    const refetchFn = vi.fn();
    const cancelUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseCancelWithdrawalMutation.mockReturnValue({ unwrap: cancelUnwrap });

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: MOCK_WITHDRAWAL_SUMMARY,
      isLoading: false,
      error: undefined,
      refetch: refetchFn,
    });

    renderPage();

    // Click Cancel on the pending withdrawal
    fireEvent.click(screen.getByText('Cancel'));

    await vi.waitFor(() => {
      expect(cancelUnwrap).toHaveBeenCalled();
      expect(refetchFn).toHaveBeenCalled();
    });
  });

  it('shows error message when cancel fails', async () => {
    const cancelUnwrap = vi.fn().mockRejectedValue({
      data: { message: 'Only pending withdrawals can be cancelled' },
    });
    mockUseCancelWithdrawalMutation.mockReturnValue({ unwrap: cancelUnwrap });

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: MOCK_WITHDRAWAL_SUMMARY,
      isLoading: false,
      error: undefined,
      refetch: vi.fn(),
    });

    renderPage();

    fireEvent.click(screen.getByText('Cancel'));

    await vi.waitFor(() => {
      expect(
        screen.getByText('Only pending withdrawals can be cancelled'),
      ).toBeInTheDocument();
    });
  });

  // ── Refresh ──

  it('has a Refresh button that refetches data', () => {
    const refetchFn = vi.fn();
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_INSTRUCTOR_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetWithdrawalSummaryQuery.mockReturnValue({
      data: MOCK_WITHDRAWAL_SUMMARY,
      isLoading: false,
      error: undefined,
      refetch: refetchFn,
    });

    renderPage();

    fireEvent.click(screen.getByText('Refresh'));
    expect(refetchFn).toHaveBeenCalled();
  });
});
