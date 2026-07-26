'use client';

import React from 'react';
import { HiExclamationCircle } from 'react-icons/hi';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * React Error Boundary — catches runtime errors in the component tree and
 * displays a graceful fallback UI instead of crashing the whole page.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <YourComponent />
 *   </ErrorBoundary>
 */
export default class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[50vh] flex items-center justify-center px-4">
          <div className="text-center max-w-md">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <HiExclamationCircle className="w-10 h-10 text-red-500" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-2">
              An unexpected error occurred while rendering this page.
            </p>
            <p className="text-sm text-gray-500 mb-6 font-mono bg-gray-50 rounded-lg p-3 text-left overflow-auto max-h-24">
              {this.state.error?.message || 'Unknown error'}
            </p>
            <button
              onClick={this.handleRetry}
              className="px-6 py-2.5 bg-[rgb(var(--ctc-primary))] text-white rounded-lg hover:bg-[rgb(var(--ctc-primary-dark))]
                         transition-colors font-medium"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
