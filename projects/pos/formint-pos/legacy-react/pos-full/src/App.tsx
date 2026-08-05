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
import Notes from './pages/Notes';
import SupportChat from './pages/SupportChat';
import InvoicePage from './pages/InvoicePage';
import ChatSupport from './components/ChatSupport';
import { useAuth } from './contexts/AuthContext';

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
  '/notes': 21,
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
  const [direction, setDirection] = useState(1);
  const prevPathRef = useRef(location.pathname);
  const { isAuthenticated, isAuthRequired } = useAuth();
  const isFirstRender = useRef(true);

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
          <Route path="/notes" element={<PageWrapper direction={direction} isFirstRender={isFirstRender.current}><Notes /></PageWrapper>} />
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
