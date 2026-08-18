/** Redux slice for the product catalog — preloaded from Wagtail page data.
 *
 * The products page (and any page exposing `pageData.products`, e.g. home)
 * bridges its backend-owned product cards into this slice so every listed
 * product component reads ONE source of truth instead of re-fetching or
 * holding page-local copies. The slice is hydrated by init.ts from the SSR
 * data bridge (pageData.products) — no extra network request.
 */
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface ProductCard {
  title: string;
  slug?: string;
  tagline?: string;
  href?: string;
  tag?: string;
  category?: string;
  excerpt?: string;
  description?: string;
  logo_style?: string;
  status?: string;
  version?: string;
  /** Catalog language code (en / ar / …) — part of the snippet contract. */
  language?: string;
  /** ISO 4217 code — unified pricing via FUSION_DEFAULT_CURRENCY. */
  currency?: string;
  /** Base price string in the unified currency (0 = free/open source). */
  price?: string;
  editions?: { name: string; price: string }[];
  tech?: string[];
  [key: string]: unknown;
}

export interface ProductsState {
  /** Catalog as returned by the backend (pageData.products). */
  catalog: ProductCard[];
  /** Lookup by slug for product detail pages. */
  bySlug: Record<string, ProductCard>;
  /** Active language filter — empty string means all languages. */
  languageFilter: string;
  /** True once the catalog has been bridged from Wagtail data. */
  loaded: boolean;
}

const initialState: ProductsState = {
  catalog: [],
  bySlug: {},
  languageFilter: '',
  loaded: false,
};

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    setProducts(state, action: PayloadAction<ProductCard[]>) {
      state.catalog = action.payload;
      state.bySlug = Object.fromEntries(
        action.payload
          .filter((product) => product.slug)
          .map((product) => [String(product.slug), product]),
      );
      state.loaded = true;
    },
    setLanguageFilter(state, action: PayloadAction<string>) {
      state.languageFilter = action.payload;
    },
  },
});

export const { setProducts, setLanguageFilter } = productsSlice.actions;
export default productsSlice.reducer;

// ── Selectors ────────────────────────────────────────────────────────────────
// Typed against the slice shape (not the full RootState) so the slice module
// stays dependency-free — no circular import with store/index.ts. Client
// components (e.g. <ProductGrid />) read the catalog through these instead of
// reaching into the state shape themselves.

export const selectProducts = (state: { products: ProductsState }): ProductCard[] => {
  const filter = state.products.languageFilter;
  if (!filter) return state.products.catalog;
  return state.products.catalog.filter(
    (product) => String(product.language || 'en') === filter,
  );
};

export const selectProductBySlug = (
  state: { products: ProductsState },
  slug: string,
): ProductCard | undefined => state.products.bySlug[slug];

export const selectProductsLoaded = (state: { products: ProductsState }): boolean =>
  state.products.loaded;
