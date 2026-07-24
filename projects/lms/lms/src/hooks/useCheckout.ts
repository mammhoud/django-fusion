/**
 * useCheckout — unified enrollment + payment checkout hook.
 *
 * Combines `enrollInCourse` and `initializePayment` into a single
 * state-machine-driven hook so course-detail pages and checkout
 * pages share the same orchestration logic.
 *
 * Usage:
 *
 *   const {
 *     step, enrollment, paymentData, clientSecret, error,
 *     enroll, initPayment, onStripeSuccess, onStripeError, reset,
 *   } = useCheckout({ courseId: 42, price: 49.99 });
 *
 *   // Step 1 — enroll
 *   await enroll();  // → 'enrolled_free' or 'enrolled_paid'
 *
 *   // Step 2 (paid only) — init payment
 *   await initPayment('stripe');  // → 'stripe_form' | 'redirecting' | 'complete'
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';

import {
  useEnrollInCourseMutation,
  useInitializePaymentMutation,
  type PaymentInitResponse,
  type Enrollment,
} from '@/store/api/endpoints/students';

// ── Types ───────────────────────────────────────────────────────────

export type PaymentProvider = 'stripe' | 'paypal' | 'paymo';

export type CheckoutStep =
  | 'idle'               // waiting for user to click "enroll"
  | 'enrolling'          // POST /apis/enrollments in flight
  | 'enrolled_free'      // free course — enrolled, redirecting to course
  | 'enrolled_paid'      // paid course — enrollment created, needs payment
  | 'processing_payment' // POST /apis/enrollments/<id>/payment/init in flight
  | 'redirecting'        // being redirected to PayPal / Paymo
  | 'stripe_form'        // Stripe Elements card form visible
  | 'complete'           // payment confirmed — show success UI
  | 'error';             // something went wrong

export interface CheckoutState {
  /** Current step in the checkout flow. */
  step: CheckoutStep;
  /** The enrollment record (available after `enroll()` resolves). */
  enrollment: Enrollment | null;
  /** Raw payment init response from the backend. */
  paymentData: PaymentInitResponse | null;
  /** Stripe client secret for Elements (set when step === 'stripe_form'). */
  clientSecret: string | null;
  /** Payment transaction ID for verification. */
  transactionId: number | null;
  /** Human-readable error message. */
  error: string | null;
}

export interface UseCheckoutParams {
  courseId: number;
  price: number;
  isFree?: boolean;
  /** Pre-existing enrollment — skip enroll() and go directly to payment. */
  enrollment?: Enrollment;
}

export interface UseCheckoutReturn extends CheckoutState {
  /**
   * Enroll the authenticated user in the course.
   * - Free courses → step becomes 'enrolled_free' (caller should redirect).
   * - Paid courses → step becomes 'enrolled_paid' (caller should show payment UI).
   */
  enroll: () => Promise<void>;

  /**
   * Initialize a payment for the enrolled course (paid only).
   * - Stripe → step becomes 'stripe_form' (caller shows `<StripePaymentForm>`).
   * - PayPal / Paymo → step becomes 'redirecting' (hook sets window.location).
   * - No redirect needed → step becomes 'complete'.
   */
  initPayment: (provider: PaymentProvider, opts?: { redirectOrigin?: string }) => Promise<void>;

  /** Call from `<StripePaymentForm onSuccess>`.  Redirects to success page. */
  onStripeSuccess: () => void;

  /** Call from `<StripePaymentForm onError>`.  Returns to provider selection. */
  onStripeError: (message: string) => void;

  /** Reset the entire flow back to `idle`. */
  reset: () => void;
}

// ── Hook ────────────────────────────────────────────────────────────

export function useCheckout({ courseId, price, isFree = price === 0, enrollment: initialEnrollment }: UseCheckoutParams): UseCheckoutReturn {
  const [enrollMutation] = useEnrollInCourseMutation();
  const [initPaymentMutation] = useInitializePaymentMutation();

  // Ref-based busy flag avoids stale closures in useCallback
  const isBusyRef = useRef(false);

  const [state, setState] = useState<CheckoutState>(() => ({
    step: initialEnrollment ? 'enrolled_paid' : 'idle',
    enrollment: initialEnrollment || null,
    paymentData: null,
    clientSecret: null,
    transactionId: null,
    error: null,
  }));

  // Sync enrollment when it arrives after mount (checkout page loads it async)
  useEffect(() => {
    if (initialEnrollment && !state.enrollment) {
      setState((prev) => ({
        ...prev,
        step: 'enrolled_paid',
        enrollment: initialEnrollment,
      }));
    }
  }, [initialEnrollment]);

  // ── navigate ──────────────────────────────────────────────────────
  const navigateTo = useCallback((path: string) => {
    window.location.href = path;
  }, []);

  // ── enroll ────────────────────────────────────────────────────────
  const enroll = useCallback(async () => {
    // Guard against double-clicks / race conditions
    // Uses a ref instead of state to avoid stale-closure issues.
    if (isBusyRef.current) return;
    isBusyRef.current = true;
    setState((prev) => ({ ...prev, step: 'enrolling', error: null }));

    try {
      const result = await enrollMutation({ course_id: courseId }).unwrap();
      const enrollment = (result as any)?.data || result;

      if (isFree || enrollment?.payment_status === 'completed') {
        setState((prev) => ({
          ...prev,
          step: 'enrolled_free',
          enrollment,
          error: null,
        }));
        // Auto-redirect after a brief pause
        setTimeout(() => navigateTo(`/course-details/${courseId}`), 1500);
      } else {
        setState((prev) => ({
          ...prev,
          step: 'enrolled_paid',
          enrollment,
          error: null,
        }));
      }
    } catch (err: any) {
      const msg = err?.data?.message || err?.data?.error || '';
      if (msg.includes('Already enrolled')) {
        setState((prev) => ({
          ...prev,
          step: 'error',
          error: 'You are already enrolled in this course.',
        }));
        setTimeout(() => navigateTo(`/course-details/${courseId}`), 2000);
      } else {
        setState((prev) => ({
          ...prev,
          step: 'error',
          error: msg || 'Enrollment failed. Please try again.',
        }));
      }
    } finally {
      isBusyRef.current = false;
    }
  }, [courseId, isFree, enrollMutation, navigateTo]);

  // ── initPayment ───────────────────────────────────────────────────
  const initPayment = useCallback(async (
    provider: PaymentProvider,
    opts?: { redirectOrigin?: string },
  ) => {
    const enrollmentId = state.enrollment?.id;
    if (!enrollmentId) {
      setState((prev) => ({ ...prev, step: 'error', error: 'No enrollment found. Please enroll first.' }));
      return;
    }

    setState((prev) => ({ ...prev, step: 'processing_payment', error: null }));

    const origin = opts?.redirectOrigin || (typeof window !== 'undefined' ? window.location.origin : '');

    try {
      const result = await initPaymentMutation({
        enrollment_id: enrollmentId,
        data: {
          provider,
          success_url: `${origin}/payment/success?enrollment_id=${enrollmentId}`,
          cancel_url: `${origin}/payment/cancel?enrollment_id=${enrollmentId}`,
        },
      }).unwrap();

      // .unwrap() returns the data directly (not { data: ... })
      const responseData = (result as any)?.data || result;
      const txId = responseData.transaction_id;

      if (provider === 'stripe' && responseData.client_secret) {
        // Stripe Elements inline payment
        setState((prev) => ({
          ...prev,
          step: 'stripe_form',
          paymentData: responseData,
          clientSecret: responseData.client_secret,
          transactionId: txId,
        }));
      } else if (responseData.redirect_url) {
        // PayPal / Paymo redirect
        setState((prev) => ({
          ...prev,
          step: 'redirecting',
          paymentData: responseData,
          transactionId: txId,
        }));
        navigateTo(responseData.redirect_url);
      } else if (responseData.payment_url) {
        // Direct payment URL
        setState((prev) => ({
          ...prev,
          step: 'redirecting',
          paymentData: responseData,
          transactionId: txId,
        }));
        navigateTo(responseData.payment_url);
      } else {
        // Payment initialized without redirect — redirect to success page
        navigateTo(`/payment/success?enrollment_id=${enrollmentId}&transaction_id=${txId}`);
      }
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        step: 'error',
        error: err?.data?.message || err?.data?.error || 'Payment initialization failed. Please try again.',
      }));
    }
  }, [state.enrollment, initPaymentMutation, navigateTo]);

  // ── onStripeSuccess ───────────────────────────────────────────────
  const onStripeSuccess = useCallback(() => {
    if (state.transactionId) {
      navigateTo(`/payment/success?enrollment_id=${state.enrollment?.id}&transaction_id=${state.transactionId}`);
    } else {
      setState((prev) => ({ ...prev, step: 'complete' }));
      setTimeout(() => navigateTo('/student-dashboard'), 2000);
    }
  }, [state.transactionId, state.enrollment, navigateTo]);

  // ── onStripeError ─────────────────────────────────────────────────
  const onStripeError = useCallback((message: string) => {
    setState((prev) => ({
      ...prev,
      step: 'enrolled_paid',
      clientSecret: null,
      error: message,
    }));
  }, []);

  // ── reset ─────────────────────────────────────────────────────────
  const reset = useCallback(() => {
    isBusyRef.current = false;
    setState({
      step: 'idle',
      enrollment: null,
      paymentData: null,
      clientSecret: null,
      transactionId: null,
      error: null,
    });
  }, []);

  return {
    ...state,
    enroll,
    initPayment,
    onStripeSuccess,
    onStripeError,
    reset,
  };
}

