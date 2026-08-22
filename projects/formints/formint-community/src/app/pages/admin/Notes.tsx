import { useState, useEffect, useMemo, useRef } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import { Note, NoteStep } from '../../../types';
import { useDebouncedSearch } from '../../../hooks/useDebouncedSearch';
import AnimatePresence from '../../../components/ui/AnimatePresence';
import SearchInput from '../../../components/ui/SearchInput';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';
import PrepStepsEditor from '../../../components/notes/PrepStepsEditor';
import { parseNoteSteps, serializeNoteSteps } from '../../../utils/noteSteps';
import Card from '../../../components/ui/Card';

// ── Category color mapping ──
const CATEGORY_COLORS: Record<string, string> = {
  general: 'bg-base-200 text-base-content/60',
  idea: 'bg-primary/10 text-primary',
  task: 'bg-warning/10 text-warning',
  recipe: 'bg-success/10 text-success',
  receipt: 'bg-primary/10 text-primary',
  preparation: 'bg-info/10 text-info',
  'chef-tips': 'bg-warning/10 text-warning',
  allergen: 'bg-error/10 text-error',
  plating: 'bg-success/10 text-success',
  inventory: 'bg-info/10 text-info',
  staff: 'bg-secondary/10 text-secondary',
  finance: 'bg-primary/10 text-primary',
  customer: 'bg-error/10 text-error',
  other: 'bg-base-200 text-base-content/60',
};

const NOTE_CATEGORIES = [
  { value: '', label: 'General', color: 'bg-base-200 text-base-content/60' },
  { value: 'idea', label: 'Idea', color: 'bg-primary/10 text-primary' },
  { value: 'task', label: 'Task', color: 'bg-warning/10 text-warning' },
  { value: 'receipt', label: 'Receipt Template', color: 'bg-primary/10 text-primary' },
  { value: 'recipe', label: 'Recipe', color: 'bg-success/10 text-success' },
  { value: 'preparation', label: 'Preparation Steps', color: 'bg-info/10 text-info' },
  { value: 'chef-tips', label: 'Chef Tips', color: 'bg-warning/10 text-warning' },
  { value: 'allergen', label: 'Allergen Info', color: 'bg-error/10 text-error' },
  { value: 'plating', label: 'Plating Guide', color: 'bg-success/10 text-success' },
  { value: 'inventory', label: 'Inventory', color: 'bg-info/10 text-info' },
  { value: 'staff', label: 'Staff', color: 'bg-secondary/10 text-secondary' },
  { value: 'finance', label: 'Finance', color: 'bg-primary/10 text-primary' },
  { value: 'customer', label: 'Customer', color: 'bg-error/10 text-error' },
  { value: 'other', label: 'Other', color: 'bg-base-200 text-base-content/60' },
];

function getCategoryColor(cat: string | null | undefined): string {
  if (!cat) return 'bg-base-200 text-base-content/60';
  return CATEGORY_COLORS[cat.toLowerCase()] || 'bg-base-200 text-base-content/60';
}

function getCategoryAccent(cat: string | null | undefined): string {
  if (!cat) return 'var(--color-base-300)';
  const accents: Record<string, string> = {
    general: 'var(--color-base-300)',
    idea: 'var(--color-primary)',
    task: 'var(--color-warning)',
    recipe: 'var(--color-success)',
    receipt: 'var(--color-primary)',
    preparation: 'var(--color-info)',
    'chef-tips': 'var(--color-warning)',
    allergen: 'var(--color-error)',
    plating: 'var(--color-success)',
    inventory: 'var(--color-info)',
    staff: 'var(--color-secondary)',
    finance: 'var(--color-primary)',
    customer: 'var(--color-error)',
    other: 'var(--color-base-300)',
  };
  return accents[cat.toLowerCase()] || 'var(--color-base-300)';
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
  return preview || '-';
}

function getNoteIconClass(cat: string | null | undefined): string {
  switch ((cat || '').toLowerCase()) {
    case 'idea': return 'ri-lightbulb-flash-line ri-12px';
    case 'task': return 'ri-checkbox-line ri-12px';
    case 'recipe': return 'ri-restaurant-2-line ri-12px';
    case 'receipt': return 'ri-receipt-line ri-12px';
    case 'preparation': return 'ri-check-double-line ri-12px';
    case 'chef-tips': return 'ri-lightbulb-flash-line ri-12px';
    case 'allergen': return 'ri-alert-line ri-12px';
    case 'plating': return 'ri-palette-line ri-12px';
    case 'inventory': return 'ri-box-2-line ri-12px';
    case 'staff': return 'ri-group-line ri-12px';
    case 'finance': return 'ri-money-dollar-circle-line ri-12px';
    case 'customer': return 'ri-user-3-line ri-12px';
    default: return 'ri-sticky-note-2-line ri-12px';
  }
}

export default function Notes() {
  const { t } = useTranslation();
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Note | null>(null);
  const [form, setForm] = useState<{
    name: string;
    template_body: string;
    category: string;
    is_default: boolean;
    use_as_template: boolean;
    selectable: boolean;
    steps: NoteStep[];
  }>({ name: '', template_body: '', category: '', is_default: false, use_as_template: false, selectable: false, steps: [] });
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [selectableFilter, setSelectableFilter] = useState(false);

  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<'name-asc' | 'name-desc' | 'newest' | 'oldest' | 'pinned'>('pinned');
  const [selectedNotes, setSelectedNotes] = useState<Set<number>>(new Set());
  const [duplicatingId, setDuplicatingId] = useState<number | null>(null);
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleCopy = async (note: Note) => {
    const text = note.template_body || '';
    if (!text) return;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      setCopiedId(note.id);
      if (copyTimer.current) clearTimeout(copyTimer.current);
      copyTimer.current = setTimeout(() => setCopiedId(null), 1500);
    } catch (error) {
      console.error('Error copying note:', error);
    }
  };

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

  const hasBody = form.template_body.trim().length > 0;
  const hasSteps = form.category === 'preparation' && form.steps.length > 0;
  const canSave = !!form.name.trim() && (hasBody || hasSteps);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSave) return;
    try {
      const stepsJson = serializeNoteSteps(form.steps);
      const payload = {
        name: form.name.trim(),
        template_body: form.template_body.trim(),
        category: form.category || null,
        use_as_template: form.use_as_template,
        selectable: form.selectable,
        steps: stepsJson,
      };
      if (editing) {
        await invoke('update_note', {
          id: editing.id,
          update: {
            ...payload,
            is_default: form.is_default,
          },
        });
      } else {
        const result = await invoke<Note>('add_note', { template: payload });
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
      selectable: note.selectable,
      steps: parseNoteSteps(note.steps),
    });
    setShowForm(true);
  };

  const [toDelete, setToDelete] = useState<Note | null>(null);
  const [showBulkDelete, setShowBulkDelete] = useState(false);

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await invoke('delete_note', { id: toDelete.id });
      setSelectedNotes(prev => { const next = new Set(prev); next.delete(toDelete.id); return next; });
      setToDelete(null);
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
          selectable: note.selectable,
          steps: note.steps ?? null,
        }
      });
      loadNotes({ quiet: true });
    } catch (error) {
      console.error('Error duplicating note:', error);
    } finally {
      setDuplicatingId(null);
    }
  };

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
    try {
      for (const id of selectedNotes) {
        await invoke('delete_note', { id });
      }
      setShowBulkDelete(false);
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
    setForm({ name: '', template_body: '', category: '', is_default: false, use_as_template: false, selectable: false, steps: [] });
  };

  const availableCategories = useMemo(() => {
    const cats = new Set(notes.map(n => (n.category || '').toLowerCase()).filter(Boolean));
    return Array.from(cats);
  }, [notes]);

  const q = debouncedSearch.trim().toLowerCase();
  const filteredNotes = useMemo(() => {
    let result = notes;

    if (q) {
      result = result.filter(n =>
        n.name.toLowerCase().includes(q) ||
        (n.template_body || '').toLowerCase().includes(q) ||
        (n.category || '').toLowerCase().includes(q)
      );
    }

    if (categoryFilter) {
      result = result.filter(n => (n.category || '').toLowerCase() === categoryFilter);
    }

    if (selectableFilter) {
      result = result.filter(n => !!n.selectable);
    }

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
  }, [notes, q, categoryFilter, selectableFilter, sortKey]);

  useEffect(() => {
    const visibleIds = new Set(filteredNotes.map(n => n.id));
    setSelectedNotes(prev => {
      const filtered = new Set([...prev].filter(id => visibleIds.has(id)));
      if (filtered.size === prev.size) return prev;
      return filtered;
    });
  }, [filteredNotes]);

  const pinnedCount = notes.filter(n => n.is_default).length;

  return (
    <PageLayout title={t('notes.title') || 'Notes'}>
      <div className="space-y-4">
        {/* ── Eyebrow tag ── */}
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-primary/10 text-primary">
            <span className="ri-sticky-note-2-line ri-12px" />
            Documentation
          </span>
        </div>

        {/* ── Header ── */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-2xl font-bold text-base-content flex items-center gap-2">
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
              <span className="ri-download-line ri-16px" />
              Export
            </button>
            <button
              onClick={() => { setEditing(null); setForm({ name: '', template_body: '', category: '', is_default: false, use_as_template: false, selectable: false, steps: [] }); setShowForm(true); }}
              className="btn btn-primary btn-sm gap-1 shrink-0 active:scale-[0.98] transition-transform"
            >
              <span className="ri-add-line ri-14px" />
              {t('notes.addTemplate') || 'New Note'}
            </button>
          </div>
        </div>

        {/* ── Search + Sort + Category Filter Bar — compact bezel ── */}
        <Card padding="sm" variant="bezel">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder={t('notes.searchPlaceholder') || 'Search notes...'}
              ariaLabel={t('notes.searchPlaceholder') || 'Search notes'}
              testId="notes-search-input"
              loading={isFiltering}
              className="flex-1"
            />

            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as typeof sortKey)}
              aria-label={t('notes.sortBy') || 'Sort by'}
              className="select h-8 text-xs sm:w-40"
            >
              <option value="pinned">{t('notes.sortPinned') || 'Pinned first'}</option>
              <option value="newest">{t('notes.sortNewest') || 'Newest'}</option>
              <option value="oldest">{t('notes.sortOldest') || 'Oldest'}</option>
              <option value="name-asc">{t('notes.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('notes.sortNameDesc') || 'Name (Z→A)'}</option>
            </select>

            {availableCategories.length > 0 && (
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                aria-label="Filter by category"
                className="select h-8 text-xs sm:w-36"
              >
                <option value="">All categories</option>
                {availableCategories.map(cat => (
                  <option key={cat} value={cat}>{getCategoryLabel(cat)}</option>
                ))}
              </select>
            )}

            <button
              type="button"
              onClick={() => setSelectableFilter(f => !f)}
              aria-pressed={selectableFilter}
              className={`inline-flex items-center gap-1.5 px-3 h-8 rounded-full text-xs font-medium transition-all ${
                selectableFilter ? 'bg-primary/10 text-primary' : 'bg-base-200 text-base-content/50 hover:bg-primary/10 hover:text-primary'
              }`}
            >
              <span className="ri-cursor-line ri-12px" />
              {t('notes.selectable') || 'Selectable'}
            </button>

            <label className="flex items-center gap-1.5 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={filteredNotes.length > 0 && selectedNotes.size === filteredNotes.length}
                onChange={selectAll}
                className="checkbox checkbox-primary checkbox-xs"
              />
              <span className="text-[10px] text-base-content/40">All</span>
            </label>
            <span className="text-[10px] text-base-content/40 whitespace-nowrap px-2">
              {filteredNotes.length} / {notes.length}
            </span>
          </div>
        </Card>

        {/* ── Create/Edit Note Form (slide-up) ── */}
        <AnimatePresence>
          {showForm && (
            <form
              onSubmit={handleSubmit}
              className="bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-2xl p-5 space-y-4 shadow-lg overflow-hidden"
            >
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-base-content flex items-center gap-2">
                  <span className="ri-pencil-line ri-16px text-primary" />
                  {editing ? (t('common.edit') || 'Edit Note') : (t('notes.addTemplate') || 'New Note')}
                </h3>
                <button
                  type="button"
                  onClick={resetForm}
                  className="w-7 h-7 rounded-full bg-base-200 flex items-center justify-center hover:bg-base-300 transition-colors"
                >
                  <span className="ri-close-line ri-14px" />
                </button>
              </div>

              {form.category === 'preparation' && (
                <p className="-mt-2 text-[11px] text-base-content/40 flex items-center gap-1.5">
                  <span className="ri-check-double-line ri-14px text-info" />
                  {t('notes.preparationHint') || 'Structured steps below will render as a prep checklist on the Kitchen Display.'}
                </p>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="sm:col-span-2 space-y-1">
                  <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                    {t('notes.name') || 'Title'} <span className="text-error">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    placeholder={t('notes.titlePlaceholder') || 'Note title...'}
                    required
                    className="input input-compact w-full"
                    autoFocus
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                    {t('notes.category') || 'Category'}
                  </label>
                  <select
                    value={form.category}
                    onChange={e => setForm({ ...form, category: e.target.value })}
                    className="select w-full h-8 text-xs"
                  >
                    {NOTE_CATEGORIES.map(cat => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {form.category === 'preparation' ? (
                <div className="space-y-1">
                  <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                    {t('notes.stepsTitle') || 'Preparation Steps'}
                  </label>
                  <PrepStepsEditor
                    value={form.steps}
                    onChange={steps => setForm(f => ({ ...f, steps }))}
                  />
                </div>
              ) : (
                <div className="space-y-1">
                  <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                    {t('notes.body') || 'Content'}
                  </label>
                  <textarea
                    value={form.template_body}
                    onChange={e => setForm({ ...form, template_body: e.target.value })}
                    placeholder={t('notes.bodyPlaceholder') || 'Write your notes here...'}
                    rows={6}
                    required
                    className="textarea w-full text-sm leading-relaxed resize-y min-h-[120px]"
                  />
                </div>
              )}

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2 border-t border-base-300/30">
                <div className="flex flex-wrap items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={form.is_default}
                      onChange={e => setForm({ ...form, is_default: e.target.checked })}
                      className="checkbox checkbox-primary checkbox-sm"
                    />
                    <span className="text-xs text-base-content/70 group-hover:text-base-content transition-colors flex items-center gap-1.5">
                      <span className="ri-pushpin-2-line ri-14px" />
                      {t('notes.setAsDefault') || 'Pin note'}
                    </span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={form.use_as_template}
                      onChange={e => setForm({ ...form, use_as_template: e.target.checked })}
                      className="checkbox checkbox-primary checkbox-sm"
                    />
                    <span className="text-xs text-base-content/70 group-hover:text-base-content transition-colors flex items-center gap-1.5">
                      <span className="ri-receipt-line ri-14px" />
                      {t('notes.useAsReceiptTemplate') || 'Use as receipt template'}
                    </span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={form.selectable}
                      onChange={e => setForm({ ...form, selectable: e.target.checked })}
                      className="checkbox checkbox-primary checkbox-sm"
                    />
                    <span className="text-xs text-base-content/70 group-hover:text-base-content transition-colors flex items-center gap-1.5">
                      <span className="ri-cursor-line ri-14px" />
                      {t('notes.selectable') || 'Quick-select on Sale'}
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
                    disabled={!canSave}
                  >
                    <span className="ri-check-line ri-14px" />
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
                <span className="ri-pushpin-2-line ri-14px" /> Pin all
              </button>
              <button onClick={() => bulkPin(false)} className="btn btn-ghost btn-xs gap-1">
                <span className="ri-pushpin-2-line ri-14px rotate-45" /> Unpin all
              </button>
              <button onClick={() => setShowBulkDelete(true)} className="btn btn-ghost btn-xs gap-1 text-error">
                <span className="ri-delete-bin-line ri-14px" /> Delete
              </button>
              <button onClick={() => setSelectedNotes(new Set())} className="btn btn-ghost btn-xs">
                Clear
              </button>
            </div>
          </div>
        )}

        {/* ── Notes Grid — Double-Bezel cards ── */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-[3px] border-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-base-content/50">{t('common.loading')}</span>
            </div>
          </div>
        ) : filteredNotes.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-base-content/40">
            <span className="ri-sticky-note-line w-16 h-16 mb-4 opacity-30" />
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
                <span className="ri-add-line ri-16px" />
                {t('notes.addTemplate') || 'Create your first note'}
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredNotes.map((note, idx) => (
              <div
                key={note.id}
                className={`
                  group relative
                  overflow-hidden
                  bg-base-200/40 dark:bg-white/5
                  border border-base-300/25 dark:border-white/10
                  rounded-[1.5rem]
                  p-1.5
                  shadow-[var(--shadow-bezel-outer)]
                  transition-all duration-500 ease-[var(--ease-fluid)]
                  hover:-translate-y-0.5 hover:shadow-[var(--shadow-bezel-hover)]
                  animate-fade-up delay-${Math.min(idx * 75, 450)}
                `}
              >
                {/* Category accent bar */}
                <div
                  className="absolute top-0 bottom-0 inset-inline-start-0 w-1 rounded-l-[inherit]"
                  style={{ backgroundColor: getCategoryAccent(note.category) }}
                />

                {/* Inner core */}
                <div className="bg-base-100 dark:bg-base-900 rounded-[1.125rem] p-4 shadow-[var(--shadow-bezel-inner)] h-full">
                  {/* Selection checkbox */}
                  <div className="absolute top-2 left-3 z-10" onClick={e => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedNotes.has(note.id)}
                      onChange={() => toggleSelect(note.id)}
                      className="checkbox checkbox-primary checkbox-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    />
                  </div>

                  {/* Pin indicator */}
                  {note.is_default && (
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center shadow-lg shadow-primary/20 z-10">
                      <span className="ri-pushpin-2-line ri-12px text-primary-content" />
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
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary">
                        <span className="ri-receipt-line ri-12px" />
                        Template
                      </span>
                    )}
                    {note.selectable && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-success/10 text-success">
                        <span className="ri-cursor-line ri-12px" />
                        {t('notes.selectable') || 'Selectable'}
                      </span>
                    )}
                    {note.category === 'preparation' && (note.steps || '').length > 2 && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-info/10 text-info">
                        <span className="ri-check-double-line ri-12px" />
                        {parseNoteSteps(note.steps).length} steps
                      </span>
                    )}
                  </div>

                  {/* Title */}
                  <h3 className="font-semibold text-base-content text-sm leading-snug mb-1.5 line-clamp-2 cursor-pointer" onClick={() => handleEdit(note)}>
                    {note.name}
                  </h3>

                  {/* Content preview */}
                  <div className="text-[11px] text-base-content/50 leading-relaxed mb-3 line-clamp-3 font-[inherit] whitespace-pre-wrap cursor-pointer" onClick={() => handleEdit(note)}>
                    {getContentPreview(note.template_body)}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-2 border-t border-base-300/20">
                    <span className="text-[10px] text-base-content/30">
                      {formatDate(note.updated_at || note.created_at)}
                    </span>
                    <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleCopy(note); }}
                        className="w-7 h-7 rounded-lg text-base-content/30 hover:text-info hover:bg-info/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                        title={copiedId === note.id ? 'Copied!' : 'Copy note text'}
                      >
                        {copiedId === note.id
                          ? <span className="ri-check-line ri-14px text-success" />
                          : <span className="ri-clipboard-line ri-14px" />}
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDuplicate(note); }}
                        disabled={duplicatingId === note.id}
                        className="w-7 h-7 rounded-lg text-base-content/30 hover:text-info hover:bg-info/10 flex items-center justify-center transition-all duration-200 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Duplicate note"
                      >
                        <span className="ri-file-copy-line ri-14px" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleTogglePin(note); }}
                        className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200 active:scale-95 ${
                          note.is_default
                            ? 'text-primary hover:bg-primary/10'
                            : 'text-base-content/30 hover:text-base-content/60 hover:bg-base-300/30'
                        }`}
                        title={note.is_default ? 'Unpin' : 'Pin note'}
                      >
                        <span className="ri-pushpin-2-line ri-14px" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); setToDelete(note); }}
                        className="w-7 h-7 rounded-lg text-base-content/30 hover:text-error hover:bg-error/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                        title={t('common.delete')}
                      >
                        <span className="ri-delete-bin-line ri-14px" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ConfirmDialog
        isOpen={!!toDelete}
        onClose={() => setToDelete(null)}
        onConfirm={handleDelete}
        title={t('notes.deleteTitle', 'Delete note')}
        message={t('notes.deleteMessage', 'This will permanently remove the note')}
        itemName={toDelete?.name ?? ''}
        confirmLabel={t('common.delete')}
      />

      <ConfirmDialog
        isOpen={showBulkDelete}
        onClose={() => setShowBulkDelete(false)}
        onConfirm={bulkDelete}
        title={t('notes.bulkDeleteTitle', 'Delete notes')}
        message={t('notes.bulkDeleteMessage', 'This will permanently remove')}
        itemName={t('notes.bulkCount', '{{count}} note(s)', { count: selectedNotes.size })}
        confirmLabel={t('common.delete')}
      />
    </PageLayout>
  );
}
