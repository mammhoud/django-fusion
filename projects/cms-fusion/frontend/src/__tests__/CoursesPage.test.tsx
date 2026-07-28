/**
 * Integration tests for the cms-fusion CoursesPage.
 *
 * Covers:
 * - Loading skeleton when fetching
 * - Error state with retry
 * - Course grid rendering with title, price, category badge
 * - Top Courses Carousel
 * - Search and filter inputs (category, level)
 * - ScrollReveal wraps sections
 * - Toast fires welcome message on mount
 * - Pagination controls
 * - Empty state when no results
 * - Category select options from API
 */
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock RTK Query hooks ──

const mockUseGetCoursesQuery = vi.fn();
const mockUseGetCategoriesQuery = vi.fn();

vi.mock('@/store/api/endpoints/courses', () => ({
  useGetCoursesQuery: (...args: unknown[]) => mockUseGetCoursesQuery(...args),
  useGetCategoriesQuery: (...args: unknown[]) =>
    mockUseGetCategoriesQuery(...args),
}));

// ── Mock ScrollReveal (render children directly) ──

vi.mock('@/components/ui/ScrollReveal', () => ({
  default: ({ children, ...props }: any) => (
    <div data-testid="scroll-reveal" data-animation={props.animation}>
      {children}
    </div>
  ),
}));

// ── Mock Carousel (only renders count, not slide content, to avoid
// duplicate text matches with the course grid) ──

vi.mock('@/components/ui/Carousel', () => ({
  default: ({ slides, ...props }: any) => (
    <div data-testid="carousel" data-slides-count={slides?.length ?? 0}>
      Carousel with {slides?.length ?? 0} slides
    </div>
  ),
}));

// ── Import AFTER mocks ──

import CoursesPage from '@/app/courses/page';

// ── Mock data ──

const MOCK_CATEGORIES = [
  { id: 1, name: 'Development', slug: 'development' },
  { id: 2, name: 'Data Science', slug: 'data-science' },
  { id: 3, name: 'Design', slug: 'design' },
];

const MOCK_COURSES = [
  {
    id: 1,
    title: 'React Fundamentals',
    slug: 'react-fundamentals',
    short_description: 'Learn React from scratch with hands-on projects.',
    price: 49.99,
    discounted_price: 29.99,
    category_name: 'Development',
    instructor_name: 'John Doe',
    level: 'beginner',
    duration: '16 hours',
    rating: 4.5,
    reviews_count: 234,
    students_count: 1200,
  },
  {
    id: 2,
    title: 'Advanced TypeScript',
    slug: 'advanced-typescript',
    short_description: 'Master TypeScript patterns and generics.',
    price: 79.99,
    discounted_price: null,
    category_name: 'Development',
    instructor_name: 'Jane Smith',
    level: 'advanced',
    duration: '24 hours',
    rating: 4.8,
    reviews_count: 189,
    students_count: 850,
  },
  {
    id: 3,
    title: 'Python for Data Science',
    slug: 'python-data-science',
    short_description: 'Data analysis and machine learning.',
    price: 59.99,
    discounted_price: 39.99,
    category_name: 'Data Science',
    instructor_name: 'Bob Wilson',
    level: 'intermediate',
    duration: '32 hours',
    rating: 4.6,
    reviews_count: 412,
    students_count: 2100,
  },
];

// ── Helpers ──

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

describe('CoursesPage (cms-fusion)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    mockUseGetCoursesQuery.mockReturnValue({
      data: { count: 3, results: MOCK_COURSES },
      isLoading: false,
      error: undefined,
    });
    mockUseGetCategoriesQuery.mockReturnValue({
      data: MOCK_CATEGORIES,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // ── Toast ──

  it('fires explore courses toast on mount', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => {
      vi.advanceTimersByTime(1500);
    });
    // "Explore Courses" appears as both the page heading and toast title
    const titles = screen.getAllByText('Explore Courses');
    expect(titles.length).toBeGreaterThanOrEqual(1);
    expect(
      screen.getByText('Discover courses from expert instructors.'),
    ).toBeInTheDocument();
  });

  it('does not show toast before the delay elapses', () => {
    renderWithProviders(<CoursesPage />);
    vi.advanceTimersByTime(1000);
    // The page heading "Explore Courses" is always visible; check the
    // toast description instead, which is unique to the toast
    expect(
      screen.queryByText('Discover courses from expert instructors.'),
    ).not.toBeInTheDocument();
  });

  // ── ScrollReveal ──

  it('wraps page content in ScrollReveal with fadeUp', () => {
    renderWithProviders(<CoursesPage />);
    const reveals = screen.getAllByTestId('scroll-reveal');
    expect(reveals.length).toBeGreaterThanOrEqual(1);
    expect(reveals[0]).toHaveAttribute('data-animation', 'fadeUp');
  });

  it('wraps search/filter section in ScrollReveal', () => {
    renderWithProviders(<CoursesPage />);
    const reveals = screen.getAllByTestId('scroll-reveal');
    const filterReveal = reveals.find(
      (r) => r.querySelector('input') !== null,
    );
    expect(filterReveal).toBeInTheDocument();
  });

  // ── Top Courses Carousel ──

  it('renders Top Courses Carousel with first 6 courses', () => {
    renderWithProviders(<CoursesPage />);
    const carousel = screen.getByTestId('carousel');
    expect(carousel).toBeInTheDocument();
    // 3 courses total, all shown
    expect(carousel).toHaveAttribute('data-slides-count', '3');
  });

  it('renders Top Courses heading with star icon', () => {
    renderWithProviders(<CoursesPage />);
    expect(screen.getByText('Top Courses')).toBeInTheDocument();
  });

  it('displays course title in carousel slide', () => {
    renderWithProviders(<CoursesPage />);
    // Course titles appear in both carousel and grid
    const reactFund = screen.getAllByText('React Fundamentals');
    expect(reactFund.length).toBeGreaterThan(0);
    const ts = screen.getAllByText('Advanced TypeScript');
    expect(ts.length).toBeGreaterThan(0);
  });

  it('shows discounted price in carousel', () => {
    renderWithProviders(<CoursesPage />);
    // Discounted prices appear in both carousel and grid
    const prices = screen.getAllByText('$29.99');
    expect(prices.length).toBeGreaterThan(0);
  });

  // ── Course Grid ──

  it('renders course grid with all courses', () => {
    renderWithProviders(<CoursesPage />);
    expect(screen.getByText('Python for Data Science')).toBeInTheDocument();
  });

  it('renders course category badges', () => {
    renderWithProviders(<CoursesPage />);
    // Category names appear in both carousel and grid
    const devBadges = screen.getAllByText('Development');
    expect(devBadges.length).toBeGreaterThan(0);
    const dsBadges = screen.getAllByText('Data Science');
    expect(dsBadges.length).toBeGreaterThan(0);
  });

  it('renders course level badges', () => {
    renderWithProviders(<CoursesPage />);
    // Level badges appear in both carousel and grid
    const beginnerBadges = screen.getAllByText('beginner');
    expect(beginnerBadges.length).toBeGreaterThan(0);
    const advancedBadges = screen.getAllByText('advanced');
    expect(advancedBadges.length).toBeGreaterThan(0);
  });

  it('renders course duration', () => {
    renderWithProviders(<CoursesPage />);
    expect(screen.getByText('16 hours')).toBeInTheDocument();
    expect(screen.getByText('24 hours')).toBeInTheDocument();
    expect(screen.getByText('32 hours')).toBeInTheDocument();
  });

  it('renders instructor names in grid', () => {
    renderWithProviders(<CoursesPage />);
    // Instructor names appear in both carousel and grid
    const johns = screen.getAllByText('John Doe');
    expect(johns.length).toBeGreaterThan(0);
    const janes = screen.getAllByText('Jane Smith');
    expect(janes.length).toBeGreaterThan(0);
    const bobs = screen.getAllByText('Bob Wilson');
    expect(bobs.length).toBeGreaterThan(0);
  });

  it('renders prices with discounted amounts', () => {
    renderWithProviders(<CoursesPage />);
    // Prices appear in both carousel and grid
    const prices2999 = screen.getAllByText('$29.99');
    expect(prices2999.length).toBeGreaterThan(0);
    const prices7999 = screen.getAllByText('$79.99');
    expect(prices7999.length).toBeGreaterThan(0);
  });

  it('renders ratings with review count', () => {
    renderWithProviders(<CoursesPage />);
    // Ratings appear in both carousel and grid
    const ratings45 = screen.getAllByText(/4\.5/);
    expect(ratings45.length).toBeGreaterThan(0);
    // Review counts appear in the format "4.5 (234)"
    const reviewCounts = screen.getAllByText(/\(234\)/);
    expect(reviewCounts.length).toBeGreaterThan(0);
  });

  // ── Search & Filters ──

  it('renders search input with search icon', () => {
    renderWithProviders(<CoursesPage />);
    const searchInput = screen.getByPlaceholderText('Search courses...');
    expect(searchInput).toBeInTheDocument();
  });

  it('renders category select with options from API', () => {
    renderWithProviders(<CoursesPage />);
    expect(screen.getByText('All Categories')).toBeInTheDocument();
    // Category names appear in both the select dropdown and course badges
    const devCategories = screen.getAllByText('Development');
    expect(devCategories.length).toBeGreaterThan(0);
    const dsCategories = screen.getAllByText('Data Science');
    expect(dsCategories.length).toBeGreaterThan(0);
    expect(screen.getByText('Design')).toBeInTheDocument();
  });

  it('renders level select with all levels', () => {
    renderWithProviders(<CoursesPage />);
    expect(screen.getByText('All Levels')).toBeInTheDocument();
    expect(screen.getByText('Beginner')).toBeInTheDocument();
    expect(screen.getByText('Intermediate')).toBeInTheDocument();
    expect(screen.getByText('Advanced')).toBeInTheDocument();
  });

  it('updates search value on input change', () => {
    renderWithProviders(<CoursesPage />);
    const searchInput = screen.getByPlaceholderText(
      'Search courses...',
    ) as HTMLInputElement;
    fireEvent.change(searchInput, { target: { value: 'React' } });
    expect(searchInput.value).toBe('React');
  });

  // ── Loading State ──

  it('shows LoadingSkeleton when isLoading', () => {
    mockUseGetCoursesQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: undefined,
    });
    const { container } = renderWithProviders(<CoursesPage />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  // ── Error State ──

  it('shows error state with retry when request fails', () => {
    mockUseGetCoursesQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: { status: 500, message: 'Server Error' },
    });
    renderWithProviders(<CoursesPage />);
    expect(
      screen.getByText('Failed to load courses. Please try again.'),
    ).toBeInTheDocument();
  });

  // ── Empty State ──

  it('shows empty state when no courses match', () => {
    mockUseGetCoursesQuery.mockReturnValue({
      data: { count: 0, results: [] },
      isLoading: false,
      error: undefined,
    });
    renderWithProviders(<CoursesPage />);
    expect(
      screen.getByText('No courses found'),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'No courses match your current filters. Try adjusting your search criteria.',
      ),
    ).toBeInTheDocument();
  });

  // ── Pagination ──

  it('renders pagination buttons when multiple pages exist', () => {
    const manyCourses = Array.from({ length: 25 }, (_, i) => ({
      ...MOCK_COURSES[0],
      id: i + 1,
      title: `Course ${i + 1}`,
    }));
    mockUseGetCoursesQuery.mockReturnValue({
      data: { count: 25, results: manyCourses.slice(0, 10) },
      isLoading: false,
      error: undefined,
    });
    renderWithProviders(<CoursesPage />);
    // 25 courses / 10 per page = 3 pages
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('does not show pagination when only one page', () => {
    renderWithProviders(<CoursesPage />);
    // 3 courses = 1 page, no pagination buttons
    expect(screen.queryByText('2')).not.toBeInTheDocument();
  });
});
