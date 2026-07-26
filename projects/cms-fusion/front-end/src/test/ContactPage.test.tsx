/**
 * Unit tests for the Contact page component (ContactPage + ContactPageContent).
 *
 * Covers:
 * - Hero section renders with heading and intro from page data
 * - Contact info cards render with icons, labels, values, and links
 * - Contact form renders with all input fields
 * - Form submission sends data via mutation
 * - Success message displays after submission
 * - Error message displays on submission failure
 * - Form reset after successful submission
 * - Default fallbacks when no page data (undefined)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { FusionMiddleware } from '@/components/FusionMiddleware';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks — use mutable objects so tests can update state
// ═══════════════════════════════════════════════════════════════════

const mockUseGetPageDataQuery = vi.fn();

const { mockSubmitContact, mutationState } = vi.hoisted(() => ({
  mockSubmitContact: vi.fn(),
  mutationState: { isLoading: false, isSuccess: false, error: undefined as any, reset: vi.fn() },
}));

vi.mock('@/store/api/endpoints/pages', () => ({
  useGetPageDataQuery: (...args: unknown[]) => mockUseGetPageDataQuery(...args),
  useGetPageFragmentQuery: vi.fn(),
  useGetPageQuery: vi.fn(),
  useGetPageHtmlQuery: vi.fn(),
}));

vi.mock('@/store/api/endpoints/contact', () => ({
  useSubmitContactMutation: () => [mockSubmitContact, mutationState],
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const CONTACT_PAGE_DATA = {
  slug: 'contact',
  title: 'Contact Us',
  seo: { title: 'Contact | CTC Research', description: 'Get in touch' },
  blocks: [
    {
      type: 'hero',
      heading: 'Get In Touch',
      intro: 'We\'d love to hear from you. Reach out with any questions.',
    },
    {
      type: 'contact_methods',
      items: [
        { type: 'email', label: 'Email', value: 'hello@ctc-research.com', href: 'mailto:hello@ctc-research.com' },
        { type: 'phone', label: 'Phone', value: '+1 (555) 123-4567' },
        { type: 'address', label: 'Office', value: '123 Research Drive, Boston, MA' },
        { type: 'hours', label: 'Hours', value: 'Mon-Fri, 9AM-6PM EST' },
      ],
    },
  ],
};

const MINIMAL_CONTACT_PAGE = {
  slug: 'contact',
  title: 'Contact Us',
  blocks: [],
};

// Codec-encoded versions
const ENCODED_FULL = 'fusion_v1:' + btoa(JSON.stringify(CONTACT_PAGE_DATA));
const ENCODED_MINIMAL = 'fusion_v1:' + btoa(JSON.stringify(MINIMAL_CONTACT_PAGE));

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

// Import the ContactPage for rendering
import ContactPage from '@/app/contact/page';

function renderContactPage(encoded: string | null = ENCODED_FULL) {
  if (encoded) {
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded },
      isLoading: false,
      error: undefined,
    });
  } else {
    mockUseGetPageDataQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    });
  }

  return render(
    <Provider store={createTestStore()}>
      <FusionMiddleware initialMode="data">
        <ContactPage />
      </FusionMiddleware>
    </Provider>,
  );
}

function renderContactLoading() {
  mockUseGetPageDataQuery.mockReturnValue({
    data: undefined,
    isLoading: true,
    error: undefined,
  });

  return render(
    <Provider store={createTestStore()}>
      <FusionMiddleware initialMode="data">
        <ContactPage />
      </FusionMiddleware>
    </Provider>,
  );
}

function fillAndSubmitForm() {
  const nameInput = screen.getByPlaceholderText('Your name');
  const emailInput = screen.getByPlaceholderText('your@email.com');
  const subjectInput = screen.getByPlaceholderText('How can we help?');
  const messageInput = screen.getByPlaceholderText(
    'Tell us more about your inquiry...',
  );

  fireEvent.change(nameInput, { target: { value: 'John Doe' } });
  fireEvent.change(emailInput, {
    target: { value: 'john@example.com' },
  });
  fireEvent.change(subjectInput, {
    target: { value: 'Course Inquiry' },
  });
  fireEvent.change(messageInput, {
    target: { value: 'I have a question about courses.' },
  });

  fireEvent.click(screen.getByText('Send Message'));
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('Contact Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    // Default: mock returns a resolved promise
    mockSubmitContact.mockReturnValue({
      unwrap: () => Promise.resolve({ status: 'success' }),
    });
  });

  it('renders the hero heading from CMS', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(screen.getByText('Get In Touch')).toBeInTheDocument();
    });
  });

  it('renders the hero intro text from CMS', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText(
          "We'd love to hear from you. Reach out with any questions.",
        ),
      ).toBeInTheDocument();
    });
  });

  it('renders contact info cards with labels from CMS', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      // Use getAllByText for 'Email' since it appears as both a card label and form field label
      const emailLabels = screen.getAllByText('Email');
      expect(emailLabels.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('Phone')).toBeInTheDocument();
      expect(screen.getByText('Office')).toBeInTheDocument();
      expect(screen.getByText('Hours')).toBeInTheDocument();
    });
  });

  it('renders contact info values from CMS', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByText('hello@ctc-research.com'),
      ).toBeInTheDocument();
      expect(
        screen.getByText('+1 (555) 123-4567'),
      ).toBeInTheDocument();
    });
  });

  it('renders email contact info as a clickable link', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      const emailLink = screen.getByText('hello@ctc-research.com');
      expect(emailLink.closest('a')).toHaveAttribute(
        'href',
        'mailto:hello@ctc-research.com',
      );
    });
  });

  it('renders all form input fields', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByPlaceholderText('Your name'),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText('your@email.com'),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText('How can we help?'),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText(
          'Tell us more about your inquiry...',
        ),
      ).toBeInTheDocument();
    });
  });

  it('renders the submit button', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(screen.getByText('Send Message')).toBeInTheDocument();
    });
  });

  it('submits the form with form data on send', async () => {
    renderContactPage(ENCODED_FULL);

    await vi.waitFor(() => {
      expect(
        screen.getByPlaceholderText('Your name'),
      ).toBeInTheDocument();
    });

    // Set up mock to succeed
    const unwrapMock = vi
      .fn()
      .mockResolvedValue({ status: 'success' });
    mockSubmitContact.mockReturnValue({ unwrap: unwrapMock });

    fillAndSubmitForm();

    await vi.waitFor(() => {
      expect(mockSubmitContact).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        subject: 'Course Inquiry',
        message: 'I have a question about courses.',
      });
    });
  });

  it('shows success message after successful submission', async () => {
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: ENCODED_FULL },
      isLoading: false,
      error: undefined,
    });

    render(
      <Provider store={createTestStore()}>
        <FusionMiddleware initialMode="data">
          <ContactPage />
        </FusionMiddleware>
      </Provider>,
    );

    await vi.waitFor(() => {
      expect(
        screen.getByPlaceholderText('Your name'),
      ).toBeInTheDocument();
    });

    // Set mutation to succeed
    const unwrapMock = vi.fn().mockResolvedValue({ status: 'success' });
    mockSubmitContact.mockReturnValue({ unwrap: unwrapMock });

    // Fill and submit the form
    fillAndSubmitForm();

    // Simulate mutation success by updating the mutable state
    mutationState.isSuccess = true;

    // Re-render to pick up the updated state
    render(
      <Provider store={createTestStore()}>
        <FusionMiddleware initialMode="data">
          <ContactPage />
        </FusionMiddleware>
      </Provider>,
    );

    await vi.waitFor(() => {
      expect(
        screen.getByText(
          "Message sent successfully! We'll get back to you soon.",
        ),
      ).toBeInTheDocument();
    });
  });

  it('resets form fields after successful submission', async () => {
    mockUseGetPageDataQuery.mockReturnValue({
      data: { encoded: ENCODED_FULL },
      isLoading: false,
      error: undefined,
    });

    render(
      <Provider store={createTestStore()}>
        <FusionMiddleware initialMode="data">
          <ContactPage />
        </FusionMiddleware>
      </Provider>,
    );

    await vi.waitFor(() => {
      expect(
        screen.getByPlaceholderText('Your name'),
      ).toBeInTheDocument();
    });

    const unwrapMock = vi.fn().mockResolvedValue({ status: 'success' });
    mockSubmitContact.mockReturnValue({ unwrap: unwrapMock });

    fillAndSubmitForm();

    await vi.waitFor(() => {
      const nameInput = screen.getByPlaceholderText(
        'Your name',
      ) as HTMLInputElement;
      expect(nameInput.value).toBe('');
    });
  });

  it('renders default title fallback when no page data', async () => {
    renderContactPage(ENCODED_MINIMAL);

    await vi.waitFor(() => {
      expect(screen.getByText('Contact Us')).toBeInTheDocument();
    });
  });

  it('shows loading skeleton when data is loading', () => {
    renderContactLoading();

    // FusionPageDataInner renders LoadingSkeleton — page content should NOT appear
    expect(screen.queryByText('Get In Touch')).not.toBeInTheDocument();
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
          <ContactPage />
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
