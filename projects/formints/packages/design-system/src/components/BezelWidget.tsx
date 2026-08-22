/**
 * @formints/design-system — BezelWidget Component
 * 
 * Ultra-compact widget for dashboard stats and CRUD data display.
 * Uses Double-Bezel architecture with minimal padding.
 * 
 * Features:
 * - RTL-aware accent bar
 * - Icon badge with semantic color
 * - Optional sparkline area
 * - Compact mode for dense grids
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface BezelWidgetProps extends HTMLAttributes<HTMLDivElement> {
  /** Widget title */
  title: string;
  /** Primary value */
  value?: string | number;
  /** Description or delta text */
  desc?: string;
  /** Icon element */
  icon?: ReactNode;
  /** Color theme */
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  /** Show accent bar on start edge */
  accent?: boolean;
  /** Compact mode (reduced padding/font) */
  compact?: boolean;
  /** Loading skeleton state */
  loading?: boolean;
  /** Click handler */
  onClick?: () => void;
}

const colorClasses = {
  primary: {
    text: 'text-primary',
    bg: 'bg-primary/10',
    icon: 'text-primary',
  },
  success: {
    text: 'text-success',
    bg: 'bg-success/10',
    icon: 'text-success',
  },
  warning: {
    text: 'text-warning',
    bg: 'bg-warning/10',
    icon: 'text-warning',
  },
  error: {
    text: 'text-error',
    bg: 'bg-error/10',
    icon: 'text-error',
  },
  info: {
    text: 'text-info',
    bg: 'bg-info/10',
    icon: 'text-info',
  },
  neutral: {
    text: 'text-neutral',
    bg: 'bg-neutral/10',
    icon: 'text-neutral',
  },
};

const BezelWidget = forwardRef<HTMLDivElement, BezelWidgetProps>(
  (
    {
      title,
      value,
      desc,
      icon,
      color = 'primary',
      accent = false,
      compact = false,
      loading = false,
      onClick,
      className = '',
      ...props
    },
    ref,
  ) => {
    const colorStyle = colorClasses[color];
    const isClickable = !!onClick;

    // Loading skeleton
    if (loading) {
      return (
        <div
          ref={ref}
          className={`
            relative overflow-hidden
            bg-base-200/40 dark:bg-white/5
            border border-base-300/25 dark:border-white/10
            ${compact ? 'p-2.5 rounded-[1rem]' : 'p-3.5 rounded-[1.25rem]'}
            shadow-[var(--shadow-bezel-outer)]
            ${className}
          `}
          {...props}
        >
          <div className="space-y-2">
            <div className="h-2.5 w-16 bg-base-300/50 rounded animate-pulse" />
            <div className={`h-6 w-20 bg-base-300/50 rounded ${compact ? 'h-5 w-16' : ''} animate-pulse`} />
            <div className="h-2 w-24 bg-base-300/50 rounded animate-pulse" />
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
          ${compact ? 'p-2.5 rounded-[1rem]' : 'p-3.5 rounded-[1.25rem]'}
          shadow-[var(--shadow-bezel-outer)]
          ${isClickable ? 'cursor-pointer hover:bg-base-200/60 dark:hover:bg-white/8' : ''}
          transition-all duration-300 ease-[var(--ease-fluid)]
          ${className}
        `}
        onClick={onClick}
        {...props}
      >
        {/* RTL-aware accent bar */}
        {accent && (
          <div
            className="absolute top-0 bottom-0 inset-inline-start-0 w-1 rounded-l-[inherit]"
            style={{ backgroundColor: `var(--color-${color})` }}
          />
        )}

        {/* Icon badge */}
        {icon && (
          <div
            className={`
              absolute top-2.5 end-2.5 z-10
              ${compact ? 'w-7 h-7 rounded-lg' : 'w-9 h-9 rounded-xl'}
              flex items-center justify-center shrink-0
              ${colorStyle.bg}
              shadow-sm
            `}
          >
            <span className={`${colorStyle.icon} ${compact ? 'text-xs' : 'text-sm'}`}>{icon}</span>
          </div>
        )}

        {/* Inner core */}
        <div
          className={`
            flex flex-col flex-1
            bg-base-100 dark:bg-base-900
            ${compact ? 'p-2.5 rounded-[0.75rem]' : 'p-3 rounded-[0.875rem]'}
            shadow-[var(--shadow-bezel-inner)]
          `}
        >
          {/* Title */}
          <div className={`
            ${compact ? 'text-[10px]' : 'text-[11px]'}
            font-medium text-base-content/60 uppercase tracking-wide
            ${icon ? 'pe-10' : ''}
            truncate min-w-0
          `}>
            {title}
          </div>

          {/* Value */}
          {value !== undefined && (
            <div className={`
              ${compact ? 'text-lg' : 'text-2xl'}
              font-bold tabular-nums truncate min-w-0
              ${colorStyle.text}
              mt-0.5
            `}>
              {value}
            </div>
          )}

          {/* Description */}
          {desc && (
            <div className={`
              ${compact ? 'text-[10px]' : 'text-xs'}
              text-base-content/50
              line-clamp-1 min-w-0
              mt-1
            `}>
              {desc}
            </div>
          )}
        </div>
      </div>
    );
  },
);

BezelWidget.displayName = 'BezelWidget';

export default BezelWidget;
