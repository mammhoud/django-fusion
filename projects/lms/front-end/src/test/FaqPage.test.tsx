/**
 * Unit tests for the FAQ page component (FaqPage + FaqPageContent).
 *
 * Covers:
 * - Hero section renders with heading and intro from page data
 * - FAQ groups render with question/answer items
 * - Search filters FAQ items by question and answer text
 * - Accordion toggle opens/closes answers
 * - CTA section renders when present
 * - Empty categories (after filtering) are hidden
 * - Default fallbacks when no page data (undefined)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { FusionMiddleware } from '@/components/FusionMiddleware';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetPageDataQuery = vi.fn();

vi.mock('@/store/api/endpoints/pages', () => ({
  useGetPageDataQuery: (...args: unknown[]) => mockUseGetPageDataQuery(...args),
  useGetPageFragmentQuery: vi.fn(),
  useGetPageQuery: vi.fn(),
  useGetPageHtmlQuery: vi.fn(),
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const FAQ_PAGE_DATA = {
  slug: 'faq',
  title: 'FAQ',
  seo: { title: 'FAQ | CTC Research', description: 'Frequently Asked Questions' },
  blocks: [
    {
      type: 'hero',
      heading: 'Frequently Asked Questions',
      intro: 'Find answers to common questions about our courses and platform.',
    },
    {
      type: 'faq_groups',
      groups: [
        {
          title: 'Getting Started',
          items: [
            { question: 'How do I create an account?', answer: 'Click the Sign Up button and follow the registration steps.' },
            { question: 'How do I enroll in a course?', answer: 'Browse courses and click Enroll on any course page.' },
          ],
        },
        {
          title: 'Payments',
          items: [
            { question: 'What payment methods are accepted?', answer: 'We accept all major credit cards and PayPal.' },
          ],
        },
      ],
    },
    {
      type: 'cta',
      heading: 'Still have questions?',
      intro: 'Our support team is here to help.',
      ctas: [{ label: 'Contact Support', href: '/contact' }],
    },
  ],
};

const MINIMAL_FAQ_PAGE = {
  slug: 'faq',
  title: 'FAQ',
  seo: { title: 'FAQ', description: 'FAQ page' },
  blocks: [],
};

// Codec-encoded versions of the test data
const ENCODED_FULL =
  'fusion_v1:' + btoa(JSON.stringify(FAQ_PAGE_DATA));
const ENCODED_MINIMAL =
  'fusion_v1:' + btoa(JSON.stringify(MINIMAL_FAQ_PAGE));

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

// Import the actual FaqPageContent component for direct testing
import FaqPage from '@/app/faq/page';

// Since FaqPage wraps FaqPageContent inside FusionPage, we test by rendering
// the page with proper mock data and then examining the DOM
function renderPageWithData(encoded: string) {
  mockUseGetPageDataQuery.mockReturnValue({
    data: { encoded },
    isLoading: false,
    error: undefined,
  });

  return render(
    <Provider store={createTestStore()}>
      <FusionMiddleware initialMode="data">
        <FaqPage />
      </FusionMiddleware>
    </Provider>,
  );
}

function renderPageLoading() {
  mockUseGetPageDataQuery.mockReturnValue({
    data: undefined,
    isLoading: true,
    error: undefined,
  });

  return render(
    <Provider store={createTestStore()}>
      <FusionMiddleware initialMode="data">
        <FaqPage />
      </FusionMiddleware>
    </Provider>,
  );
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('FAQ Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('renders the hero section with heading from CMS', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText('Frequently Asked Questions'),
      ).toBeInTheDocument();
    });
  });

  it('renders the hero intro text from CMS', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText(
          'Find answers to common questions about our courses and platform.',
        ),
      ).toBeInTheDocument();
    });
  });

  it('renders FAQ category headers', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(screen.getByText('Getting Started')).toBeInTheDocument();
      expect(screen.getByText('Payments')).toBeInTheDocument();
    });
  });

  it('renders FAQ question text', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText('How do I create an account?'),
      ).toBeInTheDocument();
      expect(
        screen.getByText('How do I enroll in a course?'),
      ).toBeInTheDocument();
      expect(
        screen.getByText('What payment methods are accepted?'),
      ).toBeInTheDocument();
    });
  });

  it('hides answers by default (accordion closed via CSS)', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      // Answers are in the DOM but hidden via CSS max-height
      // We check that the parent div has the 'max-h-0' class
      const answerText = screen.queryByText(
        'Click the Sign Up button and follow the registration steps.',
      );
      expect(answerText).toBeInTheDocument();
      // Verify it's hidden behind the accordion collapse
      const parentDiv = answerText?.closest('div[class*="max-h"]');
      expect(parentDiv?.className).toContain('max-h-0');
    });
  });

  it('toggles answer visibility on question click (accordion)', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText('How do I create an account?'),
      ).toBeInTheDocument();
    });

    // Find the answer text element
    const getAnswerContainer = () => {
      const answer = screen.queryByText(
        'Click the Sign Up button and follow the registration steps.',
      );
      if (!answer) return null;
      return answer.closest('div[class*="max-h"]');
    };

    // Initially the answer container should have max-h-0
    const container = getAnswerContainer();
    expect(container?.className).toContain('max-h-0');

    // Click the question to open
    fireEvent.click(screen.getByText('How do I create an account?'));

    // After click, the container should have max-h-96 (open)
    const openContainer = getAnswerContainer();
    expect(openContainer?.className).toContain('max-h-96');

    // Click again to close
    fireEvent.click(screen.getByText('How do I create an account?'));

    // After second click, the container should have max-h-0 again
    const closedContainer = getAnswerContainer();
    expect(closedContainer?.className).toContain('max-h-0');
  });

  it('renders the search input field', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByPlaceholderText('Search FAQs...'),
      ).toBeInTheDocument();
    });
  });

  it('filters FAQ items by question text when searching', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(screen.getByText('Getting Started')).toBeInTheDocument();
    });

    // Type in search box
    const searchInput = screen.getByPlaceholderText('Search FAQs...');
    fireEvent.change(searchInput, { target: { value: 'account' } });

    // 'Getting Started' category should still be visible (has matching items)
    expect(screen.getByText('Getting Started')).toBeInTheDocument();
    expect(
      screen.getByText('How do I create an account?'),
    ).toBeInTheDocument();

    // 'Payments' category should be hidden (no matching items)
    expect(screen.queryByText('Payments')).not.toBeInTheDocument();
  });

  it('filters FAQ items by answer text when searching', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(screen.getByText('Getting Started')).toBeInTheDocument();
    });

    // Search for text that appears in an answer
    const searchInput = screen.getByPlaceholderText('Search FAQs...');
    fireEvent.change(searchInput, { target: { value: 'credit cards' } });

    // Only the Payments category should match
    expect(screen.getByText('Payments')).toBeInTheDocument();
    expect(screen.queryByText('Getting Started')).not.toBeInTheDocument();
  });

  it('renders CTA section when present in page data', async () => {
    renderPageWithData(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText('Still have questions?'),
      ).toBeInTheDocument();
      expect(
        screen.getByText('Our support team is here to help.'),
      ).toBeInTheDocument();
    });

    // CTA link should exist
    const ctaLink = screen.getByText('Contact Support');
    expect(ctaLink).toBeInTheDocument();
    expect(ctaLink.closest('a')).toHaveAttribute('href', '/contact');
  });

  it('renders default title fallback when no hero or page data', async () => {
    renderPageWithData(ENCODED_MINIMAL);

    await vi.waitFor(() => {
      // Should show default "FAQ" heading (page.title fallback)
      expect(screen.getByText('FAQ')).toBeInTheDocument();
    });
  });

  it('shows loading state when data is loading', () => {
    renderPageLoading();

    // FusionPageDataInner shows LoadingSkeleton when isLoading is true,
    // so page content should NOT be rendered
    expect(
      screen.queryByText('Frequently Asked Questions'),
    ).not.toBeInTheDocument();
  });

  it('shows error state when page data fails to load', async () => {
    mockUseGetPageDataQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    });

    render(
      <Provider store={createTestStore()}>
        <FusionMiddleware initialMode="data">
          <FaqPage />
        </FusionMiddleware>
      </Provider>,
    );

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Unable to load page content/i),
      ).toBeInTheDocument();
    });
  });
});
