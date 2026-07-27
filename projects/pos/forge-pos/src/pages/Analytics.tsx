import { motion } from 'framer-motion';
import { useState, useEffect, useMemo } from 'react';
import { MdTrendingUp, MdAttachMoney, MdShoppingCart } from 'react-icons/md';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../components/KeyboardShortcutsModal';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { invoke } from '@tauri-apps/api/core';
import { AnalyticsData, Settings } from '../types';
import { useStatusToast } from '../hooks/useStatusToast';
import StatusToast from '../components/StatusToast';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function Analytics() {
  const { t } = useTranslation();
  const [data, setData] = useState<AnalyticsData>({
    daily_revenue: [],
    top_products: [],
    product_distribution: [],
    summary: { total_orders: 0, total_revenue: 0, average_order_value: 0 }
  });
  const [currency, setCurrency] = useState('USD');
  const [loading, setLoading] = useState(true);
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);

  // Status toast — load failures must surface visibly even when there is no
  // future date-range reload path to apply the `quiet` flag to.
  const { status, showError, dismiss } = useStatusToast();

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      
      if (e.key === '?' || e.key === '/') {
        e.preventDefault();
        setShowShortcutHelp(prev => !prev);
        return;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const loadData = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setLoading(true);
    try {
      const [analyticsRes, settingsRes] = await Promise.all([
        invoke<AnalyticsData>('get_analytics'),
        invoke<Settings>('get_settings')
      ]);

      // Ensure we have valid data structure
      setData({
        daily_revenue: analyticsRes?.daily_revenue || [],
        top_products: analyticsRes?.top_products || [],
        product_distribution: analyticsRes?.product_distribution || [],
        summary: analyticsRes?.summary || {
          total_orders: 0,
          total_revenue: 0,
          average_order_value: 0
        }
      });
      setCurrency(settingsRes?.currency || 'USD');
    } catch (error) {
      console.error('Error loading analytics data:', error);
      // Even when the load is quiet, the failure must be visible — silent
      // reloads would leave the user staring at an empty dashboard.
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
      // Set empty data structure on error so the UI degrades gracefully
      setData({
        daily_revenue: [],
        top_products: [],
        product_distribution: [],
        summary: { total_orders: 0, total_revenue: 0, average_order_value: 0 }
      });
    } finally {
      if (!quiet) setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // mount-once only; loadData captures no reactive state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Calculate growth rate
  const growthRate = useMemo(() => {
    if (data.daily_revenue.length < 2) return 0;
    const first = data.daily_revenue[0].revenue;
    const last = data.daily_revenue[data.daily_revenue.length - 1].revenue;
    return ((last - first) / first * 100).toFixed(1);
  }, [data.daily_revenue]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 dark:bg-slate-900 flex items-center justify-center transition-colors duration-300">
        <div className="text-slate-900 dark:text-white">{t('analytics.title')}...</div>
      </div>
    );
  }  return (
    <PageLayout
      title={t('analytics.title')}
      background="bg-linear-to-br from-slate-100 via-purple-100 to-slate-100 dark:from-slate-900 dark:via-purple-900 dark:to-slate-900"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4 sm:gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass card--hover rounded-xl p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-teal-500/20 rounded-lg">
                <MdAttachMoney className="w-6 h-6 text-teal-600 dark:text-teal-500" />
              </div>
              <div>
                <p className="text-slate-600 dark:text-white/60">{t('analytics.totalRevenue')}</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {currency} {data.summary.total_revenue.toFixed(2)}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card--glass card--hover rounded-xl p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <MdTrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-500" />
              </div>
              <div>
                <p className="text-slate-600 dark:text-white/60">{t('analytics.growthRate')}</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{growthRate}%</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card--glass card--hover rounded-xl p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-500/20 rounded-lg">
                <MdShoppingCart className="w-6 h-6 text-purple-600 dark:text-purple-500" />
              </div>
              <div>
                <p className="text-slate-600 dark:text-white/60">{t('analytics.totalOrders')}</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{data.summary.total_orders}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card--glass card--hover rounded-xl p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-500/20 rounded-lg">
                <MdAttachMoney className="w-6 h-6 text-orange-600 dark:text-orange-500" />
              </div>
              <div>
                <p className="text-slate-600 dark:text-white/60">{t('analytics.avgOrderValue')}</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {currency} {data.summary.average_order_value.toFixed(2)}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Empty State Message */}
        {data.summary.total_orders === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass rounded-xl p-8 mb-8 text-center transition-colors duration-300"
          >
            <div className="text-slate-600 dark:text-white/60 text-lg mb-2">{t('analytics.noData')}</div>
            <div className="text-slate-500 dark:text-white/40">
              {t('analytics.noDataHint')}
            </div>
          </motion.div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 3xl:grid-cols-4 gap-5 md:gap-6">
          {/* Revenue Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass rounded-xl p-4 sm:p-6 transition-colors duration-300"
          >
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-4">{t('analytics.revenueTrend')}</h2>
            <div className="h-[250px] sm:h-[300px]" dir="ltr">
              {data.daily_revenue.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.daily_revenue}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0088FE" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#0088FE" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                    <XAxis dataKey="date" stroke="#ffffff60" />
                    <YAxis stroke="#ffffff60" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1f2937', border: 'none' }}
                      labelStyle={{ color: '#ffffff' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#0088FE"
                      fillOpacity={1}
                      fill="url(#colorRevenue)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-slate-500 dark:text-white/40">{t('analytics.noRevenueData')}</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Top Products */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass rounded-xl p-4 sm:p-6 transition-colors duration-300"
          >
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-4">{t('analytics.topProducts')}</h2>
            <div className="h-[250px] sm:h-[300px]" dir="ltr">
              {data.top_products.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.top_products}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                    <XAxis dataKey="name" stroke="#ffffff60" />
                    <YAxis stroke="#ffffff60" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1f2937', border: 'none' }}
                      labelStyle={{ color: '#ffffff' }}
                    />
                    <Bar dataKey="sales" fill="#00C49F" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-slate-500 dark:text-white/40">{t('analytics.noProductData')}</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Product Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass rounded-xl p-4 sm:p-6 transition-colors duration-300"
          >
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-4">{t('analytics.productDistribution')}</h2>
            <div className="h-[250px] sm:h-[300px]" dir="ltr">
              {data.product_distribution.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.product_distribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name} (${value}) ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {data.product_distribution.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: 'none',
                        color: '#ffffff'
                      }}
                      itemStyle={{ color: '#ffffff' }}
                      labelStyle={{ color: '#ffffff' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-slate-500 dark:text-white/40">{t('analytics.noDistributionData')}</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Daily Orders Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass rounded-xl p-4 sm:p-6 transition-colors duration-300"
          >
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-4">{t('analytics.dailyOrders')}</h2>
            <div className="h-[250px] sm:h-[300px]" dir="ltr">
              {data.daily_revenue.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.daily_revenue}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                    <XAxis dataKey="date" stroke="#ffffff60" />
                    <YAxis stroke="#ffffff60" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1f2937', border: 'none' }}
                      labelStyle={{ color: '#ffffff' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="orders"
                      stroke="#FFBB28"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-slate-500 dark:text-white/40">{t('analytics.noOrdersData')}</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      {/* Keyboard Shortcut Help Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcutHelp}
        onClose={() => setShowShortcutHelp(false)}
      />

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}

