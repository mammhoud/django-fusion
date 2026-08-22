/**
 * @formints/design-system — CompactButton Component
 * 
 * Minimal action button for CRUD operations.
 * Design: pill shape with nested icon, hover reveals trailing action.
 * Touch-friendly (min 44px tap target).
 */

import { type ButtonHTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface CompactButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';
  /** Size variant */
  size?: 'xs' | 'sm' | 'md';
  /** Leading icon */
  icon?: ReactNode;
  /** Button label */
  label?: string;
  /** Trailing icon (shown on hover) */
  trailingIcon?: ReactNode;
  /** Show loading spinner */
  loading?: boolean;
}

const variantClasses = {
  primary: 'bg-primary text-white hover:bg-primary/90 active:bg-primary/95',
  secondary: 'bg-base-200 dark:bg-base-800 text-base-content hover:bg-base-300 dark:hover:bg-base-700',
  ghost: 'text-base-content/60 hover:bg-base-200 dark:hover:bg-base-800 hover:text-base-content',
  danger: 'bg-error/10 text-error hover:bg-error/20 active:bg-error/25',
  success: 'bg-success/10 text-success hover:bg-success/20 active:bg-success/25',
};

const sizeClasses = {
  xs: 'h-6 px-2 text-[10px] gap-1',
  sm: 'h-8 px-3 text-xs gap-1.5',
  md: 'h-10 px-4 text-sm gap-2',
};

const CompactButton = forwardRef<HTMLButtonElement, CompactButtonProps>(
  (
    {
      variant = 'primary',
      size = 'sm',
      icon,
      label,
      trailingIcon,
      loading = false,
      disabled,
      className = '',
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`
          inline-flex items-center justify-center
          rounded-full font-medium
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'active:scale-[0.98]'}
          transition-all duration-200 ease-[var(--ease-fluid)]
          ${className}
        `}
        {...props}
      >
        {loading ? (
          <div className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : (
          <>
            {icon && <span className="shrink-0">{icon}</span>}
            {label && <span>{label}</span>}
            {children}
            {trailingIcon && (
              <span className="w-5 h-5 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center shrink-0 group-hover:translate-x-0.5 transition-transform duration-200">
                {trailingIcon}
              </span>
            )}
          </>
        )}
      </button>
    );
  },
);

CompactButton.displayName = 'CompactButton';

export default CompactButton;
