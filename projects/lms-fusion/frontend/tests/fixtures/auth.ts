import { test as base, Page } from '@playwright/test';

/**
 * Shared authentication fixture for LMS E2E tests.
 *
 * Mocks the `/apis/auth/profile/` endpoint so dashboard pages render
 * with the correct role context without needing a real backend.
 *
 * ## Usage
 *
 * ```ts
 * import { test, expect } from '../../fixtures/auth';
 *
 * test('instructor page', async ({ instructorPage }) => {
 *   await instructorPage.goto('/dashboard/courses');
 *   await expect(instructorPage.locator('h1')).toContainText('My Courses');
 * });
 *
 * test('admin page', async ({ adminPage }) => {
 *   await adminPage.goto('/dashboard/admin/withdrawals');
 *   // renders admin-only content
 * });
 * ```
 */

// ── Mock profiles ──────────────────────────────────────────

export interface LMSProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar: string;
  role: 'student' | 'instructor' | 'admin';
  bio: string;
  date_joined: string;
  last_login: string;
}

export const STUDENT_PROFILE: LMSProfile = {
  id: 1,
  username: 'student',
  email: 'student@structa.cloud',
  first_name: 'Test',
  last_name: 'Student',
  avatar: '',
  role: 'student',
  bio: '',
  date_joined: '2025-01-01T00:00:00Z',
  last_login: '2025-06-01T00:00:00Z',
};

export const INSTRUCTOR_PROFILE: LMSProfile = {
  id: 2,
  username: 'instructor',
  email: 'instructor@structa.cloud',
  first_name: 'Test',
  last_name: 'Instructor',
  avatar: '',
  role: 'instructor',
  bio: 'Experienced instructor',
  date_joined: '2025-01-01T00:00:00Z',
  last_login: '2025-06-01T00:00:00Z',
};

export const ADMIN_PROFILE: LMSProfile = {
  id: 3,
  username: 'admin',
  email: 'admin@structa.cloud',
  first_name: 'Test',
  last_name: 'Admin',
  avatar: '',
  role: 'admin',
  bio: '',
  date_joined: '2025-01-01T00:00:00Z',
  last_login: '2025-06-01T00:00:00Z',
};

// ── Mock helpers ───────────────────────────────────────────

export async function mockAuthProfile(page: Page, profile: LMSProfile): Promise<void> {
  await page.route('**/apis/auth/profile/', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(profile),
    })
  );
}

// ── Custom fixtures ────────────────────────────────────────

type AuthFixtures = {
  studentPage: Page;
  instructorPage: Page;
  adminPage: Page;
};

export const test = base.extend<AuthFixtures>({
  studentPage: async ({ page }, use) => {
    await mockAuthProfile(page, STUDENT_PROFILE);
    await use(page);
  },

  instructorPage: async ({ page }, use) => {
    await mockAuthProfile(page, INSTRUCTOR_PROFILE);
    await use(page);
  },

  adminPage: async ({ page }, use) => {
    await mockAuthProfile(page, ADMIN_PROFILE);
    await use(page);
  },
});

export { expect } from '@playwright/test';
