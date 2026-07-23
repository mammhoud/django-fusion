import { FaClipboardList, FaChartBar, FaHistory, FaCog, FaHeart, FaBoxes, FaUsers, FaMortarPestle, FaFileAlt, FaMoneyBillWave, FaComments, FaFileInvoiceDollar, FaStickyNote } from 'react-icons/fa';
import { MdPointOfSale, MdPeople, MdLocalShipping, MdKitchen, MdEvent, MdReceiptLong, MdAccountBalance, MdSecurity, MdDashboard } from 'react-icons/md';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useGetSettingsQuery } from '../store/api/endpoints/core';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import defaultLogo from '../assets/pos-crest.svg';
import { isTauri } from '../utils/tauri';

// ── FlyonUI-inspired semantic category definitions ──
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
  { id: 'sales', label: 'nav.categorySales', icon: <MdPointOfSale className="w-5 h-5" />, color: 'text-emerald-600 dark:text-emerald-400' },
  { id: 'products', label: 'nav.categoryProducts', icon: <FaBoxes className="w-5 h-5" />, color: 'text-blue-600 dark:text-blue-400' },
  { id: 'staff', label: 'nav.categoryStaff', icon: <FaUsers className="w-5 h-5" />, color: 'text-purple-600 dark:text-purple-400' },
  { id: 'reports', label: 'nav.categoryReports', icon: <FaChartBar className="w-5 h-5" />, color: 'text-rose-600 dark:text-rose-400' },
  { id: 'system', label: 'nav.categorySystem', icon: <MdDashboard className="w-5 h-5" />, color: 'text-slate-600 dark:text-slate-400' },
];

const MENU_ITEMS: Record<string, MenuItem[]> = {
  sales: [
    { label: 'nav.newSale', route: '/sale', icon: MdPointOfSale, color: 'from-emerald-400 to-emerald-500 dark:from-emerald-500 dark:to-emerald-600', borderColor: 'border-emerald-300 dark:border-emerald-600' },
    { label: 'nav.kitchen', route: '/kitchen', icon: MdKitchen, color: 'from-teal-400 to-teal-500 dark:from-teal-500 dark:to-teal-600', borderColor: 'border-teal-300 dark:border-teal-600' },
    { label: 'nav.transactions', route: '/transactions', icon: FaHistory, color: 'from-cyan-400 to-cyan-500 dark:from-cyan-500 dark:to-cyan-600', borderColor: 'border-cyan-300 dark:border-cyan-600' },
    { label: 'nav.invoice', route: '/invoice', icon: FaFileInvoiceDollar, color: 'from-lime-400 to-lime-500 dark:from-lime-500 dark:to-lime-600', borderColor: 'border-lime-300 dark:border-lime-600' },
  ],
  products: [
    { label: 'nav.productManager', route: '/manager', icon: FaClipboardList, color: 'from-blue-400 to-blue-500 dark:from-blue-500 dark:to-blue-600', borderColor: 'border-blue-300 dark:border-blue-600' },
    { label: 'nav.inventory', route: '/inventory', icon: FaBoxes, color: 'from-sky-400 to-sky-500 dark:from-sky-500 dark:to-sky-600', borderColor: 'border-sky-300 dark:border-sky-600' },
    { label: 'nav.recipes', route: '/recipes', icon: FaMortarPestle, color: 'from-indigo-400 to-indigo-500 dark:from-indigo-500 dark:to-indigo-600', borderColor: 'border-indigo-300 dark:border-indigo-600' },
    { label: 'nav.suppliers', route: '/suppliers', icon: MdLocalShipping, color: 'from-violet-400 to-violet-500 dark:from-violet-500 dark:to-violet-600', borderColor: 'border-violet-300 dark:border-violet-600' },
  ],
  staff: [
    { label: 'nav.employees', route: '/employees', icon: FaUsers, color: 'from-purple-400 to-purple-500 dark:from-purple-500 dark:to-purple-600', borderColor: 'border-purple-300 dark:border-purple-600' },
    { label: 'nav.schedule', route: '/schedule', icon: MdEvent, color: 'from-fuchsia-400 to-fuchsia-500 dark:from-fuchsia-500 dark:to-fuchsia-600', borderColor: 'border-fuchsia-300 dark:border-fuchsia-600' },
    { label: 'nav.payroll', route: '/payroll', icon: FaMoneyBillWave, color: 'from-pink-400 to-pink-500 dark:from-pink-500 dark:to-pink-600', borderColor: 'border-pink-300 dark:border-pink-600' },
    { label: 'nav.customers', route: '/customers', icon: MdPeople, color: 'from-orange-400 to-orange-500 dark:from-orange-500 dark:to-orange-600', borderColor: 'border-orange-300 dark:border-orange-600' },
    { label: 'nav.roles', route: '/roles', icon: MdSecurity, color: 'from-red-400 to-red-500 dark:from-red-500 dark:to-red-600', borderColor: 'border-red-300 dark:border-red-600' },
  ],
  reports: [
    { label: 'nav.analytics', route: '/analytics', icon: FaChartBar, color: 'from-rose-400 to-rose-500 dark:from-rose-500 dark:to-rose-600', borderColor: 'border-rose-300 dark:border-rose-600' },
    { label: 'nav.reports', route: '/reports', icon: FaFileAlt, color: 'from-amber-400 to-amber-500 dark:from-amber-500 dark:to-amber-600', borderColor: 'border-amber-300 dark:border-amber-600' },
    { label: 'nav.taxReports', route: '/tax-reports', icon: MdAccountBalance, color: 'from-yellow-400 to-yellow-500 dark:from-yellow-500 dark:to-yellow-600', borderColor: 'border-yellow-300 dark:border-yellow-600' },
  ],
  system: [
    { label: 'nav.settings', route: '/settings', icon: FaCog, color: 'from-slate-400 to-slate-500 dark:from-slate-500 dark:to-slate-600', borderColor: 'border-slate-300 dark:border-slate-600' },
    { label: 'nav.notes', route: '/notes', icon: FaStickyNote, color: 'from-amber-400 to-amber-500 dark:from-amber-500 dark:to-amber-600', borderColor: 'border-amber-300 dark:border-amber-600' },
    { label: 'nav.receiptTemplates', route: '/receipt-templates', icon: MdReceiptLong, color: 'from-stone-400 to-stone-500 dark:from-stone-500 dark:to-stone-600', borderColor: 'border-stone-300 dark:border-stone-600' },
    { label: 'nav.supportChat', route: '/support-chat', icon: FaComments, color: 'from-green-400 to-green-500 dark:from-green-500 dark:to-green-600', borderColor: 'border-green-300 dark:border-green-600' },
    { label: 'nav.about', route: '/about', icon: FaHeart, color: 'from-rose-400 to-rose-500 dark:from-rose-500 dark:to-rose-600', borderColor: 'border-rose-300 dark:border-rose-600' },
  ],
};

export default function Home() {
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.06 } },
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 120, damping: 14 } },
  };

  const iconAnimation = {
    initial: { scale: 0 },
    animate: { scale: 1, transition: { type: 'spring' as const, stiffness: 260, damping: 20 } },
  };

  const { t } = useTranslation();
  const navigate = useNavigate();
  const [restaurantName, setRestaurantName] = useState('Forge');
  const [logo, setLogo] = useState<string | null>(null);
  const [loadingRoute, setLoadingRoute] = useState<string | null>(null);

  const { data: settingsRes } = useGetSettingsQuery();

  const handleNavigation = (route: string) => {
    setLoadingRoute(route);
    setTimeout(() => navigate(route), 250);
  };

  useEffect(() => {
    if (settingsRes) {
      const s = settingsRes as any;
      if (s.restaurant_name) setRestaurantName(s.restaurant_name);
      if (s.logo) setLogo(s.logo);
    } else if (!isTauri) {
      setRestaurantName('Forge');
    }
  }, [settingsRes]);

  useEffect(() => {
    if (!isTauri || settingsRes) return;
    const loadLegacy = async () => {
      const { invoke } = await import('@tauri-apps/api/core');
      try {
        const response = await invoke<any>('get_settings');
        if (response) {
          if (response.restaurant_name) setRestaurantName(response.restaurant_name);
          if (response.logo) setLogo(response.logo);
        }
      } catch { /* silent */ }
    };
    loadLegacy();
  }, [settingsRes]);

  return (
    <PageLayout
      showNav={false}
      background="bg-linear-to-br from-slate-50 via-indigo-50 to-slate-50 dark:from-slate-950 dark:via-indigo-950 dark:to-slate-950"
      padding="py-12 md:py-16 lg:py-12"
    >
      <motion.div className="text-center mb-10 md:mb-12" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <motion.div initial={iconAnimation.initial} animate={iconAnimation.animate} whileHover={{ rotate: 360 }} transition={{ duration: 0.6 }}
          className="bg-white/40 dark:bg-white/10 backdrop-blur-md rounded-2xl p-5 w-fit mx-auto mb-5 shadow-xl border border-white/20 dark:border-white/5">
          <img src={logo || defaultLogo} alt="Logo" className="w-14 h-14 md:w-18 md:h-18 object-contain" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
        </motion.div>
        <motion.h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-transparent bg-clip-text bg-linear-to-r from-indigo-600 via-purple-600 to-pink-600 dark:from-indigo-400 dark:via-purple-400 dark:to-pink-400 py-2"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>{restaurantName}</motion.h1>
        <motion.p className="text-slate-500 dark:text-slate-400 mt-2 text-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          {t('home.dashboard') || 'Dashboard'}
        </motion.p>
      </motion.div>

      <div className="max-w-6xl mx-auto px-2 space-y-8">
        {MENU_CATEGORIES.map((cat, catIdx) => (
          <motion.section key={cat.id} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: catIdx * 0.08 }}>
            <div className="flex items-center gap-2.5 mb-3 pl-1">
              <span className={cat.color}>{cat.icon}</span>
              <h2 className={`text-sm font-semibold uppercase tracking-wider ${cat.color}`}>{t(cat.label)}</h2>
              <div className={`flex-1 h-px bg-gradient-to-r ${cat.color.replace('text-', 'from-').replace('dark:', '')} to-transparent opacity-30`} />
            </div>
            <motion.div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 md:gap-4" variants={container} initial="hidden" animate="show">
              {(MENU_ITEMS[cat.id] || []).map((menuItem) => {
                const Icon = menuItem.icon;
                const isLoading = loadingRoute === menuItem.route;
                return (
                  <motion.button key={menuItem.route} variants={item} onClick={() => handleNavigation(menuItem.route)}
                    whileHover={{ y: -4, scale: 1.02 }} whileTap={{ scale: 0.97 }} disabled={loadingRoute !== null}
                    className={`relative flex flex-col items-center p-4 rounded-2xl transition-all duration-300 bg-white/80 dark:bg-white/5 backdrop-blur-sm border-2 ${menuItem.borderColor} hover:shadow-xl hover:border-opacity-100 group disabled:opacity-60`}>
                    <div className={`absolute top-0 left-0 right-0 h-1 rounded-t-xl bg-gradient-to-r ${menuItem.color} opacity-80`} />
                    {isLoading ? (
                      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-8 h-8 mb-1.5 border-3 border-slate-300 border-t-slate-600 rounded-full" />
                    ) : (
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-2 bg-gradient-to-br ${menuItem.color} text-white shadow-md group-hover:scale-110 transition-transform duration-300`}>
                        <Icon className="w-6 h-6" />
                      </div>
                    )}
                    <span className="text-sm font-semibold text-slate-800 dark:text-white text-center leading-tight">{t(menuItem.label)}</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 text-center leading-tight max-w-[110px]">{t(menuItem.label + 'Desc')}</span>
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
