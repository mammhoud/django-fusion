/// <reference types="astro/client" />

interface ToastStore {
  visible: boolean;
  message: string;
  variant: 'success' | 'error' | 'info';
  show(message: string, variant?: 'success' | 'error' | 'info', duration?: number): void;
}

declare global {
  interface Window {
    Alpine?: {
      store(name: string, value?: unknown): unknown;
      store(name: 'toast'): ToastStore;
    } & Record<string, unknown>;
    gtag?: (...args: unknown[]) => void;
  }
}

export {};
