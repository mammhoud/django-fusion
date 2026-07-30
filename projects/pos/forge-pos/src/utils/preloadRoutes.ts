/**
 * Route Preloader
 * ================
 * Preloads lazy-loaded page chunks on hover/focus so navigations feel instant.
 *
 * Call `preloadRoute(route)` from `onMouseEnter` / `onFocus` on a nav link.
 * The dynamic import shares the same module cache as the `React.lazy()` calls
 * in App.tsx, so by the time the user clicks, the chunk is already resident.
 *
 * Usage:
 *   import { preloadRoute } from '../utils/preloadRoutes';
 *   <button onMouseEnter={() => preloadRoute('/reports')} onClick={...}>
 *
 * The import is a no-op after the first call (module stays cached).
 */

// ── Each lazy import mirrors the `React.lazy(() => import('./pages/X'))`
//    calls in App.tsx so they share the same webpack/Vite chunk cache. ──

const preloadRegistry: Record<string, () => Promise<unknown>> = {
  '/': () => import('../pages/Home'),
  '/manager': () => import('../pages/ProductManager'),
  '/sale': () => import('../pages/Sale'),
  '/analytics': () => import('../pages/Analytics'),
  '/transactions': () => import('../pages/Transactions'),
  '/inventory': () => import('../pages/Inventory'),
  '/employees': () => import('../pages/Employees'),
  '/recipes': () => import('../pages/Recipes'),
  '/reports': () => import('../pages/Reports'),
  '/settings': () => import('../pages/Settings'),
  '/about': () => import('../pages/About'),
  '/customers': () => import('../pages/Customers'),
  '/suppliers': () => import('../pages/Suppliers'),
  '/kitchen': () => import('../pages/KitchenDisplay'),
  '/schedule': () => import('../pages/EmployeeSchedule'),
  '/payroll': () => import('../pages/Payroll'),
  '/receipt-templates': () => import('../pages/ReceiptTemplates'),
  '/tax-reports': () => import('../pages/TaxReports'),
  '/roles': () => import('../pages/Roles'),
  '/support-chat': () => import('../pages/SupportChat'),
  '/invoice': () => import('../pages/InvoicePage'),
  '/theme-showcase': () => import('../pages/ThemeShowcase'),
  '/theme-studio': () => import('../pages/ThemeStudio'),
  '/staff': () => import('../pages/StaffPage'),
  '/products': () => import('../pages/ProductsPage'),
};

/** Already-preloaded routes — guards against duplicate import() calls. */
const preloaded = new Set<string>();

/**
 * Start loading the chunk for a route path.
 * Safe to call multiple times — only the first call fetches the chunk.
 * Errors are swallowed (preload is a best-effort optimization).
 */
export function preloadRoute(route: string): void {
  if (preloaded.has(route)) return;
  const loader = preloadRegistry[route];
  if (!loader) return;
  preloaded.add(route);
  loader().catch(() => {
    // Preload failure is non-critical — remove from set so we retry if
    // the user actually navigates (the real lazy() call in App.tsx will
    // still work).
    preloaded.delete(route);
  });
}

/**
 * Preload all routes in a category or group.
 * Used when hovering over a category header to warm up all child chunks.
 */
export function preloadRoutes(routes: string[]): void {
  for (const route of routes) {
    preloadRoute(route);
  }
}
