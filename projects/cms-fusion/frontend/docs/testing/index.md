# Testing Docs — LMS Front-End

> **Directory:** `docs/testing/`
> **Frameworks:** Vitest (unit) + Playwright (E2E)
> **Project:** `projects/lms/front-end/`

---

## Test Commands

```bash
# Unit tests (Vitest)
npm run test              # 354 tests

# E2E tests (Playwright)
npm run test:e2e          # All E2E tests
npm run test:e2e:ui       # Interactive mode
npm run test:e2e:report   # HTML report

# Visual regression
npm run test:e2e:visual           # Compare against baselines
npm run test:e2e:visual-update    # Update baselines

# All tests
npm run test:all          # Vitest + Playwright
```

## Test File Conventions

| File Pattern | Purpose |
|-------------|---------|
| `src/test/{Component}.test.tsx` | Component unit test |
| `tests/e2e/{feature}.spec.ts` | E2E test |
| `tests/e2e/theme-visual-regression.spec.ts` | Visual regression |

## E2E Test Files

| File | Coverage |
|------|----------|
| `dashboard-core-flows.spec.ts` | 10 test groups, dashboard navigation |
| `dashboard-ctc-theme.spec.ts` | 14 dashboard pages CTC compliance |
| `withdrawal-flow.spec.ts` | 15 tests, full withdrawal lifecycle |
| `public-pages.spec.ts` | Public page smoke tests (planned) |

## CI

```yaml
# .github/workflows/js-test.yml
# Jobs: lms-frontend-test (vitest), lms-frontend-e2e (playwright)
```

See `../PROMPTS.md#documentation-prompts` for test generation templates.

## Detailed Guides

| Guide | Description |
|-------|-------------|
| [Test Patterns](./test-patterns.md) | Vitest 4-state + responsive variant tests, Playwright POM usage, CTC theme compliance, visual regression |
