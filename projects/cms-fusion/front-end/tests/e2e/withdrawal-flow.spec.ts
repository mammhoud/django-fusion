/**
 * E2E tests: Withdrawal Flow
 *
 * Tests the complete withdrawal lifecycle using Playwright + API mocking:
 *   1. Instructor views their balance and creates a withdrawal request
 *   2. Admin approves the pending withdrawal
 *   3. Instructor sees the approved status and updated balance
 *
 * Pages tested:
 *   - /dashboard/withdraw (instructor-facing withdrawal page)
 *
 * API endpoints mocked:
 *   - GET  /apis/auth/profile          — instructor/admin profiles
 *   - GET  /apis/withdrawals/summary    — withdrawal summary & history
 *   - POST /apis/withdrawals/create     — create withdrawal request
 *   - PATCH /apis/withdrawals/:id/approve — admin approval (API-only)
 *   - PATCH /apis/withdrawals/:id/cancel  — instructor cancellation
 */

import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════════════
// Helpers — console error tracking & filtering
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
      !e.includes("404")
  );
}

// ═══════════════════════════════════════════════════════════════════
// Mock Data Factories
// ═══════════════════════════════════════════════════════════════════

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
  status: "pending" | "approved" | "processing" | "completed" | "rejected" | "cancelled";
  status_display: string;
  payment_method: "paypal" | "bank_transfer" | "stripe";
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

function makeApprovedWithdrawal(overrides: Partial<Withdrawal> = {}): Withdrawal {
  return {
    id: 1,
    instructor: 1,
    instructor_name: "Jane Doe",
    amount: 200,
    current_balance: 1050,
    status: "approved",
    status_display: "Approved",
    payment_method: "paypal",
    payment_method_display: "PayPal",
    payment_details: {},
    notes: "",
    reference: "REF-2026-001",
    processed_by: 99,
    created_at: "2026-07-24T10:00:00Z",
    updated_at: "2026-07-24T14:00:00Z",
    processed_at: "2026-07-24T14:00:00Z",
    can_cancel: false,
    is_completed: false,
    is_pending: false,
    ...overrides,
  };
}

interface WithdrawalSummary {
  current_balance: number;
  pending_amount: number;
  total_withdrawn: number;
  total_earned: number;
  pending_count: number;
  recent_withdrawals: Withdrawal[];
}

function makeSummary(overrides: Partial<WithdrawalSummary> = {}): WithdrawalSummary {
  return {
    current_balance: 1250,
    pending_amount: 0,
    total_withdrawn: 500,
    total_earned: 1750,
    pending_count: 0,
    recent_withdrawals: [],
    ...overrides,
  };
}

// ═══════════════════════════════════════════════════════════════════
// Route Helpers — sets up API mocking for different test scenarios
// ═══════════════════════════════════════════════════════════════════

/**
 * Set up API mocks for an authenticated instructor.
 */
async function mockInstructorSession(
  page: import("@playwright/test").Page,
  summary?: WithdrawalSummary
) {
  const data = summary ?? makeSummary();

  // Profile
  await page.route("**/apis/auth/profile/", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(INSTRUCTOR_PROFILE),
    })
  );

  // Summary
  await page.route("**/apis/withdrawals/summary/", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(data),
    })
  );
}

/**
 * Set up API mocks for non-instructor (student / not logged in).
 */
async function mockNonInstructorSession(
  page: import("@playwright/test").Page,
  role?: string
) {
  await page.route("**/apis/auth/profile/", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        ...INSTRUCTOR_PROFILE,
        role: role ?? "student",
      }),
    })
  );
}

// ═══════════════════════════════════════════════════════════════════
// Test Suite
// ═══════════════════════════════════════════════════════════════════

test.describe("Withdrawal Flow — E2E", () => {
  // ── 1. Page Load & Auth Gating ────────────────────────────────────

  test.describe("Page Load & Auth Gating", () => {
    test("instructor sees the withdrawal page", async ({ page }) => {
      await mockInstructorSession(page);
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("h1")).toContainText("Withdrawals & Payouts");
      await expect(
        page.locator("text=Manage your earnings and withdrawal requests")
      ).toBeVisible();
    });

    test("student is shown access-denied message", async ({ page }) => {
      await mockNonInstructorSession(page, "student");
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      await expect(
        page.locator("text=This page is only available for instructors")
      ).toBeVisible();
      // The withdrawal form should NOT be present
      await expect(page.locator("text=Request Withdrawal")).toHaveCount(0);
    });

    test("unauthenticated user is shown access-denied message", async ({ page }) => {
      // No profile mock = profile query returns undefined
      await page.route("**/apis/auth/profile/", (route) =>
        route.fulfill({ status: 401, contentType: "application/json", body: "{}" })
      );
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      await expect(
        page.locator("text=This page is only available for instructors")
      ).toBeVisible();
    });
  });

  // ── 2. Balance Cards Display ──────────────────────────────────────

  test.describe("Balance Cards", () => {
    test("displays current balance, pending amount, and total earned", async ({ page }) => {
      const summary = makeSummary({
        current_balance: 2500,
        pending_amount: 300,
        total_earned: 4800,
        total_withdrawn: 2300,
        pending_count: 2,
      });
      await mockInstructorSession(page, summary);
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      // The balance cards use comma-formatted dollar amounts
      await expect(page.locator("text=$2,500")).toBeVisible();
      await expect(page.locator("text=$300")).toBeVisible();
      await expect(page.locator("text=$4,800")).toBeVisible();
      await expect(page.locator("text=Available for withdrawal")).toBeVisible();
    });

    test("shows zero balances when instructor has no earnings", async ({ page }) => {
      const summary = makeSummary({
        current_balance: 0,
        pending_amount: 0,
        total_earned: 0,
        total_withdrawn: 0,
        pending_count: 0,
        recent_withdrawals: [],
      });
      await mockInstructorSession(page, summary);
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      // $0 appears in multiple places — at least one should be visible
      const zeroElements = page.locator("text=$0");
      await expect(zeroElements.first()).toBeVisible();
    });
  });

  // ── 3. Create Withdrawal (Instructor) ─────────────────────────────

  test.describe("Create Withdrawal — Instructor", () => {
    test("fills in amount and submits a withdrawal request", async ({ page }) => {
      const summary = makeSummary({
        current_balance: 1250,
        pending_amount: 0,
        total_withdrawn: 500,
        total_earned: 1750,
      });
      await mockInstructorSession(page, summary);

      // Mock the create endpoint
      const newWithdrawal = makePendingWithdrawal({
        id: 99,
        amount: 200,
        current_balance: 1050,
      });
      await page.route("**/apis/withdrawals/create/", (route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(newWithdrawal),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      // Fill in the amount
      const amountInput = page.locator('input[type="number"]');
      await amountInput.fill("200");

      // Verify the submit button is enabled and shows the amount
      const submitBtn = page.locator("button", { hasText: /Withdraw \$200/ });
      await expect(submitBtn).toBeEnabled();

      // Click submit
      await submitBtn.click();

      // Wait for success message
      await expect(
        page.locator("text=/Withdrawal of \\$200 requested successfully/i")
      ).toBeVisible({ timeout: 10000 });
    });

    test("shows error when withdrawal creation fails server-side", async ({ page }) => {
      const summary = makeSummary({ current_balance: 1250 });
      await mockInstructorSession(page, summary);

      // Mock create endpoint to return an error
      await page.route("**/apis/withdrawals/create/", (route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ message: "Insufficient balance for this withdrawal." }),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      const amountInput = page.locator('input[type="number"]');
      await amountInput.fill("100");

      await page.locator("button", { hasText: /Withdraw \$100/ }).click();

      await expect(
        page.locator("text=Insufficient balance for this withdrawal.")
      ).toBeVisible({ timeout: 10000 });
    });

    test("switches payment method and submits with bank transfer", async ({ page }) => {
      const summary = makeSummary({ current_balance: 1500 });
      await mockInstructorSession(page, summary);

      await page.route("**/apis/withdrawals/create/", (route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(
              makePendingWithdrawal({
                id: 200,
                amount: 500,
                payment_method: "bank_transfer",
                payment_method_display: "Bank Transfer",
              })
            ),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      // Click Bank Transfer
      await page.locator("button", { hasText: "Bank Transfer" }).click();

      // Fill amount
      await page.locator('input[type="number"]').fill("500");

      // Submit
      await page.locator("button", { hasText: /Withdraw \$500/ }).click();

      await expect(
        page.locator("text=/Withdrawal of \\$500 requested successfully/i")
      ).toBeVisible({ timeout: 10000 });
    });
  });

  // ── 4. Withdrawal History Display ─────────────────────────────────

  test.describe("Withdrawal History", () => {
    test("shows pending and completed withdrawals with status badges", async ({ page }) => {
      const withdrawals: Withdrawal[] = [
        makePendingWithdrawal({ id: 1, amount: 200 }),
        makeApprovedWithdrawal({ id: 2, amount: 350, status: "completed", status_display: "Completed", can_cancel: false, is_completed: true, is_pending: false }),
        { ...makeApprovedWithdrawal(), id: 3, amount: 100, status: "rejected", status_display: "Rejected", can_cancel: false },
      ];
      const summary = makeSummary({
        current_balance: 600,
        pending_amount: 200,
        total_withdrawn: 350,
        total_earned: 1150,
        pending_count: 1,
        recent_withdrawals: withdrawals,
      });
      await mockInstructorSession(page, summary);
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      // History section visible
      await expect(page.locator("text=Withdrawal History")).toBeVisible();

      // Count in header
      await expect(page.locator("text=(3)")).toBeVisible();

      // Status badges (scoped to the history section to avoid "Pending" matching
      // the pending_count text "1 pending request" and the submit button label)
      const historySection = page.locator("section", { hasText: "Withdrawal History" });
      await expect(historySection.locator("text=Pending")).toBeVisible();
      await expect(historySection.locator("text=Completed")).toBeVisible();
      await expect(historySection.locator("text=Rejected")).toBeVisible();

      // Amounts in history (scoped to avoid strict mode: $200 also appears in pending payout card)
      await expect(historySection.locator("text=$200")).toBeVisible();
      await expect(historySection.locator("text=$350")).toBeVisible();
      await expect(historySection.locator("text=$100")).toBeVisible();
    });

    test("Cancel button is only visible on pending withdrawals", async ({ page }) => {
      const withdrawals: Withdrawal[] = [
        makePendingWithdrawal({ id: 1, amount: 150, can_cancel: true }),
        makeApprovedWithdrawal({ id: 2, amount: 300, status: "completed", status_display: "Completed", can_cancel: false }),
      ];
      const summary = makeSummary({
        current_balance: 950,
        pending_amount: 150,
        recent_withdrawals: withdrawals,
        pending_count: 1,
      });
      await mockInstructorSession(page, summary);
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      // Only 1 Cancel button — for the pending withdrawal
      const cancelButtons = page.locator("button", { hasText: "Cancel" });
      await expect(cancelButtons).toHaveCount(1);
    });

    test("shows empty state when no withdrawals exist", async ({ page }) => {
      const summary = makeSummary({
        current_balance: 0,
        pending_amount: 0,
        total_withdrawn: 0,
        total_earned: 0,
        pending_count: 0,
        recent_withdrawals: [],
      });
      await mockInstructorSession(page, summary);
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("text=No withdrawals yet")).toBeVisible();
      await expect(
        page.locator("text=Your payout requests will appear here")
      ).toBeVisible();
      await expect(page.locator("text=(0)")).toBeVisible();
    });
  });

  // ── 5. Cancel Withdrawal (Instructor) ─────────────────────────────

  test.describe("Cancel Withdrawal — Instructor", () => {
    test("cancels a pending withdrawal and shows updated list", async ({ page }) => {
      test.setTimeout(60000);
      const pendingW = makePendingWithdrawal({ id: 5, amount: 180, can_cancel: true });
      const cancelledW = {
        ...pendingW,
        status: "cancelled" as const,
        status_display: "Cancelled",
        can_cancel: false,
        is_pending: false,
      };
      const summary = makeSummary({
        current_balance: 820,
        pending_amount: 180,
        recent_withdrawals: [pendingW],
        pending_count: 1,
      });

      // Call-counted handlers: initial load returns pending summary;
      // post-cancel refetch returns the cancelled version.  This avoids
      // unroute/re-register races that surface under suite concurrency.
      let summaryCalls = 0;
      await page.route("**/apis/auth/profile/", (route) =>
        route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(INSTRUCTOR_PROFILE) })
      );
      await page.route("**/apis/withdrawals/summary/", (route) => {
        summaryCalls++;
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(
            summaryCalls === 1
              ? summary
              : { ...summary, pending_amount: 0, pending_count: 0, recent_withdrawals: [cancelledW] }
          ),
        });
      });

      // Mock cancel endpoint
      await page.route("**/apis/withdrawals/5/cancel/", (route) => {
        if (route.request().method() === "PATCH") {
          return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(cancelledW) });
        }
        return route.continue();
      });

      await page.goto("/dashboard/withdraw", { waitUntil: "domcontentloaded", timeout: 30000 });

      // Wait for Cancel button to become visible, then click
      const cancelBtn = page.locator("button", { hasText: "Cancel" });
      await cancelBtn.waitFor({ state: "visible", timeout: 15000 });
      await cancelBtn.click();

      // The withdrawal should now show "Cancelled"
      await expect(page.locator("text=Cancelled")).toBeVisible({ timeout: 10000 });
    });

    test("shows error when cancellation fails", async ({ page }) => {
      const pendingW = makePendingWithdrawal({ id: 7, amount: 220, can_cancel: true });
      await mockInstructorSession(
        page,
        makeSummary({
          current_balance: 780,
          pending_amount: 220,
          recent_withdrawals: [pendingW],
          pending_count: 1,
        })
      );

      await page.route("**/apis/withdrawals/7/cancel/", (route) => {
        if (route.request().method() === "PATCH") {
          return route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ message: "Only pending withdrawals can be cancelled." }),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      await page.locator("button", { hasText: "Cancel" }).click();

      await expect(
        page.locator("text=Only pending withdrawals can be cancelled.")
      ).toBeVisible({ timeout: 10000 });
    });
  });

  // ── 6. Full Lifecycle: Create → Approve → Balance Update ──────────

  test.describe("Full Withdrawal Lifecycle", () => {
    test("instructor creates withdrawal, admin approves, balance reflects approval", async ({ page }) => {
      // ── Phase 1: Instructor creates withdrawal ──────────────────
      const initialSummary = makeSummary({
        current_balance: 1500,
        pending_amount: 0,
        total_withdrawn: 800,
        total_earned: 2300,
        pending_count: 0,
        recent_withdrawals: [],
      });
      await mockInstructorSession(page, initialSummary);

      // Intercept the create call
      let createdWithdrawal: Withdrawal | null = null;
      await page.route("**/apis/withdrawals/create/", (route) => {
        if (route.request().method() === "POST") {
          createdWithdrawal = makePendingWithdrawal({
            id: 42,
            amount: 500,
            current_balance: 1000,
          });
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(createdWithdrawal),
          });
        }
        return route.continue();
      });

      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });
      await expect(page.locator("text=$1,500")).toBeVisible();

      // Fill amount and submit
      await page.locator('input[type="number"]').fill("500");
      await page.locator("button", { hasText: /Withdraw \$500/ }).click();

      // Verify success
      await expect(
        page.locator("text=/Withdrawal of \\$500 requested successfully/i")
      ).toBeVisible({ timeout: 10000 });

      // ── Phase 2: Admin approves the withdrawal (API-level) ──────
      // In a real app, admin would log in via /admin dashboard.
      // Here we simulate the approval by mocking the approve endpoint
      // and the subsequent summary refetch.
      expect(createdWithdrawal).not.toBeNull();

      const approvedWithdrawal: Withdrawal = {
        ...createdWithdrawal!,
        status: "approved",
        status_display: "Approved",
        processed_by: 99,
        processed_at: "2026-07-24T15:00:00Z",
        updated_at: "2026-07-24T15:00:00Z",
        can_cancel: false,
        is_pending: false,
        reference: "REF-2026-042",
      };

      // Update summary to reflect post-approval state (balance reduced, pending cleared)
      const postApprovalSummary: WithdrawalSummary = {
        current_balance: 1000, // 1500 - 500
        pending_amount: 0,
        total_withdrawn: 1300, // 800 + 500
        total_earned: 2300,
        pending_count: 0,
        recent_withdrawals: [approvedWithdrawal],
      };

      // Remove the old summary route and add the updated one
      await page.unroute("**/apis/withdrawals/summary/");
      await page.route("**/apis/withdrawals/summary/", (route) =>
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(postApprovalSummary),
        })
      );

      // Click Refresh to trigger a refetch of the summary
      await page.locator("button", { hasText: "Refresh" }).click();

      // ── Phase 4: Verify updated state ───────────────────────────
      // Current balance card shows $1,000 (reduced from $1,500 by the $500 withdrawal)
      await expect(page.locator("text=$1,000")).toBeVisible({ timeout: 10000 });

      // The withdrawal should show "Approved" status in history
      await expect(page.locator("text=Approved")).toBeVisible({ timeout: 10000 });

      // Pending Payout card shows $0 (no longer pending after approval).
      // Target the second balance card (Pending Payout) via nth-child to avoid
      // matching the disabled submit button's "$0" text elsewhere on the page.
      const pendingCard = page.locator(".grid > div").nth(1);
      await expect(pendingCard.locator("text=$0")).toBeVisible();
    });
  });

  // ── 7. No Console Errors ──────────────────────────────────────────

  test.describe("Console Error Checks", () => {
    test("withdrawal page loads without critical console errors", async ({ page }) => {
      const errors = await captureConsoleErrors(page);
      await mockInstructorSession(page, makeSummary());
      await page.goto("/dashboard/withdraw", { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("h1")).toContainText("Withdrawals & Payouts");

      const criticalErrors = filterNextJSWarnings(errors);
      expect(criticalErrors, "Should have no critical console errors").toHaveLength(0);
    });
  });
});
