# Formints JS/TS Client Bundle — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a **modular, framework-agnostic TypeScript client bundle** (`@formints/client`) with one module per API resource, consumable by any TS framework (React, Astro, Vue), covering the Standard/Cloud surfaces including the new money, export, and monitor endpoints.

**Architecture:** A new package `projects/formints/packages/formints-client/`. `core.ts` owns the fetch client (`createClient(baseUrl)`) and shared types; resource modules (`currencies.ts`, `taxProfiles.ts`, `exports.ts`, `monitor.ts`) export pure functions that take the client. Modules import only from `core.ts` (tree-shakeable, no framework imports). Compiled with `tsc` to ESM + `.d.ts`, tested with Vitest.

**Tech Stack:** TypeScript 5, Vitest, `tsc`. No runtime dependencies (fetch only).

## Global Constraints

- Lives under `projects/formints/packages/formints-client/` only.
- **Zero runtime dependencies** — browser `fetch` only; `package.json` has no `dependencies` key.
- **One module per resource**; modules never import each other (only `./core`).
- Framework-agnostic: no React/Vue/Astro imports anywhere in `src/`.
- Node `>=18` (global `fetch`).
- Test command: `cd projects/formints/packages/formints-client && pnpm vitest run`
- Type/build command: `cd projects/formints/packages/formints-client && pnpm build` (`tsc -p tsconfig.build.json`).

---

## Task S1: Scaffold package + core client

**Files:**
- Create: `packages/formints-client/package.json`
- Create: `packages/formints-client/tsconfig.json`
- Create: `packages/formints-client/tsconfig.build.json`
- Create: `packages/formints-client/vitest.config.ts`
- Create: `packages/formints-client/src/core.ts`
- Create: `packages/formints-client/src/index.ts`
- Create: `packages/formints-client/tests/core.test.ts`

**Interfaces:**
- Produces: `createClient(baseUrl: string): FormintsClient`, `FormintsClient.request<T>(path, init?)`, `ApiError`. Consumed by Tasks S2, S3 and by every edition plan's SDK tasks.

- [ ] **Step 1: Write the failing test**

Create `packages/formints-client/tests/core.test.ts`:

```ts
import { describe, it, expect, vi, afterEach } from 'vitest';
import { createClient, ApiError } from '../src/core';

describe('core client', () => {
  afterEach(() => vi.restoreAllMocks());

  it('GETs JSON and applies the base URL', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'content-type': 'application/json' } }),
    );
    vi.stubGlobal('fetch', fetchMock);
    const client = createClient('http://127.0.0.1:8767');
    const data = await client.request<{ ok: boolean }>('/health');
    expect(fetchMock).toHaveBeenCalledWith('http://127.0.0.1:8767/health', expect.any(Object));
    expect(data).toEqual({ ok: true });
  });

  it('throws ApiError on non-2xx', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('nope', { status: 403 })));
    const client = createClient('http://x');
    await expect(client.request('/secret')).rejects.toThrow(ApiError);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/packages/formints-client && pnpm vitest run`
Expected: FAIL — cannot find module `../src/core` (files missing)

- [ ] **Step 3: Write the scaffold**

Create `packages/formints-client/package.json`:

```json
{
  "name": "@formints/client",
  "version": "0.1.0",
  "description": "Modular, framework-agnostic TypeScript client for the Formints POS API (Standard + Cloud surfaces).",
  "type": "module",
  "license": "AGPL-3.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js" },
    "./currencies": { "types": "./dist/currencies.d.ts", "import": "./dist/currencies.js" },
    "./tax-profiles": { "types": "./dist/taxProfiles.d.ts", "import": "./dist/taxProfiles.js" },
    "./exports": { "types": "./dist/exports.d.ts", "import": "./dist/exports.js" },
    "./monitor": { "types": "./dist/monitor.d.ts", "import": "./dist/monitor.js" }
  },
  "files": ["dist"],
  "scripts": {
    "build": "tsc -p tsconfig.build.json",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "vitest run"
  },
  "devDependencies": {
    "typescript": "~5.8.3",
    "vitest": "^4.1.10"
  }
}
```

Create `packages/formints-client/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "declaration": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "types": ["vitest/globals"]
  },
  "include": ["src", "tests"]
}
```

Create `packages/formints-client/tsconfig.build.json`:

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "emitDeclarationOnly": false
  },
  "include": ["src"]
}
```

Create `packages/formints-client/vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
  },
});
```

Create `packages/formints-client/src/core.ts`:

```ts
/** Core HTTP client for the Formints POS API. Framework-agnostic (fetch only). */

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface FormintsClient {
  /** Perform a JSON request relative to the base URL. */
  request<T>(path: string, init?: RequestInit): Promise<T>;
}

export function createClient(baseUrl: string): FormintsClient {
  const root = baseUrl.replace(/\/$/, '');
  return {
    async request<T>(path: string, init: RequestInit = {}): Promise<T> {
      const res = await fetch(`${root}${path}`, {
        ...init,
        headers: {
          'content-type': 'application/json',
          ...(init.headers ?? {}),
        },
      });
      if (!res.ok) {
        throw new ApiError(res.status, `Request failed: ${res.status} ${res.statusText}`, await res.text());
      }
      const text = await res.text();
      return (text ? JSON.parse(text) : undefined) as T;
    },
  };
}
```

Create `packages/formints-client/src/index.ts`:

```ts
export { createClient, ApiError } from './core';
export type { FormintsClient } from './core';
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/formints/packages/formints-client && pnpm vitest run`
Expected: PASS — 2 tests green.

- [ ] **Step 5: Commit**

```bash
git add projects/formints/packages/formints-client/
git commit -m "feat(formints-client): scaffold modular TS client with core fetch wrapper"
```

---

## Task S2: Resource modules (currencies, tax profiles, exports, monitor)

**Files:**
- Create: `packages/formints-client/src/currencies.ts`
- Create: `packages/formints-client/src/taxProfiles.ts`
- Create: `packages/formints-client/src/exports.ts`
- Create: `packages/formints-client/src/monitor.ts`
- Update: `packages/formints-client/src/index.ts` (barrel)
- Test: `packages/formints-client/tests/resources.test.ts`

**Interfaces:**
- Consumes: `createClient`, `FormintsClient` from `./core` (Task S1).
- Produces (all consume `client: FormintsClient`):
  - `listCurrencies(client)`, `createCurrency(client, input)`
  - `listTaxProfiles(client)`
  - `exportUrl(baseUrl, resource, format)` where `resource: 'products' | 'sales' | 'customers' | 'inventory'`
  - `getMonitorStatus(client)` returning `{ database, last_backup, sync_queue_depth }`

- [ ] **Step 1: Write the failing test**

Create `packages/formints-client/tests/resources.test.ts`:

```ts
import { describe, it, expect, vi, afterEach } from 'vitest';
import { createClient } from '../src/core';
import { listCurrencies, createCurrency } from '../src/currencies';
import { listTaxProfiles } from '../src/taxProfiles';
import { exportUrl } from '../src/exports';
import { getMonitorStatus } from '../src/monitor';

describe('resource modules', () => {
  afterEach(() => vi.restoreAllMocks());

  it('lists and creates currencies', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ count: 1, items: [{ code: 'USD' }] }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ code: 'EUR' }), { status: 201 })));
    const client = createClient('http://api');
    const list = await listCurrencies(client);
    expect(list.items[0]?.code).toBe('USD');
    const created = await createCurrency(client, { code: 'EUR', name: 'Euro', symbol: '€', exchange_rate: '0.92' });
    expect(created.code).toBe('EUR');
  });

  it('lists tax profiles', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ count: 1, items: [{ name: 'Standard' }] }), { status: 200 })));
    const profiles = await listTaxProfiles(createClient('http://api'));
    expect(profiles.items[0]?.name).toBe('Standard');
  });

  it('builds export URLs for csv and json', () => {
    expect(exportUrl('http://api', 'products', 'csv')).toBe('http://api/export/products.csv');
    expect(exportUrl('http://api', 'sales', 'json')).toBe('http://api/export/sales.csv?format=json');
  });

  it('reads monitor status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ database: 'ok', last_backup: null, sync_queue_depth: 0 }), { status: 200 })));
    const status = await getMonitorStatus(createClient('http://api'));
    expect(status.database).toBe('ok');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/packages/formints-client && pnpm vitest run`
Expected: FAIL — cannot find modules `../src/currencies`, `../src/taxProfiles`, `../src/exports`, `../src/monitor`

- [ ] **Step 3: Write the modules**

Create `packages/formints-client/src/currencies.ts`:

```ts
import type { FormintsClient } from './core';

export interface Currency {
  id: number;
  code: string;
  name: string;
  symbol: string;
  exchange_rate: string;
  is_default: boolean;
  is_active: boolean;
}

export interface CurrencyInput {
  code: string;
  name: string;
  symbol?: string;
  exchange_rate?: string;
  is_default?: boolean;
}

export async function listCurrencies(client: FormintsClient): Promise<{ count: number; items: Currency[] }> {
  return client.request('/api/v1/currencies');
}

export async function createCurrency(client: FormintsClient, input: CurrencyInput): Promise<Currency> {
  return client.request('/api/v1/currencies', { method: 'POST', body: JSON.stringify(input) });
}
```

Create `packages/formints-client/src/taxProfiles.ts`:

```ts
import type { FormintsClient } from './core';

export interface TaxProfile {
  id: number;
  name: string;
  rate: string;
  is_default: boolean;
  is_active: boolean;
}

export async function listTaxProfiles(client: FormintsClient): Promise<{ count: number; items: TaxProfile[] }> {
  return client.request('/api/v1/tax-profiles');
}
```

Create `packages/formints-client/src/exports.ts`:

```ts
export type ExportResource = 'products' | 'sales' | 'customers' | 'inventory';
export type ExportFormat = 'csv' | 'json';

export function exportUrl(baseUrl: string, resource: ExportResource, format: ExportFormat = 'csv'): string {
  const root = baseUrl.replace(/\/$/, '');
  return format === 'json'
    ? `${root}/export/${resource}.csv?format=json`
    : `${root}/export/${resource}.csv`;
}
```

Create `packages/formints-client/src/monitor.ts`:

```ts
import type { FormintsClient } from './core';

export interface MonitorStatus {
  database: 'ok' | 'error';
  last_backup: { filename: string; status: string; size_bytes: number | null; started_at: string } | null;
  sync_queue_depth: number;
}

export async function getMonitorStatus(client: FormintsClient): Promise<MonitorStatus> {
  return client.request('/monitor/status');
}
```

Update `packages/formints-client/src/index.ts`:

```ts
export { createClient, ApiError } from './core';
export type { FormintsClient } from './core';
export { listCurrencies, createCurrency } from './currencies';
export type { Currency, CurrencyInput } from './currencies';
export { listTaxProfiles } from './taxProfiles';
export type { TaxProfile } from './taxProfiles';
export { exportUrl } from './exports';
export type { ExportResource, ExportFormat } from './exports';
export { getMonitorStatus } from './monitor';
export type { MonitorStatus } from './monitor';
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/packages/formints-client && pnpm vitest run`
Expected: PASS — 6 tests green.

- [ ] **Step 5: Commit**

```bash
git add projects/formints/packages/formints-client/
git commit -m "feat(formints-client): currencies, tax-profiles, exports, monitor resource modules"
```

---

## Task S3: Build output + typecheck gate

**Files:**
- No code changes unless the build fails.

- [ ] **Step 1: Typecheck**

Run: `cd projects/formints/packages/formints-client && pnpm typecheck`
Expected: no errors.

- [ ] **Step 2: Build**

Run: `cd projects/formints/packages/formints-client && pnpm build`
Expected: `dist/` contains `index.js`, `core.js`, `currencies.js`, `taxProfiles.js`, `monitor.js`, `exports.js` + matching `.d.ts` files.

- [ ] **Step 3: Verify the exports map resolves**

Run: `node -e "import('./dist/index.js').then(m => { if (!m.createClient) process.exit(1); console.log('ok') })"`
Expected: prints `ok`.

- [ ] **Step 4: Commit**

```bash
git add projects/formints/packages/formints-client/
git commit -m "build(formints-client): ESM + types build output with exports map"
```

---

## Self-Review

1. **Spec coverage:** modular bundle (S1), one module per resource (S2), framework-agnostic build usable by TS frameworks (S3). Consumed by edition plans 01-05 via their SDK tasks.
2. **Placeholder scan:** none.
3. **Type consistency:** `FormintsClient.request<T>(path, init?)` used identically across `core.ts`, all resource modules, and tests. `exportUrl` matches the `?format=json` contract from plan 02-standard (B4). `getMonitorStatus` matches plan 04-cloud (C3) payload keys.

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/06-js-sdk.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
