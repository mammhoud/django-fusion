import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { useEffect, Suspense, lazy } from 'react';
import Auth from './pages/auth/Auth';
import ChatSupport from './components/pos/ChatSupport';
import { useAuth } from './contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';
import { useNavigationPredictor } from './hooks/useNavigationPredictor';
import { ROLE_ROUTES } from './components/layout/SideNav';

// ── Lazy-loaded pages (code-split by route) ──
// These chunks load on first navigation, not on initial page load.
// The largest pages (Reports: 2438 lines, Settings: 1841, Transactions: 1642,
// Sale: 1551) are the biggest beneficiaries — they bundle heavy deps like
// Recharts, jsPDF, and Excel export utilities only when visited.
const Home = lazy(() => import('./pages/dashboard/Home'));
const ProductManager = lazy(() => import('./pages/pos/ProductManager'));
const Sale = lazy(() => import('./pages/pos/Sale'));
const Analytics = lazy(() => import('./pages/analytics/Analytics'));
const Transactions = lazy(() => import('./pages/pos/Transactions'));
const Inventory = lazy(() => import('./pages/kitchen/Inventory'));
const Employees = lazy(() => import('./pages/admin/Employees'));
const Recipes = lazy(() => import('./pages/kitchen/Recipes'));
const Reports = lazy(() => import('./pages/analytics/Reports'));
const Settings = lazy(() => import('./pages/admin/Settings'));
const About = lazy(() => import('./pages/admin/About'));
const Customers = lazy(() => import('./pages/customers/Customers'));
const Suppliers = lazy(() => import('./pages/customers/Suppliers'));
const KitchenDisplay = lazy(() => import('./pages/kitchen/KitchenDisplay'));
const EmployeeSchedule = lazy(() => import('./pages/admin/EmployeeSchedule'));
const Payroll = lazy(() => import('./pages/admin/Payroll'));
const Notes = lazy(() => import('./pages/admin/Notes'));
const Coupons = lazy(() => import('./pages/admin/Coupons'));
const Roles = lazy(() => import('./pages/admin/Roles'));
const SupportChat = lazy(() => import('./pages/admin/SupportChat'));
// const ThemeShowcase = lazy(() => import('./pages/ThemeShowcase')); // merged into ThemePreviewModal (Settings > Theme)
const StaffPage = lazy(() => import('./pages/admin/StaffPage'));
const ProductsPage = lazy(() => import('./pages/pos/ProductsPage'));

// ── Employee-accessible routes (shared with SideNav filtering) ──
const EMPLOYEE_ROUTES = ROLE_ROUTES.employee;

// FlyonUI — reinitialize interactive components after route changes
// The module is already loaded via static import in main.tsx — this just
// triggers autoInit on new DOM elements after navigation
async function reinitFlyonUI() {
  await import('flyonui/flyonui');
  setTimeout(() => window.HSStaticMethods?.autoInit(), 100);
}

// Page-level transitions removed — only component-level animations remain.
// Individual components use FlyonUI's built-in animation classes
// (animate-scale-in, animate-fade-in, etc.) for micro-interactions.

function AnimatedRoutes() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, isAuthRequired, user } = useAuth();
  const { toggleMode } = useTheme();

  // ── Predictive route preloading — preload the most-likely next page chunk
  //     based on the user's navigation history patterns ──
  useNavigationPredictor(location.pathname);

  // FlyonUI — reinitialize interactive components (modals, dropdowns, toggles)
  // on every route change so new DOM elements get bound properly
  useEffect(() => {
    reinitFlyonUI();
  }, [location.pathname]);

  // Global keyboard shortcuts — navigate between pages with single keys
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input/textarea
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      switch (e.key.toLowerCase()) {
        case 'g':
          e.preventDefault();
          navigate('/dashboard');
          break;
        case 's':
          if (!e.shiftKey) {
            e.preventDefault();
            navigate('/sale');
          }
          break;
        case 't':
          if (!e.shiftKey) {
            e.preventDefault();
            toggleMode();
          }
          break;
        case '?':
          e.preventDefault();
          // Dispatch a custom event that the SideNav's shortcut modal listens for,
          // or just navigate to the current page (the individual page handlers
          // for '?' are already in place).
          // Nothing to do globally — each page handles '?' via its own listener.
          break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate, toggleMode]);



  // ── Suspense fallback shown while lazy chunks load ──
  const PageFallback = (
    <div className="min-h-[100dvh] flex items-center justify-center bg-base-100">
      <div className="text-center">
        <span className="loading loading-spinner loading-lg text-primary" />
        <p className="text-sm text-base-content/50 mt-3">Loading...</p>
        <div className="flex items-center justify-center gap-1 mt-6">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );

  // If auth is still being checked, show a loading screen
  if (isAuthRequired === null) {
    return (
      <div className="min-h-[100dvh] bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Auth guard: if auth is required and user is not authenticated, show Auth
  if (isAuthRequired && !isAuthenticated) {
    return <Auth />;
  }

  // Route guard: restrict employee access to certain pages
  if (user?.role === 'employee' && !EMPLOYEE_ROUTES.has(location.pathname)) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="relative min-h-[100dvh] bg-base-100">
      <Suspense fallback={PageFallback}>
        <Routes location={location} key={location.pathname}>
          {/* Root route: Auth/Login is the first page for unauthenticated users */}
          <Route path="/" element={
            !isAuthenticated ? <Auth /> : <Navigate to="/dashboard" replace />
          } />
          <Route path="/dashboard" element={<Home />} />
          <Route path="/manager" element={<ProductManager />} />
          <Route path="/sale" element={<Sale />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/employees" element={<Employees />} />
          <Route path="/recipes" element={<Recipes />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/about" element={<About />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/suppliers" element={<Suppliers />} />
          <Route path="/kitchen" element={<KitchenDisplay />} />
          <Route path="/schedule" element={<EmployeeSchedule />} />
          <Route path="/payroll" element={<Payroll />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/coupons" element={<Coupons />} />
          <Route path="/tax-reports" element={<Navigate to="/reports?tab=taxReports" replace />} />
          <Route path="/roles" element={<Roles />} />
          <Route path="/support-chat" element={<SupportChat />} />
          <Route path="/staff" element={<StaffPage />} />
          <Route path="/products" element={<ProductsPage />} />
        </Routes>
      </Suspense>
      {/* Global floating chat widget — visible on all authenticated pages */}
      <ChatSupport />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AnimatedRoutes />
    </Router>
  );
}

export default App;
