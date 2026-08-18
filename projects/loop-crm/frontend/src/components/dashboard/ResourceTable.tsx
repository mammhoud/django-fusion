/**
 * ResourceTable — live fusion table for a Bolt API resource.
 *
 * Fetches the schema-aware table contract from the API
 * (``/bolt/tables/{resource}`` canonical, ``/api/v1/tables/{resource}/``
 * compatibility fallback) and renders it with the Loop-CRM tactical
 * telemetry design: mono uppercase headers with `+` ticks, hard corners,
 * red accent rows, and type-driven cells (money/date/pill/link).
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';
import StoreProvider from '@/components/StoreProvider';
import { useLiveSync } from '@/lib/useLiveSync';
import type { RootState } from '@/store';

const useAppSelector = useSelector.withTypes<RootState>();

export interface TableHeader {
  key: string;
  label: string;
  type: 'text' | 'money' | 'date' | 'pill' | 'link';
  sortable?: boolean;
}

export interface ResourceTablePayload {
  resource: string;
  headers: TableHeader[];
  rows: string[][];
  count: number;
}

interface ResourceTableProps {
  resource: string;
  title?: string;
  kicker?: string;
}

const num = new Intl.NumberFormat('en-US');

function Cell({ value, type }: { value: string; type: TableHeader['type'] }) {
  if (type === 'pill') {
    return <span className="loop-res-table__pill">{value || '—'}</span>;
  }
  if (type === 'link') {
    if (!value || value === '—') return <span>—</span>;
    return (
      <a className="loop-res-table__link" href={value} target="_blank" rel="noreferrer">
        Open ↗
      </a>
    );
  }
  return <span className={type === 'money' ? 'loop-res-table__money' : undefined}>{value}</span>;
}

function Table({ resource, title, kicker }: ResourceTableProps) {
  const apiPrefix = useAppSelector((state) => state.config.apiPrefix);
  const fallbackPrefix = useAppSelector((state) => state.config.fallbackApiPrefix);
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [payload, setPayload] = useState<ResourceTablePayload | null>(null);
  const { synced, flash } = useLiveSync();
  const requestedRef = useRef<string | null>(null);

  const load = useCallback(async () => {
    // The bolt road routes ``/tables/{resource}`` (no trailing slash); the
    // compatibility road routes ``/tables/<resource>/``. Shape the path to
    // each prefix so the canonical road is used when available.
    const path = (prefix: string) =>
      prefix === '/bolt' ? `/tables/${resource}` : `/tables/${resource}/`;
    try {
      let response = await fetch(`${apiPrefix}${path(apiPrefix)}`);
      if (!response.ok && fallbackPrefix !== apiPrefix) {
        response = await fetch(`${fallbackPrefix}${path(fallbackPrefix)}`);
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = (await response.json()) as ResourceTablePayload;
      setPayload(data);
      setStatus('ready');
      flash();
    } catch (err) {
      console.error(`ResourceTable ${resource} load failed`, err);
      setStatus('error');
    }
  }, [apiPrefix, fallbackPrefix, resource, flash]);

  // Load on mount and whenever the realtime "synced" flag flips, but never
  // re-request the same resource twice for one event batch.
  useEffect(() => {
    void load();
    if (!synced) return;
    if (requestedRef.current === resource) return;
    requestedRef.current = resource;
    const timer = setTimeout(() => {
      void load();
      requestedRef.current = null;
    }, 250);
    return () => clearTimeout(timer);
  }, [load, synced, resource]);

  if (status === 'error') {
    return (
      <section className="loop-res-table" aria-label={`${title ?? resource} table`}>
        <div className="loop-res-table__head">
          <span className="loop-res-table__kicker">{kicker ?? 'live table'}</span>
          <span className="loop-res-table__count">&gt;&gt; offline</span>
        </div>
        <div className="loop-res-table__error">The {resource} table did not respond. Check that the backend is running.</div>
      </section>
    );
  }

  if (status === 'loading' || !payload) {
    return (
      <section className="loop-res-table" aria-label={`${title ?? resource} table`} aria-busy="true">
        <div className="loop-res-table__head">
          <span className="loop-res-table__kicker">{kicker ?? 'live table'}</span>
          <span className="loop-res-table__count htmx-indicator">loading</span>
        </div>
        <div className="loop-res-table__skeleton" aria-hidden="true">
          <i />
          <i />
          <i />
          <i />
        </div>
      </section>
    );
  }

  return (
    <section className="loop-res-table" aria-label={`${title ?? resource} table`} aria-live="polite">
      <div className="loop-res-table__head">
        <span className="loop-res-table__kicker">{kicker ?? 'live table'}</span>
        <span className="loop-res-table__count">
          &gt;&gt; {num.format(payload.count)} record{payload.count === 1 ? '' : 's'}
          {synced && <em className="loop-res-table__flash">synced</em>}
        </span>
      </div>
      <div className="loop-res-table__wrap">
        <table className="loop-res-table__grid">
          <thead>
            <tr>
              {payload.headers.map((header) => (
                <th key={header.key} scope="col">
                  {header.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {payload.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {payload.headers.map((header, colIndex) => (
                  <td key={header.key} data-type={header.type}>
                    <Cell value={row[colIndex]} type={header.type} />
                  </td>
                ))}
              </tr>
            ))}
            {payload.rows.length === 0 && (
              <tr>
                <td colSpan={payload.headers.length} className="loop-res-table__empty">
                  <strong>No {resource} yet.</strong>
                  <span>Records created through the app or API appear here.</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// StoreProvider is the bridge each data-heavy island mounts around itself
// (Astro can't nest <slot/> inside a React component, so the provider lives in
// the island, not the layout). Without it, `useSelector` throws during the
// static build because there is no Redux context to read from.
export default function ResourceTable(props: ResourceTableProps) {
  return (
    <StoreProvider>
      <Table {...props} />
    </StoreProvider>
  );
}
