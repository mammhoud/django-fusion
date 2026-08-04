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
  variant: 'success' | 'error' | 'info';
  show(message: string, variant?: 'success' | 'error' | 'info', duration?: number): void;
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
  }
}

export {};
