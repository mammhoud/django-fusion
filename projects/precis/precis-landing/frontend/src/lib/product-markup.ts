/**
 * Product card/grid markup — the ONE source of truth for how a product card
 * renders in precis-landing.
 *
 * Imported by both sides of the render contract:
 *   - `<ProductGrid />` (Astro frontmatter, build/SSR time) renders the grid
 *     from page props so static output carries the real catalog.
 *   - `src/alpine.js` (`productGrid` component) re-renders the same grid
 *     client-side from the Redux products slice (`selectProducts`), keeping
 *     the DOM in sync with the store.
 *
 * Keeping the card markup in one pure module guarantees the SSR markup and
 * the client re-render are byte-identical (no layout jump, no reveal flash).
 */
import type { ProductCard } from './store/productsSlice';

const ENTITIES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

/** HTML-escape a value for safe interpolation into markup. */
export function esc(value: unknown): string {
  return String(value ?? '').replace(/[&<>"']/g, (c) => ENTITIES[c] ?? c);
}

// ── Brand logo glyphs ────────────────────────────────────────────────────
// Mirrors components/ui/ProductLogo.astro: each style owns a muted accent
// hue via .product-logo[data-brand=…] in globals.css; the glyph is always
// currentColor. Kept here as raw SVG so the client re-render (innerHTML)
// can render logos without importing an .astro component.

const LOGO_BRAND: Record<string, string> = {
  crest: 'formints',
  ribbon: 'precis',
  isometric: 'loop',
  orbit: 'syntara',
  mark: 'syntara',
  ascent: 'vresume',
  research: 'precis-ctc',
};

const LOGO_SVGS: Record<string, string> = {
  crest: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M16 2.5l11.5 4v9.5c0 6.8-4.9 11.6-11.5 13.5C9.4 27.6 4.5 22.8 4.5 16.5V6.5L16 2.5z" stroke-linejoin="round"/><path d="M9.5 19.5h13" stroke-linecap="round"/><path d="M11.8 14.8l2.9 2.9 5.8-6.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  ribbon: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 8.5h24v7.5a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V8.5z" stroke-linejoin="round"/><path d="M10.5 19.5l2.4 4.5M16 19.5v4.5M21.5 19.5l-2.4 4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M12.5 12.5l2.6 2.6 5-5.4M15.1 15.1V9" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  isometric: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M16 3l11 6v14L16 29 5 23V9l11-6z" stroke-linejoin="round"/><path d="M5 9l11 6 11-6M16 15v14" stroke-linejoin="round"/><path d="M16 10.5l5.8 3.2v6.6L16 23.5l-5.8-3.2v-6.6l5.8-3.2z" stroke-linejoin="round"/><path d="M10.2 13.7l5.8 3.2 5.8-3.2M16 16.9v6.6" stroke-linejoin="round"/></svg>',
  ascent: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 26h7v-7h7v-7h7" stroke-linecap="round" stroke-linejoin="round"/><path d="M24.8 12.2l2.4 2.4 4-4.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 6v20" stroke-linecap="round"/></svg>',
  research: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="16" cy="16" r="9"/><path d="M16 7v18M7 16h18" stroke-linecap="round"/><circle cx="16" cy="16" r="2.5" fill="currentColor" stroke="none"/></svg>',
  orbit: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="16" cy="16" r="2.6" fill="currentColor" stroke="none"/><ellipse cx="16" cy="16" rx="10.5" ry="4.2" transform="rotate(-24 16 16)" stroke-linejoin="round"/><ellipse cx="16" cy="16" rx="10.5" ry="4.2" transform="rotate(24 16 16)" stroke-linejoin="round"/><circle cx="25.2" cy="12.4" r="1.4" fill="currentColor" stroke="none"/></svg>',
};

/** Brand token for a logo style — drives the per-brand accent hue. */
export function brandForStyle(style?: string): string {
  return LOGO_BRAND[String(style || '')] ?? 'formints';
}

/** ProductLogo markup (span + per-style SVG), byte-compatible with ProductLogo.astro. */
export function productLogoMarkup(product: ProductCard): string {
  const style = String(product.logo_style || 'crest');
  const svg = LOGO_SVGS[style] ?? LOGO_SVGS.orbit;
  return `<span class="product-logo" data-brand="${brandForStyle(style)}">${svg}</span>`;
}

/** Reveal directive shared by every card (scroll-into-view via x-intersect). */
const REVEAL = 'x-data x-intersect=\'`$el.classList.add("reveal-visible")`\'';

/** One catalog card — the exact markup the products page and home grid share. */
export function productCardMarkup(product: ProductCard, index: number): string {
  const href = esc(product.href) || `/products/${esc(product.slug || '')}/`;
  // External product links (GitHub, hosted SaaS) open in a new tab — same
  // behavior the pages previously applied via product.external.
  const external = String(product.href || '').startsWith('http');
  const externalAttrs = external ? ' target="_blank" rel="noopener noreferrer"' : '';
  const status =
    product.status === 'development'
      ? '<span class="badge-dev">under development</span>'
      : '';
  const version = product.version
    ? `<p class="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-fu-muted">${esc(product.version)}</p>`
    : '';
  const tagline = product.tagline
    ? `<p class="text-sm leading-relaxed text-fu-muted">${esc(product.tagline)}</p>`
    : '';
  const description =
    !product.tagline && product.description
      ? `<p class="text-sm leading-relaxed text-fu-muted">${esc(product.description)}</p>`
      : '';
  const editions = Array.isArray(product.editions) && product.editions.length
    ? `<div class="flex flex-wrap gap-1.5">${product.editions
        .slice(0, 3)
        .map((ed) => `<span class="edition-chip">${esc(ed.name)} <strong>${esc(ed.price)}</strong></span>`)
        .join('')}${
        product.editions.length > 3
          ? `<span class="inline-flex items-center px-1 font-mono text-[0.62rem] text-fu-muted">+${product.editions.length - 3}</span>`
          : ''
      }</div>`
    : '';
  const tech = Array.isArray(product.tech) && product.tech.length
    ? `<span class="inline-flex items-center gap-1 rounded-full border border-fu-line bg-fu-card px-2.5 py-0.5 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-fu-muted">${esc(product.tech[0])}${product.tech.length > 1 ? ` +${product.tech.length - 1}` : ''}</span>`
    : '';
  // Unified-currency price chip — part of the language/currency snippet
  // contract. Free/open-source products (price 0) show a “free” label;
  // anything else shows the amount + ISO currency code.
  const currency = product.currency || '';
  const price = product.price;
  const priceChip =
    price !== undefined && price !== null
      ? Number(price) <= 0
        ? '<span class="inline-flex items-center rounded-full border border-fu-live/40 bg-fu-live/10 px-2.5 py-0.5 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-fu-live">free</span>'
        : `<span class="inline-flex items-center gap-1 rounded-full border border-fu-line bg-fu-card px-2.5 py-0.5 font-mono text-[0.6rem] uppercase tracking-[0.12em] text-fu-ink">${esc(price)}${currency ? ` <em class="not-italic text-fu-muted">${esc(currency)}</em>` : ''}</span>`
      : '';
  const languageChip = product.language && product.language !== 'en'
    ? `<span class="inline-flex items-center rounded-full border border-fu-line bg-fu-card px-2 py-0.5 font-mono text-[0.55rem] uppercase tracking-[0.12em] text-fu-muted">${esc(product.language)}</span>`
    : '';
  const category = esc(product.category || product.tag || 'product');

  return `<a href="${href}"${externalAttrs} class="card reveal group flex flex-col gap-3 p-6 hover:-translate-y-0.5" ${REVEAL} style="--reveal-i: ${index}">
  <div class="flex items-start justify-between gap-3">
    ${productLogoMarkup(product)}
    <div class="flex flex-col items-end gap-1.5">
      <div class="flex items-center gap-1.5">
        ${status}
        <button type="button" data-open-brand="${esc(product.slug || '')}" aria-label="${esc(product.title)} brand kit" title="Brand kit — the story behind the mark" class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-fu-line bg-fu-card text-fu-muted transition-colors hover:border-fu-link/50 hover:text-fu-link"><svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path stroke-linecap="round" d="M12 11v5M12 8h.01"/></svg></button>
      </div>
      <span class="badge badge-primary">${category}</span>
    </div>
  </div>
  <h3 class="font-display text-[1.05rem] font-semibold text-fu-ink transition-colors group-hover:text-fu-link">${esc(product.title)}</h3>
  ${version}${tagline}${description}${editions}
  <div class="mt-auto flex flex-wrap items-center gap-2 pt-2">
    <span class="font-mono text-[0.7rem] uppercase tracking-[0.14em] text-fu-link">View product →</span>
    ${tech}${priceChip}${languageChip}
  </div>
</a>`;
}

/** Join cards into a grid body (used by SSR and the client re-render). */
export function productGridMarkup(products: ProductCard[]): string {
  return products.map((product, index) => productCardMarkup(product, index)).join('\n');
}

/**
 * Stable identity of a catalog for change detection: slug order joined by '|'.
 * The ProductGrid client component compares its SSR key to the store key and
 * only re-renders when the catalog actually changed (no flash on mount).
 */
export function productSlugKey(products: ProductCard[]): string {
  return products
    .map((p) => String(p.slug || p.title || ''))
    .filter(Boolean)
    .join('|');
}
