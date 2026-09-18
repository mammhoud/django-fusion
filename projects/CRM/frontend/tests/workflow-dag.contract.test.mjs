import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('DAG canvas ships a trigger-rooted node/edge graph', async () => {
  const template = await read('../backend/templates/dashboard/partials/workflow_dag_editor.html');
  assert.match(template, /id="workflow-dag"/);
  assert.match(template, /id="dag-canvas"/);
  assert.match(template, /id="dag-edges"/);
  assert.match(template, /data-triggers/);
});

test('DAG canvas supports branching via port-to-port edge creation', async () => {
  const template = await read('../backend/templates/dashboard/partials/workflow_dag_editor.html');
  assert.match(template, /loop-dag-port--out/);
  assert.match(template, /loop-dag-port--in/);
  assert.match(template, /startConnect/);
  assert.match(template, /addEdge/);
  assert.match(template, /removeEdge/);
});

test('DAG canvas blocks cycles and persists through the graph endpoint', async () => {
  const template = await read('../backend/templates/dashboard/partials/workflow_dag_editor.html');
  assert.match(template, /wouldCycle/);
  assert.match(template, /\/fragments\/workflows\//);
  assert.match(template, /\/graph\//);
  assert.match(template, /nodes: nodes, edges: edges/);
});

test('Graph normalization enforces acyclicity and trigger rooting on the server', async () => {
  const workflows = await read('../backend/apps/core/workflows.py');
  assert.match(workflows, /def normalize_workflow_graph/);
  assert.match(workflows, /def _topological_order/);
  assert.match(workflows, /contains a cycle/);
  assert.match(workflows, /exactly one trigger node/);
  assert.match(workflows, /def graph_from_actions/);
});

test('WorkflowDefinition stores the canvas graph as a JSON column', async () => {
  const models = await read('../backend/apps/core/models.py');
  assert.match(models, /graph = models\.JSONField/);
});

test('The graph fragment route is mounted on the browser road', async () => {
  const urls = await read('../backend/urls.py');
  assert.match(urls, /fragments\/workflows\/<int:pk>\/graph\//);
  assert.match(urls, /workflow_graph_update/);
});
