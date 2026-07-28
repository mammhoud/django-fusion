import { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import { KitchenTicket, Sale } from '../types';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

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
  1: { icon: 'sofa', label: 'Dine-in / Extra', color: 'text-primary bg-primary/10' },
  2: { icon: 'shopping-bag', label: 'Takeaway / Dated', color: 'text-warning bg-warning/10' },
  3: { icon: 'truck-delivery', label: 'Delivery', color: 'text-success bg-success/10' },
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
  const [tickets, setTickets] = useState<KitchenTicket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('pending');

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
  // Preference: which order types to show in the KDS (by priority: 1=dine-in, 2=takeaway, 3=delivery)
  const [preferredPriorities, setPreferredPriorities] = useState<number[]>(() => {
    try { return JSON.parse(localStorage.getItem('kds-preferred-priorities') || '[1,2,3]'); }
    catch { return [1, 2, 3]; }
  });
  const detailDialogRef = useRef<HTMLDialogElement>(null);
  const reportDialogRef = useRef<HTMLDialogElement>(null);

  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  useEffect(() => {
    loadTickets({ quiet: false });
    const interval = setInterval(() => loadTickets({ quiet: true }), 10000);
    return () => clearInterval(interval);
  }, [filter]);

  const loadTickets = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<KitchenTicket[]>('get_kitchen_tickets', { status: filter === 'all' ? null : filter });
      setTickets(data);
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
      setTimeout(() => detailDialogRef.current?.showModal(), 50);
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
    detailDialogRef.current?.close();
  }, [selectedTicket]);

  // Filter — text search + order-type preference (via priority: 1=dine-in, 2=takeaway, 3=delivery)
  const q = debouncedSearch.trim().toLowerCase();
  const showAllPriorities = preferredPriorities.length === 0;
  const filteredTickets = tickets.filter(t => {
    if (q && !String(t.sale_id || '').includes(q) && !(t.notes || '').toLowerCase().includes(q)) return false;
    return showAllPriorities || preferredPriorities.includes(t.priority);
  });

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
            <div className="relative flex-1 sm:w-48">
              <span className="icon-[tabler--search] absolute left-2.5 top-1/2 -translate-y-1/2 text-base-content/40 w-3.5 h-3.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('kitchen.searchPlaceholder') || 'Search...'}
                aria-label={t('kitchen.searchPlaceholder') || 'Search kitchen tickets'}
                className="input input-bordered w-full pl-8 h-9 text-xs"
              />
              {isFiltering ? (
                <div className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              ) : search ? (
                <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content">
                  <span className="icon-[tabler--x] w-3.5 h-3.5" />
                </button>
              ) : null}
            </div>
            {/* Status filter */}
            <select
              value={filter}
              onChange={e => setFilter(e.target.value)}
              aria-label={t('kitchen.statusFilter') || 'Filter by status'}
              className="select select-bordered w-full sm:w-36 h-9 text-xs"
            >
              <option value="all">{t('kitchen.allTickets')}</option>
              <option value="pending">{t('kitchen.pending')}</option>
              <option value="preparing">{t('kitchen.preparing')}</option>
              <option value="ready">{t('kitchen.ready')}</option>
              <option value="delivered">{t('kitchen.delivered')}</option>
            </select>
            {/* Chef Report button */}
            <button
              type="button"
              onClick={openChefReport}
              className="btn btn-ghost btn-sm gap-1 text-xs"
              title="Chef action report"
            >
              <span className="icon-[tabler--clipboard-list] w-3.5 h-3.5" />
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
              <span className="icon-[tabler--adjustments] w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* ── KDS Preferences Panel ── */}
        {showPreferences && (
          <div className="bg-base-100 border border-base-300 rounded-lg p-3 text-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-base-content flex items-center gap-1.5">
                <span className="icon-[tabler--adjustments] w-3.5 h-3.5" />
                Product Display Preferences
              </span>
              <button
                type="button"
                onClick={() => setShowPreferences(false)}
                className="btn btn-ghost btn-xs btn-square"
              >
                <span className="icon-[tabler--x] w-3 h-3" />
              </button>
            </div>
            <p className="text-[10px] text-base-content/50 mb-2">
              Select which order types to display as kitchen tasks:
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                { priority: 1, label: 'Dine-in / Extra', icon: 'tabler--sofa' },
                { priority: 2, label: 'Takeaway / Dated', icon: 'tabler--shopping-bag' },
                { priority: 3, label: 'Delivery', icon: 'tabler--truck-delivery' },
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
                  <span className={`icon-[${icon}] w-3.5 h-3.5 text-base-content/60`} />
                  <span className="text-xs text-base-content">{label}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* ── Ticket count ── */}
        {filteredTickets.length > 0 && (
          <div className="text-[10px] text-base-content/40 text-right -mt-1">
            {filteredTickets.length} / {tickets.length}
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
            {filteredTickets.map(ticket => (
              <motion.button
                key={ticket.id}
                type="button"
                onClick={() => openDetail(ticket)}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.97 }}
                className={`rounded-lg border-2 p-2.5 text-left cursor-pointer transition-all
                  hover:shadow-md ${statusColors[ticket.status] || 'border-base-300 bg-base-100'}`}
              >
                {/* Ticket header - order type icon + order number + status */}
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1 min-w-0">
                    <span className={`icon-[tabler--${ORDER_TYPE_MAP[ticket.priority]?.icon || 'tools-kitchen-2'}] w-3.5 h-3.5 shrink-0 ${ORDER_TYPE_MAP[ticket.priority]?.color.split(' ')[0] || 'text-base-content/60'}`} />
                    <span className="font-bold text-sm text-base-content truncate">#{ticket.sale_id}</span>
                  </div>
                  <span className={`${statusBadges[ticket.status] || 'badge badge-soft'} shrink-0 ml-1`}>{ticket.status}</span>
                </div>
                {/* Order type + elapsed time row */}
                <div className="flex items-center justify-between gap-1 mb-1">
                  {ORDER_TYPE_MAP[ticket.priority] && (
                    <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${ORDER_TYPE_MAP[ticket.priority].color}`}>
                      {ORDER_TYPE_MAP[ticket.priority].label}
                    </span>
                  )}
                  <span className="text-[9px] text-base-content/40 flex items-center gap-1">
                    <span className="icon-[tabler--clock] w-3 h-3" />
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
                    <span className="flex items-center gap-1 text-[9px] text-base-content/50">
                      <span className="icon-[tabler--clock-play] w-3 h-3" />
                      {ticket.prepare_time_minutes}min
                      <span className="text-base-content/30">Est.</span>
                    </span>
                  )}
                </div>
                {/* Quick status badge */}
                <div className="flex gap-1">
                  {ticket.status === 'pending' && (
                    <span className="text-[9px] px-2 py-0.5 rounded bg-warning/20 text-warning font-medium">Awaiting</span>
                  )}
                  {ticket.status === 'preparing' && (
                    <span className="text-[9px] px-2 py-0.5 rounded bg-info/20 text-info font-medium">In Progress</span>
                  )}
                  {ticket.status === 'ready' && (
                    <span className="text-[9px] px-2 py-0.5 rounded bg-success/20 text-success font-medium">Ready ✓</span>
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        )}

        {/* ── Ticket Detail Modal ── */}
        <dialog ref={detailDialogRef} className="modal">
          <div className="modal-box max-w-lg p-0 overflow-hidden">
            {selectedTicket && (
              <>
                {/* Modal header with order-type-specific icon */}
                <div className="sticky top-0 z-10 bg-base-100 border-b border-base-200 px-5 py-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {ORDER_TYPE_MAP[selectedTicket.priority] ? (
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${ORDER_TYPE_MAP[selectedTicket.priority].color}`}>
                        <span className={`icon-[tabler--${ORDER_TYPE_MAP[selectedTicket.priority].icon}] w-4 h-4`} />
                      </div>
                    ) : (
                      <span className="icon-[tabler--tools-kitchen-2] w-5 h-5 text-primary" />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg text-base-content">
                          Order #{selectedTicket.sale_id}
                        </h3>
                        <span className={statusBadges[selectedTicket.status] || 'badge badge-sm'}>{selectedTicket.status}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-base-content/40">
                        <span>{timeAgo(selectedTicket.created_at)}</span>
                        <span>·</span>
                        <span>{new Date(selectedTicket.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        {selectedTicket.prepare_time_minutes > 0 && (
                          <>
                            <span>·</span>
                            <span className="flex items-center gap-0.5 text-primary/70">
                              <span className="icon-[tabler--clock-play] w-3 h-3" />
                              Est. {selectedTicket.prepare_time_minutes}min
                            </span>
                          </>
                        )}
                        {selectedTicket.completed_at && (
                          <>
                            <span>·</span>
                            <span className="text-success">Completed {timeAgo(selectedTicket.completed_at)}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={closeDetail}
                    className="btn btn-ghost btn-sm btn-square"
                    aria-label="Close"
                  >
                    <span className="icon-[tabler--x] w-4 h-4" />
                  </button>
                </div>

                <div className="px-5 py-3 space-y-3">
                  {/* Order flags: table, delivery, total */}
                  <div className="flex flex-wrap items-center gap-2">
                    {saleDetail?.table_number && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                        <span className="icon-[tabler--door-enter] w-3.5 h-3.5" />
                        Table {saleDetail.table_number}
                      </span>
                    )}
                    {saleDetail?.delivery_address && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400">
                        <span className="icon-[tabler--map-pin] w-3.5 h-3.5" />
                        {saleDetail.delivery_address}
                      </span>
                    )}
                    {saleDetail?.total_amount !== undefined && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                        <span className="icon-[tabler--currency-dollar] w-3.5 h-3.5" />
                        ${saleDetail.total_amount.toFixed(2)}
                      </span>
                    )}
                    {saleItems.length > 0 && (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-base-200/50 text-base-content/60">
                        <span className="icon-[tabler--shopping-cart] w-3.5 h-3.5" />
                        {saleItems.length} item{saleItems.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>

                  {selectedTicket.notes && (
                    <div className="bg-base-200/50 rounded-lg p-2.5 text-xs text-base-content/70 flex items-start gap-2">
                      <span className="icon-[tabler--note] w-3.5 h-3.5 text-base-content/40 mt-0.5 shrink-0" />
                      {selectedTicket.notes}
                    </div>
                  )}

                  {/* Sale Items */}
                  <div>
                    <h4 className="text-xs font-semibold text-base-content/70 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <span className="icon-[tabler--shopping-cart] w-3.5 h-3.5" />
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
                            className="flex items-center justify-between py-1.5 px-2 rounded-lg bg-base-200/30 text-xs"
                          >
                            <div className="flex items-center gap-2 min-w-0">
                              <span className="w-5 h-5 rounded bg-primary/10 text-primary flex items-center justify-center text-[10px] font-bold shrink-0">
                                {item.quantity}
                              </span>
                              <span className="font-medium text-base-content truncate">{item.product_name}</span>
                            </div>
                            <span className="text-base-content/60 shrink-0 ml-2">${(item.price * item.quantity).toFixed(2)}</span>
                          </div>
                        ))}
                        {/* Total */}
                        <div className="flex items-center justify-between py-2 px-2 mt-1 border-t border-base-200/50 text-xs font-bold text-base-content">
                          <span>Total</span>
                          <span>${saleItems.reduce((sum, i) => sum + i.price * i.quantity, 0).toFixed(2)}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Chef action records for this ticket */}
                  {chefReport.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-base-content/70 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <span className="icon-[tabler--history] w-3.5 h-3.5" />
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

                {/* Action footer */}
                <div className="border-t border-base-200 px-5 py-3 flex gap-2 justify-end">
                  {selectedTicket.status === 'pending' && (
                    <button
                      onClick={() => { updateStatus(selectedTicket, 'preparing'); closeDetail(); }}
                      className="btn btn-info btn-sm gap-1"
                    >
                      <span className="icon-[tabler--chef-hat] w-4 h-4" />
                      Start Preparing
                    </button>
                  )}
                  {selectedTicket.status === 'preparing' && (
                    <button
                      onClick={() => { updateStatus(selectedTicket, 'ready'); closeDetail(); }}
                      className="btn btn-success btn-sm gap-1"
                    >
                      <span className="icon-[tabler--circle-check] w-4 h-4" />
                      Mark Ready
                    </button>
                  )}
                  {selectedTicket.status === 'ready' && (
                    <button
                      onClick={() => { updateStatus(selectedTicket, 'delivered'); closeDetail(); }}
                      className="btn btn-ghost btn-sm gap-1"
                    >
                      <span className="icon-[tabler--circle-check] w-4 h-4" />
                      Deliver
                    </button>
                  )}
                  <button onClick={closeDetail} className="btn btn-ghost btn-sm">Close</button>
                </div>
              </>
            )}
          </div>
          <form method="dialog" className="modal-backdrop">
            <button type="button" onClick={closeDetail}>close</button>
          </form>
        </dialog>

        {/* ── Chef Report Modal ── */}
        <dialog ref={reportDialogRef} className="modal">
          <div className="modal-box max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-base text-base-content flex items-center gap-2">
                <span className="icon-[tabler--clipboard-list] w-4 h-4 text-primary" />
                Chef Action Report
              </h3>
              <button
                type="button"
                onClick={() => { reportDialogRef.current?.close(); }}
                className="btn btn-ghost btn-sm btn-square"
              >
                <span className="icon-[tabler--x] w-4 h-4" />
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
                  <span className="icon-[tabler--trash] w-3.5 h-3.5" />
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
