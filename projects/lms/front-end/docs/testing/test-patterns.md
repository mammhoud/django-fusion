# LMS Front-End — Test Patterns

> **Directory:** `docs/testing/`
> **Frameworks:** Vitest (unit) + Playwright (E2E)

---

## Vitest Unit Test Pattern

### Component Test (4-State Coverage)

```typescript
// src/test/components/CourseGrid.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CourseGrid from '@/components/pages/courses/CourseGrid';

describe('CourseGrid', () => {
  // 1. Loading state
  it('shows loading skeleton when isLoading', () => {
    render(<CourseGrid isLoading={true} />);
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  // 2. Error state
  it('shows error message and retry button when error', () => {
    const onRetry = vi.fn();
    render(<CourseGrid error={new Error('Network error')} onRetry={onRetry} />);
    expect(screen.getByText(/error/i)).toBeInTheDocument();
    screen.getByRole('button', { name: /try again/i }).click();
    expect(onRetry).toHaveBeenCalled();
  });

  // 3. Empty state
  it('shows empty state when data is empty', () => {
    render(<CourseGrid data={[]} />);
    expect(screen.getByText(/no courses found/i)).toBeInTheDocument();
  });

  // 4. Normal state
  it('renders course cards when data is present', () => {
    const courses = [{ id: 1, title: 'React 101', price: 49 }];
    render(<CourseGrid data={courses} />);
    expect(screen.getByText('React 101')).toBeInTheDocument();
    expect(screen.getByText('$49')).toBeInTheDocument();
  });
});
```

### Responsive Variant Test

```typescript
it('renders 1 column on mobile variant', () => {
  const { container } = render(<CourseGrid data={courses} variant="mobile" />);
  const grid = container.querySelector('.grid');
  expect(grid).toHaveClass('grid-cols-1');
});

it('renders 3 columns on desktop variant', () => {
  const { container } = render(<CourseGrid data={courses} variant="desktop" />);
  const grid = container.querySelector('.grid');
  expect(grid).toHaveClass('grid-cols-3');
});
```

### RTK Query Hook Test

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '@/store';
import { useGetCoursesQuery } from '@/store/api/endpoints/courses';

it('fetches courses on mount', async () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  );
  const { result } = renderHook(() => useGetCoursesQuery({ page: 1 }), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data?.results).toBeDefined();
});
```

---

## Playwright E2E Test Pattern

### Page Object Model Usage

```typescript
// tests/e2e/customers-crud.spec.ts
import { test, expect } from '@playwright/test';
import { CustomersPage } from '../pages/customers-page';

test.describe('Customers CRUD', () => {
  let customersPage: CustomersPage;

  test.beforeEach(async ({ page }) => {
    customersPage = new CustomersPage(page);
    await customersPage.goto();
  });

  test('adds a new customer', async () => {
    await customersPage.clickAdd();
    await customersPage.fillForm({
      name: 'John Doe',
      phone: '+1234567890',
      email: 'john@example.com',
    });
    await customersPage.submit();

    // Verify customer card appears
    await expect(customersPage.customerCards.filter({ hasText: 'John Doe' })).toBeVisible();
  });

  test('searches customers', async () => {
    await customersPage.search('John');
    // Wait for filter to complete
    await customersPage.page.waitForTimeout(500);
    const count = await customersPage.getCustomerCount();
    expect(count).toBeGreaterThan(0);
  });

  test('deletes a customer', async () => {
    await customersPage.clickDelete('John Doe');
    await customersPage.confirmDelete();
    await expect(customersPage.customerCards.filter({ hasText: 'John Doe' })).not.toBeVisible();
  });
});
```

### CTC Theme Compliance Test

```typescript
// tests/e2e/theme-compliance.spec.ts
import { test, expect } from '@playwright/test';

const PUBLIC_PAGES = [
  { path: '/', name: 'Homepage' },
  { path: '/courses', name: 'Courses' },
  { path: '/login', name: 'Login' },
  { path: '/registration', name: 'Registration' },
  { path: '/about-us', name: 'About Us' },
];

test.describe('CTC Teal Theme — Public Pages', () => {
  for (const { path, name } of PUBLIC_PAGES) {
    test(`${name} (${path}) has no indigo/purple classes`, async ({ page }) => {
      await page.goto(path);
      const forbiddenCount = await page.locator('[class*="indigo-"], [class*="purple-"]').count();
      expect(forbiddenCount, `${name} contains forbidden indigo/purple classes`).toBe(0);
    });

    test(`${name} (${path}) has CTC teal classes`, async ({ page }) => {
      await page.goto(path);
      const tealElements = page.locator('[class*="ctc-primary"], [class*="teal-"], .section-hero, .card-gradient, .btn-primary');
      await expect(tealElements.first()).toBeVisible();
    });
  }
});
```

### Visual Regression Test

```typescript
// tests/e2e/visual-regression.spec.ts
import { test, expect } from '@playwright/test';

const VIEWPORTS = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

test.describe('Visual Regression', () => {
  for (const viewport of VIEWPORTS) {
    test(`homepage — ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`, { fullPage: true });
    });
  }
});
```

---

## Test File Naming Convention

| Pattern | Example | Framework |
|---------|---------|-----------|
| `src/test/components/{Name}.test.tsx` | `Header.test.tsx` | Vitest (unit) |
| `src/test/pages/{Name}.test.tsx` | `LoginPage.test.tsx` | Vitest (unit) |
| `tests/e2e/{feature}.spec.ts` | `withdrawal-flow.spec.ts` | Playwright (E2E) |
| `tests/e2e/visual-{feature}.spec.ts` | `visual-homepage.spec.ts` | Playwright (visual) |

## Test Commands Reference

```bash
# Unit tests
npm run test              # Run all Vitest tests
npm run test:watch        # Watch mode
npx vitest src/test/components/Header.test.tsx  # Single file

# E2E tests
npm run test:e2e          # Run all Playwright tests
npm run test:e2e:ui       # Interactive debug mode
npm run test:e2e:report   # Open HTML report
npx playwright test tests/e2e/customers.spec.ts  # Single file

# Visual regression
npm run test:e2e:visual              # Compare against baselines
npm run test:e2e:visual-update       # Update baselines

# All tests
npm run test:all          # Vitest + Playwright
```
