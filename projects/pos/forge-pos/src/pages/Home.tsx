// ── Icons use Tabler icon CSS classes via icon-[tabler--*] ──
function Ic(name: string): React.ComponentType<{ className?: string }> {
  return ({ className = '' }) => <span className={`icon-[tabler--${name}] ${className}`} />;
}
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Settings, Sale, Ingredient, Employee, KitchenTicket } from '../types';
import PageLayout from '../components/PageLayout';
import StatCard from '../components/StatCard';
import Card from '../components/Card';
import { useDashboardDeltas } from '../hooks/useDashboardDeltas';
import { useTranslation } from 'react-i18next';
import defaultLogo from '../assets/pos-crest.svg';

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
  color: string;
  borderColor: string;
}

const MENU_CATEGORIES: MenuCategory[] = [
  { id: 'sales', label: 'nav.categorySales', icon: <span className="icon-[tabler--shopping-cart] w-5 h-5" />, color: 'text-success' },
  { id: 'products', label: 'nav.categoryProducts', icon: <span className="icon-[tabler--package] w-5 h-5" />, color: 'text-info' },
  { id: 'staff', label: 'nav.categoryStaff', icon: <span className="icon-[tabler--users] w-5 h-5" />, color: 'text-secondary' },
  { id: 'reports', label: 'nav.categoryReports', icon: <span className="icon-[tabler--chart-bar] w-5 h-5" />, color: 'text-error' },
  { id: 'system', label: 'nav.categorySystem', icon: <span className="icon-[tabler--dashboard] w-5 h-5" />, color: 'text-base-content/70' },
];

const MENU_ITEMS: Record<string, MenuItem[]> = {
  sales: [
    { label: 'nav.newSale', route: '/sale', icon: Ic('shopping-cart'), color: 'from-emerald-400 to-emerald-500 dark:from-emerald-500 dark:to-emerald-600', borderColor: 'border-emerald-300 dark:border-emerald-600' },
    { label: 'nav.kitchen', route: '/kitchen', icon: Ic('tools-kitchen-2'), color: 'from-teal-400 to-teal-500 dark:from-teal-500 dark:to-teal-600', borderColor: 'border-teal-300 dark:border-teal-600' },
    { label: 'nav.transactions', route: '/transactions', icon: Ic('history'), color: 'from-cyan-400 to-cyan-500 dark:from-cyan-500 dark:to-cyan-600', borderColor: 'border-cyan-300 dark:border-cyan-600' },
    { label: 'nav.invoice', route: '/invoice', icon: Ic('file-invoice'), color: 'from-lime-400 to-lime-500 dark:from-lime-500 dark:to-lime-600', borderColor: 'border-lime-300 dark:border-lime-600' },
  ],
  products: [
    { label: 'nav.productManager', route: '/manager', icon: Ic('clipboard-list'), color: 'from-blue-400 to-blue-500 dark:from-blue-500 dark:to-blue-600', borderColor: 'border-blue-300 dark:border-blue-600' },
    { label: 'nav.inventory', route: '/inventory', icon: Ic('package'), color: 'from-sky-400 to-sky-500 dark:from-sky-500 dark:to-sky-600', borderColor: 'border-sky-300 dark:border-sky-600' },
    { label: 'nav.recipes', route: '/recipes', icon: Ic('flask'), color: 'from-indigo-400 to-indigo-500 dark:from-indigo-500 dark:to-indigo-600', borderColor: 'border-indigo-300 dark:border-indigo-600' },
    { label: 'nav.suppliers', route: '/suppliers', icon: Ic('truck'), color: 'from-violet-400 to-violet-500 dark:from-violet-500 dark:to-violet-600', borderColor: 'border-violet-300 dark:border-violet-600' },
  ],
  staff: [
    { label: 'nav.staff', route: '/staff', icon: Ic('users'), color: 'from-fuchsia-400 to-fuchsia-500 dark:from-fuchsia-500 dark:to-fuchsia-600', borderColor: 'border-fuchsia-300 dark:border-fuchsia-600' },
    { label: 'nav.customers', route: '/customers', icon: Ic('users'), color: 'from-orange-400 to-orange-500 dark:from-orange-500 dark:to-orange-600', borderColor: 'border-orange-300 dark:border-orange-600' },
    { label: 'nav.roles', route: '/roles', icon: Ic('shield'), color: 'from-red-400 to-red-500 dark:from-red-500 dark:to-red-600', borderColor: 'border-red-300 dark:border-red-600' },
  ],
  reports: [
    { label: 'nav.analytics', route: '/analytics', icon: Ic('chart-bar'), color: 'from-rose-400 to-rose-500 dark:from-rose-500 dark:to-rose-600', borderColor: 'border-rose-300 dark:border-rose-600' },
    { label: 'nav.reports', route: '/reports', icon: Ic('file-text'), color: 'from-amber-400 to-amber-500 dark:from-amber-500 dark:to-amber-600', borderColor: 'border-amber-300 dark:border-amber-600' },
    { label: 'nav.taxReports', route: '/tax-reports', icon: Ic('building-bank'), color: 'from-yellow-400 to-yellow-500 dark:from-yellow-500 dark:to-yellow-600', borderColor: 'border-yellow-300 dark:border-yellow-600' },
  ],
  system: [
    { label: 'nav.settings', route: '/settings', icon: Ic('settings'), color: 'from-slate-400 to-slate-500 dark:from-slate-500 dark:to-slate-600', borderColor: 'border-slate-300 dark:border-slate-600' },
    { label: 'nav.receiptTemplates', route: '/receipt-templates', icon: Ic('receipt'), color: 'from-stone-400 to-stone-500 dark:from-stone-500 dark:to-stone-600', borderColor: 'border-stone-300 dark:border-stone-600' },
    { label: 'nav.supportChat', route: '/support-chat', icon: Ic('messages'), color: 'from-green-400 to-green-500 dark:from-green-500 dark:to-green-600', borderColor: 'border-green-300 dark:border-green-600' },
    { label: 'nav.themeShowcase', route: '/theme-showcase', icon: Ic('palette'), color: 'from-indigo-400 to-indigo-500 dark:from-indigo-500 dark:to-indigo-600', borderColor: 'border-indigo-300 dark:border-indigo-600' },
    { label: 'nav.themeStudio', route: '/theme-studio', icon: Ic('paint'), color: 'from-purple-400 to-purple-500 dark:from-purple-500 dark:to-purple-600', borderColor: 'border-purple-300 dark:border-purple-600' },
    { label: 'nav.about', route: '/about', icon: Ic('heart'), color: 'from-rose-400 to-rose-500 dark:from-rose-500 dark:to-rose-600', borderColor: 'border-rose-300 dark:border-rose-600' },
  ],
};

/** Quick-access merged page cards shown at the top of the home page */
const QUICK_ACCESS = [
  { label: 'nav.staff', desc: 'nav.staffDesc', route: '/staff', icon: 'users', gradient: 'from-fuchsia-500 to-pink-500', color: 'text-fuchsia-400' },
  { label: 'nav.productsMerged', desc: 'nav.productsMergedDesc', route: '/products', icon: 'apps', gradient: 'from-blue-500 to-indigo-500', color: 'text-blue-400' },
  { label: 'nav.salesMerged', desc: 'nav.salesMergedDesc', route: '/sale', icon: 'shopping-cart', gradient: 'from-emerald-500 to-teal-500', color: 'text-emerald-400' },
  { label: 'nav.reportsMerged', desc: 'nav.reportsMergedDesc', route: '/reports', icon: 'chart-bar', gradient: 'from-amber-500 to-orange-500', color: 'text-amber-400' },
];

export default function Home() {
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.06 } },
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: {
      opacity: 1,
      y: 0,
      transition: { type: 'spring' as const, stiffness: 120, damping: 14 },
    },
  };

  const iconAnimation = {
    initial: { scale: 0 },
    animate: { scale: 1, transition: { type: 'spring' as const, stiffness: 260, damping: 20 } },
  };

  const { t } = useTranslation();
  const navigate = useNavigate();
  const [restaurantName, setRestaurantName] = useState('Forge POS');
  const [currency, setCurrency] = useState('$');
  const [loadingRoute, setLoadingRoute] = useState<string | null>(null);
  const [sales, setSales] = useState<Sale[]>([]);
  const [kpis, setKpis] = useState<{ openTables: number; lowStockCount: number; activeEmployees: number; activeKitchenTickets: number } | null>(null);
  const [kpisLoading, setKpisLoading] = useState(true);
  const [sparklines, setSparklines] = useState<{
    revenue: { value: number }[];
    orders: { value: number }[];
  } | null>(null);

  const { todayStats, revDelta, orderDelta } = useDashboardDeltas(sales);

  const handleNavigation = (route: string) => {
    setLoadingRoute(route);
    setTimeout(() => navigate(route), 250);
  };

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [settingsRes, salesRes, ingredientsRes, employeesRes, kitchenTicketsRes] = await Promise.all([
          invoke<Settings>('get_settings'),
          invoke<Sale[]>('get_sales'),
          invoke<Ingredient[]>('get_ingredients', { includeInactive: false }),
          invoke<Employee[]>('get_employees', { includeInactive: true }),
          invoke<KitchenTicket[]>('get_kitchen_tickets', { status: null }),
        ]);

        if (settingsRes) {
          if (settingsRes.restaurant_name) setRestaurantName(settingsRes.restaurant_name);
          if (settingsRes.currency) setCurrency(settingsRes.currency);
        }
        setSales(Array.isArray(salesRes) ? salesRes : []);

        const pendingStatuses = ['pending', 'active', 'in-progress'];
        const openTables = salesRes.filter(s => s.order_type === 'dine-in' && pendingStatuses.includes(s.status)).length;
        const lowStockCount = ingredientsRes.filter(i => i.current_quantity <= i.reorder_level).length;
        const activeEmployees = employeesRes.filter(e => e.is_active).length;
        const activeKitchenTickets = kitchenTicketsRes.filter(t => pendingStatuses.includes(t.status)).length;

        const dayKeys: string[] = [];
        for (let i = 6; i >= 0; i--) {
          const d = new Date(Date.now() - i * 86400000);
          dayKeys.push(d.toISOString().slice(0, 10));
        }
        const revenue: { value: number }[] = [];
        const orders: { value: number }[] = [];
        for (const date of dayKeys) {
          const daySales = salesRes.filter(s => s.date === date);
          revenue.push({ value: daySales.reduce((sum, s) => sum + s.total_amount, 0) });
          orders.push({ value: daySales.length });
        }
        setSparklines({ revenue, orders });

        setKpis({ openTables, lowStockCount, activeEmployees, activeKitchenTickets });
      } catch {
        setKpis({ openTables: 0, lowStockCount: 0, activeEmployees: 0, activeKitchenTickets: 0 });
      } finally {
        setKpisLoading(false);
      }
    };
    loadDashboard();
  }, []);

  return (
    <PageLayout
      showNav={false}
      background="bg-linear-to-br from-slate-50 via-info/5 to-slate-50 dark:from-slate-950 dark:via-info/10 dark:to-slate-950"
      padding="py-12 md:py-16 lg:py-12"
    >
      {/* ── Header ── */}
      <motion.div
        className="text-center mb-10 md:mb-12"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          initial={iconAnimation.initial}
          animate={iconAnimation.animate}
          whileHover={{ rotate: 360 }}
          transition={{ duration: 0.6 }}
          className="bg-white/40 dark:bg-white/10 backdrop-blur-md rounded-2xl p-5 w-fit mx-auto mb-5 shadow-xl border border-white/20 dark:border-white/5"
        >
          <img
            src={defaultLogo}
            alt="Forge POS"
            className="w-14 h-14 md:w-18 md:h-18 object-contain"
            onError={(e) => { e.currentTarget.style.display = 'none'; }}
          />
        </motion.div>
        <motion.h1
          className="text-3xl md:text-4xl lg:text-5xl font-bold text-transparent bg-clip-text
            bg-linear-to-r from-indigo-600 via-purple-600 to-pink-600
            dark:from-indigo-400 dark:via-purple-400 dark:to-pink-400 py-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {restaurantName}
        </motion.h1>
        <motion.p
          className="text-base-content/50 mt-2 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {t('home.dashboard') || 'Dashboard'}
        </motion.p>
      </motion.div>

      {/* ── Quick Access Cards ── */}
      <motion.div
        className="max-w-6xl mx-auto px-2 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card padding="md" className="shadow-sm border border-white/20 dark:border-white/10">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {QUICK_ACCESS.map(qa => (
              <motion.button
                key={qa.route}
                onClick={() => handleNavigation(qa.route)}
                whileHover={{ y: -3, scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                disabled={loadingRoute !== null}
                className="relative flex flex-col items-center p-4 rounded-xl bg-base-200/50 hover:bg-base-200
                  dark:bg-white/5 dark:hover:bg-white/10 border border-base-300/30
                  transition-all duration-200 group disabled:opacity-60"
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2
                  bg-linear-to-br ${qa.gradient} text-white shadow-lg shadow-${qa.gradient.replace('from-', '').split(' ')[0]}/20
                  group-hover:scale-110 transition-transform duration-200`}
                >
                  <span className={`icon-[tabler--${qa.icon}] w-5 h-5`} />
                </div>
                <span className="text-xs font-semibold text-base-content text-center">{t(qa.label)}</span>
                <span className="text-[9px] text-base-content/40 text-center mt-0.5 leading-tight">{t(qa.desc)}</span>
              </motion.button>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* ── Live KPI Dashboard ── */}
      <div className="max-w-6xl mx-auto px-2 mb-8">
        <div className="grid grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
          {kpisLoading ? (
            <>
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="stat rounded-xl bg-white/40 dark:bg-white/5 backdrop-blur-sm border border-white/20 animate-pulse">
                  <div className="stat-title"><div className="h-3 w-16 rounded bg-base-300/50" /></div>
                  <div className="stat-value"><div className="h-7 w-20 rounded bg-base-300/50 mt-1" /></div>
                  <div className="stat-desc"><div className="h-2.5 w-24 rounded bg-base-300/50 mt-1" /></div>
                </div>
              ))}
            </>
          ) : (
            <>
              <StatCard
                title={t('home.todaySales', 'Today Sales')}
                value={todayStats.orders}
                desc={`${todayStats.orders === 1 ? '1 order' : `${todayStats.orders} orders`} today — ${orderDelta.pct} vs yesterday`}
                icon={<span className="icon-[tabler--shopping-cart] w-6 h-6" />}
                sparklineData={sparklines?.orders}
                color="primary"
                onClick={() => handleNavigation('/transactions')}
              />
              <StatCard
                title={t("home.todayRevenue", "Today's Revenue")}
                value={`${currency} ${todayStats.revenue.toLocaleString()}`}
                desc={todayStats.revenue > 0
                  ? `${currency}${(todayStats.revenue / (todayStats.orders || 1)).toFixed(2)} avg — ${revDelta.pct} vs yesterday`
                  : 'No revenue yet'}
                icon={<span className="icon-[tabler--moneybag] w-6 h-6" />}
                sparklineData={sparklines?.revenue}
                color="info"
                onClick={() => handleNavigation('/reports')}
              />
              <StatCard
                title={t('home.openTables', 'Open Tables')}
                value={kpis?.openTables ?? 0}
                desc={kpis?.openTables === 0 ? 'All clear' : `${kpis?.openTables} table${kpis?.openTables !== 1 ? 's' : ''} in service`}
                icon={<span className="icon-[tabler--building-store] w-6 h-6" />}
                color="warning"
                onClick={() => handleNavigation('/sale')}
              />
              <StatCard
                title={t('home.staff', 'Active Staff')}
                value={kpis?.activeEmployees ?? 0}
                desc={`${kpis?.activeEmployees === 1 ? '1 employee' : `${kpis?.activeEmployees ?? 0} employees`} on payroll`}
                icon={<span className="icon-[tabler--users] w-6 h-6" />}
                color="secondary"
                onClick={() => handleNavigation('/staff')}
              />
              <StatCard
                title={t('home.lowStock', 'Low Stock')}
                value={kpis?.lowStockCount ?? 0}
                desc={kpis?.lowStockCount === 0 ? 'All stocked' : `${kpis?.lowStockCount} item${kpis?.lowStockCount !== 1 ? 's' : ''} below reorder level`}
                icon={<span className="icon-[tabler--alert-triangle] w-6 h-6" />}
                color={kpis?.lowStockCount && kpis.lowStockCount > 0 ? 'error' : 'success'}
                onClick={() => handleNavigation('/inventory')}
              />
              <StatCard
                title={t('home.kitchenTickets', 'Kitchen Tickets')}
                value={kpis?.activeKitchenTickets ?? 0}
                desc={kpis?.activeKitchenTickets === 0 ? 'No active orders' : `${kpis?.activeKitchenTickets} ticket${kpis?.activeKitchenTickets !== 1 ? 's' : ''} in progress`}
                icon={<span className="icon-[tabler--tools-kitchen-2] w-6 h-6" />}
                color={kpis?.activeKitchenTickets && kpis.activeKitchenTickets > 0 ? 'warning' : 'success'}
                onClick={() => handleNavigation('/kitchen')}
              />
            </>
          )}
        </div>
      </div>

      {/* ── Categorized Menu Grid ── */}
      <div className="max-w-6xl mx-auto px-2 space-y-8">
        {MENU_CATEGORIES.map((cat, catIdx) => (
          <motion.section
            key={cat.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: catIdx * 0.08 }}
          >
            {/* Category Header */}
            <div className="flex items-center gap-2.5 mb-3 pl-1">
              <span className={`${cat.color}`}>{cat.icon}</span>
              <h2 className={`text-sm font-semibold uppercase tracking-wider ${cat.color}`}>
                {t(cat.label)}
              </h2>
              <div className={`flex-1 h-px bg-gradient-to-r ${cat.color.replace('text-', 'from-').replace('dark:', '')} to-transparent opacity-30`} />
            </div>

            {/* Category Items */}
            <motion.div
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 3xl:grid-cols-8 gap-3 md:gap-4"
              variants={container}
              initial="hidden"
              animate="show"
            >
              {(MENU_ITEMS[cat.id] || []).map((menuItem) => {
                const Icon = menuItem.icon;
                const isLoading = loadingRoute === menuItem.route;

                return (
                  <motion.button
                    key={menuItem.route}
                    variants={item}
                    onClick={() => handleNavigation(menuItem.route)}
                    whileHover={{ y: -4, scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    disabled={loadingRoute !== null}
                    className={`relative flex flex-col items-center p-4 rounded-2xl transition-all duration-300
                      bg-white/80 dark:bg-white/5 backdrop-blur-sm
                      border-2 ${menuItem.borderColor}
                      hover:shadow-xl hover:border-opacity-100
                      group disabled:opacity-60`}
                  >
                    <div className={`absolute top-0 left-0 right-0 h-1 rounded-t-xl bg-gradient-to-r ${menuItem.color} opacity-80`} />
                    {isLoading ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-8 h-8 mb-1.5 border-3 border-slate-300 border-t-slate-600 rounded-full"
                      />
                    ) : (
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-2
                        bg-gradient-to-br ${menuItem.color} text-white shadow-md
                        group-hover:scale-110 transition-transform duration-300`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                    )}

                    <span className="text-sm font-semibold text-base-content text-center leading-tight">
                      {t(menuItem.label)}
                    </span>
                    <span className="text-[10px] text-base-content/50 mt-0.5 text-center leading-tight max-w-[110px]">
                      {t(menuItem.label + 'Desc')}
                    </span>
                  </motion.button>
                );
              })}
            </motion.div>
          </motion.section>
        ))}
      </div>
    </PageLayout>
  );
}
