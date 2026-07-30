import { useState, useEffect, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import { Note } from '../../types';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import AnimatePresence from '../../components/utils/AnimatePresence';

// ── Category color mapping ──
const CATEGORY_COLORS: Record<string, string> = {
  general: 'badge-ghost',
  idea: 'badge-primary',
  task: 'badge-warning',
  recipe: 'badge-success',
  preparation: 'badge-info',
  'chef-tips': 'badge-warning',
  allergen: 'badge-error',
  plating: 'badge-success',
  inventory: 'badge-info',
  staff: 'badge-secondary',
  finance: 'badge-accent',
  customer: 'badge-error',
  other: 'badge-ghost',
};

const NOTE_CATEGORIES = [
  { value: '', label: 'General', color: 'badge-ghost' },
  { value: 'idea', label: 'Idea', color: 'badge-primary' },
  { value: 'task', label: 'Task', color: 'badge-warning' },
  { value: 'recipe', label: 'Recipe', color: 'badge-success' },
  { value: 'preparation', label: 'Preparation Steps', color: 'badge-info' },
  { value: 'chef-tips', label: 'Chef Tips', color: 'badge-warning' },
  { value: 'allergen', label: 'Allergen Info', color: 'badge-error' },
  { value: 'plating', label: 'Plating Guide', color: 'badge-success' },
  { value: 'inventory', label: 'Inventory', color: 'badge-info' },
  { value: 'staff', label: 'Staff', color: 'badge-secondary' },
  { value: 'finance', label: 'Finance', color: 'badge-accent' },
  { value: 'customer', label: 'Customer', color: 'badge-error' },
  { value: 'other', label: 'Other', color: 'badge-ghost' },
];

function getCategoryColor(cat: string | null | undefined): string {
  if (!cat) return 'badge-ghost';
  return CATEGORY_COLORS[cat.toLowerCase()] || 'badge-ghost';
}


function getCategoryBorder(cat: string | null | undefined): string {
  if (!cat) return 'border-l-base-300';
  const borders: Record<string, string> = {
    general: 'border-l-base-300',
    idea: 'border-l-primary',
    task: 'border-l-warning',
    recipe: 'border-l-success',
    preparation: 'border-l-info',
    'chef-tips': 'border-l-warning',
    allergen: 'border-l-error',
    plating: 'border-l-success',
    inventory: 'border-l-info',
    staff: 'border-l-secondary',
    finance: 'border-l-accent',
    customer: 'border-l-error',
    other: 'border-l-base-300',
  };
  return borders[cat.toLowerCase()] || 'border-l-base-300';
}

function getCategoryLabel(cat: string | null | undefined): string {
  if (!cat) return 'General';
  const found = NOTE_CATEGORIES.find(c => c.value === cat.toLowerCase());
  return found?.label || cat;
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr.replace(' ', 'T') + 'Z');
    if (isNaN(d.getTime())) return dateStr;
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

function getContentPreview(body: string, maxLines = 3): string {
  const lines = body.split('\n').filter(l => l.trim());
  const preview = lines.slice(0, maxLines).join('\n');
  return preview || '—';
}

function getNoteIconClass(cat: string | null | undefined): string {
  switch ((cat || '').toLowerCase()) {
    case 'idea': return 'icon-[tabler--bulb] w-3 h-3';
    case 'task': return 'icon-[tabler--checkbox] w-3 h-3';
    case 'recipe': return 'icon-[tabler--chef-hat] w-3 h-3';
    case 'preparation': return 'icon-[tabler--list-check] w-3 h-3';
    case 'chef-tips': return 'icon-[tabler--bulb] w-3 h-3';
    case 'allergen': return 'icon-[tabler--alert-triangle] w-3 h-3';
    case 'plating': return 'icon-[tabler--palette] w-3 h-3';
    case 'inventory': return 'icon-[tabler--packages] w-3 h-3';
    case 'staff': return 'icon-[tabler--users] w-3 h-3';
    case 'finance': return 'icon-[tabler--cash] w-3 h-3';
    case 'customer': return 'icon-[tabler--handshake] w-3 h-3';
    default: return 'icon-[tabler--notes] w-3 h-3';
  }
}

export default function Notes() {
  const { t } = useTranslation();
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Note | null>(null);
  const [form, setForm] = useState({ name: '', template_body: '', category: '', is_default: false, use_as_template: false });
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<'name-asc' | 'name-desc' | 'newest' | 'oldest' | 'pinned'>('pinned');
  const [selectedNotes, setSelectedNotes] = useState<Set<number>>(new Set());
  const [duplicatingId, setDuplicatingId] = useState<number | null>(null);

  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<Note[]>('get_notes');
      setNotes(data);
    } catch (error) {
      console.error('Error loading notes:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.template_body.trim()) return;
    try {
      const payload = {
        name: form.name.trim(),
        template_body: form.template_body.trim(),
        category: form.category || null,
        use_as_template: form.use_as_template,
      };
      if (editing) {
        await invoke('update_note', {
          id: editing.id,
          update: {
            ...payload,
            is_default: form.is_default,
            use_as_template: form.use_as_template,
          },
        });
      } else {
        const result = await invoke<Note>('add_note', { template: payload });
        // If is_default is checked, update after creation
        if (form.is_default && result) {
          await invoke('update_note', {
            id: result.id,
            update: { is_default: true },
          });
        }
      }
      resetForm();
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error saving note:', error);
      loadNotes({ quiet: true });
    }
  };

  const handleEdit = (note: Note) => {
    setEditing(note);
    setForm({
      name: note.name,
      template_body: note.template_body,
      category: note.category || '',
      is_default: note.is_default,
      use_as_template: note.use_as_template,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('delete_note', { id });
      setSelectedNotes(prev => { const next = new Set(prev); next.delete(id); return next; });
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error deleting note:', error);
      loadNotes({ quiet: true });
    }
  };

  const handleTogglePin = async (note: Note) => {
    try {
      await invoke('update_note', {
        id: note.id,
        update: { is_default: !note.is_default },
      });
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error toggling pin:', error);
    }
  };

  const handleDuplicate = async (note: Note) => {
    setDuplicatingId(note.id);
    try {
      await invoke<Note>('add_note', {
        template: {
          name: `${note.name} (copy)`,
          template_body: note.template_body,
          category: note.category || null,
          use_as_template: note.use_as_template,
        }
      });
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error duplicating note:', error);
    } finally {
      setDuplicatingId(null);
    }
  };

  // ── Bulk actions ──
  const toggleSelect = (id: number) => {
    setSelectedNotes(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (selectedNotes.size === filteredNotes.length) {
      setSelectedNotes(new Set());
    } else {
      setSelectedNotes(new Set(filteredNotes.map(n => n.id)));
    }
  };

  const bulkDelete = async () => {
    if (selectedNotes.size === 0) return;
    if (!confirm(`Delete ${selectedNotes.size} note(s)?`)) return;
    try {
      for (const id of selectedNotes) {
        await invoke('delete_note', { id });
      }
      setSelectedNotes(new Set());
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error bulk deleting:', error);
    }
  };

  const bulkPin = async (pinned: boolean) => {
    if (selectedNotes.size === 0) return;
    try {
      for (const id of selectedNotes) {
        await invoke('update_note', { id, update: { is_default: pinned } });
      }
      setSelectedNotes(new Set());
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error bulk pinning:', error);
    }
  };

  // ── E6: Export filtered notes as JSON ──
  const handleExport = () => {
    const data = filteredNotes.map(n => ({
      name: n.name,
      category: n.category || '',
      body: n.template_body,
      pinned: n.is_default,
      template: n.use_as_template,
    }));
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `notes-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const resetForm = () => {
    setShowForm(false);
    setEditing(null);
    setForm({ name: '', template_body: '', category: '', is_default: false, use_as_template: false });
  };

  // ── Unique categories from notes for the filter bar ──
  const availableCategories = useMemo(() => {
    const cats = new Set(notes.map(n => (n.category || '').toLowerCase()).filter(Boolean));
    return Array.from(cats);
  }, [notes]);

  // ── Filtered + sorted notes ──
  const q = debouncedSearch.trim().toLowerCase();
  const filteredNotes = useMemo(() => {
    let result = notes;

    // Search filter
    if (q) {
      result = result.filter(n =>
        n.name.toLowerCase().includes(q) ||
        (n.template_body || '').toLowerCase().includes(q) ||
        (n.category || '').toLowerCase().includes(q)
      );
    }

    // Category filter
    if (categoryFilter) {
      result = result.filter(n => (n.category || '').toLowerCase() === categoryFilter);
    }

    // Sort
    const sorted = [...result];
    switch (sortKey) {
      case 'name-asc': sorted.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'name-desc': sorted.sort((a, b) => b.name.localeCompare(a.name)); break;
      case 'newest': sorted.sort((a, b) => b.id - a.id); break;
      case 'oldest': sorted.sort((a, b) => a.id - b.id); break;
      case 'pinned':
      default:
        sorted.sort((a, b) => Number(b.is_default) - Number(a.is_default) || a.name.localeCompare(b.name));
    }
    return sorted;
  }, [notes, q, categoryFilter, sortKey]);

  // Clear selectedNotes when filtered notes change (search/category filter)
  useEffect(() => {
    const visibleIds = new Set(filteredNotes.map(n => n.id));
    setSelectedNotes(prev => {
      const filtered = new Set([...prev].filter(id => visibleIds.has(id)));
      // Only update state if something was removed (avoids infinite loops)
      if (filtered.size === prev.size) return prev;
      return filtered;
    });
  }, [filteredNotes]);

  const pinnedCount = notes.filter(n => n.is_default).length;

  return (
    <PageLayout title={t('notes.title') || 'Notes'}>
      <div className="space-y-4">
        {/* ── Header ── */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-2xl font-bold text-base-content flex items-center gap-2">
              <span className="icon-[tabler--notes] w-6 h-6 text-primary" />
              {t('notes.title') || 'Notes'}
            </h1>
            <p className="text-sm text-base-content/50 mt-0.5">
              {notes.length} {t('notes.totalNotes') || 'notes'}
              {pinnedCount > 0 && ` · ${pinnedCount} pinned`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              disabled={filteredNotes.length === 0}
              className="btn btn-ghost btn-sm gap-1.5"
              title="Export filtered notes as JSON"
            >
              <span className="icon-[tabler--download] w-4 h-4" />
              Export
            </button>
            <button
              onClick={() => { setEditing(null); setForm({ name: '', template_body: '', category: '', is_default: false, use_as_template: false }); setShowForm(true); }}
              className="btn btn-primary gap-2 active:scale-[0.98] transition-all"
            >
              <span className="icon-[tabler--plus]" />
              {t('notes.addTemplate') || 'New Note'}
            </button>
          </div>
        </div>

        {/* ── Search + Sort + Category Filter Bar ── */}
        <div className="bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-xl p-3 shadow-sm">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            {/* Search */}
            <div className="relative flex-1">
              <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 text-base-content/40" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('notes.searchPlaceholder') || 'Search notes...'}
                aria-label={t('notes.searchPlaceholder') || 'Search notes'}
                className="w-full pl-10 pr-9 py-2 rounded-lg bg-base-200/50
                  border border-base-300/50 text-base-content
                  placeholder:text-base-content/40
                  focus:outline-none focus:border-primary transition-colors text-sm"
              />
              {isFiltering ? (
                <div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  aria-label="filtering"
                  className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4
                    border-2 border-primary border-t-transparent rounded-full"
                />
              ) : search ? (
                <button
                  onClick={() => setSearch('')}
                  aria-label={t('common.clear')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content transition-colors"
                >
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              ) : null}
            </div>

            {/* Sort */}
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as typeof sortKey)}
              aria-label={t('notes.sortBy') || 'Sort by'}
              className="px-3 py-2 rounded-lg bg-base-200/50
                border border-base-300/50 text-base-content
                text-sm focus:outline-none focus:border-primary transition-colors sm:w-40"
            >
              <option value="pinned">{t('notes.sortPinned') || 'Pinned first'}</option>
              <option value="newest">{t('notes.sortNewest') || 'Newest'}</option>
              <option value="oldest">{t('notes.sortOldest') || 'Oldest'}</option>
              <option value="name-asc">{t('notes.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('notes.sortNameDesc') || 'Name (Z→A)'}</option>
            </select>

            {/* Category filter */}
            {availableCategories.length > 0 && (
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                aria-label="Filter by category"
                className="px-3 py-2 rounded-lg bg-base-200/50
                  border border-base-300/50 text-base-content
                  text-sm focus:outline-none focus:border-primary transition-colors sm:w-36"
              >
                <option value="">All categories</option>
                {availableCategories.map(cat => (
                  <option key={cat} value={cat}>{getCategoryLabel(cat)}</option>
                ))}
              </select>
            )}

            <label className="flex items-center gap-1.5 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={filteredNotes.length > 0 && selectedNotes.size === filteredNotes.length}
                onChange={selectAll}
                className="checkbox checkbox-primary checkbox-xs"
              />
              <span className="text-[10px] text-base-content/40">All</span>
            </label>
            <span className="text-xs text-base-content/40 whitespace-nowrap px-2">
              {filteredNotes.length} / {notes.length}
            </span>
          </div>
        </div>

        {/* ── Create/Edit Note Form (slide-up) ── */}
        <AnimatePresence>
          {showForm && (
            <form
              initial={{ opacity: 0, y: -10, scaleY: 0.95 }}
              animate={{ opacity: 1, y: 0, scaleY: 1 }}
              exit={{ opacity: 0, y: -10, scaleY: 0.95 }}
              transition={{ duration: 0.2 }}
              onSubmit={handleSubmit}
              className="bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-xl p-5 space-y-4 shadow-lg overflow-hidden"
            >
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-base-content flex items-center gap-2">
                  <span className="icon-[tabler--pencil] w-4 h-4 text-primary" />
                  {editing ? (t('common.edit') || 'Edit Note') : (t('notes.addTemplate') || 'New Note')}
                </h3>
                <button
                  type="button"
                  onClick={resetForm}
                  className="btn btn-ghost btn-sm btn-square"
                >
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Title */}
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-base-content/70 mb-1">
                    {t('notes.name') || 'Title'}
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    placeholder={t('notes.titlePlaceholder') || 'Note title...'}
                    required
                    className="input input-bordered w-full"
                    autoFocus
                  />
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-base-content/70 mb-1">
                    {t('notes.category') || 'Category'}
                  </label>
                  <select
                    value={form.category}
                    onChange={e => setForm({ ...form, category: e.target.value })}
                    className="select select-bordered w-full"
                  >
                    {NOTE_CATEGORIES.map(cat => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Content */}
              <div>
                <label className="block text-sm font-medium text-base-content/70 mb-1">
                  {t('notes.body') || 'Content'}
                </label>
                <textarea
                  value={form.template_body}
                  onChange={e => setForm({ ...form, template_body: e.target.value })}
                  placeholder={t('notes.bodyPlaceholder') || 'Write your notes here...'}
                  rows={6}
                  required
                  className="textarea textarea-bordered w-full text-sm leading-relaxed resize-y min-h-[120px]"
                />
              </div>

              {/* Toggle row: Pin + Template */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-4">
                  {/* Pin toggle */}
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={form.is_default}
                      onChange={e => setForm({ ...form, is_default: e.target.checked })}
                      className="toggle toggle-primary toggle-sm"
                    />
                    <span className="text-sm text-base-content/70 group-hover:text-base-content transition-colors flex items-center gap-1.5">
                      <span className="icon-[tabler--pin] w-3.5 h-3.5" />
                      {t('notes.setAsDefault') || 'Pin note'}
                    </span>
                  </label>
                  {/* Use as receipt template toggle */}
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={form.use_as_template}
                      onChange={e => setForm({ ...form, use_as_template: e.target.checked })}
                      className="toggle toggle-accent toggle-sm"
                    />
                    <span className="text-sm text-base-content/70 group-hover:text-base-content transition-colors flex items-center gap-1.5">
                      <span className="icon-[tabler--receipt] w-3.5 h-3.5" />
                      {t('notes.useAsReceiptTemplate') || 'Use as receipt template'}
                    </span>
                  </label>
                </div>

                <div className="flex gap-2">
                  <button type="button" onClick={resetForm} className="btn btn-ghost btn-sm">
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary btn-sm gap-1.5"
                    disabled={!form.name.trim() || !form.template_body.trim()}
                  >
                    <span className="icon-[tabler--check] w-3.5 h-3.5" />
                    {editing ? (t('common.update') || 'Update') : (t('common.save') || 'Save')}
                  </button>
                </div>
              </div>
            </form>
          )}
        </AnimatePresence>

        {/* ── Bulk Actions Bar ── */}
        {selectedNotes.size > 0 && (
          <div className="bg-primary/10 border border-primary/30 rounded-xl p-3 flex items-center justify-between gap-3">
            <span className="text-sm font-medium text-primary">
              {selectedNotes.size} selected
            </span>
            <div className="flex items-center gap-2">
              <button onClick={() => bulkPin(true)} className="btn btn-ghost btn-xs gap-1">
                <span className="icon-[tabler--pin] w-3.5 h-3.5" /> Pin all
              </button>
              <button onClick={() => bulkPin(false)} className="btn btn-ghost btn-xs gap-1">
                <span className="icon-[tabler--pin-off] w-3.5 h-3.5" /> Unpin all
              </button>
              <button onClick={bulkDelete} className="btn btn-ghost btn-xs gap-1 text-error">
                <span className="icon-[tabler--trash] w-3.5 h-3.5" /> Delete
              </button>
              <button onClick={() => setSelectedNotes(new Set())} className="btn btn-ghost btn-xs">
                Clear
              </button>
            </div>
          </div>
        )}

        {/* ── Notes Grid ── */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3">
              <div
                animate={{ rotate: 360 }}
                transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                className="w-8 h-8 border-[3px] border-primary border-t-transparent rounded-full"
              />
              <span className="text-sm text-base-content/50">{t('common.loading')}</span>
            </div>
          </div>
        ) : filteredNotes.length === 0 ? (
          <div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 text-base-content/40"
          >
            <span className="icon-[tabler--note-off] w-16 h-16 mb-4 opacity-30" />
            <p className="text-lg font-medium">
              {debouncedSearch || categoryFilter
                ? (t('common.noDataFound') || 'No matches found')
                : (t('notes.noTemplates') || 'No notes yet')}
            </p>
            {!debouncedSearch && !categoryFilter && (
              <button
                onClick={() => { setShowForm(true); }}
                className="btn btn-primary btn-sm mt-4 gap-2"
              >
                <span className="icon-[tabler--plus] w-4 h-4" />
                {t('notes.addTemplate') || 'Create your first note'}
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {filteredNotes.map((note, idx) => (
              <div
                key={note.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(idx * 0.03, 0.3) }}
                className={`group bg-base-100/70 backdrop-blur-sm border border-base-300/30 border-l-4
                  rounded-xl p-4 hover:shadow-lg hover:shadow-base-300/20
                  hover:border-primary/30 hover:bg-base-100/90
                  transition-all duration-200 relative ${note.category ? getCategoryBorder(note.category) : 'border-l-base-300'}`}
              >
                {/* Selection checkbox */}
                <div className="absolute top-2 left-2 z-10" onClick={e => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={selectedNotes.has(note.id)}
                    onChange={() => toggleSelect(note.id)}
                    className="checkbox checkbox-primary checkbox-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  />
                </div>
                <div className="cursor-pointer" onClick={() => handleEdit(note)}>
                {/* Pin indicator */}
                {note.is_default && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center shadow-lg shadow-primary/20">
                    <span className="icon-[tabler--pin] w-3 h-3 text-primary-content" />
                  </div>
                )}

                {/* Badges row */}
                <div className="flex flex-wrap items-center gap-1.5 mb-2">
                  {note.category && (
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${getCategoryColor(note.category)}`}>
                      <span className={getNoteIconClass(note.category)} /> {getCategoryLabel(note.category)}
                    </span>
                  )}
                  {note.use_as_template && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium badge-accent">
                      <span className="icon-[tabler--receipt] w-3 h-3" />
                      Template
                    </span>
                  )}
                </div>

                {/* Title */}
                <h3 className="font-semibold text-base-content text-sm leading-snug mb-1.5 line-clamp-2">
                  {note.name}
                </h3>

                {/* Content preview */}
                <div className="text-xs text-base-content/50 leading-relaxed mb-3 line-clamp-3 font-[inherit] whitespace-pre-wrap">
                  {getContentPreview(note.template_body)}
                </div>

                </div>
                {/* Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-base-300/20">
                  <span className="text-[10px] text-base-content/30">
                    {formatDate(note.updated_at || note.created_at)}
                  </span>
                  <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDuplicate(note); }}
                      disabled={duplicatingId === note.id}
                      className="p-1.5 rounded-lg text-base-content/30 hover:text-info hover:bg-info/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Duplicate note"
                    >
                      <span className="icon-[tabler--copy] w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleTogglePin(note); }}
                      className={`p-1.5 rounded-lg transition-colors ${
                        note.is_default
                          ? 'text-primary hover:bg-primary/10'
                          : 'text-base-content/30 hover:text-base-content/60 hover:bg-base-300/30'
                      }`}
                      title={note.is_default ? 'Unpin' : 'Pin note'}
                    >
                      <span className="icon-[tabler--pin] w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(note.id); }}
                      className="p-1.5 rounded-lg text-base-content/30 hover:text-error hover:bg-error/10 transition-colors"
                      title={t('common.delete')}
                    >
                      <span className="icon-[tabler--trash] w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
