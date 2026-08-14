import { type HTMLAttributes, forwardRef } from 'react';

// ── BEM style presets ──

const bemModifiers: Record<string, string> = {
  glass: 'card--glass',
  elevated: 'card--elevated',
  bordered: 'card--bordered',
  flat: 'card--flat',
  interactive: 'card--interactive',
  primary: 'card--primary',
  compact: 'card--compact',
  bezel: 'card--bezel',
};

const paddingClasses = {
  xs: 'p-2',
  sm: 'p-3',
  md: 'p-4',          // BEM default padding via --card__padding-x/y, p-4 as fallback
  lg: 'p-5',
  xl: 'p-6',
  '2xl': 'p-8',
  none: 'p-0',
} as const;

const radiusClasses = {
  lg: 'rounded-lg',
  xl: '',             // BEM default uses --radius--lg
  '2xl': 'rounded-2xl',
  none: 'rounded-none',
} as const;

const shadowClasses = {
  sm: '',             // BEM default has --shadow--sm
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: '',             // use card--elevated for xl shadow
  none: 'shadow-none',
} as const;

/** Map old `border` prop values to BEM variant, for backward compat */
const borderToVariant: Record<string, string> = {
  'base-200': 'bordered',
  'base-300': 'bordered',
  'theme': 'bordered',
};

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  /** Padding preset. Default: md (p-4 + BEM variable) */
  padding?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'none';
  /** Border radius. Default: xl (uses BEM --radius--lg) */
  radius?: 'lg' | 'xl' | '2xl' | 'none';
  /** Shadow depth. Default: sm (BEM default shadow) */
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | 'none';
  /** BEM card modifier — applies a preset card class.
   *  `bezel` renders the Double-Bezel (Doppelrand) nested enclosure:
   *  an outer machined shell (`.bezel`) around an inner core (`.bezel-core`)
   *  with a concentric radius — the register client's signature card. */
  variant?: 'glass' | 'elevated' | 'bordered' | 'flat' | 'interactive' | 'primary' | 'compact' | 'bezel';
  /** Legacy border prop — maps to variant='bordered'. Kept for backward compat. */
  border?: 'base-200' | 'base-300' | 'theme' | 'none';
  /** Enable hover lift effect (card--hover) */
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
      variant,
      border,
      hover,
      center,
      transitional,
      spaceY,
      ...props
    },
    ref,
  ) => {
    // Derive variant from legacy border prop if no explicit variant
    const resolvedVariant = variant || (border && borderToVariant[border]);

    // ── Double-Bezel (Doppelrand) variant — nested machined enclosure ──
    // Outer shell carries the bezel (hairline ring + tinted tray), the inner
    // core carries the surface + concentric radius. Padding/radius apply to
    // the core; hover lift applies to the shell.
    if (resolvedVariant === 'bezel') {
      return (
        <div
          ref={ref}
          className={`bezel ${hover ? 'transition-transform duration-300 hover:-translate-y-0.5' : ''} ${className}`}
          {...props}
        >
          <div
            className={`bezel-core ${paddingClasses[padding]} ${center ? 'text-center' : ''} ${spaceY ? `space-y-${spaceY}` : ''}`}
          >
            {children}
          </div>
        </div>
      );
    }

    const classes = [
      'card',
      hover && 'card--hover',
      resolvedVariant && bemModifiers[resolvedVariant],
      shadowClasses[shadow],
      radiusClasses[radius],
      paddingClasses[padding],
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
