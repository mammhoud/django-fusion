'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { HiCheckCircle, HiAcademicCap, HiArrowRight, HiMail, HiExclamation, HiRefresh } from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetStudentEnrollmentsQuery, useVerifyPaymentMutation } from '@/store/api/endpoints/students';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

function PaymentSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const enrollmentId = searchParams?.get('enrollment_id');
  const urlTxId = searchParams?.get('transaction_id');

  const { data: profile, isLoading: profileLoading, error: profileError, refetch: refetchProfile } = useGetProfileQuery();
  const { data: enrollments, isLoading: enrollmentsLoading } = useGetStudentEnrollmentsQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });
  const [verifyPayment, { isLoading: verifying }] = useVerifyPaymentMutation();

  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [verifyAttempted, setVerifyAttempted] = useState(false);
  const [verifySuccess, setVerifySuccess] = useState(false);

  // Resolve transaction_id — prefer URL param, fall back to enrollment data
  // (for PayPal/Paymo redirects that can't carry the tx_id in the return URL)
  const enrollment = enrollments?.find((e) => String(e.id) === enrollmentId);
  const resolvedTxId = urlTxId || String(enrollment?.payment_transaction_id ?? '');

  // Call verify endpoint on mount (only once the user profile is available)
  useEffect(() => {
    if (!profile || !resolvedTxId || verifyAttempted) return;

    const runVerify = async () => {
      setVerifyAttempted(true);
      try {
        const result = await verifyPayment({ transaction_id: Number(resolvedTxId) }).unwrap();
        if (result.data.success) {
          setVerifySuccess(true);
        } else {
          setVerifyError(result.data.message || 'Payment verification returned an unexpected status.');
        }
      } catch (err: any) {
        // Check for "already processed" — that's still a success from the user's POV
        const alreadyProcessed = err?.data?.data?.status === 'completed'
          || err?.data?.data?.message?.includes('already completed');
        if (alreadyProcessed) {
          setVerifySuccess(true);
        } else {
          setVerifyError(err?.data?.data?.message || err?.data?.message || 'Failed to verify payment. Please contact support.');
        }
      }
    };

    runVerify();
  }, [profile, resolvedTxId, verifyAttempted, verifyPayment]);

  // Auto-redirect after 10 seconds (only on success)
  useEffect(() => {
    if (!verifySuccess) return;
    const timer = setTimeout(() => {
      router.push('/student-dashboard');
    }, 10000);
    return () => clearTimeout(timer);
  }, [verifySuccess, router]);

  const isLoading = enrollmentsLoading || verifying;

  // ── Profile/auth gate — don't fall through to a success screen when the
  // ── profile request failed or the user is not signed in ──
  if (profileLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSkeleton variant="card" count={1} />
      </div>
    );
  }

  if (profileError || !profile) {
    return (
      <ErrorState
        fullPage
        message="Unable to load your enrollment details. Please sign in to continue."
        onRetry={refetchProfile}
      />
    );
  }

  // ── Verifying state ──
  if (isLoading && !verifyAttempted) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSkeleton variant="card" count={1} />
      </div>
    );
  }

  // ── Verifying in progress ──
  if (verifying) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <div className="text-center">
          <div className="w-20 h-20 bg-[rgb(var(--fu-primary))]/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <div className="w-10 h-10 border-2 border-[rgb(var(--fu-primary))] border-t-transparent rounded-full animate-spin" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifying Payment</h2>
          <p className="text-gray-500">Confirming your payment with the provider...</p>
        </div>
      </div>
    );
  }

  // ── Verification failed ──
  if (verifyError && !verifySuccess) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-lg w-full text-center"
        >
          <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <HiExclamation className="w-12 h-12 text-red-600" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-3">Payment Verification Issue</h1>
          <p className="text-gray-500 text-lg mb-2">{verifyError}</p>
          <p className="text-gray-400 mb-8 text-sm">
            Don&apos;t worry — no duplicate charges will be made. If your payment was already processed, it will reflect shortly.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {resolvedTxId && (
              <button
                onClick={() => {
                  setVerifyError(null);
                  setVerifyAttempted(false);
                }}
                className="btn-primary flex items-center justify-center gap-2"
              >
                <HiRefresh className="w-4 h-4" />
                Retry Verification
              </button>
            )}
            <button
              onClick={() => window.location.href = '/student-dashboard'}
              className="btn-secondary"
            >
              Go to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  // ── Success state ──
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg w-full text-center"
      >
        {/* Success Animation */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
          className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6"
        >
          <HiCheckCircle className="w-12 h-12 text-green-600" />
        </motion.div>

        <h1 className="text-3xl font-bold text-gray-900 mb-3">Payment Successful!</h1>
        <p className="text-gray-500 text-lg mb-2">
          You&apos;re now enrolled in
        </p>
        <p className="text-xl font-semibold text-gray-900 mb-8">
          {verifySuccess ? (enrollment?.course_title || 'your course') : 'your course'}
        </p>

        {/* Enrollment Details */}
        <div className="card p-6 mb-8 text-left space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[rgb(var(--fu-primary))]/10 rounded-lg flex items-center justify-center">
              <HiAcademicCap className="w-5 h-5 text-[rgb(var(--fu-primary))]" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Course</p>
              <p className="font-medium text-gray-900">{enrollment?.course_title || 'Course'}</p>
            </div>
          </div>

          {enrollment?.enrolled_at && (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <HiMail className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Enrolled on</p>
                <p className="font-medium text-gray-900">
                  {new Date(enrollment.enrolled_at).toLocaleDateString('en-US', {
                    month: 'long', day: 'numeric', year: 'numeric',
                  })}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => window.location.href = `/course-details/${enrollment?.course || ''}`}
            className="btn-primary flex items-center justify-center gap-2"
          >
            <HiAcademicCap className="w-4 h-4" />
            Start Learning
          </button>
          <button
            onClick={() => window.location.href = '/student-dashboard'}
            className="btn-secondary flex items-center justify-center gap-2"
          >
            Go to Dashboard
            <HiArrowRight className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs text-gray-400 mt-6">
          A confirmation email will be sent to your registered email address.
          You will be redirected to your dashboard in a few seconds.
        </p>
      </motion.div>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={<div className="min-h-[60vh] flex items-center justify-center"><LoadingSkeleton variant="card" count={1} /></div>}>
      <PaymentSuccessContent />
    </Suspense>
  );
}
