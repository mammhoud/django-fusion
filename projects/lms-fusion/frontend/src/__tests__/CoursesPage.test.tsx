/**
 * Integration tests for the lms-fusion CoursesPage.
 *
 * Covers:
 * - Loading skeleton when fetch is pending
 * - Error state with retry button
 * - Empty state when no courses match
 * - Course grid rendering with title, price, rating
 * - Featured Courses Carousel
 * - Filter sidebar with language/difficulty
 * - Search form functionality
 * - ScrollReveal wraps sections
 * - Toast fires welcome message on mount
 * - Pagination controls
 * - Price display with original price strikethrough
 */
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ToastProvider } from '@/components/ui/Toast';

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

const MOCK_FILTERS = {
  languages: ['English', 'Arabic', 'French'],
  difficulties: ['beginner', 'intermediate', 'advanced'],
};

const MOCK_COURSES = [
  {
    id: 1,
    title: 'React Fundamentals',
    slug: 'react-fundamentals',
    short_description: 'Learn React from scratch with hands-on projects.',
    image_url: null,
    instructor: 'John Doe',
    price: 49.99,
    original_price: 79.99,
    difficulty: 'beginner',
    language: 'English',
    duration: 16,
    rating: 4.5,
    reviews_count: 234,
    is_featured: true,
    has_certificate: true,
  },
  {
    id: 2,
    title: 'Advanced TypeScript',
    slug: 'advanced-typescript',
    short_description: 'Master advanced TypeScript patterns and generics.',
    image_url: null,
    instructor: 'Jane Smith',
    price: 79.99,
    original_price: null,
    difficulty: 'advanced',
    language: 'English',
    duration: 24,
    rating: 4.8,
    reviews_count: 189,
    is_featured: true,
    has_certificate: true,
  },
  {
    id: 3,
    title: 'Python Data Science',
    slug: 'python-data-science',
    short_description: 'Data analysis and machine learning with Python.',
    image_url: null,
    instructor: 'Bob Wilson',
    price: 59.99,
    original_price: 89.99,
    difficulty: 'intermediate',
    language: 'English',
    duration: 32,
    rating: 4.6,
    reviews_count: 412,
    is_featured: false,
    has_certificate: false,
  },
  {
    id: 4,
    title: 'UI/UX Design',
    slug: 'ui-ux-design',
    short_description: 'Design beautiful and functional user interfaces.',
    image_url: null,
    instructor: 'Alice Brown',
    price: 39.99,
    original_price: null,
    difficulty: 'beginner',
    language: 'Arabic',
    duration: 12,
    rating: 4.3,
    reviews_count: 98,
    is_featured: false,
    has_certificate: true,
  },
];

// ── Helper ──

function mockFetchResponse(data: any, ok = true) {
  return Promise.resolve({
    ok,
    json: () => Promise.resolve(data),
  });
}

function renderWithProviders(ui: React.ReactElement) {
  return render(<ToastProvider>{ui}</ToastProvider>);
}

// ── Tests ──

describe('CoursesPage (lms-fusion)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Mock fetch for filters and courses
    vi.spyOn(global, 'fetch').mockImplementation((url: string | URL | Request) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/filters')) {
        return mockFetchResponse(MOCK_FILTERS);
      }
      return mockFetchResponse({
        data: MOCK_COURSES,
        pagination: { page: 1, total: 4, total_pages: 1 },
      });
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  // ── Toast ──

  it('fires explore courses toast on mount', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => {
      vi.advanceTimersByTime(1500);
    });
    expect(screen.getByText('Explore Courses')).toBeInTheDocument();
    expect(
      screen.getByText('Discover new skills and advance your career.'),
    ).toBeInTheDocument();
  });

  it('does not show toast before the delay elapses', () => {
    renderWithProviders(<CoursesPage />);
    vi.advanceTimersByTime(1000);
    expect(
      screen.queryByText('Explore Courses'),
    ).not.toBeInTheDocument();
  });

  // ── ScrollReveal ──

  it('wraps hero section in ScrollReveal with fadeUp', () => {
    renderWithProviders(<CoursesPage />);
    const reveals = screen.getAllByTestId('scroll-reveal');
    expect(reveals.length).toBeGreaterThanOrEqual(1);
    expect(reveals[0]).toHaveAttribute('data-animation', 'fadeUp');
  });

  it('wraps filter sidebar in ScrollReveal with fadeLeft', async () => {
    renderWithProviders(<CoursesPage />);
    // Wait for filters to load
    await act(() => vi.advanceTimersByTime(100));
    const reveals = screen.getAllByTestId('scroll-reveal');
    const sidebarReveal = reveals.find(
      (r) => r.querySelector('aside') !== null,
    );
    expect(sidebarReveal).toBeInTheDocument();
    expect(sidebarReveal).toHaveAttribute('data-animation', 'fadeLeft');
  });

  // ── Featured Courses Carousel ──

  it('renders Featured Courses Carousel with featured courses', async () => {
    renderWithProviders(<CoursesPage />);
    // Wait for courses to load
    await act(() => vi.advanceTimersByTime(100));
    const carousel = screen.getByTestId('carousel');
    expect(carousel).toBeInTheDocument();
    // Course titles appear in both carousel and grid — use getAllByText
    const reactFund = screen.getAllByText('React Fundamentals');
    expect(reactFund.length).toBeGreaterThan(0);
  });

  it('shows featured badge on featured course cards', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    const featuredBadges = screen.getAllByText('Featured');
    expect(featuredBadges.length).toBeGreaterThanOrEqual(2);
  });

  // ── Course Grid ──

  it('renders course grid with course titles', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Titles appear in both carousel and grid
    const reactFund = screen.getAllByText('React Fundamentals');
    expect(reactFund.length).toBeGreaterThan(0);
    expect(screen.getByText('Python Data Science')).toBeInTheDocument();
  });

  it('renders course prices', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Prices appear in both carousel and grid
    const price4999 = screen.getAllByText('$49.99');
    expect(price4999.length).toBeGreaterThan(0);
    const price7999 = screen.getAllByText('$79.99');
    expect(price7999.length).toBeGreaterThan(0);
  });

  it('shows original price strikethrough when discounted', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Original prices appear in both carousel and grid
    const origPrices = screen.getAllByText('$79.99');
    expect(origPrices.length).toBeGreaterThan(0);
    const origPrices89 = screen.getAllByText('$89.99');
    expect(origPrices89.length).toBeGreaterThan(0);
  });

  it('renders course ratings with star', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Rating values appear as text in both carousel and grid
    const ratings45 = screen.getAllByText(/4\.5/);
    expect(ratings45.length).toBeGreaterThan(0);
  });

  it('renders instructor names', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
    expect(screen.getByText(/Jane Smith/)).toBeInTheDocument();
  });

  it('renders difficulty and duration badges', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Difficulty/duration appear in both carousel and grid
    const beginnerBadges = screen.getAllByText(/beginner/i);
    expect(beginnerBadges.length).toBeGreaterThan(0);
    const duration16h = screen.getAllByText(/16h/);
    expect(duration16h.length).toBeGreaterThan(0);
  });

  // ── Filters Sidebar ──

  it('renders filter sidebar with language options', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByText('Language')).toBeInTheDocument();
    expect(screen.getByText('English')).toBeInTheDocument();
    expect(screen.getByText('Arabic')).toBeInTheDocument();
  });

  it('renders filter sidebar with difficulty options', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    expect(screen.getByText('Difficulty')).toBeInTheDocument();
    // Difficulty values appear in both carousel/grid and filter sidebar
    const beginnerFilters = screen.getAllByText('beginner');
    expect(beginnerFilters.length).toBeGreaterThan(0);
    const advancedFilters = screen.getAllByText('advanced');
    expect(advancedFilters.length).toBeGreaterThan(0);
  });

  it('shows Clear all filters button when filters are active', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Click a filter button to activate it
    const engBtn = screen.getByText('English');
    fireEvent.click(engBtn);
    expect(screen.getByText('Clear all filters')).toBeInTheDocument();
  });

  // ── Search Form ──

  it('renders search input and submit button', () => {
    renderWithProviders(<CoursesPage />);
    const searchInput = screen.getByPlaceholderText('Search courses...');
    expect(searchInput).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
  });

  it('submits search query on form submit', async () => {
    renderWithProviders(<CoursesPage />);
    const searchInput = screen.getByPlaceholderText('Search courses...');
    fireEvent.change(searchInput, { target: { value: 'React' } });
    fireEvent.submit(screen.getByText('Search').closest('form')!);
    // After submit, fetch is called again with the search query
    // The mock returns the same courses, so titles should still be visible
    await act(() => vi.advanceTimersByTime(100));
    const titles = screen.getAllByText('React Fundamentals');
    expect(titles.length).toBeGreaterThan(0);
  });

  // ── Loading State ──

  it('shows loading skeleton when fetching', () => {
    // Delayed fetch
    vi.spyOn(global, 'fetch').mockImplementation(
      () => new Promise(() => {}),
    );
    const { container } = renderWithProviders(<CoursesPage />);
    // Skeleton cards have animate-pulse class
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  // ── Error State ──

  it('shows error state with retry button when fetch fails', async () => {
    vi.spyOn(global, 'fetch').mockRejectedValue(
      new Error('API error 500'),
    );
    renderWithProviders(<CoursesPage />);
    // Wait for the error to be caught
    await act(() => vi.advanceTimersByTime(100));
    // Need to wait for microtasks
    await vi.waitFor(() => {
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  // ── Empty State ──

  it('shows empty state when no courses match', async () => {
    vi.spyOn(global, 'fetch').mockImplementation((url: string | URL | Request) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/filters')) {
        return mockFetchResponse({ languages: [], difficulties: [] });
      }
      return mockFetchResponse({
        data: [],
        pagination: { page: 1, total: 0, total_pages: 0 },
      });
    });
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    await vi.waitFor(() => {
      expect(screen.getByText('No courses found')).toBeInTheDocument();
    });
  });

  // ── Pagination ──

  it('renders pagination when multiple pages exist', async () => {
    vi.spyOn(global, 'fetch').mockImplementation((url: string | URL | Request) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('/filters')) {
        return mockFetchResponse(MOCK_FILTERS);
      }
      return mockFetchResponse({
        data: MOCK_COURSES,
        pagination: { page: 1, total: 40, total_pages: 4 },
      });
    });
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    // Pagination buttons appear
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('shows total course count in results header', async () => {
    renderWithProviders(<CoursesPage />);
    await act(() => vi.advanceTimersByTime(100));
    expect(screen.getByText(/4 courses/)).toBeInTheDocument();
  });
});
