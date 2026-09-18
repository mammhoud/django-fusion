/**
 * ReportCatalog — the /reports/ list of available reports.
 *
 * Reads ``/apis/reports/`` and renders each report with its owner module,
 * availability state, and route. Reports that are not yet backed by live data
 * are marked "pending" rather than rendered as fake aggregates.
 */
import { useEffect, useState } from 'react';

interface ReportItem {
  id: string;
  name: string;
  module: string;
  href: string;
  description: string;
  available: boolean;
}

export default function ReportCatalog() {
  const [status, setStatus] = useState<'loading' | 'ready'>('loading');
  const [reports, setReports] = useState<ReportItem[]>([]);

  useEffect(() => {
    void fetch('/apis/reports/')
      .then((res) => (res.ok ? res.json() : { results: [] }))
      .then((payload) => {
        setReports(payload.results ?? []);
        setStatus('ready');
      })
      .catch(() => setStatus('ready'));
  }, []);

  if (status === 'loading') {
    return (
      <section className="loop-reports" aria-busy="true" aria-label="Loading report catalog">
        <div className="loop-reports__skeleton" aria-hidden="true"><i /><i /><i /></div>
      </section>
    );
  }

  return (
    <section className="loop-reports" aria-label="Report catalog">
      {reports.length === 0 ? (
        <div className="loop-reports__empty">
          <strong>No reports yet.</strong>
          <p>The report catalog did not respond. Check that the backend is running.</p>
        </div>
      ) : (
        <div className="loop-reports__grid" role="list">
          {reports.map((report) => (
            <a
              className={`loop-reports__card${report.available ? '' : ' is-pending'}`}
              href={report.href}
              role="listitem"
              key={report.id}
              aria-disabled={!report.available}
            >
              <header className="loop-reports__head">
                <span className="loop-reports__kicker">{report.module}</span>
                <span className={`loop-reports__state${report.available ? '' : ' is-pending'}`}>
                  {report.available ? 'live' : 'pending'}
                </span>
              </header>
              <h3>{report.name}</h3>
              <p>{report.description}</p>
              <span className="loop-reports__arrow" aria-hidden="true">→</span>
            </a>
          ))}
        </div>
      )}
    </section>
  );
}
