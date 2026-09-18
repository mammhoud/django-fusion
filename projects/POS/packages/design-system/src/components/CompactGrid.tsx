/**
 * @formints/design-system — CompactGrid Component
 * 
 * Responsive grid for CRUD widgets and cards.
 * Supports multiple layout patterns:
 * - Dense: uniform small cards
 * - Bento: asymmetric masonry-like layout
 * - Auto: responsive with sensible defaults
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface CompactGridProps extends HTMLAttributes<HTMLDivElement> {
  /** Grid content */
  children: ReactNode;
  /** Layout variant */
  variant?: 'dense' | 'bento' | 'auto' | 'masonry';
  /** Custom gap */
  gap?: 'xs' | 'sm' | 'md' | 'lg';
}

const gapClasses = {
  xs: 'gap-2',
  sm: 'gap-3',
  md: 'gap-4',
  lg: 'gap-6',
};

const variantClasses = {
  dense: `
    grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
  `,
  bento: `
    grid grid-cols-1 md:grid-cols-12 gap-4
    [&>*:first-child]:col-span-12 md:[&>*:first-child]:col-span-8
    [&>*:nth-child(2)]:col-span-12 md:[&>*:nth-child(2)]:col-span-4
    [&>*:nth-child(n+3)]:col-span-12 md:[&>*:nth-child(n+3)]:col-span-4
  `,
  auto: `
    grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
  `,
  masonry: `
    columns-1 sm:columns-2 lg:columns-3
    [&>*]:break-inside-avoid mb-4
  `,
};

const CompactGrid = forwardRef<HTMLDivElement, CompactGridProps>(
  (
    {
      children,
      variant = 'auto',
      gap = 'md',
      className = '',
      ...props
    },
    ref,
  ) => {
    const gapStyle = gapClasses[gap];
    const variantStyle = variantClasses[variant];

    return (
      <div
        ref={ref}
        className={`
          ${variantStyle}
          ${gap !== 'xs' ? gapStyle : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </div>
    );
  },
);

CompactGrid.displayName = 'CompactGrid';

export default CompactGrid;
