import { type HTMLAttributes, forwardRef } from 'react';

// ── Style presets ──

const paddingClasses = {
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-5',
  xl: 'p-6',
  '2xl': 'p-8',
  none: '',
} as const;

const radiusClasses = {
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  none: '',
} as const;

const shadowClasses = {
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
  none: '',
} as const;

const borderClasses = {
  'base-200': 'border border-base-200',
  'base-300': 'border border-base-300',
  none: '',
} as const;

const hoverClasses = 'hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Padding preset: sm(p-3), md(p-4), lg(p-5), xl(p-6), 2xl(p-8). Default: md */
  padding?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'none';
  /** Border radius: lg, xl, 2xl. Default: xl */
  radius?: 'lg' | 'xl' | '2xl' | 'none';
  /** Shadow depth. Default: sm */
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | 'none';
  /** Theme-adaptive border. Default: no border */
  border?: 'base-200' | 'base-300' | 'none';
  /** Enable hover lift effect (-translate-y + shadow-lg) */
  hover?: boolean;
  /** Center text content */
  center?: boolean;
  /** Smooth theme-color transitions */
  transitional?: boolean;
  /** Vertical spacing between children */
  spaceY?: '3' | '4';
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      className = '',
      padding = 'md',
      radius = 'xl',
      shadow = 'sm',
      border = 'none',
      hover,
      center,
      transitional,
      spaceY,
      ...props
    },
    ref,
  ) => {
    const classes = [
      'card',
      'bg-base-100',
      shadowClasses[shadow],
      radiusClasses[radius],
      paddingClasses[padding],
      border !== 'none' && borderClasses[border],
      hover && hoverClasses,
      center && 'text-center',
      transitional && 'transition-colors duration-300',
      spaceY && `space-y-${spaceY}`,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div ref={ref} className={classes} {...props}>
        {children}
      </div>
    );
  },
);

Card.displayName = 'Card';

export default Card;
