
import { Ic } from '../../../lib/icons';
import { useNavigate } from 'react-router-dom';
import { useMemo, useState } from 'react';
import { Settings, Sale, Ingredient, Employee } from '../../../types';
import PageLayout from '../../../components/layout/PageLayout';
import StatCard from '../../../components/ui/StatCard';
import { useCurrency } from '../../../contexts/CurrencyContext';
import Card from '../../../components/ui/Card';
import { ROLE_ROUTES } from '../../../components/layout/SideNav';
import { useAuth } from '../../../contexts/AuthContext';
import { useDashboardDeltas } from '../../../hooks/useDashboardDeltas';
import { useApiQueries } from '../../../hooks/useApi';
import { useTranslation } from 'react-i18next';
import { staggerContainer, iconSpring } from '../../../utils/pageTransitions';
import defaultLogo from '@formints-assets/images/formint-crest.svg';

interface MenuCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  /** Header text + icon color class */
  color: string;
  /** Tinted icon-chip background (matches the item chips below) */
  chip: string;
  /** Gradient start for the header rule */
  gradient: string;
}

interface MenuItem {
  label: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  colorClass: string;
}

// Category header icons — Remix Icon components
const ShoppingCartIcon = Ic('hi:shopping-cart');
const CubeIcon = Ic('hi:cube');
const UsersIcon = Ic('hi:users');
const ChartPieIcon = Ic('hi:chart-pie');
const CogIcon = Ic('hi:cog-6-tooth');
const BanknotesIcon = Ic('hi:banknotes');
const TableCellsIcon = Ic('hi:table-cells');
const ExclamationTriangleIcon = Ic('hi:exclamation-triangle');

const MENU_CATEGORIES: MenuCategory[] = [
  { id: 'sales', label: 'nav.categorySales', icon: <ShoppingCartIcon className="w-6 h-6" />, color: 'text-success', chip: 'bg-success/10', gradient: 'from-success' },
  { id: 'products', label: 'nav.categoryProducts', icon: <CubeIcon className="w-6 h-6" />, color: 'text-info', chip: 'bg-info/10', gradient: 'from-info' },
  { id: 'staff', label: 'nav.categoryStaff', icon: <UsersIcon className="w-6 h-6" />, color: 'text-secondary', chip: 'bg-secondary/10', gradient: 'from-secondary' },
  { id: 'reports', label: 'nav.categoryReports', icon: <ChartPieIcon className="w-6 h-6" />, color: 'text-error', chip: 'bg-error/10', gradient: 'from-error' },
  { id: 'system', label: 'nav.categorySystem', icon: <CogIcon className="w-6 h-6" />, color: 'text-neutral', chip: 'bg-neutral/10', gradient: 'from-neutral' },
];

// Each section's items share the section's accent color as the icon background.
// Mirrors the SideNav module list so the dashboard exposes the full app.
const MENU_ITEMS: Record<string, MenuItem[]> = {
  sales: [
    { label: 'nav.newSale', route: '/sale', icon: Ic('hi:shopping-cart'), colorClass: 'bg-success text-success-content' },
    { label: 'nav.transactions', route: '/transactions', icon: Ic('hi:clock'), colorClass: 'bg-success text-success-content' },
  ],
  products: [
    { label: 'nav.productsMerged', route: '/products', icon: Ic('hi:squares-2x2'), colorClass: 'bg-info text-info-content' },
    { label: 'nav.productManager', route: '/manager', icon: Ic('hi:clipboard-document-list'), colorClass: 'bg-info text-info-content' },
    { label: 'nav.inventory', route: '/inventory', icon: Ic('hi:cube'), colorClass: 'bg-info text-info-content' },
    { label: 'nav.recipes', route: '/recipes', icon: Ic('hi:beaker'), colorClass: 'bg-info text-info-content' },
    { label: 'nav.suppliers', route: '/suppliers', icon: Ic('hi:truck'), colorClass: 'bg-info text-info-content' },
  ],
  staff: [
    { label: 'nav.employees', route: '/employees', icon: Ic('hi:users'), colorClass: 'bg-secondary text-secondary-content' },
    { label: 'nav.schedule', route: '/schedule', icon: Ic('hi:calendar-days'), colorClass: 'bg-secondary text-secondary-content' },
    { label: 'nav.customers', route: '/customers', icon: Ic('hi:user-group'), colorClass: 'bg-secondary text-secondary-content' },
    { label: 'nav.roles', route: '/roles', icon: Ic('hi:shield-check'), colorClass: 'bg-secondary text-secondary-content' },
  ],
  reports: [
    { label: 'nav.analytics', route: '/analytics', icon: Ic('hi:chart-bar'), colorClass: 'bg-error text-error-content' },
    { label: 'nav.reports', route: '/reports', icon: Ic('hi:document-chart-bar'), colorClass: 'bg-error text-error-content' },
    { label: 'nav.taxReports', route: '/reports?tab=taxReports', icon: Ic('hi:receipt-percent'), colorClass: 'bg-error text-error-content' },
  ],
  system: [
    { label: 'nav.settings', route: '/settings', icon: Ic('hi:cog-6-tooth'), colorClass: 'bg-neutral text-neutral-content' },
    { label: 'nav.notes', route: '/notes', icon: Ic('hi:document-text'), colorClass: 'bg-neutral text-neutral-content' },
    { label: 'nav.coupons', route: '/coupons', icon: Ic('hi:tag'), colorClass: 'bg-neutral text-neutral-content' },
    { label: 'nav.supportChat', route: '/support-chat', icon: Ic('hi:chat-bubble-left-right'), colorClass: 'bg-neutral text-neutral-content' },
    { label: 'nav.about', route: '/about', icon: Ic('hi:heart'), colorClass: 'bg-neutral text-neutral-content' },
  ],
};

/** Quick-access merged page cards shown at the top of the home page */
const QUICK_ACCESS = [
  { label: 'nav.staff', desc: 'nav.staffDesc', route: '/staff', icon: Ic('hi:users'), gradient: 'from-secondary to-primary' },
  { label: 'nav.productsMerged', desc: 'nav.productsMergedDesc', route: '/products', icon: Ic('hi:squares-2x2'), gradient: 'from-info to-primary' },
  { label: 'nav.salesMerged', desc: 'nav.salesMergedDesc', route: '/sale', icon: Ic('hi:shopping-cart'), gradient: 'from-success to-primary' },
  { label: 'nav.reportsMerged', desc: 'nav.reportsMergedDesc', route: '/reports', icon: Ic('hi:chart-pie'), gradient: 'from-warning to-secondary' },
];

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loadingRoute, setLoadingRoute] = useState<string | null>(null);

  // Role-based visibility — mirrors the SideNav (manager sees everything).
  const allowedRoutes = useMemo(() => {
    const role = user?.role || 'manager';
    return ROLE_ROUTES[role] || ROLE_ROUTES.manager;
  }, [user]);

  const handleNavigation = (route: string) => {
    setLoadingRoute(route);
    setTimeout(() => navigate(route), 250);
  };

  // ── Data fetching via shared useApiQueries hook ──
  const {
    data: [settingsRes, salesRes, ingredientsRes, employeesRes],
    isLoading: kpisLoading,
  } = useApiQueries([
    { command: 'get_settings' },
    { command: 'get_sales' },
    { command: 'get_ingredients', params: { includeInactive: false } },
    { command: 'get_employees', params: { includeInactive: true } },
  ]);

  const settings = (settingsRes as Settings | undefined) ?? null;
  const restaurantName = settings?.restaurant_name || 'Formint';
  const { formatPrice, currencySymbol } = useCurrency();
  const sales = (Array.isArray(salesRes) ? (salesRes as Sale[]) : []) as Sale[];

  const { todayStats, revDelta, orderDelta } = useDashboardDeltas(sales);

  // ── Derived KPIs from fetched data (useMemo for stability) ──
  const kpis = useMemo(() => {
    if (!salesRes || !ingredientsRes || !employeesRes) return null;
    const s = salesRes as Sale[];
    const i = ingredientsRes as Ingredient[];
    const e = employeesRes as Employee[];
    const pendingStatuses = ['pending', 'active', 'in-progress'];
    return {
      openTables: s.filter(sale => sale.order_type === 'dine-in' && pendingStatuses.includes(sale.status)).length,
      lowStockCount: i.filter(ing => ing.current_quantity <= ing.reorder_level).length,
      activeEmployees: e.filter(emp => emp.is_active).length,
    };
  }, [salesRes, ingredientsRes, employeesRes]);

  // ── Sparkline data for StatCard charts ──
  const sparklines = useMemo(() => {
    if (!salesRes) return null;
    const s = salesRes as Sale[];
    const dayKeys: string[] = [];
    for (let i = 6; i >= 0; i--) {
      dayKeys.push(new Date(Date.now() - i * 86400000).toISOString().slice(0, 10));
    }
    const revenue: { value: number }[] = [];
    const orders: { value: number }[] = [];
    for (const date of dayKeys) {
      const daySales = s.filter(sale => sale.date === date);
      revenue.push({ value: daySales.reduce((sum, sale) => sum + sale.total_amount, 0) });
      orders.push({ value: daySales.length });
    }
    return { revenue, orders };
  }, [salesRes]);

  return (
    <PageLayout
      showNav={false}
      background="bg-linear-to-br from-base-200 via-primary/5 to-base-200"
      padding="py-12 md:py-16 lg:py-12"
    >
      {/* ── Header — asymmetric left-aligned brand block (skill Rule 3: no
          centered hero at high variance). Logo tile anchors the left edge;
          title + subtitle stack beside it. ── */}
      <div className="flex items-center gap-4 md:gap-6 mb-10 md:mb-12 animate-slide-up max-w-6xl mx-auto px-2">
        <div className={`${iconSpring} bg-base-100/60 dark:bg-white/10 backdrop-blur-md rounded-2xl p-4 md:p-5 shrink-0 shadow-xl border border-base-300/30 dark:border-white/5`}>
          <img
            src={defaultLogo as unknown as string}
            alt="Formint"
            className="w-14 h-14 md:w-16 md:h-16 object-contain"
            onError={(e) => { e.currentTarget.style.display = 'none'; }}
          />
        </div>
        <div className="min-w-0">
          {/* Eyebrow pill — register design language: breathing verdigris dot
              + uppercase micro-label above the brand headline. */}
          <div
            className="flex items-center gap-2 mb-2.5 animate-fade-in"
            style={{ animationDelay: '0.05s' }}
          >
            <span className="eyebrow">
              <span className="w-1.5 h-1.5 rounded-full bg-primary fu-breath" aria-hidden="true" />
              {t('home.brandEyebrow', 'Formints · POS')}
            </span>
          </div>
          <h1
            className="text-2xl md:text-4xl font-bold text-base-content leading-tight truncate animate-fade-in"
            style={{ animationDelay: '0.15s' }}
          >
            {restaurantName}
          </h1>
          <p
            className="text-base-content/50 mt-1.5 text-sm animate-fade-in"
            style={{ animationDelay: '0.25s' }}
          >
            {t('home.dashboard') || 'Dashboard'}
          </p>
        </div>
      </div>

      {/* ── Quick Access Cards — hover gradient animation + keyboard accessible ── */}
      <div className="max-w-6xl mx-auto px-2 mb-8 animate-slide-up"
        style={{ animationDelay: '0.1s' }}
      >
        <Card padding="sm" variant="bezel" hover>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {QUICK_ACCESS.map((qa, i) => (
              <button
                key={qa.route}
                onClick={() => handleNavigation(qa.route)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleNavigation(qa.route); } }}
                disabled={loadingRoute !== null}
                tabIndex={0}
                role="button"
                aria-label={t(qa.label)}
                style={{ animationDelay: `${0.2 + i * 0.06}s` }}
                className="relative card bg-base-200/50 dark:bg-white/5
                  border border-base-300/20 p-3 rounded-xl
                  transition-all duration-200 group disabled:opacity-60 animate-fade-in
                  hover:shadow-card-hover hover:-translate-y-0.5
                  hover:bg-base-100/80 dark:hover:bg-white/10 hover:border-primary/30
                  focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none
                  overflow-hidden"
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-2 relative z-10
                  bg-linear-to-br ${qa.gradient} text-white shadow-lg
                  group-hover:scale-110 transition-transform duration-200`}
                >
                  <qa.icon className="w-6 h-6" />
                </div>
                <span className="text-xs font-semibold text-base-content/60 text-center leading-tight relative z-10">{t(qa.label)}</span>
                <span className="text-[10px] text-base-content/50 text-center mt-0.5 leading-tight line-clamp-1 relative z-10">{t(qa.desc)}</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* ── Live KPI Dashboard ── */}
      <div className="max-w-6xl mx-auto px-2 mb-8 animate-slide-up"
        style={{ animationDelay: '0.2s' }}
      >
        <h2 className="text-sm font-semibold uppercase tracking-wider text-base-content/50 mb-3 pl-1 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-success animate--breathe" aria-hidden="true" />
          {t('home.liveDashboard', 'Live Dashboard')}
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
          {kpisLoading ? (
            <>
              {[1, 2, 3, 4, 5, 6].map(i => (
                <StatCard key={i} loading compact />
              ))}
            </>
          ) : (
            <>
              <StatCard
                title={t('home.todaySales', 'Today Sales')}
                value={todayStats.orders}
                desc={todayStats.orders === 1
                  ? t('home.oneOrderToday', '1 order today') + ` · ${orderDelta.pct} ` + t('home.vsYesterday', 'vs yesterday')
                  : `${todayStats.orders} ${t('home.ordersToday', 'orders today')} · ${orderDelta.pct} ${t('home.vsYesterday', 'vs yesterday')}`}
                icon={<ShoppingCartIcon className="w-6 h-6" />}
                sparklineData={sparklines?.orders}
                color="primary"
                compact
                onClick={() => handleNavigation('/transactions')}
              />
              <StatCard
                title={t("home.todayRevenue", "Today's Revenue")}
                value={`${currencySymbol} ${todayStats.revenue.toLocaleString()}`}
                desc={todayStats.revenue > 0
                  ? `${formatPrice(todayStats.revenue / (todayStats.orders || 1))} ${t('home.avg', 'avg')} · ${revDelta.pct} ${t('home.vsYesterday', 'vs yesterday')}`
                  : t('home.noRevenueYet', 'No revenue yet')}
                icon={<BanknotesIcon className="w-6 h-6" />}
                sparklineData={sparklines?.revenue}
                color="info"
                compact
                onClick={() => handleNavigation('/reports')}
              />
              <StatCard
                title={t('home.openTables', 'Open Tables')}
                value={kpis?.openTables ?? 0}
                desc={kpis?.openTables === 0
                  ? t('home.allClear', 'All clear')
                  : `${kpis?.openTables} ${kpis?.openTables === 1 ? t('home.table', 'table') : t('home.tables', 'tables')} ${t('home.inService', 'in service')}`}
                icon={<TableCellsIcon className="w-6 h-6" />}
                color="warning"
                compact
                onClick={() => handleNavigation('/sale')}
              />
              <StatCard
                title={t('home.staff', 'Active Staff')}
                value={kpis?.activeEmployees ?? 0}
                desc={kpis?.activeEmployees === 1
                  ? `1 ${t('home.employee', 'employee')}`
                  : `${kpis?.activeEmployees ?? 0} ${t('home.employees', 'employees')}`}
                icon={<UsersIcon className="w-6 h-6" />}
                color="secondary"
                compact
                onClick={() => handleNavigation('/staff')}
              />
              <StatCard
                title={t('home.lowStock', 'Low Stock')}
                value={kpis?.lowStockCount ?? 0}
                desc={kpis?.lowStockCount === 0
                  ? t('home.allStocked', 'All stocked')
                  : `${kpis?.lowStockCount} ${kpis?.lowStockCount === 1 ? t('home.item', 'item') : t('home.items', 'items')} ${t('home.belowReorder', 'below reorder level')}`}
                icon={<ExclamationTriangleIcon className="w-6 h-6" />}
                color={kpis?.lowStockCount && kpis.lowStockCount > 0 ? 'error' : 'success'}
                compact
                onClick={() => handleNavigation('/inventory')}
              />
            </>
          )}
        </div>
      </div>

      {/* ── Categorized Menu Grid — single stagger animation ── */}
      <div
        className={`max-w-6xl mx-auto px-2 space-y-8 ${staggerContainer}`}
      >
        {MENU_CATEGORIES.map((cat) => {
          // Skip categories the user's role cannot see (mirrors SideNav).
          const visibleItems = (MENU_ITEMS[cat.id] || []).filter(item => allowedRoutes.has(item.route));
          if (visibleItems.length === 0) return null;
          return (
          <div key={cat.id}>
            {/* Category Header — tinted icon chip + colored title + gradient rule */}
            <div className="flex items-center gap-3 mb-3 pl-1">
              <span className={`${cat.chip} rounded-xl w-10 h-10 flex items-center justify-center shrink-0 shadow-sm`}>
                <span className={cat.color}>{cat.icon}</span>
              </span>
              <h2 className={`text-sm font-bold ${cat.color} tracking-tight`}>
                {t(cat.label)}
              </h2>
              <div className={`flex-1 h-px bg-linear-to-r ${cat.gradient} to-transparent opacity-40 rtl:bg-linear-to-l`} />
            </div>

            {/* Category Items — staggered children, filtered by role like the SideNav */}
            <div className="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 3xl:grid-cols-8 gap-3 md:gap-4">
              {visibleItems.map((menuItem) => {
                const Icon = menuItem.icon;
                const isLoading = loadingRoute === menuItem.route;

                return (
                  <button
                    key={menuItem.route}
                    onClick={() => handleNavigation(menuItem.route)}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleNavigation(menuItem.route); } }}
                    disabled={loadingRoute !== null}
                    tabIndex={0}
                    role="button"
                    aria-label={t(menuItem.label)}
                    className="relative card bg-base-100/80 dark:bg-white/5 backdrop-blur-sm
                      border-2 border-base-300/40
                      dark:border-white/10
                      p-3 rounded-2xl transition-all duration-300
                      hover:shadow-card-hover hover:-translate-y-0.5 active:scale-[0.98]
                      focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:outline-none
                      group disabled:opacity-60 overflow-hidden
                      flex flex-col items-center justify-center text-center"
                  >
                    {/* Hover glow effect */}
                    <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500
                      bg-radial-[at_50%_0%] from-white/10 via-transparent to-transparent
                      dark:from-white/5" />

                    {isLoading ? (
                      <div className="w-full flex items-center justify-center py-4">
                        <div className="w-7 h-7 border-3 border-base-300 border-t-primary rounded-full animate-spin" />
                      </div>
                    ) : (
                      <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-2
                        ${menuItem.colorClass} shadow-md
                        group-hover:scale-110 transition-transform duration-300`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                    )}

                    <span className="text-sm font-semibold text-base-content/80 leading-tight">
                      {t(menuItem.label)}
                    </span>
                    <span className="text-[10px] text-base-content/50 mt-0.5 leading-tight max-w-[100px] mx-auto">
                      {t(menuItem.label + 'Desc')}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
          );
        })}
      </div>
    </PageLayout>
  );
}
