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
  '/': () => import('../app/pages/dashboard/Home'),
  '/manager': () => import('../app/pages/pos/ProductManager'),
  '/sale': () => import('../app/pages/pos/Sale'),
  '/analytics': () => import('../app/pages/analytics/Analytics'),
  '/transactions': () => import('../app/pages/pos/Transactions'),
  '/inventory': () => import('../app/pages/kitchen/Inventory'),
  '/employees': () => import('../app/pages/admin/Employees'),
  '/recipes': () => import('../app/pages/kitchen/Recipes'),
  '/reports': () => import('../app/pages/analytics/Reports'),
  '/settings': () => import('../app/pages/admin/Settings'),
  '/coupons': () => import('../app/pages/admin/Coupons'),
  '/about': () => import('../app/pages/admin/About'),
  '/customers': () => import('../app/pages/customers/Customers'),
  '/suppliers': () => import('../app/pages/customers/Suppliers'),
  '/kitchen': () => import('../app/pages/kitchen/KitchenDisplay'),
  '/schedule': () => import('../app/pages/admin/EmployeeSchedule'),
  '/payroll': () => import('../app/pages/admin/Payroll'),
  '/notes': () => import('../app/pages/admin/Notes'),
  '/reports?tab=taxReports': () => import('../app/pages/analytics/Reports'),
  '/roles': () => import('../app/pages/admin/Roles'),
  '/currencies': () => import('../app/pages/admin/Currencies'),
  '/tax-profiles': () => import('../app/pages/admin/TaxProfiles'),
  '/export': () => import('../app/pages/analytics/Export'),
  '/support-chat': () => import('../app/pages/admin/SupportChat'),
  '/staff': () => import('../app/pages/admin/StaffPage'),
  '/register': () => import('../app/pages/admin/CashRegister'),
  '/products': () => import('../app/pages/pos/ProductsPage'),
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
