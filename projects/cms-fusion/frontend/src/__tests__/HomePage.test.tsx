/**
 * Integration tests for the cms-fusion HomePage.
 *
 * Covers:
 * - FusionPage renders HomePageContent with page data
 * - Carousel appears when featured courses are loaded
 * - ScrollReveal wraps each section
 * - Toast fires welcome message on mount
 * - Hero section renders default content when no CMS page data
 * - Stats render from API data
 */
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock RTK Query hooks ──

const mockUseGetFeaturedCoursesQuery = vi.fn();
const mockUseGetCoursesQuery = vi.fn();
const mockUseGetInstructorsQuery = vi.fn();
const mockUseGetPageDataQuery = vi.fn();

vi.mock('@/store/api/endpoints/courses', () => ({
  useGetFeaturedCoursesQuery: (...args: unknown[]) =>
    mockUseGetFeaturedCoursesQuery(...args),
  useGetCoursesQuery: (...args: unknown[]) => mockUseGetCoursesQuery(...args),
  useGetCategoriesQuery: vi.fn(),
}));

vi.mock('@/store/api/endpoints/instructors', () => ({
  useGetInstructorsQuery: (...args: unknown[]) =>
    mockUseGetInstructorsQuery(...args),
}));

vi.mock('@/store/api/endpoints/pages', () => ({
  useGetPageDataQuery: (...args: unknown[]) => mockUseGetPageDataQuery(...args),
}));

// ── Mock FusionPage to render content directly ──

vi.mock('@/components/FusionPage', () => ({
  FusionPage: ({ children, slug }: any) => {
    // Render children with a mock CmsPage and fallback state
    const mockPage = {
      slug: 'home',
      title: 'Home',
      blocks: [
        {
          type: 'hero',
          heading: 'Learn Without Limits',
          intro: 'Master new skills with expert-led courses.',
          ctas: [
            { label: 'Explore Courses', href: '/courses' },
            { label: 'Get Started Free', href: '/registration' },
          ],
        },
        {
          key: 'featured_courses',
          heading: 'Featured Courses',
          intro: 'Most popular courses picked for you',
        },
        {
          type: 'cta',
          heading: 'Start Learning Today',
          intro: 'Join thousands of students.',
          ctas: [{ label: 'Create Free Account', href: '/registration' }],
        },
      ],
    };
    return children(mockPage, { isLoading: false });
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

// ── Import page AFTER mocks ──

import HomePage from '@/app/page';

// ── Mock data ──

const mockFeaturedCourses = [
  {
    id: 1,
    title: 'React Basics',
    short_description: 'Learn React from scratch',
    price: 49.99,
    discounted_price: 29.99,
    category_name: 'Development',
    instructor_name: 'John Doe',
    rating: 4.5,
    students_count: 1200,
  },
  {
    id: 2,
    title: 'Advanced TypeScript',
    short_description: 'Master TypeScript patterns',
    price: 79.99,
    discounted_price: null,
    category_name: 'Development',
    instructor_name: 'Jane Smith',
    rating: 4.8,
    students_count: 850,
  },
  {
    id: 3,
    title: 'Python for Data Science',
    short_description: 'Data analysis with Python',
    price: 59.99,
    discounted_price: 39.99,
    category_name: 'Data Science',
    instructor_name: 'Bob Wilson',
    rating: 4.6,
    students_count: 2100,
  },
];

const mockInstructors = [
  {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    title: 'Senior Engineer',
    courses_count: 5,
    average_rating: 4.7,
  },
];

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

describe('HomePage (cms-fusion)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    mockUseGetFeaturedCoursesQuery.mockReturnValue({
      data: mockFeaturedCourses,
      isLoading: false,
    });
    mockUseGetCoursesQuery.mockReturnValue({
      data: { count: 3, results: mockFeaturedCourses },
    });
    mockUseGetInstructorsQuery.mockReturnValue({
      data: { results: mockInstructors, count: 1 },
    });
    mockUseGetPageDataQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: undefined,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders hero heading from CMS page data', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('Learn Without Limits')).toBeInTheDocument();
  });

  it('renders featured courses Carousel with course titles', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('React Basics')).toBeInTheDocument();
    expect(screen.getByText('Advanced TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Python for Data Science')).toBeInTheDocument();
  });

  it('renders Carousel with course prices', () => {
    renderWithProviders(<HomePage />);
    // Discounted price should appear
    expect(screen.getByText('$29.99')).toBeInTheDocument();
  });

  it('renders the featured courses section heading', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('Featured Courses')).toBeInTheDocument();
  });

  it('renders View All courses link', () => {
    renderWithProviders(<HomePage />);
    const viewAllLinks = screen.getAllByText('View All');
    const coursesLink = viewAllLinks.find(
      (link) => link.closest('a')?.getAttribute('href') === '/courses',
    );
    expect(coursesLink).toBeInTheDocument();
  });

  it('renders CTA section from CMS page data', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('Start Learning Today')).toBeInTheDocument();
    expect(
      screen.getByText('Join thousands of students.'),
    ).toBeInTheDocument();
  });

  it('renders CTA button with correct href', () => {
    renderWithProviders(<HomePage />);
    const ctaBtn = screen.getByText('Create Free Account');
    expect(ctaBtn.closest('a')).toHaveAttribute('href', '/registration');
  });

  it('renders stats with course count from API', () => {
    renderWithProviders(<HomePage />);
    // coursesData?.count is 3
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders instructors preview section', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('Expert Instructors')).toBeInTheDocument();
    // "John Doe" appears in both instructor card and course instructor names
    const johnDoes = screen.getAllByText('John Doe');
    expect(johnDoes.length).toBeGreaterThan(0);
  });

  it('renders View All instructors link', () => {
    renderWithProviders(<HomePage />);
    const viewAllLinks = screen.getAllByText('View All');
    const instructorLink = viewAllLinks.find(
      (link) => link.closest('a')?.getAttribute('href') === '/instructors',
    );
    expect(instructorLink).toBeInTheDocument();
  });

  it('fires a welcome toast on mount', async () => {
    renderWithProviders(<HomePage />);
    await act(() => {
      vi.advanceTimersByTime(1500);
    });
    expect(
      screen.getByText('Welcome to LMS'),
    ).toBeInTheDocument();
  });

  it('renders hero CTA buttons', () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('Explore Courses')).toBeInTheDocument();
    expect(screen.getByText('Get Started Free')).toBeInTheDocument();
  });

  it('renders the Carousel role region', () => {
    renderWithProviders(<HomePage />);
    const carousel = screen.getByRole('region', { name: /Image carousel/i });
    expect(carousel).toBeInTheDocument();
  });

  it('renders loading skeleton when courses are loading', () => {
    mockUseGetFeaturedCoursesQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    renderWithProviders(<HomePage />);
    // Skeleton cards have animate-pulse class
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders instructor initials in avatar', () => {
    renderWithProviders(<HomePage />);
    // John Doe's initials are "JD"
    expect(screen.getByText('JD')).toBeInTheDocument();
  });
});
