/**
 * Unit tests for `useCheckout` — enrollment + payment state machine hook.
 *
 * Covers every `CheckoutStep` transition.
 */

import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// ── Mutable mock state (hoisted so vi.mock() factories see them) ─────

const ctx = vi.hoisted(function () {
  // RTK Query mutations return thenable objects with .unwrap() directly on them.
  // The mock must return an object that is both thenable (has .then) AND has .unwrap().
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

  return {
    mockEnrollFn: vi.fn(),
    mockInitPaymentFn: vi.fn(),
    makeResult: makeResult,
    makeError: makeError,
  };
});

// ── Module-level mocks (run after vi.hoisted, before imports) ────────

vi.mock('@/store/api/endpoints/students', () => ({
  useEnrollInCourseMutation: function () { return [ctx.mockEnrollFn, { isLoading: false }]; },
  useInitializePaymentMutation: function () { return [ctx.mockInitPaymentFn, { isLoading: false }]; },
}));

vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(), replace: vi.fn(), back: vi.fn(),
    forward: vi.fn(), prefetch: vi.fn(), refresh: vi.fn(),
  })),
}));

import { useCheckout } from '@/hooks/useCheckout';

// ═════════════════════════════════════════════════════════════════════
// Helpers
// ═════════════════════════════════════════════════════════════════════

var enrolled_data = { id: 1, student: 1, course: 42, course_title: 'Test Course', price: 49.99, payment_status: 'pending' };

function renderCheckout(params?: { courseId?: number; price?: number; isFree?: boolean }) {
  var p = { courseId: 42, price: 49.99, ...params };
  return renderHook(function () { return useCheckout(p); });
}

function setupWindowLocation() {
  var orig = window.location.href;
  Object.defineProperty(window, 'location', {
    value: { href: '' },
    writable: true,
    configurable: true,
  });
  return orig;
}

function restoreWindowLocation(orig: string) {
  Object.defineProperty(window, 'location', {
    value: { href: orig },
    writable: true,
    configurable: true,
  });
}

// ═════════════════════════════════════════════════════════════════════
// Tests
// ═════════════════════════════════════════════════════════════════════

describe('useCheckout', function () {
  beforeEach(function () {
    vi.clearAllMocks();
  });

  // ── Initial state ──────────────────────────────────────────────
  it('starts in idle step with all nulls', function () {
    var result = renderCheckout().result;
    expect(result.current.step).toBe('idle');
    expect(result.current.enrollment).toBeNull();
    expect(result.current.paymentData).toBeNull();
    expect(result.current.clientSecret).toBeNull();
    expect(result.current.transactionId).toBeNull();
    expect(result.current.error).toBeNull();
  });

  // ── Free course ────────────────────────────────────────────────
  it('transitions idle → enrolling → enrolled_free for free course', async function () {
    ctx.mockEnrollFn.mockImplementation(function () {
      return ctx.makeResult({ ...enrolled_data, price: 0, payment_status: 'completed' });
    });

    var result = renderCheckout({ price: 0, isFree: true }).result;
    expect(result.current.step).toBe('idle');

    await act(function () { return result.current.enroll(); });

    expect(result.current.step).toBe('enrolled_free');
    expect(result.current.enrollment).not.toBeNull();
    expect(result.current.error).toBeNull();
  });

  // ── Paid course ────────────────────────────────────────────────
  it('transitions idle → enrolling → enrolled_paid for paid course', async function () {
    ctx.mockEnrollFn.mockImplementation(function () {
      return ctx.makeResult(enrolled_data);
    });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });

    expect(result.current.step).toBe('enrolled_paid');
    expect(result.current.enrollment).not.toBeNull();
    expect(result.current.enrollment?.payment_status).toBe('pending');
    expect(result.current.error).toBeNull();
  });

  // ── Stripe inline payment ──────────────────────────────────────
  it('transitions enrolled_paid → processing_payment → stripe_form for Stripe', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeResult({
        success: true, transaction_id: 1001, provider: 'stripe',
        amount: 49.99, currency: 'USD',
        redirect_url: null, client_secret: 'pi_secret_abc', payment_url: null, metadata: {},
      });
    });

    var result = renderCheckout().result;

    await act(function () { return result.current.enroll(); });
    expect(result.current.step).toBe('enrolled_paid');

    await act(function () { return result.current.initPayment('stripe'); });

    expect(result.current.step).toBe('stripe_form');
    expect(result.current.clientSecret).toBe('pi_secret_abc');
    expect(result.current.transactionId).toBe(1001);
    expect(result.current.error).toBeNull();
  });

  // ── PayPal redirect ────────────────────────────────────────────
  it('redirects to PayPal URL and sets step to redirecting', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeResult({
        success: true, transaction_id: 2001, provider: 'paypal',
        amount: 49.99, currency: 'USD',
        redirect_url: 'https://www.paypal.com/checkout/abc123',
        client_secret: null, payment_url: null, metadata: {},
      });
    });

    var orig = setupWindowLocation();
    var result = renderCheckout().result;

    await act(function () { return result.current.enroll(); });
    expect(result.current.step).toBe('enrolled_paid');

    await act(function () { return result.current.initPayment('paypal'); });

    expect(result.current.step).toBe('redirecting');
    expect(window.location.href).toBe('https://www.paypal.com/checkout/abc123');
    restoreWindowLocation(orig);
  });

  // ── Paymo redirect ─────────────────────────────────────────────
  it('redirects via payment_url for Paymo', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeResult({
        success: true, transaction_id: 3001, provider: 'paymo',
        amount: 49.99, currency: 'USD',
        redirect_url: null, client_secret: null,
        payment_url: 'https://paymo.example.com/pay/xyz789', metadata: {},
      });
    });

    var orig = setupWindowLocation();
    var result = renderCheckout().result;

    await act(function () { return result.current.enroll(); });
    await act(function () { return result.current.initPayment('paymo'); });

    expect(result.current.step).toBe('redirecting');
    expect(window.location.href).toBe('https://paymo.example.com/pay/xyz789');
    restoreWindowLocation(orig);
  });

  // ── Fallback redirect ──────────────────────────────────────────
  it('redirects to success page when no redirect_url or client_secret', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeResult({
        success: true, transaction_id: 4001, provider: 'stripe',
        amount: 49.99, currency: 'USD',
        redirect_url: null, client_secret: null, payment_url: null, metadata: {},
      });
    });

    var orig = setupWindowLocation();
    var result = renderCheckout().result;

    await act(function () { return result.current.enroll(); });
    await act(function () { return result.current.initPayment('stripe'); });

    expect(window.location.href).toContain('/payment/success');
    expect(window.location.href).toContain('transaction_id=4001');
    restoreWindowLocation(orig);
  });

  // ── Payment init error ─────────────────────────────────────────
  it('shows error when initPayment rejects with API message', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeError({ message: 'Insufficient funds' });
    });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });
    await act(function () { return result.current.initPayment('stripe'); });

    expect(result.current.step).toBe('error');
    expect(result.current.error).toBe('Insufficient funds');
  });

  it('shows generic error when initPayment fails with no message', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeError({});
    });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });
    await act(function () { return result.current.initPayment('stripe'); });

    expect(result.current.step).toBe('error');
    expect(result.current.error).toContain('Payment initialization failed');
  });

  it('shows error when initPayment is called before enrollment', async function () {
    var result = renderCheckout().result;
    await act(function () { return result.current.initPayment('stripe'); });

    expect(result.current.step).toBe('error');
    expect(result.current.error).toContain('No enrollment found');
  });

  // ── Enrollment error ───────────────────────────────────────────
  it('shows already-enrolled error when API says Already enrolled', async function () {
    ctx.mockEnrollFn.mockImplementation(function () {
      return ctx.makeError({ message: 'Already enrolled in this course' });
    });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });

    expect(result.current.step).toBe('error');
    expect(result.current.error).toBe('You are already enrolled in this course.');
  });

  it('shows generic error for other enrollment failures', async function () {
    ctx.mockEnrollFn.mockImplementation(function () {
      return ctx.makeError({ message: 'Server error' });
    });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });

    expect(result.current.step).toBe('error');
    expect(result.current.error).toBe('Server error');
  });

  // ── onStripeSuccess ────────────────────────────────────────────
  it('redirects to success page when transactionId is set', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeResult({
        success: true, transaction_id: 1001, provider: 'stripe',
        amount: 49.99, currency: 'USD',
        redirect_url: null, client_secret: 'pi_secret_abc', payment_url: null, metadata: {},
      });
    });

    var orig = setupWindowLocation();
    var result = renderCheckout().result;

    await act(function () { return result.current.enroll(); });
    await act(function () { return result.current.initPayment('stripe'); });
    expect(result.current.transactionId).toBe(1001);

    act(function () { result.current.onStripeSuccess(); });

    expect(window.location.href).toContain('/payment/success');
    expect(window.location.href).toContain('transaction_id=1001');
    restoreWindowLocation(orig);
  });

  it('falls back to complete step when no transactionId', function () {
    var result = renderCheckout().result;
    act(function () { result.current.onStripeSuccess(); });
    expect(result.current.step).toBe('complete');
  });

  // ── onStripeError ──────────────────────────────────────────────
  it('returns to enrolled_paid with error and clears clientSecret', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });
    ctx.mockInitPaymentFn.mockImplementation(function () {
      return ctx.makeResult({
        success: true, transaction_id: 1001, provider: 'stripe',
        amount: 49.99, currency: 'USD',
        redirect_url: null, client_secret: 'pi_secret_abc', payment_url: null, metadata: {},
      });
    });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });
    await act(function () { return result.current.initPayment('stripe'); });
    expect(result.current.clientSecret).toBe('pi_secret_abc');

    act(function () { result.current.onStripeError('Card declined'); });

    expect(result.current.step).toBe('enrolled_paid');
    expect(result.current.clientSecret).toBeNull();
    expect(result.current.error).toBe('Card declined');
  });

  // ── Reset ──────────────────────────────────────────────────────
  it('resets state back to idle defaults from any step', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });

    var result = renderCheckout().result;
    await act(function () { return result.current.enroll(); });
    expect(result.current.step).toBe('enrolled_paid');

    act(function () { result.current.reset(); });

    expect(result.current.step).toBe('idle');
    expect(result.current.enrollment).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('can restart flow after reset', async function () {
    ctx.mockEnrollFn.mockImplementation(function () { return ctx.makeResult(enrolled_data); });

    var result = renderCheckout().result;

    await act(function () { return result.current.enroll(); });
    expect(result.current.step).toBe('enrolled_paid');

    act(function () { result.current.reset(); });
    expect(result.current.step).toBe('idle');

    // Enroll again with different data
    ctx.mockEnrollFn.mockImplementation(function () {
      return ctx.makeResult({ ...enrolled_data, id: 10 });
    });
    await act(function () { return result.current.enroll(); });
    expect(result.current.step).toBe('enrolled_paid');
    expect(result.current.enrollment?.id).toBe(10);
  });

  // ── Double-click guard ─────────────────────────────────────────
  it('ignores second enroll() call while already enrolling', async function () {
    ctx.mockEnrollFn.mockImplementation(function () {
      return ctx.makeResult(enrolled_data);
    });

    var result = renderCheckout().result;

    act(function () { result.current.enroll(); });
    expect(result.current.step).toBe('enrolling');

    await act(function () { return result.current.enroll(); });
    expect(ctx.mockEnrollFn).toHaveBeenCalledTimes(1);
  });

  // ── Type contract ──────────────────────────────────────────────
  it('returns all expected actions as functions', function () {
    var result = renderCheckout().result;
    expect(typeof result.current.enroll).toBe('function');
    expect(typeof result.current.initPayment).toBe('function');
    expect(typeof result.current.onStripeSuccess).toBe('function');
    expect(typeof result.current.onStripeError).toBe('function');
    expect(typeof result.current.reset).toBe('function');
  });

  it('returns all expected state fields', function () {
    var result = renderCheckout().result;
    expect(result.current).toHaveProperty('step');
    expect(result.current).toHaveProperty('enrollment');
    expect(result.current).toHaveProperty('paymentData');
    expect(result.current).toHaveProperty('clientSecret');
    expect(result.current).toHaveProperty('transactionId');
    expect(result.current).toHaveProperty('error');
  });
});
