/**
 * Centralized Icon System
 * =======================
 * Multi-set icon lookup with fallback priority and disambiguation support.
 *
 * Supported 8 icon sets:
 *   ── 7 Iconify CSS-based sets (tree-shaken at build time) ──
 *   tabler:    Tabler Icons (default) — icon-[tabler--search]
 *   lucide:    Lucide Icons            — icon-[lucide--search]
 *   mdi:       Material Design Icons   — icon-[mdi--magnify]
 *   ph:        Phosphor Icons          — icon-[ph--magnifying-glass]
 *   heroicons: Heroicons (Iconify)     — icon-[heroicons--magnifying-glass]
 *   carbon:    Carbon Icons            — icon-[carbon--search]
 *   solar:     Solar Icons             — icon-[solar--calendar-search-linear]
 *   ── 1 React component-based set ──
 *   hi:        Heroicons v2 Solid (react-icons/hi2) — <HiShoppingCart />
 *
 * Usage:
 *   import { ic, Ic, iconClass, getAllIconClasses } from '../lib/icons';
 *
 *   // Iconify CSS-based sets:
 *   iconClass('lucide:alert-circle')           // icon-[lucide--alert-circle]
 *   const Search = ic('tabler:search');
 *
 *   // react-icons/hi2 React component:
 *   const CartIcon = Ic('hi:shopping-cart');    // renders <HiShoppingCart />
 *
 *   // Plain names auto-resolve to best Iconify set:
 *   iconClass('trash')                          // icon-[lucide--trash]
 *   iconClass('chef-hat')                       // icon-[tabler--chef-hat]
 *
 *   // Get all possible icon classes for a name (for disambiguation UI):
 *   getAllIconClasses('search')
 *   // ["icon-[tabler--search]", "icon-[lucide--search]", ...]
 *
 *   // Legacy — same as old Ic():
 *   tabs = [{ icon: Ic('globe'), ... }]
 */

import type React from 'react';

// ── Lazy-loaded react-icons/hi2 module (loaded once on first use) ──
let _hi2: Record<string, React.ComponentType<{ className?: string }>> | null = null;
function getHi2() {
  if (!_hi2) {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    _hi2 = require('react-icons/hi2');
  }
  return _hi2;
}

/** Common HI icon name overrides — Tabler names that differ in Heroicons v2 */
const HI_NAME_MAP: Record<string, string> = {
  'x': 'HiXMark',
  'x-mark': 'HiXMark',
  'alert-triangle': 'HiExclamationTriangle',
  'warning': 'HiExclamationTriangle',
  'info': 'HiInformationCircle',
  'info-circle': 'HiInformationCircle',
  'help': 'HiQuestionMarkCircle',
  'help-circle': 'HiQuestionMarkCircle',
  'circle-x': 'HiXCircle',
  'arrow-back': 'HiArrowLeft',
  'arrow-up': 'HiArrowUp',
  'arrow-down': 'HiArrowDown',
  'arrow-right': 'HiArrowRight',
  'arrow-left': 'HiArrowLeft',
  'chevron-up': 'HiChevronUp',
  'chevron-down': 'HiChevronDown',
  'chevron-right': 'HiChevronRight',
  'chevron-left': 'HiChevronLeft',
  'menu': 'HiBars3',
  'dots': 'HiEllipsisHorizontal',
  'dots-vertical': 'HiEllipsisVertical',
};

/** Available icon sets with their CSS class prefixes */
export const ICON_SETS = {
  tabler:    'icon-[tabler--',
  lucide:    'icon-[lucide--',
  mdi:       'icon-[mdi--',
  ph:        'icon-[ph--',
  heroicons: 'icon-[heroicons--',
  carbon:    'icon-[carbon--',
  solar:     'icon-[solar--',
} as const;

export type IconSet = keyof typeof ICON_SETS;

/** Default icon set when no prefix is specified */
const DEFAULT_SET: IconSet = 'tabler';

/** Fallback priority order — when preferred set isn't a match, try these */
const FALLBACK_ORDER: IconSet[] = ['lucide', 'ph', 'mdi', 'heroicons', 'carbon', 'solar'];

/** All icon sets in discovery order (used by getAllIconClasses) */
export const ALL_SETS: IconSet[] = ['tabler', ...FALLBACK_ORDER];

/**
 * Known ambiguous names — icons that exist in multiple sets.
 * Specifies which set to prefer when the developer doesn't specify.
 */
const AMBIGUOUS_NAMES: Record<string, IconSet> = {
  'search': 'tabler',        'check': 'tabler',
  'x': 'tabler',             'heart': 'tabler',
  'star': 'tabler',          'alert-circle': 'tabler',
  'info': 'tabler',          'arrow-left': 'tabler',
  'arrow-right': 'tabler',   'chevron-down': 'tabler',
  'chevron-left': 'tabler',  'chevron-right': 'tabler',
  'plus': 'tabler',          'minus': 'tabler',
  'trash': 'lucide',         // Lucide's trash is more polished
  'edit': 'tabler',          'settings': 'tabler',
  'user': 'tabler',          'mail': 'tabler',
  'clock': 'tabler',         'calendar': 'tabler',
  'map-pin': 'tabler',       'phone': 'tabler',
  'download': 'tabler',      'upload': 'tabler',
  'external-link': 'tabler',
};

// ── Core Helpers ──────────────────────────────────────────────────────────

/** Build the raw icon CSS class prefix for a given set */
function setPrefix(set: IconSet): string {
  return ICON_SETS[set];
}

/**
 * Resolve the best icon set for a plain name (no prefix).
 * Uses AMBIGUOUS_NAMES table, then falls back to DEFAULT_SET.
 */
function resolveBestSet(name: string): IconSet {
  if (AMBIGUOUS_NAMES[name]) return AMBIGUOUS_NAMES[name];
  return DEFAULT_SET;
}

/** Parse "set:name" or "name" into { set, name } */
function parseIcon(fullName: string): { set: IconSet | 'hi'; name: string } {
  const colonIdx = fullName.indexOf(':');
  if (colonIdx > 0) {
    const prefix = fullName.slice(0, colonIdx);
    if (prefix === 'hi') {
      return { set: 'hi', name: fullName.slice(colonIdx + 1) };
    }
    if (prefix in ICON_SETS) {
      return { set: prefix as IconSet, name: fullName.slice(colonIdx + 1) };
    }
  }
  return { set: DEFAULT_SET, name: fullName };
}

/**
 * Convert kebab-case icon name to Heroicons PascalCase component name.
 * e.g. 'shopping-cart' → 'HiShoppingCart', 'x-mark' → 'HiXMark'
 */
function toHiComponentName(name: string): string {
  const pascal = name
    .split('-')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join('');
  return `Hi${pascal}`;
}

// ── Public API ────────────────────────────────────────────────────────────

/**
 * Build a CSS class string for an Iconify icon.
 * Supports explicit set prefixes ("lucide:search"), plain names ("heart"),
 * and the "hi:" prefix for react-icons/hi2.
 *
 * **Note:** When using "hi:name", this returns a descriptive class string
 * but the icon is rendered as a React component. Use `ic()`/`Ic()` instead
 * for HI icons.
 *
 * @example
 *   iconClass('lucide:alert-circle')             → "icon-[lucide--alert-circle]"
 *   iconClass('heart', 'w-5 h-5 text-error')     → "icon-[tabler--heart] w-5 h-5 text-error"
 */
export function iconClass(fullName: string, extraClasses: string = ''): string {
  const { set, name } = parseIcon(fullName);
  if (set === 'hi') return ''; // HI icons are React components, no CSS class
  const resolvedSet = fullName.includes(':') ? set : resolveBestSet(name);
  const base = `${setPrefix(resolvedSet)}${name}]`;
  return extraClasses ? `${base} ${extraClasses}` : base;
}

/**
 * Get ALL possible icon class strings for a given icon name across all 7 Iconify sets.
 * Useful for building disambiguation UIs (e.g., icon picker).
 *
 * @example
 *   getAllIconClasses('search')
 *   → ["icon-[tabler--search]", "icon-[lucide--search]", ...]
 */
export function getAllIconClasses(name: string): string[] {
  const cleanName = name.includes(':') ? name.split(':')[1] : name;
  if (name.startsWith('hi:')) return []; // HI icons are components, not classes
  const seen = new Set<string>();
  const results: string[] = [];

  // Always include the best match first
  const best = iconClass(cleanName);
  seen.add(best);
  results.push(best);

  // Then add all other sets
  for (const set of ALL_SETS.slice(1)) {
    const cls = `${setPrefix(set)}${cleanName}]`;
    if (!seen.has(cls)) {
      seen.add(cls);
      results.push(cls);
    }
  }
  return results;
}

/**
 * Create a React component that renders an icon.
 *
 * For Iconify sets (tabler, lucide, mdi, ph, heroicons, carbon, solar),
 * renders a <span> with the appropriate icon-[tabler--star] CSS class.
 *
 * For the "hi:" prefix, renders a Heroicons v2 Solid React component
 * from `react-icons/hi2`.
 *
 * @example
 *   const Heart = ic('tabler:heart');
 *   <Heart className="w-5 h-5 text-error" />
 *
 *   const CartIcon = ic('hi:shopping-cart');
 *   <CartIcon className="w-5 h-5 text-primary" />
 */
export function ic(fullName: string): React.ComponentType<{ className?: string }> {
  const { set, name } = parseIcon(fullName);

  // ── HI: Heroicons v2 Solid React component ──
  if (set === 'hi') {
    const componentName = HI_NAME_MAP[name] || toHiComponentName(name);
    return ({ className = '' }) => {
      try {
        const hi2 = getHi2();
        if (!hi2) {
          console.warn('[icons] react-icons/hi2 module not loaded');
          return <span className={`icon-[tabler--question-mark] ${className}`} />;
        }
        const HiIcon = hi2[componentName];
        if (HiIcon) {
          return <HiIcon className={className} />;
        }
        console.warn(`[icons] HI icon "${componentName}" not found in react-icons/hi2 for name "${name}"`);
        return <span className={`icon-[tabler--question-mark] ${className}`} />;
      } catch {
        console.warn('[icons] Failed to load react-icons/hi2');
        return <span className={`icon-[tabler--question-mark] ${className}`} />;
      }
    };
  }

  // ── Iconify CSS-based icon ──
  const resolvedSet = fullName.includes(':') ? set : resolveBestSet(name);
  const base = `${setPrefix(resolvedSet)}${name}]`;

  return ({ className = '' }) => (
    <span className={className ? `${base} ${className}` : base} />
  );
}

/**
 * Legacy-compatible Ic() helper.
 * Behaves identically to the old `function Ic(name: string)` but supports
 * multi-set prefixes, auto-resolution via AMBIGUOUS_NAMES, and the "hi:" prefix
 * for react-icons/hi2 Heroicons.
 *
 * @example
 *   Ic('globe')              → icon-[tabler--globe] (tabler default)
 *   Ic('lucide:search')      → icon-[lucide--search] (explicit set)
 *   Ic('hi:shopping-cart')   → <HiShoppingCart /> (react-icons/hi2)
 */
export function Ic(name: string): React.ComponentType<{ className?: string }> {
  return ic(name);
}
