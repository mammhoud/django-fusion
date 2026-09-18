/**
 * Product card/grid markup — the ONE source of truth for how a product card
 * renders in precis.
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

/** Reveal directive shared by every card (scroll-into-view via x-intersect). */
const REVEAL = 'x-data x-intersect="$el.classList.add(\'reveal-visible\')"';

/** One catalog card — the exact markup the products page grid shares. */
export function productCardMarkup(product: ProductCard, index: number): string {
  const href = esc(product.href) || `/products/${esc(product.slug || '')}/`;
  const tagline = product.tagline
    ? `<p class="text-sm leading-relaxed text-fu-muted">${esc(product.tagline)}</p>`
    : '';

  return `<a href="${href}" class="card reveal group flex flex-col gap-2 p-6 hover:-translate-y-0.5" ${REVEAL} style="transition-delay: ${index * 80}ms">
  <h3 class="font-display text-[1.05rem] font-semibold text-fu-ink transition-colors group-hover:text-fu-link">${esc(product.title)}</h3>
  ${tagline}
  <span class="mt-auto pt-2 font-mono text-[0.7rem] uppercase tracking-[0.14em] text-fu-link">View product →</span>
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
