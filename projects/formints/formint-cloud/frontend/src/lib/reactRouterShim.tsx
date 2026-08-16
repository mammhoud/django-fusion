/**
 * react-router-dom → Astro MPA shim
 * =================================
 * formintA now runs on Astro's file-based routing: every route is a real HTML
 * page and every navigation is a full page load. The app components were
 * written against react-router hooks (`useNavigate`, `useLocation`,
 * `useSearchParams`); `astro.config.mjs` aliases `react-router-dom` to this
 * module so those hooks keep working without touching the ~40k lines of page
 * code.
 *
 *  - `useNavigate`     → `window.location.assign` / `replace` (real MPA nav)
 *  - `useLocation`     → the current page's URL parts (static per load)
 *  - `useSearchParams` → read-only `URLSearchParams` from `window.location`
 *
 * Tests still resolve the REAL `react-router-dom` (vitest.config.ts has no
 * alias) and mock `useNavigate` explicitly in test-utils.
 */
import { useCallback, type ReactNode } from 'react';

/**
 * Test-only compatibility wrapper. The production app uses Astro's MPA
 * routing, but a few existing component tests still wrap trees in
 * `MemoryRouter`. Keeping the wrapper intentionally transparent preserves
 * those tests without reintroducing a client-side router into the app.
 */
export function MemoryRouter({ children }: { children?: ReactNode }) {
  return children ?? null;
}

function currentSearchParams(): URLSearchParams {
  return typeof window === 'undefined'
    ? new URLSearchParams()
    : new URLSearchParams(window.location.search);
}

/** Mirrors react-router's `useNavigate` — but navigation is a page load. */
export function useNavigate() {
  return useCallback((to: string, options?: { replace?: boolean }) => {
    if (typeof window === 'undefined') return;
    const target = String(to);
    if (options?.replace) {
      window.location.replace(target);
    } else {
      window.location.assign(target);
    }
  }, []);
}

/** Static per page load — used by PageLayout for the active nav highlight. */
export function useLocation() {
  return {
    pathname: typeof window === 'undefined' ? '/' : window.location.pathname,
    search: typeof window === 'undefined' ? '' : window.location.search,
    hash: typeof window === 'undefined' ? '' : window.location.hash,
    state: null,
    key: 'default',
  };
}

/** Read-only — every call site in this codebase only reads params. */
export function useSearchParams() {
  const searchParams = currentSearchParams();
  const setSearchParams = useCallback(() => {
    // No-op setter: MPA navigation goes through real URLs (query params are
    // already reflected in window.location.search on load).
  }, []);
  return [searchParams, setSearchParams] as const;
}

/** Tiny compatibility export for anything that rendered a <Navigate>. */
export function Navigate({ to }: { to: string }) {
  if (typeof window !== 'undefined') window.location.replace(to);
  return null;
}
