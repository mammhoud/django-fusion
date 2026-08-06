import { useState, useEffect, useMemo } from 'react';
import PageLayout from '../../components/layout/PageLayout';
import Card from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { invoke } from '@tauri-apps/api/core';
import { AnalyticsData, PaymentMethodRevenue, PaymentMethod, PAYMENT_METHODS, PAYMENT_METHOD_LABELS, PAYMENT_ICONS } from '../../types';
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
  const [paymentRevenue, setPaymentRevenue] = useState<PaymentMethodRevenue[]>([]);
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
      const [analyticsRes, paymentRevRes] = await Promise.all([
        invoke<AnalyticsData>('get_analytics'),
        invoke<PaymentMethodRevenue[]>('get_revenue_by_payment_method'),
      ]);
      setPaymentRevenue(Array.isArray(paymentRevRes) ? paymentRevRes : []);

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
      <div className="min-h-[100dvh] bg-base-200 flex items-center justify-center transition-colors duration-300">
        <div className="text-base-content">{t('analytics.title')}...</div>
      </div>
    );
  }  return (
    <PageLayout
      title={t('analytics.title')}
      background="bg-linear-to-br from-base-200 via-secondary/15 to-base-200"
    >

        {/* Summary Cards — dashboard-style StatCards (same sizing as Home) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4 mb-8">
          <StatCard
            title={t('analytics.totalRevenue')}
            value={formatPrice(data.summary.total_revenue)}
            icon={<span className="ri-money-dollar-box-line ri-24px" />}
            color="primary"
            compact
          />
          <StatCard
            title={t('analytics.growthRate')}
            value={`${growthRate}%`}
            icon={<span className="ri-stock-line ri-24px" />}
            color="info"
            compact
          />
          <StatCard
            title={t('analytics.totalOrders')}
            value={data.summary.total_orders}
            icon={<span className="ri-shopping-cart-line ri-24px" />}
            color="secondary"
            compact
          />
          <StatCard
            title={t('analytics.avgOrderValue')}
            value={formatPrice(data.summary.average_order_value)}
            icon={<span className="ri-money-dollar-box-line ri-24px" />}
            color="warning"
            compact
          />
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

        {/* Revenue by Payment Method — how customers paid */}
        {paymentRevenue.length > 0 && (
          <div className="animate-fade-in mb-2">
            <Card padding="md" transitional>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg sm:text-xl font-bold text-base-content flex items-center gap-2">
                  <span className="ri-bank-card-line ri-20px text-primary" />
                  {t('analytics.paymentMethods')}
                </h2>
                <span className="tag tag--sm tag--ghost">
                  {t('analytics.totalRevenue')}: {formatPrice(paymentRevenue.reduce((s, p) => s + p.revenue, 0))}
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-3">
                {(() => {
                  const total = paymentRevenue.reduce((s, p) => s + p.revenue, 0);
                  return paymentRevenue.map(pr => {
                    const method = (PAYMENT_METHODS as string[]).includes(pr.payment_method)
                      ? (pr.payment_method as PaymentMethod)
                      : 'other';
                    const pct = total > 0 ? (pr.revenue / total) * 100 : 0;
                    return (
                      <div
                        key={pr.payment_method}
                        className="rounded-xl border border-base-300/30 bg-base-100/50 p-4 transition-all duration-200 hover:border-primary/30 hover:bg-base-100/80"
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-8 h-8 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80 flex items-center justify-center">
                            <span className={`${PAYMENT_ICONS[method]} ri-16px`} />
                          </div>
                          <p className="text-sm font-medium text-base-content truncate">
                            {t(`payments.${pr.payment_method}`, PAYMENT_METHOD_LABELS[method] || pr.payment_method)}
                          </p>
                        </div>
                      <p className="text-lg font-bold text-base-content tabular-nums">{formatPrice(pr.revenue)}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="flex-1 h-1.5 rounded-full bg-base-200 dark:bg-base-300/40 overflow-hidden">
                          <div className="h-full rounded-full bg-primary/70 dark:bg-primary/60" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-[11px] text-base-content/50 tabular-nums shrink-0">{pct.toFixed(0)}%</span>
                      </div>
                        <p className="text-[11px] text-base-content/50 mt-1.5">{pr.orders} {t('analytics.paymentOrders')}</p>
                      </div>
                    );
                  });
                })()}
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

