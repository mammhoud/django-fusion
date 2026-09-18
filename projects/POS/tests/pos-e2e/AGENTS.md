# Formints POS E2E — AI Agent Instructions

**Path:** `projects/formints/tests/pos-e2e/`
**Stack:** Playwright + TypeScript + Node.js

Read `projects/formints/AGENTS.md` first. This suite is shared POS validation,
not a product frontend and not a replacement for edition-local tests.

## Current structure

```text
pos-e2e/
├── pages/                    # Page Object Models for POS flows
├── helpers/                  # API and browser utilities
├── fixtures/                 # Auth and shared Playwright fixtures
├── tests/
│   ├── e2e/                  # Browser user-flow specs
│   └── api/                  # API/contract specs
├── playwright.config.ts
├── package.json
├── README.md
├── PROMPTS.md
└── docs/                     # Local test notes where present
```

Confirm the exact spec names in the tree before using an example command; the
suite is actively consolidated and old `flows/`/`visual/` paths may be stale.

## Test boundaries

- Use browser tests for visible workflows: auth, home/navigation, inventory,
  sale, responsiveness, and critical operational flows.
- Use Playwright's `request` fixture for API contract tests where no browser is
  needed.
- Keep page selectors and workflow knowledge in `pages/`; keep transport/setup
  logic in `helpers/` and `fixtures/`.
- Do not assert internal implementation details when a user-visible or API
  contract assertion is available.
- Keep edition-specific base URLs/configuration in `playwright.config.ts` or
  environment variables, not duplicated in each spec.

## Commands

```bash
cd projects/formints/tests/pos-e2e
pnpm install                 # or the package's documented npm command
npx playwright test
npx playwright test tests/api/
npx playwright test tests/e2e/
npx playwright show-report
```

Run only the relevant project/spec first. Browser installation and running
backend services may be prerequisites; report those as environment requirements
rather than changing application code to bypass them.

## Safety and fixtures

Use isolated test data and ephemeral/local services. Never point E2E tests at a
production POS, real customer data, or a shared destructive database. Keep
credentials in Playwright environment/fixture configuration and never commit
real tokens or screenshots containing sensitive information.
