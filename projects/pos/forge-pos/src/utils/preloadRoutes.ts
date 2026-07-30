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
  '/manager': () => import('../pages/inventory/ProductManager'),
  '/sale': () => import('../pages/sales/Sale'),
  '/analytics': () => import('../pages/reports/Analytics'),
  '/transactions': () => import('../pages/sales/Transactions'),
  '/inventory': () => import('../pages/inventory/Inventory'),
  '/employees': () => import('../pages/staff/Employees'),
  '/recipes': () => import('../pages/inventory/Recipes'),
  '/reports': () => import('../pages/reports/Reports'),
  '/settings': () => import('../pages/settings/Settings'),
  '/about': () => import('../pages/settings/About'),
  '/customers': () => import('../pages/customers/Customers'),
  '/suppliers': () => import('../pages/customers/Suppliers'),
  '/kitchen': () => import('../pages/kitchen/KitchenDisplay'),
  '/schedule': () => import('../pages/staff/EmployeeSchedule'),
  '/payroll': () => import('../pages/staff/Payroll'),
  '/notes': () => import('../pages/settings/Notes'),
  '/tax-reports': () => import('../pages/reports/TaxReports'),
  '/roles': () => import('../pages/staff/Roles'),
  '/support-chat': () => import('../pages/settings/SupportChat'),
  '/invoice': () => import('../pages/sales/InvoicePage'),
  '/theme-studio': () => import('../pages/settings/ThemeStudio'),
  '/staff': () => import('../pages/staff/StaffPage'),
  '/products': () => import('../pages/inventory/ProductsPage'),
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
