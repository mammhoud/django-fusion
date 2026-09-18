import { useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect, memo } from 'react';
import LanguageToggle from '../display/LanguageToggle';
import KeyboardShortcutsModal from '../shared/KeyboardShortcutsModal';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from 'react-i18next';
import { preloadRoute } from '../../utils/preloadRoutes';
import { Ic } from '../../lib/icons';

// Remix Icon components used across the sidebar
const HomeIcon = Ic('hi:home');
const PinIcon = Ic('hi:map-pin');
const LogoutIcon = Ic('hi:arrow-right-start-on-rectangle');
const HelpIcon = Ic('hi:help-circle');
const RoleBadgeIcon = Ic('hi:check-badge');

// ── Role-based nav visibility ──
// Which routes each role can see. 'manager' sees everything.
// 'employee' sees only operational pages — no settings, reports, or admin.
export const ROLE_ROUTES: Record<string, Set<string>> = {
  manager: new Set([
    '/dashboard', '/sale', '/kitchen', '/transactions',
    '/products', '/manager', '/inventory', '/recipes', '/suppliers',
    '/employees', '/schedule', '/payroll', '/customers', '/roles', '/currencies', '/tax-profiles', '/register',
    '/analytics', '/reports', '/export', '/reports?tab=taxReports',
    '/settings', '/notes', '/coupons', '/badges', '/support-chat', '/about',
  ]),
  employee: new Set([
    '/dashboard', '/sale', '/kitchen', '/transactions', '/inventory',
  ]),
};

function filterNavByRole(categories: NavCategory[], role: string): NavCategory[] {
  const allowed = ROLE_ROUTES[role] || ROLE_ROUTES.manager;
  return categories
    .map(cat => ({
      ...cat,
      items: cat.items.filter(item => allowed.has(item.route)),
    }))
    .filter(cat => cat.items.length > 0);
}

// ── Category definitions with section headers ──
interface NavItem {
  label: string;
  desc: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  colorClass: string;
}

interface NavCategory {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  /** Text accent color for the category header — mirrors the dashboard's MENU_CATEGORIES palette. */
  color: string;
  items: NavItem[];
}

const navCategories: NavCategory[] = [
  {
    id: 'sales',
    label: 'nav.sales',
    icon: Ic('hi:shopping-cart'),
    color: 'text-success',
    items: [
      { label: 'nav.newSale', desc: 'nav.newSaleDesc', route: '/sale', icon: Ic('hi:shopping-cart'), colorClass: 'bg-success' },
      { label: 'nav.kitchen', desc: 'nav.kitchenDesc', route: '/kitchen', icon: Ic('hi:fire'), colorClass: 'bg-success' },
      { label: 'nav.transactions', desc: 'nav.transactionsDesc', route: '/transactions', icon: Ic('hi:clock'), colorClass: 'bg-success' },
    ],
  },
  {
    id: 'products',
    label: 'nav.products',
    icon: Ic('hi:cube'),
    color: 'text-info',
    items: [
      { label: 'nav.productsMerged', desc: 'nav.productsMergedDesc', route: '/products', icon: Ic('hi:squares-2x2'), colorClass: 'bg-info' },
      { label: 'nav.productManager', desc: 'nav.productManagerDesc', route: '/manager', icon: Ic('hi:clipboard-document-list'), colorClass: 'bg-info' },
      { label: 'nav.inventory', desc: 'nav.inventoryDesc', route: '/inventory', icon: Ic('hi:cube'), colorClass: 'bg-info' },
      { label: 'nav.recipes', desc: 'nav.recipesDesc', route: '/recipes', icon: Ic('hi:beaker'), colorClass: 'bg-info' },
      { label: 'nav.suppliers', desc: 'nav.suppliersDesc', route: '/suppliers', icon: Ic('hi:truck'), colorClass: 'bg-info' },
    ],
  },
  {
    id: 'staff',
    label: 'nav.staff',
    icon: Ic('hi:users'),
    color: 'text-secondary',
    items: [
      { label: 'nav.employees', desc: 'nav.employeesDesc', route: '/employees', icon: Ic('hi:users'), colorClass: 'bg-secondary' },
      { label: 'nav.schedule', desc: 'nav.scheduleDesc', route: '/schedule', icon: Ic('hi:calendar-days'), colorClass: 'bg-secondary' },
      { label: 'nav.payroll', desc: 'nav.payrollDesc', route: '/payroll', icon: Ic('hi:banknotes'), colorClass: 'bg-secondary' },
      { label: 'nav.customers', desc: 'nav.customersDesc', route: '/customers', icon: Ic('hi:user-group'), colorClass: 'bg-secondary' },
      { label: 'nav.roles', desc: 'nav.rolesDesc', route: '/roles', icon: Ic('hi:shield-check'), colorClass: 'bg-secondary' },
      { label: 'nav.currencies', desc: 'Manage sale currencies', route: '/currencies', icon: Ic('hi:banknotes'), colorClass: 'bg-secondary' },
      { label: 'nav.taxProfiles', desc: 'Manage named tax rates', route: '/tax-profiles', icon: Ic('hi:receipt-percent'), colorClass: 'bg-secondary' },
      { label: 'nav.register', desc: 'nav.registerDesc', route: '/register', icon: Ic('hi:banknotes'), colorClass: 'bg-secondary' },
    ],
  },
  {
    id: 'reports',
    label: 'nav.reports',
    icon: Ic('hi:chart-pie'),
    color: 'text-error',
    items: [
      { label: 'nav.analytics', desc: 'nav.analyticsDesc', route: '/analytics', icon: Ic('hi:chart-bar'), colorClass: 'bg-error' },
      { label: 'nav.reports', desc: 'nav.reportsDesc', route: '/reports', icon: Ic('hi:document-chart-bar'), colorClass: 'bg-error' },
      { label: 'nav.export', desc: 'Export local data', route: '/export', icon: Ic('hi:arrow-down-tray'), colorClass: 'bg-error' },
      { label: 'nav.taxReports', desc: 'nav.taxReportsDesc', route: '/reports?tab=taxReports', icon: Ic('hi:receipt-percent'), colorClass: 'bg-error' },
    ],
  },
  {
    id: 'system',
    label: 'nav.system',
    icon: Ic('hi:cog-6-tooth'),
    color: 'text-base-content/50',
    items: [
      { label: 'nav.settings', desc: 'nav.settingsDesc', route: '/settings', icon: Ic('hi:cog-6-tooth'), colorClass: 'bg-neutral' },
      { label: 'nav.notes', desc: 'nav.notesDesc', route: '/notes', icon: Ic('hi:document-text'), colorClass: 'bg-neutral' },
      { label: 'nav.coupons', desc: 'nav.couponsDesc', route: '/coupons', icon: Ic('hi:tag'), colorClass: 'bg-neutral' },
      { label: 'nav.badges', desc: 'nav.badgesDesc', route: '/badges', icon: Ic('hi:award'), colorClass: 'bg-neutral' },
      { label: 'nav.supportChat', desc: 'nav.supportChatDesc', route: '/support-chat', icon: Ic('hi:chat-bubble-left-right'), colorClass: 'bg-neutral' },
      { label: 'nav.about', desc: 'nav.aboutDesc', route: '/about', icon: Ic('hi:heart'), colorClass: 'bg-neutral' },
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
  const { t } = useTranslation();
  const CategoryIcon = category.icon;
  const content = (
    <div className="flex items-center gap-2 px-2.5 py-2 mt-1 first:mt-0 w-full">
      <span className={`${category.color}`}>
        <CategoryIcon className="w-3.5 h-3.5 shrink-0" />
      </span>
      {isExpanded && (
        <span className={`text-[10px] font-semibold uppercase tracking-wider truncate ${category.color}`}>
          {t(category.label)}
        </span>
      )}
    </div>
  );

  if (isClickable && onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className="w-full text-start cursor-pointer hover:bg-base-200/30 rounded-xl transition-all active:scale-[0.97]"
      >
        {content}
      </button>
    );
  }

  return content;
}

// ── Nav Item Button ──
function NavItemButton({
  item,
  isActive,
  isExpanded,
  onClick,
}: {
  item: NavItem;
  isActive: boolean;
  isExpanded: boolean;
  onClick: () => void;
}) {
  const { t } = useTranslation();
  const Icon = item.icon;
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => preloadRoute(item.route)}
      onFocus={() => preloadRoute(item.route)}
      className={`w-full flex items-center gap-3 px-2.5 py-2 rounded-xl text-sm
        transition-all duration-200 group whitespace-nowrap active:scale-[0.98] ${
        isActive
          ? 'bg-base-200/70 dark:bg-white/10 text-base-content font-semibold shadow-sm'
          : 'text-base-content/60 hover:text-base-content hover:bg-base-200/40 dark:hover:bg-white/5 font-medium'
      }`}
      title={!isExpanded ? t(item.label) : undefined}
    >
      <div className={`w-7 h-7 min-w-[1.75rem] rounded-lg flex items-center justify-center text-white text-xs
        ${item.colorClass} shadow-sm
        ${isActive ? 'scale-110' : 'group-hover:scale-105'} transition-transform shrink-0`}
      >
        <Icon className="w-3.5 h-3.5" />
      </div>
      <div className="flex flex-col items-start overflow-hidden">
        <span
          className={`overflow-hidden truncate text-start w-full transition-opacity duration-150 ${isExpanded ? 'opacity-100' : 'opacity-0'}`}
        >
          {t(item.label)}
        </span>
        {isExpanded && item.desc && (
          <span className="text-[10px] text-base-content/40 truncate w-full leading-tight mt-0.5">
            {t(item.desc)}
          </span>
        )}
      </div>
      {isActive && isExpanded && (
        <div className="ms-auto w-1.5 h-1.5 rounded-full bg-primary fu-breath shrink-0" />
      )}
    </button>
  );
}

// ── Render a category with its items ──
function NavCategorySection({
  category,
  currentRoute,
  isExpanded,
  onNavigate,
  onHeaderClick,
  isCollapsed,
}: {
  category: NavCategory;
  currentRoute: string;
  isExpanded: boolean;
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
  const { isAuthRequired, logout, user } = useAuth();
  const { t } = useTranslation();
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
  const userRole = user?.role || 'manager';

  const handleNavigate = (route: string) => {
    navigate(route);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      <aside
        className={`fixed left-0 top-0 h-full z-30
          bg-base-100/95 backdrop-blur-xl
          border-r border-base-300/50
          shadow-xl flex flex-col overflow-hidden
          hidden 4xl:flex
          rtl:left-auto rtl:right-0 rtl:border-r-0 rtl:border-l
          transition-[width] duration-200 ease-out
          ${expanded ? 'w-[280px]' : 'w-16'}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => { if (!isPinned) setIsHovered(false); }}
      >
        {/* Header — logo + pin toggle */}
        <div className="flex items-center justify-end p-3 border-b border-base-300/50 min-h-[52px]">
          {expanded && (
            <span className="text-xs font-semibold text-base-content/50 uppercase tracking-wider flex-1 truncate ps-0.5">
              {t('nav.navigation')}
            </span>
          )}
          <button
            onClick={() => setIsPinned(!isPinned)}
            className="p-1.5 rounded-lg text-base-content/40 hover:text-base-content/70
              hover:bg-base-200/50 dark:hover:bg-white/10 transition-all active:scale-[0.9]"
            title={isPinned ? 'Unpin sidebar' : 'Pin sidebar'}
          >
            <PinIcon className={`w-4 h-4 transition-transform duration-200 ${isPinned ? 'rotate-45 text-primary' : ''}`} />
          </button>
        </div>

        {/* Home button always visible */}
        <div className="px-3 pt-2 pb-1">
          <NavItemButton
            item={{ label: 'nav.home', desc: 'nav.homeDesc', route: '/dashboard', icon: HomeIcon, colorClass: 'bg-info' }}
            isActive={currentRoute === '/dashboard'}
            isExpanded={expanded}
            onClick={() => handleNavigate('/dashboard')}
          />
        </div>

        {/* Nav categories — scrollable, filtered by role */}
        <nav className="px-2 pb-2 space-y-1 flex-1 overflow-y-auto overflow-x-hidden">
          {filterNavByRole(navCategories, userRole).map(cat => (
            <NavCategorySection
              key={cat.id}
              category={cat}
              currentRoute={currentRoute}
              isExpanded={expanded}
              onNavigate={handleNavigate}
              onHeaderClick={() => toggleCategory(cat.id)}
              isCollapsed={collapsedCategories.has(cat.id)}
            />
          ))}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-base-300/50 mt-auto">
          {isAuthRequired && (
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-2 py-2 mb-2
                bg-error/10 hover:bg-error/20 text-error
                rounded-xl text-sm font-medium transition-all active:scale-[0.97]"
              title={!expanded ? t('auth.signOut') : undefined}
            >
              <LogoutIcon className="w-4 h-4 shrink-0" />
              <span
                className={`overflow-hidden truncate transition-opacity duration-150 ${expanded ? 'opacity-100' : 'opacity-0'}`}
              >
                {expanded && t('auth.signOut')}
              </span>
            </button>
          )}

          <button
            onClick={() => setShowShortcuts(true)}
            className="w-full flex items-center justify-center gap-2 px-2 py-2 mb-2
              bg-base-200/50 dark:bg-white/5 hover:bg-base-200 dark:hover:bg-white/10
              text-base-content/60 rounded-xl text-sm font-medium transition-all active:scale-[0.97]"
            title={!expanded ? t('transactions.shortcutHelp') : undefined}
          >
            <HelpIcon className="w-4 h-4 shrink-0" />
            <span
              className={`overflow-hidden truncate flex items-center gap-1 transition-opacity duration-150 ${expanded ? 'opacity-100' : 'opacity-0'}`}
            >
              {expanded && <>{t('transactions.shortcutHelp')} <kbd className="px-1 py-0.5 text-[10px] font-mono rounded bg-base-200 dark:bg-white/10">?</kbd></>}
            </span>
          </button>

          <div className="flex items-center justify-center gap-3 mb-1">
            <LanguageToggle />
          </div>

          {expanded && user && (
            <div className="flex items-center justify-center gap-1.5 mt-2 mb-1">
              <RoleBadgeIcon className="w-3 h-3 text-base-content/40" />
              <span className="text-[10px] font-medium text-base-content/50 capitalize">
                {user.role || 'Manager'}
              </span>
            </div>
          )}

          {expanded && (
            <p className="text-[10px] text-base-content/30 text-center mt-1">
              {t('nav.footer')}
            </p>
          )}
        </div>
      </aside>

      <KeyboardShortcutsModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
    </>
  );
}

const SideNav = memo(function SideNav({ isOpen = false, onClose = () => {}, currentRoute, persistent = false }: SideNavProps) {
  if (persistent) {
    return <PersistentSidebar currentRoute={currentRoute} />;
  }
  const navigate = useNavigate();
  const { isAuthRequired, logout, user } = useAuth();
  const { language } = useLanguage();
  const { t } = useTranslation();
  const isRtl = language === 'ar';
  const [showShortcuts, setShowShortcuts] = useState(false);
  // Self-contained closing state — guarantees the drawer unmounts even when CSS
  // exit animations are disabled (reduced motion) or interrupted.
  const [closing, setClosing] = useState(false);
  const closeTimerRef = useRef<number | null>(null);
  const navContainerRef = useRef<HTMLDivElement | null>(null);
  const userRole = user?.role || 'manager';
  // Reset closing state whenever the drawer is re-opened, then trigger the
  // staggered mask reveal (links rise out of their hidden box) right after
  // the glass pill begins its slide-in.
  const [revealed, setRevealed] = useState(false);
  useEffect(() => {
    if (isOpen) {
      setClosing(false);
      setRevealed(false);
      const id = window.setTimeout(() => setRevealed(true), 60);
      return () => window.clearTimeout(id);
    }
  }, [isOpen]);

  // Clean up any pending close timer on unmount.
  useEffect(() => () => {
    if (closeTimerRef.current !== null) window.clearTimeout(closeTimerRef.current);
  }, []);

  const requestCloseRef = useRef<(() => void) | null>(null);
  const requestClose = () => {
    if (closing) return;
    setClosing(true);
    closeTimerRef.current = window.setTimeout(() => {
      setClosing(false);
      onClose();
    }, 200); // matches the drawer-out animation duration (--duration--normal)
  };
  requestCloseRef.current = requestClose;

  // Close on Escape (standard drawer a11y affordance).
  useEffect(() => {
    if (!isOpen || closing) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') requestCloseRef.current?.();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, closing]);

  const scrollToCategory = (catId: string) => {
    const el = document.getElementById(`sidenav-cat-${catId}`);
    if (el && navContainerRef.current) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleNavigate = (route: string) => {
    requestClose();
    navigate(route);
  };

  const handleLogout = () => {
    requestClose();
    logout();
  };

  return (
    <>
      {(isOpen || closing) && (
        <>
          {/* Backdrop */}
          <div
            className={`fixed inset-0 bg-black/40 backdrop-blur-sm z-40 ${closing ? 'animate--fade-out' : 'animate--fade-in'}`}
            onClick={requestClose}
          />

          {/* Panel — floating glass pill chrome */}
          <aside
            className={`fixed top-3 bottom-3 left-3 w-80 max-w-[calc(100vw-1.5rem)] z-50
              glass-pill rounded-[2rem] flex flex-col overflow-hidden
              rtl:left-auto rtl:right-3
              ${closing
                ? (isRtl ? 'animate--drawer-out-right' : 'animate--drawer-out-left')
                : (isRtl ? 'animate--drawer-in-right' : 'animate--drawer-in-left')}`}
          >
            {/* Header — eyebrow + hamburger→X morph */}
            <div
              className={`nav-mask overflow-hidden px-4 pt-4 pb-2 ${revealed ? 'is-visible' : ''}`}
              style={{ transitionDelay: '80ms' }}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-base-content/50">
                  {t('nav.navigation')}
                </span>
                <button
                  onClick={requestClose}
                  className="relative flex h-10 w-10 items-center justify-center rounded-full
                    transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                    hover:bg-base-200/80 dark:hover:bg-white/10 active:scale-95"
                  aria-label={t('common.closeNavigation') || 'Close navigation'}
                  aria-expanded="true"
                >
                  <span
                    className={`absolute h-[1.5px] w-4 rounded-full bg-base-content
                      transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                      ${revealed ? 'rotate-45' : '-translate-y-[4.5px]'}`}
                  />
                  <span
                    className={`absolute h-[1.5px] w-4 rounded-full bg-base-content
                      transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)]
                      ${revealed ? '-rotate-45' : 'translate-y-[4.5px]'}`}
                  />
                </button>
              </div>
            </div>

            {/* Home link */}
            <div
              className={`nav-mask overflow-hidden px-4 pt-3 pb-1 ${revealed ? 'is-visible' : ''}`}
              style={{ transitionDelay: '140ms' }}
            >
              <button
                onClick={() => handleNavigate('/dashboard')}
                onMouseEnter={() => preloadRoute('/dashboard')}
                onFocus={() => preloadRoute('/dashboard')}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
                  transition-all duration-200 group active:scale-[0.98] ${
                  currentRoute === '/dashboard'
                    ? 'bg-base-200/70 dark:bg-white/10 text-base-content font-semibold shadow-sm'
                    : 'text-base-content/60 hover:text-base-content hover:bg-base-200/40 dark:hover:bg-white/5 font-medium'
                }`}
                title={t('nav.home')}
              >
                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm
                  bg-info shadow-sm shrink-0
                  group-hover:scale-105 transition-transform">
                  <HomeIcon className="w-4 h-4" />
                </div>
                <div className="flex flex-col items-start">
                  <span className="font-semibold">{t('nav.home')}</span>
                  <span className="text-[10px] text-base-content/40 leading-tight">{t('nav.homeDesc')}</span>
                </div>
                {currentRoute === '/dashboard' && (
                  <div
                    className="ms-auto w-1.5 h-1.5 rounded-full bg-primary fu-breath"
                  />
                )}
              </button>
            </div>

            {/* Nav Categories — clickable headers scroll to section, filtered by role */}
            <nav ref={navContainerRef} className="p-3 space-y-1 flex-1 overflow-y-auto">
              {filterNavByRole(navCategories, userRole).map(cat => (
                <NavCategorySection
                  key={cat.id}
                  category={cat}
                  currentRoute={currentRoute}
                  isExpanded={true}
                  onNavigate={handleNavigate}
                  onHeaderClick={() => scrollToCategory(cat.id)}
                />
              ))}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-base-300/50 mt-auto">
              {isAuthRequired && (
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 mb-3 
                    bg-error/10 hover:bg-error/20 text-error 
                    rounded-xl text-sm font-medium transition-all active:scale-[0.97] 
                    border border-error/20"
                >
                  <LogoutIcon className="w-4 h-4" />
                  {t('auth.signOut')}
                </button>
              )}

              <button
                onClick={() => setShowShortcuts(true)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 mb-3
                  bg-base-200/50 dark:bg-white/5 hover:bg-base-200 dark:hover:bg-white/10
                  text-base-content/60 rounded-xl text-sm font-medium transition-all active:scale-[0.97]
                  border border-base-300/50"
              >
                <HelpIcon className="w-4 h-4" />
                <span>{t('transactions.shortcutHelp')}</span>
                <kbd className="ms-1 px-1.5 py-0.5 text-[10px] font-mono rounded
                  bg-base-200 dark:bg-white/10 text-base-content/50">
                  ?
                </kbd>
              </button>

              <div className="flex items-center justify-center gap-4 mb-2">
                <LanguageToggle />
              </div>
              {user && (
                <div className="flex items-center justify-center gap-1.5 mt-2 mb-1">
                  <RoleBadgeIcon className="w-3 h-3 text-base-content/40" />
                  <span className="text-[10px] font-medium text-base-content/50 capitalize">
                    {user.role || 'Manager'}
                  </span>
                </div>
              )}
              <p className="text-[10px] text-base-content/30 text-center mt-3">
                {t('nav.footer')}
              </p>
            </div>

            <KeyboardShortcutsModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
          </aside>
        </>
      )}
    </>
  );
});

export default SideNav;
