/**
 * @formints/design-system — CompactInput Component
 * 
 * Space-efficient form input for CRUD modals and widgets.
 * Features integrated label, validation states, and optional action button.
 */

import { type InputHTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface CompactInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Field label */
  label: string;
  /** Error message */
  error?: string;
  /** Hint text (shown when no error) */
  hint?: string;
  /** Show required asterisk */
  required?: boolean;
  /** Optional action button (e.g., generate, clear) */
  action?: ReactNode;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-7 text-[10px] px-2',
  md: 'h-8 text-xs px-2.5',
  lg: 'h-10 text-sm px-3',
};

const CompactInput = forwardRef<HTMLInputElement, CompactInputProps>(
  (
    {
      label,
      error,
      hint,
      required,
      action,
      size = 'md',
      className = '',
      ...props
    },
    ref,
  ) => {
    return (
      <div className="space-y-1">
        {/* Label */}
        <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
          {label}
          {required && <span className="text-error ml-0.5">*</span>}
        </label>

        {/* Input container */}
        <div className="flex items-center gap-1.5">
          <input
            ref={ref}
            className={`
              flex-1
              ${sizeClasses[size]}
              bg-base-100 dark:bg-base-900
              border rounded-lg
              ${error ? 'border-error' : 'border-base-300/50 dark:border-white/10'}
              focus:border-primary focus:ring-1 focus:ring-primary/20
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors duration-200
              placeholder:text-base-content/40
              ${className}
            `}
            {...props}
          />

          {/* Action button */}
          {action && (
            <div className="shrink-0">
              {action}
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <p className="text-[10px] text-error">{error}</p>
        )}

        {/* Hint text */}
        {hint && !error && (
          <p className="text-[10px] text-base-content/40">{hint}</p>
        )}
      </div>
    );
  },
);

CompactInput.displayName = 'CompactInput';

export default CompactInput;
