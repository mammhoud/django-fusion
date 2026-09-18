import { useEffect, useMemo, useState } from 'react';

type Stage = 'lead' | 'qualified' | 'won';

interface Deal {
  id: number;
  company: string;
  value: string;
  stage: Stage;
}

const INITIAL: Deal[] = [
  { id: 1, company: 'Halcyon Labs', value: '$18.4k', stage: 'won' },
  { id: 2, company: 'Northwind', value: '$9.2k', stage: 'won' },
  { id: 3, company: 'Sable & Co', value: '$24.1k', stage: 'qualified' },
  { id: 4, company: 'Meadowbank', value: '$6.8k', stage: 'qualified' },
  { id: 5, company: 'Copperline', value: '$12.6k', stage: 'lead' },
  { id: 6, company: 'Fieldstone', value: '$8.9k', stage: 'lead' },
];

const STAGE_ORDER: Stage[] = ['lead', 'qualified', 'won'];
const STAGE_LABEL: Record<Stage, string> = { lead: 'Lead', qualified: 'Qualified', won: 'Won' };

const parseK = (v: string) => Number(v.replace(/[$k]/g, ''));

export default function PipelineDemo() {
  const [deals, setDeals] = useState<Deal[]>(INITIAL);
  const [recognized, setRecognized] = useState(27.6);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduced(media.matches);
  }, []);

  useEffect(() => {
    if (reduced) return;
    const timer = window.setInterval(() => {
      setDeals((prev) => {
        const next = prev.map((deal) => {
          if (deal.stage === 'won') return deal;
          const idx = STAGE_ORDER.indexOf(deal.stage);
          return { ...deal, stage: STAGE_ORDER[idx + 1] ?? 'won' };
        });
        const newlyWon = next.filter((d) => d.stage === 'won').length;
        if (newlyWon === 1) {
          setRecognized((r) => r + parseK(next[0].value));
        }
        return next;
      });
      if (Math.random() > 0.35) {
        setDeals((prev) => {
          const idx = prev.findIndex((d) => d.stage !== 'won');
          if (idx === -1) return prev;
          const lead = prev[idx];
          if (lead.stage === 'qualified') {
            return prev.map((d) => (d.id === lead.id ? { ...d, stage: 'won' as Stage } : d));
          }
          return prev.map((d) => (d.id === lead.id ? { ...d, stage: 'qualified' as Stage } : d));
        });
      }
    }, 2600);
    return () => window.clearInterval(timer);
  }, [reduced]);

  const columns = useMemo(
    () =>
      STAGE_ORDER.map((stage) => ({
        stage,
        items: deals.filter((d) => d.stage === stage),
        total: deals.filter((d) => d.stage === stage).reduce((sum, d) => sum + parseK(d.value), 0),
      })),
    [deals],
  );

  return (
    <div className="loop-pipeline">
      <div className="loop-pipeline__header">
        <div>
          <span className="loop-pipeline__kicker">RevOps · live pipeline</span>
          <strong>Deal flow</strong>
        </div>
        <div className="loop-pipeline__revenue">
          <span>Recognized revenue</span>
          <strong>${recognized.toFixed(1)}k</strong>
        </div>
      </div>
      <div className="loop-pipeline__board">
        {columns.map(({ stage, items, total }) => (
          <div className="loop-pipeline__col" key={stage}>
            <div className="loop-pipeline__col-head">
              <span className={`loop-pipeline__dot loop-pipeline__dot--${stage}`} />
              <span>{STAGE_LABEL[stage]}</span>
              <span className="loop-pipeline__total">${total.toFixed(1)}k</span>
            </div>
            <div className="loop-pipeline__col-body">
              {items.map((deal, i) => (
                <div className="loop-pipeline__card" key={deal.id} style={{ animationDelay: `${i * 90}ms` }}>
                  <span>{deal.company}</span>
                  <strong>{deal.value}</strong>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="loop-pipeline__foot">
        <span>campaign · summer launch</span>
        <span>attribution · time-decay</span>
      </div>
    </div>
  );
}
