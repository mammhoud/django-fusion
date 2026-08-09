/**
 * Theme manager — framework-agnostic.
 *
 * FOUC-safe theme bootstrap + toggle + cross-tab sync. Replicates the
 * behaviour of the fusion head script + ThemeToggle component as a
 * reusable module for any TS framework (React/Vue/Svelte/Astro).
 *
 * ```ts
 * import { createTheme } from 'fusion-js/modules/theme';
 *
 * const theme = createTheme({ storageKey: 'fu:theme', root: document.documentElement });
 * theme.apply();           // resolve stored/prefers-color-scheme → class
 * theme.toggle();          // flip and persist
 * const isDark = theme.matches('dark');
 * ```
 */

export interface ThemeOptions {
  /** localStorage key. Default: 'fu:theme'. */
  storageKey?: string;
  /** Element that gets the theme class. Default: document.documentElement. */
  root?: HTMLElement;
  /** Class names for dark/light. Default: 'dark' / 'light'. */
  darkClass?: string;
  lightClass?: string;
  /** theme-color meta selector. Default: 'meta[name="theme-color"]'. */
  metaSelector?: string;
  /** Colors written to theme-color meta for dark/light. */
  darkMetaColor?: string;
  lightMetaColor?: string;
}

export type ThemeName = 'dark' | 'light';

export interface ThemeManager {
  /** Current resolved theme. */
  readonly current: ThemeName;
  /** Apply the stored (or system) theme to the root element — FOUC-safe. */
  apply: () => ThemeName;
  /** Toggle dark/light, persist to localStorage, update meta. Returns new theme. */
  toggle: () => ThemeName;
  /** Set a specific theme and persist it. */
  set: (theme: ThemeName) => ThemeName;
  /** Whether the manager currently resolves to the given theme. */
  matches: (theme: ThemeName) => boolean;
  /** Subscribe to theme changes: `(theme) => void`. Returns an unsubscribe fn. */
  subscribe: (listener: (theme: ThemeName) => void) => () => void;
}

const readStored = (key: string): ThemeName | null => {
  try {
    const value = localStorage.getItem(key);
    return value === 'dark' || value === 'light' ? value : null;
  } catch {
    return null;
  }
};

const systemPrefersDark = (): boolean =>
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-color-scheme: dark)').matches;

/**
 * Create a theme manager bound to a root element. `apply()` is safe to
 * call in a head script; `toggle()`/`set()` persist the choice.
 */
export function createTheme(options: ThemeOptions = {}): ThemeManager {
  const storageKey = options.storageKey ?? 'fu:theme';
  const root = options.root ?? document.documentElement;
  const darkClass = options.darkClass ?? 'dark';
  const lightClass = options.lightClass ?? 'light';
  const metaSelector = options.metaSelector ?? 'meta[name="theme-color"]';
  const darkMetaColor = options.darkMetaColor ?? '#131312';
  const lightMetaColor = options.lightMetaColor ?? '#fcfcfa';

  let current: ThemeName = readStored(storageKey) ?? (systemPrefersDark() ? 'dark' : 'light');
  const listeners = new Set<(theme: ThemeName) => void>();

  const paint = (theme: ThemeName): void => {
    root.classList.remove(darkClass, lightClass);
    root.classList.add(theme === 'dark' ? darkClass : lightClass);
    const meta = document.querySelector<HTMLMetaElement>(metaSelector);
    meta?.setAttribute('content', theme === 'dark' ? darkMetaColor : lightMetaColor);
    current = theme;
    for (const listener of listeners) listener(theme);
  };

  const apply = (): ThemeName => {
    current = readStored(storageKey) ?? (systemPrefersDark() ? 'dark' : 'light');
    paint(current);
    return current;
  };

  const set = (theme: ThemeName): ThemeName => {
    current = theme;
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      /* storage unavailable (private mode) — theme still applies */
    }
    paint(theme);
    return theme;
  };

  const toggle = (): ThemeName => set(current === 'dark' ? 'light' : 'dark');

  // Cross-tab sync.
  window.addEventListener('storage', (event) => {
    if (event.key === storageKey) {
      const next = event.newValue === 'dark' ? 'dark' : 'light';
      paint(next);
    }
  });

  return {
    get current() {
      return current;
    },
    apply,
    toggle,
    set,
    matches: (theme: ThemeName) => current === theme,
    subscribe: (listener: (theme: ThemeName) => void) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

export default { createTheme };
