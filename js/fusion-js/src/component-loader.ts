/**
 * FusionComponentLoader — lazy-loads component JS/CSS chunks using
 * ``window.__FUSION_COMPONENT_ASSETS__`` and IntersectionObserver.
 *
 * The asset map is embedded by the Django backend via
 * {% fusion_component_assets_json %}.
 *
 * Usage::
 *
 *   import { FusionComponentLoader } from 'fusion-js/component-loader';
 *
 *   if (window.__FUSION_COMPONENT_ASSETS__) {
 *     const loader = new FusionComponentLoader(
 *       window.__FUSION_COMPONENT_ASSETS__
 *     );
 *     loader.preloadCritical(skeletonBridge.getEntries());
 *     loader.observeComponents();
 *   }
 */

// ── types ─────────────────────────────────────────────────────────────

export interface ComponentAssetEntry {
  component: string;
  css: string[];
  js: string[];
  vendor?: string[];
  size_bytes?: number;
  preload?: boolean;
}

export interface ComponentAssetMap {
  components: Record<string, ComponentAssetEntry>;
}

// ── loader ────────────────────────────────────────────────────────────

export class FusionComponentLoader {
  private loaded = new Set<string>();
  private observer: IntersectionObserver | null = null;

  constructor(private assetMap: ComponentAssetMap) {}

  /**
   * Preload critical (above-the-fold) component chunks via
   * ``<link rel="modulepreload">`` or ``<link rel="preload">``.
   *
   * @param pageComponents  List of component paths on the page (e.g.
   *   from the skeleton bridge). Only components marked ``preload``
   *   in the asset map are preloaded.
   */
  preloadCritical(pageComponents: { component: string }[]): void {
    for (const { component } of pageComponents) {
      const entry = this.assetMap.components[component];
      if (entry?.preload) {
        this._preloadEntry(entry);
      }
    }
  }

  /**
   * Start observing ``[data-fusion-component]`` elements and lazy-load
   * their JS/CSS when they enter the viewport (with 200px root margin).
   */
  observeComponents(): void {
    if (typeof IntersectionObserver === 'undefined') {
      // Fallback: load everything eagerly
      for (const name of Object.keys(this.assetMap.components)) {
        this.loadComponent(name);
      }
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const name = (entry.target as HTMLElement).dataset.fusionComponent;
            if (name) {
              this.loadComponent(name);
              this.observer!.unobserve(entry.target);
            }
          }
        }
      },
      { rootMargin: '200px' },
    );

    // Observe all elements with data-fusion-component
    document.querySelectorAll('[data-fusion-component]').forEach((el) => {
      this.observer!.observe(el);
    });
  }

  /**
   * Dynamically load a component's JS and CSS.  Idempotent — each
   * component is loaded at most once.
   */
  async loadComponent(name: string): Promise<void> {
    if (this.loaded.has(name)) return;

    const entry = this.assetMap.components[name];
    if (!entry) return;

    this.loaded.add(name);

    // Inject CSS
    for (const css of entry.css) {
      if (!document.querySelector(`link[href="${css}"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = css;
        document.head.appendChild(link);
      }
    }

    // Dynamic JS import (supports both webpack chunks and ESM modules)
    for (const js of entry.js) {
      try {
        await import(/* @vite-ignore */ /* webpackIgnore: true */ js);
      } catch {
        // Fallback: create a script tag for non-module bundles
        if (!document.querySelector(`script[src="${js}"]`)) {
          const script = document.createElement('script');
          script.src = js;
          script.defer = true;
          document.body.appendChild(script);
        }
      }
    }

    // Vendor dependencies (shared chunks)
    if (entry.vendor) {
      for (const vendor of entry.vendor) {
        if (!document.querySelector(`script[src="${vendor}"]`)) {
          const script = document.createElement('script');
          script.src = vendor;
          script.defer = true;
          document.body.appendChild(script);
        }
      }
    }
  }

  /** Check whether a component has already been loaded. */
  isLoaded(name: string): boolean {
    return this.loaded.has(name);
  }

  // ── internal ────────────────────────────────────────────────────

  private _preloadEntry(entry: ComponentAssetEntry): void {
    for (const js of entry.js) {
      if (!document.querySelector(`link[rel="modulepreload"][href="${js}"]`)) {
        const link = document.createElement('link');
        link.rel = 'modulepreload';
        link.href = js;
        document.head.appendChild(link);
      }
    }
    for (const css of entry.css) {
      if (!document.querySelector(`link[rel="preload"][href="${css}"]`)) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = css;
        document.head.appendChild(link);
      }
    }
  }
}

// ── global types ──────────────────────────────────────────────────────

declare global {
  interface Window {
    __FUSION_COMPONENT_ASSETS__?: ComponentAssetMap;
  }
}
