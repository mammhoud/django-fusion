# POS E2E — AI Agent Instructions

> **Project:** `projects/pos/pos-e2e/`  
> **Type:** Playwright E2E test suite (standalone)  
> **Stack:** TypeScript + Playwright + Node.js

---

## Project Overview

POS E2E is the shared Playwright end-to-end test suite for all POS editions.
It has its own `package.json` and `playwright.config.ts` and is designed to
run independently of any single POS project. Tests use the **bolt pattern**
(API-only tests via Playwright `request` fixture, no browser needed for
sidecar/Robyn endpoints).

---

## Directory Structure

```
pos-e2e/
├── playwright.config.ts          # 3 Playwright projects (pos-full, pos-solo, pos-mini)
├── package.json                  # Standalone deps (@playwright/test only)
├── tests/
│   ├── api/                      # API tests (bolt pattern — no browser)
│   │   ├── pos-api.spec.ts       # POS core API endpoints
│   │   └── sidecar-health.spec.ts # Sidecar health checks
│   ├── flows/                    # Full flow tests (require browser)
│   │   ├── sale-flow.spec.ts
│   │   ├── inventory-flow.spec.ts
│   │   └── auth-flow.spec.ts
│   └── visual/                   # Visual regression tests
│       └── theme-regression.spec.ts
├── fixtures/
│   └── auth.ts                   # Shared auth fixtures (Fusion sidecar + API)
├── helpers/
│   └── api.ts                    # API helper utilities
├── pages/                        # Page Object Models
│   ├── pos-page.ts
│   ├── inventory-page.ts
│   └── auth-page.ts
├── docs/                         # Documentation
│   ├── typescript/               # TypeScript/Playwright docs
│   └── testing/                  # Test strategy docs
└── plan/                         # Implementation plans
```

---

## Playwright Configuration

The `playwright.config.ts` defines 3 projects:

| Project | Target | WebServer | Browser |
|---------|--------|:---------:|:-------:|
| `pos-full` | POS Full sidecar on `localhost:8765` | ❌ (no webServer) | Chromium |
| `pos-solo` | POS Solo sidecar on `localhost:8766` | ❌ (no webServer) | Chromium |
| `pos-mini` | POS Mini (no sidecar) | ❌ | Chromium |

---

## Bolt Pattern (API-Only Tests)

API tests use Playwright's `request` fixture — no browser needed:

```typescript
import { test, expect } from '@playwright/test';

test('GET /api/products returns product list', async ({ request }) => {
  const response = await request.get('http://localhost:8765/api/products/');
  expect(response.status()).toBe(200);
  const data = await response.json();
  expect(data.products).toBeInstanceOf(Array);
});
```

---

## Testing Commands

```bash
# Install deps
npm install

# Run all E2E tests
npx playwright test

# Run specific edition
npx playwright test --project=pos-full
npx playwright test --project=pos-solo
npx playwright test --project=pos-mini

# API tests only (no browser needed)
npx playwright test tests/api/

# Flow tests (require browser + dev server)
npx playwright test tests/flows/

# Show report
npx playwright show-report

# Interactive UI mode
npx playwright test --ui
```

---

## Documentation References

| Topic | File |
|-------|------|
| POS architecture | `../docs/POS_ARCHITECTURE.md` |
| Getting started | `../docs/GETTING_STARTED.md` |
| Implementation plan | `./plan/` |
| Prompt variations | `./PROMPTS.md` |
