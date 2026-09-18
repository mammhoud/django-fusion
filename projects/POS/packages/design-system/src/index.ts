/**
 * @formints/design-system
 * 
 * Shared design system for Formint POS editions.
 * Provides design tokens, CSS utilities, and React components.
 * 
 * @packageDocumentation
 */

// ═══════════════════════════════════════════════════════════════════
// Design Tokens (TypeScript)
// ═══════════════════════════════════════════════════════════════════

export {
  tokens,
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
} from './tokens';

export type {
  SpacingToken,
  Tokens,
} from './tokens';

// ═══════════════════════════════════════════════════════════════════
// Components (Bezel + Bento + Compact CRUD)
// ═══════════════════════════════════════════════════════════════════

export {
  // Bezel components
  BezelCard,
  BezelWidget,
  // Bento components
  BentoGrid,
  BentoItem,
  BentoSection,
  // Compact CRUD components
  CompactInput,
  CompactButton,
  CompactRow,
  CompactModal,
  CompactGrid,
  CompactBadge,
  CompactLabel,
} from './components';

export type {
  // Bezel component props
  BezelCardProps,
  BezelWidgetProps,
  // Bento component props
  BentoGridProps,
  BentoItemProps,
  BentoSectionProps,
  // Compact CRUD component props
  CompactInputProps,
  CompactButtonProps,
  CompactRowProps,
  CompactModalProps,
  CompactGridProps,
  CompactBadgeProps,
  CompactLabelProps,
} from './components';

// ═══════════════════════════════════════════════════════════════════
// Hooks
// ═══════════════════════════════════════════════════════════════════

export {
  useScrollReveal,
  initScrollReveal,
} from './hooks';

// ═══════════════════════════════════════════════════════════════════
// CSS (import as side effect)
// ═══════════════════════════════════════════════════════════════════

// Import CSS files
import './css/variables.css';
import './css/animations.css';
import './css/bezel.css';
import './css/motion.css';

// ═══════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════

/**
 * Merge class names (simple implementation).
 * For production, use clsx or tailwind-merge.
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Get a CSS variable value with fallback.
 */
export function cssVar(name: string, fallback?: string): string {
  return `var(--${name}${fallback ? `, ${fallback}` : ''})`;
}

/**
 * Generate stagger delay class name.
 */
export function staggerDelay(index: number): string {
  const delays = [0, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400];
  const delay = delays[Math.min(index, delays.length - 1)];
  return `animation-delay: ${delay}ms`;
}

/**
 * Generate stagger delay CSS variable.
 */
export function staggerDelayVar(index: number, base: number = 75): string {
  return `${index * base}ms`;
}
