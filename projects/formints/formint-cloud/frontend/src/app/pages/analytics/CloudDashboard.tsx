/**
 * POS Cloud — Cloud Dashboard (Multi-branch Management)
 * =====================================================
 * The management surface over `apps.handlers.sync_dashboard`: where an
 * operator triages the sync mesh. Three panels:
 *
 *   1. Sync Queue  — pending/failed items with retry + cancel actions.
 *   2. Conflicts   — pending conflicts with resolve (local/remote/merge) +
 *                    dismiss actions.
 *   3. Activity    — the most recent sync activity across branches.
 *
 * Complements `BranchOverview` (the read-only telemetry roster): this page
 * is the *action* side of the same `/api/dashboard/*` contract, rendered in
 * the same phosphor-on-carbon CRT aesthetic.
 *
 * Liveness: initial fetch + 10s polling + best-effort refetch on
 * `/ws/sync-events/` frames (polling is the backbone).
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import PageLayout from '../../../components/layout/PageLayout';
import { dashboard, createSyncEventsWs, type SyncEventsConnection } from '../../../api';
import type {
  QueueSummary,
  QueueItem,
  SyncConflict,
  ActivityEntry,
} from '../../../api';
import { useTranslation } from 'react-i18next';

// ── Tactical Telemetry palette (mirrors BranchOverview) ────────────────────
const CRT = '#0A0A0A';
const PANEL = '#101010';
const PHOSPHOR = '#EAEAEA';
const HAZARD = '#E61919';
const TERMINAL_GREEN = '#4AF626';

const POLL_MS = 10_000;
const WS_REFETCH_MIN_MS = 2_000;

/** Status glyph metadata for queue items. */
const QUEUE_META: Record<string, { label: string; color: string }> = {
  pending: { label: 'PENDING', color: '#EAEAEA' },
  delivering: { label: 'DELIVERING', color: '#4AF626' },
  delivered: { label: 'DELIVERED', color: '#4AF626' },
  failed: { label: 'FAILED', color: HAZARD },
  cancelled: { label: 'CANCELLED', color: 'rgba(234,234,234,0.4)' },
};

export default function CloudDashboard() {
  const { t } = useTranslation();

  const [queueSummary, setQueueSummary] = useState<QueueSummary | null>(null);
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const lastWsRefetchRef = useRef(0);

  const refresh = useCallback(async ({ quiet = false }: { quiet?: boolean } = {}) => {
    if (!quiet) setLoading(true);
    const [summary, list, conflictRes, activityRes] = await Promise.all([
      dashboard.getQueueSummary(),
      dashboard.getQueueList('pending'),
      dashboard.getConflicts(),
      dashboard.getActivity(20),
    ]);

    if (summary.ok && summary.data) setQueueSummary(summary.data);
    if (list.ok && list.data) setQueueItems(list.data.items);
    if (conflictRes.ok && conflictRes.data) setConflicts(conflictRes.data.conflicts);
    if (activityRes.ok && activityRes.data) setActivity(activityRes.data.entries);

    if (!summary.ok && !list.ok) {
      setError(summary.error || list.error || 'HTTP error');
      if (!quiet) setLoading(false);
      return;
    }
    setError(null);
    setLastUpdated(new Date());
    if (!quiet) setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
    const pollId = window.setInterval(() => refresh({ quiet: true }), POLL_MS);
    const onFocus = () => refresh({ quiet: true });
    window.addEventListener('focus', onFocus);
    return () => {
      window.clearInterval(pollId);
      window.removeEventListener('focus', onFocus);
    };
  }, [refresh]);

  useEffect(() => {
    let conn: SyncEventsConnection | null = null;
    try {
      conn = createSyncEventsWs({
        onEvent: () => {
          const now = Date.now();
          if (now - lastWsRefetchRef.current < WS_REFETCH_MIN_MS) return;
          lastWsRefetchRef.current = now;
          refresh({ quiet: true });
        },
      });
    } catch {
      // WebSocket is optional — polling keeps the view live without it.
    }
    return () => {
      conn?.close();
    };
  }, [refresh]);

  // ── Actions ──────────────────────────────────────────────────────────────

  const run = async (key: string, fn: () => Promise<void>, okMsg: string) => {
    setBusy(key);
    setNotice(null);
    try {
      await fn();
      setNotice(okMsg);
    } catch (err) {
      setNotice(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(null);
      refresh({ quiet: true });
    }
  };

  const retryItem = (item: QueueItem) =>
    run(`retry-${item.id}`, async () => {
      const res = await dashboard.retryQueueItem(item.id);
      if (!res.ok) throw new Error(res.error || 'retry failed');
    }, t('cloudDashboard.retryQueued', 'Item queued for retry'));

  const cancelItem = (item: QueueItem) =>
    run(`cancel-${item.id}`, async () => {
      const res = await dashboard.cancelQueueItem(item.id);
      if (!res.ok) throw new Error(res.error || 'cancel failed');
    }, t('cloudDashboard.cancelled', 'Item cancelled'));

  const resolveConflict = (conflict: SyncConflict, resolution: 'use_local' | 'use_remote' | 'merge') =>
    run(`resolve-${conflict.id}-${resolution}`, async () => {
      const res = await dashboard.resolveConflict(conflict.id, resolution);
      if (!res.ok) throw new Error(res.error || 'resolve failed');
    }, t('cloudDashboard.resolved', 'Conflict resolved'));

  const dismissConflict = (conflict: SyncConflict) =>
    run(`dismiss-${conflict.id}`, async () => {
      const res = await dashboard.dismissConflict(conflict.id);
      if (!res.ok) throw new Error(res.error || 'dismiss failed');
    }, t('cloudDashboard.dismissed', 'Conflict dismissed'));

  const firstLoad = loading && queueSummary === null;

  return (
    <PageLayout
      title={t('cloudDashboard.title', 'Cloud Dashboard')}
      background="bg-base-200/40"
    >
      <div
        role="region"
        aria-label="Cloud dashboard management"
        className="relative overflow-hidden border"
        style={{
          fontFamily: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
          backgroundColor: CRT,
          color: PHOSPHOR,
          borderColor: 'rgba(234, 234, 234, 0.15)',
        }}
      >
        {/* CRT scanlines */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 z-0 opacity-40"
          style={{
            background:
              'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.35) 2px, rgba(0,0,0,0.35) 4px)',
          }}
        />

        <div className="relative z-10">
          {/* Header */}
          <header className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-b border-[#EAEAEA]/15 px-4 py-2.5">
            <p className="text-[11px] font-bold tracking-[0.18em]" style={{ color: HAZARD }}>
              [ CLOUD DASHBOARD ]
            </p>
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/50 uppercase">
              UNIT / POS-CLOUD&nbsp;·&nbsp;MODE / MANAGE
            </p>
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/45 uppercase">
              {lastUpdated ? `POLL / ${lastUpdated.toLocaleTimeString()}` : 'POLL / AWAITING…'}
            </p>
          </header>

          {/* Notice / error strip */}
          {(notice || (error && queueSummary === null)) && (
            <div
              role="status"
              className="flex flex-wrap items-center justify-between gap-3 border-b border-[#E61919]/50 bg-[#E61919]/10 px-4 py-2.5"
            >
              <p className="text-[11px] tracking-[0.14em] text-[#E61919] uppercase">
                &gt;&gt;&gt; {error && queueSummary === null ? `LINK ERROR — ${error}` : notice}
              </p>
              {(error && queueSummary === null) && (
                <button
                  type="button"
                  onClick={() => refresh()}
                  className="border border-[#E61919] px-3 py-1 text-[10px] font-bold tracking-[0.18em] text-[#E61919] uppercase transition-colors hover:bg-[#E61919] hover:text-[#0A0A0A]"
                >
                  RETRY LINK
                </button>
              )}
            </div>
          )}

          {/* Summary strip */}
          <section className="grid grid-cols-3 gap-px bg-[#EAEAEA]/15">
            {[
              { label: 'QUEUED', value: queueSummary?.pending ?? '—' },
              { label: 'FAILED', value: queueSummary?.failed ?? '—' },
              { label: 'CONFLICTS', value: conflicts.length ?? '—' },
            ].map(stat => (
              <div key={stat.label} className="flex flex-col justify-between p-4" style={{ backgroundColor: PANEL }}>
                <dt className="text-[10px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">{stat.label}</dt>
                <dd className="mt-2 text-2xl font-bold text-[#EAEAEA] tabular-nums">{stat.value}</dd>
              </div>
            ))}
          </section>

          {/* ── Sync Queue ── */}
          <section className="border-t border-[#EAEAEA]/15">
            <header className="flex items-center justify-between px-4 py-2.5 border-b border-[#EAEAEA]/15">
              <p className="text-[11px] font-bold tracking-[0.18em]" style={{ color: TERMINAL_GREEN }}>
                [ {t('cloudDashboard.syncQueue', 'SYNC QUEUE')} ]
              </p>
              <p className="text-[10px] tracking-[0.14em] text-[#EAEAEA]/45 uppercase">
                {queueItems.length} {t('cloudDashboard.items', 'ITEMS')}
              </p>
            </header>

            {firstLoad && (
              <ul className="divide-y divide-[#EAEAEA]/10">
                {[0, 1].map(i => (
                  <li key={i} className="px-4 py-4 text-xs tracking-[0.16em] text-[#EAEAEA]/50 uppercase opacity-40">
                    AWAITING TELEMETRY…
                  </li>
                ))}
              </ul>
            )}

            {!firstLoad && queueItems.length === 0 && (
              <p className="px-4 py-8 text-center text-[11px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                &lt; {t('cloudDashboard.noQueue', 'NO PENDING ITEMS')} / &gt;
              </p>
            )}

            {!firstLoad && queueItems.length > 0 && (
              <ul data-testid="cloud-queue" className="divide-y divide-[#EAEAEA]/10">
                {queueItems.map(item => {
                  const meta = QUEUE_META[item.status] ?? QUEUE_META.pending;
                  return (
                    <li
                      key={item.id}
                      className="grid grid-cols-1 gap-2 px-4 py-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"
                    >
                      <div className="min-w-0">
                        <p className="truncate text-[12px] font-bold tracking-[0.12em] text-[#EAEAEA] uppercase">
                          {item.entity_type} / {item.operation}
                        </p>
                        <p className="truncate text-[10px] tracking-[0.12em] text-[#EAEAEA]/45 uppercase">
                          {item.branch_code} · ATTEMPT {item.attempt_count}/{item.max_attempts}
                          {item.last_error ? ` · ${item.last_error}` : ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className="border px-2 py-0.5 text-[10px] font-bold tracking-[0.16em]"
                          style={{ color: meta.color, borderColor: meta.color }}
                        >
                          {meta.label}
                        </span>
                        {item.status === 'failed' && (
                          <button
                            type="button"
                            data-testid={`retry-${item.id}`}
                            disabled={busy === `retry-${item.id}`}
                            onClick={() => retryItem(item)}
                            className="border border-[#4AF626] px-2.5 py-0.5 text-[10px] font-bold tracking-[0.16em] text-[#4AF626] uppercase transition-colors hover:bg-[#4AF626] hover:text-[#0A0A0A] disabled:opacity-40"
                          >
                            {busy === `retry-${item.id}` ? '…' : 'RETRY'}
                          </button>
                        )}
                        {item.status === 'pending' && (
                          <button
                            type="button"
                            data-testid={`cancel-${item.id}`}
                            disabled={busy === `cancel-${item.id}`}
                            onClick={() => cancelItem(item)}
                            className="border border-[#E61919] px-2.5 py-0.5 text-[10px] font-bold tracking-[0.16em] text-[#E61919] uppercase transition-colors hover:bg-[#E61919] hover:text-[#0A0A0A] disabled:opacity-40"
                          >
                            {busy === `cancel-${item.id}` ? '…' : 'CANCEL'}
                          </button>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>

          {/* ── Conflicts ── */}
          <section className="border-t border-[#EAEAEA]/15">
            <header className="flex items-center justify-between px-4 py-2.5 border-b border-[#EAEAEA]/15">
              <p className="text-[11px] font-bold tracking-[0.18em]" style={{ color: HAZARD }}>
                [ {t('cloudDashboard.conflicts', 'CONFLICTS')} ]
              </p>
              <p className="text-[10px] tracking-[0.14em] text-[#EAEAEA]/45 uppercase">
                {conflicts.length} {t('cloudDashboard.pending', 'PENDING')}
              </p>
            </header>

            {!firstLoad && conflicts.length === 0 && (
              <p className="px-4 py-8 text-center text-[11px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                &lt; {t('cloudDashboard.noConflicts', 'NO PENDING CONFLICTS')} / &gt;
              </p>
            )}

            {conflicts.length > 0 && (
              <ul data-testid="cloud-conflicts" className="divide-y divide-[#EAEAEA]/10">
                {conflicts.map(conflict => (
                  <li key={conflict.id} className="px-4 py-3">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="text-[12px] font-bold tracking-[0.12em] text-[#EAEAEA] uppercase">
                          {conflict.entity_type}#{conflict.entity_id}
                        </p>
                        <p className="mt-0.5 text-[10px] tracking-[0.12em] text-[#EAEAEA]/50 uppercase">
                          {conflict.branch_code} · {conflict.resolver_used}
                          {conflict.reason ? ` · ${conflict.reason}` : ''}
                        </p>
                        {conflict.conflict_fields?.length > 0 && (
                          <p className="mt-1 text-[10px] tracking-[0.1em] text-[#EAEAEA]/60">
                            {conflict.conflict_fields
                              .map(f => `${f.field}: ${String(f.local_value)} → ${String(f.remote_value)}`)
                              .join(' · ')}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-1.5">
                        <button
                          type="button"
                          data-testid={`resolve-local-${conflict.id}`}
                          disabled={busy?.startsWith(`resolve-${conflict.id}`)}
                          onClick={() => resolveConflict(conflict, 'use_local')}
                          className="border border-[#EAEAEA]/50 px-2 py-0.5 text-[10px] font-bold tracking-[0.14em] text-[#EAEAEA] uppercase transition-colors hover:bg-[#EAEAEA] hover:text-[#0A0A0A] disabled:opacity-40"
                        >
                          {busy === `resolve-${conflict.id}-use_local` ? '…' : 'KEEP LOCAL'}
                        </button>
                        <button
                          type="button"
                          data-testid={`resolve-remote-${conflict.id}`}
                          disabled={busy?.startsWith(`resolve-${conflict.id}`)}
                          onClick={() => resolveConflict(conflict, 'use_remote')}
                          className="border border-[#4AF626] px-2 py-0.5 text-[10px] font-bold tracking-[0.14em] text-[#4AF626] uppercase transition-colors hover:bg-[#4AF626] hover:text-[#0A0A0A] disabled:opacity-40"
                        >
                          {busy === `resolve-${conflict.id}-use_remote` ? '…' : 'KEEP REMOTE'}
                        </button>
                        <button
                          type="button"
                          data-testid={`resolve-merge-${conflict.id}`}
                          disabled={busy?.startsWith(`resolve-${conflict.id}`)}
                          onClick={() => resolveConflict(conflict, 'merge')}
                          className="border border-[#EAEAEA]/50 px-2 py-0.5 text-[10px] font-bold tracking-[0.14em] text-[#EAEAEA] uppercase transition-colors hover:bg-[#EAEAEA] hover:text-[#0A0A0A] disabled:opacity-40"
                        >
                          {busy === `resolve-${conflict.id}-merge` ? '…' : 'MERGE'}
                        </button>
                        <button
                          type="button"
                          data-testid={`dismiss-${conflict.id}`}
                          disabled={busy?.startsWith(`resolve-${conflict.id}`) || busy?.startsWith(`dismiss-${conflict.id}`)}
                          onClick={() => dismissConflict(conflict)}
                          className="border border-[#E61919] px-2 py-0.5 text-[10px] font-bold tracking-[0.14em] text-[#E61919] uppercase transition-colors hover:bg-[#E61919] hover:text-[#0A0A0A] disabled:opacity-40"
                        >
                          {busy === `dismiss-${conflict.id}` ? '…' : 'DISMISS'}
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* ── Activity ── */}
          <section className="border-t border-[#EAEAEA]/15">
            <header className="flex items-center justify-between px-4 py-2.5 border-b border-[#EAEAEA]/15">
              <p className="text-[11px] font-bold tracking-[0.18em]" style={{ color: PHOSPHOR }}>
                [ {t('cloudDashboard.activity', 'RECENT ACTIVITY')} ]
              </p>
            </header>

            {!firstLoad && activity.length === 0 && (
              <p className="px-4 py-8 text-center text-[11px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                &lt; {t('cloudDashboard.noActivity', 'NO ACTIVITY')} / &gt;
              </p>
            )}

            {activity.length > 0 && (
              <ul data-testid="cloud-activity" className="divide-y divide-[#EAEAEA]/10">
                {activity.map(entry => (
                  <li key={entry.id} className="grid grid-cols-1 gap-1 px-4 py-2.5 sm:grid-cols-[minmax(0,1fr)_auto]">
                    <p className="truncate text-[11px] tracking-[0.12em] text-[#EAEAEA]/80 uppercase">
                      {entry.branch_code} · {entry.entity_type} × {entry.entity_count}
                    </p>
                    <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/40 uppercase tabular-nums">
                      {entry.status}
                      {entry.received_at ? ` · ${entry.received_at}` : ''}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Footer */}
          <footer className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-t border-[#EAEAEA]/15 px-4 py-2.5">
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/40 uppercase">
              © 2026 FORMINT CLOUD ® · POS-CLOUD / SYNC MESH
            </p>
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/40 uppercase tabular-nums">
              {error ? 'LINK / STALE — POLLING' : `UPDATED / EVERY ${POLL_MS / 1000}S`}
            </p>
          </footer>
        </div>
      </div>
    </PageLayout>
  );
}
