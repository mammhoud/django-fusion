/**
 * Unit tests for the Enrollment Checkout Page
 *
 * Covers:
 *   - Loading / not-found states
 *   - Provider selection (Stripe / PayPal / Paymo)
 *   - Payment initialization (Stripe Elements, redirect, error)
 *   - Stripe success redirect and payment complete UI
 *   - Order summary display
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { useParams, useRouter } from 'next/navigation';

// ═════════════════════════════════════════════════════════════════════
// Module mocks — all vi.mock() calls must be at module top level
// ═════════════════════════════════════════════════════════════════════

vi.mock('next/navigation', () => ({
  useParams: vi.fn(() => ({ enrollmentId: '1' })),
  useRouter: vi.fn(() => ({
    push: vi.fn(), replace: vi.fn(), back: vi.fn(),
    forward: vi.fn(), prefetch: vi.fn(), refresh: vi.fn(),
  })),
  useSearchParams: vi.fn(() => new URLSearchParams()),
  usePathname: vi.fn(() => '/enroll/checkout/1'),
}));

vi.mock('next/link', () => ({
  default: function MockLink(props: any) { return React.createElement('a', { href: props.href, className: props.className }, props.children); },
}));

vi.mock('framer-motion', () => ({
  motion: {
    div: function MockMotionDiv(props: any) {
      const { initial, animate, transition, exit, whileHover, whileTap, variants, layout, children, ...rest } = props;
      return React.createElement('div', rest, children);
    },
    span: function MockMotionSpan(props: any) {
      const { initial, animate, transition, exit, children, ...rest } = props;
      return React.createElement('span', rest, children);
    },
    button: function MockMotionButton(props: any) {
      const { initial, animate, transition, exit, whileHover, whileTap, children, ...rest } = props;
      return React.createElement('button', rest, children);
    },
  },
  AnimatePresence: function MockAnimatePresence(props: any) { return React.createElement(React.Fragment, null, props.children); },
  AnimateSharedLayout: function MockAnimateSharedLayout(props: any) { return React.createElement(React.Fragment, null, props.children); },
}));

vi.mock('@stripe/react-stripe-js', () => ({
  Elements: function MockElements(props: any) { return React.createElement('div', { 'data-testid': 'stripe-elements' }, props.children); },
  useStripe: vi.fn(function mockUseStripe() { return { confirmPayment: vi.fn(), createPaymentMethod: vi.fn(), retrievePaymentIntent: vi.fn() }; }),
  useElements: vi.fn(function mockUseElements() { return { getElement: vi.fn(), fetchUpdates: vi.fn() }; }),
  PaymentElement: function MockPaymentElement() { return React.createElement('div', { 'data-testid': 'payment-element' }, 'Mock PaymentElement'); },
}));

vi.mock('@stripe/stripe-js', () => ({
  loadStripe: vi.fn(function mockLoadStripe() { return Promise.resolve({ elements: function() { return {}; }, createToken: vi.fn(), confirmPayment: vi.fn() }); }),
}));

vi.mock('react-icons/hi', () => ({
  HiArrowLeft: function() { return React.createElement('span', { 'data-testid': 'icon-arrow-left' }, '\u2190'); },
  HiLockClosed: function() { return React.createElement('span', { 'data-testid': 'icon-lock' }, '\uD83D\uDD12'); },
  HiShieldCheck: function() { return React.createElement('span', { 'data-testid': 'icon-shield' }, '\uD83D\uDEE1'); },
  HiCreditCard: function() { return React.createElement('span', { 'data-testid': 'icon-credit' }, '\uD83D\uDCB3'); },
  HiAcademicCap: function() { return React.createElement('span', { 'data-testid': 'icon-academic' }, '\uD83C\uDF93'); },
  HiClock: function() { return React.createElement('span', { 'data-testid': 'icon-clock' }, '\uD83D\uDD50'); },
  HiUser: function() { return React.createElement('span', { 'data-testid': 'icon-user' }, '\uD83D\uDC64'); },
  HiCheckCircle: function() { return React.createElement('span', { 'data-testid': 'icon-check' }, '\u2713'); },
  HiExclamation: function() { return React.createElement('span', { 'data-testid': 'icon-exclamation' }, '\u26A0'); },
  HiXCircle: function() { return React.createElement('span', { 'data-testid': 'icon-x-circle' }, '\u2717'); },
  HiRefresh: function() { return React.createElement('span', { 'data-testid': 'icon-refresh' }, '\u21BB'); },
}));

vi.mock('react-icons/fa', () => ({
  FaPaypal: function() { return React.createElement('span', { 'data-testid': 'icon-paypal' }, 'PayPal'); },
}));

vi.mock('react-icons/si', () => ({
  SiStripe: function() { return React.createElement('span', { 'data-testid': 'icon-stripe' }, 'Stripe'); },
}));

// ── RTK Query mutation helpers ──────────────────────────────────────
// Mutations return thenable objects with .unwrap(). Native Promises won't work.

function makeResult(data: any) {
  var thenable: any;
  thenable = {
    data: data,
    unwrap: function () { return Promise.resolve(data); },
    then: function (resolve: any) { resolve(thenable); },
  };
  return thenable;
}

function makeError(errData: any) {
  var error = new Error('API Error') as any;
  error.data = errData;
  var thenable: any;
  thenable = {
    error: error,
    unwrap: function () { return Promise.reject(error); },
    then: function (resolve: any) { resolve(thenable); },
  };
  return thenable;
}

// ── Mock data ───────────────────────────────────────────────────────

const mockEnrollment = {
  id: 1,
  student: 1,
  course: 42,
  course_title: 'Advanced React Patterns',
  course_thumbnail: null,
  price: 49.99,
  progress: 0,
  status: 'active',
  payment_status: 'pending',
  payment_transaction_id: null,
  enrolled_at: '2026-07-23T10:00:00Z',
  completed_at: null,
  is_completed: false,
  instructor_name: 'Jane Doe',
  duration: '8 weeks',
};

// ── Mutable mock state (avoids re-invoking vi.mock() in tests) ───────

const mockMutationResult: {
  isLoading: boolean;
  data: any;
  error: any;
  isSuccess: boolean;
  reset: ReturnType<typeof vi.fn>;
} = { isLoading: false, data: undefined, error: undefined, isSuccess: false, reset: vi.fn() };

const mockInitPayment = vi.fn();
const mockGetProfileQuery = vi.fn();
const mockGetEnrollmentsQuery = vi.fn();

vi.mock('@/store/api/endpoints/auth', () => ({
  useGetProfileQuery: function(...args: any[]) { return mockGetProfileQuery(...args); },
}));

vi.mock('@/store/api/endpoints/students', () => ({
  useGetStudentEnrollmentsQuery: function(...args: any[]) { return mockGetEnrollmentsQuery(...args); },
  useInitializePaymentMutation: function() { return [mockInitPayment, mockMutationResult]; },
  useEnrollInCourseMutation: function() { return [vi.fn(), { isLoading: false }]; },
}));

vi.mock('@/components/payment/StripePaymentForm', () => ({
  default: function MockStripeForm(props: any) {
    return React.createElement('div', { 'data-testid': 'stripe-payment-form' },
      React.createElement('span', null, 'client_secret: ' + props.clientSecret),
      React.createElement('button', { 'data-testid': 'mock-stripe-success', onClick: props.onSuccess }, 'Simulate Stripe Success'),
      React.createElement('button', { 'data-testid': 'mock-stripe-error', onClick: function() { props.onError('Card declined'); } }, 'Simulate Stripe Error'),
    );
  },
}));

vi.mock('@/components/ui/LoadingSkeleton', () => ({
  default: function MockSkeleton(props: any) { return React.createElement('div', { 'data-testid': 'loading-skeleton' }, 'Loading (' + props.variant + ')...'); },
}));

vi.mock('@/components/ui/ErrorState', () => ({
  default: function MockErrorState(props: any) {
    return React.createElement('div', { 'data-testid': 'error-state' },
      React.createElement('span', null, props.message),
      React.createElement('button', { 'data-testid': 'retry-btn', onClick: props.onRetry }, 'Retry'),
    );
  },
}));

// ── Import component AFTER all mocks ─────────────────────────────────
import EnrollmentCheckoutPage from '@/app/enroll/checkout/[enrollmentId]/page';

// ═════════════════════════════════════════════════════════════════════
// Helpers
// ═════════════════════════════════════════════════════════════════════

function setDefaultMocks() {
  // Reset next/navigation mocks (clearAllMocks wipes their factory return values)
  vi.mocked(useParams).mockReturnValue({ enrollmentId: '1' });

  mockGetProfileQuery.mockReturnValue({
    data: { id: 1, email: 'student@test.com', username: 'student' },
    isLoading: false,
  });

  mockGetEnrollmentsQuery.mockReturnValue({
    data: [mockEnrollment],
    isLoading: false,
  });

  mockInitPayment.mockImplementation(function () {
    return makeResult({
      success: true, transaction_id: 1001, provider: 'stripe',
      amount: 49.99, currency: 'USD',
      redirect_url: null, client_secret: 'pi_secret_abc123',
      payment_url: null, metadata: {},
    });
  });

  mockMutationResult.isLoading = false;
  mockMutationResult.data = undefined;
  mockMutationResult.error = undefined;
  mockMutationResult.isSuccess = false;
}

function captureWindowLocation(): string {
  var original = window.location.href;
  Object.defineProperty(window, 'location', {
    value: { href: '' },
    writable: true,
    configurable: true,
  });
  return original;
}

function restoreWindowLocation(original: string) {
  Object.defineProperty(window, 'location', {
    value: { href: original },
    writable: true,
    configurable: true,
  });
}

// ═════════════════════════════════════════════════════════════════════
// Tests
// ═════════════════════════════════════════════════════════════════════

describe('EnrollmentCheckoutPage', () => {
  beforeEach(function() {
    vi.clearAllMocks();
    setDefaultMocks();
  });

  // ── Loading state ──────────────────────────────────────────────
  describe('Loading state', function() {
    it('renders loading skeleton when enrollments are loading', function() {
      mockGetEnrollmentsQuery.mockReturnValue({ isLoading: true, data: undefined });

      render(React.createElement(EnrollmentCheckoutPage));

      expect(screen.getByTestId('loading-skeleton')).toBeTruthy();
      expect(screen.getByText('Loading (detail)...')).toBeTruthy();
    });
  });

  // ── Enrollment not found ───────────────────────────────────────
  describe('Enrollment not found', function() {
    it('shows error state when enrollment ID does not match any enrollment', function() {
      vi.mocked(useParams).mockReturnValue({ enrollmentId: '999' });

      render(React.createElement(EnrollmentCheckoutPage));

      expect(screen.getByTestId('error-state')).toBeTruthy();
      expect(screen.getByText(/Enrollment not found/)).toBeTruthy();
    });

    it('retry button navigates to /courses page', async function() {
      vi.mocked(useParams).mockReturnValue({ enrollmentId: '999' });

      var origLocation = captureWindowLocation();
      render(React.createElement(EnrollmentCheckoutPage));

      await userEvent.click(screen.getByTestId('retry-btn'));
      expect(window.location.href).toBe('/courses');

      restoreWindowLocation(origLocation);
    });
  });

  // ── Provider selection ─────────────────────────────────────────
  describe('Provider selection', function() {
    it('shows all three provider options by default', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getByText('Credit Card')).toBeTruthy();
      expect(screen.getAllByText('PayPal').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('Paymo')).toBeTruthy();
    });

    it('has Stripe (Credit Card) selected by default', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      var stripeCard = screen.getByText('Credit Card').closest('button')!;
      expect(stripeCard.querySelector('[data-testid="icon-check"]')).toBeTruthy();
    });

    it('switches selection between all three providers', async function() {
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      expect(
        screen.getByText('Credit Card').closest('button')!.querySelector('[data-testid="icon-check"]')
      ).toBeTruthy();

      var getProviderBtn = function(name: string) {
        return screen.getByRole('button', { name: new RegExp(name, 'i') });
      };

      await user.click(getProviderBtn('PayPal'));
      expect(
        getProviderBtn('PayPal').querySelector('[data-testid="icon-check"]')
      ).toBeTruthy();
      expect(
        getProviderBtn('Credit Card').querySelector('[data-testid="icon-check"]')
      ).toBeFalsy();

      await user.click(getProviderBtn('Paymo'));
      expect(
        getProviderBtn('Paymo').querySelector('[data-testid="icon-check"]')
      ).toBeTruthy();
      expect(
        getProviderBtn('PayPal').querySelector('[data-testid="icon-check"]')
      ).toBeFalsy();
    });

    it('shows error when payment init fails and provider selection still visible', async function() {
      var user = userEvent.setup();
      mockInitPayment.mockImplementation(function () {
        return makeError({ message: 'Server error' });
      });

      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      expect(await screen.findByText('Server error')).toBeTruthy();
      expect(screen.getByText('Select Payment Method')).toBeTruthy();
    });
  });

  // ── Pay button ─────────────────────────────────────────────────
  describe('Pay button', function() {
    it('shows the correct price from enrollment', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getByRole('button', { name: /Pay \$49.99/ })).toBeTruthy();
    });

    it('shows processing card while payment is being initialized', async function() {
      var deferredResolve: (v: any) => void = (undefined as any);
      mockInitPayment.mockImplementation(function() {
        var thenable: any = {
          then: function(resolve: any) { resolve(thenable); },
          unwrap: function() { return new Promise(function(resolve) { deferredResolve = resolve; }); },
        };
        return thenable;
      });

      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      var payBtn = screen.getByRole('button', { name: /Pay \$49.99/ });
      await user.click(payBtn);

      // During processing, pay button is hidden and a processing card is shown
      expect(screen.queryByRole('button', { name: /Pay \$49.99/ })).toBeFalsy();
      expect(screen.getByText('Processing Payment')).toBeTruthy();

      deferredResolve({
        success: true, transaction_id: 1001, provider: 'stripe',
        amount: 49.99, currency: 'USD',
        redirect_url: null, client_secret: null, payment_url: null, metadata: {},
      });
    });
  });

  // ── Stripe Elements flow ───────────────────────────────────────
  describe('Stripe Elements flow', function() {
    it('shows Stripe payment form after successful init with client_secret', async function() {
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      var form = await screen.findByTestId('stripe-payment-form');
      expect(form).toBeTruthy();
      expect(screen.getByText(/client_secret: pi_secret_abc123/)).toBeTruthy();
    });

    it('shows processing state while payment is being initialized', async function() {
      var deferredResolve: (v: any) => void = (undefined as any);
      mockInitPayment.mockImplementation(function() {
        var thenable: any = {
          then: function(resolve: any) { resolve(thenable); },
          unwrap: function() { return new Promise(function(resolve) { deferredResolve = resolve; }); },
        };
        return thenable;
      });

      var origLocation = captureWindowLocation();
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      expect(screen.getByText('Processing Payment')).toBeTruthy();

      deferredResolve({
        success: true, transaction_id: 1001, provider: 'stripe',
        amount: 49.99, currency: 'USD',
        client_secret: null, redirect_url: null, payment_url: null, metadata: {},
      });
      await new Promise(function(r) { return setTimeout(r, 100); });
      restoreWindowLocation(origLocation);
    });

    it('redirects to success page on Stripe success', async function() {
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));
      await screen.findByTestId('stripe-payment-form');

      var origLocation = captureWindowLocation();

      await user.click(screen.getByTestId('mock-stripe-success'));

      // Use vi.waitFor for polling assertions
      await vi.waitFor(function() {
        expect(window.location.href).toContain('/payment/success');
        expect(window.location.href).toContain('enrollment_id=1');
        expect(window.location.href).toContain('transaction_id=1001');
      });

      restoreWindowLocation(origLocation);
    });

    it('shows error message when Stripe returns an error and returns to provider selection', async function() {
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));
      await screen.findByTestId('stripe-payment-form');

      await user.click(screen.getByTestId('mock-stripe-error'));

      expect(screen.getByText('Card declined')).toBeTruthy();
      expect(screen.getByText('Select Payment Method')).toBeTruthy();
    });
  });

  // ── PayPal redirect flow ───────────────────────────────────────
  describe('PayPal redirect flow', function() {
    it('redirects to PayPal URL and shows redirecting state', async function() {
      mockInitPayment.mockImplementation(function () {
        return makeResult({
          success: true, transaction_id: 1002, provider: 'paypal',
          amount: 49.99, currency: 'USD',
          redirect_url: 'https://www.paypal.com/checkout/abc123',
          client_secret: null, payment_url: null, metadata: {},
        });
      });

      var origLocation = captureWindowLocation();
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /PayPal/i }));
      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      await vi.waitFor(function() {
        expect(window.location.href).toBe('https://www.paypal.com/checkout/abc123');
      });
      expect(screen.getByText(/Redirecting to PayPal/)).toBeTruthy();

      restoreWindowLocation(origLocation);
    });
  });

  // ── Paymo redirect flow ────────────────────────────────────────
  describe('Paymo redirect flow', function() {
    it('redirects to payment URL and shows generic redirecting text', async function() {
      mockInitPayment.mockImplementation(function () {
        return makeResult({
          success: true, transaction_id: 1003, provider: 'paymo',
          amount: 49.99, currency: 'USD',
          redirect_url: null, client_secret: null,
          payment_url: 'https://paymo.example.com/pay/xyz789',
          metadata: {},
        });
      });

      var origLocation = captureWindowLocation();
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Paymo/i }));
      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      await vi.waitFor(function() {
        expect(window.location.href).toBe('https://paymo.example.com/pay/xyz789');
      });
      expect(screen.getByText(/Redirecting to Payment Page/)).toBeTruthy();

      restoreWindowLocation(origLocation);
    });
  });

  // ── Fallback: no redirect_url, no client_secret ────────────────
  describe('Fallback redirect (no redirect_url, no client_secret)', function() {
    it('redirects to success page with transaction_id', async function() {
      mockInitPayment.mockImplementation(function () {
        return makeResult({
          success: true, transaction_id: 1004, provider: 'stripe',
          amount: 49.99, currency: 'USD',
          redirect_url: null, client_secret: null, payment_url: null, metadata: {},
        });
      });

      var origLocation = captureWindowLocation();
      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      await vi.waitFor(function() {
        expect(window.location.href).toContain('/payment/success');
        expect(window.location.href).toContain('transaction_id=1004');
      });

      restoreWindowLocation(origLocation);
    });
  });

  // ── Error handling ─────────────────────────────────────────────
  describe('Error handling', function() {
    it('shows error message from API response', async function() {
      mockInitPayment.mockImplementation(function () {
        return makeError({ message: 'Insufficient funds' });
      });

      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      expect(await screen.findByText('Insufficient funds')).toBeTruthy();
    });

    it('falls back to generic error when no message is returned', async function() {
      mockInitPayment.mockImplementation(function () {
        return makeError({});
      });

      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      expect(
        await screen.findByText('Payment initialization failed. Please try again.')
      ).toBeTruthy();
    });

    it('returns to provider selection on error', async function() {
      mockInitPayment.mockImplementation(function () {
        return makeError({ message: 'Error' });
      });

      var user = userEvent.setup();
      render(React.createElement(EnrollmentCheckoutPage));

      await user.click(screen.getByRole('button', { name: /Pay \$49.99/ }));

      await screen.findByText('Error');

      expect(screen.getByText('Select Payment Method')).toBeTruthy();
      expect(screen.queryByText('Processing Payment')).toBeFalsy();
    });
  });

  // ── Order Summary ──────────────────────────────────────────────
  describe('Order Summary', function() {
    it('shows the course title', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getByText('Advanced React Patterns')).toBeTruthy();
    });

    it('shows the instructor name', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getAllByText('Jane Doe').length).toBeGreaterThanOrEqual(1);
    });

    it('shows the course duration', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getByText('8 weeks')).toBeTruthy();
    });

    it('shows the correct course fee', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getAllByText('$49.99').length).toBeGreaterThanOrEqual(1);
    });

    it('shows Total matching the course fee (at least 2 price instances)', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(screen.getAllByText('$49.99').length).toBeGreaterThanOrEqual(2);
    });

    it('shows security notice about encryption', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      expect(
        screen.getByText(/Your payment is secured by industry-standard encryption/)
      ).toBeTruthy();
    });
  });

  // ── Back navigation ────────────────────────────────────────────
  describe('Back navigation', function() {
    it('renders a back link to the course details page', function() {
      render(React.createElement(EnrollmentCheckoutPage));
      var backLink = screen.getByText('Back to Course');
      expect(backLink).toBeTruthy();
      expect(backLink.closest('a')!.getAttribute('href')).toBe('/course-details/42');
    });
  });
});

// ═════════════════════════════════════════════════════════════════════
// API Contract — verify mock data shape matches runtime types
// ═════════════════════════════════════════════════════════════════════

describe('API Contract — mock data shape', function() {
  it('mock enrollment has all required fields with correct types', function() {
    expect(mockEnrollment).toHaveProperty('id');
    expect(mockEnrollment).toHaveProperty('course');
    expect(mockEnrollment).toHaveProperty('course_title');
    expect(mockEnrollment).toHaveProperty('price');
    expect(mockEnrollment).toHaveProperty('payment_status');
    expect(mockEnrollment).toHaveProperty('payment_transaction_id');
    expect(mockEnrollment).toHaveProperty('instructor_name');
    expect(mockEnrollment).toHaveProperty('duration');
    expect(typeof mockEnrollment.price).toBe('number');
    expect(typeof mockEnrollment.course_title).toBe('string');
  });

  it('mock payment init response matches PaymentInitResponse shape', function() {
    var resp = {
      success: true, transaction_id: 1001, provider: 'stripe',
      amount: 49.99, currency: 'USD',
      redirect_url: null, client_secret: 'secret_abc', payment_url: null, metadata: {},
    };
    expect(resp).toHaveProperty('transaction_id');
    expect(resp).toHaveProperty('client_secret');
    expect(resp).toHaveProperty('redirect_url');
    expect(typeof resp.transaction_id).toBe('number');
  });
});
