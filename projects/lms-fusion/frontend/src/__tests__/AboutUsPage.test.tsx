/**
 * Tests for the About Us page loading behavior.
 *
 * Covers:
 * - Shows skeleton placeholders (not "0") for the Courses/Instructors stat
 *   cards while their API queries are loading
 * - Shows real stat values once the APIs respond
 * - Static cards (Students / Countries) still render immediately
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { FusionMiddleware } from '@/components/FusionMiddleware';

// ── Mock RTK Query hooks ──

const mockUseGetPageDataQuery = vi.fn();
const mockUseGetInstructorsQuery = vi.fn();
const mockUseGetCoursesQuery = vi.fn();

vi.mock('@/store/api/endpoints/pages', () => ({
  useGetPageDataQuery: (...args: unknown[]) => mockUseGetPageDataQuery(...args),
  useGetPageFragmentQuery: vi.fn(),
  useGetPageQuery: vi.fn(),
  useGetPageHtmlQuery: vi.fn(),
}));

vi.mock('@/store/api/endpoints/instructors', () => ({
  useGetInstructorsQuery: (...args: unknown[]) => mockUseGetInstructorsQuery(...args),
  useGetInstructorDashboardQuery: vi.fn(),
  useGetInstructorQuery: vi.fn(),
  useGetInstructorCoursesQuery: vi.fn(),
  useGetInstructorReviewsQuery: vi.fn(),
  useUpdateInstructorProfileMutation: vi.fn(),
}));

vi.mock('@/store/api/endpoints/courses', () => ({
  useGetCoursesQuery: (...args: unknown[]) => mockUseGetCoursesQuery(...args),
  useGetCourseQuery: vi.fn(),
  useGetCourseCurriculumQuery: vi.fn(),
  useEnrollInCourseMutation: vi.fn(),
}));

// ── Import page AFTER mocks ──

import AboutPage from '@/app/about-us/page';

// ── Test data ──

const ABOUT_PAGE_DATA = {
  slug: 'about-us',
  title: 'About Us',
  seo: { title: 'About | Fusion', description: 'About page' },
  blocks: [{ type: 'hero', heading: 'Learn With Us', intro: 'We teach real skills.' }],
};

const ENCODED = 'fusion_v1:' + btoa(JSON.stringify(ABOUT_PAGE_DATA));

// ── Helpers ──

function createStore() {
  return configureStore({ reducer: {} });
}

function renderAbout() {
  return render(
    <Provider store={createStore()}>
      <FusionMiddleware initialMode="data">
        <AboutPage />
      </FusionMiddleware>
    </Provider>,
  );
}

// ── Tests ──

describe('AboutUsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: ENCODED },
      isLoading: false,
      error: undefined,
    });
  });

  it('shows skeleton placeholders (not 0) while Courses/Instructors stats load', async () => {
    mockUseGetInstructorsQuery.mockReturnValue({ data: undefined, isLoading: true });
    mockUseGetCoursesQuery.mockReturnValue({ data: undefined, isLoading: true });

    const { container } = renderAbout();

    // Wait for the CMS page content to render
    await screen.findByText('Learn With Us');

    // Stat skeletons (Courses + Instructors cards) render pulse placeholders
    const statSkeletons = container.querySelectorAll('.animate-pulse');
    expect(statSkeletons.length).toBeGreaterThanOrEqual(2);

    // The API-driven stat cards must NOT render a premature "0"
    expect(screen.queryByText('0')).not.toBeInTheDocument();

    // Static cards still render immediately
    expect(screen.getByText('5K+')).toBeInTheDocument();
    expect(screen.getByText('50+')).toBeInTheDocument();
  });

  it('shows real stat values once Courses/Instructors APIs respond', async () => {
    mockUseGetInstructorsQuery.mockReturnValue({
      data: { count: 12, results: [] },
      isLoading: false,
    });
    mockUseGetCoursesQuery.mockReturnValue({
      data: { count: 25, results: [] },
      isLoading: false,
    });

    renderAbout();

    await screen.findByText('Learn With Us');

    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    // No skeleton placeholders remain after data arrives
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });
});
