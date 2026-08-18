/// <reference types="astro/client" />

// Allow client:* directives on all HTML elements (used by @astrojs/alpinejs islands).
declare namespace astroHTML.JSX {
  interface IntrinsicAttributes {
    'client:load'?: boolean | string;
    'client:idle'?: boolean | string;
    'client:visible'?: boolean | string;
    'client:media'?: string;
    'client:only'?: boolean | string;
  }
}

interface ToastStore {
  visible: boolean;
  message: string;
  variant: 'success' | 'error' | 'info' | 'warning';
  show?: (message: string, variant?: 'success' | 'error' | 'info' | 'warning', duration?: number) => void;
}

declare global {
  interface Window {
    htmx?: unknown;
    /** Redux store instance (configureStore result) */
    __reduxStore?: {
      getState: () => { toast: ToastStore; site: { theme: string; loaded: boolean } };
      dispatch: (action: unknown) => void;
      subscribe: (listener: () => void) => () => void;
    };
    /** Redux-powered toast helper */
    __showToast?: (message: string, variant?: 'success' | 'error' | 'info' | 'warning') => void;
    Alpine?: {
      store(name: string, value?: unknown): unknown;
      store(name: 'toast'): ToastStore;
    } & Record<string, unknown>;
    gtag?: (...args: unknown[]) => void;
    /** Bundled language catalog injected by the LanguageSwitcher (fallback). */
    __FUSION_LANGS?: { code: string; native: string; flag: string; dir: 'ltr' | 'rtl' }[];
    __FUSION_DEFAULT_LANG?: string;
    /** Backend base URL (from lib/api.ts) used by the switcher hydration fetch. */
    __FUSION_API_BASE?: string;
  }
}

export {};
