/**
 * POS Cloud — Branch Overview (Tactical Telemetry)
 * =================================================
 * Live fleet roster for the pos-cloud sync mesh. Renders the
 * `/api/dashboard/branches/health` contract as an industrial CRT
 * telemetry panel — phosphor-on-carbon, hazard-red accents, ASCII
 * framing, scanlines — with ONLINE / DEGRADED / OFFLINE states.
 *
 * Liveness: initial fetch + 10s polling + refetch on window focus +
 * push-triggered refetch from the `/ws/sync-events/` stream (best-effort;
 * polling is the backbone, the socket just accelerates it).
 *
 * Design language: the `industrial-brutalist-ui` "Tactical Telemetry &
 * CRT Terminal" archetype — dark substrate only, one terminal-green
 * element (the fleet sync-rate readout), zero border-radius, 1px
 * mechanical dividers, monospace telemetry throughout.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import PageLayout from '../../../components/layout/PageLayout';
import { dashboard, createSyncEventsWs, type SyncEventsConnection } from '../../../api';
import type { BranchHealth, QueueSummary, ConflictStats } from '../../../api';
import { useTranslation } from 'react-i18next';

// ── Tactical Telemetry palette ────────────────────────────────────────────
const CRT = '#0A0A0A'; // deactivated CRT substrate
const PANEL = '#101010'; // instrument panel
const PHOSPHOR = '#EAEAEA'; // white phosphor text
const HAZARD = '#E61919'; // aviation/hazard red — the ONLY accent
const TERMINAL_GREEN = '#4AF626'; // exactly one element per screen

/** Poll interval for the telemetry feed. */
const POLL_MS = 10_000;
/** Minimum gap between WS-triggered refetches (throttle). */
const WS_REFETCH_MIN_MS = 2_000;

// ── Status derivation (exported for tests) ───────────────────────────────

export type BranchStatus = 'ONLINE' | 'DEGRADED' | 'OFFLINE';

/**
 * Derive the roster state from live health:
 *   ONLINE    — WS connected with ≥1 terminal
 *   DEGRADED  — WS connected but zero terminals (or sync disabled)
 *   OFFLINE   — no WS connection
 */
export function deriveBranchStatus(branch: BranchHealth): BranchStatus {
  if (!branch.online) return 'OFFLINE';
  if (branch.connected_terminals > 0 && branch.sync_enabled) return 'ONLINE';
  return 'DEGRADED';
}

/** Fleet sync-rate as a percentage of online branches (0–100). */
export function fleetSyncRate(branches: BranchHealth[]): number {
  if (branches.length === 0) return 0;
  const online = branches.filter(b => b.online).length;
  return (online / branches.length) * 100;
}

type FilterId = 'ALL' | 'ONLINE' | 'ALERT';
const FILTERS: FilterId[] = ['ALL', 'ONLINE', 'ALERT'];

// ── Status glyphs ─────────────────────────────────────────────────────────

const STATUS_META: Record<
  BranchStatus,
  { dot: string; badge: string; label: string }
> = {
  ONLINE: {
    dot: `bg-[#4AF626] animate--breathe`,
    badge: 'text-[#EAEAEA] border-[#EAEAEA]/60',
    label: 'ONLINE',
  },
  DEGRADED: {
    dot: 'bg-[#E61919] animate--breathe',
    badge: 'text-[#E61919] border-[#E61919]/70',
    label: 'DEGRADED',
  },
  OFFLINE: {
    dot: 'bg-[#EAEAEA]/25',
    badge: 'text-[#EAEAEA]/45 border-[#EAEAEA]/25',
    label: 'OFFLINE',
  },
};

// ── Component ─────────────────────────────────────────────────────────────

export default function BranchOverview() {
  const { t } = useTranslation();

  const [branches, setBranches] = useState<BranchHealth[] | null>(null);
  const [queue, setQueue] = useState<QueueSummary | null>(null);
  const [conflicts, setConflicts] = useState<ConflictStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [filter, setFilter] = useState<FilterId>('ALL');

  // Throttle WS-triggered refetches so a burst of entity events doesn't
  // hammer the dashboard endpoints.
  const lastWsRefetchRef = useRef(0);

  const refresh = useCallback(async ({ quiet = false }: { quiet?: boolean } = {}) => {
    if (!quiet) setLoading(true);
    const [health, queueRes, conflictRes] = await Promise.all([
      dashboard.getBranchesHealth(),
      dashboard.getQueueSummary(),
      dashboard.getConflictStats(),
    ]);

    if (health.ok && health.data) setBranches(health.data.branches);
    if (queueRes.ok && queueRes.data) setQueue(queueRes.data);
    if (conflictRes.ok && conflictRes.data) setConflicts(conflictRes.data);

    if (!health.ok) {
      setError(health.error || 'HTTP error');
      if (!quiet) setLoading(false);
      return;
    }
    setError(null);
    setLastUpdated(new Date());
    if (!quiet) setLoading(false);
  }, []);

  // Initial load + polling + focus refetch.
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

  // Best-effort push updates via the sync-events WS — polling covers the
  // case where the socket isn't reachable.
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

  // ── Derived telemetry ────────────────────────────────────────────────────

  const total = branches?.length ?? 0;
  const onlineCount = useMemo(
    () => (branches ?? []).filter(b => b.online).length,
    [branches],
  );
  const offlineCount = useMemo(
    () => (branches ?? []).filter(b => !b.online).length,
    [branches],
  );
  const rate = useMemo(() => fleetSyncRate(branches ?? []), [branches]);

  const visibleBranches = useMemo(() => {
    if (!branches) return [];
    switch (filter) {
      case 'ONLINE':
        return branches.filter(b => deriveBranchStatus(b) === 'ONLINE');
      case 'ALERT':
        return branches.filter(b => deriveBranchStatus(b) !== 'ONLINE');
      default:
        return branches;
    }
  }, [branches, filter]);

  const filterCounts = useMemo(() => {
    const alerts = (branches ?? []).filter(b => deriveBranchStatus(b) !== 'ONLINE').length;
    return { ALL: total, ONLINE: onlineCount, ALERT: alerts };
  }, [branches, total, onlineCount]);

  const onFilterKeyDown = (e: React.KeyboardEvent, index: number) => {
    let next = index;
    if (e.key === 'ArrowRight') next = (index + 1) % FILTERS.length;
    else if (e.key === 'ArrowLeft') next = (index - 1 + FILTERS.length) % FILTERS.length;
    else return;
    e.preventDefault();
    const id = FILTERS[next];
    setFilter(id);
    document.getElementById(`telemetry-filter-${id}`)?.focus();
  };

  const firstLoad = loading && branches === null;

  return (
    <PageLayout
      title={t('telemetry.title', 'Branch Overview')}
      background="bg-base-200/40"
    >
      <div
        role="region"
        aria-label="Branch sync telemetry"
        className="relative overflow-hidden border"
        style={{
          fontFamily: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
          backgroundColor: CRT,
          color: PHOSPHOR,
          borderColor: 'rgba(234, 234, 234, 0.15)',
        }}
      >
        {/* CRT scanlines — fixed to the panel, pointer-events none */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 z-0 opacity-40"
          style={{
            background:
              'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.35) 2px, rgba(0,0,0,0.35) 4px)',
          }}
        />
        {/* Mechanical noise — low-opacity grain */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 z-0 opacity-[0.06]"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
          }}
        />

        <div className="relative z-10">
          {/* ── Header — ASCII framing + metadata line ── */}
          <header className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-b border-[#EAEAEA]/15 px-4 py-2.5">
            <p className="text-[11px] font-bold tracking-[0.18em]" style={{ color: HAZARD }}>
              [ BRANCH OVERVIEW ]
            </p>
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/50 uppercase">
              UNIT / POS-CLOUD&nbsp;·&nbsp;REV / 2.6&nbsp;·&nbsp;MODE / TELEMETRY
            </p>
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/45 uppercase">
              {lastUpdated
                ? `POLL / ${lastUpdated.toLocaleTimeString()}`
                : 'POLL / AWAITING…'}
            </p>
          </header>

          {/* ── Error banner (only when we have nothing to show) ── */}
          {error && branches === null && (
            <div
              role="alert"
              className="flex flex-wrap items-center justify-between gap-3 border-b border-[#E61919]/50 bg-[#E61919]/10 px-4 py-3"
            >
              <p className="text-[11px] tracking-[0.14em] text-[#E61919] uppercase">
                &gt;&gt;&gt; LINK ERROR — {error}
              </p>
              <button
                type="button"
                onClick={() => refresh()}
                className="border border-[#E61919] px-3 py-1 text-[10px] font-bold tracking-[0.18em] text-[#E61919] uppercase transition-colors hover:bg-[#E61919] hover:text-[#0A0A0A] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E61919]"
              >
                RETRY LINK
              </button>
            </div>
          )}

          {/* ── Hero: fleet sync-rate (the ONE green element) + stat strip ── */}
          <section className="grid grid-cols-1 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] gap-px bg-[#EAEAEA]/15">
            {/* Fleet sync-rate readout */}
            <div className="bg-[#0A0A0A] p-5 sm:p-7">
              <p className="text-[10px] tracking-[0.2em] text-[#EAEAEA]/50 uppercase">
                Fleet Sync-Rate
              </p>
              <p
                data-testid="telemetry-rate"
                className="mt-2 font-bold leading-none tabular-nums"
                style={{ color: TERMINAL_GREEN, fontSize: 'clamp(2.75rem, 7vw, 5.5rem)' }}
              >
                {rate.toFixed(1)}
                <span className="text-[0.35em] align-top">%</span>
              </p>
              <p className="mt-2 text-[11px] tracking-[0.14em] text-[#EAEAEA]/60 uppercase">
                ONLINE {onlineCount} / {total} BRANCHES&nbsp;·&nbsp;{offlineCount} DARK
              </p>
            </div>

            {/* Stat strip — queued / conflicts / offline */}
            <dl data-testid="telemetry-stats" className="grid grid-cols-3 gap-px bg-[#EAEAEA]/15">
              {[
                { label: 'QUEUED', value: queue?.pending ?? '—' },
                { label: 'CONFLICTS', value: conflicts?.pending ?? '—' },
                { label: 'OFFLINE', value: offlineCount },
              ].map(stat => (
                <div
                  key={stat.label}
                  className="flex flex-col justify-between p-4 sm:p-5"
                  style={{ backgroundColor: PANEL }}
                >
                  <dt className="text-[10px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                    {stat.label}
                  </dt>
                  <dd className="mt-3 text-2xl sm:text-3xl font-bold text-[#EAEAEA] tabular-nums">
                    {stat.value}
                  </dd>
                </div>
              ))}
            </dl>
          </section>

          {/* ── Filter tabs ── */}
          <div
            role="tablist"
            aria-label="Filter roster by status"
            className="flex border-b border-[#EAEAEA]/15"
          >
            {FILTERS.map((id, i) => {
              const active = filter === id;
              const count = filterCounts[id];
              return (
                <button
                  key={id}
                  id={`telemetry-filter-${id}`}
                  role="tab"
                  aria-selected={active}
                  tabIndex={active ? 0 : -1}
                  onClick={() => setFilter(id)}
                  onKeyDown={e => onFilterKeyDown(e, i)}
                  className={`flex items-center gap-2 border-r border-[#EAEAEA]/15 px-4 py-2.5 text-[10px] font-bold tracking-[0.18em] uppercase transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-[#E61919] ${
                    active
                      ? 'bg-[#E61919] text-[#0A0A0A]'
                      : 'bg-[#0A0A0A] text-[#EAEAEA]/55 hover:bg-[#1a1a1a] hover:text-[#EAEAEA]'
                  }`}
                >
                  <span>{id}</span>
                  <span
                    className={`tabular-nums ${active ? 'text-[#0A0A0A]/70' : 'text-[#EAEAEA]/35'}`}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
            <span className="ms-auto hidden sm:flex items-center px-4 text-[10px] tracking-[0.14em] text-[#EAEAEA]/35 uppercase">
              &gt;&gt;&gt; live feed
            </span>
          </div>

          {/* ── Roster ── */}
          <div aria-live="polite">
            {firstLoad && (
              <ul className="divide-y divide-[#EAEAEA]/10">
                {[0, 1, 2].map(i => (
                  <li
                    key={i}
                    className="grid grid-cols-[0.5rem_1fr_auto] items-center gap-4 px-4 py-4 opacity-40"
                  >
                    <span className="h-2 w-2 rounded-none bg-[#EAEAEA]/30" />
                    <span className="text-xs tracking-[0.16em] text-[#EAEAEA]/60">
                      AWAITING TELEMETRY…
                    </span>
                    <span className="h-4 w-16 border border-[#EAEAEA]/20" />
                  </li>
                ))}
              </ul>
            )}

            {!firstLoad && error && branches === null && (
              <div className="px-4 py-10 text-center">
                <p className="text-[11px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                  &lt; SIGNAL LOST / NO TELEMETRY &gt;
                </p>
              </div>
            )}

            {!firstLoad && !error && branches !== null && branches.length === 0 && (
              <div className="px-4 py-10 text-center">
                <p className="text-[11px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                  &lt; NO BRANCHES REGISTERED / {t('telemetry.emptyHint', 'register a branch to begin syncing')} &gt;
                </p>
              </div>
            )}

            {branches !== null && branches.length > 0 && visibleBranches.length === 0 && (
              <div className="px-4 py-10 text-center">
                <p className="text-[11px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
                  &lt; NO BRANCHES MATCH {filter} / &gt;
                </p>
              </div>
            )}

            {branches !== null && visibleBranches.length > 0 && (
              <ul data-testid="telemetry-roster" className="divide-y divide-[#EAEAEA]/10">
                {visibleBranches.map(branch => {
                  const status = deriveBranchStatus(branch);
                  const meta = STATUS_META[status];
                  return (
                    <li
                      key={branch.id}
                      className="grid grid-cols-[0.5rem_minmax(0,1fr)_auto] items-center gap-x-4 gap-y-1 px-4 py-3.5 transition-colors hover:bg-[#161616] md:grid-cols-[0.5rem_minmax(0,1.4fr)_minmax(0,1fr)_minmax(0,1fr)_7rem]"
                    >
                      {/* Status dot */}
                      <span
                        aria-hidden="true"
                        className={`h-2 w-2 ${meta.dot}`}
                      />
                      {/* Identity */}
                      <div className="min-w-0">
                        <p className="truncate text-[13px] font-bold tracking-[0.12em] text-[#EAEAEA] uppercase">
                          {branch.name}
                        </p>
                        <p className="truncate text-[10px] tracking-[0.12em] text-[#EAEAEA]/45 uppercase">
                          {branch.code} · NODE / {branch.node_id || '—'} · {branch.pos_type}
                        </p>
                      </div>
                      {/* Terminals */}
                      <p className="hidden text-xs tracking-[0.14em] text-[#EAEAEA]/60 uppercase tabular-nums md:block">
                        {branch.connected_terminals} TERM
                      </p>
                      {/* Sync state */}
                      <p className="hidden text-xs tracking-[0.14em] text-[#EAEAEA]/60 uppercase md:block">
                        {branch.sync_enabled ? 'SYNC / ON' : 'SYNC / OFF'}
                      </p>
                      {/* Status badge */}
                      <span
                        className={`w-fit justify-self-start border px-2 py-0.5 text-[10px] font-bold tracking-[0.16em] md:justify-self-end ${meta.badge}`}
                      >
                        {status}
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* ── Footer — registration marks + meta ── */}
          <footer className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-t border-[#EAEAEA]/15 px-4 py-2.5">
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/40 uppercase">
              © 2026 FORMINT CLOUD ® · POS-CLOUD / SYNC MESH
            </p>
            <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/40 uppercase tabular-nums">
              {error
                ? 'LINK / STALE — POLLING'
                : lastUpdated
                  ? `UPDATED / ${lastUpdated.toLocaleTimeString()} · EVERY ${POLL_MS / 1000}S`
                  : 'UPDATED / —'}
            </p>
          </footer>
        </div>
      </div>
    </PageLayout>
  );
}
