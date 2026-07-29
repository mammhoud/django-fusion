import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { useEffect, Suspense, lazy, useState } from 'react';
import Auth from './pages/Auth';
import ChatSupport from './components/ChatSupport';
import { useAuth } from './contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';
import { useNavigationPredictor } from './hooks/useNavigationPredictor';

// ── Lazy-loaded pages (code-split by route) ──
// These chunks load on first navigation, not on initial page load.
// The largest pages (Reports: 2438 lines, Settings: 1841, Transactions: 1642,
// Sale: 1551) are the biggest beneficiaries — they bundle heavy deps like
// Recharts, jsPDF, and Excel export utilities only when visited.
const Home = lazy(() => import('./pages/Home'));
const ProductManager = lazy(() => import('./pages/ProductManager'));
const Sale = lazy(() => import('./pages/Sale'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Transactions = lazy(() => import('./pages/Transactions'));
const Inventory = lazy(() => import('./pages/Inventory'));
const Employees = lazy(() => import('./pages/Employees'));
const Recipes = lazy(() => import('./pages/Recipes'));
const Reports = lazy(() => import('./pages/Reports'));
const Settings = lazy(() => import('./pages/Settings'));
const About = lazy(() => import('./pages/About'));
const Customers = lazy(() => import('./pages/Customers'));
const Suppliers = lazy(() => import('./pages/Suppliers'));
const KitchenDisplay = lazy(() => import('./pages/KitchenDisplay'));
const EmployeeSchedule = lazy(() => import('./pages/EmployeeSchedule'));
const Payroll = lazy(() => import('./pages/Payroll'));
const ReceiptTemplates = lazy(() => import('./pages/ReceiptTemplates'));
const TaxReports = lazy(() => import('./pages/TaxReports'));
const Roles = lazy(() => import('./pages/Roles'));
const SupportChat = lazy(() => import('./pages/SupportChat'));
const InvoicePage = lazy(() => import('./pages/InvoicePage'));
const ThemeShowcase = lazy(() => import('./pages/ThemeShowcase'));
const ThemeStudio = lazy(() => import('./pages/ThemeStudio'));
const StaffPage = lazy(() => import('./pages/StaffPage'));
const ProductsPage = lazy(() => import('./pages/ProductsPage'));

// FlyonUI — reinitialize interactive components after route changes
// The module is already loaded via static import in main.tsx — this just
// triggers autoInit on new DOM elements after navigation
async function reinitFlyonUI() {
  await import('flyonui/flyonui');
  setTimeout(() => window.HSStaticMethods?.autoInit(), 100);
}

// Route transitions are handled by the AnimatePresence + motion.div
// inside PageLayout. Each page inherits a consistent fade+slide-up entrance
// via the shared pageSlideUp variant from utils/pageTransitions.ts.

function AnimatedRoutes() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, isAuthRequired } = useAuth();
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
    <div className="min-h-screen flex items-center justify-center bg-base-100">
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
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-teal-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Auth guard: if auth is required and user is not authenticated, show Auth
  if (isAuthRequired && !isAuthenticated) {
    return <Auth />;
  }

  return (
    <div className="relative min-h-screen bg-base-100">
      <Suspense fallback={PageFallback}>
        <Routes location={location} key={location.pathname}>
          {/* Root route: show Auth if not authenticated, otherwise redirect to dashboard */}
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
          <Route path="/receipt-templates" element={<ReceiptTemplates />} />
          <Route path="/tax-reports" element={<TaxReports />} />
          <Route path="/roles" element={<Roles />} />
          <Route path="/support-chat" element={<SupportChat />} />
          <Route path="/invoice" element={<InvoicePage />} />
          <Route path="/theme-showcase" element={<ThemeShowcase />} />
          <Route path="/theme-studio" element={<ThemeStudio />} />
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
