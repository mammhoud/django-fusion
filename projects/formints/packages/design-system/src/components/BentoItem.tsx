/**
 * @formints/design-system — BentoItem Component
 * 
 * Individual grid item for BentoGrid with responsive spanning support.
 * Uses Double-Bezel architecture for premium nested card appearance.
 * 
 * Features:
 * - Responsive column/row spanning
 * - RTL-aware accent bar
 * - Hover lift effects
 * - Optional icon badge
 * - Loading skeleton state
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface BentoItemProps extends HTMLAttributes<HTMLDivElement> {
  /** Item content */
  children: ReactNode;
  /** Column span on desktop */
  colSpan?: 1 | 2 | 3 | 4 | 6 | 8 | 12;
  /** Row span on desktop */
  rowSpan?: 1 | 2 | 3;
  /** Column span on tablet */
  tabletColSpan?: 1 | 2 | 3 | 4;
  /** Accent color for outer shell */
  accent?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  /** Enable hover lift effect */
  hover?: boolean;
  /** Show accent bar on start edge */
  accentBar?: boolean;
  /** Loading skeleton state */
  loading?: boolean;
}

// Responsive col-span classes
const colSpanClasses: Record<number, string> = {
  1: 'lg:col-span-1',
  2: 'lg:col-span-2',
  3: 'lg:col-span-3',
  4: 'lg:col-span-4',
  6: 'lg:col-span-6',
  8: 'lg:col-span-8',
  12: 'lg:col-span-12',
};

// Responsive row-span classes
const rowSpanClasses: Record<number, string> = {
  1: 'lg:row-span-1',
  2: 'lg:row-span-2',
  3: 'lg:row-span-3',
};

// Tablet col-span classes
const tabletColSpanClasses: Record<number, string> = {
  1: 'sm:col-span-1',
  2: 'sm:col-span-2',
  3: 'sm:col-span-3',
  4: 'sm:col-span-4',
};

const accentClasses = {
  primary: 'border-primary/25',
  success: 'border-success/25',
  warning: 'border-warning/25',
  error: 'border-error/25',
  info: 'border-info/25',
  neutral: 'border-neutral/25',
};

const BentoItem = forwardRef<HTMLDivElement, BentoItemProps>(
  (
    {
      children,
      colSpan = 1,
      rowSpan = 1,
      tabletColSpan,
      accent,
      hover = true,
      accentBar = false,
      loading = false,
      className = '',
      ...props
    },
    ref,
  ) => {
    const colSpanStyle = colSpanClasses[colSpan] || '';
    const rowSpanStyle = rowSpanClasses[rowSpan] || '';
    const tabletColSpanStyle = tabletColSpan ? tabletColSpanClasses[tabletColSpan] : '';
    const accentStyle = accent ? accentClasses[accent] : '';

    // Loading skeleton
    if (loading) {
      return (
        <div
          ref={ref}
          className={`
            relative overflow-hidden
            bg-base-200/40 dark:bg-white/5
            border border-base-300/25 dark:border-white/10
            rounded-[1.5rem]
            p-4
            min-h-[180px]
            ${className}
          `}
          {...props}
        >
          <div className="space-y-3 animate-pulse">
            <div className="h-3 w-1/3 bg-base-300/50 rounded" />
            <div className="h-8 w-1/2 bg-base-300/50 rounded" />
            <div className="h-2 w-2/3 bg-base-300/50 rounded" />
          </div>
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={`
          relative overflow-hidden
          bg-base-200/40 dark:bg-white/5
          border border-base-300/25 dark:border-white/10
          rounded-[1.5rem]
          p-1.5
          shadow-[var(--shadow-bezel-outer)]
          ${hover ? 'transition-all duration-500 ease-[var(--ease-fluid)] hover:-translate-y-0.5 hover:shadow-[var(--shadow-bezel-hover)]' : ''}
          ${colSpanStyle}
          ${rowSpanStyle}
          ${tabletColSpanStyle}
          ${accentStyle}
          ${className}
        `}
        {...props}
      >
        {/* RTL-aware accent bar */}
        {accentBar && accent && (
          <div
            className="absolute top-0 bottom-0 inset-inline-start-0 w-1 rounded-l-[inherit]"
            style={{ backgroundColor: `var(--color-${accent})` }}
          />
        )}

        {/* Inner core */}
        <div
          className="
            flex flex-col flex-1
            bg-base-100 dark:bg-base-900
            rounded-[1.125rem]
            p-4
            shadow-[var(--shadow-bezel-inner)]
            h-full
          "
        >
          {children}
        </div>
      </div>
    );
  },
);

BentoItem.displayName = 'BentoItem';

export default BentoItem;
