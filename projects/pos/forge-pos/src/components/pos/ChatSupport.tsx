/**
 * ChatSupport — Tawk-style Pre-Chat Form Widget
 * ==============================================
 * Floating support button that opens a pre-chat form (Name, Email, Phone,
 * Subject, Category, Priority, Message). Submissions are persisted to the
 * `support_messages` table via `submit_support_message` (status = "new") and
 * forwarded to the support inbox by email.
 *
 * Visibility logic:
 *   - If SMTP recipient is configured (settings DB) AND MCP is NOT configured: show email chat
 *   - If MCP is configured (settings.mcp_enabled): hide email chat (MCP takes priority)
 *   - If neither is set: hidden entirely (returns null)
 */

import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import AnimatePresence from '../../components/ui/AnimatePresence';

interface ChatSupportProps {
  showTrigger?: boolean;
  defaultOpen?: boolean;
}

interface FormState {
  name: string;
  email: string;
  phone: string;
  subject: string;
  category: string;
  priority: string;
  message: string;
}

const CATEGORIES = ['general', 'billing', 'technical', 'feature', 'feedback'];
const PRIORITIES = ['low', 'normal', 'high', 'urgent'];

const INITIAL_FORM: FormState = {
  name: '',
  email: '',
  phone: '',
  subject: '',
  category: 'general',
  priority: 'normal',
  message: '',
};

export default function ChatSupport({
  showTrigger = true,
  defaultOpen = false,
}: ChatSupportProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [mcpConfigured, setMcpConfigured] = useState<boolean | null>(null);
  const [supportEmail, setSupportEmail] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitState, setSubmitState] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  // Check MCP settings + SMTP config on mount — MCP takes priority over email support
  useEffect(() => {
    invoke<{ mcp_enabled?: boolean }>('get_settings')
      .then(s => setMcpConfigured(!!s.mcp_enabled))
      .catch(() => setMcpConfigured(false));
    invoke<{ support_email?: string | null }>('get_smtp_config')
      .then(cfg => setSupportEmail(cfg.support_email ?? null))
      .catch(() => setSupportEmail(null));
  }, []);

  // Close on Escape key (hooks must run unconditionally — declared before any
  // conditional returns so the hook order never changes between renders)
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleChange = useCallback(
    (field: keyof FormState, value: string) => {
      setForm(f => ({ ...f, [field]: value }));
      setErrors(e => ({ ...e, [field]: undefined }));
    },
    [],
  );

  const validate = useCallback((): boolean => {
    const next: Partial<Record<keyof FormState, string>> = {};
    if (!form.name.trim()) next.name = t('support.errorsName') || 'Please enter your name';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()))
      next.email = t('support.errorsEmail') || 'Please enter a valid email';
    if (!form.message.trim())
      next.message = t('support.errorsMessage') || 'Please enter a message';
    setErrors(next);
    return Object.keys(next).length === 0;
  }, [form, t]);

  const handleSubmit = useCallback(async () => {
    if (!validate()) return;
    setSubmitting(true);
    setSubmitState('idle');
    setErrorMessage('');
    try {
      await invoke('submit_support_message', {
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        subject: form.subject.trim() || null,
        category: form.category,
        priority: form.priority,
        message: form.message.trim(),
      });
      setSubmitState('success');
      setForm(INITIAL_FORM);
    } catch (error) {
      console.error('Error submitting support message:', error);
      setSubmitState('error');
      setErrorMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setSubmitting(false);
    }
  }, [form, validate, t]);

  // Hide while checking MCP status (prevents flash of email panel)
  if (mcpConfigured === null) return null;
  // Hide entirely if no support email configured, or if MCP takes priority
  if (!supportEmail || mcpConfigured) return null;

  return (
    <>
      {/* Floating trigger button */}
      {showTrigger && (
        <button
          aria-label={isOpen ? 'Close support panel' : 'Open support'}
          onClick={() => setIsOpen(o => !o)}
          className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-linear-to-br from-primary to-primary/70 text-white shadow-xl flex items-center justify-center active:scale-[0.93] transition-transform hover:shadow-2xl"
        >
          <AnimatePresence mode="wait" initial={false}>
            {isOpen ? (
              <span key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }}>
                <span className="icon-[tabler--x] w-6 h-6" />
              </span>
            ) : (
              <span key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }}>
                <span className="icon-[tabler--message] w-6 h-6" />
              </span>
            )}
          </AnimatePresence>
        </button>
      )}

      {/* Support panel */}
      <AnimatePresence>
        {isOpen && (
          <div
            role="dialog"
            aria-label="Support contact"
            initial={{ opacity: 0, y: 32, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 32, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
            className="fixed bottom-24 right-6 z-50 w-[360px] max-w-[calc(100vw-1.5rem)] rounded-2xl shadow-2xl overflow-hidden border border-base-300 bg-base-100"
          >
            {/* Header */}
            <div className="bg-linear-to-r from-base-300 to-primary/90 text-white px-4 py-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                  <span className="icon-[tabler--headset] w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-sm">Need Help?</p>
                  <p className="text-xs text-white/60 mt-0.5">We're here to assist you</p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-white/10 transition-colors"
                >
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Body — Tawk-style pre-chat form */}
            <div className="p-5 space-y-4 max-h-[70vh] overflow-y-auto">
              <p className="text-sm text-base-content/70 leading-relaxed">
                Please fill out the form below and we will get back to you as soon as possible.
              </p>

              {submitState === 'success' ? (
                <div className="text-center py-6 space-y-3">
                  <div className="w-14 h-14 mx-auto rounded-full bg-success/15 flex items-center justify-center">
                    <span className="icon-[tabler--check] w-7 h-7 text-success" />
                  </div>
                  <p className="font-semibold text-base-content">{t('support.success') || 'Message sent!'}</p>
                  <p className="text-xs text-base-content/50">
                    {t('support.successBody') || 'We will get back to you as soon as possible.'}
                  </p>
                  <button
                    onClick={() => setSubmitState('idle')}
                    className="btn btn-ghost btn-sm"
                  >
                    <span className="icon-[tabler--send] w-3.5 h-3.5" />
                    {t('support.sendAnother') || 'Send another message'}
                  </button>
                </div>
              ) : (
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    handleSubmit();
                  }}
                  className="space-y-3"
                >
                  {/* Name */}
                  <div className="field">
                    <label htmlFor="chat-name" className="input__label input__label--required">
                      {t('support.name') || 'Name'}
                    </label>
                    <div className="input__wrapper">
                      <input
                        id="chat-name"
                        name="name"
                        required
                        placeholder="Your name"
                        value={form.name}
                        onChange={e => handleChange('name', e.target.value)}
                        className="input__field"
                      />
                    </div>
                    {errors.name && <p className="input__message">{errors.name}</p>}
                  </div>

                  {/* Email */}
                  <div className="field">
                    <label htmlFor="chat-email" className="input__label input__label--required">
                      {t('support.email') || 'Email'}
                    </label>
                    <div className="input__wrapper">
                      <input
                        id="chat-email"
                        name="email"
                        type="email"
                        required
                        placeholder="you@example.com"
                        value={form.email}
                        onChange={e => handleChange('email', e.target.value)}
                        className="input__field"
                      />
                    </div>
                    {errors.email && <p className="input__message">{errors.email}</p>}
                  </div>

                  {/* Phone */}
                  <div className="field">
                    <label htmlFor="chat-phone" className="input__label">
                      {t('support.phone') || 'Phone'}
                    </label>
                    <div className="input__wrapper">
                      <input
                        id="chat-phone"
                        name="phone"
                        type="tel"
                        placeholder="+1 555 000 0000"
                        value={form.phone}
                        onChange={e => handleChange('phone', e.target.value)}
                        className="input__field"
                      />
                    </div>
                  </div>

                  {/* Subject */}
                  <div className="field">
                    <label htmlFor="chat-subject" className="input__label">
                      {t('support.subject') || 'Subject'}
                    </label>
                    <div className="input__wrapper">
                      <input
                        id="chat-subject"
                        name="subject"
                        placeholder="Brief summary of your issue"
                        value={form.subject}
                        onChange={e => handleChange('subject', e.target.value)}
                        className="input__field"
                      />
                    </div>
                  </div>

                  {/* Category + Priority */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="field">
                      <label htmlFor="chat-category" className="input__label">
                        {t('support.category') || 'Category'}
                      </label>
                      <div className="input__wrapper">
                        <select
                          id="chat-category"
                          name="category"
                          value={form.category}
                          onChange={e => handleChange('category', e.target.value)}
                          className="input__field input__field--select"
                        >
                          {CATEGORIES.map(c => (
                            <option key={c} value={c}>
                              {t(`support.categories.${c}`) || c}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className="field">
                      <label htmlFor="chat-priority" className="input__label">
                        {t('support.priority') || 'Priority'}
                      </label>
                      <div className="input__wrapper">
                        <select
                          id="chat-priority"
                          name="priority"
                          value={form.priority}
                          onChange={e => handleChange('priority', e.target.value)}
                          className="input__field input__field--select"
                        >
                          {PRIORITIES.map(p => (
                            <option key={p} value={p}>
                              {t(`support.priorities.${p}`) || p}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Message */}
                  <div className="field">
                    <label htmlFor="chat-message" className="input__label input__label--required">
                      {t('support.message') || 'Message'}
                    </label>
                    <div className="input__wrapper">
                      <textarea
                        id="chat-message"
                        name="message"
                        required
                        maxLength={500}
                        placeholder="Describe your issue, question, or feedback…"
                        value={form.message}
                        onChange={e => handleChange('message', e.target.value)}
                        className="input__field input__field--textarea"
                      />
                    </div>
                    {errors.message && <p className="input__message">{errors.message}</p>}
                  </div>

                  {/* Submit */}
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn btn-primary w-full gap-2"
                  >
                    {submitting ? (
                      <>
                        <span className="icon-[tabler--loader-2] w-4 h-4 animate-spin" />
                        {t('support.sending') || 'Sending…'}
                      </>
                    ) : (
                      <>
                        <span className="icon-[tabler--send] w-4 h-4" />
                        {t('support.submit') || 'Submit'}
                      </>
                    )}
                  </button>

                  {submitState === 'error' && (
                    <p className="text-xs text-error text-center">{errorMessage}</p>
                  )}

                  <p className="text-[10px] text-base-content/30 text-center">
                    {t('support.mcpHint') || 'Want faster help? Enable MCP support in Settings → General for AI-powered assistance.'}
                  </p>
                </form>
              )}
            </div>

            {/* Footer */}
            <div className="bg-base-200/50 px-4 py-2 border-t border-base-300/50">
              <p className="text-[10px] text-base-content/30 text-center">
                Powered by Forge POS &mdash; structa.cloud
              </p>
            </div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
