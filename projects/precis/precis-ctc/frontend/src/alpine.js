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

/**
 * courseCatalog — the client component behind the /courses/ catalog page.
 *
 * The course grid is fully server-rendered (no-JS fallback shows every
 * course); this component layers search, filters, sort and grid/list views
 * on top by reading the per-card data-* attributes emitted by
 * pages/courses/index.astro. Filter options are derived from the cards
 * themselves so the UI can never drift from the seeded content.
 */
const registerCourseCatalog = (Alpine) => {
Alpine.data('courseCatalog', () => ({
  // Filter state
  q: '',
  difficulty: [],
  language: '',
  spec: '',
  tags: [],
  offer: 'all',
  cert: false,
  sort: 'default',
  view: 'grid',
  showFilters: false,
  // Derived
  cards: [],
  total: 0,
  count: 0,
  activeCount: 0,
  options: { difficulties: [], languages: [], specs: [], tags: [] },

  init() {
    this.cards = Array.from(this.$root.querySelectorAll('.c-course'));
    this.total = this.cards.length;
    this.count = this.total;
    this.options = this.buildOptions();
    this.apply();
    this.bindSearchShortcut();
  },

  buildOptions() {
    const difficulties = new Set();
    const languages = new Set();
    const specs = new Set();
    const tags = new Set();
    for (const card of this.cards) {
      const diff = card.dataset.difficulty;
      const lang = card.dataset.language;
      if (diff) difficulties.add(diff.replace(/\b\w/g, (c) => c.toUpperCase()));
      if (lang) languages.add(lang);
      for (const s of (card.dataset.specs || '').split(/\s+/).filter(Boolean)) specs.add(s);
      for (const t of (card.dataset.tags || '').split(/\s+/).filter(Boolean)) tags.add(t);
    }
    return {
      difficulties: [...difficulties].sort(),
      languages: [...languages].sort(),
      specs: [...specs].sort(),
      tags: [...tags].sort(),
    };
  },

  matches(card) {
    const d = card.dataset;
    // Search — title + short description
    if (this.q.trim() && !(d.search || '').includes(this.q.trim().toLowerCase())) return false;
    // Difficulty — any-of
    if (this.difficulty.length) {
      const diff = (d.difficulty || '').replace(/\b\w/g, (c) => c.toUpperCase());
      if (!this.difficulty.includes(diff)) return false;
    }
    // Language
    if (this.language && d.language !== this.language) return false;
    // Specialization
    if (this.spec && !(d.specs || '').split(/\s+/).includes(this.spec)) return false;
    // Tags — any-of
    if (this.tags.length) {
      const cardTags = (d.tags || '').split(/\s+/);
      if (!this.tags.some((t) => cardTags.includes(t))) return false;
    }
    // Offer — free vs paid
    if (this.offer === 'free' && d.free !== '1') return false;
    if (this.offer === 'paid' && d.free === '1') return false;
    // Certificate
    if (this.cert && d.cert !== '1') return false;
    return true;
  },

  apply() {
    const grid = this.$root.querySelector('.catalog__grid');
    if (!grid) return;
    const visible = [];
    for (const card of this.cards) {
      const show = this.matches(card);
      card.classList.toggle('is-hidden', !show);
      if (show) visible.push(card);
    }
    // Sort — reorder only the visible cards in place.
    const sorted = this.sortCards(visible);
    if (sorted.length) {
      const fragment = document.createDocumentFragment();
      for (const card of sorted) fragment.appendChild(card);
      grid.appendChild(fragment);
    }
    this.count = visible.length;
    this.activeCount = this.countActiveFilters();
  },

  sortCards(cards) {
    const price = (card) => Number(card.dataset.price || 0);
    const sorted = [...cards];
    switch (this.sort) {
      case 'rating': sorted.sort((a, b) => Number(b.dataset.rating || 0) - Number(a.dataset.rating || 0)); break;
      case 'price-asc': sorted.sort((a, b) => price(a) - price(b)); break;
      case 'price-desc': sorted.sort((a, b) => price(b) - price(a)); break;
      case 'duration': sorted.sort((a, b) => Number(a.dataset.duration || 0) - Number(b.dataset.duration || 0)); break;
      case 'title': sorted.sort((a, b) => (a.dataset.search || '').localeCompare(b.dataset.search || '')); break;
      default: break; // keep server order (featured first, newest first)
    }
    return sorted;
  },

  countActiveFilters() {
    let n = 0;
    if (this.q.trim()) n += 1;
    n += this.difficulty.length;
    if (this.language) n += 1;
    if (this.spec) n += 1;
    n += this.tags.length;
    if (this.offer !== 'all') n += 1;
    if (this.cert) n += 1;
    if (this.sort !== 'default') n += 1;
    return n;
  },

  toggleTag(tag) {
    this.tags = this.tags.includes(tag)
      ? this.tags.filter((t) => t !== tag)
      : [...this.tags, tag];
    this.apply();
  },

  setView(view) {
    this.view = view;
    this.$root.dataset.view = view;
  },

  clear() {
    this.q = '';
    this.difficulty = [];
    this.language = '';
    this.spec = '';
    this.tags = [];
    this.offer = 'all';
    this.cert = false;
    this.sort = 'default';
    this.apply();
  },

  bindSearchShortcut() {
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && !['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement?.tagName || '')) {
        e.preventDefault();
        this.$root.querySelector('.catalog__search-input')?.focus();
      }
    });
  },
}));
};

export default (Alpine) => {
  Alpine.plugin(intersect);
  Alpine.plugin(collapse);
  registerRenderModeSwitch(Alpine);
  registerProductGrid(Alpine);
  registerCourseCatalog(Alpine);
};
