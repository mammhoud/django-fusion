import { useState } from 'react';
import { motion } from 'framer-motion';
import { MdReceipt, MdAdd, MdEdit, MdDelete, MdSearch, MdClose } from 'react-icons/md';
import PageLayout from '../components/PageLayout';
import { FusionPage } from '../components/FusionPage';
import { useTranslation } from 'react-i18next';
import { useGetReceiptTemplatesQuery, useAddReceiptTemplateMutation, useUpdateReceiptTemplateMutation, useDeleteReceiptTemplateMutation } from '../store/api/endpoints/receipts';
import type { ReceiptTemplate } from '../store/api/endpoints/receipts';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

export default function ReceiptTemplates() {
  const { t } = useTranslation();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ReceiptTemplate | null>(null);
  const [form, setForm] = useState({ name: '', template_body: '', is_default: false });

  // AJAX-style debounced search + sort. Searches across name + body content.
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<'name-asc' | 'name-desc' | 'newest' | 'default-first'>('default-first');

  const { data: templates = [], isLoading, error } = useGetReceiptTemplatesQuery();
  const [addReceiptTemplate] = useAddReceiptTemplateMutation();
  const [updateReceiptTemplate] = useUpdateReceiptTemplateMutation();
  const [deleteReceiptTemplate] = useDeleteReceiptTemplateMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        await updateReceiptTemplate({ id: editing.id, data: form }).unwrap();
      } else {
        await addReceiptTemplate(form).unwrap();
      }
      setShowForm(false);
      setEditing(null);
      setForm({ name: '', template_body: '', is_default: false });
    } catch (error) {
      console.error('Error saving template:', error);
    }
  };

  const handleEdit = (template: ReceiptTemplate) => {
    setEditing(template);
    setForm({ name: template.name, template_body: (template.content || template.template_body || ''), is_default: template.is_default });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await deleteReceiptTemplate(id).unwrap();
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  // Filtered + sorted templates (debounced search + sort applies to visible grid)
  const q = debouncedSearch.trim().toLowerCase();
  const filteredTemplates = (() => {
    let result = q
      ? templates.filter(t =>
          t.name.toLowerCase().includes(q) ||
          (t.template_body || '').toLowerCase().includes(q)
        )
      : templates;
    const sorted = [...result];
    switch (sortKey) {
      case 'name-asc': sorted.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'name-desc': sorted.sort((a, b) => b.name.localeCompare(a.name)); break;
      case 'newest': sorted.sort((a, b) => b.id - a.id); break;
      case 'default-first':
      default:
        sorted.sort((a, b) => (b.is_default ? 1 : 0) - (a.is_default ? 1 : 0) || a.name.localeCompare(b.name));
    }
    return sorted;
  })();

  return (
    <PageLayout title={t('receiptTemplates.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('receiptTemplates.title')}</h1>
          <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} onClick={() => { setShowForm(true); setEditing(null); setForm({ name: '', template_body: '', is_default: false }); }} className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">
            <MdAdd /> {t('receiptTemplates.addTemplate')}
          </motion.button>
        </div>

        {/* ── Search + sort bar (debounced async UX) ── */}
        <div className="card--glass rounded-xl p-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative flex-1">
              <MdSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('receiptTemplates.searchPlaceholder') || 'Search templates...'}
                aria-label={t('receiptTemplates.searchPlaceholder') || 'Search receipt templates'}
                className="w-full pl-10 pr-9 py-2 rounded-lg bg-white/50 dark:bg-white/5
                  border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white
                  placeholder:text-slate-400 dark:placeholder:text-gray-500
                  focus:outline-none focus:border-teal-400 transition-colors text-sm"
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
                  <MdClose className="w-4 h-4" />
                </button>
              ) : null}
            </div>
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as 'name-asc' | 'name-desc' | 'newest' | 'default-first')}
              aria-label={t('receiptTemplates.sortBy') || 'Sort by'}
              className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5
                border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white
                text-sm focus:outline-none focus:border-teal-400 transition-colors sm:w-48"
            >
              <option value="default-first">{t('receiptTemplates.sortDefaultFirst') || 'Default first'}</option>
              <option value="name-asc">{t('receiptTemplates.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('receiptTemplates.sortNameDesc') || 'Name (Z→A)'}</option>
              <option value="newest">{t('receiptTemplates.sortNewest') || 'Newest'}</option>
            </select>
            <span className="text-xs text-slate-500 dark:text-gray-400 whitespace-nowrap px-2">
              {filteredTemplates.length} / {templates.length}
            </span>
          </div>
        </div>

        {showForm && (
          <motion.form initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="card--glass rounded-xl p-4 space-y-3">
            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder={t('receiptTemplates.name')} required className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
            <textarea value={form.template_body} onChange={e => setForm({ ...form, template_body: e.target.value })} placeholder={t('receiptTemplates.body')} rows={8} required className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white font-mono text-sm" />
            <label className="flex items-center gap-2 text-slate-700 dark:text-gray-300">
              <input type="checkbox" checked={form.is_default} onChange={e => setForm({ ...form, is_default: e.target.checked })} className="w-4 h-4" />
              {t('receiptTemplates.setAsDefault')}
            </label>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">{editing ? t('common.update') : t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-slate-300 dark:bg-slate-700 rounded-lg">{t('common.cancel')}</button>
            </div>
          </motion.form>
        )}

        {/* Data rendering wrapped with FusionPage for fragment-rendering support */}
        <FusionPage
          standalone
          data={filteredTemplates}
          isLoading={isLoading}
          error={error}
          skeletonVariant="card"
        >
          {(data, fallback) => {
            const items = (data ?? []) as typeof filteredTemplates;
            if (items.length === 0) {
              return (
                <div className="text-center py-12 text-slate-500">
                  {debouncedSearch
                    ? (t('common.noDataFound') || 'No matches found.')
                    : (t('receiptTemplates.noTemplates'))}
                </div>
              );
            }
            return (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {items.map(template => (
                  <motion.div key={template.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card--glass rounded-xl p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400">
                          <MdReceipt className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-white">{template.name}</h3>
                          {template.is_default && <span className="text-xs text-teal-600 dark:text-teal-400">{t('receiptTemplates.default')}</span>}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => handleEdit(template)} className="p-2 text-slate-600 hover:text-teal-600"><MdEdit /></button>
                        <button onClick={() => handleDelete(template.id)} className="p-2 text-slate-600 hover:text-red-600"><MdDelete /></button>
                      </div>
                    </div>
                    <pre className="mt-3 text-xs text-slate-600 dark:text-gray-400 overflow-hidden text-ellipsis whitespace-nowrap">{template.template_body}</pre>
                  </motion.div>
                ))}
              </div>
            );
          }}
        </FusionPage>
      </div>
    </PageLayout>
  );
}
