/**
 * SupportChat page
 * ================
 * Full-page support and customer service view.
 * Embeds the ChatSupport widget in an expanded (always-open) layout,
 * alongside a ticket history panel that queries the Sanic sidecar.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import PageLayout from '../components/PageLayout';
import ChatSupport from '../components/ChatSupport';
import sidecar from '../api/sidecar';
import tickets from '../api/tickets';
import type { SupportTicket } from '../api/tickets';

const STATUS_COLOURS: Record<string, string> = {
  open:        'bg-amber-100 text-amber-700',
  in_progress: 'bg-blue-100 text-blue-700',
  resolved:    'bg-teal-100 text-teal-700',
  closed:      'bg-slate-100 text-slate-500',
};

export default function SupportChat() {
  const [ticketList, setTicketList]   = useState<SupportTicket[]>(() => []);
  const [loadingTickets, setLoading]  = useState(() => false);
  const [sidecarOk, setSidecarOk]     = useState<boolean | null>(() => null);
  const [selectedTicket, setSelected] = useState<SupportTicket | null>(() => null);

  const fetchTickets = async () => {
    setLoading(true);
    const { data, ok } = await tickets.list();
    if (ok && data) {
      setTicketList(data);
      setSidecarOk(true);
    } else {
      setSidecarOk(false);
    }
    setLoading(false);
  };

  useEffect(() => {
    sidecar.healthCheck().then(setSidecarOk);
    fetchTickets();
  }, []);

  return (
    <PageLayout
      title={
        <span className="flex items-center gap-2">
          <span className="icon-[tabler--headset] w-5 h-5 text-teal-500" />
          Support &amp; Customer Service
        </span>
      }
    >
      {/* Sidecar status bar */}
      <div className={`flex items-center gap-2 px-4 py-2 rounded-xl mb-6 text-sm font-medium w-fit ${
        sidecarOk === true
          ? 'bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400'
          : sidecarOk === false
          ? 'bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
          : 'bg-slate-100 text-slate-500'
      }`}>
        <span className={`icon-[tabler--circle] w-3 h-3 ${
          sidecarOk === true ? 'text-teal-500' : sidecarOk === false ? 'text-rose-500' : 'text-base-content/40'
        }`} />
        {sidecarOk === true
          ? 'Sanic sidecar connected — real-time chat active'
          : sidecarOk === false
          ? 'Sanic sidecar offline — chat will queue messages locally'
          : 'Checking sidecar status…'}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

        {/* LEFT — Chat panel (always open, no trigger button) */}
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
            <span className="icon-[tabler--headset] w-4 h-4" /> Live Chat
          </h2>
          <div className="relative" style={{ height: 560 }}>
            <ChatSupport showTrigger={false} defaultOpen={true} room="support-page" />
          </div>
        </div>

        {/* RIGHT — Ticket history */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <span className="icon-[tabler--inbox] w-4 h-4" /> Support Tickets
            </h2>
            <motion.button
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              onClick={fetchTickets}
              disabled={loadingTickets}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-medium hover:bg-base-300/80 disabled:opacity-50"
            >
              <span className={`icon-[tabler--refresh] w-3.5 h-3.5 ${loadingTickets ? 'animate-spin' : ''}`} />
              Refresh
            </motion.button>
          </div>

          {sidecarOk === false ? (
            <div className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-6 text-center text-slate-400 text-sm">
              <span className="icon-[tabler--headset] w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="font-medium mb-1">Sidecar not running</p>
              <p className="text-xs">Start the sidecar to view ticket history.</p>
            </div>
          ) : ticketList.length === 0 ? (
            <div className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-6 text-center text-slate-400 text-sm">
              <span className="icon-[tabler--inbox] w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>{loadingTickets ? 'Loading tickets…' : 'No support tickets yet.'}</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
              {ticketList.map(ticket => (
                <motion.div
                  key={ticket.id}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => setSelected(s => s?.id === ticket.id ? null : ticket)}
                  className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 cursor-pointer border border-transparent hover:border-teal-300 transition-all"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm truncate">
                        {ticket.subject}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">{ticket.name} &bull; {ticket.email}</p>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 uppercase tracking-wider ${STATUS_COLOURS[ticket.status] ?? 'bg-slate-100 text-slate-500'}`}>
                      {ticket.status.replace('_', ' ')}
                    </span>
                  </div>

                  {selectedTicket?.id === ticket.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700"
                    >
                      <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-line">{ticket.message}</p>
                      <p className="text-[11px] text-slate-400 mt-2">
                        Submitted: {new Date(ticket.created_at).toLocaleString()}
                      </p>
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
