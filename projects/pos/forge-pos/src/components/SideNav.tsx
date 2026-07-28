import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState, useRef } from 'react';
// ── Icons use Tabler icon CSS classes via icon-[tabler--*] ──
function Ic(name: string): React.ComponentType<{ className?: string }> {
  return ({ className = '' }) => <span className={`icon-[tabler--${name}] ${className}`} />;
}
import ThemeToggle from './ThemeToggle';
import LanguageToggle from './LanguageToggle';
import KeyboardShortcutsModal from './KeyboardShortcutsModal';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useTranslation } from 'react-i18next';

// ── Category definitions with section headers ──
interface NavItem {
  label: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  gradient: string;
}

interface NavCategory {
  id: string;
  label: string;
  icon: string;
  items: NavItem[];
}

const navCategories: NavCategory[] = [
  {
    id: 'sales',
    label: 'nav.sales',
    icon: 'shopping-cart',
    items: [
      { label: 'nav.newSale', route: '/sale', icon: Ic('shopping-cart'), gradient: 'from-emerald-400 to-emerald-500' },
      { label: 'nav.kitchen', route: '/kitchen', icon: Ic('tools-kitchen-2'), gradient: 'from-teal-400 to-teal-500' },
      { label: 'nav.transactions', route: '/transactions', icon: Ic('history'), gradient: 'from-cyan-400 to-cyan-500' },
      { label: 'nav.invoice', route: '/invoice', icon: Ic('file-invoice'), gradient: 'from-sky-400 to-sky-500' },
    ],
  },    {
    id: 'products',
    label: 'nav.products',
    icon: 'package',
    items: [
      { label: 'nav.productsMerged', route: '/products', icon: Ic('apps'), gradient: 'from-blue-400 to-blue-500' },
      { label: 'nav.productManager', route: '/manager', icon: Ic('clipboard-list'), gradient: 'from-indigo-400 to-indigo-500' },
      { label: 'nav.inventory', route: '/inventory', icon: Ic('package'), gradient: 'from-violet-400 to-violet-500' },
      { label: 'nav.recipes', route: '/recipes', icon: Ic('flask'), gradient: 'from-purple-400 to-purple-500' },
      { label: 'nav.suppliers', route: '/suppliers', icon: Ic('truck'), gradient: 'from-pink-400 to-pink-500' },
    ],
  },
  {
    id: 'staff',
    label: 'nav.staff',
    icon: 'users',
    items: [
      { label: 'nav.employees', route: '/employees', icon: Ic('users'), gradient: 'from-fuchsia-400 to-fuchsia-500' },
      { label: 'nav.schedule', route: '/schedule', icon: Ic('calendar-event'), gradient: 'from-pink-400 to-pink-500' },
      { label: 'nav.payroll', route: '/payroll', icon: Ic('moneybag'), gradient: 'from-rose-400 to-rose-500' },
      { label: 'nav.customers', route: '/customers', icon: Ic('users'), gradient: 'from-orange-400 to-orange-500' },
      { label: 'nav.roles', route: '/roles', icon: Ic('shield'), gradient: 'from-red-400 to-red-500' },
    ],
  },
  {
    id: 'reports',
    label: 'nav.reports',
    icon: 'chart-bar',
    items: [
      { label: 'nav.analytics', route: '/analytics', icon: Ic('chart-bar'), gradient: 'from-amber-400 to-amber-500' },
      { label: 'nav.reports', route: '/reports', icon: Ic('file-text'), gradient: 'from-yellow-400 to-yellow-500' },
      { label: 'nav.taxReports', route: '/tax-reports', icon: Ic('building-bank'), gradient: 'from-lime-400 to-lime-500' },
    ],
  },
  {
    id: 'system',
    label: 'nav.system',
    icon: 'dashboard',
    items: [
      { label: 'nav.settings', route: '/settings', icon: Ic('settings'), gradient: 'from-slate-400 to-slate-500' },
      { label: 'nav.receiptTemplates', route: '/receipt-templates', icon: Ic('receipt'), gradient: 'from-stone-400 to-stone-500' },
      { label: 'nav.supportChat', route: '/support-chat', icon: Ic('messages'), gradient: 'from-green-400 to-green-500' },
      { label: 'nav.themeShowcase', route: '/theme-showcase', icon: Ic('palette'), gradient: 'from-indigo-400 to-indigo-500' },
      { label: 'nav.themeStudio', route: '/theme-studio', icon: Ic('paint'), gradient: 'from-purple-400 to-purple-500' },
      { label: 'nav.about', route: '/about', icon: Ic('heart'), gradient: 'from-rose-400 to-rose-500' },
    ],
  },
];

interface SideNavProps {
  isOpen?: boolean;
  onClose?: () => void;
  currentRoute: string;
  persistent?: boolean;
}

// ── Category Section Header (clickable for jump/expand) ──
function CategoryHeader({
  category,
  isExpanded,
  isClickable,
  onClick,
}: {
  category: NavCategory;
  isExpanded: boolean;
  isClickable?: boolean;
  onClick?: () => void;
}) {
  const content = (
    <div className="flex items-center gap-2 px-2.5 py-2 mt-1 first:mt-0 w-full">
      <span className={`icon-[tabler--${category.icon}] w-3.5 h-3.5 text-base-content/40 shrink-0`} />
      {isExpanded && (
        <span className="text-[10px] font-semibold uppercase tracking-wider text-base-content/40 truncate">
          {category.label}
        </span>
      )}
    </div>
  );

  if (isClickable && onClick) {
    return (
      <motion.button
        type="button"
        onClick={onClick}
        whileHover={{ x: 2 }}
        whileTap={{ scale: 0.97 }}
        className="w-full text-left cursor-pointer hover:bg-base-200/30 rounded-xl transition-colors"
      >
        {content}
      </motion.button>
    );
  }

  return content;
}

// ── Nav Item Button ──
function NavItemButton({
  item,
  isActive,
  isExpanded,
  isRtl,
  onClick,
}: {
  item: NavItem;
  isActive: boolean;
  isExpanded: boolean;
  isRtl: boolean;
  onClick: () => void;
}) {
  const Icon = item.icon;
  return (
    <motion.button
      whileHover={{ x: isExpanded ? (isRtl ? -4 : 4) : 0 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-2.5 py-2 rounded-xl text-sm
        transition-all duration-200 group whitespace-nowrap ${
        isActive
          ? 'bg-base-200/70 dark:bg-white/10 text-base-content font-semibold shadow-sm'
          : 'text-base-content/60 hover:text-base-content hover:bg-base-200/40 dark:hover:bg-white/5 font-medium'
      }`}
      title={!isExpanded ? item.label : undefined}
    >
      <div className={`w-7 h-7 min-w-[1.75rem] rounded-lg flex items-center justify-center text-white text-xs
        bg-linear-to-br ${item.gradient} shadow-sm
        ${isActive ? 'scale-110' : 'group-hover:scale-105'} transition-transform shrink-0`}
      >
        <Icon className="w-3.5 h-3.5" />
      </div>
      <motion.span
        animate={{ opacity: isExpanded ? 1 : 0, width: isExpanded ? 'auto' : 0 }}
        transition={{ duration: 0.12 }}
        className="overflow-hidden truncate text-left"
      >
        {item.label}
      </motion.span>
      {isActive && isExpanded && (
        <motion.div
          layoutId="sidenav-persistent-active"
          className="ml-auto rtl:mr-auto rtl:ml-0 w-1.5 h-1.5 rounded-full bg-primary shrink-0"
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        />
      )}
    </motion.button>
  );
}

// ── Render a category with its items ──
function NavCategorySection({
  category,
  currentRoute,
  isExpanded,
  isRtl,
  onNavigate,
  onHeaderClick,
  isCollapsed,
}: {
  category: NavCategory;
  currentRoute: string;
  isExpanded: boolean;
  isRtl: boolean;
  onNavigate: (route: string) => void;
  onHeaderClick?: () => void;
  isCollapsed?: boolean;
}) {
  const hasActiveItem = category.items.some(item => currentRoute === item.route);

  return (
    <div id={`sidenav-cat-${category.id}`} className={`${hasActiveItem && isExpanded && !isCollapsed ? 'bg-base-200/20 dark:bg-white/[0.02] rounded-xl' : ''}`}>
      <CategoryHeader
        category={category}
        isExpanded={isExpanded}
        isClickable={!!onHeaderClick}
        onClick={onHeaderClick}
      />
      {/* If collapsed, hide items */}
      {!isCollapsed && (
        <div className="space-y-0.5 px-1.5">
          {category.items.map(item => (
            <NavItemButton
              key={item.route}
              item={item}
              isActive={currentRoute === item.route}
              isExpanded={isExpanded}
              isRtl={isRtl}
              onClick={() => onNavigate(item.route)}
            />
          ))}
        </div>
      )}
    </div>
  );
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
  // Track collapsed categories in the persistent sidebar — clicking a category
  // header toggles its visibility, making room for other sections.
  const [collapsedCategories, setCollapsedCategories] = useState<Set<string>>(new Set());

  const toggleCategory = (catId: string) => {
    setCollapsedCategories(prev => {
      const next = new Set(prev);
      if (next.has(catId)) next.delete(catId);
      else next.add(catId);
      return next;
    });
  };

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
          bg-base-100/95 backdrop-blur-xl
          border-r border-base-300/50
          shadow-xl flex flex-col overflow-hidden
          hidden 4xl:flex
          rtl:left-auto rtl:right-0 rtl:border-r-0 rtl:border-l"
        animate={{ width: expanded ? 280 : 64 }}
        transition={{ type: 'spring', stiffness: 300, damping: 28 }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => { if (!isPinned) setIsHovered(false); }}
      >
        {/* Header — logo + pin toggle */}
        <div className="flex items-center justify-end p-3 border-b border-base-300/50 min-h-[52px]">
          {expanded && (
            <span className="text-xs font-semibold text-base-content/50 uppercase tracking-wider flex-1 truncate pl-0.5">
              {t('nav.navigation')}
            </span>
          )}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsPinned(!isPinned)}
            className="p-1.5 rounded-lg text-base-content/40 hover:text-base-content/70
              hover:bg-base-200/50 dark:hover:bg-white/10 transition-colors"
            title={isPinned ? 'Unpin sidebar' : 'Pin sidebar'}
          >
            <span className={`icon-[tabler--pin] w-4 h-4 transition-transform duration-200 ${isPinned ? 'rotate-45 text-primary' : ''}`} />
          </motion.button>
        </div>

        {/* Home button always visible */}
        <div className="px-3 pt-2 pb-1">
          <NavItemButton
            item={{ label: 'nav.home', route: '/', icon: Ic('dashboard'), gradient: 'from-teal-400 to-teal-500' }}
            isActive={currentRoute === '/'}
            isExpanded={expanded}
            isRtl={isRtl}
            onClick={() => handleNavigate('/')}
          />
        </div>

        {/* Nav categories — scrollable */}
        <nav className="px-2 pb-2 space-y-1 flex-1 overflow-y-auto overflow-x-hidden">
          {navCategories.map(cat => (
            <NavCategorySection
              key={cat.id}
              category={cat}
              currentRoute={currentRoute}
              isExpanded={expanded}
              isRtl={isRtl}
              onNavigate={handleNavigate}
              onHeaderClick={() => toggleCategory(cat.id)}
              isCollapsed={collapsedCategories.has(cat.id)}
            />
          ))}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-base-300/50 mt-auto">
          {isAuthRequired && (
            <motion.button
              onClick={handleLogout}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="w-full flex items-center justify-center gap-2 px-2 py-2 mb-2
                bg-error/10 hover:bg-error/20 text-error
                rounded-xl text-sm font-medium transition-colors"
              title={!expanded ? t('auth.signOut') : undefined}
            >
              <span className="icon-[tabler--logout] w-4 h-4 shrink-0" />
              <motion.span
                animate={{ opacity: expanded ? 1 : 0 }}
                transition={{ duration: 0.12 }}
                className="overflow-hidden truncate"
              >
                {expanded && t('auth.signOut')}
              </motion.span>
            </motion.button>
          )}

          <motion.button
            onClick={() => setShowShortcuts(true)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="w-full flex items-center justify-center gap-2 px-2 py-2 mb-2
              bg-base-200/50 dark:bg-white/5 hover:bg-base-200 dark:hover:bg-white/10
              text-base-content/60 rounded-xl text-sm font-medium transition-colors"
            title={!expanded ? t('transactions.shortcutHelp') : undefined}
          >
            <span className="icon-[tabler--help-circle] w-4 h-4 shrink-0" />
            <motion.span
              animate={{ opacity: expanded ? 1 : 0 }}
              transition={{ duration: 0.12 }}
              className="overflow-hidden truncate flex items-center gap-1"
            >
              {expanded && <>{t('transactions.shortcutHelp')} <kbd className="px-1 py-0.5 text-[10px] font-mono rounded bg-base-200 dark:bg-white/10">?</kbd></>}
            </motion.span>
          </motion.button>

          <div className="flex items-center justify-center gap-3 mb-1">
            <LanguageToggle />
          </div>
          <div className="flex items-center justify-center mb-1">
            <ThemeToggle />
          </div>

          {expanded && (
            <p className="text-[10px] text-base-content/30 text-center mt-2">
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
  const navContainerRef = useRef<HTMLDivElement | null>(null);

  const scrollToCategory = (catId: string) => {
    const el = document.getElementById(`sidenav-cat-${catId}`);
    if (el && navContainerRef.current) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

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
            className="fixed top-0 left-0 h-full w-80 max-w-[90vw] z-50
              bg-base-100/90 backdrop-blur-xl
              border-r border-base-300/50
              shadow-2xl flex flex-col
              rtl:left-auto rtl:right-0 rtl:border-r-0 rtl:border-l"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-base-300/50">
              <span className="text-sm font-semibold text-base-content/50 uppercase tracking-wider">
                {t('nav.navigation')}
              </span>
              <motion.button
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-1.5 rounded-lg text-base-content/40 hover:text-base-content
                  hover:bg-base-200/50 dark:hover:bg-white/10 transition-colors"
              >
                <span className="icon-[tabler--x] w-5 h-5" />
              </motion.button>
            </div>

            {/* Home link */}
            <div className="px-4 pt-3 pb-1">
              <motion.button
                whileHover={{ x: isRtl ? -4 : 4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleNavigate('/')}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
                  transition-all duration-200 group ${
                  currentRoute === '/'
                    ? 'bg-base-200/70 dark:bg-white/10 text-base-content font-semibold shadow-sm'
                    : 'text-base-content/60 hover:text-base-content hover:bg-base-200/40 dark:hover:bg-white/5 font-medium'
                }`}
              >
                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm
                  bg-linear-to-br from-teal-400 to-teal-500 shadow-sm shrink-0
                  group-hover:scale-105 transition-transform">
                  <span className="icon-[tabler--dashboard] w-4 h-4" />
                </div>
                <span className="font-semibold">{t('nav.home')}</span>
                {currentRoute === '/' && (
                  <motion.div
                    layoutId="sidenav-active"
                    className="ml-auto rtl:mr-auto rtl:ml-0 w-1.5 h-1.5 rounded-full bg-primary"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </motion.button>
            </div>

            {/* Nav Categories — clickable headers scroll to section */}
            <nav ref={navContainerRef} className="p-3 space-y-1 flex-1 overflow-y-auto">
              {navCategories.map(cat => (
                <NavCategorySection
                  key={cat.id}
                  category={cat}
                  currentRoute={currentRoute}
                  isExpanded={true}
                  isRtl={isRtl}
                  onNavigate={handleNavigate}
                  onHeaderClick={() => scrollToCategory(cat.id)}
                />
              ))}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-base-300/50 mt-auto">
              {isAuthRequired && (
                <motion.button
                  onClick={handleLogout}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.97 }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 mb-3 
                    bg-error/10 hover:bg-error/20 text-error 
                    rounded-xl text-sm font-medium transition-colors 
                    border border-error/20"
                >
                  <span className="icon-[tabler--logout] w-4 h-4" />
                  {t('auth.signOut')}
                </motion.button>
              )}

              <motion.button
                onClick={() => setShowShortcuts(true)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 mb-3
                  bg-base-200/50 dark:bg-white/5 hover:bg-base-200 dark:hover:bg-white/10
                  text-base-content/60 rounded-xl text-sm font-medium transition-colors
                  border border-base-300/50"
              >
                <span className="icon-[tabler--help-circle] w-4 h-4" />
                <span>{t('transactions.shortcutHelp')}</span>
                <kbd className="ml-1 px-1.5 py-0.5 text-[10px] font-mono rounded
                  bg-base-200 dark:bg-white/10 text-base-content/50">
                  ?
                </kbd>
              </motion.button>

              <div className="flex items-center justify-center gap-4 mb-2">
                <LanguageToggle />
              </div>
              <div className="flex items-center justify-center mb-2">
                <ThemeToggle />
              </div>
              <p className="text-[10px] text-base-content/30 text-center mt-3">
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
