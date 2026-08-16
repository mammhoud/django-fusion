import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import gsap from 'gsap';
import { Draggable } from 'gsap/Draggable';
import StoreProvider from '@/components/StoreProvider';
import { useWorkspaceRealtime, type WorkspaceEvent } from '@/lib/useWorkspaceRealtime';
import { useLiveSync } from '@/lib/useLiveSync';
import { setActivePipeline, setPipelines, moveDeal, type Pipeline } from '@/store/slices/crmSlice';

gsap.registerPlugin(Draggable);

// Typed Redux hooks (mirror of the store module's AppDispatch/RootState).
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '@/store';
import type { AppDispatch } from '@/store';
const useAppDispatch = useDispatch.withTypes<AppDispatch>();
const useAppSelector = useSelector.withTypes<RootState>();

const BOARD_URL = '/api/v1/board/';
const MOVE_URL = (dealId: number) => `/api/v1/deals/${dealId}/stage/`;

// Django's csrftoken cookie is readable from JS (CSRF_COOKIE_HTTPONLY=False),
// so the kanban can echo it back on the move mutation. Mirrors the
// precis-landing proxied-Django convention.
function readCsrfToken(): string {
  if (typeof document === 'undefined') return '';
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : '';
}

const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const formatMoney = (raw: string | number) => money.format(Number(raw));

// The stage order within a pipeline: used by the keyboard/reduced-motion
// chevrons to compute the previous/next stage without a graph lookup.
export function stageOrder(pipeline: Pipeline): number[] {
  return [...pipeline.stages].sort((a, b) => a.order - b.order).map((stage) => stage.id);
}

function Board() {
  const dispatch = useAppDispatch();
  const pipelines = useAppSelector((state) => state.crm.pipelines);
  const activePipelineId = useAppSelector((state) => state.crm.activePipelineId);
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [reduced, setReduced] = useState(false);
  const [focusStageId, setFocusStageId] = useState<number | null>(null);
  const boardRef = useRef<HTMLDivElement>(null);
  const { synced, flash } = useLiveSync();

  const pipeline = useMemo(
    () => pipelines.find((item) => item.id === activePipelineId) ?? pipelines[0],
    [pipelines, activePipelineId],
  );

  // Load the board from the compatibility API road (proxied by Astro).
  // ``silent`` refreshes keep the board interactive (no skeleton flash) when
  // a realtime mutation event arrives.
  const loadBoard = useCallback(async (silent = false) => {
    try {
      const res = await fetch(BOARD_URL);
      if (!res.ok) throw new Error(`Board request failed (${res.status})`);
      const payload = await res.json();
      dispatch(setPipelines(payload.results ?? []));
      if (!silent) {
        // Deep-link support: /crm/deals/?pipeline=<id>&stage=<id> (used by the
        // RevOps dashboard funnel) opens the board with that stage in focus.
        const params = new URLSearchParams(window.location.search);
        const pipelineParam = Number(params.get('pipeline'));
        const stageParam = Number(params.get('stage'));
        if (pipelineParam && (payload.results ?? []).some((item: { id: number }) => item.id === pipelineParam)) {
          dispatch(setActivePipeline(pipelineParam));
        }
        if (stageParam) setFocusStageId(stageParam);
      }
      setStatus('ready');
    } catch (err) {
      if (!silent) setStatus('error');
      console.error('Pipeline board load failed', err);
    }
  }, [dispatch]);

  useEffect(() => {
    void loadBoard();
  }, [loadBoard]);

  // Live updates: refresh the board when a deal or pipeline mutates in this
  // workspace (own drags are already optimistic; this keeps other sessions and
  // API-road mutations in sync).
  useWorkspaceRealtime(
    () => {
      flash();
      void loadBoard(true);
    },
    {
      filter: (event: WorkspaceEvent) =>
        event.event.startsWith('resource.') && ['deals', 'pipelines'].includes(String(event.data?.resource)),
    },
  );

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduced(media.matches);
  }, []);

  // Once the board renders, bring the focused stage column into view.
  useEffect(() => {
    if (status !== 'ready' || !focusStageId || !boardRef.current) return;
    const col = boardRef.current.querySelector<HTMLElement>(`[data-stage-id="${focusStageId}"]`);
    if (!col) {
      // The stage is not in the active pipeline — clear the stale focus.
      setFocusStageId(null);
      return;
    }
    col.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', inline: 'center', block: 'nearest' });
  }, [status, focusStageId, pipeline?.id, reduced]);

  // Move a deal between stages; optimistic in the store, rolled back on error.
  const move = async (dealId: number, fromStageId: number, toStageId: number) => {
    if (fromStageId === toStageId || saving) return;
    const snapshot = pipelines;
    dispatch(moveDeal({ dealId, fromStageId, toStageId }));
    setSaving(true);
    setErrorMsg(null);
    try {
      const res = await fetch(MOVE_URL(dealId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': readCsrfToken(),
        },
        body: JSON.stringify({ stage_id: toStageId }),
      });
      if (!res.ok) throw new Error(`Move rejected (${res.status})`);
    } catch (err) {
      dispatch(setPipelines(snapshot));
      setErrorMsg('Move failed — the deal snapped back. Try again.');
      console.error('Deal move failed', err);
    } finally {
      setSaving(false);
    }
  };

  // GSAP drag physics for pointer users. Column membership is decided by the
  // pointer coordinates against column bounding rects, so a drop always lands
  // on the column the card is actually over (never on the dragged card itself).
  useEffect(() => {
    if (reduced || status !== 'ready' || !boardRef.current) return;
    const root = boardRef.current;
    const columnEls = Array.from(root.querySelectorAll<HTMLElement>('[data-stage-id]'));
    const cards = Array.from(root.querySelectorAll<HTMLElement>('[data-deal-id]'));
    const instances = cards.map((card) => {
      return Draggable.create(card, {
        type: 'x,y',
        cursor: 'grab',
        zIndexBoost: true,
        dragResistance: 0.12,
        onDragStart() {
          card.classList.add('is-dragging');
        },
        onDragEnd(event: DragEvent) {
          card.classList.remove('is-dragging');
          const dealId = Number(card.dataset.dealId);
          const fromStageId = Number(card.dataset.stageId);
          const x = event.clientX ?? 0;
          const y = event.clientY ?? 0;
          const target = columnEls.find((el) => {
            const rect = el.getBoundingClientRect();
            return x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom;
          });
          const toStageId = target ? Number(target.dataset.stageId) : fromStageId;
          if (toStageId !== fromStageId) {
            void move(dealId, fromStageId, toStageId);
          } else {
            gsap.to(card, { x: 0, y: 0, duration: 0.55, ease: 'elastic.out(1, 0.55)' });
          }
        },
      });
    });
    return () => {
      instances.forEach((instance) => instance[0]?.kill());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reduced, status, pipeline?.id, pipelines]);

  if (status === 'loading') {
    return (
      <section className="loop-board loop-board--skeleton" aria-busy="true" aria-label="Loading pipeline board">
        <div className="loop-board__rail"><span /><span /><span /></div>
        <div className="loop-board__grid">
          {[0, 1, 2, 3].map((i) => (
            <div className="loop-board__col" key={i}>
              <div className="loop-board__col-head"><span className="loop-board__skeleton" /><span className="loop-board__skeleton" /></div>
              <div className="loop-board__col-body">{<div className="loop-board__card loop-board__skeleton" />}</div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (status === 'error') {
    return (
      <section className="loop-board loop-board--error">
        <strong>Could not load the pipeline board.</strong>
        <p>Check that the backend is running, then try again.</p>
        <button type="button" onClick={() => { setStatus('loading'); window.location.reload(); }}>
          Retry
        </button>
      </section>
    );
  }

  if (!pipeline) {
    return (
      <section className="loop-board loop-board--error">
        <strong>No pipeline yet.</strong>
        <p>Create a pipeline with stages to start dragging deals.</p>
      </section>
    );
  }

  const order = stageOrder(pipeline);
  const columns = pipeline.stages
    .map((stage) => ({ ...stage, order: order.indexOf(stage.id) }))
    .sort((a, b) => a.order - b.order);

  const stageTotal = (stageId: number) =>
    columns.find((stage) => stage.id === stageId)?.deals.reduce((sum, deal) => sum + Number(deal.value), 0) ?? 0;

  return (
    <section className={focusStageId ? 'loop-board loop-board--focused' : 'loop-board'} ref={boardRef} aria-label={`${pipeline.name} kanban board`}>
      <div className="loop-board__rail">
        <span className="loop-board__kicker">Pipeline</span>
        {pipelines.length > 1 ? (
          <div className="loop-board__tabs" role="tablist" aria-label="Pipelines">
            {pipelines.map((item) => (
              <button
                type="button"
                role="tab"
                aria-selected={item.id === pipeline.id}
                className={item.id === pipeline.id ? 'is-active' : ''}
                onClick={() => dispatch(setActivePipeline(item.id))}
                key={item.id}
              >
                {item.name}
              </button>
            ))}
          </div>
        ) : (
          <strong className="loop-board__title">{pipeline.name}</strong>
        )}
        {saving && <span className="loop-board__saving">saving…</span>}
        {errorMsg && <span className="loop-board__error-msg" role="alert">{errorMsg}</span>}
        <span
          className="loop-live-sync"
          data-synced={synced ? 'true' : 'false'}
          role="status"
          aria-live="polite"
        >
          <span className="loop-live-sync__dot" aria-hidden="true" />
          <span className="loop-live-sync__label">{synced ? 'synced' : 'live'}</span>
        </span>
        {focusStageId && (
          <button type="button" className="loop-board__focus-chip" onClick={() => setFocusStageId(null)}>
            Focused on {columns.find((stage) => stage.id === focusStageId)?.name ?? 'stage'} · clear
          </button>
        )}
      </div>

      <div className="loop-board__grid">
        {columns.map((stage) => (
          <div
            className={focusStageId === stage.id ? 'loop-board__col is-focused' : 'loop-board__col'}
            data-stage-id={stage.id}
            key={stage.id}
          >
            <div className="loop-board__col-head">
              <span
                className="loop-board__dot"
                style={stage.color ? { background: stage.color } : undefined}
                aria-hidden="true"
              />
              <span className="loop-board__col-name">{stage.name}</span>
              <span className="loop-board__col-meta">
                {stage.deals.length} · {stage.probability}%
              </span>
              <span className="loop-board__col-total">{formatMoney(stageTotal(stage.id))}</span>
            </div>
            <div className="loop-board__col-body">
              {stage.deals.length === 0 && <div className="loop-board__drop-hint">Drop a deal here</div>}
              {stage.deals.map((deal) => {
                const pos = order.indexOf(stage.id);
                const prev = pos > 0 ? columns[pos - 1].id : null;
                const next = pos < columns.length - 1 ? columns[pos + 1].id : null;
                return (
                  <article className="loop-board__card" data-deal-id={deal.id} data-stage-id={stage.id} key={deal.id} draggable={false}>
                    <div className="loop-board__card-top">
                      <span className="loop-board__company">{deal.company}</span>
                      <strong className="loop-board__value">{formatMoney(deal.value)}</strong>
                    </div>
                    <h4 className="loop-board__deal">{deal.name}</h4>
                    <div className="loop-board__card-foot">
                      <span className="loop-board__owner">{deal.owner || 'Unassigned'}</span>
                      <span className="loop-board__stepper">
                        <button
                          type="button"
                          aria-label={`Move ${deal.name} back to previous stage`}
                          disabled={prev === null}
                          onClick={() => prev !== null && void move(deal.id, stage.id, prev)}
                        >
                          ‹
                        </button>
                        <button
                          type="button"
                          aria-label={`Move ${deal.name} forward to next stage`}
                          disabled={next === null}
                          onClick={() => next !== null && void move(deal.id, stage.id, next)}
                        >
                          ›
                        </button>
                      </span>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

// StoreProvider is the bridge each data-heavy island mounts around itself
// (Astro can't nest <slot/> inside a React component, so the provider lives
// in the island, not the layout).
export default function PipelineBoard() {
  return (
    <StoreProvider>
      <Board />
    </StoreProvider>
  );
}
