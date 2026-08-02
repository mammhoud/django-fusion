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
  '/': () => import('../pages/dashboard/Home'),
  '/manager': () => import('../pages/pos/ProductManager'),
  '/sale': () => import('../pages/pos/Sale'),
  '/analytics': () => import('../pages/analytics/Analytics'),
  '/transactions': () => import('../pages/pos/Transactions'),
  '/inventory': () => import('../pages/kitchen/Inventory'),
  '/employees': () => import('../pages/admin/Employees'),
  '/recipes': () => import('../pages/kitchen/Recipes'),
  '/reports': () => import('../pages/analytics/Reports'),
  '/settings': () => import('../pages/admin/Settings'),
  '/about': () => import('../pages/admin/About'),
  '/customers': () => import('../pages/customers/Customers'),
  '/suppliers': () => import('../pages/customers/Suppliers'),
  '/kitchen': () => import('../pages/kitchen/KitchenDisplay'),
  '/schedule': () => import('../pages/admin/EmployeeSchedule'),
  '/payroll': () => import('../pages/admin/Payroll'),
  '/notes': () => import('../pages/admin/Notes'),
  '/tax-reports': () => import('../pages/analytics/TaxReports'),
  '/roles': () => import('../pages/admin/Roles'),
  '/support-chat': () => import('../pages/admin/SupportChat'),
  '/staff': () => import('../pages/admin/StaffPage'),
  '/products': () => import('../pages/pos/ProductsPage'),
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
