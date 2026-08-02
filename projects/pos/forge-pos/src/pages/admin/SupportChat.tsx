/**
 * SupportChat page — Email-Based Support
 * =======================================
 * Shows the ChatSupport widget and contact information, plus a history of
 * every message/ticket persisted in the `support_messages` table with its
 * workflow state (new / in-progress / resolved / closed).
 * SMTP/support email is now configured in Settings → Business (stored in the
 * settings DB) instead of the VITE_SUPPORT_EMAIL env var.
 */

import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../components/layout/PageLayout';
import ChatSupport from '../../components/pos/ChatSupport';

interface SmtpConfig {
  configured: boolean;
  support_email?: string | null;
}

interface SupportMessage {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  subject?: string | null;
  category?: string | null;
  priority: string;
  message: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const STATUS_OPTIONS = ['new', 'in-progress', 'resolved', 'closed'];

const STATUS_STYLES: Record<string, string> = {
  new: 'badge badge-soft bg-info/15 text-info border-info/20',
  'in-progress': 'badge badge-soft bg-warning/15 text-warning border-warning/20',
  resolved: 'badge badge-soft bg-success/15 text-success border-success/20',
  closed: 'badge badge-soft bg-neutral/15 text-base-content/60 border-base-300/30',
};

const PRIORITY_STYLES: Record<string, string> = {
  low: 'text-base-content/40',
  normal: 'text-base-content/70',
  high: 'text-warning',
  urgent: 'text-error',
};

function formatDate(value: string): string {
  const d = new Date(value.replace(' ', 'T'));
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

export default function SupportChat() {
  const [smtpConfig, setSmtpConfig] = useState<SmtpConfig | null>(null);
  const [messages, setMessages] = useState<SupportMessage[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(true);

  const loadMessages = useCallback(async () => {
    setLoadingMessages(true);
    try {
      const list = await invoke<SupportMessage[]>('get_support_messages');
      setMessages(list ?? []);
    } catch {
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  }, []);

  useEffect(() => {
    invoke<SmtpConfig>('get_smtp_config')
      .then(setSmtpConfig)
      .catch(() => setSmtpConfig({ configured: false, support_email: null }));
    loadMessages();
  }, [loadMessages]);

  const updateStatus = useCallback(
    async (id: number, status: string) => {
      try {
        await invoke('update_support_message_status', { id, status });
        await loadMessages();
      } catch (error) {
        console.error('Failed to update message status:', error);
      }
    },
    [loadMessages],
  );

  const deleteMessage = useCallback(
    async (id: number) => {
      try {
        await invoke('delete_support_message', { id });
        await loadMessages();
      } catch (error) {
        console.error('Failed to delete message:', error);
      }
    },
    [loadMessages],
  );

  const SUPPORT_EMAIL = smtpConfig?.support_email;

  return (
    <PageLayout
      title={
        <span className="flex items-center gap-2">
          <span className="icon-[tabler--headset] w-5 h-5 text-primary" />
          Support
        </span>
      }
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Status */}
        {smtpConfig === null ? (
          <div className="alert alert-info">
            <span className="icon-[tabler--loader-2] w-5 h-5 animate-spin" />
            <span>Checking email configuration…</span>
          </div>
        ) : SUPPORT_EMAIL ? (
          <div className="alert alert-success">
            <span className="icon-[tabler--check] w-5 h-5" />
            <span>
              Support email configured — <strong className="font-mono">{SUPPORT_EMAIL}</strong>
            </span>
          </div>
        ) : (
          <div className="alert alert-warning">
            <span className="icon-[tabler--alert-triangle] w-5 h-5" />
            <span>
              No support email configured. Set the SMTP recipient in Settings → Business → Email to
              enable email support.
            </span>
          </div>
        )}

        {/* Chat widget */}
        <div className="bg-base-100 rounded-2xl border border-base-300/50 shadow-sm overflow-hidden" style={{ minHeight: 400 }}>
          <ChatSupport showTrigger={false} defaultOpen={true} />
        </div>

        {/* Contact info */}
        {SUPPORT_EMAIL && (
          <div className="card bg-base-200 border border-base-300/50 p-6">
            <h2 className="text-lg font-semibold text-base-content mb-4 flex items-center gap-2">
              <span className="icon-[tabler--info-circle] w-5 h-5 text-info" />
              Contact Information
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <span className="icon-[tabler--mail] w-4 h-4 text-primary" />
                <a href={`mailto:${SUPPORT_EMAIL}`} className="text-primary hover:underline font-mono text-xs">
                  {SUPPORT_EMAIL}
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Message history */}
        <div className="bg-base-100 rounded-2xl border border-base-300/50 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-base-300/50 flex items-center justify-between">
            <h2 className="text-base font-semibold text-base-content flex items-center gap-2">
              <span className="icon-[tabler--messages] w-5 h-5 text-primary" />
              Message History
              <span className="badge badge-soft bg-primary/10 text-primary border-primary/20">{messages.length}</span>
            </h2>
            <button onClick={loadMessages} className="btn btn-ghost btn-sm gap-1.5">
              <span className="icon-[tabler--refresh] w-3.5 h-3.5" />
              Refresh
            </button>
          </div>

          {loadingMessages ? (
            <div className="p-8 text-center text-base-content/40 text-sm">
              <span className="icon-[tabler--loader-2] w-5 h-5 animate-spin inline-block" /> Loading messages…
            </div>
          ) : messages.length === 0 ? (
            <div className="p-8 text-center text-base-content/40 text-sm">
              <span className="icon-[tabler--inbox] w-8 h-8 mx-auto mb-2 opacity-50 block" />
              No messages yet. Submissions from the chat widget will appear here.
            </div>
          ) : (
            <ul className="divide-y divide-base-300/50 max-h-[480px] overflow-y-auto">
              {messages.map(m => (
                <li key={m.id} className="px-5 py-4 hover:bg-base-200/30 transition-colors">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-semibold text-sm text-base-content">{m.name}</span>
                        <span className="text-xs text-base-content/40 font-mono">{m.email}</span>
                        <span className={`text-[10px] font-semibold uppercase ${PRIORITY_STYLES[m.priority] || ''}`}>
                          {m.priority}
                        </span>
                      </div>
                      {m.subject && (
                        <p className="text-sm font-medium text-base-content/80 mt-1 truncate">{m.subject}</p>
                      )}
                      <p className="text-xs text-base-content/50 mt-1 line-clamp-2">{m.message}</p>
                      <div className="flex items-center gap-2 mt-2 flex-wrap text-[10px] text-base-content/30">
                        {m.category && (
                          <span className="inline-flex items-center gap-1">
                            <span className="icon-[tabler--tag] w-3 h-3" /> {m.category}
                          </span>
                        )}
                        {m.phone && (
                          <span className="inline-flex items-center gap-1">
                            <span className="icon-[tabler--phone] w-3 h-3" /> {m.phone}
                          </span>
                        )}
                        <span className="inline-flex items-center gap-1">
                          <span className="icon-[tabler--clock] w-3 h-3" /> {formatDate(m.created_at)}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-2 shrink-0">
                      <select
                        value={m.status}
                        onChange={e => updateStatus(m.id, e.target.value)}
                        className="select select-sm select-bordered text-xs"
                        aria-label="Message status"
                      >
                        {STATUS_OPTIONS.map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                      <span className={STATUS_STYLES[m.status] || 'badge'}>{m.status}</span>
                      <button
                        onClick={() => deleteMessage(m.id)}
                        className="btn btn-ghost btn-xs text-error gap-1"
                        aria-label="Delete message"
                      >
                        <span className="icon-[tabler--trash] w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
