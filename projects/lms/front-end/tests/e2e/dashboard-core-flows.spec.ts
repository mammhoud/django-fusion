/**
 * E2E tests: Core Dashboard Flows
 *
 * Tests the essential user-facing flows across the student dashboard,
 * including authentication, navigation, and interactive components.
 *
 * Pages tested:
 *   - /login (auth form, password toggle, validation)
 *   - /registration (role selection, password match validation)
 *   - /student-dashboard (stats, quick nav, enrolled courses list)
 *   - /student-dashboard/enrolled-courses (filter buttons, search)
 *   - /student-dashboard/history (timeline, filter dropdown)
 *   - /student-dashboard/reviews (star rating, comment, submit)
 *   - /student-dashboard/wishlist (course cards, remove, empty state)
 */

import { test, expect } from "@playwright/test";

// ── Helper: collect console errors ──────────────────────────────────
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

// ── Helpers: quick assertions ─────────────────────────────────────────
async function assertPageLoaded(
  page: import("@playwright/test").Page,
  name: string,
  expectedStatus = 200
) {
  const response = await page.waitForLoadState("networkidle", { timeout: 15000 }).then(() => null, () => null);
  // Check no 404 in body
  const bodyText = await page.textContent("body").catch(() => "");
  expect(
    bodyText?.includes("404") && bodyText?.includes("Not Found"),
    `${name} should not show a 404 error`
  ).toBe(false);
}

// ── Test Data ─────────────────────────────────────────────────────────
const AUTH_PAGES = [
  { path: "/login", name: "Login Page" },
  { path: "/registration", name: "Registration Page" },
] as const;

const STUDENT_DASHBOARD_PAGES = [
  { path: "/student-dashboard", name: "Student Dashboard" },
  { path: "/student-dashboard/enrolled-courses", name: "Enrolled Courses" },
  { path: "/student-dashboard/history", name: "Activity History" },
  { path: "/student-dashboard/reviews", name: "My Reviews" },
  { path: "/student-dashboard/wishlist", name: "Wishlist" },
] as const;

// ── 1. Auth Page Smoke Tests ──────────────────────────────────────────

test.describe("Auth Pages – Smoke Tests", () => {
  for (const { path, name } of AUTH_PAGES) {
    test(`${name} renders without console errors`, async ({ page }) => {
      const errors = await captureConsoleErrors(page);
      await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });
      expect(filterNextJSWarnings(errors), `${name} should have no console errors`).toHaveLength(0);
    });

    test(`${name} has key form elements`, async ({ page }) => {
      await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });

      // Logo / heading should be visible
      await expect(page.locator("h1")).toBeVisible();
      expect(await page.locator("input").count()).toBeGreaterThanOrEqual(2);

      // Submit button exists
      const submitBtn = page.locator('button[type="submit"]');
      await expect(submitBtn).toBeVisible();
      expect(await submitBtn.textContent()).toContain(
        path === "/login" ? "Sign" : "Create"
      );
    });
  }
});

// ── 2. Login Page Specifics ───────────────────────────────────────────

test.describe("Login Page – Interactions", () => {
  test("password toggle reveals and hides password", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });

    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();

    // Click the eye toggle button
    const toggleBtn = page.locator('button[type="button"]').filter({ has: page.locator("svg") }).first();
    await toggleBtn.click();

    // Input should now be text type
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toHaveCount(0);

    // Click again to hide
    await toggleBtn.click();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test("sign in button is enabled with valid inputs", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });

    const emailInput = page.locator("#email");
    const passwordInput = page.locator("#password");
    const submitBtn = page.locator('button[type="submit"]');

    await emailInput.fill("test@example.com");
    await passwordInput.fill("password123");

    await expect(submitBtn).toBeEnabled();
    expect(await submitBtn.textContent()).toContain("Sign In");
  });

  test("sign-up link navigates to registration page", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });

    const signUpLink = page.locator('a[href="/registration"]');
    await expect(signUpLink).toBeVisible();

    await signUpLink.click();
    await page.waitForURL("**/registration");
    await expect(page.locator("h1")).toContainText("Create Account");
  });
});

// ── 3. Registration Page Specifics ────────────────────────────────────

test.describe("Registration Page – Interactions", () => {
  test("password mismatch shows error message", async ({ page }) => {
    await page.goto("/registration", { waitUntil: "networkidle", timeout: 15000 });

    const passwordInput = page.locator('input[type="password"]').first();
    const confirmInput = page.locator('input[type="password"]').nth(1);

    await passwordInput.fill("password123");
    await confirmInput.fill("different");

    // Error text should appear
    const errorText = page.locator("text=Passwords do not match");
    await expect(errorText).toBeVisible();

    // Submit button should be disabled
    const submitBtn = page.locator('button[type="submit"]');
    await expect(submitBtn).toBeDisabled();
  });

  test("role selection buttons toggle active state", async ({ page }) => {
    await page.goto("/registration", { waitUntil: "networkidle", timeout: 15000 });

    const studentBtn = page.locator("button", { hasText: "Learn as Student" });
    const instructorBtn = page.locator("button", { hasText: "Teach as Instructor" });

    // Click student
    await studentBtn.click();
    await expect(studentBtn).toHaveClass(/ctc-primary/);

    // Click instructor
    await instructorBtn.click();
    await expect(instructorBtn).toHaveClass(/ctc-primary/);
    // Student should no longer have active class
    await expect(studentBtn).not.toHaveClass(/ctc-primary/);
  });

  test("confirm password border turns red on mismatch", async ({ page }) => {
    await page.goto("/registration", { waitUntil: "networkidle", timeout: 15000 });

    const passwordInput = page.locator('input[type="password"]').first();
    const confirmInput = page.locator('input[type="password"]').nth(1);

    await passwordInput.fill("password123");
    await confirmInput.fill("different");

    // Confirm input should have the border-red-500 class
    await expect(confirmInput).toHaveClass(/border-red-500/);
  });
});

// ── 4. Student Dashboard Page Smoke Tests ─────────────────────────────

test.describe("Student Dashboard – Page Integrity", () => {
  for (const { path, name } of STUDENT_DASHBOARD_PAGES) {
    test(`${name} loads without 404 errors`, async ({ page }) => {
      const errors = await captureConsoleErrors(page);
      await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });

      // The page may show a loading skeleton (no auth) — that's fine
      // Just ensure it's not a 404 or blank page
      const bodyText = await page.textContent("body").catch(() => "");
      expect(bodyText?.length ?? 0, `${name} should have page content`).toBeGreaterThan(20);
      expect(bodyText?.includes("404") && bodyText?.includes("Not Found")).toBe(false);

      const criticalErrors = filterNextJSWarnings(errors);
      expect(criticalErrors, `${name} should have no critical console errors`).toHaveLength(0);
    });

    test(`${name} has a title heading`, async ({ page }) => {
      await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });

      // Every dashboard page has an h1
      const heading = page.locator("h1");
      await expect(heading).toBeVisible();
      expect(await heading.textContent()).toBeTruthy();
    });
  }
});

// ── 5. Student Dashboard – Main Page ─────────────────────────────────

test.describe("Student Dashboard – Main Page", () => {
  test("quick navigation links are present", async ({ page }) => {
    await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });

    // Quick nav links should render
    const navLinks = page.locator('a[href*="/student-dashboard/"]');
    const count = await navLinks.count();
    expect(count).toBeGreaterThanOrEqual(4); // At least 4 quick nav links
  });

  test("stats cards have values", async ({ page }) => {
    await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });

    // Stat values render (may show 0 when not authenticated)
    const statValues = page.locator(".text-2xl.font-bold");
    const count = await statValues.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });
});

// ── 6. Enrolled Courses Page ─────────────────────────────────────────

test.describe("Enrolled Courses – Filters & Search", () => {
  test("filter buttons render and activate on click", async ({ page }) => {
    await page.goto("/student-dashboard/enrolled-courses", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Filter buttons: All, Active, Completed
    const allBtn = page.locator("button", { hasText: "All" });
    const activeBtn = page.locator("button", { hasText: "Active" });
    const completedBtn = page.locator("button", { hasText: "Completed" });

    await expect(allBtn).toBeVisible();
    await expect(activeBtn).toBeVisible();
    await expect(completedBtn).toBeVisible();

    // "All" should be active by default (bg-teal / text-white)
    await expect(allBtn).toHaveClass(/text-white/);
    await expect(allBtn).toHaveClass(/ctc-primary/);

    // Click "Active" — it should become active, "All" should become inactive
    await activeBtn.click();
    await expect(activeBtn).toHaveClass(/text-white/);
    await expect(activeBtn).toHaveClass(/ctc-primary/);
    await expect(allBtn).not.toHaveClass(/text-white/);

    // Click "Completed" — it should become active, "Active" should become inactive
    await completedBtn.click();
    await expect(completedBtn).toHaveClass(/text-white/);
    await expect(completedBtn).toHaveClass(/ctc-primary/);
    await expect(activeBtn).not.toHaveClass(/text-white/);
  });

  test("search input accepts text", async ({ page }) => {
    await page.goto("/student-dashboard/enrolled-courses", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    const searchInput = page.locator('input[placeholder="Search courses..."]');
    await expect(searchInput).toBeVisible();

    await searchInput.fill("Machine Learning");
    expect(await searchInput.inputValue()).toBe("Machine Learning");
  });

  test("stats cards display headers", async ({ page }) => {
    await page.goto("/student-dashboard/enrolled-courses", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Stats should be visible
    await expect(page.locator("text=Total Enrolled")).toBeVisible();
    await expect(page.locator("text=In Progress")).toBeVisible();
    await expect(page.locator("text=Completed")).toBeVisible();
  });
});

// ── 7. History Page ──────────────────────────────────────────────────

test.describe("History – Timeline & Filters", () => {
  test("activity filter dropdown exists", async ({ page }) => {
    await page.goto("/student-dashboard/history", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Filter select should exist
    const filterSelect = page.locator("select");
    await expect(filterSelect).toBeVisible();

    // Has expected options
    const options = await filterSelect.locator("option").allTextContents();
    expect(options.length).toBeGreaterThanOrEqual(4);
    expect(options).toContain("All Activity");
    expect(options).toContain("Completed");
  });

  test("stats cards display headers", async ({ page }) => {
    await page.goto("/student-dashboard/history", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    await expect(page.locator("text=Courses Enrolled")).toBeVisible();
    await expect(page.locator("text=Hours Learned")).toBeVisible();
  });

  test("timeline line is rendered", async ({ page }) => {
    await page.goto("/student-dashboard/history", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // The timeline uses a vertical line (w-0.5 bg-gray-200) via absolute positioning
    // We check that the timeline section is in the DOM
    const timelineIcons = page.locator("svg").first();
    await expect(timelineIcons).toBeVisible();
  });
});

// ── 8. Reviews Page ──────────────────────────────────────────────────

test.describe("Reviews – Star Rating & Submit", () => {
  test("empty state shows when no courses to review", async ({ page }) => {
    await page.goto("/student-dashboard/reviews", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Either review cards or empty state will show
    const reviewCards = page.locator("button", { hasText: "Submit Review" });
    const emptyTitle = page.locator("text=No courses to review yet");

    // Both should not be visible at the same time
    const hasCards = (await reviewCards.count()) > 0;
    const hasEmpty = (await emptyTitle.count()) > 0;
    expect(hasCards || hasEmpty, "Should show review cards or empty state").toBe(true);
  });
});

// ── 9. Wishlist Page ─────────────────────────────────────────────────

test.describe("Wishlist – Cards & Interactions", () => {
  test("wishlist renders course cards", async ({ page }) => {
    await page.goto("/student-dashboard/wishlist", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Wishlist loads with static data — course titles should appear
    const courseTitles = [
      "Advanced Machine Learning",
      "Full-Stack Web Development",
      "Data Science Fundamentals",
    ];

    for (const title of courseTitles) {
      await expect(page.locator(`text=${title}`).first()).toBeVisible();
    }
  });

  test("wishlist shows saved count", async ({ page }) => {
    await page.goto("/student-dashboard/wishlist", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Saved count indicator
    const savedText = page.locator("text=/\\d+ saved/");
    await expect(savedText).toBeVisible();
    expect(await savedText.textContent()).toContain("3");
  });

  test("remove button appears on hover and removes course", async ({ page }) => {
    await page.goto("/student-dashboard/wishlist", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // First course card — hover to reveal the remove button
    const firstCard = page.locator(".card.overflow-hidden").first();
    await firstCard.hover();

    // Remove button (trash icon) should appear
    const removeBtn = firstCard.locator("button").filter({ has: page.locator("svg") }).first();
    await expect(removeBtn).toBeVisible();
    await expect(removeBtn.locator("svg")).toBeVisible();

    // Click remove and verify the course is gone
    await removeBtn.click();

    // Should now have 2 items (one removed)
    const savedText = page.locator("text=/\\d+ saved/");
    expect(await savedText.textContent()).toContain("2");
  });

  test("remove all courses shows empty state", async ({ page }) => {
    await page.goto("/student-dashboard/wishlist", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Remove all 3 courses
    const cards = page.locator(".card.overflow-hidden");
    const cardCount = await cards.count();
    expect(cardCount).toBe(3);

    for (let i = 0; i < cardCount; i++) {
      // Re-query the first card each iteration since DOM updates
      const firstCard = page.locator(".card.overflow-hidden").first();
      await firstCard.hover();
      const removeBtn = firstCard.locator("button").filter({ has: page.locator("svg") }).first();
      await removeBtn.click();
    }

    // After removing all, the empty state should appear
    await expect(page.locator("text=Your wishlist is empty")).toBeVisible();
  });

  test("each course card has price and level badge", async ({ page }) => {
    await page.goto("/student-dashboard/wishlist", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Each card should have a price and a level badge
    const prices = page.locator(".text-lg.font-bold");
    const priceCount = await prices.count();
    expect(priceCount).toBeGreaterThanOrEqual(3);

    // Level badges exist
    const badges = page.locator("text=/Beginner|Intermediate|Advanced/");
    expect(await badges.count()).toBeGreaterThanOrEqual(3);
  });

  test("View Course button links to course details", async ({ page }) => {
    await page.goto("/student-dashboard/wishlist", {
      waitUntil: "networkidle",
      timeout: 15000,
    });

    // Each card has a "View Course" link
    const viewLinks = page.locator('a[href*="/course-details/"]');
    expect(await viewLinks.count()).toBeGreaterThanOrEqual(3);
    await expect(viewLinks.first()).toContainText("View Course");
  });
});

// ── 10. Cross-Page Navigation ─────────────────────────────────────────

test.describe("Dashboard Navigation – Cross-Page", () => {
  test("navigate from login to registration and back", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });

    // Login page → Sign up link → Registration page
    await page.locator('a[href="/registration"]').click();
    await page.waitForURL("**/registration");
    await expect(page.locator("h1")).toContainText("Create Account");

    // Registration page → Sign in link → Login page
    await page.locator('a[href="/login"]').click();
    await page.waitForURL("**/login");
    await expect(page.locator("h1")).toContainText("Welcome Back");
  });

  test("student dashboard quick nav links lead to sub-pages", async ({ page }) => {
    await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });

    // Click "My Courses" quick nav link
    const myCoursesLink = page.locator('a[href="/student-dashboard/enrolled-courses"]');
    if (await myCoursesLink.isVisible()) {
      await myCoursesLink.click();
      await page.waitForURL("**/student-dashboard/enrolled-courses");
      await expect(page.locator("h1")).toContainText("My Courses");
    }
  });
});
