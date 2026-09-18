import { useEffect, useState } from 'react';

interface Result { type: string; title: string; meta?: string; href: string }

const ROUTES: Result[] = [
  { type: 'route', title: 'Overview', href: '/overview/' },
  { type: 'route', title: 'Companies', href: '/crm/companies/' },
  { type: 'route', title: 'Contacts', href: '/crm/contacts/' },
  { type: 'route', title: 'Deals', href: '/crm/deals/' },
  { type: 'route', title: 'Content calendar', href: '/marketing/calendar/' },
  { type: 'route', title: 'Approvals', href: '/marketing/approvals/' },
  { type: 'route', title: 'Finance invoices', href: '/finance/invoices/' },
  { type: 'route', title: 'AI Hub', href: '/ai/' },
  { type: 'route', title: 'Reports', href: '/reports/' },
  { type: 'route', title: 'Workspace settings', href: '/settings/' },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>(ROUTES);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); setOpen(true); }
      if (event.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    const needle = query.trim();
    const local = ROUTES.filter((route) => route.title.toLowerCase().includes(needle.toLowerCase()));
    if (needle.length < 2) { setResults(local); return; }
    fetch(`/apis/core/search/?q=${encodeURIComponent(needle)}`, { credentials: 'include' })
      .then((response) => response.ok ? response.json() as Promise<{ results: Result[] }> : { results: [] })
      .then((payload) => setResults([...local, ...(payload.results ?? [])]))
      .catch(() => setResults(local));
  }, [query]);

  if (!open) return null;
  return <div className="loop-palette" role="dialog" aria-modal="true" aria-label="Command palette"><button className="loop-palette__backdrop" type="button" aria-label="Close command palette" onClick={() => setOpen(false)} /><div className="loop-palette__panel"><div className="loop-palette__head"><span>COMMAND / SEARCH</span><kbd>ESC</kbd></div><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search routes, companies, contacts, deals…" /><div className="loop-palette__results">{results.length === 0 ? <p>No matching records.</p> : results.slice(0, 12).map((result, index) => <a href={result.href} key={`${result.href}-${index}`}><span>{result.type}</span><strong>{result.title}</strong><small>{result.meta}</small><b>↗</b></a>)}</div></div></div>;
}
