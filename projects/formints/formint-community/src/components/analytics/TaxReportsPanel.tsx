import { useState, useEffect, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import { TaxReport } from '../../types';
import { useCurrency } from '../../contexts/CurrencyContext';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import SearchInput from '../../components/ui/SearchInput';
import StatCard from '../../components/ui/StatCard';
import FormModal from '../../components/ui/FormModal';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

type SortKey = 'newest' | 'oldest' | 'sales-desc' | 'sales-asc';

const EMPTY_FORM = { period_start: '', period_end: '', total_sales: 0, total_tax: 0, transaction_count: 0 };

/**
 * Tax Reports panel — rendered inside the Reports page as the "Tax Reports" tab.
 *
 * Self-contained (fetches its own data via `get_tax_reports`), so the panel only
 * loads when the tab is actually opened. Includes:
 * - summary stat row (periods, total sales, total tax) — reuse of the fit-design StatCard
 * - debounced search + sort toolbar
 * - add-report dialog via the shared FormModal
 * - responsive report-card grid with an effective-tax-rate badge
 */
export default function TaxReportsPanel() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
  const [reports, setReports] = useState<TaxReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [sortKey, setSortKey] = useState<SortKey>('newest');

  // AJAX-style debounced search + sort. Searches across period dates and totals
  // as strings (date format is YYYY-MM-DD so substring matches work intuitively).
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  useEffect(() => {
    loadReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadReports = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<TaxReport[]>('get_tax_reports');
      setReports(data);
    } catch (error) {
      console.error('Error loading tax reports:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    setIsSaving(true);
    try {
      await invoke('add_tax_report', { report: form });
      setShowForm(false);
      setForm(EMPTY_FORM);
      await loadReports({ quiet: true });
    } catch (error) {
      console.error('Error saving tax report:', error);
      await loadReports({ quiet: true });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete') || 'Delete this report?')) return;
    try {
      await invoke('delete_tax_report', { id });
      await loadReports({ quiet: true });
    } catch (error) {
      console.error('Error deleting tax report:', error);
      await loadReports({ quiet: true });
    }
  };

  // ── Filtered + sorted list (memoized — cheap to recompute, stable between renders) ──
  const filteredReports = useMemo(() => {
    const q = debouncedSearch.trim().toLowerCase();
    let result = q
      ? reports.filter(r => {
          const haystack = [
            r.period_start || '',
            r.period_end || '',
            String(r.total_sales ?? ''),
            String(r.total_tax ?? ''),
            String(r.transaction_count ?? ''),
          ].join(' ').toLowerCase();
          return haystack.includes(q);
        })
      : reports;
    const sorted = [...result];
    switch (sortKey) {
      case 'sales-desc': sorted.sort((a, b) => b.total_sales - a.total_sales); break;
      case 'sales-asc': sorted.sort((a, b) => a.total_sales - b.total_sales); break;
      case 'oldest':
        sorted.sort((a, b) => (a.period_start || '').localeCompare(b.period_start || '')); break;
      case 'newest':
      default:
        sorted.sort((a, b) => (b.period_start || '').localeCompare(a.period_start || ''));
    }
    return sorted;
  }, [reports, debouncedSearch, sortKey]);

  // ── Summary stats (memoized) ──
  const summary = useMemo(() => ({
    totalSales: reports.reduce((s, r) => s + (r.total_sales || 0), 0),
    totalTax: reports.reduce((s, r) => s + (r.total_tax || 0), 0),
  }), [reports]);

  const effectiveRate = (r: TaxReport) =>
    r.total_sales > 0 ? `${((r.total_tax / r.total_sales) * 100).toFixed(1)}%` : null;

  return (
    <div className="space-y-6">
      {/* ── Summary stat row ── */}
      {isLoading && reports.length === 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
          <StatCard loading compact />
          <StatCard loading compact />
          <StatCard loading compact />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
          <StatCard
            title={t('taxReports.periods')}
            value={reports.length}
            icon={<span className="ri-calendar-2-line ri-20px" />}
            color="primary"
            compact
          />
          <StatCard
            title={t('taxReports.totalSales')}
            value={formatPrice(summary.totalSales)}
            icon={<span className="ri-money-dollar-box-line ri-20px" />}
            color="info"
            compact
          />
          <StatCard
            title={t('taxReports.totalTax')}
            value={formatPrice(summary.totalTax)}
            icon={<span className="ri-percent-line ri-20px" />}
            color="warning"
            compact
          />
        </div>
      )}

      {/* ── Header + Add action ── */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-bold text-base-content">{t('taxReports.title')}</h2>
        <Button
          variant="primary"
          size="md"
          onClick={() => setShowForm(true)}
          iconStart={<span className="ri-add-line ri-16px" />}
        >
          {t('taxReports.addReport')}
        </Button>
      </div>

      {/* ── Search + sort toolbar ── */}
      <Card padding="sm" variant="bordered">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder={t('taxReports.searchPlaceholder') || 'Search by period or amount...'}
            ariaLabel={t('taxReports.searchPlaceholder') || 'Search tax reports'}
            testId="tax-search-input"
            loading={isFiltering}
            className="flex-1"
          />
          <div className="field field--sm sm:w-48">
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
              aria-label={t('taxReports.sortBy') || 'Sort by'}
              className="select"
            >
              <option value="newest">{t('taxReports.sortNewest') || 'Period (newest)'}</option>
              <option value="oldest">{t('taxReports.sortOldest') || 'Period (oldest)'}</option>
              <option value="sales-desc">{t('taxReports.sortSalesDesc') || 'Sales (high → low)'}</option>
              <option value="sales-asc">{t('taxReports.sortSalesAsc') || 'Sales (low → high)'}</option>
            </select>
          </div>
          <span className="text-xs text-base-content/50 whitespace-nowrap px-2 tabular-nums">
            {filteredReports.length} / {reports.length}
          </span>
        </div>
      </Card>

      {/* ── Add Report dialog ── */}
      <FormModal
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        title={t('taxReports.addTitle')}
        size="md"
        onSubmit={handleSubmit}
        submitDisabled={!form.period_start || !form.period_end}
        isSubmitting={isSaving}
        submitLabel={t('common.save')}
        contentTestId="tax-report-form"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="tax-period-start" className="block text-sm font-medium text-base-content/70 mb-1.5">
              {t('taxReports.periodStart')}
            </label>
            <input
              id="tax-period-start"
              type="date"
              value={form.period_start}
              onChange={(e) => setForm(prev => ({ ...prev, period_start: e.target.value }))}
              className="input w-full"
            />
          </div>
          <div>
            <label htmlFor="tax-period-end" className="block text-sm font-medium text-base-content/70 mb-1.5">
              {t('taxReports.periodEnd')}
            </label>
            <input
              id="tax-period-end"
              type="date"
              value={form.period_end}
              onChange={(e) => setForm(prev => ({ ...prev, period_end: e.target.value }))}
              className="input w-full"
            />
          </div>
          <div>
            <label htmlFor="tax-total-sales" className="block text-sm font-medium text-base-content/70 mb-1.5">
              {t('taxReports.totalSales')}
            </label>
            <input
              id="tax-total-sales"
              type="number"
              step="0.01"
              min="0"
              value={form.total_sales}
              onChange={(e) => setForm(prev => ({ ...prev, total_sales: Number(e.target.value) }))}
              className="input w-full"
            />
          </div>
          <div>
            <label htmlFor="tax-total-tax" className="block text-sm font-medium text-base-content/70 mb-1.5">
              {t('taxReports.totalTax')}
            </label>
            <input
              id="tax-total-tax"
              type="number"
              step="0.01"
              min="0"
              value={form.total_tax}
              onChange={(e) => setForm(prev => ({ ...prev, total_tax: Number(e.target.value) }))}
              className="input w-full"
            />
          </div>
          <div className="sm:col-span-2">
            <label htmlFor="tax-tx-count" className="block text-sm font-medium text-base-content/70 mb-1.5">
              {t('taxReports.transactionCount')}
            </label>
            <input
              id="tax-tx-count"
              type="number"
              min="0"
              value={form.transaction_count}
              onChange={(e) => setForm(prev => ({ ...prev, transaction_count: Number(e.target.value) }))}
              className="input w-full"
            />
          </div>
        </div>
      </FormModal>

      {/* ── List / empty / loading states ── */}
      {isLoading && reports.length === 0 ? (
        <div className="text-center py-16 text-base-content/50">{t('common.loading')}</div>
      ) : filteredReports.length === 0 ? (
        <div className="text-center py-16">
          <span className="ri-bank-line ri-48px mx-auto mb-3 text-base-content/20 block" />
          <p className="text-base-content/50">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No matches found.')
              : (t('taxReports.noReports'))}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
          {filteredReports.map(report => (
            <div
              key={report.id}
              className="bg-base-100/70 dark:bg-white/5 backdrop-blur-sm border border-base-300/40 dark:border-white/10 rounded-2xl p-4 shadow-sm
                transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 shrink-0 rounded-xl bg-info/10 dark:bg-info/20 text-info flex items-center justify-center">
                    <span className="ri-bank-line ri-20px" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-base-content truncate">
                      {report.period_start} – {report.period_end}
                    </h3>
                    <p className="text-xs text-base-content/50">
                      {report.transaction_count} {t('taxReports.transactions')}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(report.id)}
                  className="p-1.5 rounded-lg text-base-content/40 hover:text-error hover:bg-error/10 transition-colors shrink-0"
                  aria-label={`${t('common.delete')} ${report.period_start}`}
                >
                  <span className="ri-delete-bin-line ri-16px" />
                </button>
              </div>

              <div className="mt-3 pt-3 border-t border-base-300/30 grid grid-cols-2 gap-3">
                <div className="min-w-0">
                  <p className="text-[11px] text-base-content/50">{t('taxReports.totalSales')}</p>
                  <p className="text-sm font-semibold text-base-content tabular-nums truncate">{formatPrice(report.total_sales)}</p>
                </div>
                <div className="min-w-0">
                  <p className="text-[11px] text-base-content/50">{t('taxReports.totalTax')}</p>
                  <p className="text-sm font-semibold text-warning tabular-nums truncate">{formatPrice(report.total_tax)}</p>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between gap-2">
                <span className="text-[11px] text-base-content/40 truncate">{report.period_start}</span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-warning/10 text-warning text-[11px] font-medium shrink-0">
                  <span className="ri-percent-line ri-12px" />
                  {effectiveRate(report) ?? '—'} {t('taxReports.effectiveRate')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
