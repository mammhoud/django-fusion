/**
 * @formints/design-system — CompactLabel Component
 * 
 * Compact form label with optional required indicator and hint text.
 * Features uppercase tracking and semantic typography.
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface CompactLabelProps extends HTMLAttributes<HTMLLabelElement> {
  /** Label text */
  children: ReactNode;
  /** Show required asterisk */
  required?: boolean;
  /** Optional hint text */
  hint?: string;
  /** Size variant */
  size?: 'xs' | 'sm' | 'md';
}

const sizeClasses = {
  xs: 'text-[9px]',
  sm: 'text-[10px]',
  md: 'text-[11px]',
};

const CompactLabel = forwardRef<HTMLLabelElement, CompactLabelProps>(
  (
    {
      children,
      required = false,
      hint,
      size = 'sm',
      className = '',
      ...props
    },
    ref,
  ) => {
    return (
      <div className="space-y-0.5">
        <label
          ref={ref}
          className={`
            block font-medium
            text-base-content/70
            uppercase tracking-wide
            ${sizeClasses[size]}
            ${className}
          `}
          {...props}
        >
          {children}
          {required && <span className="text-error ml-0.5">*</span>}
        </label>
        {hint && (
          <p className="text-[9px] text-base-content/40">{hint}</p>
        )}
      </div>
    );
  },
);

CompactLabel.displayName = 'CompactLabel';

export default CompactLabel;
