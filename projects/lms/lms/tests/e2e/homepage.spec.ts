import { test, expect } from "@playwright/test";

/**
 * Homepage Smoke Tests — lms/lms
 *
 * Tests are split into two groups:
 *   1. Static checks — always pass (title, header, footer, DOM classes)
 *   2. Backend-dependent — require a running CMS backend on the API URL
 *
 * If the CMS backend isn't reachable, backend-dependent tests are skipped
 * automatically so CI stays green while the lms-e2e workflow is still being
 * set up with a full backend.
 */

// ── Pre-flight: check if the CMS backend is reachable ──────────────
let backendAvailable = false;

test.beforeAll(async ({ request }) => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const res = await request.get(`${apiUrl}/apis/fusion/health`, {
      timeout: 5000,
    });
    backendAvailable = res.ok();
  } catch {
    backendAvailable = false;
  }
});

// ═══════════════════════════════════════════════════════════════════
// Group 1 — Static checks (always run)
// ═══════════════════════════════════════════════════════════════════

test.describe("Homepage — Static", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("page title is 'LMS - Learning Management System'", async ({
    page,
  }) => {
    await expect(page).toHaveTitle("LMS - Learning Management System");
  });

  test("header is visible with logo text", async ({ page }) => {
    const header = page.locator("header");
    await expect(header).toBeVisible();
    await expect(header).toContainText("LMS");
  });

  test("footer is visible", async ({ page }) => {
    await expect(page.locator("footer")).toBeVisible();
  });

  test("hero section renders with gradient background", async ({ page }) => {
    await expect(page.locator(".section-hero")).toBeVisible();
  });

  test("page has no forbidden indigo or purple classes (CTC teal migration)", async ({
    page,
  }) => {
    const forbidden = page.locator('[class*="indigo-"], [class*="purple-"]');
    await expect(forbidden).toHaveCount(0);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Group 2 — Backend-dependent (skipped when CMS is unreachable)
// ═══════════════════════════════════════════════════════════════════

test.describe("Homepage — Backend-Dependent", () => {
  test.beforeEach(async ({ page }) => {
    test.skip(!backendAvailable, "CMS backend not reachable — skipping");
    await page.goto("/");
    // Wait for the hero heading to appear (handles loading/error states gracefully)
    await page.locator(".section-hero h1").waitFor({ timeout: 10000 });
  });

  test("hero heading renders from CMS or fallback", async ({ page }) => {
    await expect(
      page.locator(".section-hero h1")
    ).toContainText("Learn Without Limits");
  });

  test("hero CTA links are present", async ({ page }) => {
    const hero = page.locator(".section-hero");
    await expect(
      hero.getByRole("link", { name: /explore courses/i })
    ).toBeVisible();
    await expect(
      hero.getByRole("link", { name: /get started free/i })
    ).toBeVisible();
  });

  test("featured courses section renders", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /featured courses/i })
    ).toBeVisible();
  });

  test("CTA section heading renders", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /start learning today/i })
    ).toBeVisible();
  });

  test("instructors section renders", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /expert instructors/i })
    ).toBeVisible();
  });

  test("page has CTC teal theme component classes", async ({ page }) => {
    const tealElements = page.locator(
      ".section-hero, .card, .btn-primary, .card-gradient"
    );
    await expect(tealElements.first()).toBeVisible();
  });
});
