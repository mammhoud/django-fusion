import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import { Supplier } from '../types';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';
import { useStatusToast } from '../hooks/useStatusToast';
import StatusToast from '../components/StatusToast';

type SortKey = 'name-asc' | 'name-desc' | 'newest';

export default function Suppliers() {
  const { t } = useTranslation();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Supplier | null>(null);
  const [form, setForm] = useState({ name: '', contact_name: '', email: '', phone: '', address: '', tax_id: '', payment_terms: '' });

  // Status toast — shared hook ensures load + mutation errors are visible to
  // the user, not just logged to console.
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  // AJAX-style debounced search — shared hook. Rename-destructure keeps the
  // existing JSX variable names (`search`, `debouncedSearch`, `isFiltering`).
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<SortKey>('newest');

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<Supplier[]>('get_suppliers', { includeInactive: false });
      setSuppliers(data);
    } catch (error) {
      console.error('Error loading suppliers:', error);
      // Quiet reload failure still needs to be loud — user must know if the
      // post-CRUD reconciliation failed.
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        await invoke('update_supplier', { id: editing.id, update: form });
      } else {
        await invoke('add_supplier', { supplier: form });
      }
      setShowForm(false);
      setEditing(null);
      setForm({ name: '', contact_name: '', email: '', phone: '', address: '', tax_id: '', payment_terms: '' });
      showSuccess(t('common.saved'));
      loadSuppliers({ quiet: true });
    } catch (error) {
      console.error('Error saving supplier:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const handleEdit = (supplier: Supplier) => {
    setEditing(supplier);
    setForm({
      name: supplier.name,
      contact_name: supplier.contact_name || '',
      email: supplier.email || '',
      phone: supplier.phone || '',
      address: supplier.address || '',
      tax_id: supplier.tax_id || '',
      payment_terms: supplier.payment_terms || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('soft_delete_supplier', { id });
      showSuccess(t('common.deleted'));
      loadSuppliers({ quiet: true });
    } catch (error) {
      console.error('Error deleting supplier:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const q = debouncedSearch.trim().toLowerCase();
  const filteredSuppliers = q
    ? suppliers.filter(s => {
        const haystack = [s.name, s.contact_name || '', s.email || '', s.phone || '', s.address || '']
          .join(' ')
          .toLowerCase();
        return haystack.includes(q);
      })
    : suppliers;

  const sorted = [...filteredSuppliers];
  switch (sortKey) {
    case 'name-asc': sorted.sort((a, b) => a.name.localeCompare(b.name)); break;
    case 'name-desc': sorted.sort((a, b) => b.name.localeCompare(a.name)); break;
    case 'newest':
    default: sorted.sort((a, b) => b.id - a.id);
  }

  return (
    <PageLayout title={t('suppliers.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex justify-between items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('suppliers.title')}</h1>
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => { setShowForm(true); setEditing(null); setForm({ name: '', contact_name: '', email: '', phone: '', address: '', tax_id: '', payment_terms: '' }); }}
            className="btn btn-primary gap-2 shrink-0"
          >
            <span className="icon-[tabler--plus]" /> {t('suppliers.addSupplier')}
          </motion.button>
        </div>

        {/* ── Search + sort bar (debounced async UX) ── */}
        <div className="bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative flex-1">
              <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('suppliers.searchPlaceholder') || 'Search suppliers...'}
                aria-label={t('suppliers.searchPlaceholder') || 'Search suppliers'}
                className="input input-bordered w-full pl-10"
              />
              {isFiltering ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  aria-label="filtering"
                  className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4
                    border-2 border-teal-400 border-t-transparent rounded-full"
                />
              ) : search ? (
                <button
                  onClick={() => setSearch('')}
                  aria-label={t('common.clear')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-white"
                >
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              ) : null}
            </div>
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
              aria-label={t('suppliers.sortBy') || 'Sort by'}
              className="select select-bordered sm:w-44"
            >
              <option value="newest">{t('suppliers.sortNewest') || 'Newest'}</option>
              <option value="name-asc">{t('suppliers.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('suppliers.sortNameDesc') || 'Name (Z→A)'}</option>
            </select>
            <span className="text-xs text-slate-500 dark:text-gray-400 whitespace-nowrap px-2">
              {sorted.length} / {suppliers.length}
            </span>
          </div>
        </div>

        {showForm && (
          <motion.form
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            onSubmit={handleSubmit}
            className="bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 space-y-3"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder={t('suppliers.name')} required className="input input-bordered w-full" />
              <input type="text" value={form.contact_name} onChange={e => setForm({ ...form, contact_name: e.target.value })} placeholder={t('suppliers.contactName')} className="input input-bordered w-full" />
              <input type="text" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} placeholder={t('suppliers.phone')} className="input input-bordered w-full" />
              <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder={t('suppliers.email')} className="input input-bordered w-full" />
              <input type="text" value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} placeholder={t('suppliers.address')} className="input input-bordered w-full" />
              <input type="text" value={form.tax_id} onChange={e => setForm({ ...form, tax_id: e.target.value })} placeholder={t('suppliers.taxId')} className="input input-bordered w-full" />
              <input type="text" value={form.payment_terms} onChange={e => setForm({ ...form, payment_terms: e.target.value })} placeholder={t('suppliers.paymentTerms')} className="input input-bordered w-full sm:col-span-2" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">{editing ? t('common.update') : t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost">{t('common.cancel')}</button>
            </div>
          </motion.form>
        )}

        {isLoading ? (
          <div className="bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-8 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-6 h-6 border-2 border-teal-400 border-t-transparent rounded-full inline-block mb-2"
            />
            <p className="text-slate-500 dark:text-gray-400 text-sm">{t('common.loading')}</p>
          </div>
        ) : sorted.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No matches found.')
              : (t('suppliers.noSuppliers'))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {sorted.map(supplier => (
              <motion.div key={supplier.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white/70 dark:bg-white/10 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400">
                      <span className="icon-[tabler--building] w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">{supplier.name}</h3>
                      {supplier.contact_name && <p className="text-sm text-slate-500">{supplier.contact_name}</p>}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleEdit(supplier)} className="p-2 text-slate-600 hover:text-teal-600"><span className="icon-[tabler--pencil]" /></button>
                    <button onClick={() => handleDelete(supplier.id)} className="p-2 text-slate-600 hover:text-red-600"><span className="icon-[tabler--trash]" /></button>
                  </div>
                </div>
                <div className="mt-3 space-y-1 text-sm text-slate-600 dark:text-gray-400">
                  {supplier.phone && <div className="flex items-center gap-1"><span className="icon-[tabler--phone]" /> {supplier.phone}</div>}
                  {supplier.email && <div className="flex items-center gap-1"><span className="icon-[tabler--mail]" /> {supplier.email}</div>}
                  {supplier.address && <div className="flex items-center gap-1"><span className="icon-[tabler--map-pin]" /> {supplier.address}</div>}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}
