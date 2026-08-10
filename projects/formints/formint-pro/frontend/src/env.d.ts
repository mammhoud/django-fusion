/// <reference types="astro/client" />

// ── Alpine.js global types ──
declare global {
  interface Window {
    Alpine: typeof import('alpinejs').default;
    htmx?: {
      process: (element: Element) => void;
    };
  }

  // Alpine.js $store type (loose — typed stores come from alpine-stores.ts)
  interface AlpineStore {
    kds: {
      filter: string;
      sortOrder: string;
      mutedUntil: number | null;
      chimeVariant: string;
      preferredPriorities: number[];
      selectedCategory: string | number;
      isMuted: boolean;
      muteRemaining: string | null;
      init(): void;
      persist(): void;
      toggleMute(minutes?: number): void;
    };
    ui: {
      theme: string;
      mode: string;
      sidebarOpen: boolean;
      rtl: boolean;
      toasts: { id: number; message: string; type: string }[];
      init(): void;
      toggleDark(): void;
      toggleRTL(): void;
      toast(message: string, type?: string, duration?: number): void;
    };
    cart: {
      items: { id: number; name: string; price: number; qty: number; modifiers?: string[] }[];
      customerId: number | null;
      customerName: string;
      notes: string;
      discount: number;
      subtotal: number;
      tax: number;
      total: number;
      isEmpty: boolean;
      itemCount: number;
      init(): void;
      add(product: { id: number; name: string; price: number }): void;
      remove(productId: number): void;
      updateQty(productId: number, qty: number): void;
      recalc(): void;
      clear(): void;
    };
  }

  // Augment HTMX attributes on HTML elements
  namespace JSX {
    interface IntrinsicAttributes {
      'x-data'?: string;
      'x-init'?: string;
      'x-show'?: string;
      'x-text'?: string;
      'x-model'?: string;
      'x-bind'?: string;
      'x-on:click'?: string;
      'x-on:click.self'?: string;
      'x-on:keydown.escape.window'?: string;
      'x-transition:enter'?: string;
      'x-transition:enter-start'?: string;
      'x-transition:enter-end'?: string;
      'x-transition:leave'?: string;
      'x-transition:leave-start'?: string;
      'x-transition:leave-end'?: string;
      'x-transition.opacity'?: string;
      'x-for'?: string;
      'x-if'?: string;
      'x-html'?: string;
      'x-effect'?: string;
      'x-ref'?: string;
      'x-cloak'?: string;
      'x-teleport'?: string;
      ':key'?: string;
      ':class'?: string;
      ':style'?: string;
      ':id'?: string;
      ':aria-label'?: string;
      ':title'?: string;
      '@click'?: string;
      '@click.self'?: string;
      '@keydown.escape.window'?: string;
      // HTMX attributes
      'hx-get'?: string;
      'hx-post'?: string;
      'hx-put'?: string;
      'hx-patch'?: string;
      'hx-delete'?: string;
      'hx-target'?: string;
      'hx-swap'?: string;
      'hx-trigger'?: string;
      'hx-headers'?: string;
      'hx-indicator'?: string;
      'hx-confirm'?: string;
      'hx-select'?: string;
      'hx-push-url'?: string;
      'hx-replace-url'?: string;
      'hx-vals'?: string;
      'hx-sync'?: string;
      'hx-boost'?: string | boolean;
      'hx-ext'?: string;
      'hx-params'?: string;
      // Alpine $store references in html
      '$store'?: unknown;
    }
  }
}

// Declare Alpine as a global
declare const Alpine: import('alpinejs').default;

export {};
