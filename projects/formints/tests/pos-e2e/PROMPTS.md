# POS E2E — Prompt Variations

> **Project:** `projects/pos/pos-e2e/`
> **Purpose:** Reusable AI prompts for Playwright E2E test generation

---

## Playwright / TypeScript Prompts

### Add a new E2E test (API-only — bolt pattern)
```
Add a Playwright E2E test using the bolt pattern (API-only, no browser):
- File: tests/api/[feature].spec.ts
- Use Playwright's request fixture: test('...', async ({ request }) => { ... })
- Target: http://localhost:8765 (pos-full) or http://localhost:8766 (pos-solo)
- Graceful skip with test.skip() if server not running
- Verify status codes, response shapes, and data integrity
```

### Add a new E2E test (full flow — browser required)
```
Add a Playwright E2E test for the full [feature] flow:
- File: tests/flows/[feature]-flow.spec.ts
- Use page fixture: test('...', async ({ page }) => { ... })
- Start from the feature page, interact with UI elements
- Verify visual state changes after actions
- Use data-testid attributes for selectors (preferred over CSS class selectors)
```

### Add a new visual regression test
```
Add a Playwright visual regression test for [page]:
- File: tests/visual/[page]-regression.spec.ts
- Use expect(page).toHaveScreenshot() 
- Test on multiple viewport sizes (mobile, tablet, desktop)
- Update snapshots: npx playwright test --update-snapshots
```

### Add a new Page Object Model
```
Add a new Page Object Model for [page]:
- File: pages/[page]-page.ts
- Export class with locator getters and action methods
- Use data-testid for stable selectors
- Import and use in flow tests
```

### Run tests for a specific edition
```bash
# POS Full (server on 8765)
npx playwright test --project=pos-full

# POS Solo (server on 8766)
npx playwright test --project=pos-solo

# POS Mini (no server)
npx playwright test --project=pos-mini

# API-only tests (no browser)
npx playwright test tests/api/

# Full suite (all editions)
npx playwright test
```

### CI Integration
```yaml
# GitHub Actions — add to js-test.yml
- name: Run POS E2E tests
  working-directory: projects/pos/pos-e2e
  run: npx playwright test tests/api/ --project=pos-full
```
