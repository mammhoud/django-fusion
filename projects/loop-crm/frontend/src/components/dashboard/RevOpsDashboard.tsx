import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import StoreProvider from '@/components/StoreProvider';
import { useWorkspaceRealtime, type WorkspaceEvent } from '@/lib/useWorkspaceRealtime';
import { useLiveSync } from '@/lib/useLiveSync';
import type { RootState } from '@/store';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

const useAppSelector = useSelector.withTypes<RootState>();

// ── Payload contracts (compatibility road, mirrors backend views) ───────────

interface DashboardCounts {
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
}

interface DashboardPayload {
  data: { counts: DashboardCounts; workflow_count: number };
}

interface DealRow {
  id: number;
  name: string;
  company: string;
  value: string;
  owner: string;
  campaign: string | null;
}

interface StageRow {
  id: number;
  name: string;
  stage_type: string;
  color: string;
  probability: number;
  order: number;
  deals: DealRow[];
}

interface PipelineRow {
  id: number;
  name: string;
  stages: StageRow[];
}

interface TrendPoint {
  month: string;
  label: string;
  total: string;
  events: number;
  pos_total: string;
  deal_total: string;
}

interface RevenueTrendPayload {
  results: TrendPoint[];
  count: number;
  grand_total: string;
  pos_total: string;
  deal_total: string;
}

const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const num = (value: number) => new Intl.NumberFormat('en-US').format(value);

function StatCard({ label, value, hint, href }: { label: string; value: string; hint?: string; href?: string }) {
  const body = (
    <>
      <CardHeader>
        <CardTitle className="text-muted-foreground">{label}</CardTitle>
        {hint && <CardDescription>{hint}</CardDescription>}
      </CardHeader>
      <CardContent>
        <span className="loop-dash__number">{value}</span>
      </CardContent>
    </>
  );
  return (
    <Card className="loop-dash__stat" size="sm">
      {href ? (
        <a className="loop-dash__stat-link" href={href} aria-label={`Open ${label}`}>
          {body}
        </a>
      ) : (
        body
      )}
    </Card>
  );
}

function Board() {
  const apiPrefix = useAppSelector((state) => state.config.fallbackApiPrefix);
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [counts, setCounts] = useState<DashboardCounts | null>(null);
  const [workflows, setWorkflows] = useState(0);
  const [pipeline, setPipeline] = useState<PipelineRow | null>(null);
  const [trend, setTrend] = useState<RevenueTrendPayload | null>(null);
  const { synced, flash } = useLiveSync();

  // Load counts + funnel + trend. ``silent`` refreshes keep the dashboard
  // interactive (no skeleton flash) when a realtime mutation event arrives.
  const loadDashboard = useCallback(async (silent = false) => {
    try {
      const [dashboardRes, boardRes, trendRes] = await Promise.allSettled([
        fetch(`${apiPrefix}/dashboard/`),
        fetch(`${apiPrefix}/board/`),
        fetch(`${apiPrefix}/revenue/trend/`),
      ]);
      if (dashboardRes.status === 'rejected') throw dashboardRes.reason;
      const dashboard = (await (dashboardRes.value as Response).json()) as DashboardPayload;
      setCounts(dashboard.data.counts ?? null);
      setWorkflows(dashboard.data.workflow_count ?? 0);
      if (boardRes.status === 'fulfilled' && (boardRes.value as Response).ok) {
        const board = (await (boardRes.value as Response).json()) as { results: PipelineRow[] };
        const candidates = (board.results ?? []).filter((item) => item.stages.length > 0);
        setPipeline(candidates.sort((a, b) => b.stages.length - a.stages.length)[0] ?? null);
      }
      if (trendRes.status === 'fulfilled' && (trendRes.value as Response).ok) {
        const payload = (await (trendRes.value as Response).json()) as RevenueTrendPayload;
        setTrend(payload.results?.length ? payload : null);
      }
      setStatus('ready');
    } catch (err) {
      if (!silent) setStatus('error');
      console.error('RevOps dashboard load failed', err);
    }
  }, [apiPrefix]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  // Live updates: every resource mutation and POS ingest changes at least one
  // KPI/funnel/trend, so refresh the whole dashboard silently on any event.
  useWorkspaceRealtime(
    () => {
      flash();
      void loadDashboard(true);
    },
    {
      filter: (event: WorkspaceEvent) =>
        event.event.startsWith('resource.') || event.event === 'pos.sales.ingested',
    },
  );

  const funnel = useMemo(() => {
    if (!pipeline) return null;
    const stages = [...pipeline.stages].sort((a, b) => a.order - b.order);
    const totals = stages.map((stage) => stage.deals.reduce((sum, deal) => sum + Number(deal.value), 0));
    const maxTotal = Math.max(1, ...totals);
    return stages.map((stage, index) => ({
      stage,
      total: totals[index],
      width: Math.max(6, Math.round((totals[index] / maxTotal) * 100)),
    }));
  }, [pipeline]);

  if (status === 'loading') {
    return (
      <div className="loop-dash" aria-busy="true" aria-label="Loading RevOps dashboard">
        <div className="loop-dash__grid">
          <Skeleton className="loop-dash__skeleton loop-dash__skeleton--wide" />
          <Skeleton className="loop-dash__skeleton" />
          <Skeleton className="loop-dash__skeleton" />
          <Skeleton className="loop-dash__skeleton loop-dash__skeleton--tall" />
          <Skeleton className="loop-dash__skeleton loop-dash__skeleton--stack" />
          <Skeleton className="loop-dash__skeleton loop-dash__skeleton--stack" />
        </div>
      </div>
    );
  }

  if (status === 'error' || !counts) {
    return (
      <div className="loop-dash loop-dash__error">
        <strong>Could not load the dashboard.</strong>
        <p>The /api/v1/dashboard endpoint did not respond. Check that the backend is running.</p>
        <Button type="button" onClick={() => { setStatus('loading'); window.location.reload(); }}>Retry</Button>
      </div>
    );
  }

  return (
    <TooltipProvider delayDuration={120}>
      <div className="loop-dash">
        <div className="loop-dash__head">
          <span
            className="loop-live-sync"
            data-synced={synced ? 'true' : 'false'}
            role="status"
            aria-live="polite"
          >
            <span className="loop-live-sync__dot" aria-hidden="true" />
            <span className="loop-live-sync__label">{synced ? 'synced' : 'live'}</span>
          </span>
        </div>
        <div className="loop-dash__kpis">
          <StatCard label="Deals in pipeline" value={num(counts.deals)} hint={`${num(counts.pipelines)} configured pipelines`} href="/crm/deals/" />
          <StatCard label="Posts scheduled" value={num(counts.posts)} hint={`${num(counts.channels)} connected channels`} href="/marketing/calendar/" />
          <StatCard label="Revenue events" value={num(counts.revenue)} hint={`${num(counts.invoices)} invoices · ${num(counts.payments)} payments`} href="/finance/revenue/" />
          <StatCard label="Attribution touchpoints" value={num(counts.touchpoints)} hint="Social touches credited to deals" href="/attribution/touchpoints/" />
          <StatCard label="Workflows" value={num(workflows)} hint="Cross-module automations" href="/settings/workflows/" />
        </div>

        <div className="loop-dash__grid">
          <Card className="loop-dash__funnel">
            <CardHeader>
              <CardTitle>Deal flow</CardTitle>
              <CardDescription>{pipeline ? `${pipeline.name} · stage totals from live deals` : 'No pipeline with stages yet'}</CardDescription>
              <CardAction>
                <Button asChild size="sm" variant="outline"><a href="/crm/deals/">Open board</a></Button>
              </CardAction>
            </CardHeader>
            <CardContent className="loop-dash__funnel-body">
              {funnel ? (
                funnel.map(({ stage, total, width }) => (
                  <a
                    className="loop-dash__stage loop-dash__stage--link"
                    key={stage.id}
                    href={`/crm/deals/?pipeline=${pipeline?.id}&stage=${stage.id}`}
                    aria-label={`Open the deals board filtered to ${stage.name}`}
                  >
                    <div className="loop-dash__stage-head">
                      <span className="loop-dash__stage-name" style={stage.color ? { color: stage.color } : undefined}>{stage.name}</span>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span tabIndex={0}><Badge variant="secondary">{stage.deals.length} deal{stage.deals.length === 1 ? '' : 's'}</Badge></span>
                        </TooltipTrigger>
                        <TooltipContent>Winning probability {stage.probability}%</TooltipContent>
                      </Tooltip>
                      <span className="loop-dash__stage-total">{money.format(total)}</span>
                      <span className="loop-dash__stage-arrow" aria-hidden="true">→</span>
                    </div>
                    <div className="loop-dash__track" aria-hidden="true">
                      <span className="loop-dash__fill" style={{ width: `${width}%`, background: stage.color || undefined }} />
                    </div>
                  </a>
                ))
              ) : (
                <p className="loop-dash__empty">Create a pipeline with stages and deals to see the funnel.</p>
              )}
            </CardContent>
          </Card>

          <div className="loop-dash__stack">
            <Card size="sm">
              <CardHeader>
                <CardTitle>Revenue trail</CardTitle>
                <CardDescription>Closed pipeline becomes cash, in order</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="loop-dash__trail">
                  <span><b>{num(counts.invoices)}</b> invoices</span>
                  <Separator orientation="vertical" />
                  <span><b>{num(counts.payments)}</b> payments</span>
                  <Separator orientation="vertical" />
                  <span><b>{num(counts.revenue)}</b> recognized</span>
                </div>
              </CardContent>
            </Card>
            <Card size="sm">
              <CardHeader>
                <CardTitle>Operation scale</CardTitle>
                <CardDescription>Accounts, people, and content under management</CardDescription>
              </CardHeader>
              <CardContent className="loop-dash__scale">
                <span><b>{num(counts.companies)}</b> companies</span>
                <span><b>{num(counts.contacts)}</b> contacts</span>
                <span><b>{num(counts.campaigns)}</b> campaigns</span>
                <span><b>{num(counts.channels)}</b> channels</span>
              </CardContent>
            </Card>
          </div>
        </div>

        <Card className="loop-dash__trend">
          <CardHeader>
            <CardTitle>Recognized revenue</CardTitle>
            <CardDescription>Monthly totals, trailing six months</CardDescription>
            <CardAction>
              <Button asChild size="sm" variant="outline"><a href="/finance/revenue/">Revenue ledger</a></Button>
            </CardAction>
          </CardHeader>
          <CardContent>
            {trend ? (
              <>
                <div className="loop-dash__trend-head">
                  <span className="loop-dash__trend-total">{money.format(Number(trend.grand_total))}</span>
                  <span className="loop-dash__trend-meta">{(() => { const n = trend.results.reduce((sum, point) => sum + point.events, 0); return `${num(n)} event${n === 1 ? '' : 's'} recognized`; })()}</span>
                </div>
                <div className="loop-dash__trend-split" aria-label="Recognized revenue split by source">
                  <span className="loop-dash__trend-split-deal"><i aria-hidden="true" /> Deal <b>{money.format(Number(trend.deal_total))}</b></span>
                  <span className="loop-dash__trend-split-pos"><i aria-hidden="true" /> POS <b>{money.format(Number(trend.pos_total))}</b></span>
                </div>
                <div className="loop-dash__trend-bars" role="group" aria-label="Monthly recognized revenue by source, trailing six months">
                  {(() => {
                    const max = Math.max(1, ...trend.results.map((point) => Number(point.total)));
                    return trend.results.map((point) => {
                      const dealH = Math.round((Number(point.deal_total) / max) * 100);
                      const posH = Math.round((Number(point.pos_total) / max) * 100);
                      return (
                        <div className="loop-dash__trend-col" key={point.month}>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <span className="loop-dash__trend-bar-wrap" tabIndex={0}>
                                {dealH > 0 && <span className="loop-dash__trend-bar loop-dash__trend-bar--deal" style={{ height: `${dealH}%` }} />}
                                {posH > 0 && <span className="loop-dash__trend-bar loop-dash__trend-bar--pos" style={{ height: `${posH}%` }} />}
                              </span>
                            </TooltipTrigger>
                            <TooltipContent>
                              {point.label} · {money.format(Number(point.total))} ({money.format(Number(point.deal_total))} deal, {money.format(Number(point.pos_total))} POS)
                            </TooltipContent>
                          </Tooltip>
                          <span className="loop-dash__trend-label">{point.label}</span>
                        </div>
                      );
                    });
                  })()}
                </div>
              </>
            ) : (
              <p className="loop-dash__empty">No revenue events yet. Win a deal and recognize its revenue to see the trend.</p>
            )}
          </CardContent>
        </Card>

        <div className="loop-dash__actions">
          <Button asChild variant="outline"><a href="/crm/deals/">Deals board</a></Button>
          <Button asChild variant="outline"><a href="/marketing/calendar/">Content calendar</a></Button>
          <Button asChild variant="outline"><a href="/finance/invoices/">Invoices</a></Button>
          <Button asChild variant="outline"><a href="/settings/workflows/">Workflows</a></Button>
        </div>
      </div>
    </TooltipProvider>
  );
}

// StoreProvider is the bridge each data-heavy island mounts around itself.
export default function RevOpsDashboard() {
  return (
    <StoreProvider>
      <Board />
    </StoreProvider>
  );
}
