/**
 * @formints/design-system — CompactRow Component
 * 
 * Ultra-compact inline CRUD row for dense data tables.
 * Features inline editing support, hover state reveals, and touch-friendly targets.
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface CompactRowProps extends HTMLAttributes<HTMLDivElement> {
  /** Row content */
  children: ReactNode;
  /** Selected state */
  selected?: boolean;
  /** Enable hover effects */
  hover?: boolean;
  /** Compact mode (reduced padding) */
  compact?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Selection checkbox */
  checkbox?: ReactNode;
  /** Action buttons (shown on hover) */
  actions?: ReactNode;
  /** Accent color for start edge */
  accent?: 'primary' | 'success' | 'warning' | 'error';
}

const CompactRow = forwardRef<HTMLDivElement, CompactRowProps>(
  (
    {
      children,
      selected = false,
      hover = true,
      compact = false,
      onClick,
      checkbox,
      actions,
      accent,
      className = '',
      ...props
    },
    ref,
  ) => {
    return (
      <div
        ref={ref}
        className={`
          group relative
          ${compact ? 'px-3 py-2' : 'px-4 py-3'}
          border-b border-base-300/30 dark:border-white/5
          ${selected ? 'bg-primary/5 dark:bg-primary/10' : ''}
          ${hover && !selected ? 'hover:bg-base-200/50 dark:hover:bg-white/5' : ''}
          ${onClick ? 'cursor-pointer' : ''}
          transition-colors duration-200
          ${className}
        `}
        onClick={onClick}
        {...props}
      >
        {/* RTL-aware accent bar */}
        {accent && (
          <div
            className="absolute top-0 bottom-0 inset-inline-start-0 w-0.5 rounded-l"
            style={{ backgroundColor: `var(--color-${accent})` }}
          />
        )}

        {/* Selection checkbox */}
        {checkbox && (
          <div className="absolute start-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {checkbox}
          </div>
        )}

        {/* Content */}
        <div className="flex items-center gap-3">
          {children}
        </div>

        {/* Actions (shown on hover) */}
        {actions && (
          <div className="absolute end-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div className="flex items-center gap-1">
              {actions}
            </div>
          </div>
        )}
      </div>
    );
  },
);

CompactRow.displayName = 'CompactRow';

export default CompactRow;
