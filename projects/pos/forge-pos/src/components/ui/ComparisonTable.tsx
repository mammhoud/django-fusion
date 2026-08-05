import { useMemo } from 'react';
import type { Sale } from '../../types';
import Card from './Card';
import { useTranslation } from 'react-i18next';

// ── Types ──

export interface ComparisonFilter {
  label: string;
  periodALabel: string;
  periodBLabel: string;
  startA: string;
  endA: string;
  startB: string;
  endB: string;
}

interface ComparisonTableProps {
  sales: Sale[];
  filter: ComparisonFilter;
  currency?: string;
  onDismiss: () => void;
}

/**
 * ComparisonTable — click-to-filter detail view.
 *
 * Shows sales from two date-range periods in a merged table with a
 * "Period" column so the user can inspect the records contributing
 * to a delta stat card value.
 */
export default function ComparisonTable({
  sales,
  filter,
  currency = 'USD',
  onDismiss,
}: ComparisonTableProps) {
  const { t } = useTranslation();

  const rows = useMemo(() => {
    const a = sales
      .filter(s => s.date >= filter.startA && s.date <= filter.endA)
      .map(s => ({ ...s, _bucket: filter.periodALabel }));
    const b = sales
      .filter(s => s.date >= filter.startB && s.date <= filter.endB)
      .map(s => ({ ...s, _bucket: filter.periodBLabel }));
    // Sort by date descending, then bucket for consistent ordering
    return [...a, ...b].sort((x, y) => {
      const d = y.date.localeCompare(x.date);
      if (d !== 0) return d;
      return x._bucket.localeCompare(y._bucket);
    });
  }, [sales, filter]);

  const periodACount = rows.filter(r => r._bucket === filter.periodALabel).length;
  const periodBCount = rows.filter(r => r._bucket === filter.periodBLabel).length;
  const totalA = rows
    .filter(r => r._bucket === filter.periodALabel)
    .reduce((s, r) => s + r.total_amount, 0);
  const totalB = rows
    .filter(r => r._bucket === filter.periodBLabel)
    .reduce((s, r) => s + r.total_amount, 0);

  return (
    <Card variant="bordered" className="overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-base-300 bg-info/5">
        <div className="flex items-center gap-3">
          <span className="ri-filter-2-line ri-20px text-info" />
          <div>
            <h3 className="text-sm font-bold text-base-content">
              {filter.label}
            </h3>
            <p className="text-xs text-base-content/50 mt-0.5">
              <span className="font-semibold text-primary">{filter.periodALabel}</span>:{' '}
              {periodACount} orders · {currency} {totalA.toFixed(2)}
              {' · '}
              <span className="font-semibold text-secondary">{filter.periodBLabel}</span>:{' '}
              {periodBCount} orders · {currency} {totalB.toFixed(2)}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="btn btn-ghost btn-sm btn-circle"
          aria-label="Clear filter"
        >
          <span className="ri-close-line ri-16px" />
        </button>
      </div>

      {/* Table */}
      {rows.length === 0 ? (
        <div className="p-6 text-center text-base-content/50 text-sm">
          {t('common.noDataFound')}
        </div>
      ) : (
        <div className="overflow-x-auto">
          {/* Desktop header */}
          <div className="hidden sm:grid grid-cols-[80px_1fr_1fr_1fr_1fr_90px] gap-3 px-4 py-3 border-b border-base-300 text-xs font-semibold text-slate-600 dark:text-slate-300">
            <span>Period</span>
            <span>Date</span>
            <span>Time</span>
            <span>Order Type</span>
            <span>Status</span>
            <span className="text-right">Amount</span>
          </div>

          {/* Rows */}
          {rows.map((sale, _idx) => {
            const isA = sale._bucket === filter.periodALabel;
            return (
              <div
                key={`${sale.id}-${sale._bucket}`}
                className={`grid grid-cols-1 sm:grid-cols-[80px_1fr_1fr_1fr_1fr_90px] gap-2 sm:gap-3 px-4 py-2.5
                  border-b border-base-300 last:border-b-0 text-sm
                  ${isA ? 'bg-primary/[0.02]' : 'bg-secondary/[0.02]'}
                  hover:bg-base-200 transition-colors`}
              >
                {/* Mobile: single column layout */}
                <div className="sm:hidden flex items-center justify-between mb-1">
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      isA
                        ? 'bg-primary/10 text-primary'
                        : 'bg-secondary/10 text-secondary'
                    }`}
                  >
                    {sale._bucket}
                  </span>
                  <span className="text-sm font-bold text-base-content">
                    {currency} {sale.total_amount.toFixed(2)}
                  </span>
                </div>

                {/* Period (desktop) */}
                <div className="hidden sm:flex items-center">
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      isA
                        ? 'bg-primary/10 text-primary'
                        : 'bg-secondary/10 text-secondary'
                    }`}
                  >
                    {sale._bucket}
                  </span>
                </div>

                {/* Date */}
                <div>
                  <span className="sm:hidden text-xs font-medium text-slate-400 mr-2">Date</span>
                  <span className="text-base-content">{sale.date || '-'}</span>
                </div>

                {/* Time */}
                <div>
                  <span className="sm:hidden text-xs font-medium text-slate-400 mr-2">Time</span>
                  <span className="text-slate-600 dark:text-slate-300">{sale.time || '-'}</span>
                </div>

                {/* Order Type */}
                <div>
                  <span className="sm:hidden text-xs font-medium text-slate-400 mr-2">Type</span>
                  <span className="capitalize text-slate-600 dark:text-slate-300">
                    {sale.order_type || '-'}
                  </span>
                </div>

                {/* Status */}
                <div>
                  <span className="sm:hidden text-xs font-medium text-slate-400 mr-2">Status</span>
                  <span
                    className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                      sale.status === 'completed'
                        ? 'bg-success/10 text-success'
                        : sale.status === 'pending'
                          ? 'bg-warning/10 text-warning'
                          : 'bg-info/10 text-info'
                    }`}
                  >
                    {sale.status || '-'}
                  </span>
                </div>

                {/* Amount (desktop) */}
                <div className="hidden sm:flex items-center justify-end">
                  <span className="text-sm font-bold text-base-content">
                    {currency} {sale.total_amount.toFixed(2)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer summary */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-base-300 text-xs text-base-content/50">
        <span>
          {rows.length} {t('reports.transactions', 'transactions')} across 2 periods
        </span>
        <button
          type="button"
          onClick={onDismiss}
          className="text-info hover:text-info/80 transition-colors font-medium"
        >
          {t('reports.dateClear', 'Clear filter')}
        </button>
      </div>
    </Card>
  );
}
