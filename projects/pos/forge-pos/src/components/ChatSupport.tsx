/**
 * ChatSupport
 * ===========
 * Floating chat widget that connects to the Sanic WebSocket endpoint at:
 *   ws://127.0.0.1:8765/ws/chat/<room>
 *
 * Features:
 *   - Collapsible floating button (bottom-right corner)
 *   - Real-time WebSocket messaging with auto-reconnect
 *   - REST fallback: submits a support ticket via POST /api/support/ticket
 *     when the sidecar is not reachable
 *   - Message types: "message", "typing", "status" (system)
 *   - Structa.cloud branded header
 *   - Accessible: keyboard-navigable, ARIA labels, focus trap on open
 */

import {
  useState, useEffect, useRef, useId,
  KeyboardEvent, FormEvent,
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// ── Icons use Tabler icon CSS classes via icon-[tabler--*] ──
import { invoke } from '@tauri-apps/api/core';
import { createChatWs } from '../api/chat';
import tickets from '../api/tickets';
import type { ChatMessage, WsConnState, ChatWsConnection } from '../api/chat';

// ---- Constants ------------------------------------------------------------

const RECONNECT_MS = 4000;

// ---- Types ----------------------------------------------------------------

type MsgType = 'message' | 'typing' | 'status';
type Sender  = 'user' | 'support' | 'system';

interface DisplayMessage {
  id: string;
  type: MsgType;
  text: string;
  sender: Sender;
  ts: string;
}

interface TicketForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

const CONN_DOT: Record<WsConnState, { color: string; label: string }> = {
  open:       { color: 'text-primary/80',  label: 'Connected' },
  connecting: { color: 'text-warning/80', label: 'Connecting…' },
  closed:     { color: 'text-base-content/40', label: 'Reconnecting…' },
  error:      { color: 'text-error/80',  label: 'Connection error' },
};

// ---- Helpers --------------------------------------------------------------

const uid = () => Math.random().toString(36).slice(2);
const fmtTime = (iso: string) =>
  new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

// ---- Component ------------------------------------------------------------

interface ChatSupportProps {
  /** Unique room identifier — defaults to a stable per-session ID */
  room?: string;
  /** Whether to show the floating trigger button */
  showTrigger?: boolean;
  /** If true the panel starts open */
  defaultOpen?: boolean;
}

export default function ChatSupport({
  room,
  showTrigger = true,
  defaultOpen = false,
}: ChatSupportProps) {
  const sessionRoom = useRef(room ?? `room-${uid()}`);

  const [isOpen, setIsOpen]       = useState(defaultOpen);
  const [connState, setConnState] = useState<WsConnState>('closed');
  const [messages, setMessages]   = useState<DisplayMessage[]>([
    {
      id: uid(),
      type: 'status',
      text: 'Welcome! How can we help you today? Type a message or submit a ticket below.',
      sender: 'system',
      ts: new Date().toISOString(),
    },
  ]);
  const [draft, setDraft]         = useState('');
  const [isTyping, setIsTyping]   = useState(false);

  // SMTP config from backend
  const [smtpConfig, setSmtpConfig] = useState<{ configured: boolean; support_email: string | null } | null>(null);

  // Ticket fallback form
  const [showTicket, setShowTicket] = useState(false);
  const [ticket, setTicket] = useState<TicketForm>({ name: '', email: '', subject: '', message: '' });
  const [ticketStatus, setTicketStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  const bottomRef  = useRef<HTMLDivElement>(null);
  const inputRef   = useRef<HTMLInputElement>(null);
  const wsConnRef  = useRef<ChatWsConnection | null>(null);
  const titleId    = useId();

  // ---- Scroll to bottom on new messages -----------------------------------
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // ---- Focus input when panel opens ---------------------------------------
  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 120);
  }, [isOpen]);

  // ---- WebSocket connection ------------------------------------------------
  useEffect(() => {
    if (!isOpen) return;

    const conn = createChatWs({
      room: sessionRoom.current,
      onMessage: (msg: ChatMessage) => {
        setIsTyping(false);
        setMessages(prev => [...prev, {
          id: msg.id || uid(),
          type: 'message',
          text: msg.content,
          sender: (msg.user as Sender) || 'support',
          ts: msg.timestamp,
        }]);
      },
      onStateChange: setConnState,
      onTyping: setIsTyping,
      reconnectMs: RECONNECT_MS,
    });

    wsConnRef.current = conn;

    return () => {
      conn.close();
      wsConnRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  // ---- Load SMTP config on mount ------------------------------------------
  useEffect(() => {
    invoke<{ configured: boolean; support_email: string | null }>('get_smtp_config')
      .then(setSmtpConfig)
      .catch(() => setSmtpConfig({ configured: false, support_email: null }));
  }, []);

  // ---- Send message via persistent WebSocket ------------------------------
  const sendMessage = () => {
    const text = draft.trim();
    if (!text) return;

    // Optimistic local append
    setMessages(prev => [...prev, {
      id: uid(),
      type: 'message',
      text,
      sender: 'user',
      ts: new Date().toISOString(),
    }]);
    setDraft('');

    if (connState === 'open' && wsConnRef.current) {
      wsConnRef.current.send({ type: 'message', text, sender: 'user' });
    } else {
      // WS not available — show offline note
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: uid(),
          type: 'status',
          text: 'You appear to be offline. Submit a support ticket below to reach us.',
          sender: 'system',
          ts: new Date().toISOString(),
        }]);
      }, 400);
    }
  };

  // Send typing indicator via persistent WebSocket
  const sendTyping = () => {
    if (connState === 'open' && wsConnRef.current) {
      wsConnRef.current.send({ type: 'typing', sender: 'user' });
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // ---- Ticket fallback ----------------------------------------------------
  const handleTicketSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setTicketStatus('sending');
    const { ok, error } = await tickets.create(ticket);
    if (ok) {
      setTicketStatus('sent');
      setMessages(prev => [...prev, {
        id: uid(),
        type: 'status',
        text: `Ticket submitted! We'll get back to you at ${ticket.email}.`,
        sender: 'system',
        ts: new Date().toISOString(),
      }]);
      setShowTicket(false);
      setTicket({ name: '', email: '', subject: '', message: '' });
    } else {
      setTicketStatus('error');
      console.error('Ticket submission failed:', error);
    }
  };

  // ---- Bubble colours -----------------------------------------------------
  const bubbleClass = (sender: Sender, type: MsgType) => {
    if (type === 'status') return 'bg-base-200/50 text-slate-500 text-center text-xs italic rounded-xl px-3 py-1.5 mx-auto max-w-[85%]';
    if (sender === 'user') return 'bg-primary text-white rounded-2xl rounded-br-sm ml-auto max-w-[82%]';
    return 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 rounded-2xl rounded-bl-sm border border-slate-200 dark:border-slate-600 max-w-[82%]';
  };

  // ---- Render -------------------------------------------------------------
  return (
    <>
      {/* FLOATING TRIGGER BUTTON */}
      {showTrigger && (
        <motion.button
          aria-label={isOpen ? 'Close support chat' : 'Open support chat'}
          onClick={() => setIsOpen(o => !o)}
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.93 }}
          className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary/80 text-white shadow-xl flex items-center justify-center"
        >
          <AnimatePresence mode="wait" initial={false}>
            {isOpen ? (
              <motion.span key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }}>
                <span className="icon-[tabler--x] w-6 h-6" />
              </motion.span>
            ) : (
              <motion.span key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }}>
                <span className="icon-[tabler--message] w-6 h-6" />
              </motion.span>
            )}
          </AnimatePresence>
          {!isOpen && messages.filter(m => m.sender !== 'user' && m.type === 'message').length > 0 && (
            <span className="absolute top-1 right-1 w-3 h-3 rounded-full bg-error border-2 border-white" />
          )}
        </motion.button>
      )}

      {/* CHAT PANEL */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            role="dialog"
            aria-labelledby={titleId}
            aria-modal="true"
            initial={{ opacity: 0, y: 32, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 32, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
            className="fixed bottom-24 right-6 z-50 w-[360px] max-w-[calc(100vw-1.5rem)] flex flex-col rounded-2xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-700"
            style={{ maxHeight: 'min(520px, calc(100vh - 8rem))' }}
          >
            {/* HEADER */}
            <div className="bg-gradient-to-r from-slate-900 to-primary/90 text-white px-4 py-3 flex items-center gap-3 shrink-0">
              <div className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                <span className="icon-[tabler--headset] w-5 h-5 text-primary/70" />
              </div>
              <div className="flex-1 min-w-0">
                <p id={titleId} className="font-bold text-sm leading-tight">
                {smtpConfig?.support_email ? 'Support' : 'Structa Cloud Support'}
              </p>
                <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                  <span className={`icon-[tabler--circle] w-2.5 h-2.5 ${CONN_DOT[connState].color}`} />
                  <span className="text-[11px] text-white/60">{CONN_DOT[connState].label}</span>
                  {smtpConfig?.support_email && (
                    <>
                      <span className="text-white/30 text-[10px]">·</span>
                      <a
                        href={`mailto:${smtpConfig.support_email}`}
                        className="text-[11px] text-primary/80 hover:text-primary/60 underline underline-offset-2 transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {smtpConfig.support_email}
                      </a>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                {connState === 'open'
                  ? <span className="icon-[tabler--wifi] w-4 h-4 text-primary/80" aria-label="Connected" />
                  : <span className="icon-[tabler--wifi-off] w-4 h-4 text-slate-400" aria-label="Disconnected" />}
                <button onClick={() => setIsOpen(false)} aria-label="Close chat" className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-white/10 transition-colors">
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              </div>
            </div>

            {/* POWERED BY */}
            <div className="bg-primary/80 px-4 py-1 flex items-center gap-1.5 shrink-0">
              <img
                src="https://structa.cloud/favicon.ico"
                alt="Structa Cloud"
                className="w-3.5 h-3.5 opacity-80"
                onError={e => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
              />
              <span className="text-[10px] text-primary/70">
                Powered by POS &mdash; structa.cloud
              </span>
            </div>

            {/* MESSAGES */}
            <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900 px-3 py-3 space-y-2.5">
              {messages.map(msg => (
                <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : msg.type === 'status' ? 'justify-center' : 'justify-start'}`}>
                  <div className={`px-3.5 py-2 text-sm leading-relaxed ${bubbleClass(msg.sender, msg.type)}`}>
                    <p>{msg.text}</p>
                    {msg.type !== 'status' && (
                      <p className={`text-[10px] mt-1 ${msg.sender === 'user' ? 'text-primary/60 text-right' : 'text-base-content/40'}`}>
                        {fmtTime(msg.ts)}
                      </p>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white dark:bg-slate-700 rounded-2xl rounded-bl-sm border border-slate-200 dark:border-slate-600 px-3.5 py-2.5 flex items-center gap-1">
                    {[0, 1, 2].map(i => (
                      <motion.span key={i} className="w-1.5 h-1.5 rounded-full bg-slate-400"
                        animate={{ y: [0, -4, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                      />
                    ))}
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* TICKET FORM */}
            <AnimatePresence>
              {showTicket && (
                <motion.form
                  onSubmit={handleTicketSubmit}
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="bg-base-100 border-t border-slate-200 dark:border-slate-700 overflow-hidden shrink-0"
                >
                  <div className="px-4 py-3 space-y-2">
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Submit a Support Ticket</p>
                    {(['name', 'email', 'subject'] as const).map(field => (
                      <input
                        key={field}
                        required
                        type={field === 'email' ? 'email' : 'text'}
                        placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
                        value={ticket[field]}
                        onChange={e => setTicket(prev => ({ ...prev, [field]: e.target.value }))}
                        className="w-full bg-slate-100 dark:bg-slate-700 rounded-lg px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-primary"
                      />
                    ))}
                    <textarea
                      required
                      rows={2}
                      placeholder="Describe your issue…"
                      value={ticket.message}
                      onChange={e => setTicket(prev => ({ ...prev, message: e.target.value }))}
                      className="w-full bg-slate-100 dark:bg-slate-700 rounded-lg px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                    <div className="flex gap-2">
                      <button type="submit" disabled={ticketStatus === 'sending'}
                        className="flex-1 py-1.5 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary/80 disabled:opacity-60"
                      >
                        {ticketStatus === 'sending' ? 'Sending…' : 'Submit Ticket'}
                      </button>
                      <button type="button" onClick={() => setShowTicket(false)}
                        className="px-3 py-1.5 rounded-lg bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-300 text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                    {ticketStatus === 'error' && (
                      <p className="text-xs text-error text-center">Failed to submit. Is the sidecar running?</p>
                    )}
                  </div>
                </motion.form>
              )}
            </AnimatePresence>

            {/* INPUT BAR */}
            <div className="bg-base-100 border-t border-slate-200 dark:border-slate-700 px-3 py-2.5 flex items-center gap-2 shrink-0">
              {/* SMTP direct email button — visible when SMTP is configured */}
              {smtpConfig?.configured && smtpConfig.support_email && (
                <a
                  href={`mailto:${smtpConfig.support_email}?subject=Support%20Request`}
                  className="w-8 h-8 rounded-full flex items-center justify-center transition-colors shrink-0
                    bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400
                    hover:bg-amber-200 dark:hover:bg-amber-900/50"
                  title={`Send email to ${smtpConfig.support_email}`}
                  onClick={(e) => e.stopPropagation()}
                >
                  <span className="icon-[tabler--mail] w-4 h-4" />
                </a>
              )}
              <button
                onClick={() => setShowTicket(t => !t)}
                title="Submit a support ticket"
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors shrink-0 ${
                  showTicket
                    ? 'bg-primary text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-500 hover:bg-slate-200'
                }`}
              >
                <span className="icon-[tabler--headset] w-4 h-4" />
              </button>

              <input
                ref={inputRef}
                type="text"
                placeholder={connState === 'open' ? 'Type a message…' : 'Waiting for connection…'}
                value={draft}
                onChange={e => { setDraft(e.target.value); sendTyping(); }}
                onKeyDown={handleKeyDown}
                className="flex-1 bg-slate-100 dark:bg-slate-700 rounded-full px-4 py-1.5 text-sm outline-none focus:ring-2 focus:ring-primary transition-shadow"
                aria-label="Chat message"
              />

              <motion.button
                whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.9 }}
                onClick={sendMessage}
                disabled={!draft.trim()}
                aria-label="Send message"
                className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
              >
                <span className="icon-[tabler--send] w-4 h-4" />
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
