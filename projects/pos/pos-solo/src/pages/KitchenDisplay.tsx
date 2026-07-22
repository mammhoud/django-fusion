import { useState } from 'react';
import { motion } from 'framer-motion';
import { MdRestaurant, MdCheckCircle, MdAccessTime, MdSearch, MdClose } from 'react-icons/md';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import { useGetKitchenTicketsQuery, useUpdateKitchenTicketMutation } from '../store/api/endpoints/kitchen';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

export default function KitchenDisplay() {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<string>('pending');

  // AJAX-style debounced text search — searches across ticket id / sale_id / notes.
  // The status-filter dropdown stays instant (a select change is deliberate, so
  // no debounce is needed).
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  const { data: tickets = [], isLoading } = useGetKitchenTicketsQuery(
    { status: filter === 'all' ? undefined : filter },
    { pollingInterval: 10000 }
  );
  const [updateKitchenTicket] = useUpdateKitchenTicketMutation();

  const updateStatus = async (id: number, status: string) => {
    try {
      await updateKitchenTicket({ id, data: { status } }).unwrap();
    } catch (error) {
      console.error('Error updating ticket:', error);
    }
  };

  // Filter + sort (debounced search; status filter already applied server-side)
  const q = debouncedSearch.trim().toLowerCase();
  const filteredTickets = q
    ? tickets.filter(t =>
        String(t.sale_id || '').includes(q) ||
        (t.notes || '').toLowerCase().includes(q)
      )
    : tickets;

  const statusColors: Record<string, string> = {
    pending: 'border-amber-400 bg-amber-50 dark:bg-amber-900/20',
    preparing: 'border-blue-400 bg-blue-50 dark:bg-blue-900/20',
    ready: 'border-green-400 bg-green-50 dark:bg-green-900/20',
    delivered: 'border-slate-400 bg-slate-50 dark:bg-slate-800/30',
  };

  return (
    <PageLayout title={t('kitchen.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('kitchen.title')}</h1>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <MdSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('kitchen.searchPlaceholder') || 'Search by ticket or notes...'}
                aria-label={t('kitchen.searchPlaceholder') || 'Search kitchen tickets'}
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
              value={filter}
              onChange={e => setFilter(e.target.value)}
              aria-label={t('kitchen.statusFilter') || 'Filter by status'}
              className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white"
            >
              <option value="all">{t('kitchen.allTickets')}</option>
              <option value="pending">{t('kitchen.pending')}</option>
              <option value="preparing">{t('kitchen.preparing')}</option>
              <option value="ready">{t('kitchen.ready')}</option>
              <option value="delivered">{t('kitchen.delivered')}</option>
            </select>
          </div>
        </div>
        {filteredTickets.length > 0 && (
          <div className="text-xs text-slate-500 dark:text-gray-400 text-right -mt-2">
            {filteredTickets.length} / {tickets.length}
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : filteredTickets.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No ticket matches the search.')
              : (t('kitchen.noTickets'))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredTickets.map(ticket => (
              <motion.div
                key={ticket.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`rounded-xl border-2 p-4 ${statusColors[ticket.status] || 'border-slate-200 bg-white dark:bg-slate-800'}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <MdRestaurant className="text-slate-600 dark:text-slate-300" />
                    <span className="font-bold text-slate-900 dark:text-white">{t('kitchen.ticket')} #{ticket.sale_id}</span>
                  </div>
                  <span className="text-xs font-medium uppercase tracking-wider text-slate-500">{ticket.status}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-slate-500 dark:text-gray-400 mb-4">
                  <MdAccessTime />
                  <span>{new Date(ticket.created_at).toLocaleTimeString()}</span>
                </div>
                {ticket.notes && <p className="text-sm text-slate-600 dark:text-gray-300 mb-3">{ticket.notes}</p>}
                <div className="flex gap-2">
                  {ticket.status === 'pending' && (
                    <button onClick={() => updateStatus(ticket.id, 'preparing')} className="flex-1 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm">{t('kitchen.startPreparing')}</button>
                  )}
                  {ticket.status === 'preparing' && (
                    <button onClick={() => updateStatus(ticket.id, 'ready')} className="flex-1 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm">{t('kitchen.markReady')}</button>
                  )}
                  {ticket.status === 'ready' && (
                    <button onClick={() => updateStatus(ticket.id, 'delivered')} className="flex-1 py-2 bg-slate-500 text-white rounded-lg hover:bg-slate-600 text-sm flex items-center justify-center gap-1"><MdCheckCircle /> {t('kitchen.deliver')}</button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
