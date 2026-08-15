import { useState, useMemo } from 'react';
import type { Sale } from '../types';

// ── Shared types ──

export interface DayStats {
  revenue: number;
  orders: number;
  avgOrder: number;
}

export interface DeltaResult {
  pct: string;
  direction: 'up' | 'down' | 'flat';
  color: string;
}

/** Format a date to YYYY-MM-DD string. */
function fmt(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/**
 * Compute a formatted percentage change with direction indicator.
 *
 * Returns `{ pct, direction, color }` where:
 * - `pct` is the formatted percentage string (e.g. "+12.5%")
 * - `direction` is `'up' | 'down' | 'flat'`
 * - `color` is a text color class (`text-green-500`, etc.)
 */
export function delta(current: number, previous: number): DeltaResult {
  if (previous === 0 && current === 0) return { pct: '0%', direction: 'flat', color: 'text-slate-400' };
  if (previous === 0) return { pct: '+100%', direction: 'up', color: 'text-green-500' };
  const pct = ((current - previous) / previous) * 100;
  const formatted = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`;
  if (pct > 0) return { pct: formatted, direction: 'up', color: 'text-green-500' };
  if (pct < 0) return { pct: formatted, direction: 'down', color: 'text-red-500' };
  return { pct: '0%', direction: 'flat', color: 'text-slate-400' };
}

/**
 * Compute aggregate stats (revenue, orders, avgOrder) for a date range.
 */
export function periodStats(sales: Sale[], start: string, end: string): DayStats {
  const periodSales = sales.filter(s => s.date >= start && s.date <= end);
  const revenue = periodSales.reduce((sum, s) => sum + s.total_amount, 0);
  const orders = periodSales.length;
  const avgOrder = orders > 0 ? revenue / orders : 0;
  return { revenue, orders, avgOrder };
}

/**
 * Shared dashboard delta computations.
 *
 * Given a raw `Sale[]` array, returns:
 * - Date strings (`todayStr`, `yesterdayStr`, `lastWeekStr`, `thisWeekStart`, …)
 * - Daily stats (`todayStats`, `yesterdayStats`, `lastWeekStats`)
 * - Daily deltas (`revDelta`, `orderDelta`, `wkRevDelta`, `wkOrderDelta`)
 * - Period state & stats (`periodView`, `setPeriodView`, `currentStats`, `previousStats`)
 * - Period deltas (`periodRevDelta`, `periodOrderDelta`)
 * - Monthly window deltas (`sales30Stats`, `salesPrior30Stats`, `salesRevDelta`, …)
 * - Helper functions (`delta`, `periodStats`, `fmt`)
 * - Trend data (`dailyTrend`)
 */
export function useDashboardDeltas(sales: Sale[]) {
  // ── Date strings (computed on every render for freshness) ──
  const todayStr = fmt(new Date());
  const yesterdayStr = fmt(new Date(Date.now() - 86400000));
  const lastWeekStr = fmt(new Date(Date.now() - 7 * 86400000));

  const thisWeekStart = fmt(new Date(Date.now() - 6 * 86400000));
  const prevWeekStart = fmt(new Date(Date.now() - 13 * 86400000));
  const prevWeekEnd = fmt(new Date(Date.now() - 7 * 86400000));

  const currentMonthStart = fmt(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const prevMonthStart = fmt(new Date(new Date().getFullYear(), new Date().getMonth() - 1, 1));
  const prevMonthEnd = fmt(new Date(new Date().getFullYear(), new Date().getMonth(), 0));

  // 30-day comparison windows (anchored on yesterday for complete days)
  const last30End = yesterdayStr;
  const last30Start = fmt(new Date(Date.now() - 30 * 86400000));
  const prior30Start = fmt(new Date(Date.now() - 60 * 86400000));
  const prior30End = fmt(new Date(Date.now() - 31 * 86400000));

  // ── Sales grouped by date ──
  const salesByDate = useMemo(() => {
    const map = new Map<string, Sale[]>();
    for (const sale of sales) {
      const date = sale.date;
      if (!map.has(date)) map.set(date, []);
      map.get(date)!.push(sale);
    }
    return map;
  }, [sales]);

  // ── Day-level stats ──
  const dayStats = useMemo(() => {
    const compute = (date: string) => {
      const daySales = salesByDate.get(date) || [];
      const revenue = daySales.reduce((s, sale) => s + sale.total_amount, 0);
      const orders = daySales.length;
      return { revenue, orders, avgOrder: orders > 0 ? revenue / orders : 0 };
    };
    return {
      today: compute(todayStr),
      yesterday: compute(yesterdayStr),
      lastWeek: compute(lastWeekStr),
    };
  }, [salesByDate, todayStr, yesterdayStr, lastWeekStr]);

  const todayStats = dayStats.today;
  const yesterdayStats = dayStats.yesterday;
  const lastWeekStats = dayStats.lastWeek;

  // ── Daily deltas ──
  const revDelta = delta(todayStats.revenue, yesterdayStats.revenue);
  const orderDelta = delta(todayStats.orders, yesterdayStats.orders);
  const wkRevDelta = delta(todayStats.revenue, lastWeekStats.revenue);
  const wkOrderDelta = delta(todayStats.orders, lastWeekStats.orders);

  // ── Daily trend (last 14 days) ──
  const dailyTrend = useMemo(() => {
    const days: { date: string; revenue: number; orders: number }[] = [];
    for (let i = 13; i >= 0; i--) {
      const d = fmt(new Date(Date.now() - i * 86400000));
      const daySales = salesByDate.get(d) || [];
      const revenue = daySales.reduce((s, sale) => s + sale.total_amount, 0);
      const orders = daySales.length;
      days.push({ date: d, revenue, orders });
    }
    return days;
  }, [salesByDate]);

  // ── Period (week/month) state ──
  const [periodView, setPeriodView] = useState<'week' | 'month'>('week');

  const thisWeekStats = useMemo(
    () => periodStats(sales, thisWeekStart, todayStr),
    [sales, thisWeekStart, todayStr],
  );
  const prevWeekStats = useMemo(
    () => periodStats(sales, prevWeekStart, prevWeekEnd),
    [sales, prevWeekStart, prevWeekEnd],
  );
  const thisMonthStats = useMemo(
    () => periodStats(sales, currentMonthStart, todayStr),
    [sales, currentMonthStart, todayStr],
  );
  const prevMonthStats = useMemo(
    () => periodStats(sales, prevMonthStart, prevMonthEnd),
    [sales, prevMonthStart, prevMonthEnd],
  );

  const currentStats = periodView === 'week' ? thisWeekStats : thisMonthStats;
  const previousStats = periodView === 'week' ? prevWeekStats : prevMonthStats;

  const periodRevDelta = delta(currentStats.revenue, previousStats.revenue);
  const periodOrderDelta = delta(currentStats.orders, previousStats.orders);

  // ── 30-day monthly window deltas ──
  const sales30Stats = useMemo(
    () => periodStats(sales, last30Start, last30End),
    [sales, last30Start, last30End],
  );
  const salesPrior30Stats = useMemo(
    () => periodStats(sales, prior30Start, prior30End),
    [sales, prior30Start, prior30End],
  );

  const salesRevDelta = delta(sales30Stats.revenue, salesPrior30Stats.revenue);
  const salesOrderDelta = delta(sales30Stats.orders, salesPrior30Stats.orders);
  const salesAvgDelta = delta(sales30Stats.avgOrder, salesPrior30Stats.avgOrder);

  // ── Period trend (last 8 periods) ──
  const periodTrend = useMemo(() => {
    const result: { label: string; revenue: number; orders: number }[] = [];
    const now = new Date();
    if (periodView === 'week') {
      for (let i = 7; i >= 0; i--) {
        const end = fmt(new Date(Date.now() - (i * 7) * 86400000));
        const start = fmt(new Date(Date.now() - (i * 7 + 6) * 86400000));
        const stats = periodStats(sales, start, end);
        result.push({
          label: `${start.slice(5)}-${end.slice(5)}`,
          revenue: stats.revenue,
          orders: stats.orders,
        });
      }
    } else {
      for (let i = 7; i >= 0; i--) {
        const m = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const label = m.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
        const mStart = fmt(m);
        const mEnd = fmt(new Date(now.getFullYear(), now.getMonth() - i + 1, 0));
        const stats = periodStats(sales, mStart, mEnd);
        result.push({ label, revenue: stats.revenue, orders: stats.orders });
      }
    }
    return result;
  }, [sales, periodView]);

  return {
    // Helpers
    delta,
    periodStats,
    fmt,
    // Date strings
    todayStr,
    yesterdayStr,
    lastWeekStr,
    thisWeekStart,
    prevWeekStart,
    prevWeekEnd,
    currentMonthStart,
    prevMonthStart,
    prevMonthEnd,
    last30Start,
    last30End,
    prior30Start,
    prior30End,
    // Sales grouped by date (for per-employee stats, etc.)
    salesByDate,
    // Day stats
    todayStats,
    yesterdayStats,
    lastWeekStats,
    // Daily deltas
    revDelta,
    orderDelta,
    wkRevDelta,
    wkOrderDelta,
    // Daily trend
    dailyTrend,
    // Period state
    periodView,
    setPeriodView,
    currentStats,
    previousStats,
    periodRevDelta,
    periodOrderDelta,
    // Monthly window deltas
    sales30Stats,
    salesPrior30Stats,
    salesRevDelta,
    salesOrderDelta,
    salesAvgDelta,
    // Period trend
    periodTrend,
  };
}
