'use client';

import { HiExclamationCircle, HiRefresh } from 'react-icons/hi';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  fullPage?: boolean;
  className?: string;
}

export default function ErrorState({
  message = 'Something went wrong. Please try again.',
  onRetry,
  fullPage = false,
  className = '',
}: ErrorStateProps) {
  const content = (
    <div className={`text-center ${fullPage ? 'py-20' : 'py-12'} ${className}`}>
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <HiExclamationCircle className="w-8 h-8 text-red-500" />
      </div>
      <h3 className="text-lg font-semibold text-gray-700 mb-2">
        Oops! An error occurred
      </h3>
      <p className="text-gray-500 max-w-md mx-auto mb-6 text-sm">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-[rgb(var(--ctc-primary))] text-white rounded-lg
                     hover:bg-[rgb(var(--ctc-primary-dark))] transition-colors text-sm font-medium"
        >
          <HiRefresh className="w-4 h-4" />
          Try Again
        </button>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}
