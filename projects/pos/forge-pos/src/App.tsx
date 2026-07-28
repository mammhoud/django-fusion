import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { useState, useEffect, useRef } from 'react';
import Home from './pages/Home';
import ProductManager from './pages/ProductManager';
import Sale from './pages/Sale';
import Analytics from './pages/Analytics';
import Transactions from './pages/Transactions';
import Inventory from './pages/Inventory';
import Employees from './pages/Employees';
import Recipes from './pages/Recipes';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import About from './pages/About';
import Auth from './pages/Auth';
import Customers from './pages/Customers';
import Suppliers from './pages/Suppliers';
import KitchenDisplay from './pages/KitchenDisplay';
import EmployeeSchedule from './pages/EmployeeSchedule';
import Payroll from './pages/Payroll';
import ReceiptTemplates from './pages/ReceiptTemplates';
import TaxReports from './pages/TaxReports';
import Roles from './pages/Roles';
import SupportChat from './pages/SupportChat';
import InvoicePage from './pages/InvoicePage';
import ThemeShowcase from './pages/ThemeShowcase';
import ThemeStudio from './pages/ThemeStudio';
import StaffPage from './pages/StaffPage';
import ProductsPage from './pages/ProductsPage';
import ChatSupport from './components/ChatSupport';
import { useAuth } from './contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useTheme } from './contexts/ThemeContext';

// FlyonUI — reinitialize interactive components after route changes
// The module is already loaded via static import in main.tsx — this just
// triggers autoInit on new DOM elements after navigation
async function reinitFlyonUI() {
  await import('flyonui/flyonui');
  setTimeout(() => window.HSStaticMethods?.autoInit(), 100);
}

// Route ordering for direction-aware transitions
const routeOrder: Record<string, number> = {
  '/': 0,
  '/manager': 1,
  '/sale': 2,
  '/analytics': 3,
  '/transactions': 4,
  '/inventory': 5,
  '/employees': 6,
  '/recipes': 7,
  '/reports': 8,
  '/settings': 9,
  '/about': 10,
  '/customers': 11,
  '/suppliers': 12,
  '/kitchen': 13,
  '/schedule': 14,
  '/payroll': 15,
  '/receipt-templates': 16,
  '/tax-reports': 17,
  '/roles': 18,
  '/support-chat': 19,
  '/invoice': 20,
  '/theme-showcase': 21,
  '/theme-studio': 22,
  '/staff': 23,
  '/products': 24,
};

function PageWrapper({ children, direction, isFirstRender }: { children: React.ReactNode; direction: number; isFirstRender: boolean }) {
  return (
    <motion.div
      custom={direction}
      variants={{
        initial: (dir: number) => ({
          opacity: isFirstRender ? 1 : 0,
          x: isFirstRender ? 0 : dir > 0 ? 40 : -40,
          scale: isFirstRender ? 1 : 0.97,
        }),
        animate: {
          opacity: 1,
          x: 0,
          scale: 1,
        },
        exit: (dir: number) => ({
          opacity: 0,
          x: dir > 0 ? -40 : 40,
          scale: 0.97,
        }),
      }}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{
        x: { type: 'spring', stiffness: 300, damping: 30 },
        opacity: { duration: 0.25 },
        scale: { duration: 0.25 },
      }}
      style={{ position: 'absolute', inset: 0, overflowY: 'auto' }}
    >
      {children}
    </motion.div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  const navigate = useNavigate();
  const [direction, setDirection] = useState(1);
  const prevPathRef = useRef(location.pathname);
  const { isAuthenticated, isAuthRequired } = useAuth();
  const { toggleMode } = useTheme();
  const isFirstRender = useRef(true);
  // Always show Auth first on every app launch as the landing page
  // Once the user authenticates, the splash auto-dismisses
  const [showAuthSplash, setShowAuthSplash] = useState(true);

  useEffect(() => {
    isFirstRender.current = false;
  }, []);

  // Track direction for page transitions (MUST be before early returns per React hooks rules)
  useEffect(() => {
    const prev = prevPathRef.current;
    const curr = location.pathname;
    if (prev !== curr) {
      const prevIdx = routeOrder[prev] ?? 0;
      const currIdx = routeOrder[curr] ?? 0;
      setDirection(currIdx > prevIdx ? 1 : -1);
      prevPathRef.current = curr;
    }
  }, [location.pathname]);

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
          navigate('/');
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

  // Auto-dismiss splash when user authenticates (or skips auth)
  useEffect(() => {
    if (showAuthSplash && isAuthenticated) {
      setShowAuthSplash(false);
    }
    if (showAuthSplash && isAuthRequired === false) {
      // Auth not required at all — dismiss splash
      setShowAuthSplash(false);
    }
  }, [showAuthSplash, isAuthenticated, isAuthRequired]);

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

  // Always show Auth first as the landing/splash page
  if (showAuthSplash) {
    return <Auth />;
  }

  // If auth is required but user is not authenticated, show the Auth page
  if (isAuthRequired && !isAuthenticated) {
    return <Auth />;
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-900">
      <AnimatePresence mode="popLayout" initial={false}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Home /></PageWrapper>} />
          <Route path="/manager" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><ProductManager /></PageWrapper>} />
          <Route path="/sale" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Sale /></PageWrapper>} />
          <Route path="/analytics" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Analytics /></PageWrapper>} />
          <Route path="/transactions" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Transactions /></PageWrapper>} />
          <Route path="/inventory" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Inventory /></PageWrapper>} />
          <Route path="/employees" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Employees /></PageWrapper>} />
          <Route path="/recipes" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Recipes /></PageWrapper>} />
          <Route path="/reports" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Reports /></PageWrapper>} />
          <Route path="/settings" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Settings /></PageWrapper>} />
          <Route path="/about" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><About /></PageWrapper>} />
          <Route path="/customers" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Customers /></PageWrapper>} />
          <Route path="/suppliers" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Suppliers /></PageWrapper>} />
          <Route path="/kitchen" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><KitchenDisplay /></PageWrapper>} />
          <Route path="/schedule" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><EmployeeSchedule /></PageWrapper>} />
          <Route path="/payroll" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Payroll /></PageWrapper>} />
          <Route path="/receipt-templates" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><ReceiptTemplates /></PageWrapper>} />
          <Route path="/tax-reports" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><TaxReports /></PageWrapper>} />
          <Route path="/roles" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Roles /></PageWrapper>} />
          <Route path="/support-chat" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><SupportChat /></PageWrapper>} />
          <Route path="/invoice" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><InvoicePage /></PageWrapper>} />
          <Route path="/theme-showcase" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><ThemeShowcase /></PageWrapper>} />
          <Route path="/theme-studio" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><ThemeStudio /></PageWrapper>} />
          <Route path="/staff" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><StaffPage /></PageWrapper>} />
          <Route path="/products" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><ProductsPage /></PageWrapper>} />
        </Routes>
      </AnimatePresence>
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
