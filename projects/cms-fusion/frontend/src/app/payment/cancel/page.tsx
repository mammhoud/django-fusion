'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { HiXCircle, HiArrowLeft, HiRefresh } from 'react-icons/hi';

function PaymentCancelContent() {
  const searchParams = useSearchParams();
  const enrollmentId = searchParams?.get('enrollment_id');

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg w-full text-center"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
          className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6"
        >
          <HiXCircle className="w-12 h-12 text-yellow-600" />
        </motion.div>

        <h1 className="text-3xl font-bold text-gray-900 mb-3">Payment Canceled</h1>
        <p className="text-gray-500 text-lg mb-2">
          Your payment was not completed.
        </p>
        <p className="text-gray-500 mb-8">
          No charges have been made. You can try again whenever you&apos;re ready.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {enrollmentId && (
            <button
              onClick={() => window.location.href = `/enroll/checkout/${enrollmentId}`}
              className="btn-primary flex items-center justify-center gap-2"
            >
              <HiRefresh className="w-4 h-4" />
              Try Again
            </button>
          )}
          <button
            onClick={() => window.location.href = '/courses'}
            className="btn-secondary flex items-center justify-center gap-2"
          >
            <HiArrowLeft className="w-4 h-4" />
            Browse Courses
          </button>
        </div>

        <p className="text-xs text-gray-400 mt-8">
          Need help? Contact our support team for assistance with your enrollment.
        </p>
      </motion.div>
    </div>
  );
}

export default function PaymentCancelPage() {
  return (
    <Suspense fallback={<div className="min-h-[70vh] flex items-center justify-center"><div className="w-10 h-10 border-2 border-[rgb(var(--fu-primary))] border-t-transparent rounded-full animate-spin" /></div>}>
      <PaymentCancelContent />
    </Suspense>
  );
}
