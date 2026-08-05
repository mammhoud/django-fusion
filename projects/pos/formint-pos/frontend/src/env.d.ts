/// <reference types="astro/client" />

declare global {
  interface Window {
    htmx?: {
      process: (element: Element) => void;
    };
  }
}

export {};
