/**
 * Alpine entrypoint — registered via @astrojs/alpinejs in astro.config.mjs.
 *
 * The integration injects `setup(Alpine)` (calling this module's default
 * export) before `Alpine.start()`, so this file must NOT call Alpine.start()
 * itself — that double-initializes Alpine and logs a warning.
 *
 * Registers the plugins the components rely on:
 *   - @alpinejs/intersect — `x-intersect` scroll reveals (hero, cards, stats)
 *   - @alpinejs/collapse  — `x-collapse` accordions (FAQ, pricing, Accordion)
 *
 * Without the entrypoint only core Alpine loads and every `x-intersect`
 * directive silently no-ops — reveal elements stay at `opacity: 0` forever.
 */
import intersect from '@alpinejs/intersect';
import collapse from '@alpinejs/collapse';
import { productGridMarkup, productSlugKey } from './lib/product-markup';
import { selectProducts, selectProductsLoaded } from './lib/store/productsSlice';

/**
 * renderModeSwitch — the road-switching client component behind
 * `<RenderModeSwitch route=... />`.
 *
 * Reads the Redux config slice (`config.renderMode`, hydrated from the
 * /apis/assets/ manifest by Layout.astro and bridged into Redux by
 * lib/store/init.ts) and renders the region on one of the two roads:
 *
 *   - `fusion-render` → HTML road: htmx.ajax() to the server-rendered
 *     fragment (HX-Request contract, global indicator, data-fragment-fallback).
 *   - `data-api`      → data road: fetch(renderMode.content.data) JSON and
 *     render the payload client-side as a structured document.
 *
 * Registered here (before Alpine.start()) so `x-data="renderModeSwitch({…})"`
 * works on every page; the per-instance config (endpoints) is passed by the
 * Astro component.
 */
const registerRenderModeSwitch = (Alpine) => {
Alpine.data('renderModeSwitch', (config) => () => ({
  road: 'pending',
  endpoint: '',

  init() {
    const renderMode =
      (window.__reduxStore && window.__reduxStore.getState().config.renderMode) || null;
    const mode = (renderMode && renderMode.mode) || null;
    const dataPointer = config.dataEndpoint || (renderMode && renderMode.content && renderMode.content.data) || '';

    if (mode === 'data-api') {
      this.road = 'data';
      this.endpoint = dataPointer;
      this.$nextTick(() => this.loadDataRoad());
    } else if (mode === 'fusion-render' || config.hasBackend) {
      this.road = 'html';
      this.endpoint = config.htmlEndpoint;
      this.$nextTick(() => this.loadHtmlRoad());
    } else {
      this.road = 'static';
    }
  },

  /** HTML road — server-rendered fragment through htmx (indicator + fallback). */
  loadHtmlRoad() {
    const target = this.$el.querySelector('[data-road-target="html"]');
    if (!target) return;
    const htmxApi = window.htmx;
    if (!htmxApi || typeof htmxApi.ajax !== 'function') {
      this.showFallback();
      return;
    }
    htmxApi
      .ajax('GET', this.endpoint, { target, swap: 'innerHTML' })
      .catch(() => this.showFallback());
  },

  /** Data road — fetch the JSON page API and render it client-side. */
  async loadDataRoad() {
    const target = this.$el.querySelector('[data-road-target="data"]');
    if (!target) return;
    if (!this.endpoint) {
      this.showFallback();
      return;
    }
    try {
      const res = await fetch(this.endpoint, { headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const page = await res.json();
      target.innerHTML = this.renderDataRoad(page);
      if (window.Alpine && typeof window.Alpine.initTree === 'function') {
        window.Alpine.initTree(target);
      }
    } catch {
      this.showFallback();
    }
  },

  /** Swap the quiet fallback note into the ACTIVE road's target. */
  showFallback() {
    // `road` is exactly 'html' or 'data' when this runs (never 'pending' or
    // 'static'), so this always selects the visible target — the html target
    // must not win just because it comes first in the DOM.
    const target = this.$el.querySelector(`[data-road-target="${this.road}"]`);
    if (!target) return;
    const fallback = this.$el.querySelector('template[data-fragment-fallback]');
    if (fallback) target.innerHTML = fallback.innerHTML;
  },

  /** Structured client-side rendering of the JSON page payload. */
  renderDataRoad(page) {
    const esc = (value) =>
      String(value ?? '').replace(
        /[&<>"']/g,
        (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
      );
    const hero = (page && page.hero) || {};
    const cta = (page && page.cta) || {};
    const stats = Array.isArray(page && page.stats) ? page.stats : [];
    const features = Array.isArray(page && page.features) ? page.features : [];
    const products = Array.isArray(page && page.products) ? page.products : [];
    const button = (c) =>
      c && c.href
        ? `<a href="${esc(c.href)}" class="${c.style === 'secondary' ? 'btn-secondary' : 'btn-primary'}">${esc(c.label)}</a>`
        : '';
    const heroButtons = [hero.primary_cta, hero.secondary_cta]
      .map(button)
      .filter(Boolean)
      .join('');
    const parts = [];

    parts.push('<div class="road-data">');

    if (hero.badge || hero.title || hero.subtitle) {
      parts.push('<header class="road-data__hero">');
      if (hero.badge) parts.push(`<p class="tag-marker mb-4">${esc(hero.badge)}</p>`);
      parts.push(
        `<h3 class="font-display text-3xl font-bold tracking-tight text-fu-ink md:text-4xl">${esc(hero.title || (page && page.title) || '')}</h3>`
      );
      if (hero.subtitle) parts.push(`<p class="mt-3 max-w-2xl text-fu-muted">${esc(hero.subtitle)}</p>`);
      if (heroButtons) parts.push(`<div class="mt-6 flex flex-wrap gap-3">${heroButtons}</div>`);
      parts.push('</header>');
    }

    if (stats.length) {
      parts.push('<div class="mt-10 grid grid-cols-2 gap-4 md:grid-cols-4">');
      stats.forEach((stat) => {
        const value = esc(stat.value);
        const suffix = stat.suffix ? `<span class="text-fu-link">${esc(stat.suffix)}</span>` : '';
        parts.push(
          `<div class="card p-5 text-center"><p class="font-display text-3xl font-bold text-fu-ink">${value}${suffix}</p>` +
            `<p class="mt-1 text-xs uppercase tracking-wider text-fu-muted">${esc(stat.label)}</p></div>`
        );
      });
      parts.push('</div>');
    }

    if (features.length) {
      parts.push('<div class="mt-10 grid grid-cols-1 gap-4 md:grid-cols-2">');
      features.forEach((feature) => {
        parts.push(
          `<div class="card group p-5"><h4 class="font-display text-[1.05rem] font-semibold text-fu-ink">${esc(feature.title)}</h4>` +
            `<p class="mt-2 text-sm leading-relaxed text-fu-muted">${esc(feature.description)}</p></div>`
        );
      });
      parts.push('</div>');
    }

    if (products.length) {
      parts.push('<div class="mt-10 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">');
      products.forEach((product) => {
        parts.push(
          `<a href="${esc(product.href) || `/products/${esc(product.slug || '')}/`}" class="card group flex flex-col gap-2 p-5">` +
            `<h4 class="font-display text-[1.05rem] font-semibold text-fu-ink transition-colors group-hover:text-fu-link">${esc(product.title)}</h4>` +
            `<p class="text-sm leading-relaxed text-fu-muted">${esc(product.tagline || product.excerpt || '')}</p>` +
            `<span class="mt-auto pt-2 font-mono text-[0.7rem] uppercase tracking-[0.14em] text-fu-link">View product &rarr;</span></a>`
        );
      });
      parts.push('</div>');
    }

    if (page && page.body) {
      // Trusted backend rich text (same trust level as the HTMX fragment).
      parts.push(`<div class="road-data__body mt-10">${page.body}</div>`);
    }

    if (cta.title) {
      const ctaButtons = [cta.primary_cta, cta.secondary_cta].map(button).filter(Boolean).join('');
      parts.push(
        `<div class="card mt-10 flex flex-col items-center gap-4 p-8 text-center">` +
          `<h3 class="font-display text-2xl font-bold text-fu-ink">${esc(cta.title)}</h3>` +
          (cta.subtitle ? `<p class="max-w-xl text-fu-muted">${esc(cta.subtitle)}</p>` : '') +
          (ctaButtons ? `<div class="flex flex-wrap gap-3">${ctaButtons}</div>` : '') +
          `</div>`
      );
    }

    parts.push('</div>');
    return parts.join('');
  },
}));
};

/**
 * productGrid — the client component behind `<ProductGrid />`.
 *
 * Reads the Redux products slice (`selectProducts`) as the single source of
 * truth for the catalog and re-renders the grid whenever the store changes.
 * The SSR-rendered grid is left untouched while the store catalog matches it
 * (keyed by slug order), so there is no reveal flash on mount.
 */
const registerProductGrid = (Alpine) => {
Alpine.data('productGrid', (config) => () => ({
  lastKey: (config && config.ssrKey) || '',
  unsub: null,

  init() {
    this.renderGrid();
    const store = window.__reduxStore;
    this.unsub =
      store && typeof store.subscribe === 'function'
        ? store.subscribe(() => this.renderGrid())
        : null;
  },

  destroy() {
    if (this.unsub) this.unsub();
    this.unsub = null;
  },

  /** Re-render the grid from the store only when the catalog changed. */
  renderGrid() {
    const store = window.__reduxStore;
    const state = store && typeof store.getState === 'function' ? store.getState() : null;
    // The store was never bridged (no pageData.products / hydration failure) —
    // keep the server-rendered grid as-is instead of wiping it with the note.
    if (!state || !selectProductsLoaded(state)) return;
    const catalog = selectProducts(state);
    const exclude = (config && config.excludeSlug) || '';
    const visible = exclude
      ? catalog.filter((p) => String(p.slug || '') !== String(exclude))
      : catalog;
    const key = productSlugKey(visible);
    if (key === this.lastKey) return;
    this.lastKey = key;

    const target = this.$el.querySelector('[data-product-grid-target]');
    if (!target) return;
    const empty = this.$el.querySelector('template[data-product-grid-empty]');
    if (!visible.length) {
      target.innerHTML = empty ? empty.innerHTML : '';
      return;
    }
    target.innerHTML = productGridMarkup(visible);
    if (window.Alpine && typeof window.Alpine.initTree === 'function') {
      window.Alpine.initTree(target);
    }
  },
}));
};

export default (Alpine) => {
  Alpine.plugin(intersect);
  Alpine.plugin(collapse);
  registerRenderModeSwitch(Alpine);
  registerProductGrid(Alpine);
};
