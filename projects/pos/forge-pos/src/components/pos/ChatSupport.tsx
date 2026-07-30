/**
 * ChatSupport — Email-Based Support Widget
 * =========================================
 * Lightweight floating support button that opens the user's default email client.
 *
 * Visibility logic (per Section 15 of UI enhancement plan):
 *   - If VITE_SUPPORT_EMAIL is set AND MCP is NOT configured: show email chat
 *   - If MCP is configured (settings.mcp_enabled): hide email chat (MCP takes priority)
 *   - If neither is set: hidden entirely (returns null)
 *
 * No WebSocket, no sidecar, no API calls needed.
 */

import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import AnimatePresence from '../../components/ui/AnimatePresence';

/** Read the support email from Vite env vars at build time */
const SUPPORT_EMAIL = import.meta.env.VITE_SUPPORT_EMAIL as string | undefined;

interface ChatSupportProps {
  showTrigger?: boolean;
  defaultOpen?: boolean;
}

export default function ChatSupport({
  showTrigger = true,
  defaultOpen = false,
}: ChatSupportProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [mcpConfigured, setMcpConfigured] = useState<boolean | null>(null);

  // Check MCP settings on mount — MCP takes priority over email support
  useEffect(() => {
    invoke<{ mcp_enabled?: boolean }>('get_settings')
      .then(s => setMcpConfigured(!!s.mcp_enabled))
      .catch(() => setMcpConfigured(false));
  }, []);

  // Hide while checking MCP status (prevents flash of email panel)
  if (mcpConfigured === null) return null;
  // Hide entirely if no support email configured, or if MCP takes priority
  if (!SUPPORT_EMAIL || mcpConfigured) return null;

  const subject = encodeURIComponent('Forge POS — Support Request');
  const mailtoUrl = `mailto:${SUPPORT_EMAIL}?subject=${subject}`;

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

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
            className="fixed bottom-24 right-6 z-50 w-[340px] max-w-[calc(100vw-1.5rem)] rounded-2xl shadow-2xl overflow-hidden border border-base-300 bg-base-100"
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

            {/* Body */}
            <div className="p-5 space-y-4">
              <p className="text-sm text-base-content/70 leading-relaxed">
                Send us an email and we&apos;ll get back to you as soon as possible.
                Describe your issue, question, or feedback.
              </p>
              <p className="text-xs text-base-content/40 italic">
                {t('support.mcpHint') || 'Want faster help? Enable MCP support in Settings → General for AI-powered assistance.'}
              </p>

              {/* Email info */}
              <div className="bg-base-200 rounded-xl p-4 space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <span className="icon-[tabler--mail] w-4 h-4 text-primary" />
                  <span className="text-base-content/50">Support email:</span>
                  <span className="font-mono font-medium text-base-content text-xs">{SUPPORT_EMAIL}</span>
                </div>

                <a
                  href={mailtoUrl}
                  className="btn btn-primary w-full gap-2"
                >
                  <span className="icon-[tabler--send] w-4 h-4" />
                  Compose Email
                </a>

                <a
                  href={`mailto:${SUPPORT_EMAIL}`}
                  className="btn btn-ghost btn-sm w-full gap-2"
                >
                  <span className="icon-[tabler--external-link] w-3.5 h-3.5" />
                  Open in Email Client
                </a>
              </div>

              {/* Quick tips */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider">
                  Tips for faster help
                </p>
                <ul className="text-xs text-base-content/50 space-y-1.5 list-disc pl-4">
                  <li>Include your POS version (found in Settings → About)</li>
                  <li>Describe the steps to reproduce any issue</li>
                  <li>Attach screenshots if possible</li>
                </ul>
              </div>
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
