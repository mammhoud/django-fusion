import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig, devices } from '@playwright/test';

const port = 1112;
const enginePort = 8001;
// One id per run, shared by the config and the specs. Playwright re-evaluates
// this module inside worker processes (and after a test failure), so the id
// must be inherited rather than recomputed, otherwise the test namespace and
// the seeded admin account would diverge mid-run.
process.env.PLANING_PW_RUN ||= `${Date.now()}-${process.pid}`;
const testNamespace = `planing_test_${process.env.PLANING_PW_RUN}`;
const engineFile = `/tmp/planing_pw_engine_${process.env.PLANING_PW_RUN}.db`;
// Chat context roots point at disposable fixtures so the suite never reads the
// deployed project tree or writes into real documents.
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
// Binary context fixtures (a PDF with a real text stream and a PNG) are copied
// into the documents root so the suite can attach them like a member would.
const fixtureSource = path.join(path.dirname(fileURLToPath(import.meta.url)), 'tests', 'fixtures');
for (const name of fs.existsSync(fixtureSource) ? fs.readdirSync(fixtureSource) : []) {
  fs.copyFileSync(path.join(fixtureSource, name), path.join(fixtureDirs.documents, name));
}

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.mjs',
  // Suites that seed their own bootstrap admin (appearance/graph) or register
  // via the API (tickets) run under playwright.extra.config.mjs with their own
  // server + engine — they share no "first admin" premise with this config.
  testIgnore: '**/{appearance-and-graph,tickets}.spec.mjs',
  timeout: 30_000,
  workers: 1,
  use: { baseURL: `http://127.0.0.1:${port}`, ...devices['Desktop Chrome'] },
  // Web servers launch in array order and each must be ready before the next
  // starts: the disposable SurrealDB engine boots first, then the API server
  // connects to it. Tests must never share an engine with the deployed instance.
  webServer: [
    {
      // Reusable on purpose: teardown may SIGKILL the wrapper shell (skipping
      // any trap) and a surviving engine would block later runs. Data is still
      // isolated per run via PLANING_PW_RUN namespaces, so a leftover engine is
      // always safe to reuse. Fresh starts clear all stale engine files.
      command: `sh -c 'trap "docker rm -f planing-pw-engine 2>/dev/null" TERM INT EXIT; docker rm -f planing-pw-engine 2>/dev/null; rm -f /tmp/planing_pw_engine_*.db*; docker run --rm --name planing-pw-engine -p 127.0.0.1:${enginePort}:8000 surrealdb/surrealdb:v1.5.6 start --auth --user root --pass playwright-engine-pass rocksdb:${engineFile}'`,
      url: `http://127.0.0.1:${enginePort}/health`,
      reuseExistingServer: true,
      timeout: 45_000,
    },
    {
      command: 'node tests/mock-llm.mjs',
      port: 11434,
      reuseExistingServer: false,
      timeout: 15_000,
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
