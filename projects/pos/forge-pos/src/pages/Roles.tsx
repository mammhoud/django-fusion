import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import { Role } from '../types';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

export default function Roles() {
  const { t } = useTranslation();
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Role | null>(null);
  const [form, setForm] = useState({ name: '', permissions: '[]' });

  // AJAX-style debounced search — shared hook. Rename-destructure keeps the
  // existing JSX variable names (`search`, `debouncedSearch`, `isFiltering`).
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<'newest' | 'name-asc' | 'name-desc'>('newest');

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<Role[]>('get_roles');
      setRoles(data);
    } catch (error) {
      console.error('Error loading roles:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        await invoke('update_role', { id: editing.id, update: form });
      } else {
        await invoke('add_role', { role: form });
      }
      setShowForm(false);
      setEditing(null);
      setForm({ name: '', permissions: '[]' });
      loadRoles({ quiet: true });
    } catch (error) {
      console.error('Error saving role:', error);
      loadRoles({ quiet: true });
    }
  };

  const handleEdit = (role: Role) => {
    setEditing(role);
    setForm({ name: role.name, permissions: role.permissions });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('soft_delete_role', { id });
      loadRoles({ quiet: true });
    } catch (error) {
      console.error('Error deleting role:', error);
      loadRoles({ quiet: true });
    }
  };

  // Filtered + sorted roles (debounced search + sort apply to the visible grid)
  const q = debouncedSearch.trim().toLowerCase();
  const filteredRoles = (() => {
    let result = q
      ? roles.filter(r =>
          r.name.toLowerCase().includes(q) ||
          (r.permissions || '').toLowerCase().includes(q)
        )
      : roles;
    const sorted = [...result];
    switch (sortKey) {
      case 'name-asc': sorted.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'name-desc': sorted.sort((a, b) => b.name.localeCompare(a.name)); break;
      case 'newest':
      default: sorted.sort((a, b) => b.id - a.id);
    }
    return sorted;
  })();

  return (
    <PageLayout title={t('roles.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('roles.title')}</h1>
          <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} onClick={() => { setShowForm(true); setEditing(null); setForm({ name: '', permissions: '[]' }); }} className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">
            <span className="icon-[tabler--plus]" /> {t('roles.addRole')}
          </motion.button>
        </div>

        {/* ── Search + sort bar (debounced async UX) ── */}
        <div className="card--glass rounded-xl p-3">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative flex-1">
              <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('roles.searchPlaceholder') || 'Search roles...'}
                aria-label={t('roles.searchPlaceholder') || 'Search roles'}
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
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              ) : null}
            </div>
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as 'newest' | 'name-asc' | 'name-desc')}
              aria-label={t('roles.sortBy') || 'Sort by'}
              className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5
                border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white
                text-sm focus:outline-none focus:border-teal-400 transition-colors sm:w-44"
            >
              <option value="newest">{t('roles.sortNewest') || 'Newest'}</option>
              <option value="name-asc">{t('roles.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('roles.sortNameDesc') || 'Name (Z→A)'}</option>
            </select>
            <span className="text-xs text-slate-500 dark:text-gray-400 whitespace-nowrap px-2">
              {filteredRoles.length} / {roles.length}
            </span>
          </div>
        </div>

        {showForm && (
          <motion.form initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="card--glass rounded-xl p-4 space-y-3">
            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder={t('roles.name')} required className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
            <textarea value={form.permissions} onChange={e => setForm({ ...form, permissions: e.target.value })} placeholder={t('roles.permissions')} rows={4} required className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white font-mono text-sm" />
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">{editing ? t('common.update') : t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-slate-300 dark:bg-slate-700 rounded-lg">{t('common.cancel')}</button>
            </div>
          </motion.form>
        )}

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : filteredRoles.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No matches found.')
              : (t('roles.noRoles'))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {filteredRoles.map(role => (
              <motion.div key={role.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card--glass rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600 dark:text-red-400">
                      <span className="icon-[tabler--shield] w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">{role.name}</h3>
                      <p className="text-xs text-slate-500">{role.is_active ? t('common.active') : t('common.inactive')}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleEdit(role)} className="p-2 text-slate-600 hover:text-teal-600"><span className="icon-[tabler--pencil]" /></button>
                    <button onClick={() => handleDelete(role.id)} className="p-2 text-slate-600 hover:text-red-600"><span className="icon-[tabler--trash]" /></button>
                  </div>
                </div>
                <pre className="mt-3 text-xs text-slate-600 dark:text-gray-400 overflow-hidden text-ellipsis whitespace-nowrap">{role.permissions}</pre>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
