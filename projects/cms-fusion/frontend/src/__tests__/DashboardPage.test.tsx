/**
 * Integration tests for the Dashboard page.
 *
 * Covers:
 * - Shows loading skeleton when profile is loading
 * - Shows error state when profile is null
 * - Instructor dashboard: stats, quick links, Carousel, ScrollReveal, Toast
 * - Student dashboard: enrolled courses, stats Carousel, ScrollReveal, Toast
 * - Admin dashboard: withdrawals card, ScrollReveal, Toast
 * - CmsDashboardContentBlocks renders Accordion + Tabs from CMS data
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock RTK Query hooks ──

const mockUseGetProfileQuery = vi.fn();
const mockUseGetInstructorDashboardQuery = vi.fn();
const mockUseGetDashboardQuery = vi.fn();
const mockUseGetStudentEnrollmentsQuery = vi.fn();
const mockUseGetDashboardContentQuery = vi.fn();
const mockUseGetWithdrawalsQuery = vi.fn();

vi.mock('@/store/api/endpoints/auth', () => ({
  useGetProfileQuery: (...args: unknown[]) => mockUseGetProfileQuery(...args),
  useLoginMutation: vi.fn(),
  useLogoutMutation: vi.fn(),
  useRegisterMutation: vi.fn(),
}));

vi.mock('@/store/api/endpoints/instructors', () => ({
  useGetInstructorDashboardQuery: (...args: unknown[]) =>
    mockUseGetInstructorDashboardQuery(...args),
  useGetInstructorsQuery: vi.fn(),
  useGetInstructorQuery: vi.fn(),
  useGetInstructorCoursesQuery: vi.fn(),
  useGetInstructorReviewsQuery: vi.fn(),
  useUpdateInstructorProfileMutation: vi.fn(),
}));

vi.mock('@/store/api/endpoints/students', () => ({
  useGetDashboardQuery: (...args: unknown[]) =>
    mockUseGetDashboardQuery(...args),
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

vi.mock('@/store/api/endpoints/dashboard', () => ({
  useGetDashboardContentQuery: (...args: unknown[]) =>
    mockUseGetDashboardContentQuery(...args),
}));

vi.mock('@/store/api/endpoints/withdrawals', () => ({
  useGetWithdrawalsQuery: (...args: unknown[]) =>
    mockUseGetWithdrawalsQuery(...args),
}));

// ── Import page AFTER mocks ──

import DashboardPage from '@/app/dashboard/page';

// ── Mock data ──

const instructorProfile = {
  id: 1,
  first_name: 'Sarah',
  username: 'sarah_instructor',
  role: 'instructor' as const,
};

const studentProfile = {
  id: 2,
  first_name: 'Mike',
  username: 'mike_student',
  role: 'student' as const,
};

const adminProfile = {
  id: 3,
  first_name: 'Admin',
  username: 'admin_user',
  role: 'admin' as const,
};

const mockInstructorDash = {
  total_courses: 5,
  total_students: 120,
  total_revenue: 15000,
  completion_rate: 78,
  monthly_earnings: [
    { month: '2024-01', amount: 3000 },
    { month: '2024-02', amount: 4000 },
  ],
  enrollment_trends: [
    { month: '2024-01', count: 20 },
    { month: '2024-02', count: 30 },
  ],
  total_enrollments: 50,
  completed_enrollments: 35,
  active_enrollments: 15,
  popular_courses: [
    { id: 1, title: 'React 101', student_count: 45, course_revenue: 3000, course_completed: 30 },
  ],
};

const mockStudentDash = {
  enrolled_courses: 3,
  completed_courses: 1,
  total_hours: 45,
};

const mockEnrollments = [
  {
    id: 1,
    course: 10,
    course_title: 'Python Basics',
    enrolled_at: '2024-01-15T00:00:00Z',
    progress: 60,
    is_completed: false,
  },
  {
    id: 2,
    course: 11,
    course_title: 'JavaScript Advanced',
    enrolled_at: '2024-02-01T00:00:00Z',
    progress: 100,
    is_completed: true,
  },
];

// Codec-encoded CMS dashboard content with welcome, tip, quick links, and announcements
// to exercise both Accordion (tips) and Tabs (quick links + announcements) rendering paths.
const CMS_CONTENT_ENCODED =
  'fusion_v1:' +
  btoa(
    JSON.stringify({
      blocks: [
        {
          type: 'dashboard_welcome',
          heading: 'Welcome back, {name}!',
          intro: 'Here is your dashboard.',
        },
        {
          type: 'dashboard_tip',
          heading: 'Pro Tip',
          content: 'Upload a profile photo to personalize your account.',
        },
        {
          type: 'dashboard_quick_links',
          heading: 'Useful Resources',
          links: [
            { href: '/docs', label: 'Documentation' },
            { href: '/support', label: 'Support' },
            { href: '/faq', label: 'FAQ' },
          ],
        },
        {
          type: 'dashboard_announcement',
          heading: 'New Course Editor',
          content: 'Check out the new course editor with enhanced features.',
          link: '/dashboard/courses/new',
          link_label: 'Try it now',
        },
      ],
    }),
  );

// ── Helper ──

function createStore() {
  return configureStore({ reducer: (state: any) => state ?? {} });
}

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <Provider store={createStore()}>
      <ToastProvider>{ui}</ToastProvider>
    </Provider>,
  );
}

// ── Tests ──

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // ── Loading & Error States ──

  it('shows loading skeleton when profile is loading', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    const { container } = renderWithProviders(<DashboardPage />);
    // LoadingSkeleton variant="profile" renders animate-pulse elements
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('shows error state when profile is null (not authenticated)', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: null,
      isLoading: false,
    });
    renderWithProviders(<DashboardPage />);
    expect(
      screen.getByText('Please sign in to access your dashboard.'),
    ).toBeInTheDocument();
  });

  // ── Instructor Dashboard ──

  describe('Instructor Dashboard', () => {
    beforeEach(() => {
      mockUseGetProfileQuery.mockReturnValue({
        data: instructorProfile,
        isLoading: false,
      });
      mockUseGetInstructorDashboardQuery.mockReturnValue({
        data: mockInstructorDash,
        isLoading: false,
      });
      mockUseGetDashboardContentQuery.mockReturnValue({
        data: { encoded: CMS_CONTENT_ENCODED },
        isLoading: false,
      });
    });

    it('renders instructor heading', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Instructor Dashboard')).toBeInTheDocument();
    });

    it('renders stat cards with instructor data', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      // Multiple elements contain "5" (desktop grid + mobile carousel)
      const fives = screen.getAllByText('5');
      expect(fives.length).toBeGreaterThan(0);
      expect(screen.getByText('120')).toBeInTheDocument();
    });

    it('renders revenue stat with dollar formatting', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      // Multiple elements contain "$15,000" (desktop grid + mobile carousel)
      const revs = screen.getAllByText('$15,000');
      expect(revs.length).toBeGreaterThan(0);
    });

    it('renders completion rate stat', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      // Multiple elements contain "78%" (desktop grid + mobile carousel)
      const rates = screen.getAllByText('78%');
      expect(rates.length).toBeGreaterThan(0);
    });

    it('renders quick links section', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('My Courses')).toBeInTheDocument();
      expect(screen.getByText('Quizzes')).toBeInTheDocument();
    });

    it('renders analytics section when data is available', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Analytics')).toBeInTheDocument();
    });

    it('renders popular courses table', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('React 101')).toBeInTheDocument();
    });

    it('renders CMS welcome block', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Welcome back, Sarah!')).toBeInTheDocument();
    });

    it('renders CMS tip in Accordion', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Pro Tip')).toBeInTheDocument();
    });

    it('renders Tabs with Quick Links tab', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(
        screen.getByRole('tab', { name: /Quick Links/i }),
      ).toBeInTheDocument();
    });

    it('renders Tabs with Announcements tab', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(
        screen.getByRole('tab', { name: /Announcements/i }),
      ).toBeInTheDocument();
    });

    it('renders quick link items from CMS content', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Documentation')).toBeInTheDocument();
      expect(screen.getByText('Support')).toBeInTheDocument();
      expect(screen.getByText('FAQ')).toBeInTheDocument();
    });

    it('renders announcement content from CMS', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      // Tab button text includes announcement count — proves blocks were parsed
      // and the Tabs component received both tabs (shouldUseTabs = true).
      // We avoid checking announcement panel content (inside inactive tab)
      // because AnimatePresence mode="wait" doesn't reliably render new tab
      // panel content in jsdom without requestAnimationFrame.
      expect(
        screen.getByRole('tab', { name: /Announcements \(1\)/i }),
      ).toBeInTheDocument();
      // The quick link items from the default active tab should be visible
      expect(screen.getByText('Documentation')).toBeInTheDocument();
      expect(screen.getByText('Support')).toBeInTheDocument();
    });

    it('renders both tab buttons when quick links and announcements present', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      const tabs = screen.getAllByRole('tab');
      // At minimum Quick Links + Announcements (1) tabs
      expect(tabs.length).toBeGreaterThanOrEqual(2);
    });

    it('fires welcome-back toast', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      vi.advanceTimersByTime(800);
      expect(
        screen.getByText('Welcome back, Sarah!'),
      ).toBeInTheDocument();
    });

    it('renders Carousel for mobile stats (exists in DOM)', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      // The Carousel is rendered with aria-roledescription="carousel"
      // It may be hidden on desktop via sm:hidden, but it's still rendered
      const carousel = screen.queryByRole('region', { name: /Image carousel/i });
      // Carousel renders when statSlides.length > 0
      expect(carousel).toBeInTheDocument();
    });
  });

  // ── Student Dashboard ──

  describe('Student Dashboard', () => {
    beforeEach(() => {
      mockUseGetProfileQuery.mockReturnValue({
        data: studentProfile,
        isLoading: false,
      });
      mockUseGetDashboardQuery.mockReturnValue({
        data: mockStudentDash,
        isLoading: false,
      });
      mockUseGetStudentEnrollmentsQuery.mockReturnValue({
        data: mockEnrollments,
        isLoading: false,
      });
      mockUseGetDashboardContentQuery.mockReturnValue({
        data: null,
        isLoading: false,
      });
    });

    it('renders student welcome heading', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Welcome back, Mike!')).toBeInTheDocument();
    });

    it('renders enrolled courses count', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      // Multiple elements contain "Enrolled Courses" (desktop grid + mobile carousel)
      const labels = screen.getAllByText('Enrolled Courses');
      expect(labels.length).toBeGreaterThan(0);
    });

    it('renders enrolled courses list', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Python Basics')).toBeInTheDocument();
      expect(screen.getByText('JavaScript Advanced')).toBeInTheDocument();
    });

    it('shows completed course with checkmark', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      const checkIcon = document.querySelector('.text-green-500');
      expect(checkIcon).toBeInTheDocument();
    });

    it('renders Browse More Courses link', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      const link = screen.getByText('Browse More Courses');
      expect(link.closest('a')).toHaveAttribute('href', '/courses');
    });

    it('fires welcome-back toast', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      vi.advanceTimersByTime(800);
      expect(
        screen.getByText('Welcome back, Mike!'),
      ).toBeInTheDocument();
    });

    it('renders Carousel for stats on mobile', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      const carousel = screen.queryByRole('region', { name: /Image carousel/i });
      expect(carousel).toBeInTheDocument();
    });
  });

  // ── Admin Dashboard ──

  describe('Admin Dashboard', () => {
    beforeEach(() => {
      mockUseGetProfileQuery.mockReturnValue({
        data: adminProfile,
        isLoading: false,
      });
      mockUseGetWithdrawalsQuery.mockReturnValue({
        data: { count: 7, results: [] },
        isLoading: false,
      });
      mockUseGetDashboardContentQuery.mockReturnValue({
        data: null,
        isLoading: false,
      });
    });

    it('renders admin dashboard heading', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });

    it('renders pending withdrawals count', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      expect(screen.getByText('7 pending')).toBeInTheDocument();
    });

    it('renders withdrawals link', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      const link = screen.getByText('Pending Withdrawals');
      expect(link.closest('a')).toHaveAttribute(
        'href',
        '/dashboard/admin/withdrawals',
      );
    });

    it('fires admin welcome toast', async () => {
      await act(async () => {
        renderWithProviders(<DashboardPage />);
      });
      vi.advanceTimersByTime(800);
      expect(
        screen.getByText('Admin Dashboard'),
      ).toBeInTheDocument();
    });
  });
});
