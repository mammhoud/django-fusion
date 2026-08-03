/**
 * Tests for the student-dashboard page loading behavior.
 *
 * Covers:
 * - Shows skeleton placeholders (not "0") for the stat cards while the
 *   dashboard / enrollments APIs are loading
 * - Shows real stat values once the APIs respond
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock RTK Query hooks ──

const mockUseGetProfileQuery = vi.fn();
const mockUseGetDashboardQuery = vi.fn();
const mockUseGetStudentEnrollmentsQuery = vi.fn();

vi.mock('@/store/api/endpoints/auth', () => ({
  useGetProfileQuery: (...args: unknown[]) => mockUseGetProfileQuery(...args),
  useLoginMutation: vi.fn(),
  useLogoutMutation: vi.fn(),
  useRegisterMutation: vi.fn(),
}));

vi.mock('@/store/api/endpoints/students', () => ({
  useGetDashboardQuery: (...args: unknown[]) => mockUseGetDashboardQuery(...args),
  useGetStudentEnrollmentsQuery: (...args: unknown[]) =>
    mockUseGetStudentEnrollmentsQuery(...args),
  useGetStudentsQuery: vi.fn(),
  useGetStudentQuery: vi.fn(),
  useGetEnrollmentProgressQuery: vi.fn(),
  useEnrollInCourseMutation: vi.fn(),
  useUpdateProgressMutation: vi.fn(),
  useInitializePaymentMutation: vi.fn(),
  useVerifyPaymentMutation: vi.fn(),
}));

// ── Import page AFTER mocks ──

import StudentDashboardPage from '@/app/student-dashboard/page';

// ── Test data ──

const studentProfile = { id: 2, first_name: 'Mike', username: 'mike_student' };

// ── Helpers ──

function createStore() {
  return configureStore({ reducer: (state: any) => state ?? {} });
}

function renderPage() {
  return render(
    <Provider store={createStore()}>
      <ToastProvider>
        <StudentDashboardPage />
      </ToastProvider>
    </Provider>,
  );
}

// ── Tests ──

describe('StudentDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetProfileQuery.mockReturnValue({
      data: studentProfile,
      isLoading: false,
    });
  });

  it('shows skeleton placeholders (not 0) while dashboard APIs load', () => {
    mockUseGetDashboardQuery.mockReturnValue({ data: undefined, isLoading: true });
    mockUseGetStudentEnrollmentsQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    const { container } = renderPage();

    expect(screen.getByText('Welcome back, Mike!')).toBeInTheDocument();

    // Stat cards render pulse placeholders while the APIs are in flight
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0);
    // No premature "0" values in the stat cards
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('shows real stat values once the APIs respond', () => {
    mockUseGetDashboardQuery.mockReturnValue({
      data: { enrolled_courses: 3, completed_courses: 1, total_hours: 45 },
      isLoading: false,
    });
    mockUseGetStudentEnrollmentsQuery.mockReturnValue({
      data: [
        {
          id: 1,
          course: 10,
          course_title: 'Python Basics',
          enrolled_at: '2024-01-15T00:00:00Z',
          progress: 60,
          is_completed: false,
          course_thumbnail: null,
        },
      ],
      isLoading: false,
    });

    renderPage();

    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('Python Basics')).toBeInTheDocument();
  });
});
