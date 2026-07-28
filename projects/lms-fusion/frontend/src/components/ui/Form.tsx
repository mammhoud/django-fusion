'use client';

import { useState, type FormEvent, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import {
  HiCheckCircle,
  HiExclamationCircle,
  HiExclamationTriangle,
} from 'react-icons/hi';
import LoadingSpinner from './LoadingSpinner';

// ── Types ──

export interface FormFieldError {
  field: string;
  message: string;
}

export interface FormState {
  status: 'idle' | 'submitting' | 'success' | 'error';
  message?: string;
  errors?: FormFieldError[];
}

interface FormProps {
  /** Form content (fields) */
  children: ReactNode;
  /** Submit handler - return FormState or throw */
  onSubmit: (data: Record<string, string>) => Promise<FormState>;
  /** Called after successful submission */
  onSuccess?: () => void;
  /** Initial form state */
  initialState?: FormState;
  /** Submit button label */
  submitLabel?: string;
  /** Submit button loading label */
  submittingLabel?: string;
  /** Show success message inline */
  showSuccessMessage?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Reset form after success */
  resetOnSuccess?: boolean;
  /** Validate before submit - return error if invalid */
  validate?: (data: Record<string, string>) => FormFieldError[] | null;
  /** Custom success component */
  successComponent?: ReactNode;
  /** Form ID for external submit button */
  id?: string;
}

// ── Error display component ──

function FormErrors({ errors }: { errors: FormFieldError[] }) {
  if (!errors?.length) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg"
      role="alert"
    >
      <div className="flex items-center gap-2 mb-1">
        <HiExclamationTriangle className="w-4 h-4 text-red-500" />
        <p className="text-sm font-medium text-red-800">
          Please fix the following errors:
        </p>
      </div>
      <ul className="list-disc list-inside text-xs text-red-600 space-y-0.5">
        {errors.map((err, i) => (
          <li key={i}>
            <span className="font-medium">{err.field}:</span> {err.message}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

// ── Component ──

export default function Form({
  children,
  onSubmit,
  onSuccess,
  initialState,
  submitLabel = 'Submit',
  submittingLabel = 'Submitting...',
  showSuccessMessage = true,
  className = '',
  resetOnSuccess = false,
  validate,
  successComponent,
  id,
}: FormProps) {
  const [state, setState] = useState<FormState>(
    initialState ?? { status: 'idle' },
  );

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setState({ status: 'submitting' });

    const form = e.currentTarget;
    const formData = new FormData(form);
    const data: Record<string, string> = {};
    formData.forEach((value, key) => {
      data[key] = value.toString();
    });

    // Client-side validation
    if (validate) {
      const errors = validate(data);
      if (errors && errors.length > 0) {
        setState({ status: 'error', message: 'Please fix the errors below.', errors });
        return;
      }
    }

    try {
      const result = await onSubmit(data);
      if (result.status === 'success') {
        setState(result);
        onSuccess?.();
        if (resetOnSuccess) {
          form.reset();
        }
      } else {
        setState(result);
      }
    } catch (err) {
      setState({
        status: 'error',
        message: err instanceof Error ? err.message : 'An unexpected error occurred.',
      });
    }
  };

  // ── Success state ──
  if (state.status === 'success' && showSuccessMessage) {
    if (successComponent) return <>{successComponent}</>;
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center py-8"
      >
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <HiCheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">
          {state.message || 'Submitted successfully!'}
        </h3>
        <p className="text-sm text-gray-500">
          Thank you for your submission.
        </p>
      </motion.div>
    );
  }

  const isSubmitting = state.status === 'submitting';

  return (
    <form
      id={id}
      onSubmit={handleSubmit}
      className={`space-y-4 ${className}`}
      noValidate
    >
      {/* General error message */}
      {state.status === 'error' && state.message && !state.errors && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2"
          role="alert"
        >
          <HiExclamationCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700">{state.message}</p>
        </motion.div>
      )}

      {/* Field-level errors */}
      <FormErrors errors={state.errors ?? []} />

      {/* Form fields */}
      <div className={isSubmitting ? 'pointer-events-none opacity-60' : ''}>
        {children}
      </div>

      {/* Submit button */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary w-full flex items-center justify-center gap-2 !py-2.5"
        >
          {isSubmitting ? (
            <>
              <LoadingSpinner variant="circular" size="sm" color="white" />
              {submittingLabel}
            </>
          ) : (
            submitLabel
          )}
        </button>
      </div>
    </form>
  );
}

// ── Field wrapper ──

interface FormFieldProps {
  label?: string;
  name?: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
  hint?: string;
}

export function FormField({
  label,
  name,
  error,
  required,
  children,
  className = '',
  hint,
}: FormFieldProps) {
  return (
    <div className={className}>
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-1.5"
        >
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
      )}
      {children}
      {hint && !error && (
        <p className="mt-1 text-xs text-gray-400">{hint}</p>
      )}
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-1 text-xs text-red-500 flex items-center gap-1"
        >
          <HiExclamationCircle className="w-3.5 h-3.5" />
          {error}
        </motion.p>
      )}
    </div>
  );
}
