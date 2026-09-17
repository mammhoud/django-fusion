import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';

interface LedgerSettings {
  currency: string;
  timezone: string;
  workspace?: { name: string };
}

interface IntegrationSummary {
  id: string;
  label: string;
  capabilities: string[];
}

interface WorkflowSummary {
  count: number;
}

interface AiSummary {
  consent: boolean;
  providers: Array<{ label: string; configured: boolean }>;
}

function csrfToken(): string {
  return document.cookie.match(/(?:^|; )csrftoken=([^;]*)/)?.[1] ?? '';
}

export default function WorkspaceControls() {
  const [ledger, setLedger] = useState<LedgerSettings | null>(null);
  const [integrations, setIntegrations] = useState<IntegrationSummary[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowSummary>({ count: 0 });
  const [ai, setAi] = useState<AiSummary | null>(null);
  const [currency, setCurrency] = useState('USD');
  const [timezone, setTimezone] = useState('UTC');
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void Promise.all([
      fetch('/apis/core/settings/ledger/', { credentials: 'include' }).then((res) => res.ok ? res.json() : null),
      fetch('/apis/core/integrations/', { credentials: 'include' }).then((res) => res.ok ? res.json() : { results: [] }),
      fetch('/apis/core/workflows/', { credentials: 'include' }).then((res) => res.ok ? res.json() : { results: [] }),
      fetch('/apis/core/ai/', { credentials: 'include' }).then((res) => res.ok ? res.json() : null),
    ]).then(([ledgerPayload, integrationPayload, workflowPayload, aiPayload]) => {
      if (ledgerPayload) {
        setLedger(ledgerPayload);
        setCurrency(ledgerPayload.currency ?? 'USD');
        setTimezone(ledgerPayload.timezone ?? 'UTC');
      }
      setIntegrations(integrationPayload.results ?? []);
      setWorkflows({ count: (workflowPayload.results ?? []).length });
      if (aiPayload) setAi(aiPayload);
    }).catch(() => setMessage('Workspace controls are temporarily unavailable.'));
  }, []);

  const saveLedger = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      const response = await fetch('/apis/core/settings/ledger/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
        body: JSON.stringify({ currency, timezone }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? payload.currency ?? 'Ledger settings could not be saved.');
      setLedger({ ...ledger, ...payload });
      setMessage('Ledger defaults saved and audited.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Ledger settings could not be saved.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="loop-controls" data-control-surface="workspace" aria-label="Workspace controls">
      <div className="loop-controls__grid">
        <form className="loop-controls__panel" data-ledger-settings-form onSubmit={(event) => void saveLedger(event)}>
          <span className="loop-controls__kicker">FINANCE / LEDGER DEFAULTS</span>
          <h2>Ledger settings</h2>
          <p>These defaults drive new invoices, payments, and revenue reports.</p>
          <label htmlFor="ledger-currency">Currency<input id="ledger-currency" name="currency" value={currency} maxLength={3} onChange={(event) => setCurrency(event.target.value.toUpperCase())} /></label>
          <label htmlFor="ledger-timezone">Timezone<input id="ledger-timezone" name="timezone" value={timezone} maxLength={50} onChange={(event) => setTimezone(event.target.value)} /></label>
          <button className="loop-button loop-button--primary" disabled={saving || !ledger} type="submit">{saving ? 'Saving…' : 'Save ledger defaults →'}</button>
        </form>
        <div className="loop-controls__panel">
          <span className="loop-controls__kicker">AI / AUTOMATION CONTROL</span>
          <h2>Integration readiness</h2>
          <div className="loop-controls__status"><b>{ai?.providers[0]?.configured ? 'AI provider configured' : 'AI provider not configured'}</b><span>{ai?.consent ? 'Workspace consent enabled' : 'Consent required per member'}</span></div>
          <div className="loop-controls__status"><b>{workflows.count} workflow definitions</b><span>Executed through the Dramatiq worker boundary</span></div>
          <a className="loop-button loop-button--quiet" href="/ai/">Open AI Hub →</a>
          <a className="loop-button loop-button--quiet" href="/settings/workflows/">Manage automation →</a>
        </div>
      </div>
      <div className="loop-controls__panel loop-controls__panel--wide">
        <span className="loop-controls__kicker">CONNECTOR CATALOG</span>
        <h2>{integrations.length} integration families available</h2>
        <div className="loop-controls__chips">{integrations.map((integration) => <span key={integration.id}>{integration.label} · {integration.capabilities.join(' / ')}</span>)}</div>
        <a className="loop-button loop-button--quiet" href="/settings/integrations/">Open integration settings →</a>
      </div>
      {message && <p className="loop-controls__message" role="status">{message}</p>}
    </section>
  );
}
