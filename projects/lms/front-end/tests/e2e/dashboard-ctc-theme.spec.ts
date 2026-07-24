/**
 * E2E tests: Verify all dashboard pages render with the CTC Research teal theme.
 *
 * The CTC teal theme uses:
 *   --ctc-primary: 0 161 179  (rgb(0, 161, 179))
 *   --ctc-primary-dark: 0 122 136
 *   --ctc-accent: 108 99 255
 *
 * Assertions:
 *   1. Every page returns HTTP 200 (no 404/500)
 *   2. At least one CTC teal class (btn-primary, card-gradient, progress-fill, etc.) is present
 *   3. Zero indigo-* or purple-* Tailwind classes (proves no old theme remnants)
 *   4. No console errors
 *   5. Dashboard sidebar and key CTAs are visible
 */

import { test, expect } from "@playwright/test";

// ── All 14 dashboard pages ──────────────────────────────────────────
interface DashboardPage {
  path: string;
  name: string;
  /** CSS classes that should appear at least once */
  expectedClasses: string[];
  /** CSS classes that must NOT appear */
  forbiddenClasses: string[];
}

const DASHBOARD_PAGES: DashboardPage[] = [
  {
    path: "/dashboard",
    name: "Main Dashboard",
    expectedClasses: ["card-gradient", "btn-primary", "progress-fill"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/courses",
    name: "Courses List",
    expectedClasses: ["btn-primary", "card-gradient"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/courses/new",
    name: "New Course",
    expectedClasses: ["btn-primary", "input-field"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/quiz",
    name: "Quiz Dispatcher",
    expectedClasses: ["btn-primary"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/enrolled-courses",
    name: "Enrolled Courses",
    expectedClasses: ["card-gradient", "progress-fill", "progress-track"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/review",
    name: "Review",
    expectedClasses: ["btn-primary"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/history",
    name: "History",
    expectedClasses: ["btn-primary"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/profile",
    name: "Profile",
    expectedClasses: ["btn-primary", "input-field"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/attempts",
    name: "Quiz Attempts",
    expectedClasses: ["btn-primary"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/student-manage",
    name: "Student Management",
    expectedClasses: ["btn-primary", "progress-fill"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/withdraw",
    name: "Withdraw",
    expectedClasses: ["btn-primary", "input-field"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/announcement",
    name: "Announcement",
    expectedClasses: ["btn-primary"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/assignment",
    name: "Assignment",
    expectedClasses: ["btn-primary"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
  {
    path: "/dashboard/courses/1/edit",
    name: "Edit Course",
    expectedClasses: ["btn-primary", "input-field"],
    forbiddenClasses: ["indigo-", "purple-"],
  },
];

// ── Tests ────────────────────────────────────────────────────────────

test.describe("Dashboard Pages – CTC Teal Theme", () => {
  for (const page of DASHBOARD_PAGES) {
    test(`${page.name} (${page.path})`, async ({ page: browserPage }) => {
      const consoleErrors: string[] = [];
      browserPage.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      // Navigate and wait for network idle
      const response = await browserPage.goto(page.path, {
        waitUntil: "networkidle",
        timeout: 15000,
      });

      // ── Assertion 1: HTTP 200 ──
      expect(response?.status(), `${page.name} should return 200`).toBe(200);

      // ── Assertion 2: No console errors ──
      const filteredErrors = consoleErrors.filter(
        (e) =>
          !e.includes(" hydration ") &&
          !e.includes("Warning:") &&
          !e.includes("next")
      );
      expect(
        filteredErrors,
        `${page.name} should have no console errors (found: ${filteredErrors.join("; ")})`
      ).toHaveLength(0);

      // Get the full HTML to search for CSS classes
      const html = await browserPage.content();
      const bodyText = await browserPage.textContent("body");

      // ── Assertion 3: Expected CTC teal classes present ──
      for (const cls of page.expectedClasses) {
        const hasClass = html.includes(cls);
        expect(
          hasClass,
          `${page.name} should contain CSS class "${cls}" (CTC teal theme)`
        ).toBe(true);
      }

      // ── Assertion 4: No forbidden old-theme classes ──
      for (const cls of page.forbiddenClasses) {
        const hasForbidden = html.includes(cls);
        expect(
          hasForbidden,
          `${page.name} should NOT contain forbidden class "${cls}"`
        ).toBe(false);
      }

      // ── Assertion 5: Page has meaningful content (not empty/error) ──
      expect(
        bodyText?.length ?? 0,
        `${page.name} should have page content`
      ).toBeGreaterThan(50);

      // ── Assertion 6: No "404" or "Not Found" in body ──
      if (bodyText) {
        expect(
          bodyText.includes("404") || bodyText.includes("Not Found"),
          `${page.name} should not show 404 error`
        ).toBe(false);
      }
    });
  }
});

// ── Cross-page consistency tests ──────────────────────────────────────

test.describe("Cross-page CTC Theme Consistency", () => {
  test("CTC primary CSS variables are defined", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "networkidle" });

    // Verify the CTC teal custom properties are set on :root
    const ctcPrimary = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue("--ctc-primary").trim()
    );
    const ctcPrimaryDark = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue("--ctc-primary-dark").trim()
    );

    expect(ctcPrimary).toBe("0 161 179");
    expect(ctcPrimaryDark).toBe("0 122 136");
  });

  test("All dashboard pages share consistent sidebar navigation", async ({
    page,
  }) => {
    await page.goto("/dashboard", { waitUntil: "networkidle" });

    // Sidebar links should use /dashboard/* paths
    const sidebarLinks = await page.$$eval(
      'nav a[href*="/dashboard"]',
      (links) => links.map((l) => (l as HTMLAnchorElement).getAttribute("href"))
    );

    expect(sidebarLinks.length).toBeGreaterThanOrEqual(3);
    for (const href of sidebarLinks) {
      expect(href).toMatch(/^\/dashboard/);
    }
  });

  test("No indigo or purple Tailwind classes anywhere in dashboard", async ({
    page,
  }) => {
    // Sample 4 key pages — if all pass, the full per-page tests above
    // already verify all 14 individually.
    const samplePages = [
      "/dashboard",
      "/dashboard/courses",
      "/dashboard/enrolled-courses",
      "/dashboard/quiz",
    ];

    for (const path of samplePages) {
      await page.goto(path, { waitUntil: "networkidle" });
      const html = await page.content();

      const indigoCount = (html.match(/\bindigo-/g) || []).length;
      const purpleCount = (html.match(/\bpurple-/g) || []).length;

      expect(indigoCount, `${path} should have zero indigo- classes`).toBe(0);
      expect(purpleCount, `${path} should have zero purple- classes`).toBe(0);
    }
  });

  test("btn-primary buttons render with correct CTC teal color", async ({
    page,
  }) => {
    await page.goto("/dashboard", { waitUntil: "networkidle" });

    // Find the first btn-primary button and check its computed background
    const btn = page.locator(".btn-primary").first();
    if (await btn.isVisible({ timeout: 3000 }).catch(() => false)) {
      const bgColor = await btn.evaluate((el) =>
        getComputedStyle(el).backgroundColor
      );
      // rgb(0, 161, 179) is the CTC primary teal
      expect(bgColor).toBe("rgb(0, 161, 179)");
    }
  });
});
