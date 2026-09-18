import type { FormEvent } from 'react';
import { useEffect, useState } from 'react';

interface Operation {
  id: string;
  label: string;
  description: string;
}

interface Catalog {
  consent: boolean;
  operations: Operation[];
  providers: Array<{ id: string; label: string; configured: boolean; transport: string }>;
}

interface Result {
  status: string;
  provider?: string;
  operation?: string;
  reason?: string;
  output?: Record<string, unknown>;
}

function csrfToken(): string {
  return document.cookie.match(/(?:^|; )csrftoken=([^;]*)/)?.[1] ?? '';
}

export default function AiHub() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [operation, setOperation] = useState('lead_score');
  const [brief, setBrief] = useState('');
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  const load = () => {
    void fetch('/apis/core/ai/', { credentials: 'include' })
      .then((response) => (response.ok ? response.json() as Promise<Catalog> : Promise.reject(new Error('AI catalog unavailable'))))
      .then(setCatalog)
      .catch(() => setMessage('AI catalog unavailable. The workspace remains fully usable without AI.'));
  };

  useEffect(load, []);

  const toggleConsent = async () => {
    if (!catalog) return;
    const response = await fetch('/apis/core/ai/consent/', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
      body: JSON.stringify({ enabled: !catalog.consent }),
    });
    if (response.ok) setCatalog({ ...catalog, consent: !catalog.consent });
    else setMessage('Consent could not be updated. Refresh the page and try again.');
  };

  const run = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setMessage('');
    setResult(null);
    try {
      const response = await fetch(`/apis/core/ai/${operation}/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
        body: JSON.stringify({ context: { brief: brief.trim() } }),
      });
      const payload = await response.json() as Result;
      setResult(payload);
    } catch {
      setMessage('The AI operation could not be reached. No CRM record was changed.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="loop-ai-island" aria-label="AI Hub operations">
      <div className="loop-ai-island__head">
        <div><span className="loop-ai-kicker">LIVE CONTROL SURFACE</span><strong>{catalog?.providers[0]?.label ?? 'Provider'} · {catalog?.providers[0]?.configured ? 'configured' : 'not configured'}</strong></div>
        <button className="loop-ai-consent" type="button" onClick={() => void toggleConsent()} disabled={!catalog}>
          {catalog?.consent ? 'Disable workspace consent' : 'Enable workspace consent'}
        </button>
      </div>
      {!catalog?.consent && <p className="loop-ai-notice">Enable workspace consent before submitting CRM context to an AI provider.</p>}
      <form className="loop-ai-form" onSubmit={(event) => void run(event)}>
        <label htmlFor="ai-operation">Operation<select id="ai-operation" value={operation} onChange={(event) => setOperation(event.target.value)}>{(catalog?.operations ?? []).map((item) => <option value={item.id} key={item.id}>{item.label}</option>)}</select></label>
        <label htmlFor="ai-brief">Brief<textarea id="ai-brief" value={brief} onChange={(event) => setBrief(event.target.value)} placeholder="Paste a bounded lead, opportunity, or campaign brief…" rows={6} maxLength={12000} /></label>
        <button className="loop-button loop-button--primary" type="submit" disabled={busy || !catalog?.consent || !brief.trim()}>{busy ? 'Running…' : 'Run assisted operation →'}</button>
      </form>
      {message && <p className="loop-ai-message" role="status">{message}</p>}
      {result && <section className={`loop-ai-result loop-ai-result--${result.status}`} aria-live="polite"><span className="loop-ai-kicker">{result.status} · {result.provider}</span>{result.reason && <p>{result.reason}</p>}{result.output && <pre>{JSON.stringify(result.output, null, 2)}</pre>}<small>Human review is required before taking any external action.</small></section>}
    </section>
  );
}
