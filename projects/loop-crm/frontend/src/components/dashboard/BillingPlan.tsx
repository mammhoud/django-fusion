/**
 * BillingPlan — the workspace's subscription state + plan catalog.
 *
 * Reads ``/apis/billing/account/`` (current plan, status, seats) and
 * ``/apis/billing/plans/`` (the public tier catalog) and renders the tactical
 * telemetry treatment. Checkout routes to ``/billing/checkout/``; "Manage
 * billing" routes to the Stripe portal. When billing is not configured the
 * island shows an honest state instead of erroring.
 */
import { useEffect, useState } from 'react';

interface PlanItem {
  slug: string;
  name: string;
  price: string;
  period: string;
  seat_limit: number;
  feature_flags: Record<string, boolean>;
  checkout: string;
}

interface AccountPayload {
  configured: boolean;
  status: string;
  plan: { slug: string; name: string; period: string; seat_limit: number } | null;
  seats: number;
  trial_ends_at: string | null;
}

const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

function centsToDollars(cents: number): string {
  return money.format(cents / 100);
}

export default function BillingPlan() {
  const [status, setStatus] = useState<'loading' | 'ready'>('loading');
  const [account, setAccount] = useState<AccountPayload | null>(null);
  const [plans, setPlans] = useState<PlanItem[]>([]);

  useEffect(() => {
    void Promise.allSettled([
      fetch('/apis/billing/account/').then((r) => (r.ok ? r.json() : null)),
      fetch('/apis/billing/plans/').then((r) => (r.ok ? r.json() : null)),
    ]).then(([accountRes, plansRes]) => {
      if (accountRes.status === 'fulfilled' && accountRes.value) setAccount(accountRes.value);
      if (plansRes.status === 'fulfilled' && plansRes.value) setPlans(plansRes.value.plans ?? []);
      setStatus('ready');
    });
  }, []);

  if (status === 'loading') {
    return (
      <section className="loop-billing" aria-busy="true" aria-label="Loading billing plan">
        <div className="loop-billing__skeleton" aria-hidden="true"><i /><i /><i /></div>
      </section>
    );
  }

  const currentSlug = account?.plan?.slug;
  const configured = account?.configured ?? false;

  return (
    <section className="loop-billing" aria-label="Billing plan">
      <div className="loop-billing__state">
        <span className="loop-billing__kicker">Current plan</span>
        <strong className="loop-billing__plan">{account?.plan?.name ?? 'No plan'}</strong>
        <span className={`loop-billing__status loop-billing__status--${account?.status ?? 'none'}`}>
          {account?.status ?? 'none'}
        </span>
        <span className="loop-billing__meta">
          {account?.seats ?? 0} seat{(account?.seats ?? 0) === 1 ? '' : 's'} in use
          {account?.plan ? ` · limit ${account.plan.seat_limit}` : ''}
        </span>
      </div>

      {!configured && (
        <p className="loop-billing__notice">
          Billing is not configured. Set Stripe keys in the environment to enable checkout and the customer portal.
        </p>
      )}

      <div className="loop-billing__grid" role="list" aria-label="Available plans">
        {plans.map((plan) => (
          <article
            className={`loop-billing__card${plan.slug === currentSlug ? ' is-current' : ''}`}
            role="listitem"
            key={plan.slug}
          >
            <header className="loop-billing__card-head">
              <span className="loop-billing__kicker">{plan.period}</span>
              <h3>{plan.name}</h3>
            </header>
            <span className="loop-billing__price">{centsToDollars(Number(plan.price) * 100)}<small>/mo</small></span>
            <ul className="loop-billing__features">
              <li>{plan.seat_limit} seats</li>
              {Object.entries(plan.feature_flags)
                .filter(([, on]) => on)
                .map(([flag]) => (
                  <li key={flag}>{flag.replace(/_/g, ' ')}</li>
                ))}
            </ul>
            {plan.slug === currentSlug ? (
              <span className="loop-billing__current">current</span>
            ) : (
              <a className="loop-billing__cta" href={plan.checkout} data-method="post" aria-disabled={!configured}>
                {configured ? 'Start checkout' : 'Unavailable'}
              </a>
            )}
          </article>
        ))}
      </div>

      {configured && account && (
        <a className="loop-billing__manage" href="/billing/portal/">
          Manage billing & invoice history in Stripe →
        </a>
      )}
    </section>
  );
}
