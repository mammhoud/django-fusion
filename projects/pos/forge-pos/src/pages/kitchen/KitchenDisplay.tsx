import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import PageLayout from '../../components/layout/PageLayout';
import { iconClass } from '../../lib/icons';
import { useTranslation } from 'react-i18next';
import { KitchenTicket, Sale, Category, Note, NoteStep } from '../../types';
import SearchInput from '../../components/ui/SearchInput';
import CategoryFilterPills from '../../components/pos/CategoryFilterPills';
import Modal from '../../components/ui/Modal';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import { useKDSNotification, CHIME_VARIANTS, type ChimeVariant } from '../../hooks/useKDSNotification';
import { useCurrency } from '../../contexts/CurrencyContext';
import StatCard from '../../components/ui/StatCard';
import { parseNoteSteps } from '../../utils/noteSteps';


// Type from the Rust KitchenTicketCategory model (ticket → product-category rows)
interface KitchenTicketCategoryRow {
  ticket_id: number;
  category_id: number;
  name: string;
  color?: string | null;
}

// Type from the Rust SaleItem model (mirrored here for the ticket detail modal)
interface SaleItemData {
  id: number;
  sale_id: number;
  product_name: string;
  price: number;
  quantity: number;
  unit: string;
  subtotal: number;
  created_at: string;
}

// ── Order type icon/label mapping ──
const ORDER_TYPE_MAP: Record<number, { icon: string; label: string; color: string }> = {
  1: { icon: 'lucide:utensils', label: 'Dine-in / Extra', color: 'text-primary bg-primary/10' },
  2: { icon: 'lucide:package', label: 'Takeaway / Dated', color: 'text-warning bg-warning/10' },
  3: { icon: 'lucide:truck', label: 'Delivery', color: 'text-success bg-success/10' },
};

// ── Elapsed time formatter ──
function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr.replace(' ', 'T')).getTime();
  if (diff < 0) return 'just now';
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ${mins % 60}m ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/**
 * Check if a ticket has been pending/preparing longer than its estimated
 * prep time. Returns `true` if the elapsed time exceeds the estimate.
 */
function isOverdue(ticket: KitchenTicket): boolean {
  if (ticket.status === 'delivered' || ticket.status === 'ready') return false;
  if (ticket.prepare_time_minutes <= 0) return false;
  const elapsed = Date.now() - new Date(ticket.created_at.replace(' ', 'T')).getTime();
  const estMs = ticket.prepare_time_minutes * 60 * 1000;
  return elapsed > estMs;
}

// ── Click tracking entries stored in localStorage ──
interface ClickRecord {
  ticketId: number;
  saleId: number;
  timestamp: string;
  action: 'opened' | 'closed' | 'started' | 'completed';
}

const CLICK_STORAGE_KEY = 'kds-click-history';

function loadClickRecords(): ClickRecord[] {
  try {
    return JSON.parse(localStorage.getItem(CLICK_STORAGE_KEY) || '[]');
  } catch {
    return [];
  }
}

function saveClickRecord(record: ClickRecord): ClickRecord[] {
  const records = loadClickRecords();
  records.push(record);
  // Keep last 500 entries to avoid unbounded growth
  if (records.length > 500) records.splice(0, records.length - 500);
  localStorage.setItem(CLICK_STORAGE_KEY, JSON.stringify(records));
  return records;
}

export default function KitchenDisplay() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
  const [tickets, setTickets] = useState<KitchenTicket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('pending');
  // ── Product-category filter (colored tag pills) ──
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | 'all'>('all');
  const [ticketCategoryIds, setTicketCategoryIds] = useState<Record<number, number[]>>({});

  // ── P2 KDS enhancements: sort, mute, overdue tracking ──
  const [sortOrder, setSortOrder] = useState<'newest' | 'overdue-first'>(() => {
    try { return (localStorage.getItem('kds-sort-order') as 'newest' | 'overdue-first') || 'newest'; }
    catch { return 'newest'; }
  });
  const [chimeVariant, setChimeVariant] = useState<ChimeVariant>(() => {
    try { return (localStorage.getItem('kds-chime-variant') as ChimeVariant) || 'chime1'; }
    catch { return 'chime1'; }
  });
  const [mutedUntil, setMutedUntil] = useState<number | null>(() => {
    try {
      const saved = localStorage.getItem('kds-muted-until');
      if (saved) {
        const ts = parseInt(saved, 10);
        return ts > Date.now() ? ts : null;
      }
    } catch {}
    return null;
  });
  // Calculate mutedUntil directly from state for the countdown display
  const muteRemaining = useMemo(() => {
    if (!mutedUntil || mutedUntil <= Date.now()) return null;
    const remaining = Math.ceil((mutedUntil - Date.now()) / 60000);
    return remaining > 0 ? `${remaining}m` : '<1m';
  }, [mutedUntil]);

  // Ticket detail modal state
  const [selectedTicket, setSelectedTicket] = useState<KitchenTicket | null>(null);
  const [saleItems, setSaleItems] = useState<SaleItemData[]>([]);
  const [isLoadingItems, setIsLoadingItems] = useState(false);
  const [saleDetail, setSaleDetail] = useState<{
    order_type: string;
    table_number?: number | null;
    delivery_address?: string | null;
    total_amount?: number;
  } | null>(null);
  const [chefReport, setChefReport] = useState<ClickRecord[]>([]);
  const [showPreferences, setShowPreferences] = useState(false);
  // ── Selectable notes (quick-pick prep steps + attached notes on the ticket) ──
  const [selectableNotes, setSelectableNotes] = useState<Note[]>([]);
  const [activePrepNoteId, setActivePrepNoteId] = useState<number | null>(null);
  const [checkedSteps, setCheckedSteps] = useState<Record<string, boolean>>({});
  const [showQuickAddNote, setShowQuickAddNote] = useState(false);
  const [quickNoteName, setQuickNoteName] = useState('');
  const [quickNoteBody, setQuickNoteBody] = useState('');
  // Preference: which order types to show in the KDS (by priority: 1=dine-in, 2=takeaway, 3=delivery)
  const [preferredPriorities, setPreferredPriorities] = useState<number[]>(() => {
    try { return JSON.parse(localStorage.getItem('kds-preferred-priorities') || '[1,2,3]'); }
    catch { return [1, 2, 3]; }
  });
  const reportDialogRef = useRef<HTMLDialogElement>(null);

  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  // ── Sound + tab-title flash for new pending tickets ──
  useKDSNotification(tickets, mutedUntil, chimeVariant);

  useEffect(() => {
    loadTickets({ quiet: false });
  }, [filter]);

  // ── Sync tray badge on mount only (not on filter changes) ──
  useEffect(() => {
    invoke('sync_tray_badge').catch(() => {});
  }, []);

  // ── Real-time event listener — replaces the old 10s polling ──
  useEffect(() => {
    const unlisten = listen<{ type: string; ticket: KitchenTicket }>(
      'kitchen-ticket-update',
      () => {
        loadTickets({ quiet: true });
      },
    );
    return () => {
      unlisten.then(fn => fn());
    };
  }, [filter]);

  // ── Load selectable notes for the quick-notes / prep-steps picker ──
  useEffect(() => {
    invoke<Note[]>('get_selectable_notes')
      .then(rows => setSelectableNotes(rows ?? []))
      .catch(() => {});
  }, []);

  const loadTickets = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [data, categoryRows] = await Promise.all([
        invoke<KitchenTicket[]>('get_kitchen_tickets', { status: filter === 'all' ? null : filter }),
        invoke<KitchenTicketCategoryRow[]>('get_kitchen_ticket_categories', { status: filter === 'all' ? null : filter })
          .then(rows => rows ?? [])
          .catch(() => []),
      ]);
      setTickets(data);

      // Build category list (deduped) + per-ticket category membership
      const catById = new Map<number, Category>();
      const perTicket: Record<number, number[]> = {};
      for (const row of categoryRows) {
        if (!catById.has(row.category_id)) {
          catById.set(row.category_id, { id: row.category_id, name: row.name, color: row.color });
        }
        (perTicket[row.ticket_id] ??= []).push(row.category_id);
      }
      setCategories([...catById.values()]);
      setTicketCategoryIds(perTicket);
      // Reset category selection if it no longer matches the loaded set
      setSelectedCategory(prev =>
        prev !== 'all' && !Object.values(perTicket).some(ids => ids.includes(prev))
          ? 'all'
          : prev,
      );
    } catch (error) {
      console.error('Error loading kitchen tickets:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const updateStatus = useCallback(async (ticket: KitchenTicket, status: string) => {
    try {
      await invoke('update_kitchen_ticket', { id: ticket.id, update: { status } });
      setClickRecords(saveClickRecord({
        ticketId: ticket.id,
        saleId: ticket.sale_id,
        timestamp: new Date().toISOString(),
        action: status === 'preparing' ? 'started' : status === 'delivered' ? 'completed' : 'closed',
      }));
      loadTickets({ quiet: true });
    } catch (error) {
      console.error('Error updating ticket:', error);
      loadTickets({ quiet: true });
    }
  }, []);

  /*** Open detail modal — fetches sale items + sale details for the clicked ticket ***/
  const openDetail = useCallback(async (ticket: KitchenTicket) => {
    setSelectedTicket(ticket);
    setIsLoadingItems(true);
    setClickRecords(saveClickRecord({ ticketId: ticket.id, saleId: ticket.sale_id, timestamp: new Date().toISOString(), action: 'opened' }));
    try {
      // Fetch sale items
      const items = await invoke<SaleItemData[]>('get_sale_items_by_sale_id', { saleId: ticket.sale_id });
      setSaleItems(items);
      // Fetch sale details for order type, table, delivery info, etc.
      try {
        const sale = await invoke<Sale>('get_sale_by_id', { id: ticket.sale_id });
        setSaleDetail({
          order_type: sale.order_type || 'dine-in',
          table_number: sale.table_number,
          delivery_address: sale.delivery_address,
          total_amount: sale.total_amount,
        });
      } catch {
        setSaleDetail(null);
      }
      setChefReport(loadClickRecords().filter(r => r.ticketId === ticket.id));
    } catch (error) {
      console.error('Error loading sale items:', error);
      setSaleItems([]);
    } finally {
      setIsLoadingItems(false);
    }
  }, []);

  const closeDetail = useCallback(() => {
    if (selectedTicket) {
      saveClickRecord({ ticketId: selectedTicket.id, saleId: selectedTicket.sale_id, timestamp: new Date().toISOString(), action: 'closed' });
    }
    setSelectedTicket(null);
    setSaleItems([]);
    setSaleDetail(null);
    setChefReport([]);
    setActivePrepNoteId(null);
    setCheckedSteps({});
  }, [selectedTicket]);

  /*** Attach a selectable note to the open ticket (persists into ticket.notes) ***/
  const attachNoteToTicket = useCallback(async (note: Note) => {
    if (!selectedTicket) return;
    const existing = selectedTicket.notes || '';
    const block = note.template_body && note.template_body.trim()
      ? note.template_body.trim()
      : note.name;
    const next = existing
      ? `${existing}\n\n[${note.name}] ${block}`
      : `[${note.name}] ${block}`;
    try {
      await invoke('update_kitchen_ticket', { id: selectedTicket.id, update: { notes: next } });
      loadTickets({ quiet: true });
    } catch (error) {
      console.error('Error attaching note to ticket:', error);
    }
  }, [selectedTicket, loadTickets]);

  /*** Quick-add a new selectable note from the KDS detail modal ***/
  const handleQuickAddNote = useCallback(async () => {
    if (!quickNoteName.trim()) return;
    try {
      const note = await invoke<Note>('add_note', {
        template: {
          name: quickNoteName.trim(),
          template_body: quickNoteBody.trim() || quickNoteName.trim(),
          category: 'preparation',
          use_as_template: false,
          selectable: true,
          steps: null,
        },
      });
      setSelectableNotes(prev => [...prev, note]);
      setShowQuickAddNote(false);
      setQuickNoteName('');
      setQuickNoteBody('');
      if (selectedTicket) {
        await attachNoteToTicket(note);
      }
    } catch (error) {
      console.error('Error adding quick note:', error);
    }
  }, [quickNoteName, quickNoteBody, selectedTicket, attachNoteToTicket]);

  // Active prep note = explicitly picked one, else first preparation note with steps
  const activePrepNote = useMemo(() => {
    if (activePrepNoteId != null) {
      return selectableNotes.find(n => n.id === activePrepNoteId) || null;
    }
    return selectableNotes.find(n => n.category === 'preparation' && parseNoteSteps(n.steps).length > 0) || null;
  }, [activePrepNoteId, selectableNotes]);

  const activePrepSteps: NoteStep[] = useMemo(
    () => (activePrepNote ? parseNoteSteps(activePrepNote.steps) : []),
    [activePrepNote],
  );

  // Filter — text search + order-type preference + product category
  const q = debouncedSearch.trim().toLowerCase();
  const showAllPriorities = preferredPriorities.length === 0;
  const rawFiltered = tickets.filter(t => {
    if (q && !String(t.sale_id || '').includes(q) && !(t.notes || '').toLowerCase().includes(q)) return false;
    if (selectedCategory !== 'all' && !(ticketCategoryIds[t.id] ?? []).includes(selectedCategory)) return false;
    return showAllPriorities || preferredPriorities.includes(t.priority);
  });

  // Per-category ticket counts for pill badges
  const categoryCounts = useMemo(() => {
    const counts: Record<number, number> = {};
    for (const ids of Object.values(ticketCategoryIds)) {
      for (const id of new Set(ids)) counts[id] = (counts[id] ?? 0) + 1;
    }
    return counts;
  }, [ticketCategoryIds]);

  // ── Sort: overdue-first or newest first ──
  const filteredTickets = useMemo(() => {
    const sorted = [...rawFiltered];
    if (sortOrder === 'overdue-first') {
      sorted.sort((a, b) => {
        const aOverdue = isOverdue(a);
        const bOverdue = isOverdue(b);
        if (aOverdue && !bOverdue) return -1;
        if (!aOverdue && bOverdue) return 1;
        // Both overdue or both not overdue — sort by newest first
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
    } else {
      // Newest first (default)
      sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }
    return sorted;
  }, [rawFiltered, sortOrder]);

  const statusColors: Record<string, string> = {
    pending: 'border-warning/50 bg-warning/5',
    preparing: 'border-primary/40 bg-primary/5',
    ready: 'border-success/50 bg-success/5',
    delivered: 'border-base-300 bg-base-200/30',
  };

  const statusBadges: Record<string, string> = {
    pending: 'badge badge-soft badge-warning',
    preparing: 'badge badge-soft badge-info',
    ready: 'badge badge-soft badge-success',
    delivered: 'badge badge-soft badge-neutral',
  };

  // Cache click records in state to avoid repeated localStorage reads
  const [clickRecords, setClickRecords] = useState<ClickRecord[]>(() => loadClickRecords());
  const ticketClickCount = clickRecords.length;

  // Refresh click records when modal opens
  const openChefReport = useCallback(() => {
    setClickRecords(loadClickRecords());
    setTimeout(() => reportDialogRef.current?.showModal(), 50);
  }, []);

  const clearClickHistory = useCallback(() => {
    localStorage.removeItem(CLICK_STORAGE_KEY);
    setClickRecords([]);
    setChefReport([]);
  }, []);

  return (
    <PageLayout title={t('kitchen.title')} background="bg-base-200/50">
      <div className="space-y-3">
        {/* ── Header Bar ── */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <h1 className="text-lg font-bold text-base-content">{t('kitchen.title')}</h1>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
            {/* Search */}
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder={t('kitchen.searchPlaceholder') || 'Search...'}
              ariaLabel={t('kitchen.searchPlaceholder') || 'Search kitchen tickets'}
              testId="kds-search-input"
              loading={isFiltering}
              className="flex-1 sm:w-48"
            />
            {/* Status filter — tag pills (same pattern as ProductManager/Sale) */}
            <div
              role="group"
              aria-label={t('kitchen.statusFilter') || 'Filter by status'}
              className="flex flex-wrap items-center gap-1.5"
            >
              {[
                { value: 'all', label: t('kitchen.allTickets') || 'All', active: 'tag--primary' },
                { value: 'pending', label: t('kitchen.pending') || 'Pending', active: 'tag--warning' },
                { value: 'preparing', label: t('kitchen.preparing') || 'Preparing', active: 'tag--info' },
                { value: 'ready', label: t('kitchen.ready') || 'Ready', active: 'tag--success' },
                { value: 'delivered', label: t('kitchen.delivered') || 'Delivered', active: 'tag--neutral' },
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setFilter(opt.value)}
                  data-testid={`kds-status-filter-${opt.value}`}
                  aria-pressed={filter === opt.value}
                  className={`tag tag--sm cursor-pointer transition-all ${
                    filter === opt.value ? opt.active : 'tag--ghost hover:tag--primary'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            {/* Chef Report button */}
            <button
              type="button"
              onClick={openChefReport}
              className="btn btn-ghost btn-sm gap-1 text-xs"
              title="Chef action report"
            >
              <span className="ri-clipboard-line ri-14px" />
              <span className="hidden sm:inline">Report</span>
              {ticketClickCount > 0 && (
                <span className="badge badge-xs badge-soft badge-primary">{ticketClickCount}</span>
              )}
            </button>
            {/* Preferences toggle */}
            <button
              type="button"
              onClick={() => setShowPreferences(!showPreferences)}
              className={`btn btn-ghost btn-sm gap-1 text-xs ${showPreferences ? 'btn-active' : ''}`}
              title="Display preferences"
            >
              <span className="ri-equalizer-line ri-14px" />
            </button>
            {/* Sort toggle */}
            <button
              type="button"
              onClick={() => {
                const next = sortOrder === 'newest' ? 'overdue-first' : 'newest';
                setSortOrder(next);
                localStorage.setItem('kds-sort-order', next);
              }}
              className={`btn btn-ghost btn-sm gap-1 text-xs ${sortOrder === 'overdue-first' ? 'btn-active text-error' : ''}`}
              title={sortOrder === 'overdue-first' ? 'Sorting: Overdue first' : 'Sorting: Newest first'}
            >
              <span className={iconClass('lucide:alert-triangle', `w-3.5 h-3.5 ${sortOrder === 'overdue-first' ? 'text-error' : ''}`)} />
              <span className="hidden sm:inline">{sortOrder === 'overdue-first' ? 'Overdue' : 'Newest'}</span>
            </button>
            {/* Chime sound dropdown */}
            <select
              value={chimeVariant}
              onChange={(e) => {
                const v = e.target.value as ChimeVariant;
                setChimeVariant(v);
                localStorage.setItem('kds-chime-variant', v);
              }}
              className="select select-ghost select-xs text-xs max-w-[140px]"
              title="Notification sound"
              aria-label="Notification sound"
            >
              {CHIME_VARIANTS.map(c => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>
            {/* Mute 30min button */}
            <button
              type="button"
              onClick={() => {
                if (mutedUntil && mutedUntil > Date.now()) {
                  setMutedUntil(null);
                  localStorage.removeItem('kds-muted-until');
                } else {
                  const ts = Date.now() + 30 * 60 * 1000;
                  setMutedUntil(ts);
                  localStorage.setItem('kds-muted-until', String(ts));
                }
              }}
              className={`btn btn-ghost btn-sm gap-1 text-xs ${mutedUntil && mutedUntil > Date.now() ? 'btn-active text-error' : ''}`}
              title={mutedUntil && mutedUntil > Date.now() ? `Muted for ${muteRemaining}` : 'Mute notifications for 30 min'}
            >
              <span className={iconClass(mutedUntil && mutedUntil > Date.now() ? 'lucide:bell-off' : 'lucide:bell', 'w-3.5 h-3.5')} />
              <span className="hidden sm:inline">{mutedUntil && mutedUntil > Date.now() ? muteRemaining : 'Mute'}</span>
            </button>
          </div>
        </div>

        {/* ── Product category filter — colored tag pills (same pattern as ProductManager/Sale) ── */}
        {categories.length > 0 && (
          <CategoryFilterPills
            categories={categories}
            selected={selectedCategory}
            onChange={setSelectedCategory}
            allLabel={t('kitchen.allCategories') || 'All categories'}
            ariaLabel={t('kitchen.categoryFilter') || 'Filter by category'}
            testIdPrefix="kds-category-filter"
            allTestId="kds-category-filter-all"
            counts={categoryCounts}
          />
        )}

        {/* ── KDS Preferences Panel ── */}
        {showPreferences && (
          <div className="bg-base-100 border border-base-300 rounded-lg p-3 text-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-base-content flex items-center gap-1.5">
                <span className="ri-equalizer-line ri-14px" />
                Product Display Preferences
              </span>
              <button
                type="button"
                onClick={() => setShowPreferences(false)}
                className="btn btn-ghost btn-xs btn-square"
              >
                <span className="ri-close-line ri-12px" />
              </button>
            </div>
            <p className="text-[10px] text-base-content/50 mb-2">
              Select which order types to display as kitchen tasks:
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                { priority: 1, label: 'Dine-in / Extra', icon: 'lucide:utensils' },
                { priority: 2, label: 'Takeaway / Dated', icon: 'lucide:package' },
                { priority: 3, label: 'Delivery', icon: 'lucide:truck' },
              ].map(({ priority, label, icon }) => (
                <label key={priority} className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-base-200/50 cursor-pointer hover:bg-base-200 transition-colors">
                  <input
                    type="checkbox"
                    checked={preferredPriorities.includes(priority)}
                    onChange={() => {
                      const next = preferredPriorities.includes(priority)
                        ? preferredPriorities.filter(p => p !== priority)
                        : [...preferredPriorities, priority];
                      setPreferredPriorities(next);
                      localStorage.setItem('kds-preferred-priorities', JSON.stringify(next));
                    }}
                    className="checkbox checkbox-primary checkbox-xs"
                  />
                  <span className={iconClass(icon, 'w-3.5 h-3.5 text-base-content/60')} />
                  <span className="text-xs text-base-content">{label}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* ── Ticket Stats Row ── */}
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            title={t('kitchen.activeTickets', 'Active')}
            value={tickets.filter(t => t.status !== 'delivered').length}
            desc={`${tickets.filter(t => isOverdue(t)).length} ${t('kitchen.overdue', 'overdue')}`}
            color="warning"
            loading={isLoading}
            compact
          />
          <StatCard
            title={t('kitchen.completedTickets', 'Completed')}
            value={tickets.filter(t => t.status === 'delivered').length}
            desc={`${tickets.filter(t => t.status === 'ready').length} ${t('kitchen.ready', 'ready')}`}
            color="success"
            loading={isLoading}
            compact
          />
        </div>

        {/* ── Ticket count ── */}
        {filteredTickets.length > 0 && (
          <div className="flex items-center justify-end gap-2 text-[10px] text-base-content/40 -mt-1">
            <span>{filteredTickets.length} / {tickets.length}</span>
            {filteredTickets.filter(t => isOverdue(t)).length > 0 && (
              <span className="badge badge-xs badge-error gap-1 animate-pulse">
                <span className="ri-alert-line w-2.5 h-2.5" />
                {filteredTickets.filter(t => isOverdue(t)).length} overdue
              </span>
            )}
          </div>
        )}

        {/* ── Ticket Grid (compact) ── */}
        {isLoading ? (
          <div className="text-center py-8 text-base-content/50 text-sm">{t('common.loading')}</div>
        ) : filteredTickets.length === 0 ? (
          <div className="text-center py-8 text-base-content/50 text-sm">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No ticket matches the search.')
              : (t('kitchen.noTickets'))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 gap-2">
            {filteredTickets.map(ticket => {
              const overdue = isOverdue(ticket);
              return (
                <button
                  key={ticket.id}
                  type="button"
                  onClick={() => openDetail(ticket)}
                  className={`rounded-lg border-2 p-2.5 text-left cursor-pointer transition-all
                    hover:shadow-md hover:-translate-y-0.5 active:scale-[0.97] ${overdue ? 'bg-error/5' : statusColors[ticket.status] || 'border-base-300 bg-base-100'}
                    ${overdue ? 'shadow-[0_0_12px_rgba(239,68,68,0.15)]' : ''}`}
                  style={overdue ? { borderColor: 'rgba(239, 68, 68, 1)' } : undefined}
                >
                  {/* Ticket header - order type icon + order number + overdue badge */}
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1 min-w-0">
                      <span className={iconClass(ORDER_TYPE_MAP[ticket.priority]?.icon || 'tools-kitchen-2', 'w-3.5 h-3.5 shrink-0 ' + (ORDER_TYPE_MAP[ticket.priority]?.color.split(' ')[0] || 'text-base-content/60'))} />
                      <span className="font-bold text-sm text-base-content truncate">#{ticket.sale_id}</span>
                    </div>
                    {overdue ? (
                      <span className="badge badge-sm badge-error gap-1 shrink-0 ml-1 animate-pulse">
                        <span className="text-[10px]">🔴</span> Overdue
                      </span>
                    ) : (
                      <span className={`${statusBadges[ticket.status] || 'badge badge-soft'} shrink-0 ml-1`}>{ticket.status}</span>
                    )}
                  </div>
                  {/* Order type + elapsed time row */}
                  <div className="flex items-center justify-between gap-1 mb-1">
                    {ORDER_TYPE_MAP[ticket.priority] && (
                      <span className={`tag tag--sm ${ORDER_TYPE_MAP[ticket.priority].color.includes('primary') ? 'tag--primary' : ORDER_TYPE_MAP[ticket.priority].color.includes('warning') ? 'tag--warning' : 'tag--success'}`}>
                        {ORDER_TYPE_MAP[ticket.priority].label}
                      </span>
                    )}
                    <span className={`text-[9px] flex items-center gap-1 ${overdue ? 'text-error font-semibold' : 'text-base-content/40'}`}>
                      <span className="ri-time-line ri-12px" />
                      {timeAgo(ticket.created_at)}
                    </span>
                  </div>
                  {/* Notes (truncated) */}
                  {ticket.notes && (
                    <p className="text-[10px] text-base-content/60 line-clamp-1 mb-1.5">{ticket.notes}</p>
                  )}
                  {/* Prep time + status row */}
                  <div className="flex items-center justify-between mt-auto mb-1">
                    {ticket.prepare_time_minutes > 0 && (
                      <span className={`flex items-center gap-1 text-[9px] ${overdue ? 'text-error' : 'text-base-content/50'}`}>
                        <span className="ri-play-circle-line ri-12px" />
                        {ticket.prepare_time_minutes}min
                        <span className="text-base-content/30">Est.</span>
                      </span>
                    )}
                    {overdue && (
                      <span className="text-[9px] text-error font-bold">
                        +{Math.floor((Date.now() - new Date(ticket.created_at.replace(' ', 'T')).getTime()) / 60000) - ticket.prepare_time_minutes}min overdue
                      </span>
                    )}
                  </div>
                  {/* Quick status badge */}
                  <div className="flex gap-1">
                    {ticket.status === 'pending' && !overdue && (
                      <span className="tag tag--sm tag--warning">Awaiting</span>
                    )}
                    {ticket.status === 'preparing' && !overdue && (
                      <span className="tag tag--sm tag--info">In Progress</span>
                    )}
                    {ticket.status === 'ready' && (
                      <span className="tag tag--sm tag--success">Ready ✓</span>
                    )}
                  </div>
                  {/* ── Time-elapsed progress bar (green→yellow→red) ── */}
                  {ticket.prepare_time_minutes > 0 && ticket.status !== 'delivered' && ticket.status !== 'ready' && (() => {
                    const elapsed = Date.now() - new Date(ticket.created_at.replace(' ', 'T')).getTime();
                    const estimate = ticket.prepare_time_minutes * 60 * 1000;
                    const pct = Math.min(100, Math.round((elapsed / estimate) * 100));
                    const barColor = pct < 50 ? 'bg-success' : pct < 90 ? 'bg-warning' : 'bg-error';
                    return (
                      <div className="mt-1.5 w-full">
                        <div className="flex items-center justify-between text-[8px] text-base-content/30 mb-0.5">
                          <span>{pct}%</span>
                          <span>{Math.round(elapsed / 60000)}m / {ticket.prepare_time_minutes}m</span>
                        </div>
                        <div className="w-full h-1 rounded-full bg-base-300/50 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-1000 ${barColor} ${overdue ? 'animate-pulse' : ''}`}
                            style={{ width: `${pct}%`, minWidth: pct > 0 ? '4px' : '0px' }}
                          />
                        </div>
                      </div>
                    );
                  })()}
                </button>
              );
            })}
          </div>
        )}

        {/* ── Ticket Detail Modal ── */}
        <Modal
          isOpen={!!selectedTicket}
          onClose={closeDetail}
          size="lg"
          scroll
          headerIcon={selectedTicket && ORDER_TYPE_MAP[selectedTicket.priority] ? (
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${ORDER_TYPE_MAP[selectedTicket.priority].color}`}>
              <span className={iconClass(ORDER_TYPE_MAP[selectedTicket.priority].icon, 'w-4 h-4')} />
            </div>
          ) : (
            <span className="ri-restaurant-2-line ri-20px text-primary" />
          )}
          title={selectedTicket ? `Order #${selectedTicket.sale_id}` : ''}
          subtitle={selectedTicket
            ? `${timeAgo(selectedTicket.created_at)} · ${new Date(selectedTicket.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}${selectedTicket.prepare_time_minutes > 0 ? ` · Est. ${selectedTicket.prepare_time_minutes}min` : ''}`
            : ''}
          footer={selectedTicket ? (
            <div className="flex gap-2 justify-end w-full">
              {selectedTicket.status === 'pending' && (
                <button
                  onClick={() => { updateStatus(selectedTicket, 'preparing'); closeDetail(); }}
                  className="btn btn-info btn-sm gap-1"
                >
                  <span className="ri-restaurant-2-line ri-16px" />
                  {t('kitchen.startPreparing')}
                </button>
              )}
              {selectedTicket.status === 'preparing' && (
                <button
                  onClick={() => { updateStatus(selectedTicket, 'ready'); closeDetail(); }}
                  className="btn btn-success btn-sm gap-1"
                >
                  <span className="ri-checkbox-circle-line ri-16px" />
                  {t('kitchen.markReady')}
                </button>
              )}
              {selectedTicket.status === 'ready' && (
                <button
                  onClick={() => { updateStatus(selectedTicket, 'delivered'); closeDetail(); }}
                  className="btn btn-ghost btn-sm gap-1"
                >
                  <span className="ri-checkbox-circle-line ri-16px" />
                  {t('kitchen.deliver')}
                </button>
              )}
              <button onClick={closeDetail} className="btn btn-ghost btn-sm">{t('common.close')}</button>
            </div>
          ) : undefined}
        >
          {selectedTicket && (
            <>
              {/* Status badge row */}
              <div className="flex items-center gap-2 mb-1">
                <span className={statusBadges[selectedTicket.status] || 'badge badge-sm'}>{selectedTicket.status}</span>
                {selectedTicket.completed_at && (
                  <span className="text-xs text-success">Completed {timeAgo(selectedTicket.completed_at)}</span>
                )}
              </div>

              <div className="space-y-3">
                  {/* Order flags: table, delivery, total */}
                  <div className="flex flex-wrap items-center gap-2">
                    {saleDetail?.table_number && (
                      <span className="tag tag--sm tag--info">
                        <span className="ri-login-box-line ri-14px" />
                        Table {saleDetail.table_number}
                      </span>
                    )}
                    {saleDetail?.delivery_address && (
                      <span className="tag tag--sm tag--warning">
                        <span className="ri-map-pin-2-line ri-14px" />
                        {saleDetail.delivery_address}
                      </span>
                    )}
                    {saleDetail?.total_amount !== undefined && (
                      <span className="tag tag--sm tag--primary">
                        <span className="ri-money-dollar-circle-line ri-14px" />
                        ${saleDetail.total_amount.toFixed(2)}
                      </span>
                    )}
                    {saleItems.length > 0 && (
                      <span className="tag tag--sm">
                        <span className="ri-shopping-cart-line ri-14px" />
                        {saleItems.length} item{saleItems.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>

                  {selectedTicket.notes && (
                    <div className="bg-base-200/50 rounded-lg p-2.5 text-xs text-base-content/70 flex items-start gap-2">
                      <span className="ri-sticky-note-line ri-14px text-base-content/40 mt-0.5 shrink-0" />
                      {selectedTicket.notes}
                    </div>
                  )}

                  {/* Sale Items */}
                  <div>
                    <h4 className="text-xs font-semibold text-base-content/70 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <span className="ri-shopping-cart-line ri-14px" />
                      Items
                    </h4>
                    {isLoadingItems ? (
                      <div className="flex items-center gap-2 text-xs text-base-content/50 py-3">
                        <span className="loading loading-spinner loading-xs" />
                        Loading items...
                      </div>
                    ) : saleItems.length === 0 ? (
                      <p className="text-xs text-base-content/40 italic py-3">No items recorded for this order.</p>
                    ) : (
                      <div className="space-y-1">
                        {saleItems.map(item => (
                          <div
                            key={item.id}
                            className="flex items-center justify-between py-1.5 px-2 rounded-lg text-xs"
                          >
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold shrink-0 bg-base-300 text-base-content/70">
                                {item.quantity}
                              </span>
                              <span className="font-medium text-base-content truncate">{item.product_name}</span>
                            </div>
                            <span className="text-base-content/60 shrink-0 ml-2">{formatPrice(item.price * item.quantity)}</span>
                          </div>
                        ))}
                        {/* Total */}
                        <div className="flex items-center justify-between py-2 px-2 mt-1 border-t border-base-200/50 text-xs font-bold text-base-content">
                          <span>Total</span>
                          <span>{formatPrice(saleItems.reduce((sum, i) => sum + i.price * i.quantity, 0))}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Chef action records for this ticket */}
                  {chefReport.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-base-content/70 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <span className="ri-history-line ri-14px" />
                        Actions
                      </h4>
                      <div className="space-y-1">
                        {chefReport.slice(-8).map((rec, i) => (
                          <div key={i} className="flex items-center gap-2 text-[10px] text-base-content/50">
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              rec.action === 'opened' ? 'bg-info' :
                              rec.action === 'started' ? 'bg-warning' :
                              rec.action === 'completed' ? 'bg-success' : 'bg-base-300'
                            }`} />
                            <span className="capitalize">{rec.action}</span>
                            <span className="text-base-content/30">{new Date(rec.timestamp).toLocaleTimeString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* ── Prep Steps checklist (from selectable preparation notes) ── */}
                {activePrepSteps.length > 0 && (
                  <div className="bg-info/5 border border-info/20 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-xs font-semibold text-base-content/80 uppercase tracking-wider flex items-center gap-1.5">
                        <span className="ri-check-double-line ri-14px text-info" />
                        {t('kitchen.prepSteps') || 'Prep Steps'}
                        {activePrepNote && (
                          <span className="tag tag--sm tag--info font-normal normal-case">{activePrepNote.name}</span>
                        )}
                      </h4>
                      <span className="text-[10px] text-base-content/40 tabular-nums">
                        {Object.values(checkedSteps).filter(Boolean).length}/{activePrepSteps.length} done
                      </span>
                    </div>
                    <ol className="space-y-1">
                      {activePrepSteps.map((step, i) => {
                        const key = `${activePrepNote?.id ?? 'note'}-${i}`;
                        const done = !!checkedSteps[key];
                        return (
                          <li key={key}>
                            <button
                              type="button"
                              onClick={() => setCheckedSteps(prev => ({ ...prev, [key]: !prev[key] }))}
                              className={`w-full flex items-start gap-2 rounded-md px-2 py-1.5 text-left transition-all ${
                                done ? 'bg-success/10 text-base-content/40' : 'bg-base-200/40 hover:bg-base-200/80'
                              }`}
                            >
                              <span
                                className={`mt-0.5 w-4 h-4 rounded border-2 shrink-0 flex items-center justify-center transition-all ${
                                  done ? 'bg-success border-success text-success-content' : 'border-base-content/30'
                                }`}
                              >
                                {done && <span className="ri-check-line ri-12px" />}
                              </span>
                              <span className="min-w-0">
                                <span className={`block text-xs font-medium ${done ? 'line-through' : 'text-base-content'}`}>
                                  {i + 1}. {step.title}
                                </span>
                                {step.details && (
                                  <span className={`block text-[10px] leading-snug ${done ? 'text-base-content/30' : 'text-base-content/50'}`}>
                                    {step.details}
                                  </span>
                                )}
                              </span>
                            </button>
                          </li>
                        );
                      })}
                    </ol>
                  </div>
                )}

                {/* ── Quick Notes picker — selectable notes + add-new ── */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-semibold text-base-content/70 uppercase tracking-wider flex items-center gap-1.5">
                      <span className="ri-cursor-line ri-14px text-primary" />
                      {t('kitchen.quickNotes') || 'Quick Notes'}
                    </h4>
                    <button
                      type="button"
                      onClick={() => setShowQuickAddNote(s => !s)}
                      className="btn btn-ghost btn-xs gap-1 text-primary"
                    >
                      <span className="ri-add-line ri-14px" />
                      {t('kitchen.addNote') || 'Add note'}
                    </button>
                  </div>

                  {showQuickAddNote && (
                    <div className="bg-base-200/40 rounded-lg p-2.5 space-y-2 mb-2 border border-base-300/40">
                      <input
                        type="text"
                        value={quickNoteName}
                        onChange={e => setQuickNoteName(e.target.value)}
                        placeholder={t('notes.name') || 'Note name'}
                        className="input w-full text-xs"
                      />
                      <input
                        type="text"
                        value={quickNoteBody}
                        onChange={e => setQuickNoteBody(e.target.value)}
                        placeholder={t('sale.orderNotesPlaceholder') || 'Note text...'}
                        className="input w-full text-xs"
                      />
                      <div className="flex gap-2 justify-end">
                        <button
                          type="button"
                          onClick={() => setShowQuickAddNote(false)}
                          className="btn btn-ghost btn-xs"
                        >
                          {t('common.cancel')}
                        </button>
                        <button
                          type="button"
                          onClick={handleQuickAddNote}
                          disabled={!quickNoteName.trim()}
                          className="btn btn-primary btn-xs gap-1"
                        >
                          <span className="ri-check-line ri-12px" />
                          {t('common.save')}
                        </button>
                      </div>
                    </div>
                  )}

                  {selectableNotes.length === 0 ? (
                    <p className="text-[11px] text-base-content/40 italic py-1">
                      {t('notes.noTemplates') || 'No quick notes yet — mark notes as selectable in Notes.'}
                    </p>
                  ) : (
                    <div className="flex flex-wrap gap-1.5">
                      {selectableNotes.map(note => {
                        const isPrep = note.category === 'preparation' && parseNoteSteps(note.steps).length > 0;
                        return (
                          <button
                            key={note.id}
                            type="button"
                            onClick={() => {
                              setActivePrepNoteId(isPrep ? note.id : null);
                              attachNoteToTicket(note);
                            }}
                            className={`tag tag--sm cursor-pointer transition-all ${
                              activePrepNoteId === note.id ? 'tag--primary' : 'tag--ghost hover:tag--primary'
                            }`}
                            title={isPrep ? 'Shows prep steps on this order' : note.template_body}
                          >
                            {isPrep && <span className="ri-check-double-line ri-12px" />}
                            {note.name}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </>
            )}
        </Modal>

        {/* ── Chef Report Modal ── */}
        <dialog ref={reportDialogRef} className="modal">
          <div className="modal-box max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-base text-base-content flex items-center gap-2">
                <span className="ri-clipboard-line ri-16px text-primary" />
                Chef Action Report
              </h3>
              <button
                type="button"
                onClick={() => { reportDialogRef.current?.close(); }}
                className="btn btn-ghost btn-sm btn-square"
              >
                <span className="ri-close-line ri-16px" />
              </button>
            </div>
            {clickRecords.length === 0 ? (
              <p className="text-sm text-base-content/50 italic py-4 text-center">No actions recorded yet.</p>
            ) : (
              <div className="space-y-1 max-h-80 overflow-y-auto">
                {[...clickRecords].reverse().slice(0, 100).map((rec, i) => (
                  <div key={i} className="flex items-center gap-2 py-1.5 px-2 rounded-lg bg-base-200/30 text-xs">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${
                      rec.action === 'opened' ? 'bg-info' :
                      rec.action === 'started' ? 'bg-warning' :
                      rec.action === 'completed' ? 'bg-success' : 'bg-base-400'
                    }`} />
                    <span className="font-medium text-base-content/80 capitalize">{rec.action}</span>
                    <span className="text-base-content/40">Order #{rec.saleId}</span>
                    <span className="text-base-content/30 ml-auto">{new Date(rec.timestamp).toLocaleTimeString()}</span>
                  </div>
                ))}
              </div>
            )}
            <div className="modal-action">
              {clickRecords.length > 0 && (
                <button
                  type="button"
                  onClick={clearClickHistory}
                  className="btn btn-ghost btn-sm text-error gap-1"
                >
                  <span className="ri-delete-bin-line ri-14px" />
                  Clear history
                </button>
              )}
              <button
                type="button"
                onClick={() => { reportDialogRef.current?.close(); }}
                className="btn btn-primary btn-sm"
              >
                Close
              </button>
            </div>
          </div>
          <form method="dialog" className="modal-backdrop">
            <button type="button" onClick={() => { reportDialogRef.current?.close(); }}>close</button>
          </form>
        </dialog>
      </div>
    </PageLayout>
  );
}
