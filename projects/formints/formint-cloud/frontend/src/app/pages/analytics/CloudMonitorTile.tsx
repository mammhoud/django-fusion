/**
 * POS Cloud — Cloud Backup Monitor Tile
 * =====================================
 * Consumes the `@formints/client` monitor module (via `lib/monitor`) and
 * renders database status, last backup, and sync-queue depth in the same
 * CRT telemetry aesthetic as BranchOverview.
 *
 * Liveness: initial fetch + 10s polling + refetch on window focus.
 * Renders a degraded/offline state when the monitor endpoint is unreachable.
 */

import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { monitorApi } from '../../../lib/monitor';
import type { MonitorStatus } from '@formints/client';

// ── Tactical Telemetry palette (mirrors BranchOverview) ────────────────────
const CRT = '#0A0A0A'; // deactivated CRT substrate
const PANEL = '#101010'; // instrument panel
const PHOSPHOR = '#EAEAEA'; // white phosphor text
const HAZARD = '#E61919'; // hazard red — the ONLY accent
const TERMINAL_GREEN = '#4AF626'; // exactly one green element per screen

/** Poll interval for the monitor feed. */
const POLL_MS = 10_000;

/** Human-readable database state for the tile. */
export function deriveDatabaseState(status: MonitorStatus | null): 'OK' | 'ERROR' | 'AWAITING' {
  if (!status) return 'AWAITING';
  return status.database === 'ok' ? 'OK' : 'ERROR';
}

export default function CloudMonitorTile() {
  const { t } = useTranslation();
  const [status, setStatus] = useState<MonitorStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const refresh = useCallback(async ({ quiet = false }: { quiet?: boolean } = {}) => {
    try {
      const next = await monitorApi().status();
      setStatus(next);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'HTTP error');
      if (!quiet) setStatus(null);
    }
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

  const db = deriveDatabaseState(status);
  const backup = status?.last_backup ?? null;
  const queue = status?.sync_queue_depth ?? null;

  return (
    <section
      role="region"
      aria-label="Cloud backup monitor"
      className="border-t border-[#EAEAEA]/15"
      style={{ backgroundColor: CRT, color: PHOSPHOR }}
    >
      {/* ── Header — ASCII framing ── */}
      <header className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-b border-[#EAEAEA]/15 px-4 py-2.5">
        <p className="text-[11px] font-bold tracking-[0.18em]" style={{ color: HAZARD }}>
          [ {t('cloudMonitor.title', 'CLOUD BACKUP MONITOR')} ]
        </p>
        <p className="text-[10px] tracking-[0.12em] text-[#EAEAEA]/50 uppercase">
          {t('cloudMonitor.db', 'DB')} / {db}
          {error
            ? ` · ${t('cloudMonitor.linkError', 'LINK ERROR')}`
            : lastUpdated
              ? ` · ${lastUpdated.toLocaleTimeString()}`
              : ` · ${t('cloudMonitor.awaiting', 'AWAITING…')}`}
        </p>
      </header>

      {/* ── Stat strip — db / last backup / queue depth ── */}
      <dl
        data-testid="cloud-monitor-stats"
        className="grid grid-cols-3 gap-px bg-[#EAEAEA]/15"
      >
        {/* Database status — the ONE green element */}
        <div className="flex flex-col justify-between p-4 sm:p-5" style={{ backgroundColor: PANEL }}>
          <dt className="text-[10px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
            {t('cloudMonitor.database', 'DATABASE')}
          </dt>
          <dd
            data-testid="cloud-monitor-db"
            className="mt-3 text-2xl sm:text-3xl font-bold tabular-nums"
            style={{ color: db === 'OK' ? TERMINAL_GREEN : HAZARD }}
          >
            {db}
          </dd>
        </div>

        {/* Last backup */}
        <div className="flex flex-col justify-between p-4 sm:p-5" style={{ backgroundColor: PANEL }}>
          <dt className="text-[10px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
            {t('cloudMonitor.lastBackup', 'LAST BACKUP')}
          </dt>
          <dd className="mt-3 min-w-0 text-[13px] font-bold text-[#EAEAEA]">
            {error && !status ? (
              <span className="text-[10px] tracking-[0.14em] text-[#EAEAEA]/45 uppercase">
                {t('cloudMonitor.noSignal', 'NO SIGNAL')}
              </span>
            ) : backup ? (
              <span className="block truncate uppercase tracking-[0.08em]">
                {backup.filename}
                <span
                  className={`ms-2 text-[10px] tracking-[0.16em] uppercase ${
                    backup.status === 'success' ? 'text-[#4AF626]/80' : 'text-[#E61919]'
                  }`}
                >
                  {backup.status}
                </span>
              </span>
            ) : (
              <span className="text-[10px] tracking-[0.14em] text-[#EAEAEA]/45 uppercase">
                {t('cloudMonitor.noneRecorded', 'NONE / NOT RECORDED')}
              </span>
            )}
          </dd>
        </div>

        {/* Sync queue depth */}
        <div className="flex flex-col justify-between p-4 sm:p-5" style={{ backgroundColor: PANEL }}>
          <dt className="text-[10px] tracking-[0.18em] text-[#EAEAEA]/50 uppercase">
            {t('cloudMonitor.queueDepth', 'QUEUE DEPTH')}
          </dt>
          <dd
            data-testid="cloud-monitor-queue"
            className="mt-3 text-2xl sm:text-3xl font-bold text-[#EAEAEA] tabular-nums"
          >
            {queue === null ? '—' : queue}
          </dd>
        </div>
      </dl>
    </section>
  );
}
