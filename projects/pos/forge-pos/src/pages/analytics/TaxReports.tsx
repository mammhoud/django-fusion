import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import { TaxReport } from '../../types';
import { useCurrency } from '../../contexts/CurrencyContext';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';

export default function TaxReports() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
  const [reports, setReports] = useState<TaxReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ period_start: '', period_end: '', total_sales: 0, total_tax: 0, transaction_count: 0 });

  // AJAX-style debounced search + sort. Searches across period dates and totals
  // as strings (date format is YYYY-MM-DD so substring matches work intuitively).
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<'newest' | 'oldest' | 'sales-desc' | 'sales-asc'>('newest');

  useEffect(() => {
    loadReports();
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await invoke('add_tax_report', { report: form });
      setShowForm(false);
      setForm({ period_start: '', period_end: '', total_sales: 0, total_tax: 0, transaction_count: 0 });
      loadReports({ quiet: true });
    } catch (error) {
      console.error('Error saving tax report:', error);
      loadReports({ quiet: true });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('delete_tax_report', { id });
      loadReports({ quiet: true });
    } catch (error) {
      console.error('Error deleting tax report:', error);
      loadReports({ quiet: true });
    }
  };

  // Filtered + sorted list (debounced search + sort apply to visible grid)
  const q = debouncedSearch.trim().toLowerCase();
  const filteredReports = (() => {
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
  })();

  return (
    <PageLayout title={t('taxReports.title')}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-base-content">{t('taxReports.title')}</h1>
          <button onClick={() => setShowForm(true)} className="btn btn-primary gap-2 active:scale-[0.98] transition-all">
            <span className="icon-[tabler--plus]" /> {t('taxReports.addReport')}
          </button>
        </div>

        {/* ── Search + sort bar (debounced async UX) ── */}
        <div className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="input input--sm flex-1">
              <div className="input__wrapper">
                <span className="input__icon icon-[tabler--search]" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={t('taxReports.searchPlaceholder') || 'Search by period or amount...'}
                  aria-label={t('taxReports.searchPlaceholder') || 'Search tax reports'}
                  className="input__field input__field--with-icon-left"
                />
                {isFiltering ? (
                  <span className="input__icon input__icon--right w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-label="filtering" />
                ) : search ? (
                  <button
                    onClick={() => setSearch('')}
                    aria-label={t('common.clear')}
                    className="input__icon input__icon--right"
                  >
                    <span className="icon-[tabler--x]" />
                  </button>
                ) : null}
              </div>
            </div>
            <div className="input input--sm sm:w-48">
              <select
                value={sortKey}
                onChange={(e) => setSortKey(e.target.value as 'newest' | 'oldest' | 'sales-desc' | 'sales-asc')}
                aria-label={t('taxReports.sortBy') || 'Sort by'}
                className="input__field input__field--select"
              >
                <option value="newest">{t('taxReports.sortNewest') || 'Period (newest)'}</option>
                <option value="oldest">{t('taxReports.sortOldest') || 'Period (oldest)'}</option>
                <option value="sales-desc">{t('taxReports.sortSalesDesc') || 'Sales (high → low)'}</option>
                <option value="sales-asc">{t('taxReports.sortSalesAsc') || 'Sales (low → high)'}</option>
            </select>
            </div>
            <span className="text-xs text-base-content/50 whitespace-nowrap px-2">
              {filteredReports.length} / {reports.length}
            </span>
          </div>
        </div>

        {showForm && (
          <form initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input type="date" value={form.period_start} onChange={e => setForm({ ...form, period_start: e.target.value })} required className="input__field w-full" />
              <input type="date" value={form.period_end} onChange={e => setForm({ ...form, period_end: e.target.value })} required className="input__field w-full" />
              <input type="number" step="0.01" value={form.total_sales} onChange={e => setForm({ ...form, total_sales: Number(e.target.value) })} placeholder={t('taxReports.totalSales')} required className="input__field w-full" />
              <input type="number" step="0.01" value={form.total_tax} onChange={e => setForm({ ...form, total_tax: Number(e.target.value) })} placeholder={t('taxReports.totalTax')} required className="input__field w-full" />
              <input type="number" value={form.transaction_count} onChange={e => setForm({ ...form, transaction_count: Number(e.target.value) })} placeholder={t('taxReports.transactionCount')} required className="input__field w-full sm:col-span-2" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">{t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost">{t('common.cancel')}</button>
            </div>
          </form>
        )}

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : filteredReports.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No matches found.')
              : (t('taxReports.noReports'))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {filteredReports.map(report => (
              <div key={report.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-info/10 flex items-center justify-center text-info">
                      <span className="icon-[tabler--building-bank] w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">{report.period_start} - {report.period_end}</h3>
                      <p className="text-sm text-slate-500">{report.transaction_count} {t('taxReports.transactions')}</p>
                    </div>
                  </div>
                  <button onClick={() => handleDelete(report.id)} className="p-2 text-slate-600 hover:text-red-600"><span className="icon-[tabler--trash]" /></button>
                </div>
                <div className="mt-3 text-sm text-base-content/60 space-y-1">
                  <p>{t('taxReports.totalSales')}: {formatPrice(report.total_sales)}</p>
                  <p>{t('taxReports.totalTax')}: {formatPrice(report.total_tax)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
