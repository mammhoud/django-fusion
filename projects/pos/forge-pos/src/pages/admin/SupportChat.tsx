/**
 * SupportChat page — Email-Based Support
 * =======================================
 * Simplified page showing the ChatSupport widget and contact information.
 * No WebSocket, no sidecar, no ticket system needed.
 */

import PageLayout from '../../components/layout/PageLayout';
import ChatSupport from '../../components/pos/ChatSupport';

const SUPPORT_EMAIL = import.meta.env.VITE_SUPPORT_EMAIL as string | undefined;

export default function SupportChat() {
  return (
    <PageLayout
      title={
        <span className="flex items-center gap-2">
          <span className="icon-[tabler--headset] w-5 h-5 text-primary" />
          Support
        </span>
      }
    >
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Status */}
        {SUPPORT_EMAIL ? (
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
              No support email configured. Set <code className="font-mono text-xs">VITE_SUPPORT_EMAIL</code> in your
              <code className="font-mono text-xs">.env</code> file to enable email support.
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
      </div>
    </PageLayout>
  );
}
