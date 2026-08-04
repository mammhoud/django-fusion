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
    Alpine?: {
      store(name: string, value?: unknown): unknown;
      store(name: 'toast'): ToastStore;
    } & Record<string, unknown>;
    gtag?: (...args: unknown[]) => void;
  }
}

export {};
