/**
 * Centralized Icon System — Remix Icons
 * =====================================
 * Single icon set: **Remix Icon** (font-based, loaded from
 * `@formints-assets/styles/fonts/remixicon.css` with font files in
 * `@formints-assets/icons/remix/`). All helpers normalize the legacy multi-set
 * vocabulary (tabler/lucide/mdi/ph/heroicons/carbon/solar + `hi:` Heroicons)
 * into the equivalent `ri-*` class.
 *
 * Usage:
 *   import { ic, Ic, iconClass } from '../lib/icons';
 *
 *   // Class string (remix):
 *   iconClass('search')               // "ri-search-line"
 *   iconClass('tabler:trash')         // "ri-delete-bin-line"
 *   iconClass('hi:home')              // "ri-home-line"
 *   iconClass('x', 'w-4 h-4')         // "ri-close-line w-4 h-4"
 *
 *   // React component (renders <span className="ri-...-line" />):
 *   const Cart = Ic('hi:shopping-cart');
 *   const Search = ic('lucide:search');
 *   <Cart className="w-5 h-5 text-primary" />
 */

import type React from 'react';

/**
 * Map legacy icon vocabulary → Remix Icon base name.
 * Keys are the plain icon name (without set prefix); values are the remix
 * base name that gets the `-line` suffix (e.g. `search` → `ri-search-line`).
 */
const REMIX_MAP: Record<string, string> = {
  // ── generic / ui ──
  'search': 'search', 'x': 'close', 'close': 'close', 'plus': 'add', 'minus': 'subtract',
  'check': 'check', 'check-circle': 'checkbox-circle', 'circle-check': 'checkbox-circle',
  'alert-triangle': 'alert', 'alert-circle': 'alert', 'exclamation-triangle': 'alert',
  'warning': 'alert', 'info': 'information', 'info-circle': 'information',
  'help': 'question', 'help-circle': 'question', 'question-mark': 'question',
  'x-mark': 'close', 'check-badge': 'checkbox-circle',
  'arrow-left': 'arrow-left', 'arrow-right': 'arrow-right', 'arrow-up': 'arrow-up',
  'arrow-down': 'arrow-down', 'arrow-narrow-left': 'arrow-left', 'arrow-back': 'arrow-left',
  'chevron-up': 'arrow-up-s', 'chevron-down': 'arrow-down-s', 'chevron-left': 'arrow-left-s',
  'chevron-right': 'arrow-right-s', 'menu': 'menu-2', 'menu-2': 'menu-2', 'menu-4': 'menu-4',
  'dots': 'more-2', 'dots-vertical': 'more', 'loader': 'loader-4', 'loader-2': 'loader-4',
  'spinner': 'loader-4', 'settings': 'settings-3', 'cog-6-tooth': 'settings-3', 'edit': 'edit',
  'pencil': 'pencil', 'trash': 'delete-bin', 'copy': 'file-copy', 'filter': 'filter-2',
  'history': 'history', 'refresh': 'refresh', 'rotate-clockwise': 'refresh',
  'download': 'download', 'upload': 'upload-2', 'send': 'send-plane', 'external-link': 'external-link',
  'globe': 'global', 'link': 'link', 'key': 'key', 'lock': 'lock-2', 'eye': 'eye',
  'eye-slash': 'eye-off', 'calendar': 'calendar', 'calendar-days': 'calendar',
  'calendar-week': 'calendar-2', 'calendar-month': 'calendar-2', 'calendar-clock': 'calendar-2',
  'clock': 'time', 'star': 'star', 'heart': 'heart', 'fire': 'fire', 'bulb': 'lightbulb-flash',
  'tag': 'price-tag', 'pin': 'pushpin-2', 'map-pin': 'map-pin-2', 'map-pin-2': 'map-pin-2',
  'map-pin-code': 'map-pin-2', 'map-off': 'map-2', 'phone': 'phone', 'mail': 'mail',
  'paperclip': 'attachment', 'message': 'chat-1', 'messages': 'chat-3',
  'chat-bubble-left-right': 'chat-3', 'headset': 'customer-service', 'inbox': 'inbox',
  'bell': 'notification-3', 'printer': 'printer', 'image': 'image', 'photo': 'image',
  'folder': 'folder', 'file': 'file', 'file-text': 'file-text', 'document-text': 'file-text',
  'file-invoice': 'file-list-3', 'file-download': 'download-2', 'file-import': 'file-transfer',
  'file-export': 'file-transfer', 'file-type-pdf': 'file-pdf', 'template': 'layout-top',
  'note': 'sticky-note', 'note-off': 'sticky-note', 'notes': 'sticky-note-2',
  'clipboard-list': 'clipboard', 'clipboard-document-list': 'clipboard', 'list': 'list-unordered',
  'list-check': 'check-double', 'language': 'translate', 'calculator': 'calculator',
  'moneybag': 'money-dollar-box', 'cash': 'money-dollar-circle', 'currency-dollar': 'money-dollar-circle',
  'coin': 'coins', 'banknotes': 'bank-card', 'receipt': 'receipt', 'receipt-percent': 'percent',
  'credit-card': 'bank-card',  'trending-up': 'stock', 'chart-bar': 'bar-chart-2',
  'document-chart-bar': 'file-chart',
  'chart-line': 'line-chart', 'chart-pie': 'pie-chart', 'bar-chart': 'bar-chart-2',
  'dashboard': 'dashboard-2', 'layout-grid': 'layout-grid', 'grid-dots': 'layout-grid',
  'apps': 'layout-grid', 'squares-2x2': 'layout-grid', 'table-cells': 'table', 'tables': 'table',
  'adjustments': 'equalizer', 'tune': 'equalizer', 'code': 'code-s-slash', 'database': 'database-2',
  'database-off': 'database-2', 'device-desktop': 'computer', 'device-floppy': 'save-3',
  'flask': 'flask', 'beaker': 'flask', 'color-picker': 'dropper', 'paint': 'paint-brush',
  'palette': 'palette', 'sun': 'sun', 'moon': 'moon', 'flower': 'flower', 'sparkles': 'star-smile',
  'crown': 'vip-crown-2', 'star-smile': 'star-smile', 'shield': 'shield', 'shield-off': 'shield',
  'shield-check': 'shield-check', 'user': 'user', 'users': 'group', 'user-group': 'group',
  'user-circle': 'user-3', 'user-3': 'user-3', 'user-check': 'user-follow',
  'briefcase': 'briefcase-4', 'building': 'building-2', 'building-bank': 'bank',
  'building-store': 'store-2', 'store': 'store-2', 'truck': 'truck', 'package': 'archive',
  'packages': 'box-2', 'cube': 'box-3', 'box': 'box-2', 'shopping-cart': 'shopping-cart',
  'cart': 'shopping-cart', 'home': 'home', 'logout': 'logout-box-r', 'login': 'login-box',
  'arrow-right-start-on-rectangle': 'logout-box-r', 'door-enter': 'login-box',
  'chef-hat': 'restaurant-2', 'tools': 'tools', 'tools-kitchen-2': 'restaurant-2',
  'utensils': 'restaurant', 'cup': 'cup', 'barcode': 'barcode', 'align-left': 'align-left',
  'checkbox': 'checkbox', 'click': 'cursor', 'clock-play': 'play-circle',
  'clock-exclamation': 'alarm-warning', 'hand-three-fingers': 'hand',
  'magnifying-glass': 'zoom-in', 'magnify': 'zoom-in', 'calendar-search-linear': 'calendar-2',
  'flag': 'flag-2', 'book-open': 'book-open', 'chart': 'line-chart',
};

/**
 * Available icon set aliases (all normalize to Remix). Kept for
 * backward-compatible `set:name` strings.
 */
export const ICON_SETS = {
  remix: 'ri-',
  tabler: 'ri-',
  lucide: 'ri-',
  mdi: 'ri-',
  ph: 'ri-',
  heroicons: 'ri-',
  carbon: 'ri-',
  solar: 'ri-',
} as const;

export type IconSet = keyof typeof ICON_SETS;

/** Default icon set (always remix). */
const DEFAULT_SET: IconSet = 'remix';

/** All icon sets in discovery order. */
export const ALL_SETS: IconSet[] = ['remix'];

/** Resolve a legacy name → remix base name; unknown → 'question' fallback. */
function remixBase(name: string): string {
  const clean = name.includes(':') ? name.split(':').slice(1).join(':') : name;
  return REMIX_MAP[clean] || clean;
}

/** Parse "set:name" or "name" → remix base name. */
function parseIcon(fullName: string): { set: IconSet; name: string } {
  const colonIdx = fullName.indexOf(':');
  if (colonIdx > 0) {
    const prefix = fullName.slice(0, colonIdx);
    if (prefix in ICON_SETS) {
      return { set: prefix as IconSet, name: fullName.slice(colonIdx + 1) };
    }
  }
  return { set: DEFAULT_SET, name: fullName };
}

/**
 * Build the remix CSS class for an icon.
 * Accepts "set:name" (tabler/lucide/hi/… all normalize to remix) or a plain
 * name. Always returns `ri-<base>-line`.
 *
 * @example
 *   iconClass('search')                 → "ri-search-line"
 *   iconClass('tabler:trash')           → "ri-delete-bin-line"
 *   iconClass('hi:shopping-cart')       → "ri-shopping-cart-line"
 *   iconClass('x', 'w-4 h-4 text-error')→ "ri-close-line w-4 h-4 text-error"
 */
export function iconClass(fullName: string, extraClasses: string = ''): string {
  const { name } = parseIcon(fullName);
  const base = `ri-${remixBase(name)}-line`;
  return extraClasses ? `${base} ${extraClasses}` : base;
}

/**
 * Get ALL possible icon class strings for a given icon name (remix only).
 * Kept for API compatibility with the old multi-set picker.
 */
export function getAllIconClasses(name: string): string[] {
  return [iconClass(name)];
}

/**
 * Create a React component that renders a remix icon.
 *
 * @example
 *   const Heart = ic('heart');
 *   <Heart className="w-5 h-5 text-error" />
 *
 *   const CartIcon = Ic('hi:shopping-cart');
 *   <CartIcon className="w-5 h-5 text-primary" />
 */
export function ic(fullName: string): React.ComponentType<{ className?: string }> {
  const cls = iconClass(fullName);
  return ({ className = '' }) => <span className={className ? `${cls} ${className}` : cls} />;
}

/** Legacy-compatible Ic() helper — identical to ic(). */
export function Ic(name: string): React.ComponentType<{ className?: string }> {
  return ic(name);
}
