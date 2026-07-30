
import { Ic, iconClass } from '../../lib/icons';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useMemo, useState } from 'react';
import { Settings, Sale, Ingredient, Employee, KitchenTicket } from '../../types';
import PageLayout from '../../components/layout/PageLayout';
import StatCard from '../../components/data/StatCard';
import { useCurrency } from '../../contexts/CurrencyContext';
import Card from '../../components/layout/Card';
import { useDashboardDeltas } from '../../hooks/useDashboardDeltas';
import { useApiQueries } from '../../hooks/useApi';
import { useTranslation } from 'react-i18next';
import { staggerContainer, iconSpring } from '../../utils/pageTransitions';
import defaultLogo from '../../assets/pos-crest.svg';

interface MenuCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  color: string;
}

interface MenuItem {
  label: string;
  route: string;
  icon: React.ComponentType<{ className?: string }>;
  colorClass: string;
}

const MENU_CATEGORIES: MenuCategory[] = [
  { id: 'sales', label: 'nav.categorySales', icon: <span className={iconClass('lucide:shopping-cart', 'w-5 h-5')} />, color: 'text-success' },
  { id: 'products', label: 'nav.categoryProducts', icon: <span className={iconClass('lucide:package', 'w-5 h-5')} />, color: 'text-info' },
  { id: 'staff', label: 'nav.categoryStaff', icon: <span className={iconClass('lucide:users', 'w-5 h-5')} />, color: 'text-secondary' },
  { id: 'reports', label: 'nav.categoryReports', icon: <span className={iconClass('lucide:bar-chart-3', 'w-5 h-5')} />, color: 'text-error' },
  { id: 'system', label: 'nav.categorySystem', icon: <span className={iconClass('lucide:layout-dashboard', 'w-5 h-5')} />, color: 'text-base-content/50' },
];

const MENU_ITEMS: Record<string, MenuItem[]> = {
  sales: [
    { label: 'nav.newSale', route: '/sale', icon: Ic('shopping-cart'), colorClass: 'bg-success text-white' },
    { label: 'nav.kitchen', route: '/kitchen', icon: Ic('tools-kitchen-2'), colorClass: 'bg-info text-white' },
    { label: 'nav.transactions', route: '/transactions', icon: Ic('history'), colorClass: 'bg-info/70 text-white' },
    { label: 'nav.notes', route: '/notes', icon: Ic('notes'), colorClass: 'bg-neutral/70 text-neutral-content' },
  ],
  products: [
    { label: 'nav.productManager', route: '/manager', icon: Ic('clipboard-list'), colorClass: 'bg-info text-white' },
    { label: 'nav.inventory', route: '/inventory', icon: Ic('package'), colorClass: 'bg-accent text-white' },
    { label: 'nav.recipes', route: '/recipes', icon: Ic('flask'), colorClass: 'bg-secondary text-white' },
    { label: 'nav.suppliers', route: '/suppliers', icon: Ic('truck'), colorClass: 'bg-secondary/70 text-white' },
  ],
  staff: [
    { label: 'nav.staff', route: '/staff', icon: Ic('users'), colorClass: 'bg-secondary text-white' },
    { label: 'nav.customers', route: '/customers', icon: Ic('users'), colorClass: 'bg-warning text-white' },
    { label: 'nav.roles', route: '/roles', icon: Ic('shield'), colorClass: 'bg-error text-white' },
  ],
  reports: [
    { label: 'nav.analytics', route: '/analytics', icon: Ic('chart-bar'), colorClass: 'bg-error text-white' },
    { label: 'nav.reports', route: '/reports', icon: Ic('file-text'), colorClass: 'bg-warning text-white' },
    { label: 'nav.taxReports', route: '/tax-reports', icon: Ic('building-bank'), colorClass: 'bg-warning/70 text-white' },
  ],
  system: [
    { label: 'nav.settings', route: '/settings', icon: Ic('settings'), colorClass: 'bg-neutral text-neutral-content' },
    { label: 'nav.notes', route: '/notes', icon: Ic('notes'), colorClass: 'bg-neutral/70 text-neutral-content' },
    { label: 'nav.supportChat', route: '/support-chat', icon: Ic('messages'), colorClass: 'bg-success text-white' },
    { label: 'nav.themeStudio', route: '/theme-studio', icon: Ic('paint'), colorClass: 'bg-secondary text-white' },
    { label: 'nav.about', route: '/about', icon: Ic('heart'), colorClass: 'bg-error text-white' },
  ],
};

/** Quick-access merged page cards shown at the top of the home page */
const QUICK_ACCESS = [
  { label: 'nav.staff', desc: 'nav.staffDesc', route: '/staff', icon: 'users', gradient: 'from-fuchsia-500 to-pink-500' },
  { label: 'nav.productsMerged', desc: 'nav.productsMergedDesc', route: '/products', icon: 'apps', gradient: 'from-blue-500 to-indigo-500' },
  { label: 'nav.salesMerged', desc: 'nav.salesMergedDesc', route: '/sale', icon: 'shopping-cart', gradient: 'from-emerald-500 to-teal-500' },
  { label: 'nav.reportsMerged', desc: 'nav.reportsMergedDesc', route: '/reports', icon: 'chart-bar', gradient: 'from-amber-500 to-orange-500' },
];

export default function Home() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [loadingRoute, setLoadingRoute] = useState<string | null>(null);

  const handleNavigation = (route: string) => {
    setLoadingRoute(route);
    setTimeout(() => navigate(route), 250);
  };

  // ── Data fetching via shared useApiQueries hook ──
  const {
    data: [settingsRes, salesRes, ingredientsRes, employeesRes, kitchenTicketsRes],
    isLoading: kpisLoading,
  } = useApiQueries([
    { command: 'get_settings' },
    { command: 'get_sales' },
    { command: 'get_ingredients', params: { includeInactive: false } },
    { command: 'get_employees', params: { includeInactive: true } },
    { command: 'get_kitchen_tickets', params: { status: null } },
  ]);

  const settings = (settingsRes as Settings | undefined) ?? null;
  const restaurantName = settings?.restaurant_name || 'Forge POS';
  const { formatPrice, currencySymbol } = useCurrency();
  const sales = (Array.isArray(salesRes) ? (salesRes as Sale[]) : []) as Sale[];

  const { todayStats, revDelta, orderDelta } = useDashboardDeltas(sales);

  // ── Derived KPIs from fetched data (useMemo for stability) ──
  const kpis = useMemo(() => {
    if (!salesRes || !ingredientsRes || !employeesRes || !kitchenTicketsRes) return null;
    const s = salesRes as Sale[];
    const i = ingredientsRes as Ingredient[];
    const e = employeesRes as Employee[];
    const k = kitchenTicketsRes as KitchenTicket[];
    const pendingStatuses = ['pending', 'active', 'in-progress'];
    return {
      openTables: s.filter(sale => sale.order_type === 'dine-in' && pendingStatuses.includes(sale.status)).length,
      lowStockCount: i.filter(ing => ing.current_quantity <= ing.reorder_level).length,
      activeEmployees: e.filter(emp => emp.is_active).length,
      activeKitchenTickets: k.filter(t => pendingStatuses.includes(t.status)).length,
    };
  }, [salesRes, ingredientsRes, employeesRes, kitchenTicketsRes]);

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
      background="bg-linear-to-br from-slate-50 via-info/5 to-slate-50 dark:from-slate-950 dark:via-info/10 dark:to-slate-950"
      padding="py-12 md:py-16 lg:py-12"
    >
      {/* ── Header — CSS animated section entry ── */}
      {/* PageWrapper handles the page-level slide-in. This section's
          animate-slide-up provides a gentle entrance for the header content
          without duplicating framer-motion entry animations. */}
      <div className="text-center mb-10 md:mb-12 animate-slide-up">
        <motion.div
          variants={iconSpring}
          initial="initial"
          animate="animate"
          whileHover={{ rotate: 360 }}
          transition={{ duration: 0.6 }}
          className="bg-base-100/60 dark:bg-white/10 backdrop-blur-md rounded-2xl p-5 w-fit mx-auto mb-5 shadow-xl border border-base-300/30 dark:border-white/5"
        >
          <img
            src={defaultLogo}
            alt="Forge POS"
            className="w-14 h-14 md:w-18 md:h-18 object-contain"
            onError={(e) => { e.currentTarget.style.display = 'none'; }}
          />
        </motion.div>
        <h1
          className="text-3xl md:text-4xl lg:text-5xl font-bold text-transparent bg-clip-text
            bg-linear-to-r from-indigo-600 via-purple-600 to-pink-600
            dark:from-indigo-400 dark:via-purple-400 dark:to-pink-400 py-2 animate-fade-in"
          style={{ animationDelay: '0.15s' }}
        >
          {restaurantName}
        </h1>
        <p
          className="text-base-content/50 mt-2 text-sm animate-fade-in"
          style={{ animationDelay: '0.25s' }}
        >
          {t('home.dashboard') || 'Dashboard'}
        </p>
      </div>

      {/* ── Quick Access Cards — FlyonUI card grid ── */}
      <div className="max-w-6xl mx-auto px-2 mb-8 animate-slide-up"
        style={{ animationDelay: '0.1s' }}
      >
        <Card padding="sm" border="theme" className="shadow-sm">
          <div className="grid grid-cols-4 gap-2">
            {QUICK_ACCESS.map((qa, i) => (
              <button
                key={qa.route}
                onClick={() => handleNavigation(qa.route)}
                disabled={loadingRoute !== null}
                style={{ animationDelay: `${0.2 + i * 0.06}s` }}
                className="relative card bg-base-200/50 hover:bg-base-200 dark:bg-white/5 dark:hover:bg-white/10
                  border border-base-300/20 p-3 rounded-xl
                  transition-all duration-200 group disabled:opacity-60 animate-fade-in"
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-2
                  bg-linear-to-br ${qa.gradient} text-white shadow-lg
                  group-hover:scale-110 transition-transform duration-200`}
                >
                  <span className={iconClass(qa.icon, 'w-4 h-4')} />
                </div>
                <span className="text-xs font-semibold text-base-content/70 text-center leading-tight">{t(qa.label)}</span>
                <span className="text-[9px] text-base-content/30 text-center mt-0.5 leading-tight line-clamp-1">{t(qa.desc)}</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* ── Live KPI Dashboard ── */}
      <div className="max-w-6xl mx-auto px-2 mb-8 animate-slide-up"
        style={{ animationDelay: '0.2s' }}
      >
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 md:gap-4">
          {kpisLoading ? (
            <>
              {[1, 2, 3, 4, 5, 6].map(i => (
                <StatCard key={i} title="" value={0} loading />
              ))}
            </>
          ) : (
            <>
              <StatCard
                title={t('home.todaySales', 'Today Sales')}
                value={todayStats.orders}
                desc={`${todayStats.orders === 1 ? '1 order' : `${todayStats.orders} orders`} today — ${orderDelta.pct} vs yesterday`}
                icon={<span className={iconClass('lucide:shopping-cart', 'w-6 h-6')} />}
                sparklineData={sparklines?.orders}
                color="primary"
                onClick={() => handleNavigation('/transactions')}
              />
              <StatCard
                title={t("home.todayRevenue", "Today's Revenue")}
                value={`${currencySymbol} ${todayStats.revenue.toLocaleString()}`}
                desc={todayStats.revenue > 0
                  ? `${formatPrice(todayStats.revenue / (todayStats.orders || 1))} avg — ${revDelta.pct} vs yesterday`
                  : 'No revenue yet'}
                icon={<span className={iconClass('lucide:banknote', 'w-6 h-6')} />}
                sparklineData={sparklines?.revenue}
                color="info"
                onClick={() => handleNavigation('/reports')}
              />
              <StatCard
                title={t('home.openTables', 'Open Tables')}
                value={kpis?.openTables ?? 0}
                desc={kpis?.openTables === 0 ? 'All clear' : `${kpis?.openTables} table${kpis?.openTables !== 1 ? 's' : ''} in service`}
                icon={<span className={iconClass('lucide:utensils', 'w-6 h-6')} />}
                color="warning"
                onClick={() => handleNavigation('/sale')}
              />
              <StatCard
                title={t('home.staff', 'Active Staff')}
                value={kpis?.activeEmployees ?? 0}
                desc={`${kpis?.activeEmployees === 1 ? '1 employee' : `${kpis?.activeEmployees ?? 0} employees`} on payroll`}
                icon={<span className={iconClass('lucide:users', 'w-6 h-6')} />}
                color="secondary"
                onClick={() => handleNavigation('/staff')}
              />
              <StatCard
                title={t('home.lowStock', 'Low Stock')}
                value={kpis?.lowStockCount ?? 0}
                desc={kpis?.lowStockCount === 0 ? 'All stocked' : `${kpis?.lowStockCount} item${kpis?.lowStockCount !== 1 ? 's' : ''} below reorder level`}
                icon={<span className={iconClass('lucide:alert-triangle', 'w-6 h-6')} />}
                color={kpis?.lowStockCount && kpis.lowStockCount > 0 ? 'error' : 'success'}
                onClick={() => handleNavigation('/inventory')}
              />
              <StatCard
                title={t('home.kitchenTickets', 'Kitchen Tickets')}
                value={kpis?.activeKitchenTickets ?? 0}
                desc={kpis?.activeKitchenTickets === 0 ? 'No active orders' : `${kpis?.activeKitchenTickets} ticket${kpis?.activeKitchenTickets !== 1 ? 's' : ''} in progress`}
                icon={<span className={iconClass('lucide:chef-hat', 'w-6 h-6')} />}
                color={kpis?.activeKitchenTickets && kpis.activeKitchenTickets > 0 ? 'warning' : 'success'}
                onClick={() => handleNavigation('/kitchen')}
              />
            </>
          )}
        </div>
      </div>

      {/* ── Categorized Menu Grid — single stagger animation ── */}
      <motion.div
        className="max-w-6xl mx-auto px-2 space-y-8"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        {MENU_CATEGORIES.map((cat) => (
          <div key={cat.id}>
            {/* Category Header */}
            <div className="flex items-center gap-2.5 mb-3 pl-1">
              <span className={`${cat.color}`}>{cat.icon}</span>
              <h2 className={`text-sm font-semibold uppercase tracking-wider ${cat.color}`}>
                {t(cat.label)}
              </h2>
              <div className={`flex-1 h-px bg-gradient-to-r ${cat.color.replace('text-', 'from-').replace('dark:', '')} to-transparent opacity-30 rtl:bg-gradient-to-l`} />
            </div>

            {/* Category Items — staggered children */}
            <motion.div
              className="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 3xl:grid-cols-8 gap-3 md:gap-4"
              variants={{
                hidden: { opacity: 0 },
                show: { opacity: 1, transition: { staggerChildren: 0.035 } },
              }}
              initial="hidden"
              animate="show"
            >
              {(MENU_ITEMS[cat.id] || []).map((menuItem) => {
                const Icon = menuItem.icon;
                const isLoading = loadingRoute === menuItem.route;

                return (
                  <button
                    key={menuItem.route}
                    onClick={() => handleNavigation(menuItem.route)}
                    disabled={loadingRoute !== null}
                    className="relative card bg-base-100/80 dark:bg-white/5 backdrop-blur-sm
                      border-2 border-base-300/40 hover:border-base-300
                      dark:border-white/10 dark:hover:border-white/30
                      p-3 rounded-2xl transition-all duration-300
                      hover:shadow-xl hover:-translate-y-0.5 active:scale-[0.98]
                      group disabled:opacity-60"
                  >

                    {isLoading ? (
                      <div className="w-full flex items-center justify-center py-4">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="w-7 h-7 border-3 border-base-300 border-t-primary rounded-full"
                        />
                      </div>
                    ) : (
                      <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-2
                        ${menuItem.colorClass} shadow-md mx-auto
                        group-hover:scale-110 transition-transform duration-300`}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                    )}

                    <span className="text-sm font-semibold text-base-content/70 text-center leading-tight">
                      {t(menuItem.label)}
                    </span>
                    <span className="text-[10px] text-base-content/30 mt-0.5 text-center leading-tight max-w-[100px]">
                      {t(menuItem.label + 'Desc')}
                    </span>
                  </button>
                );
              })}
            </motion.div>
          </div>
        ))}
      </motion.div>
    </PageLayout>
  );
}
