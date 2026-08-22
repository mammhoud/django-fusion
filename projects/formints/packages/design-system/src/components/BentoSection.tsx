/**
 * @formints/design-system — BentoSection Component
 * 
 * Section wrapper for bento grid layouts with title and description.
 * Provides consistent spacing and typography for dashboard sections.
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface BentoSectionProps extends HTMLAttributes<HTMLElement> {
  /** Section content */
  children: ReactNode;
  /** Section title */
  title?: string;
  /** Section description */
  description?: string;
  /** Optional action button(s) */
  actions?: ReactNode;
  /** Section eyebrow badge */
  eyebrow?: string;
  /** Eye accent color */
  accentColor?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
}

const accentDotColors = {
  primary: 'bg-primary',
  success: 'bg-success',
  warning: 'bg-warning',
  error: 'bg-error',
  info: 'bg-info',
  neutral: 'bg-neutral',
};

const BentoSection = forwardRef<HTMLElement, BentoSectionProps>(
  (
    {
      children,
      title,
      description,
      actions,
      eyebrow,
      accentColor = 'primary',
      className = '',
      ...props
    },
    ref,
  ) => {
    const dotColor = accentDotColors[accentColor];

    return (
      <section
        ref={ref}
        className={`space-y-4 ${className}`}
        {...props}
      >
        {/* Section header */}
        {(title || eyebrow || actions) && (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="space-y-1">
              {/* Eyebrow badge */}
              {eyebrow && (
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-primary/10 text-primary">
                    <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
                    {eyebrow}
                  </span>
                </div>
              )}

              {/* Title */}
              {title && (
                <h2 className="text-sm font-semibold uppercase tracking-wider text-base-content/50 flex items-center gap-2">
                  {title}
                </h2>
              )}

              {/* Description */}
              {description && (
                <p className="text-xs text-base-content/40">{description}</p>
              )}
            </div>

            {/* Actions */}
            {actions && (
              <div className="flex items-center gap-2">
                {actions}
              </div>
            )}
          </div>
        )}

        {/* Section content */}
        {children}
      </section>
    );
  },
);

BentoSection.displayName = 'BentoSection';

export default BentoSection;
