import { useEffect, useMemo, useState } from 'react';

interface Pipeline { id: number; name: string; is_default: boolean; }
interface Stage { id: number; pipeline_id: number; name: string; stage_type: string; probability: number; order: number; color: string; }

const API = '/apis/core/resources';
const STAGE_TYPES = ['lead', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];

function csrfToken() { return document.cookie.match(/(?:^|; )csrftoken=([^;]*)/)?.[1] ?? ''; }
async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { credentials: 'include', ...init });
  if (!response.ok) throw new Error('Pipeline change could not be saved.');
  return response.status === 204 ? ({} as T) : response.json();
}

export default function PipelineManager() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [stages, setStages] = useState<Stage[]>([]);
  const [pipelineId, setPipelineId] = useState('');
  const [newPipeline, setNewPipeline] = useState('');
  const [stageName, setStageName] = useState('');
  const [stageType, setStageType] = useState('qualified');
  const [probability, setProbability] = useState('40');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const [pipelinePayload, stagePayload] = await Promise.all([
      json<{ results?: Pipeline[] }>('/pipelines/'),
      json<{ results?: Stage[] }>('/pipeline_stages/'),
    ]);
    const loadedPipelines = pipelinePayload.results ?? [];
    setPipelines(loadedPipelines);
    setStages(stagePayload.results ?? []);
    if (!pipelineId && loadedPipelines[0]) setPipelineId(String(loadedPipelines[0].id));
  };
  useEffect(() => { void load().catch((error) => setMessage(error instanceof Error ? error.message : 'Pipelines unavailable.')); }, []);

  const visibleStages = useMemo(() => stages.filter((stage) => String(stage.pipeline_id) === pipelineId).sort((a, b) => a.order - b.order), [stages, pipelineId]);
  const mutate = async (callback: () => Promise<void>, success: string) => {
    setBusy(true); setMessage('');
    try { await callback(); await load(); setMessage(success); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Pipeline change could not be saved.'); }
    finally { setBusy(false); }
  };
  const createPipeline = () => mutate(async () => {
    if (!newPipeline.trim()) throw new Error('Pipeline name is required.');
    const created = await json<Pipeline>('/pipelines/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify({ name: newPipeline.trim(), is_default: pipelines.length === 0, order: pipelines.length }) });
    setNewPipeline(''); setPipelineId(String(created.id));
  }, 'Pipeline created.');
  const createStage = () => mutate(async () => {
    if (!pipelineId || !stageName.trim()) throw new Error('Choose a pipeline and enter a stage name.');
    await json('/pipeline_stages/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify({ pipeline_id: Number(pipelineId), name: stageName.trim(), stage_type: stageType, probability: Number(probability), order: visibleStages.length, color: '#8A8A8A' }) });
    setStageName('');
  }, 'Stage created.');
  const updateStage = (stage: Stage, patch: Partial<Stage>) => mutate(async () => {
    await json(`/pipeline_stages/${stage.id}/`, { method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify(patch) });
  }, 'Stage updated.');
  const removeStage = (stage: Stage) => mutate(async () => {
    await json(`/pipeline_stages/${stage.id}/`, { method: 'DELETE', headers: { 'X-CSRFToken': csrfToken() } });
  }, 'Stage deleted.');
  const moveStage = (stage: Stage, direction: -1 | 1) => {
    const target = visibleStages[visibleStages.findIndex((item) => item.id === stage.id) + direction];
    if (!target) return;
    return mutate(async () => {
      await Promise.all([
        json(`/pipeline_stages/${stage.id}/`, { method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify({ order: target.order }) }),
        json(`/pipeline_stages/${target.id}/`, { method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify({ order: stage.order }) }),
      ]);
    }, 'Stage order updated.');
  };

  return <section className="loop-pipeline-manager" data-pipeline-manager aria-label="Pipeline manager">
    <div className="loop-pipeline-manager__head"><div><span className="loop-calendar__kicker">PIPELINE CONTROL</span><h2>Stages drive the kanban</h2></div><label htmlFor="pipeline-select">Pipeline<select id="pipeline-select" value={pipelineId} onChange={(event) => setPipelineId(event.target.value)}>{pipelines.map((pipeline) => <option value={pipeline.id} key={pipeline.id}>{pipeline.name}{pipeline.is_default ? ' · default' : ''}</option>)}</select></label></div>
    <div className="loop-pipeline-manager__grid"><form onSubmit={(event) => { event.preventDefault(); void createPipeline(); }}><span className="loop-calendar__kicker">NEW PIPELINE</span><label htmlFor="new-pipeline">Name<input id="new-pipeline" value={newPipeline} onChange={(event) => setNewPipeline(event.target.value)} placeholder="Enterprise sales" /></label><button className="loop-button" disabled={busy}>Create pipeline →</button></form><form onSubmit={(event) => { event.preventDefault(); void createStage(); }}><span className="loop-calendar__kicker">NEW STAGE</span><label htmlFor="stage-name">Name<input id="stage-name" value={stageName} onChange={(event) => setStageName(event.target.value)} placeholder="Security review" /></label><div className="loop-pipeline-manager__fields"><label htmlFor="stage-type">Type<select id="stage-type" value={stageType} onChange={(event) => setStageType(event.target.value)}>{STAGE_TYPES.map((type) => <option value={type} key={type}>{type.replace('_', ' ')}</option>)}</select></label><label htmlFor="stage-probability">Probability<input id="stage-probability" type="number" min="0" max="100" value={probability} onChange={(event) => setProbability(event.target.value)} /></label></div><button className="loop-button" disabled={busy || !pipelineId}>Add stage →</button></form></div>
    <div className="loop-pipeline-manager__stages">{visibleStages.length === 0 ? <p className="loop-calendar__empty">No stages in this pipeline yet.</p> : visibleStages.map((stage, index) => <article className="loop-pipeline-manager__stage" key={stage.id}><span className="loop-pipeline-manager__order">{String(index + 1).padStart(2, '0')}</span><input aria-label={`Stage ${stage.name}`} value={stage.name} onChange={(event) => setStages((current) => current.map((item) => item.id === stage.id ? { ...item, name: event.target.value } : item))} onBlur={(event) => void updateStage(stage, { name: event.target.value })} /><span className="loop-calendar__status">{stage.stage_type.replace('_', ' ')}</span><input className="loop-pipeline-manager__probability" aria-label={`${stage.name} probability`} type="number" min="0" max="100" value={stage.probability} onChange={(event) => setStages((current) => current.map((item) => item.id === stage.id ? { ...item, probability: Number(event.target.value) } : item))} onBlur={(event) => void updateStage(stage, { probability: Number(event.target.value) })} /><div><button type="button" onClick={() => void moveStage(stage, -1)} disabled={index === 0 || busy}>↑</button><button type="button" onClick={() => void moveStage(stage, 1)} disabled={index === visibleStages.length - 1 || busy}>↓</button><button type="button" onClick={() => void removeStage(stage)} disabled={busy}>Delete</button></div></article>)}</div>
    {message && <p className="loop-calendar__message" role="status">{message}</p>}
  </section>;
}
