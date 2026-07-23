'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  HiArrowLeft, HiLockClosed, HiShieldCheck, HiCreditCard,
  HiAcademicCap, HiClock, HiUser, HiCheckCircle, HiExclamation,
} from 'react-icons/hi';
import { FaPaypal } from 'react-icons/fa';
import { SiStripe } from 'react-icons/si';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetStudentEnrollmentsQuery } from '@/store/api/endpoints/students';
import { useCheckout } from '@/hooks/useCheckout';
import StripePaymentForm from '@/components/payment/StripePaymentForm';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

type PaymentProvider = 'stripe' | 'paypal' | 'paymo';

export default function EnrollmentCheckoutPage() {
  const params = useParams();
  const enrollmentId = Number(params?.enrollmentId ?? 0);

  // ── Data fetching ──────────────────────────────────────────────────
  const { data: profile } = useGetProfileQuery();
  const { data: enrollments, isLoading: enrollmentsLoading } = useGetStudentEnrollmentsQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });

  const enrollment = enrollments?.find((e) => e.id === enrollmentId);

  // ── Checkout via useCheckout ───────────────────────────────────────
  const {
    step,
    clientSecret,
    error,
    initPayment,
    onStripeSuccess,
    onStripeError,
  } = useCheckout({
    courseId: enrollment?.course ?? 0,
    price: enrollment?.price ?? 0,
    enrollment: enrollment ?? undefined,
  });

  const [selectedProvider, setSelectedProvider] = useState<PaymentProvider>('stripe');

  // ── Derived UI state ───────────────────────────────────────────────
  const isProcessing = step === 'processing_payment';
  const showProviderSelection = step === 'enrolled_paid' || step === 'error' || step === 'idle';
  const payButtonLabel = isProcessing
    ? 'Initializing Payment...'
    : `Pay $${(enrollment?.price ?? 0).toFixed(2)}`;

  // ── Loading ────────────────────────────────────────────────────────
  if (enrollmentsLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  // ── Not found ──────────────────────────────────────────────────────
  if (!enrollment) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10">
        <ErrorState
          message="Enrollment not found. Please try enrolling in the course again."
          onRetry={() => { window.location.href = '/courses'; }}
        />
      </div>
    );
  }

  // ── Payment complete ───────────────────────────────────────────────
  if (step === 'complete') {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 200 }}>
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <HiCheckCircle className="w-10 h-10 text-green-600" />
          </div>
        </motion.div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h2>
        <p className="text-gray-500 mb-6">You&apos;re now enrolled in <strong>{enrollment.course_title}</strong>.</p>
        <div className="flex gap-3 justify-center">
          <Link href={`/course-details/${enrollment.course}`} className="btn-primary">
            Start Learning
          </Link>
          <Link href="/student-dashboard" className="btn-secondary">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const providers: { id: PaymentProvider; label: string; icon: React.ReactNode; description: string }[] = [
    {
      id: 'stripe',
      label: 'Credit Card',
      icon: <SiStripe className="w-6 h-6" />,
      description: 'Pay securely with Visa, Mastercard, or Amex',
    },
    {
      id: 'paypal',
      label: 'PayPal',
      icon: <FaPaypal className="w-6 h-6" />,
      description: 'Fast checkout with your PayPal account',
    },
    {
      id: 'paymo',
      label: 'Paymo',
      icon: <HiCreditCard className="w-6 h-6" />,
      description: 'Pay with Paymo wallet or local methods',
    },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link href={`/course-details/${enrollment.course}`}
            className="inline-flex items-center gap-2 text-gray-500 hover:text-indigo-600 mb-8 transition-colors">
        <HiArrowLeft className="w-4 h-4" /> Back to Course
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Left — Payment Form */}
        <div className="lg:col-span-3">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Complete Enrollment</h1>

            {/* Provider Selection */}
            {showProviderSelection && (
              <div className="card p-6 space-y-4">
                <h2 className="font-semibold text-gray-900 mb-1">Select Payment Method</h2>
                <p className="text-sm text-gray-500 mb-4">Choose how you&apos;d like to pay</p>

                {providers.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      setSelectedProvider(p.id);
                    }}
                    className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                      selectedProvider === p.id
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        selectedProvider === p.id ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {p.icon}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{p.label}</div>
                        <div className="text-sm text-gray-500">{p.description}</div>
                      </div>
                      {selectedProvider === p.id && (
                        <HiCheckCircle className="w-5 h-5 text-indigo-600" />
                      )}
                    </div>
                  </button>
                ))}

                {error && (
                  <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-xl text-sm">
                    <HiExclamation className="w-5 h-5 flex-shrink-0" />
                    {error}
                  </div>
                )}

                <button
                  onClick={() => initPayment(selectedProvider)}
                  disabled={isProcessing}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      {payButtonLabel}
                    </>
                  ) : (
                    <>
                      <HiLockClosed className="w-4 h-4" />
                      {payButtonLabel}
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Processing */}
            {step === 'processing_payment' && (
              <div className="card p-8 text-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Processing Payment</h3>
                <p className="text-sm text-gray-500">Please wait while we process your payment...</p>
              </div>
            )}

            {/* Stripe Elements Form */}
            {step === 'stripe_form' && clientSecret && (
              <div className="card p-6">
                <h2 className="font-semibold text-gray-900 mb-4">Enter Card Details</h2>
                <StripePaymentForm
                  clientSecret={clientSecret}
                  onSuccess={onStripeSuccess}
                  onError={onStripeError}
                />
              </div>
            )}

            {/* Redirecting */}
            {step === 'redirecting' && (
              <div className="card p-8 text-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <HiShieldCheck className="w-8 h-8 text-indigo-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Redirecting to {selectedProvider === 'paypal' ? 'PayPal' : 'Payment Page'}</h3>
                <p className="text-sm text-gray-500">You&apos;ll be redirected to complete your payment securely.</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Right — Order Summary */}
        <div className="lg:col-span-2">
          <div className="card p-6 lg:sticky lg:top-24">
            <h3 className="font-semibold text-gray-900 mb-4">Order Summary</h3>

            <div className="flex items-start gap-3 pb-4 border-b border-gray-100 mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <HiAcademicCap className="w-7 h-7 text-white/60" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 text-sm line-clamp-2">{enrollment.course_title}</p>
                <p className="text-xs text-gray-500 mt-1">{enrollment.instructor_name || 'Instructor'}</p>
              </div>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <HiClock className="w-4 h-4" />
                <span>{enrollment.duration || 'Self-paced'}</span>
              </div>
              <div className="flex items-center gap-2 text-gray-500">
                <HiUser className="w-4 h-4" />
                <span>{enrollment.instructor_name || 'Expert Instructor'}</span>
              </div>
            </div>

            <hr className="my-4" />

            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-gray-500">
                <span>Course Fee</span>
                <span className="font-medium text-gray-900">${enrollment.price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>Tax</span>
                <span className="text-xs">Included</span>
              </div>
              <hr />
              <div className="flex justify-between font-bold text-gray-900 text-lg">
                <span>Total</span>
                <span>${enrollment.price.toFixed(2)}</span>
              </div>
            </div>

            <div className="mt-6 flex items-start gap-2 text-xs text-gray-400">
              <HiShieldCheck className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>Your payment is secured by industry-standard encryption. We never store your card details.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
