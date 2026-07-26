# Visual Regression Testing Guide

Theme consistency verification across all LMS pages using Playwright's built-in `toHaveScreenshot()`.

## Quick Start

```bash
# Run visual regression tests (compares against stored baselines)
npx playwright test tests/e2e/theme-visual-regression.spec.ts

# Update baselines after intentional theme changes
npx playwright test tests/e2e/theme-visual-regression.spec.ts --update-snapshots

# View diff of failed comparisons
npx playwright show-report
```

## How It Works

### 1. Theme Showcase Page (`/dev/theme`)

A single page at `/dev/theme` renders every theme token and component variant:

| Section | What's Tested |
|---------|---------------|
| Color Swatches | All 6 `--ctc-*` variables as visual blocks |
| Typography | h1–h4 hierarchy, body, small, xs text |
| Buttons | Primary, secondary, outline, accent, white, disabled, sizes, with icon |
| Cards | Base, hover, gradient |
| Inputs | Default, filled, disabled, textarea |
| Badges | Primary, success, warning, danger, neutral |
| UI Components | LoadingSkeleton (card/list/detail), ErrorState, EmptyState |
| Progress Bars | 50%, 75%, 100% fills |
| Icons & Stats | Stat cards, service cards, contact cards, avatars |
| FAQ | Accordion open/closed states |

### 2. Dashboard Snapshots

Key dashboard pages are captured with dynamic content **masked**:
- Main Dashboard — charts and stat values masked
- Courses List — table body masked
- Profile — full page
- Admin Withdrawals — table body masked

### 3. Public Page Snapshots

- Homepage — full page (higher tolerance for large page)
- Login — full page

## Snapshot Storage

```
tests/e2e/
├── theme-visual-regression.spec.ts
└── theme-visual-regression.spec.ts-snapshots/
    ├── theme-showcase-full-chromium-linux.png
    ├── theme-swatches-chromium-linux.png
    ├── theme-buttons-chromium-linux.png
    ├── theme-cards-chromium-linux.png
    ├── theme-components-chromium-linux.png
    ├── dashboard-main-chromium-linux.png
    ├── dashboard-courses-chromium-linux.png
    ├── dashboard-profile-chromium-linux.png
    ├── dashboard-admin-withdrawals-chromium-linux.png
    ├── public-homepage-chromium-linux.png
    └── public-login-chromium-linux.png
```

**All snapshot files should be committed to git.** They serve as the source of truth for visual baselines.

## Tolerance Settings

| Page Type | maxDiffPixels | threshold | Rationale |
|-----------|:-------------:|:---------:|-----------|
| Theme Showcase | 200–500 | 3–5% | Static content, should match exactly |
| Dashboard pages | 800–1000 | 8% | Dynamic data masked, minor layout shifts OK |
| Public homepage | 1500 | 10% | Large page, more tolerance |

## When to Update Snapshots

Run with `--update-snapshots` when:
- You intentionally change CSS variables, globals.css, or component styles
- You add new theme tokens
- You modify the Theme Showcase page itself
- You upgrade Tailwind, Next.js, or other dependencies that affect rendering

**Always review the diff before committing updated snapshots:**

```bash
# 1. Run with update
npx playwright test tests/e2e/theme-visual-regression.spec.ts --update-snapshots

# 2. View the HTML report to see what changed
npx playwright show-report

# 3. Review git diff of snapshot files
git diff --stat tests/e2e/**/__screenshots__/
```

## CI Integration

```yaml
- name: Visual Regression Tests
  run: |
    cd projects/lms/front-end
    npx playwright test tests/e2e/theme-visual-regression.spec.ts

- name: Upload Diff Artifacts (on failure)
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: visual-regression-diffs
    path: projects/lms/front-end/test-results/
```

## Adding New Visual Tests

1. Create a test in `tests/e2e/theme-visual-regression.spec.ts`
2. Use `expect(page).toHaveScreenshot('descriptive-name.png', { fullPage: true })`
3. Run once with `--update-snapshots` to create baselines
4. Commit the generated PNG files

```ts
test('new feature snapshot', async ({ page }) => {
  await page.goto('/new-page');
  await expect(page).toHaveScreenshot('new-page.png', {
    fullPage: true,
    maxDiffPixels: 500,
    threshold: 0.05,
  });
});
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Snapshots always fail in CI | OS differences (Linux vs macOS). Run `--update-snapshots` in CI once to capture Linux baselines |
| Dynamic content causes false positives | Use `mask: [page.locator(...)]` to exclude dynamic areas |
| Anti-aliasing differences | Increase `maxDiffPixels` or `threshold` |
| Font rendering differs | Ensure the same fonts are installed. Use `maxDiffPixels: 200` for font-heavy areas |
| Timeout waiting for page | Increase `waitUntil: 'networkidle'` timeout or add explicit `waitForSelector` |
