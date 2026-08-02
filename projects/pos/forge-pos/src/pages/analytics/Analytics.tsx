import { useState, useEffect, useMemo } from 'react';
import PageLayout from '../../components/layout/PageLayout';
import Card from '../../components/ui/Card';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { invoke } from '@tauri-apps/api/core';
import { AnalyticsData } from '../../types';
import { useStatusToast } from '../../hooks/useStatusToast';
import { useCurrency } from '../../contexts/CurrencyContext';
import StatusToast from '../../components/ui/StatusToast';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function Analytics() {
  const { t } = useTranslation();
  const [data, setData] = useState<AnalyticsData>({
    daily_revenue: [],
    top_products: [],
    product_distribution: [],
    summary: { total_orders: 0, total_revenue: 0, average_order_value: 0 }
  });
  const { formatPrice } = useCurrency();
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
      const [analyticsRes] = await Promise.all([
        invoke<AnalyticsData>('get_analytics'),
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
      <div className="min-h-screen bg-base-200 flex items-center justify-center transition-colors duration-300">
        <div className="text-base-content">{t('analytics.title')}...</div>
      </div>
    );
  }  return (
    <PageLayout
      title={t('analytics.title')}
      background="bg-linear-to-br from-base-200 via-secondary/15 to-base-200"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4 sm:gap-6 mb-8">
          <div className="animate-fade-in">
            <Card padding="xl" hover>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-primary/20 rounded-lg">
                  <span className="icon-[tabler--moneybag] w-6 h-6 text-info" />
                </div>
                <div>
                  <p className="text-base-content/60">{t('analytics.totalRevenue')}</p>
                  <p className="text-2xl font-bold text-base-content">
                    {formatPrice(data.summary.total_revenue)}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          <div className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <Card padding="xl" hover>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-info/20 rounded-lg">
                  <span className="icon-[tabler--trending-up] w-6 h-6 text-info" />
                </div>
                <div>
                  <p className="text-base-content/60">{t('analytics.growthRate')}</p>
                  <p className="text-2xl font-bold text-base-content">{growthRate}%</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <Card padding="xl" hover>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-secondary/20 rounded-lg">
                  <span className="icon-[tabler--shopping-cart] w-6 h-6 text-secondary" />
                </div>
                <div>
                  <p className="text-base-content/60">{t('analytics.totalOrders')}</p>
                  <p className="text-2xl font-bold text-base-content">{data.summary.total_orders}</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <Card padding="xl" hover>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-warning/20 rounded-lg">
                  <span className="icon-[tabler--moneybag] w-6 h-6 text-warning" />
                </div>
                <div>
                  <p className="text-base-content/60">{t('analytics.avgOrderValue')}</p>
                  <p className="text-2xl font-bold text-base-content">
                    {formatPrice(data.summary.average_order_value)}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Empty State Message */}
        {data.summary.total_orders === 0 && (
          <div className="animate-fade-in">
            <Card padding="2xl" center transitional className="mb-8">
              <div className="text-base-content/60 text-lg mb-2">{t('analytics.noData')}</div>
              <div className="text-base-content/50">
                {t('analytics.noDataHint')}
              </div>
            </Card>
          </div>
        )}

        {/* Charts Grid — medium card padding with tiny margins between cells */}
        <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 3xl:grid-cols-4 gap-2 sm:gap-2 md:gap-3">
          {/* Revenue Trend */}
          <div className="animate-fade-in">
            <Card padding="md" transitional className="p-4 sm:p-5">
              <h2 className="text-lg sm:text-xl font-bold text-base-content mb-4">{t('analytics.revenueTrend')}</h2>
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
                    <p className="text-base-content/50">{t('analytics.noRevenueData')}</p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Top Products */}
          <div className="animate-fade-in">
            <Card padding="md" transitional className="p-4 sm:p-5">
              <h2 className="text-lg sm:text-xl font-bold text-base-content mb-4">{t('analytics.topProducts')}</h2>
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
                    <p className="text-base-content/50">{t('analytics.noProductData')}</p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Product Distribution */}
          <div className="animate-fade-in">
            <Card padding="md" transitional className="p-4 sm:p-5">
              <h2 className="text-lg sm:text-xl font-bold text-base-content mb-4">{t('analytics.productDistribution')}</h2>
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
                    <p className="text-base-content/50">{t('analytics.noDistributionData')}</p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Daily Orders Trend */}
          <div className="animate-fade-in">
            <Card padding="md" transitional className="p-4 sm:p-5">
              <h2 className="text-lg sm:text-xl font-bold text-base-content mb-4">{t('analytics.dailyOrders')}</h2>
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
                    <p className="text-base-content/50">{t('analytics.noOrdersData')}</p>
                  </div>
                )}
              </div>
            </Card>
          </div>
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

