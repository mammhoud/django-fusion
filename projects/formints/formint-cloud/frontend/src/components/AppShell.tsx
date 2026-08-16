import {
  lazy,
  Suspense,
  useEffect,
  type ComponentType,
  type LazyExoticComponent,
} from 'react';
import Auth from '../app/pages/auth/Auth';
import ChatSupport from './pos/ChatSupport';
import ScrollToTopButton from './ui/ScrollToTopButton';
import BrandLoader from './ui/BrandLoader';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { LanguageProvider } from '../contexts/LanguageContext';
import { CurrencyProvider } from '../contexts/CurrencyContext';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';
import { ModalProvider } from './ui/ModalProvider';
import { useNavigationPredictor } from '../hooks/useNavigationPredictor';
import { ROLE_ROUTES } from './layout/SideNav';
import '../i18n';

// FlyonUI interactive components (modals, dropdowns, toggles, etc.) — the
// island bundles its own copy and re-inits on mount.
import 'flyonui/flyonui';

// ── Lazy-loaded pages (code-split by route) ──
// These chunks load on first visit, not on initial page load. The largest
// pages (Reports, Settings, Transactions, Sale…) bundle heavy deps like
// Recharts, jsPDF and Excel export utilities only when visited.
const Home = lazy(() => import('../app/pages/dashboard/Home'));
const ProductManager = lazy(() => import('../app/pages/pos/ProductManager'));
const Sale = lazy(() => import('../app/pages/pos/Sale'));
const Analytics = lazy(() => import('../app/pages/analytics/Analytics'));
const Transactions = lazy(() => import('../app/pages/pos/Transactions'));
const Inventory = lazy(() => import('../app/pages/kitchen/Inventory'));
const Employees = lazy(() => import('../app/pages/admin/Employees'));
const Recipes = lazy(() => import('../app/pages/kitchen/Recipes'));
const Reports = lazy(() => import('../app/pages/analytics/Reports'));
const Settings = lazy(() => import('../app/pages/admin/Settings'));
const About = lazy(() => import('../app/pages/admin/About'));
const Customers = lazy(() => import('../app/pages/customers/Customers'));
const Suppliers = lazy(() => import('../app/pages/customers/Suppliers'));
const KitchenDisplay = lazy(() => import('../app/pages/kitchen/KitchenDisplay'));
const EmployeeSchedule = lazy(() => import('../app/pages/admin/EmployeeSchedule'));
const Payroll = lazy(() => import('../app/pages/admin/Payroll'));
const Notes = lazy(() => import('../app/pages/admin/Notes'));
const Coupons = lazy(() => import('../app/pages/admin/Coupons'));
const Roles = lazy(() => import('../app/pages/admin/Roles'));
const SupportChat = lazy(() => import('../app/pages/admin/SupportChat'));
const StaffPage = lazy(() => import('../app/pages/admin/StaffPage'));
const ProductsPage = lazy(() => import('../app/pages/pos/ProductsPage'));
const BranchOverview = lazy(() => import('../app/pages/analytics/BranchOverview'));
const CloudDashboard = lazy(() => import('../app/pages/analytics/CloudDashboard'));

// ── Route → page mapping (Astro file-based routing supplies the pathname) ──
const ROUTE_PAGES: Record<string, LazyExoticComponent<ComponentType>> = {
  '/dashboard': Home,
  '/manager': ProductManager,
  '/sale': Sale,
  '/analytics': Analytics,
  '/transactions': Transactions,
  '/inventory': Inventory,
  '/employees': Employees,
  '/recipes': Recipes,
  '/reports': Reports,
  '/settings': Settings,
  '/about': About,
  '/customers': Customers,
  '/suppliers': Suppliers,
  '/kitchen': KitchenDisplay,
  '/schedule': EmployeeSchedule,
  '/payroll': Payroll,
  '/notes': Notes,
  '/coupons': Coupons,
  '/roles': Roles,
  '/support-chat': SupportChat,
  '/staff': StaffPage,
  '/products': ProductsPage,
  '/telemetry': BranchOverview,
  '/cloud-dashboard': CloudDashboard,
};

// ── Employee-accessible routes (shared with SideNav filtering) ──
const EMPLOYEE_ROUTES = ROLE_ROUTES.employee;

/**
 * The React island mounted by every Astro page.
 *
 * Replaces the react-router SPA shell: the `route` prop (the current
 * pathname, provided by Astro) selects which page component renders. All
 * navigation is a full page load through Astro's file-based routing.
 */
function AppShellContent({ route }: { route: string }) {
  const { isAuthenticated, isAuthRequired, user } = useAuth();
  const { toggleMode } = useTheme();

  // Dedicated KDS popout window (loaded with ?kds=1) — renders the Kitchen
  // Display full-bleed with no app chrome, no auth gate and no floating widgets.
  const isKdsPopout =
    typeof window !== 'undefined' &&
    new URLSearchParams(window.location.search).get('kds') === '1';

  const redirectRoot = isAuthenticated && route === '/';
  const employeeBlocked =
    user?.role === 'employee' && !EMPLOYEE_ROUTES.has(route);

  // ── Predictive route preloading (kept for parity — harmless in an MPA) ──
  useNavigationPredictor(route);

  // FlyonUI — reinitialize interactive components after the island mounts.
  useEffect(() => {
    const timer = setTimeout(() => {
      (
        window as unknown as {
          HSStaticMethods?: { autoInit: () => void };
        }
      ).HSStaticMethods?.autoInit();
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Global keyboard shortcuts — navigate between pages with single keys.
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input/textarea
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        e.target instanceof HTMLSelectElement
      )
        return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      switch (e.key.toLowerCase()) {
        case 'g':
          e.preventDefault();
          window.location.assign('/dashboard');
          break;
        case 's':
          if (!e.shiftKey) {
            e.preventDefault();
            window.location.assign('/sale');
          }
          break;
        case 't':
          if (!e.shiftKey) {
            e.preventDefault();
            toggleMode();
          }
          break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleMode]);

  // Remove the pre-island branded splash once React has mounted.
  useEffect(() => {
    document.getElementById('formint-splash')?.remove();
  }, []);

  // Redirects (full page loads, MPA style).
  useEffect(() => {
    if (redirectRoot) window.location.replace('/dashboard');
  }, [redirectRoot]);
  useEffect(() => {
    if (employeeBlocked) window.location.replace('/dashboard');
  }, [employeeBlocked]);

  // KDS popout — dedicated kitchen display window, no chrome, no auth gate.
  if (isKdsPopout) {
    return (
      <div className="relative min-h-[100dvh] bg-base-100">
        <Suspense fallback={<BrandLoader variant="dark" />}>
          <KitchenDisplay standalone />
        </Suspense>
      </div>
    );
  }

  // If auth is still being checked, show the branded loading screen.
  if (isAuthRequired === null) {
    return <BrandLoader variant="dark" />;
  }

  // Auth guard: if auth is required and the user is not authenticated, show Auth.
  if (isAuthRequired && !isAuthenticated) {
    return (
      <div className="relative min-h-[100dvh] bg-base-100">
        <Auth />
      </div>
    );
  }

  // Root route with a live session → dashboard; employee on a restricted page.
  if (redirectRoot || employeeBlocked) {
    return <BrandLoader variant="dark" />;
  }

  const Page = ROUTE_PAGES[route];

  return (
    <div className="relative min-h-[100dvh] bg-base-100">
      <Suspense fallback={<BrandLoader />}>
        {Page ? <Page /> : <BrandLoader />}
      </Suspense>
      {/* Global floating chat widget — visible on all authenticated pages */}
      <ChatSupport />
      {/* Global scroll-to-top button — bottom-right corner (left of the chat FAB) */}
      <ScrollToTopButton />
    </div>
  );
}

/**
 * Astro mounts this component as the single client-only React island. Keep
 * every app-wide provider inside that island so pages and shared chrome use
 * the same auth, theme, language, currency, and modal state.
 */
export default function AppShell({ route }: { route: string }) {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <CurrencyProvider>
          <AuthProvider>
            <ModalProvider>
              <AppShellContent route={route} />
            </ModalProvider>
          </AuthProvider>
        </CurrencyProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}
