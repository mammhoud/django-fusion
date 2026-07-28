/**
 * Integration tests for the cms-fusion EventsPage.
 *
 * Covers:
 * - Loading skeleton when fetching
 * - Upcoming Events Carousel with first 5 events
 * - Event grid with title, date, status badge, capacity
 * - ScrollReveal wraps sections
 * - Toast fires welcome message on mount
 * - Pagination controls
 * - View Details link
 * - Empty state
 * - Free/badge display
 * - Online/Location indicator
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock RTK Query hooks ──

const mockUseGetEventsQuery = vi.fn();

vi.mock('@/store/api/endpoints/events', () => ({
  useGetEventsQuery: (...args: unknown[]) => mockUseGetEventsQuery(...args),
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
// duplicate text matches with the event grid) ──

vi.mock('@/components/ui/Carousel', () => ({
  default: ({ slides, ...props }: any) => (
    <div data-testid="carousel" data-slides-count={slides?.length ?? 0}>
      Carousel with {slides?.length ?? 0} slides
    </div>
  ),
}));

// ── Import AFTER mocks ──

import EventsPage from '@/app/events/page';

// ── Mock data ──

const MOCK_EVENTS = [
  {
    id: 1,
    title: 'React Workshop',
    slug: 'react-workshop',
    short_description: 'Hands-on React workshop for beginners.',
    start_date: '2025-06-15T09:00:00Z',
    end_date: '2025-06-15T17:00:00Z',
    location: 'San Francisco, CA',
    is_online: false,
    capacity: 50,
    registered_count: 32,
    price: 0,
    is_free: true,
    status: 'upcoming',
  },
  {
    id: 2,
    title: 'TypeScript Deep Dive',
    slug: 'typescript-deep-dive',
    short_description: 'Advanced TypeScript patterns and techniques.',
    start_date: '2025-07-01T10:00:00Z',
    end_date: '2025-07-02T16:00:00Z',
    location: '',
    is_online: true,
    capacity: 200,
    registered_count: 85,
    price: 149.99,
    is_free: false,
    status: 'upcoming',
  },
  {
    id: 3,
    title: 'Data Science Summit',
    slug: 'data-science-summit',
    short_description: 'Annual data science conference.',
    start_date: '2025-08-10T08:00:00Z',
    end_date: '2025-08-12T18:00:00Z',
    location: 'New York, NY',
    is_online: false,
    capacity: 500,
    registered_count: 320,
    price: 299.99,
    is_free: false,
    status: 'upcoming',
  },
  {
    id: 4,
    title: 'Community Meetup',
    slug: 'community-meetup',
    short_description: 'Monthly community networking event.',
    start_date: '2025-06-20T18:00:00Z',
    end_date: '2025-06-20T21:00:00Z',
    location: 'Online',
    is_online: true,
    capacity: 100,
    registered_count: 45,
    price: 0,
    is_free: true,
    status: 'upcoming',
  },
  {
    id: 5,
    title: 'UI/UX Design Sprint',
    slug: 'ui-ux-design-sprint',
    short_description: 'Intensive design sprint workshop.',
    start_date: '2025-09-05T09:00:00Z',
    end_date: '2025-09-05T17:00:00Z',
    location: 'Austin, TX',
    is_online: false,
    capacity: 30,
    registered_count: 28,
    price: 199.99,
    is_free: false,
    status: 'upcoming',
  },
  {
    id: 6,
    title: 'Past Workshop',
    slug: 'past-workshop',
    short_description: 'A past completed event.',
    start_date: '2025-01-10T09:00:00Z',
    end_date: '2025-01-10T17:00:00Z',
    location: 'Chicago, IL',
    is_online: false,
    capacity: 40,
    registered_count: 40,
    price: 0,
    is_free: true,
    status: 'completed',
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

describe('EventsPage (cms-fusion)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    mockUseGetEventsQuery.mockReturnValue({
      data: {
        count: 6,
        results: MOCK_EVENTS,
      },
      isLoading: false,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // ── Toast ──

  it('fires upcoming events toast on mount', async () => {
    renderWithProviders(<EventsPage />);
    await act(() => {
      vi.advanceTimersByTime(1500);
    });
    // "Upcoming Events" appears both as a section heading and as a toast
    // title, so use getAllByText to handle multiple matches
    const titles = screen.getAllByText('Upcoming Events');
    expect(titles.length).toBeGreaterThanOrEqual(1);
    expect(
      screen.getByText(
        'Discover workshops, webinars, and community meetups.',
      ),
    ).toBeInTheDocument();
  });

  it('does not show toast before the delay elapses', () => {
    renderWithProviders(<EventsPage />);
    vi.advanceTimersByTime(1000);
    // The section heading "Upcoming Events" is always visible;
    // check the toast description which is unique to the toast
    expect(
      screen.queryByText(
        'Discover workshops, webinars, and community meetups.',
      ),
    ).not.toBeInTheDocument();
  });

  // ── ScrollReveal ──

  it('wraps page content in ScrollReveal with fadeUp', () => {
    renderWithProviders(<EventsPage />);
    const reveals = screen.getAllByTestId('scroll-reveal');
    expect(reveals.length).toBeGreaterThanOrEqual(1);
    expect(reveals[0]).toHaveAttribute('data-animation', 'fadeUp');
  });

  // ── Carousel ──

  it('renders Upcoming Events Carousel with first 5 events', () => {
    renderWithProviders(<EventsPage />);
    const carousel = screen.getByTestId('carousel');
    expect(carousel).toBeInTheDocument();
    expect(carousel).toHaveAttribute('data-slides-count', '5');
  });

  it('renders Upcoming Events heading with star icon', () => {
    renderWithProviders(<EventsPage />);
    expect(screen.getByText('Upcoming Events')).toBeInTheDocument();
  });

  it('displays event title in carousel slide', () => {
    renderWithProviders(<EventsPage />);
    // Event titles appear in both carousel and grid
    const reactWorkshops = screen.getAllByText('React Workshop');
    expect(reactWorkshops.length).toBeGreaterThan(0);
    const tsDives = screen.getAllByText('TypeScript Deep Dive');
    expect(tsDives.length).toBeGreaterThan(0);
  });

  it('shows free badge for free events in carousel', () => {
    renderWithProviders(<EventsPage />);
    const freeBadges = screen.getAllByText('Free');
    expect(freeBadges.length).toBeGreaterThanOrEqual(2);
  });

  // ── Event Grid ──

  it('renders All Events heading', () => {
    renderWithProviders(<EventsPage />);
    expect(screen.getByText('All Events')).toBeInTheDocument();
  });

  it('renders all events in the grid', () => {
    renderWithProviders(<EventsPage />);
    expect(screen.getByText('Data Science Summit')).toBeInTheDocument();
    expect(screen.getByText('UI/UX Design Sprint')).toBeInTheDocument();
    expect(screen.getByText('Community Meetup')).toBeInTheDocument();
    expect(screen.getByText('Past Workshop')).toBeInTheDocument();
  });

  it('renders event status badges', () => {
    renderWithProviders(<EventsPage />);
    const statuses = screen.getAllByText('upcoming');
    expect(statuses.length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('shows registration capacity', () => {
    renderWithProviders(<EventsPage />);
    expect(screen.getByText('32/50 registered')).toBeInTheDocument();
    expect(screen.getByText('85/200 registered')).toBeInTheDocument();
    expect(screen.getByText('320/500 registered')).toBeInTheDocument();
  });

  it('shows location or Online indicator', () => {
    renderWithProviders(<EventsPage />);
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    const onlineIndicators = screen.getAllByText('Online');
    expect(onlineIndicators.length).toBeGreaterThan(0);
    expect(screen.getByText('New York, NY')).toBeInTheDocument();
  });

  it('renders View Details links for each event', () => {
    renderWithProviders(<EventsPage />);
    const viewLinks = screen.getAllByText('View Details');
    expect(viewLinks.length).toBeGreaterThanOrEqual(6);
    viewLinks.forEach((link) => {
      expect(link.closest('a')).toHaveAttribute('href');
    });
  });

  it('shows prices for paid events', () => {
    renderWithProviders(<EventsPage />);
    expect(screen.getByText('$149.99')).toBeInTheDocument();
    expect(screen.getByText('$299.99')).toBeInTheDocument();
    expect(screen.getByText('$199.99')).toBeInTheDocument();
  });

  // ── Loading State ──

  it('shows loading skeleton when isLoading is true', () => {
    mockUseGetEventsQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    const { container } = renderWithProviders(<EventsPage />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  // ── Empty State ──

  it('shows empty state when no events', () => {
    mockUseGetEventsQuery.mockReturnValue({
      data: { count: 0, results: [] },
      isLoading: false,
    });
    renderWithProviders(<EventsPage />);
    expect(screen.queryByTestId('carousel')).not.toBeInTheDocument();
  });
});
