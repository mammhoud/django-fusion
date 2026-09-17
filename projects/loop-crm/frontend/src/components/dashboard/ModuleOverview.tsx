import { useEffect, useMemo, useState } from 'react';

type ModuleId = 'crm' | 'marketing' | 'finance' | 'attribution';

type Counts = {
  companies: number;
  contacts: number;
  deals: number;
  pipelines: number;
  campaigns: number;
  channels: number;
  posts: number;
  touchpoints: number;
  invoices: number;
  payments: number;
  revenue: number;
};

type DashboardPayload = { data?: { counts?: Partial<Counts> } };

type ModuleOverviewProps = { module: ModuleId };

const MODULES: Record<ModuleId, {
  label: string;
  title: string;
  description: string;
  metrics: Array<{ key: keyof Counts; label: string; href: string }>;
  actions: Array<{ label: string; href: string }>;
}> = {
  crm: {
    label: 'CRM / LIVE GRAPH',
    title: 'Relationship graph → pipeline',
    description: 'Accounts, people, opportunities, and stage movement from the current workspace.',
    metrics: [
      { key: 'companies', label: 'Companies', href: '/crm/companies/' },
      { key: 'contacts', label: 'Contacts', href: '/crm/contacts/' },
      { key: 'deals', label: 'Deals', href: '/crm/deals/' },
      { key: 'pipelines', label: 'Pipelines', href: '/crm/pipelines/' },
    ],
    actions: [
      { label: 'Open kanban', href: '/crm/deals/' },
      { label: 'Configure stages', href: '/crm/pipelines/' },
      { label: 'Import records', href: '/settings/import/' },
    ],
  },
  marketing: {
    label: 'MARKETING / LIVE QUEUE',
    title: 'Plan → approve → publish',
    description: 'Content operations backed by real campaigns, channels, and scheduled posts.',
    metrics: [
      { key: 'campaigns', label: 'Campaigns', href: '/marketing/campaigns/' },
      { key: 'channels', label: 'Channels', href: '/marketing/channels/' },
      { key: 'posts', label: 'Posts', href: '/marketing/calendar/' },
      { key: 'touchpoints', label: 'Touchpoints', href: '/attribution/touchpoints/' },
    ],
    actions: [
      { label: 'Open calendar', href: '/marketing/calendar/' },
      { label: 'Review approvals', href: '/marketing/approvals/' },
      { label: 'Connect channel', href: '/marketing/channels/' },
    ],
  },
  finance: {
    label: 'FINANCE / LIVE LEDGER',
    title: 'Invoice → payment → revenue',
    description: 'Receivables and recognized revenue tied back to companies, deals, and campaigns.',
    metrics: [
      { key: 'invoices', label: 'Invoices', href: '/finance/invoices/' },
      { key: 'payments', label: 'Payments', href: '/finance/payments/' },
      { key: 'revenue', label: 'Revenue events', href: '/finance/revenue/' },
      { key: 'deals', label: 'Source deals', href: '/crm/deals/' },
    ],
    actions: [
      { label: 'Open invoices', href: '/finance/invoices/' },
      { label: 'Review revenue', href: '/finance/revenue/' },
      { label: 'Ledger settings', href: '/settings/ledger/' },
    ],
  },
  attribution: {
    label: 'ATTRIBUTION / LIVE CREDIT',
    title: 'Touch → influence → revenue',
    description: 'Campaign and social touchpoints credited to the current workspace pipeline.',
    metrics: [
      { key: 'touchpoints', label: 'Touchpoints', href: '/attribution/touchpoints/' },
      { key: 'deals', label: 'Deals', href: '/crm/deals/' },
      { key: 'revenue', label: 'Revenue events', href: '/finance/revenue/' },
      { key: 'campaigns', label: 'Campaigns', href: '/marketing/campaigns/' },
    ],
    actions: [
      { label: 'Open touchpoints', href: '/attribution/touchpoints/' },
      { label: 'Open reports', href: '/attribution/reports/' },
      { label: 'Review campaigns', href: '/marketing/campaigns/' },
    ],
  },
};

const formatNumber = (value: number) => new Intl.NumberFormat('en-US').format(value);

export default function ModuleOverview({ module }: ModuleOverviewProps) {
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [counts, setCounts] = useState<Partial<Counts>>({});
  const config = MODULES[module];

  const load = () => {
    setStatus('loading');
    void fetch('/apis/core/dashboard/', { credentials: 'include', headers: { Accept: 'application/json' } })
      .then(async (response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return (await response.json()) as DashboardPayload;
      })
      .then((payload) => {
        setCounts(payload.data?.counts ?? {});
        setStatus('ready');
      })
      .catch((error) => {
        console.error(`Module overview ${module} load failed`, error);
        setStatus('error');
      });
  };

  useEffect(() => { load(); }, [module]);

  const total = useMemo(
    () => config.metrics.reduce((sum, metric) => sum + Number(counts[metric.key] ?? 0), 0),
    [config.metrics, counts],
  );

  if (status === 'loading') {
    return <section className="loop-module-overview loop-module-overview--loading" aria-busy="true" aria-label={`Loading ${config.title}`}><div className="loop-module-overview__loading-bar" /><div className="loop-module-overview__loading-grid"><i /><i /><i /><i /></div></section>;
  }

  if (status === 'error') {
    return <section className="loop-module-overview loop-module-overview--error" role="alert"><strong>{config.label} DATA UNAVAILABLE</strong><p>The workspace summary did not respond. No fallback records were loaded.</p><button type="button" onClick={load}>Retry request</button></section>;
  }

  return (
    <section className="loop-module-overview" aria-label={`${config.title} live overview`}>
      <div className="loop-module-overview__head">
        <div><span className="loop-module-overview__kicker">{config.label}</span><h2>{config.title}</h2><p>{config.description}</p></div>
        <div className="loop-module-overview__total"><strong>{formatNumber(total)}</strong><span>live records in view</span></div>
      </div>
      <div className="loop-module-overview__metrics">
        {config.metrics.map((metric) => <a href={metric.href} key={metric.key}><span>{metric.label}</span><strong>{formatNumber(Number(counts[metric.key] ?? 0))}</strong><b aria-hidden="true">↗</b></a>)}
      </div>
      <nav className="loop-module-overview__actions" aria-label={`${config.title} actions`}>
        {config.actions.map((action) => <a href={action.href} key={action.href}>{action.label}<b aria-hidden="true">→</b></a>)}
      </nav>
    </section>
  );
}
