/**
 * Unit tests for the NotificationBell component.
 *
 * Covers:
 * - Renders outline bell when no unread notifications
 * - Renders filled bell with pulse when unread
 * - Shows unread count badge (single digit, double digit, 99+)
 * - Opens dropdown on click
 * - Closes dropdown on outside click
 * - Sets aria-label with unread count
 * - Closes dropdown when NotificationDropdown calls onClose
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetUnreadCountQuery = vi.fn();

vi.mock('@/store/api/endpoints/notifications', () => ({
  useGetUnreadCountQuery: (...args: unknown[]) => mockUseGetUnreadCountQuery(...args),
  useGetNotificationsQuery: () => ({
    data: { results: [], count: 0 },
    isLoading: false,
  }),
  useMarkNotificationReadMutation: () => [vi.fn(), { isLoading: false }],
  useMarkAllNotificationsReadMutation: () => [vi.fn(), { isLoading: false }],
}));

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import NotificationBell from '@/components/NotificationBell';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <NotificationBell />
    </Provider>,
  );
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('NotificationBell', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders outline bell icon when there are no unread notifications', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 0 } },
    });

    renderPage();

    const button = screen.getByRole('button', { name: /Notifications/ });
    expect(button).toBeInTheDocument();
    // Should show outline bell (no pulse class when hasUnread is false)
    expect(button.querySelector('.animate-pulse')).toBeFalsy();
  });

  it('renders filled bell with pulse animation when there are unread notifications', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 3 } },
    });

    renderPage();

    const button = screen.getByRole('button', { name: /Notifications/ });
    expect(button).toBeInTheDocument();
    // Should show filled bell with pulse class
    expect(button.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('shows unread count badge with correct number', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 5 } },
    });

    renderPage();

    // The badge should display "5"
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('shows "99+" when unread count exceeds 99', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 150 } },
    });

    renderPage();

    expect(screen.getByText('99+')).toBeInTheDocument();
  });

  it('sets aria-label with unread count', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 3 } },
    });

    renderPage();

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Notifications (3 unread)');
  });

  it('sets aria-label without unread count when zero', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 0 } },
    });

    renderPage();

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Notifications');
  });

  it('does not show badge when unread count is zero', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 0 } },
    });

    renderPage();

    // The badge is a span with red background — should not exist
    const badges = document.querySelectorAll('span.bg-red-500');
    expect(badges.length).toBe(0);
  });

  it('handles undefined unread count gracefully', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: undefined,
    });

    renderPage();

    const button = screen.getByRole('button', { name: /Notifications/ });
    expect(button).toBeInTheDocument();
    // No badge should show when data is undefined
    const badges = document.querySelectorAll('span.bg-red-500');
    expect(badges.length).toBe(0);
  });

  it('opens dropdown when bell icon is clicked', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 2 } },
    });

    renderPage();

    const button = screen.getByRole('button');
    fireEvent.click(button);

    // Dropdown should be visible — it contains "Notifications" heading
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('closes dropdown when clicked again', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 0 } },
    });

    renderPage();

    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByText('Notifications')).toBeInTheDocument();

    fireEvent.click(button);
    expect(screen.queryByText('Notifications')).not.toBeInTheDocument();
  });

  it('closes dropdown when clicking outside', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 0 } },
    });

    renderPage();

    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByText('Notifications')).toBeInTheDocument();

    // Click outside the dropdown ref
    fireEvent.mouseDown(document.body);
    expect(screen.queryByText('Notifications')).not.toBeInTheDocument();
  });

  it('polls unread count every 30 seconds', () => {
    mockUseGetUnreadCountQuery.mockReturnValue({
      data: { status: 'success', data: { unread_count: 0 } },
    });

    renderPage();

    // The query should be called with pollingInterval: 30000
    expect(mockUseGetUnreadCountQuery).toHaveBeenCalledWith(undefined, {
      pollingInterval: 30000,
    });
  });
});
