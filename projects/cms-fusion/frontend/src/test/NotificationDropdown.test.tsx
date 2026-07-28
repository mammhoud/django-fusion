/**
 * Unit tests for the NotificationDropdown component.
 *
 * Covers:
 * - Loading spinner state
 * - Empty state (no notifications)
 * - Notification list rendering (title, message, time_ago, type icon)
 * - Unread indicator (blue dot, bold title)
 * - Read notification styling (normal weight, no dot)
 * - Marking a notification as read on click
 * - Mark all read button visibility
 * - Mark all read action
 * - "View all notifications" footer link
 * - onClose callback on notification click
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetNotificationsQuery = vi.fn();
const mockUseMarkNotificationReadMutation = vi.fn();
const mockUseMarkAllNotificationsReadMutation = vi.fn();

const markReadMutationState = { isLoading: false };
const markAllReadMutationState = { isLoading: false };

vi.mock('@/store/api/endpoints/notifications', () => ({
  useGetNotificationsQuery: (...args: unknown[]) => mockUseGetNotificationsQuery(...args),
  useMarkNotificationReadMutation: () => [mockUseMarkNotificationReadMutation, markReadMutationState],
  useMarkAllNotificationsReadMutation: () => [mockUseMarkAllNotificationsReadMutation, markAllReadMutationState],
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => <a href={href} {...props}>{children}</a>,
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const MOCK_NOTIFICATIONS = [
  {
    id: 1,
    type: 'enrollment',
    type_label: 'Enrollment',
    title: 'Enrolled in React Fundamentals',
    message: 'You have successfully enrolled in React Fundamentals.',
    link: '/course-details/1/',
    is_read: false,
    created_at: '2026-07-25T10:00:00Z',
    time_ago: '2m ago',
  },
  {
    id: 2,
    type: 'grading',
    type_label: 'Grading',
    title: 'Grade Posted: Week 3 Homework',
    message: 'Your grade for Week 3 Homework has been posted: 85.',
    link: '/dashboard/',
    is_read: true,
    created_at: '2026-07-25T09:00:00Z',
    time_ago: '1h ago',
  },
  {
    id: 3,
    type: 'quiz',
    type_label: 'Quiz',
    title: 'Quiz Result: React Fundamentals Quiz',
    message: 'You scored 80% on React Fundamentals Quiz.',
    link: '/dashboard/',
    is_read: false,
    created_at: '2026-07-25T08:00:00Z',
    time_ago: '2h ago',
  },
  {
    id: 4,
    type: 'system',
    type_label: 'System',
    title: 'Welcome to the platform!',
    message: '',
    link: '',
    is_read: false,
    created_at: '2026-07-24T00:00:00Z',
    time_ago: '1d ago',
  },
];

function createNotificationsResponse(notifications: typeof MOCK_NOTIFICATIONS) {
  return {
    results: notifications,
    count: notifications.length,
    next: null,
    previous: null,
  };
}

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import NotificationDropdown from '@/components/NotificationDropdown';

function renderDropdown(onClose?: () => void) {
  const closeFn = onClose || vi.fn();
  return render(
    <Provider store={createTestStore()}>
      <NotificationDropdown onClose={closeFn} />
    </Provider>,
  );
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('NotificationDropdown - Loading State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading spinner while notifications are loading', () => {
    mockUseGetNotificationsQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    renderDropdown();

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    // Spinning loader should be present
    expect(document.querySelector('.animate-spin')).toBeTruthy();
  });
});

describe('NotificationDropdown - Empty State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetNotificationsQuery.mockReturnValue({
      data: createNotificationsResponse([]),
      isLoading: false,
    });
  });

  it('shows empty state when there are no notifications', () => {
    renderDropdown();

    expect(screen.getByText('No notifications yet')).toBeInTheDocument();
    expect(
      screen.getByText(/We'll notify you when something arrives/),
    ).toBeInTheDocument();
  });

  it('does not show Mark all read button when there are no notifications', () => {
    renderDropdown();

    expect(screen.queryByText('Mark all read')).not.toBeInTheDocument();
  });
});

describe('NotificationDropdown - Notification List', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetNotificationsQuery.mockReturnValue({
      data: createNotificationsResponse(MOCK_NOTIFICATIONS),
      isLoading: false,
    });
  });

  it('renders the header with title', () => {
    renderDropdown();

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('renders notification titles', () => {
    renderDropdown();

    expect(screen.getByText('Enrolled in React Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Grade Posted: Week 3 Homework')).toBeInTheDocument();
    expect(screen.getByText('Quiz Result: React Fundamentals Quiz')).toBeInTheDocument();
    expect(screen.getByText('Welcome to the platform!')).toBeInTheDocument();
  });

  it('renders notification messages when present', () => {
    renderDropdown();

    expect(
      screen.getByText('You have successfully enrolled in React Fundamentals.'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Your grade for Week 3 Homework has been posted: 85.'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('You scored 80% on React Fundamentals Quiz.'),
    ).toBeInTheDocument();
  });

  it('renders time_ago for each notification', () => {
    renderDropdown();

    expect(screen.getByText('2m ago')).toBeInTheDocument();
    expect(screen.getByText('1h ago')).toBeInTheDocument();
    expect(screen.getByText('2h ago')).toBeInTheDocument();
    expect(screen.getByText('1d ago')).toBeInTheDocument();
  });

  it('shows type-specific emoji icons', () => {
    renderDropdown();

    // Enrollment type icon
    expect(screen.getByText('📝')).toBeInTheDocument();
    // Grading type icon
    expect(screen.getByText('✅')).toBeInTheDocument();
    // Quiz type icon
    expect(screen.getByText('📊')).toBeInTheDocument();
    // System type icon (default)
    expect(screen.getByText('🔔')).toBeInTheDocument();
  });

  it('shows unread indicator (blue dot) for unread notifications', () => {
    renderDropdown();

    // Unread notifications should have the blue dot
    const dots = document.querySelectorAll('span.bg-\\[rgb\\(var\\(--fu-primary\\)\\)\\]');
    // 3 unread notifications should have 3 dots
    expect(dots.length).toBe(3);
  });

  it('shows Mark all read button when there are unread notifications', () => {
    renderDropdown();

    expect(screen.getByText('Mark all read')).toBeInTheDocument();
  });

  it('renders "View all notifications" footer link', () => {
    renderDropdown();

    const viewAllLink = screen.getByText('View all notifications');
    expect(viewAllLink).toBeInTheDocument();
    expect(viewAllLink.closest('a')).toHaveAttribute('href', '/dashboard/notifications');
  });
});

describe('NotificationDropdown - Interactions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetNotificationsQuery.mockReturnValue({
      data: createNotificationsResponse(MOCK_NOTIFICATIONS),
      isLoading: false,
    });
  });

  it('calls markNotificationRead when clicking an unread notification', async () => {
    const markUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseMarkNotificationReadMutation.mockReturnValue({ unwrap: markUnwrap });
    markReadMutationState.isLoading = false;

    const onClose = vi.fn();
    renderDropdown(onClose);

    // Click the first unread notification
    fireEvent.click(screen.getByText('Enrolled in React Fundamentals'));

    await vi.waitFor(() => {
      expect(mockUseMarkNotificationReadMutation).toHaveBeenCalledWith(1);
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('does not call markNotificationRead when clicking a read notification', async () => {
    const markUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseMarkNotificationReadMutation.mockReturnValue({ unwrap: markUnwrap });
    markReadMutationState.isLoading = false;

    const onClose = vi.fn();
    renderDropdown(onClose);

    // Click the read notification (Grade Posted)
    fireEvent.click(screen.getByText('Grade Posted: Week 3 Homework'));

    await vi.waitFor(() => {
      // is_read is true, so markRead should NOT be called
      expect(mockUseMarkNotificationReadMutation).not.toHaveBeenCalled();
      // But onClose should still be called
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('calls markAllNotificationsRead when Mark all read is clicked', async () => {
    const markAllUnwrap = vi.fn().mockResolvedValue({ status: 'success', data: { marked_read: 4 } });
    mockUseMarkAllNotificationsReadMutation.mockReturnValue({ unwrap: markAllUnwrap });
    markAllReadMutationState.isLoading = false;

    renderDropdown();

    fireEvent.click(screen.getByText('Mark all read'));

    await vi.waitFor(() => {
      expect(mockUseMarkAllNotificationsReadMutation).toHaveBeenCalled();
    });
  });

  it('calls onClose when clicking the footer "View all notifications" link', () => {
    const onClose = vi.fn();
    renderDropdown(onClose);

    fireEvent.click(screen.getByText('View all notifications'));

    expect(onClose).toHaveBeenCalled();
  });
});
