/**
 * E2E tests: Admin Withdrawal Approvals
 *
 * Tests the admin-facing withdrawal approval dashboard:
 *   1. Admin views pending withdrawal requests
 *   2. Admin approves a pending withdrawal
 *   3. Admin rejects a pending withdrawal with a reason
 *   4. Status filters work correctly
 *   5. Non-admin users are denied access
 *
 * Pages tested:
 *   - /dashboard/admin/withdrawals (admin withdrawal management)
 *
 * API endpoints mocked:
 *   - GET  /api/auth/profile              — admin/instructor profiles
 *   - GET  /api/withdrawals/              — paginated withdrawals with status filter
 *   - PATCH /api/withdrawals/:id/approve  — approve a withdrawal
 *   - PATCH /api/withdrawals/:id/reject   — reject a withdrawal
 */

import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

async function captureConsoleErrors(page: import("@playwright/test").Page) {
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  return errors;
}

function filterNextJSWarnings(errors: string[]) {
  return errors.filter(
    (e) =>
      !e.includes(" hydration ") &&
      !e.includes("Warning:") &&
      !e.includes("next") &&
      !e.includes("favicon") &&
      !e.includes("404") &&
      !e.includes("Failed to load") &&
      !e.includes("ERR_CONNECTION_REFUSED") &&
      !e.includes("fetch") &&
      !e.includes("NetworkError")
  );
}

// ═══════════════════════════════════════════════════════════════════
// Mock Data
// ═══════════════════════════════════════════════════════════════════

const ADMIN_PROFILE = {
  id: 99,
  username: "admin_mike",
  first_name: "Mike",
  last_name: "Admin",
  email: "mike@example.com",
  role: "admin",
};

const INSTRUCTOR_PROFILE = {
  id: 1,
  username: "instructor_jane",
  first_name: "Jane",
  last_name: "Doe",
  email: "jane@example.com",
  role: "instructor",
};

interface Withdrawal {
  id: number;
  instructor: number;
  instructor_name: string;
  amount: number;
  current_balance: number;
  status: string;
  status_display: string;
  payment_method: string;
  payment_method_display: string;
  payment_details: Record<string, unknown>;
  notes: string;
  reference: string;
  processed_by: number | null;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
  can_cancel: boolean;
  is_completed: boolean;
  is_pending: boolean;
}

function makePendingWithdrawal(overrides: Partial<Withdrawal> = {}): Withdrawal {
  return {
    id: 1,
    instructor: 1,
    instructor_name: "Jane Doe",
    amount: 200,
    current_balance: 1250,
    status: "pending",
    status_display: "Pending",
    payment_method: "paypal",
    payment_method_display: "PayPal",
    payment_details: {},
    notes: "",
    reference: "",
    processed_by: null,
    created_at: "2026-07-24T10:00:00Z",
    updated_at: "2026-07-24T10:00:00Z",
    processed_at: null,
    can_cancel: true,
    is_completed: false,
    is_pending: true,
    ...overrides,
  };
}

// ═══════════════════════════════════════════════════════════════════
// Route Helpers
// ═══════════════════════════════════════════════════════════════════

async function mockAdminSession(page: import("@playwright/test").Page) {
  // Set localStorage token so AuthGuard and RTK Query baseApi see it
  await page.addInitScript(() => {
    localStorage.setItem('lms_token', 'test-mock-admin-token');
  });
  await page.route("**/api/auth/profile", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ADMIN_PROFILE) })
  );
}

async function mockWithdrawalsList(
  page: import("@playwright/test").Page,
  withdrawals: Withdrawal[],
  count?: number
) {
  // Register the list route with a precise URL matcher so it doesn't
  // catch approve/reject/detail URLs — those are handled by more specific
  // route handlers registered later in each test.
  await page.route(/\/api\/withdrawals\/\?/, (route) => {
    const url = route.request().url();
    // Only match the paginated list endpoint (has query params)
    if (url.includes("/api/withdrawals/") && !url.includes("/summary/") && !url.includes("/create/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          results: withdrawals,
          count: count ?? withdrawals.length,
          next: null,
          previous: null,
        }),
      });
    }
    return route.fallback();
  });
}

// ═══════════════════════════════════════════════════════════════════
// Test Suite
// ═══════════════════════════════════════════════════════════════════

test.describe("Admin Withdrawal Approvals — E2E", () => {
  // ── 1. Auth & Access Control ─────────────────────────────────────

  test.describe("Auth & Access Control", () => {
    test("admin sees the withdrawal approvals page", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [
        makePendingWithdrawal({ id: 1, amount: 200 }),
        makePendingWithdrawal({ id: 2, amount: 350, instructor_name: "Bob Smith" }),
      ]);
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("h1")).toContainText("Withdrawal Approvals");
      await expect(page.locator("text=Review and manage instructor withdrawal requests")).toBeVisible();
    });

    test("instructor is denied access to admin withdrawals page", async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('lms_token', 'test-mock-instructor-token');
      });
      await page.route("**/api/auth/profile", (route) =>
        route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(INSTRUCTOR_PROFILE) })
      );
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("text=This page is only available for administrators")).toBeVisible();
      await expect(page.locator("text=Withdrawal Approvals")).toHaveCount(0);
    });

    test("unauthenticated user is denied access", async ({ page }) => {
      await page.route("**/api/auth/profile", (route) =>
        route.fulfill({ status: 401, contentType: "application/json", body: "{}" })
      );
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("text=This page is only available for administrators")).toBeVisible();
    });
  });

  // ── 2. Withdrawals Table ────────────────────────────────────────

  test.describe("Withdrawals Table Display", () => {
    test("renders pending withdrawals in a table", async ({ page }) => {
      await mockAdminSession(page);
      const withdrawals = [
        makePendingWithdrawal({ id: 1, amount: 200 }),
        makePendingWithdrawal({ id: 2, amount: 500, instructor_name: "Alice Johnson", payment_method: "bank_transfer", payment_method_display: "Bank Transfer" }),
        makePendingWithdrawal({ id: 3, amount: 150 }),
      ];
      await mockWithdrawalsList(page, withdrawals);
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // Table rows for each withdrawal
      const rows = page.locator("tbody tr");
      await expect(rows).toHaveCount(3);

      // Amounts
      await expect(page.locator("text=$200")).toBeVisible();
      await expect(page.locator("text=$500")).toBeVisible();
      await expect(page.locator("text=$150")).toBeVisible();

      // Instructor names
      // Use .first() because "Jane Doe" may match sidebar AND table
      await expect(page.locator("text=Jane Doe").first()).toBeVisible();
      await expect(page.locator("text=Alice Johnson")).toBeVisible();
    });

    test("shows empty state when no withdrawals exist", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [], 0);
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("text=No withdrawals found")).toBeVisible();
    });
  });

  // ── 3. Status Filters ───────────────────────────────────────────

  test.describe("Status Filters", () => {
    test("filter buttons toggle active state", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [makePendingWithdrawal()]);
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // "all" should be active by default
      const allBtn = page.locator("button", { hasText: "all" });
      await expect(allBtn).toHaveClass(/text-white/);

      // Click "pending"
      const pendingBtn = page.locator("button", { hasText: "pending" });
      await pendingBtn.click();
      await expect(pendingBtn).toHaveClass(/text-white/);
      await expect(allBtn).not.toHaveClass(/text-white/);

      // Click "approved"
      const approvedBtn = page.locator("button", { hasText: "approved" });
      await approvedBtn.click();
      await expect(approvedBtn).toHaveClass(/text-white/);
      await expect(pendingBtn).not.toHaveClass(/text-white/);
    });
  });

  // ── 4. Approve Withdrawal ───────────────────────────────────────

  test.describe("Approve Withdrawal", () => {
    test("approves a pending withdrawal and shows success message", async ({ page }) => {
      await mockAdminSession(page);
      const pending = makePendingWithdrawal({ id: 10, amount: 300 });
      await mockWithdrawalsList(page, [pending]);

      // Mock approve endpoint
      let approveCalled = false;
      await page.route("**/api/withdrawals/10/approve/", (route) => {
        if (route.request().method() === "PATCH") {
          approveCalled = true;
          return route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              ...pending,
              status: "approved",
              status_display: "Approved",
              processed_by: 99,
              processed_at: "2026-07-25T12:00:00Z",
            }),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // Click Approve — the action button has title="Approve withdrawal";
      // a plain hasText "Approve" would also match the "approved" filter chip.
      const approveBtn = page.locator('button[title="Approve withdrawal"]').first();
      await expect(approveBtn).toBeVisible();
      await approveBtn.click();

      // Verify success message
      await expect(
        page.locator("text=/Withdrawal #10 approved successfully/i")
      ).toBeVisible({ timeout: 10000 });
      expect(approveCalled).toBe(true);
    });

    test("shows error when approval fails", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [makePendingWithdrawal({ id: 20, amount: 400 })]);

      await page.route("**/api/withdrawals/20/approve/", (route) => {
        if (route.request().method() === "PATCH") {
          return route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ message: "Withdrawal has already been processed." }),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // Use the title-based locator so we don't hit the "approved" filter chip.
      await page.locator('button[title="Approve withdrawal"]').first().click();

      await expect(
        page.locator("text=Withdrawal has already been processed.")
      ).toBeVisible({ timeout: 10000 });
    });
  });

  // ── 5. Reject Withdrawal ────────────────────────────────────────

  test.describe("Reject Withdrawal", () => {
    test("rejects a pending withdrawal with a reason", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [makePendingWithdrawal({ id: 30, amount: 250 })]);

      let rejectPayload: any = null;
      await page.route("**/api/withdrawals/30/reject/", (route) => {
        if (route.request().method() === "PATCH") {
          rejectPayload = route.request().postDataJSON();
          return route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              ...makePendingWithdrawal({ id: 30 }),
              status: "rejected",
              status_display: "Rejected",
            }),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // Click Reject — title-based so it can't match the "rejected" filter chip.
      await page.locator('button[title="Reject withdrawal"]').first().click();

      // Fill in rejection reason
      const reasonInput = page.locator('input[placeholder="Reason (optional)"]');
      await expect(reasonInput).toBeVisible();
      await reasonInput.fill("Invalid account details");

      // Click Confirm
      await page.locator("button", { hasText: "Confirm" }).click();

      // Verify success
      await expect(
        page.locator("text=/Withdrawal #30 rejected/i")
      ).toBeVisible({ timeout: 10000 });
      expect(rejectPayload).toBeDefined();
    });

    test("cancels rejection when Cancel is clicked", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [makePendingWithdrawal({ id: 40, amount: 175 })]);

      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // Click Reject — title-based so it can't match the "rejected" filter chip.
      await page.locator('button[title="Reject withdrawal"]').first().click();

      const reasonInput = page.locator('input[placeholder="Reason (optional)"]');
      await expect(reasonInput).toBeVisible();

      // Click Cancel to dismiss — exact text so the "cancelled" filter chip
      // (case-insensitive substring match) isn't picked up.
      await page.getByRole("button", { name: "Cancel", exact: true }).click();

      // The reject form should be gone and the Reject button should reappear
      await expect(reasonInput).toHaveCount(0);
      await expect(page.locator('button[title="Reject withdrawal"]')).toBeVisible();
    });
  });

  // ── 6. Back Navigation ──────────────────────────────────────────

  test.describe("Navigation", () => {
    test("has a back-to-dashboard link", async ({ page }) => {
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [makePendingWithdrawal()]);
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      // The header back link is scoped by its exact accessible text; the
      // sidebar contains other links to /dashboard.
      const backLink = page.getByRole("link", { name: "Back to Dashboard" });
      await expect(backLink).toBeVisible();
      await expect(backLink).toContainText("Back to Dashboard");
    });
  });

  // ── 7. Console Errors ───────────────────────────────────────────

  test.describe("Console Error Checks", () => {
    test("admin withdrawals page loads without critical errors", async ({ page }) => {
      const errors = await captureConsoleErrors(page);
      await mockAdminSession(page);
      await mockWithdrawalsList(page, [makePendingWithdrawal()]);
      await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("h1")).toContainText("Withdrawal Approvals");

      const criticalErrors = filterNextJSWarnings(errors);
      expect(criticalErrors, "Should have no critical console errors").toHaveLength(0);
    });
  });
});
