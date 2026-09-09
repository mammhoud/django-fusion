import { useEffect, useMemo, useState } from 'react';

interface Employee {
  id: number;
  name: string;
  email: string;
  role: string;
  title: string;
  metrics: { activities: number; deals: number; posts: number; invoices: number };
}

interface Report {
  employee: { id: number; name: string; email: string; role: string; title: string };
  metrics: { activities: number; deals: number; deal_value: string; posts: number; published_posts: number; invoices: number; invoice_value: string };
}

const formatRole = (role: string) => role.replaceAll('_', ' ');

export default function EmployeeDirectory() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<Report | null>(null);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');

  useEffect(() => {
    fetch('/apis/core/employees/', { credentials: 'include' })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<{ results: Employee[] }>;
      })
      .then((payload) => { setEmployees(payload.results ?? []); setStatus('ready'); })
      .catch(() => setStatus('error'));
  }, []);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return employees;
    return employees.filter((employee) => `${employee.name} ${employee.email} ${employee.role} ${employee.title}`.toLowerCase().includes(needle));
  }, [employees, query]);

  const openReport = async (employee: Employee) => {
    const response = await fetch(`/apis/core/employees/${employee.id}/report/`, { credentials: 'include' });
    if (response.ok) setSelected(await response.json() as Report);
  };

  if (status === 'loading') return <section className="loop-people" aria-busy="true"><div className="loop-people__skeleton" /><div className="loop-people__skeleton" /><div className="loop-people__skeleton" /></section>;
  if (status === 'error') return <section className="loop-people loop-people--empty"><strong>People data unavailable.</strong><p>The workspace employee endpoint did not respond.</p></section>;

  return (
    <section className="loop-people" aria-label="Workspace people directory">
      <div className="loop-people__toolbar"><div><span className="loop-people__kicker">LIVE MEMBER DIRECTORY</span><strong>{employees.length} workspace member{employees.length === 1 ? '' : 's'}</strong></div><input aria-label="Search people" placeholder="Search name, role, or email" value={query} onChange={(event) => setQuery(event.target.value)} /></div>
      {filtered.length === 0 ? <div className="loop-people--empty"><strong>No matching people.</strong><p>Members appear here when they belong to the current workspace.</p></div> : <div className="loop-people__grid" role="list">{filtered.map((employee) => <article className="loop-people__card" role="listitem" key={employee.id}><div className="loop-people__identity"><span className="loop-people__avatar">{employee.name.slice(0, 2).toUpperCase()}</span><div><h2>{employee.name}</h2><p>{employee.title || formatRole(employee.role)}</p></div></div><span className="loop-people__role">{formatRole(employee.role)}</span><dl><div><dt>Activities</dt><dd>{employee.metrics.activities}</dd></div><div><dt>Deals</dt><dd>{employee.metrics.deals}</dd></div><div><dt>Posts</dt><dd>{employee.metrics.posts}</dd></div><div><dt>Invoices</dt><dd>{employee.metrics.invoices}</dd></div></dl><button type="button" onClick={() => void openReport(employee)}>OPEN PERFORMANCE DOSSIER →</button></article>)}</div>}
      {selected && <div className="loop-people__report" role="dialog" aria-modal="true" aria-label={`${selected.employee.name} performance dossier`}><button type="button" className="loop-people__close" onClick={() => setSelected(null)} aria-label="Close report">×</button><span className="loop-people__kicker">PERFORMANCE DOSSIER</span><h2>{selected.employee.name}</h2><p>{selected.employee.title || formatRole(selected.employee.role)} · {selected.employee.email}</p><div className="loop-people__metrics">{Object.entries(selected.metrics).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{value}</strong></div>)}</div></div>}
    </section>
  );
}
