/**
 * @formints/design-system — Design Tokens
 * 
 * Central source of truth for all design values used across Formint editions.
 * These tokens are consumed by both CSS and TypeScript/React components.
 */

// ═══════════════════════════════════════════════════════════════════
// Spacing Scale (8px base unit)
// ═══════════════════════════════════════════════════════════════════

export const spacing = {
  '0': '0px',
  '0.5': '2px',
  '1': '4px',
  '1.5': '6px',
  '2': '8px',
  '2.5': '10px',
  '3': '12px',
  '3.5': '14px',
  '4': '16px',
  '5': '20px',
  '6': '24px',
  '7': '28px',
  '8': '32px',
  '9': '36px',
  '10': '40px',
  '11': '44px',
  '12': '48px',
  '14': '56px',
  '16': '64px',
  '20': '80px',
  '24': '96px',
} as const;

export type SpacingToken = keyof typeof spacing;

// ═══════════════════════════════════════════════════════════════════
// Compact Widget Spacing
// ═══════════════════════════════════════════════════════════════════

export const widgetPadding = {
  xs: spacing['2'],    // 8px - Ultra compact
  sm: spacing['3'],    // 12px - Compact widgets
  md: spacing['4'],    // 16px - Standard widgets
  lg: spacing['5'],    // 20px - Featured widgets
  xl: spacing['6'],    // 24px - Hero widgets
} as const;

export const widgetGap = {
  xs: spacing['1'],    // 4px - Tight grouping
  sm: spacing['2'],    // 8px - Related items
  md: spacing['3'],    // 12px - Standard spacing
  lg: spacing['4'],    // 16px - Section breaks
  xl: spacing['6'],    // 24px - Major sections
} as const;

export const widgetMargin = {
  none: spacing['0'],
  xs: spacing['1'],    // 4px - Subtle separation
  sm: spacing['2'],    // 8px - Card spacing
  md: spacing['4'],    // 16px - Section spacing
  lg: spacing['6'],    // 24px - Major sections
  xl: spacing['8'],    // 32px - Page sections
} as const;

// ═══════════════════════════════════════════════════════════════════
// Typography Scale
// ═══════════════════════════════════════════════════════════════════

export const typography = {
  // Font families
  fontFamily: {
    sans: '"Inter", "system-ui", "-apple-system", "Segoe UI", sans-serif',
    mono: '"JetBrains Mono", "Fira Code", "Consolas", monospace',
  },

  // Font sizes
  fontSize: {
    '2xs': '0.625rem',   // 10px
    xs: '0.75rem',       // 12px
    sm: '0.875rem',      // 14px
    base: '1rem',        // 16px
    lg: '1.125rem',      // 18px
    xl: '1.25rem',       // 20px
    '2xl': '1.5rem',     // 24px
    '3xl': '1.875rem',   // 30px
    '4xl': '2.25rem',    // 36px
  },

  // Font weights
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },

  // Line heights
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2',
  },

  // Letter spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
} as const;

// ═══════════════════════════════════════════════════════════════════
// Border Radius (Double-Bezel system)
// ═══════════════════════════════════════════════════════════════════

export const radius = {
  none: '0px',
  sm: '0.25rem',        // 4px
  md: '0.375rem',       // 6px
  lg: '0.5rem',         // 8px
  xl: '0.75rem',        // 12px
  '2xl': '1rem',        // 16px
  '3xl': '1.5rem',      // 24px
  full: '9999px',

  // Double-Bezel specific
  bezelOuter: '1.5rem',     // 24px - Outer shell
  bezelInner: '1.125rem',   // 18px - Inner core (concentric)
  widget: '0.75rem',        // 12px - Compact widgets
  card: '1rem',             // 16px - Standard cards
  button: '9999px',         // Pill buttons
  input: '0.5rem',          // 8px - Form inputs
  badge: '9999px',          // Status badges
} as const;

// ═══════════════════════════════════════════════════════════════════
// Shadows (Premium depth)
// ═══════════════════════════════════════════════════════════════════

export const shadow = {
  // Double-Bezel nested shadows
  bezelOuter: '0 0 0 1px rgba(255, 255, 255, 0.1)',
  bezelInner: 'inset 0 1px 1px rgba(255, 255, 255, 0.15)',
  bezelHover: '0 8px 24px rgba(0, 0, 0, 0.12)',

  // Card elevation
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

  // Widget depth
  widget: '0 2px 8px rgba(0, 0, 0, 0.08)',
  widgetHover: '0 4px 16px rgba(0, 0, 0, 0.12)',

  // Glass effect
  glass: '0 8px 32px rgba(0, 0, 0, 0.12)',

  // Inset shadows
  inset: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
  insetLg: 'inset 0 4px 8px 0 rgba(0, 0, 0, 0.1)',
} as const;

// ═══════════════════════════════════════════════════════════════════
// Motion (Custom cubic-bezier) — Premium Easing Functions
// ═══════════════════════════════════════════════════════════════════

export const motion = {
  // Easing functions
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    // Premium fluid transitions (organic, natural feel)
    fluid: 'cubic-bezier(0.32, 0.72, 0, 1)',
    snap: 'cubic-bezier(0.32, 0.72, 0, 1)',
    bounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    spring: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    elastic: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  // Duration tokens
  duration: {
    instant: '0ms',
    fast: '100ms',
    normal: '200ms',
    slow: '300ms',
    slower: '500ms',
    slowest: '700ms',
  },

  // Stagger delays (for list/grid items)
  stagger: {
    1: '50ms',
    2: '75ms',
    3: '100ms',
    4: '125ms',
    5: '150ms',
    6: '175ms',
    7: '200ms',
    8: '225ms',
    9: '250ms',
    10: '275ms',
    11: '300ms',
    12: '325ms',
    13: '350ms',
    14: '375ms',
    15: '400ms',
    16: '450ms',
    17: '500ms',
    18: '550ms',
    19: '600ms',
    20: '700ms',
  },

  // Scale transforms
  scale: {
    '90': '0.9',
    '95': '0.95',
    '97': '0.975',
    '100': '1',
    '102': '1.025',
    '105': '1.05',
    '110': '1.1',
  },
} as const;

// ═══════════════════════════════════════════════════════════════════
// Z-Index Scale
// ═══════════════════════════════════════════════════════════════════

export const zIndex = {
  base: '0',
  dropdown: '1000',
  sticky: '1100',
  fixed: '1200',
  modalBackdrop: '1300',
  modal: '1400',
  popover: '1500',
  tooltip: '1600',
  toast: '1700',
} as const;

// ═══════════════════════════════════════════════════════════════════
// Breakpoints
// ═══════════════════════════════════════════════════════════════════

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ═══════════════════════════════════════════════════════════════════
// Color Tokens (Semantic)
// ═══════════════════════════════════════════════════════════════════

export const colors = {
  // Primary palette
  primary: {
    50: 'oklch(0.97 0.02 160)',
    100: 'oklch(0.93 0.04 160)',
    200: 'oklch(0.87 0.08 160)',
    300: 'oklch(0.79 0.12 160)',
    400: 'oklch(0.72 0.16 160)',
    500: 'oklch(0.65 0.2 160)',
    600: 'oklch(0.57 0.22 160)',
    700: 'oklch(0.49 0.2 160)',
    800: 'oklch(0.41 0.16 160)',
    900: 'oklch(0.33 0.12 160)',
    950: 'oklch(0.25 0.08 160)',
  },

  // Semantic colors
  success: {
    light: '#10b981',
    DEFAULT: '#059669',
    dark: '#047857',
  },
  warning: {
    light: '#fbbf24',
    DEFAULT: '#d97706',
    dark: '#b45309',
  },
  error: {
    light: '#f87171',
    DEFAULT: '#dc2626',
    dark: '#b91c1c',
  },
  info: {
    light: '#60a5fa',
    DEFAULT: '#3b82f6',
    dark: '#2563eb',
  },

  // Neutral palette
  neutral: {
    50: 'oklch(0.98 0.005 260)',
    100: 'oklch(0.96 0.005 260)',
    200: 'oklch(0.92 0.005 260)',
    300: 'oklch(0.87 0.005 260)',
    400: 'oklch(0.70 0.005 260)',
    500: 'oklch(0.55 0.005 260)',
    600: 'oklch(0.45 0.005 260)',
    700: 'oklch(0.35 0.005 260)',
    800: 'oklch(0.25 0.005 260)',
    900: 'oklch(0.15 0.005 260)',
    950: 'oklch(0.08 0.005 260)',
  },
} as const;

// ═══════════════════════════════════════════════════════════════════
// Combined Token Export
// ═══════════════════════════════════════════════════════════════════

export const tokens = {
  spacing,
  widgetPadding,
  widgetGap,
  widgetMargin,
  typography,
  radius,
  shadow,
  motion,
  zIndex,
  breakpoints,
  colors,
} as const;

export type Tokens = typeof tokens;
