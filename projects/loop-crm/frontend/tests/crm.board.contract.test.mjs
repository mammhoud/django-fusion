import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('PipelineBoard island loads the board from the compatibility API road', async () => {
  const board = await read('src/components/board/PipelineBoard.tsx');
  assert.match(board, /fetch\(BOARD_URL\)/);
  assert.match(board, /BOARD_URL = '\/api\/v1\/board\/'/);
  assert.match(board, /payload\.results/);
});

test('PipelineBoard moves deals through the stage endpoint with optimistic Redux state', async () => {
  const board = await read('src/components/board/PipelineBoard.tsx');
  assert.match(board, /MOVE_URL\(dealId\)/);
  assert.match(board, /method: 'POST'/);
  assert.match(board, /stage_id: toStageId/);
  assert.match(board, /dispatch\(moveDeal/);
  assert.match(board, /dispatch\(setPipelines\(snapshot\)\)/); // rollback on failure
});

test('PipelineBoard uses GSAP Draggable and honors reduced motion', async () => {
  const board = await read('src/components/board/PipelineBoard.tsx');
  assert.match(board, /gsap\/Draggable/);
  assert.match(board, /Draggable\.create/);
  assert.match(board, /prefers-reduced-motion: reduce/);
  assert.match(board, /matchMedia/);
  // Keyboard/touch fallback exists for reduced-motion users.
  assert.match(board, /loop-board__stepper/);
});

test('PipelineBoard wraps itself in the Redux StoreProvider bridge', async () => {
  const board = await read('src/components/board/PipelineBoard.tsx');
  assert.match(board, /StoreProvider/);
  assert.match(board, /<StoreProvider>/);
});

test('crmSlice holds pipelines and an optimistic moveDeal reducer', async () => {
  const slice = await read('src/store/slices/crmSlice.ts');
  assert.match(slice, /pipelines: Pipeline\[\]/);
  assert.match(slice, /setPipelines/);
  assert.match(slice, /moveDeal/);
  assert.match(slice, /fromStage\.deals\.splice/);
});

test('Deals page mounts the island while other shell pages keep the highlight cards', async () => {
  const shell = await read('src/pages/[...path].astro');
  assert.match(shell, /import PipelineBoard/);
  assert.match(shell, /page\.path === '\/crm\/deals\/'/);
  assert.match(shell, /<PipelineBoard client:load \/>/);
});
