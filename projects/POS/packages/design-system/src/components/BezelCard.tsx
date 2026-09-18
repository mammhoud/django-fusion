/**
 * @formints/design-system — BezelCard Component
 * 
 * Double-Bezel (Doppelrand) nested card architecture.
 * Creates the illusion of machined hardware sitting in an aluminum tray.
 * 
 * Architecture:
 * - Outer shell: hairline ring + tinted tray
 * - Inner core: surface + concentric radius
 * - Premium hover lift with custom cubic-bezier
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface BezelCardProps extends HTMLAttributes<HTMLDivElement> {
  /** Card content */
  children: ReactNode;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Accent color for the outer shell border */
  accent?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  /** Enable hover lift effect */
  hover?: boolean;
  /** RTL-aware accent bar position */
  accentBar?: boolean;
  /** Compact mode (reduced padding) */
  compact?: boolean;
}

const sizeClasses = {
  sm: {
    outer: 'p-1 rounded-[1.25rem]',
    inner: 'p-3 rounded-[0.875rem]',
  },
  md: {
    outer: 'p-1.5 rounded-[1.5rem]',
    inner: 'p-4 rounded-[1.125rem]',
  },
  lg: {
    outer: 'p-2 rounded-[1.75rem]',
    inner: 'p-5 rounded-[1.375rem]',
  },
};

const accentClasses = {
  primary: 'border-primary/25',
  success: 'border-success/25',
  warning: 'border-warning/25',
  error: 'border-error/25',
  info: 'border-info/25',
  neutral: 'border-neutral/25',
};

const BezelCard = forwardRef<HTMLDivElement, BezelCardProps>(
  (
    {
      children,
      size = 'md',
      accent,
      hover = true,
      accentBar = false,
      compact = false,
      className = '',
      ...props
    },
    ref,
  ) => {
    const sizeStyle = sizeClasses[size];
    const accentStyle = accent ? accentClasses[accent] : '';

    return (
      <div
        ref={ref}
        className={`
          relative flex flex-col
          bg-base-200/40 dark:bg-white/5
          border border-base-300/25 dark:border-white/10
          ${sizeStyle.outer}
          ${accentStyle}
          shadow-[var(--shadow-bezel-outer)]
          ${hover ? 'transition-all duration-500 ease-[var(--ease-fluid)] hover:-translate-y-0.5 hover:shadow-[var(--shadow-bezel-hover)]' : ''}
          ${className}
        `}
        {...props}
      >
        {/* RTL-aware accent bar */}
        {accentBar && accent && (
          <div
            className="absolute top-0 bottom-0 inset-inline-start-0 w-1 rounded-l-[inherit]"
            style={{
              backgroundColor: `var(--color-${accent})`,
            }}
          />
        )}

        {/* Inner core */}
        <div
          className={`
            flex flex-col flex-1
            bg-base-100 dark:bg-base-900
            ${sizeStyle.inner}
            shadow-[var(--shadow-bezel-inner)]
          `}
        >
          {children}
        </div>
      </div>
    );
  },
);

BezelCard.displayName = 'BezelCard';

export default BezelCard;
