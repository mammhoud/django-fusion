import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { MdClose, MdPointOfSale, MdLogout, MdHelpOutline, MdPeople, MdLocalShipping, MdKitchen, MdEvent, MdReceiptLong, MdAccountBalance, MdSecurity, MdPushPin } from 'react-icons/md';
import {
  FaClipboardList, FaChartBar, FaHistory, FaBoxes, FaUsers,
  FaMortarPestle, FaFileAlt, FaCog, FaHeart, FaHome, FaMoneyBillWave,
  FaComments, FaFileInvoiceDollar
} from 'react-icons/fa';
import ThemeToggle from './ThemeToggle';
import LanguageToggle from './LanguageToggle';
import KeyboardShortcutsModal from './KeyboardShortcutsModal';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useTranslation } from 'react-i18next';

interface NavItem {
  label: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  gradient: string;
}

const navItems: NavItem[] = [
  { label: 'nav.home', route: '/', icon: FaHome, gradient: 'from-teal-400 to-teal-500' },
  { label: 'nav.productManager', route: '/manager', icon: FaClipboardList, gradient: 'from-blue-400 to-blue-500' },
  { label: 'nav.newSale', route: '/sale', icon: MdPointOfSale, gradient: 'from-green-400 to-green-500' },
  { label: 'nav.analytics', route: '/analytics', icon: FaChartBar, gradient: 'from-purple-400 to-purple-500' },
  { label: 'nav.transactions', route: '/transactions', icon: FaHistory, gradient: 'from-orange-400 to-orange-500' },
  { label: 'nav.inventory', route: '/inventory', icon: FaBoxes, gradient: 'from-emerald-400 to-emerald-500' },
  { label: 'nav.employees', route: '/employees', icon: FaUsers, gradient: 'from-indigo-400 to-indigo-500' },
  { label: 'nav.recipes', route: '/recipes', icon: FaMortarPestle, gradient: 'from-orange-400 to-orange-500' },
  { label: 'nav.reports', route: '/reports', icon: FaFileAlt, gradient: 'from-rose-400 to-rose-500' },
  { label: 'nav.customers', route: '/customers', icon: MdPeople, gradient: 'from-cyan-400 to-cyan-500' },
  { label: 'nav.suppliers', route: '/suppliers', icon: MdLocalShipping, gradient: 'from-amber-400 to-amber-500' },
  { label: 'nav.kitchen', route: '/kitchen', icon: MdKitchen, gradient: 'from-orange-400 to-orange-500' },
  { label: 'nav.schedule', route: '/schedule', icon: MdEvent, gradient: 'from-violet-400 to-violet-500' },
  { label: 'nav.payroll', route: '/payroll', icon: FaMoneyBillWave, gradient: 'from-emerald-400 to-emerald-500' },
  { label: 'nav.receiptTemplates', route: '/receipt-templates', icon: MdReceiptLong, gradient: 'from-lime-400 to-lime-500' },
  { label: 'nav.invoice', route: '/invoice', icon: FaFileInvoiceDollar, gradient: 'from-teal-400 to-teal-500' },
  { label: 'nav.taxReports', route: '/tax-reports', icon: MdAccountBalance, gradient: 'from-indigo-400 to-indigo-500' },
  { label: 'nav.roles', route: '/roles', icon: MdSecurity, gradient: 'from-red-400 to-red-500' },
  { label: 'nav.supportChat', route: '/support-chat', icon: FaComments, gradient: 'from-cyan-400 to-cyan-500' },
  { label: 'nav.settings', route: '/settings', icon: FaCog, gradient: 'from-gray-400 to-gray-500' },
  { label: 'nav.about', route: '/about', icon: FaHeart, gradient: 'from-pink-400 to-pink-500' },
];

interface SideNavProps {
  isOpen?: boolean;
  onClose?: () => void;
  currentRoute: string;
  persistent?: boolean;
}

// ── Persistent (hover-expand) sidebar for ultra-wide screens ──

function PersistentSidebar({ currentRoute }: { currentRoute: string }) {
  const navigate = useNavigate();
  const { isAuthRequired, logout } = useAuth();
  const { language } = useLanguage();
  const { t } = useTranslation();
  const isRtl = language === 'ar';
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);

  const expanded = isHovered || isPinned;

  const handleNavigate = (route: string) => {
    navigate(route);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      <motion.aside
        className="fixed left-0 top-0 h-full z-30
          bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl
          border-r border-slate-200 dark:border-white/10
          shadow-xl flex flex-col overflow-hidden
          hidden 4xl:flex
          rtl:left-auto rtl:right-0 rtl:border-r-0 rtl:border-l"
        animate={{ width: expanded ? 280 : 64 }}
        transition={{ type: 'spring', stiffness: 300, damping: 28 }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => { if (!isPinned) setIsHovered(false); }}
      >
        {/* Header — navigation label (only when expanded) + pin toggle */}
        <div className="flex items-center justify-end p-3 border-b border-slate-200 dark:border-white/10 min-h-[52px]">
          {expanded && (
            <span className="text-xs font-semibold text-slate-500 dark:text-white/50 uppercase tracking-wider flex-1 truncate pl-0.5">
              {t('nav.navigation')}
            </span>
          )}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsPinned(!isPinned)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white
              hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
            title={isPinned ? 'Unpin sidebar' : 'Pin sidebar'}
          >
            <MdPushPin className={`w-4 h-4 transition-transform duration-200 ${isPinned ? 'rotate-45 text-teal-500' : ''}`} />
          </motion.button>
        </div>

        {/* Nav items */}
        <nav className="p-2 space-y-0.5 flex-1 overflow-y-auto overflow-x-hidden">
          {navItems.map((item) => {
            const isActive = currentRoute === item.route;
            const Icon = item.icon;

            return (
              <motion.button
                key={item.route}
                whileHover={{ x: expanded ? (isRtl ? -4 : 4) : 0 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigate(item.route)}
                className={`w-full flex items-center gap-3 px-2.5 py-2.5 rounded-xl text-sm
                  transition-all duration-200 group whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-100 dark:bg-white/10 text-slate-900 dark:text-white font-semibold shadow-sm'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5 font-medium'
                }`}
                title={!expanded ? t(item.label) : undefined}
              >
                <div className={`w-8 h-8 min-w-[2rem] rounded-lg flex items-center justify-center text-white text-sm
                  bg-linear-to-br ${item.gradient} shadow-sm
                  ${isActive ? 'scale-110' : 'group-hover:scale-105'} transition-transform shrink-0`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <motion.span
                  animate={{ opacity: expanded ? 1 : 0 }}
                  transition={{ duration: 0.12 }}
                  className="overflow-hidden truncate text-left"
                >
                  {t(item.label)}
                </motion.span>
                {isActive && expanded && (
                  <motion.div
                    layoutId="sidenav-persistent-active"
                    className="ml-auto rtl:mr-auto rtl:ml-0 w-1.5 h-1.5 rounded-full bg-teal-500 shrink-0"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </motion.button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-slate-200 dark:border-white/10 mt-auto">
          {/* Logout */}
          {isAuthRequired && (
            <motion.button
              onClick={handleLogout}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="w-full flex items-center justify-center gap-2 px-2 py-2 mb-2
                bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400
                rounded-xl text-sm font-medium transition-colors"
              title={!expanded ? t('auth.signOut') : undefined}
            >
              <MdLogout className="w-4 h-4 shrink-0" />
              <motion.span
                animate={{ opacity: expanded ? 1 : 0 }}
                transition={{ duration: 0.12 }}
                className="overflow-hidden truncate"
              >
                {expanded && t('auth.signOut')}
              </motion.span>
            </motion.button>
          )}

          {/* Keyboard Shortcuts */}
          <motion.button
            onClick={() => setShowShortcuts(true)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="w-full flex items-center justify-center gap-2 px-2 py-2 mb-2
              bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10
              text-slate-600 dark:text-slate-300 rounded-xl text-sm font-medium transition-colors"
            title={!expanded ? t('transactions.shortcutHelp') : undefined}
          >
            <MdHelpOutline className="w-4 h-4 shrink-0" />
            <motion.span
              animate={{ opacity: expanded ? 1 : 0 }}
              transition={{ duration: 0.12 }}
              className="overflow-hidden truncate flex items-center gap-1"
            >
              {expanded && <>{t('transactions.shortcutHelp')} <kbd className="px-1 py-0.5 text-[10px] font-mono rounded bg-slate-200 dark:bg-white/10">?</kbd></>}
            </motion.span>
          </motion.button>

          {/* Toggles */}
          <div className="flex items-center justify-center gap-3 mb-1">
            <LanguageToggle />
          </div>
          <div className="flex items-center justify-center mb-1">
            <ThemeToggle />
          </div>

          {expanded && (
            <p className="text-[10px] text-slate-400 dark:text-white/30 text-center mt-2">
              {t('nav.footer')}
            </p>
          )}
        </div>
      </motion.aside>

      <KeyboardShortcutsModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
    </>
  );
}

export default function SideNav({ isOpen = false, onClose = () => {}, currentRoute, persistent = false }: SideNavProps) {
  if (persistent) {
    return <PersistentSidebar currentRoute={currentRoute} />;
  }
  const navigate = useNavigate();
  const { isAuthRequired, logout } = useAuth();
  const { language } = useLanguage();
  const { t } = useTranslation();
  const isRtl = language === 'ar';
  const [showShortcuts, setShowShortcuts] = useState(false);

  const handleNavigate = (route: string) => {
    onClose();
    navigate(route);
  };

  const handleLogout = () => {
    onClose();
    logout();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            key="sidenav-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.aside
            key="sidenav-panel"
            initial={{ x: isRtl ? '100%' : '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: isRtl ? '100%' : '-100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed top-0 left-0 h-full w-72 max-w-[85vw] z-50
              bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl
              border-r border-slate-200 dark:border-white/10
              shadow-2xl flex flex-col
              rtl:left-auto rtl:right-0 rtl:border-r-0 rtl:border-l"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-white/10">
              <span className="text-sm font-semibold text-slate-500 dark:text-white/50 uppercase tracking-wider">
                {t('nav.navigation')}
              </span>
              <motion.button
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-1.5 rounded-lg text-slate-500 dark:text-white/60 hover:text-slate-900 dark:hover:text-white
                  hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
              >
                <MdClose className="w-5 h-5" />
              </motion.button>
            </div>

            {/* Nav Items — flex-1 to push footer down */}
            <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
              {navItems.map((item, index) => {
                const isActive = currentRoute === item.route;
                const Icon = item.icon;

                return (
                  <motion.button
                    key={item.route}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    whileHover={{ x: isRtl ? -4 : 4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleNavigate(item.route)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
                      transition-all duration-200 group ${
                      isActive
                        ? 'bg-slate-100 dark:bg-white/10 text-slate-900 dark:text-white font-semibold shadow-sm'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5 font-medium'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm
                      bg-linear-to-br ${item.gradient} shadow-sm shrink-0
                      ${isActive ? 'scale-110' : 'group-hover:scale-105'} transition-transform`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="truncate">{t(item.label)}</span>
                    {isActive && (
                      <motion.div
                        layoutId="sidenav-active"
                        className="ml-auto rtl:mr-auto rtl:ml-0 w-1.5 h-1.5 rounded-full bg-teal-500"
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      />
                    )}
                  </motion.button>
                );
              })}
            </nav>

            {/* Footer — toggles and logout at the bottom */}
            <div className="p-4 border-t border-slate-200 dark:border-white/10 mt-auto">
              {isAuthRequired && (
                <motion.button
                  onClick={handleLogout}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.97 }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 mb-3 
                    bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 
                    rounded-xl text-sm font-medium transition-colors 
                    border border-red-200 dark:border-red-800/30"
                >
                  <MdLogout className="w-4 h-4" />
                  {t('auth.signOut')}
                </motion.button>
              )}
              {/* Keyboard Shortcuts */}
              <motion.button
                onClick={() => setShowShortcuts(true)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 mb-3
                  bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10
                  text-slate-600 dark:text-slate-300 rounded-xl text-sm font-medium transition-colors
                  border border-slate-200 dark:border-white/10"
              >
                <MdHelpOutline className="w-4 h-4" />
                <span>{t('transactions.shortcutHelp')}</span>
                <kbd className="ml-1 px-1.5 py-0.5 text-[10px] font-mono rounded
                  bg-slate-200 dark:bg-white/10 text-slate-500 dark:text-slate-400">
                  ?
                </kbd>
              </motion.button>

              {/* Toggles */}
              <div className="flex items-center justify-center gap-4 mb-2">
                <LanguageToggle />
              </div>
              <div className="flex items-center justify-center mb-2">
                <ThemeToggle />
              </div>
              <p className="text-[10px] text-slate-400 dark:text-white/30 text-center mt-3">
                {t('nav.footer')}
              </p>
            </div>

            <KeyboardShortcutsModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
