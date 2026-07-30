/**
 * Centralized Iconify Icon System
 * ===============================
 * Multi-set icon lookup with fallback priority and disambiguation support.
 *
 * Supported 7 icon sets (tree-shaken at build time):
 *   tabler:    Tabler Icons (default) — icon-[tabler--{name}]
 *   lucide:    Lucide Icons            — icon-[lucide--{name}]
 *   mdi:       Material Design Icons   — icon-[mdi--{name}]
 *   ph:        Phosphor Icons          — icon-[ph--{name}]
 *   heroicons: Heroicons               — icon-[heroicons--{name}]
 *   carbon:    Carbon Icons            — icon-[carbon--{name}]
 *   solar:     Solar Icons             — icon-[solar--{name}]
 *
 * Usage:
 *   import { ic, Ic, iconClass, iconClassSafe, getAllIconClasses } from '../lib/icons';
 *
 *   // Explicit set prefix (recommended for production):
 *   iconClass('lucide:alert-circle')           // icon-[lucide--alert-circle]
 *   const Search = ic('tabler:search');
 *
 *   // Auto-discover — finds the best icon set for a name:
 *   iconClassSafe('trash')                     // icon-[lucide--trash] (AMBIGUOUS_NAMES prefers lucide)
 *   iconClassSafe('chef-hat')                  // icon-[tabler--chef-hat] (only in tabler)
 *
 *   // Get all possible icon classes for a name (for disambiguation UI):
 *   getAllIconClasses('search')
 *   // ["icon-[tabler--search]", "icon-[lucide--search]", "icon-[ph--search]", "icon-[mdi--search]"]
 *
 *   // Legacy — same as old Ic():
 *   tabs = [{ icon: Ic('globe'), ... }]
 */

import type React from 'react';

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

/** Parse "set:name" or "name" into { set, name } */
function parseIcon(fullName: string): { set: IconSet; name: string } {
  const colonIdx = fullName.indexOf(':');
  if (colonIdx > 0) {
    const prefix = fullName.slice(0, colonIdx) as IconSet;
    if (prefix in ICON_SETS) {
      return { set: prefix, name: fullName.slice(colonIdx + 1) };
    }
  }
  return { set: DEFAULT_SET, name: fullName };
}

/**
 * Resolve the best icon set for a plain name (no prefix).
 * Uses AMBIGUOUS_NAMES table, then falls back to DEFAULT_SET.
 */
function resolveBestSet(name: string): IconSet {
  if (AMBIGUOUS_NAMES[name]) return AMBIGUOUS_NAMES[name];
  return DEFAULT_SET;
}

// ── Public API ────────────────────────────────────────────────────────────

/**
 * Build a CSS class string for an Iconify icon.
 * Supports both explicit set prefixes ("lucide:search") and plain names ("heart").
 * Plain names are resolved via AMBIGUOUS_NAMES → tabler default.
 *
 * @example
 *   iconClass('lucide:alert-circle')             → "icon-[lucide--alert-circle]"
 *   iconClass('heart', 'w-5 h-5 text-error')     → "icon-[tabler--heart] w-5 h-5 text-error"
 */
export function iconClass(fullName: string, extraClasses: string = ''): string {
  const { set, name } = parseIcon(fullName);
  const resolvedSet = fullName.includes(':') ? set : resolveBestSet(name);
  const base = `${setPrefix(resolvedSet)}${name}]`;
  return extraClasses ? `${base} ${extraClasses}` : base;
}

/**
 * Get ALL possible icon class strings for a given icon name across all 7 sets.
 * Useful for building disambiguation UIs (e.g., icon picker).
 *
 * @example
 *   getAllIconClasses('search')
 *   → ["icon-[tabler--search]", "icon-[lucide--search]", "icon-[ph--search]", ...]
 */
export function getAllIconClasses(name: string): string[] {
  const cleanName = name.includes(':') ? name.split(':')[1] : name;
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
 * Create a React component that renders an Iconify icon.
 *
 * @example
 *   const Heart = ic('tabler:heart');
 *   <Heart className="w-5 h-5 text-error" />
 */
export function ic(fullName: string): React.ComponentType<{ className?: string }> {
  const { set, name } = parseIcon(fullName);
  const resolvedSet = fullName.includes(':') ? set : resolveBestSet(name);
  const base = `${setPrefix(resolvedSet)}${name}]`;

  return ({ className = '' }) => (
    <span className={className ? `${base} ${className}` : base} />
  );
}

/**
 * Legacy-compatible Ic() helper.
 * Behaves identically to the old `function Ic(name: string)` but supports
 * multi-set prefixes and auto-resolution via AMBIGUOUS_NAMES.
 *
 * @example
 *   Ic('globe')           → icon-[tabler--globe] (tabler default)
 *   Ic('lucide:search')   → icon-[lucide--search] (explicit set)
 */
export function Ic(name: string): React.ComponentType<{ className?: string }> {
  return ic(name);
}
