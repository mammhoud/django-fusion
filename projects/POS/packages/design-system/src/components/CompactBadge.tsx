/**
 * @formints/design-system — CompactBadge Component
 * 
 * Minimal status badge for CRUD interfaces.
 * Features semantic colors, optional icon, and compact sizing.
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface CompactBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** Badge content */
  children: ReactNode;
  /** Badge variant */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'soft';
  /** Size variant */
  size?: 'xs' | 'sm' | 'md';
  /** Optional leading icon */
  icon?: ReactNode;
  /** Optional trailing icon */
  trailingIcon?: ReactNode;
}

const variantClasses = {
  default: 'bg-base-200 dark:bg-base-800 text-base-content',
  primary: 'bg-primary text-white',
  success: 'bg-success text-white',
  warning: 'bg-warning text-white',
  error: 'bg-error text-white',
  info: 'bg-info text-white',
  neutral: 'bg-neutral text-white',
  soft: 'bg-primary/10 text-primary',
};

const sizeClasses = {
  xs: 'h-4 px-1.5 text-[9px]',
  sm: 'h-5 px-2 text-[10px]',
  md: 'h-6 px-2.5 text-xs',
};

const CompactBadge = forwardRef<HTMLSpanElement, CompactBadgeProps>(
  (
    {
      children,
      variant = 'default',
      size = 'sm',
      icon,
      trailingIcon,
      className = '',
      ...props
    },
    ref,
  ) => {
    return (
      <span
        ref={ref}
        className={`
          inline-flex items-center justify-center gap-1
          rounded-full font-medium whitespace-nowrap
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${className}
        `}
        {...props}
      >
        {icon && <span className="shrink-0">{icon}</span>}
        {children}
        {trailingIcon && <span className="shrink-0">{trailingIcon}</span>}
      </span>
    );
  },
);

CompactBadge.displayName = 'CompactBadge';

export default CompactBadge;
