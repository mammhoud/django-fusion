import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { defineConfig, devices } from '@playwright/test';

// Dedicated config for suites that must not share the main server: the
// appearance/graph specs seed their own bootstrap admin, and tickets.spec.mjs
// registers via the API — both break on the main config where the auth suite
// already owns "first admin". Splitting gives each group its own server +
// SurrealDB namespace pair. Runs sequentially via `npm test`; ports/names are
// distinct so even parallel invocations cannot collide.
const port = 1114;
const enginePort = 8003;
process.env.PLANING_PW_RUN ||= `${Date.now()}-appearance-${process.pid}`;
const testNamespace = `planing_test_${process.env.PLANING_PW_RUN}`;
const engineFile = `/tmp/planing_pw_engine_appearance_${process.env.PLANING_PW_RUN}.db`;
// Same disposable context fixtures as the main config, under this run's id.
const contextFixture = path.join(os.tmpdir(), `planing_pw_context_${process.env.PLANING_PW_RUN}`);
const fixtureDirs = {
  project: path.join(contextFixture, 'project'),
  documents: path.join(contextFixture, 'documents'),
  notes: path.join(contextFixture, 'notes'),
};
for (const dir of Object.values(fixtureDirs)) fs.mkdirSync(dir, { recursive: true });
fs.mkdirSync(path.join(fixtureDirs.project, 'nested'), { recursive: true });
fs.writeFileSync(path.join(fixtureDirs.project, 'README.md'), '# Fixture project\n\nThis file is attached to a chat as context.\n');
fs.writeFileSync(path.join(fixtureDirs.project, 'nested', 'deep-notes.md'), '# Deep notes\n\nNested fixture file.\n');

export default defineConfig({
  testDir: './tests',
  testMatch: '**/{appearance-and-graph,tickets}.spec.mjs',
  timeout: 30_000,
  workers: 1,
  use: { baseURL: `http://127.0.0.1:${port}`, ...devices['Desktop Chrome'] },
  webServer: [
    {
      // Reusable on purpose: teardown may SIGKILL the wrapper shell (skipping
      // any trap) and a surviving engine would block later runs. Data is still
      // isolated per run via PLANING_PW_RUN namespaces. Dedicated container
      // name + ports keep this suite independent of the main config's engine.
      command: `sh -c 'trap "docker rm -f planing-pw-engine-appearance 2>/dev/null" TERM INT EXIT; docker rm -f planing-pw-engine-appearance 2>/dev/null; rm -f /tmp/planing_pw_engine_appearance_*.db*; docker run --rm --name planing-pw-engine-appearance -p 127.0.0.1:${enginePort}:8000 surrealdb/surrealdb:v1.5.6 start --auth --user root --pass playwright-engine-pass rocksdb:${engineFile}'`,
      url: `http://127.0.0.1:${enginePort}/health`,
      reuseExistingServer: true,
      timeout: 45_000,
    },
    {
      command: 'node server.mjs',
      url: `http://127.0.0.1:${port}/health`,
      reuseExistingServer: false,
      timeout: 30_000,
      stdout: 'pipe',
      stderr: 'pipe',
      env: {
        PLANING_PORT: String(port),
        SURREALDB_URL: `http://127.0.0.1:${enginePort}/rpc`,
        SURREALDB_USER: 'root',
        SURREALDB_PASS: 'playwright-engine-pass',
        SURREALDB_NS: testNamespace,
        SURREALDB_DB: 'auth',
        NEXTAUTH_SECRET: 'playwright-secret',
        PLANING_CONTEXT_PROJECT_DIR: fixtureDirs.project,
        PLANING_CONTEXT_DOCUMENTS_DIR: fixtureDirs.documents,
        PLANING_CONTEXT_NOTES_DIR: fixtureDirs.notes,
      },
    },
  ],
});
