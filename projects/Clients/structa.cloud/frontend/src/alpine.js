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
import { selectProducts, selectProductsLoaded, setLanguageFilter } from './lib/store/productsSlice';

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
    // Single learning teaser — one quiet link card into /learning/ (mirrors
    // the Django road partial, never duplicated by the static home).
    const teaser = (page && page.learning_teaser) || null;
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

    if (teaser && teaser.href) {
      parts.push(
        `<a href="${esc(teaser.href)}" class="card mt-10 flex items-center justify-between gap-4 p-5 transition-colors hover:border-fu-link/40">` +
          `<span class="min-w-0">` +
          (teaser.kicker
            ? `<span class="block font-mono text-[0.65rem] uppercase tracking-[0.14em] text-fu-muted">${esc(teaser.kicker)}</span>`
            : '') +
          `<span class="mt-1 block font-display text-[1.05rem] font-semibold text-fu-ink">${esc(teaser.title || '')}</span>` +
          `</span>` +
          (teaser.cta
            ? `<span class="flex-none font-mono text-[0.7rem] uppercase tracking-[0.14em] text-fu-link">${esc(teaser.cta)} &rarr;</span>`
            : '') +
          `</a>`
      );
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
    // Seed the Redux products slice from the multilingual snippet catalog
    // when the page bridged one (products page). init.ts bridges the
    // English-only ProductPage cards; the snippet catalog carries the
    // per-language rows that make the language filter real. Filtering here
    // matches the SSR render (default 'en'), so no reveal flash on mount.
    const store = window.__reduxStore;
    if (store && typeof store.dispatch === 'function') {
      const catalog = config && config.catalog;
      if (Array.isArray(catalog) && catalog.length) {
        store.dispatch(setProducts(catalog));
        store.dispatch(setLanguageFilter((config && config.filter) || ''));
      }
    }
    this.renderGrid();
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

// Staggered-cascade cleanup — each grid card carries an inline `--reveal-i`
// (its cascade index). Once its reveal transition lands, drop the delay so
// card hovers are never delayed by the cascade. Mirrors the listener in the
// Django base.html, so both render roads share one motion behavior.
if (typeof document !== 'undefined') {
  document.addEventListener(
    'transitionend',
    (e) => {
      const el = e.target;
      if (el && el.style && el.style.getPropertyValue('--reveal-i') && e.propertyName === 'opacity') {
        el.style.transitionDelay = '0ms';
      }
    },
    true
  );
}

/**
 * productLanguageFilter — the language filter bar above the product grid.
 *
 * Reads the distinct languages from the Redux products slice and dispatches
 * ``setLanguageFilter`` on chip click; ``selectProducts`` (the grid's own
 * source of truth) applies the filter, so the grid re-renders without any
 * page-local copy. SSR renders the chips with ``active=''`` (all languages);
 * once the store is bridged the component restores any previously selected
 * language and counts are computed from the store catalog.
 */
const registerProductLanguageFilter = (Alpine) => {
  Alpine.data('productLanguageFilter', (config) => () => ({
    languages: Array.isArray(config && config.languages) ? config.languages : [],
    active: (config && config.active) || '',
    counts: {},

    init() {
      // Restore any previously selected language from the store (SPA nav)
      // so the chips never desync from the grid the visitor actually sees.
      const store = window.__reduxStore;
      const state = store && typeof store.getState === 'function' ? store.getState() : null;
      if (state && state.products && state.products.languageFilter) {
        this.active = state.products.languageFilter;
      }
      this.refreshCounts();
      if (store && typeof store.subscribe === 'function') {
        this.unsub = store.subscribe(() => {
          this.refreshCounts();
          const latest = store.getState();
          if (latest && latest.products && latest.products.languageFilter !== this.active) {
            this.active = latest.products.languageFilter;
          }
        });
      }
    },

    destroy() {
      if (this.unsub) this.unsub();
      this.unsub = null;
    },

    refreshCounts() {
      const store = window.__reduxStore;
      const state = store && typeof store.getState === 'function' ? store.getState() : null;
      const catalog = (state && state.products && state.products.catalog) || [];
      if (!catalog.length) return;
      const counts = { '': catalog.length };
      for (const product of catalog) {
        const code = String(product.language || 'en');
        counts[code] = (counts[code] || 0) + 1;
      }
      this.counts = counts;
    },

    select(code) {
      this.active = code;
      const store = window.__reduxStore;
      if (store && typeof store.dispatch === 'function') {
        store.dispatch(setLanguageFilter(code));
      }
    },
  }));
};

export default (Alpine) => {
  Alpine.plugin(intersect);
  Alpine.plugin(collapse);
  registerRenderModeSwitch(Alpine);
  registerProductGrid(Alpine);
  registerProductLanguageFilter(Alpine);

  // Magnetic hero CTA — the button drifts toward the cursor (≤6px) and snaps
  // back on leave. Motion is a transform on the wrapper (x-data="magnetic"
  // on a .btn-magnetic span), so the button's own :active press-scale and
  // btn-chip arrow animation stay untouched. Tracked 1:1 while the pointer
  // is inside (.btn-magnetic--tracking kills the transition); on leave the
  // CSS spring re-engages for the snap-back. Mirrors the Alpine.data
  // registration in the Django base.html. GPU-cheap: one layout read per
  // pointer-enter, transform-only updates after that.
  Alpine.data('magnetic', () => ({
    mx: 0,
    my: 0,
    active: false,
    reduce: false,
    cx: 0,
    cy: 0,
    init() {
      this.reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },
    center() {
      const r = this.$el.getBoundingClientRect();
      this.cx = r.left + r.width / 2;
      this.cy = r.top + r.height / 2;
    },
    track(e) {
      if (this.reduce) return;
      this.mx = Math.max(-6, Math.min(6, (e.clientX - this.cx) * 0.08));
      this.my = Math.max(-6, Math.min(6, (e.clientY - this.cy) * 0.08));
    },
    leave() {
      this.active = false;
      this.mx = 0;
      this.my = 0;
    },
  }));
};
