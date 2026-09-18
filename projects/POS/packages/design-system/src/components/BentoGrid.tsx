/**
 * @formints/design-system — BentoGrid Component
 * 
 * Asymmetric bento grid layout for dashboards and admin CRUD pages.
 * Breaks visual monotony with masonry-like CSS Grid of varying card sizes.
 * 
 * Features:
 * - Multiple layout variants (standard, asymmetric, editorial)
 * - Responsive column configurations
 * - Custom gap and spacing
 * - Mobile-first responsive design
 */

import { type HTMLAttributes, forwardRef, type ReactNode } from 'react';

export interface BentoGridProps extends HTMLAttributes<HTMLDivElement> {
  /** Grid content */
  children: ReactNode;
  /** Layout variant */
  variant?: 'standard' | 'asymmetric' | 'editorial' | 'dense';
  /** Custom gap size */
  gap?: 'xs' | 'sm' | 'md' | 'lg';
}

const gapClasses = {
  xs: 'gap-2',
  sm: 'gap-3',
  md: 'gap-4',
  lg: 'gap-6',
};

const variantClasses = {
  // Standard responsive grid
  standard: `
    grid grid-cols-1
    sm:grid-cols-2
    lg:grid-cols-3
    xl:grid-cols-4
  `,
  
  // Asymmetric bento - first item spans 2 cols on desktop
  asymmetric: `
    grid grid-cols-1
    sm:grid-cols-2
    lg:grid-cols-12
    lg:auto-rows-[minmax(180px,auto)]
  `,
  
  // Editorial split - large left, smaller right items
  editorial: `
    grid grid-cols-1
    md:grid-cols-2
    lg:grid-cols-12
  `,
  
  // Dense - more columns, smaller gaps
  dense: `
    grid grid-cols-1
    sm:grid-cols-2
    md:grid-cols-3
    lg:grid-cols-4
    xl:grid-cols-5
  `,
};

const BentoGrid = forwardRef<HTMLDivElement, BentoGridProps>(
  (
    {
      children,
      variant = 'standard',
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
          ${gapStyle}
          ${className}
        `}
        {...props}
      >
        {children}
      </div>
    );
  },
);

BentoGrid.displayName = 'BentoGrid';

export default BentoGrid;
