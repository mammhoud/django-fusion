/// <reference types="astro/client" />

interface ToastStore {
  visible: boolean;
  message: string;
  variant: 'success' | 'error' | 'info' | 'warning';
  show?: (message: string, variant?: 'success' | 'error' | 'info' | 'warning', duration?: number) => void;
}

declare global {
  interface ImportMetaEnv {
    readonly PUBLIC_FUSION_API_URL?: string;
    readonly PUBLIC_BUILD_API_URL?: string;
  }

  interface Window {
    htmx?: unknown;
    /** Redux store instance (configureStore result). */
    __reduxStore?: {
      getState: () => { toast: ToastStore; site: { theme: string; loaded: boolean } };
      dispatch: (action: unknown) => void;
      subscribe: (listener: () => void) => () => void;
    };
    /** Redux-powered toast helper. */
    __showToast?: (message: string, variant?: 'success' | 'error' | 'info' | 'warning') => void;
    Alpine?: {
      store(name: string, value?: unknown): unknown;
      store(name: 'toast'): ToastStore;
    } & Record<string, unknown>;
    gtag?: (...args: unknown[]) => void;
    /** Headless allauth login/session endpoints injected by LoginModal. */
    __FUSION_AUTH?: {
      login: string;
      session: string;
      csrf: string;
      ensureCsrfToken: () => Promise<string>;
      apiBase: string;
      providers: { id: string; label: string; icon: string }[];
    };
  }
}

export {};
