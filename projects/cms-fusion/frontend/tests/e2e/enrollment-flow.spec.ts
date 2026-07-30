/**
 * E2E tests: Course Enrollment Flow
 *
 * Tests the complete enrollment lifecycle using Playwright + API mocking:
 *   1. Student views a course detail page with enroll button
 *   2. Clicks enroll — sees "Enrolling..." spinner
 *   3. Sees success state (free course) or redirects to checkout (paid course)
 *   4. Handles errors gracefully (API failures, already enrolled)
 *
 * Pages tested:
 *   - /course-details/{id} (student-facing course page)
 *
 * API endpoints mocked:
 *   - GET  /apis/auth/profile/         — authenticated student profile
 *   - GET  /apis/courses/{id}/         — course data (free or paid)
 *   - POST /apis/enrollments           — create enrollment
 *   - GET  /apis/students/{id}/enrollments — enrollment list (for checkout redirect)
 */

import { test, expect, type Page, type Route } from "@playwright/test";

// ═══════════════════════════════════════════════════════════════════
// Helpers — console error tracking & filtering
// ═══════════════════════════════════════════════════════════════════

function captureConsoleErrors(page: Page) {
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  return () =>
    errors.filter(
      (e) =>
        !e.includes(" hydration ") &&
        !e.includes("Warning:") &&
        !e.includes("next") &&
        !e.includes("favicon") &&
        !e.includes("404") &&
        !e.includes("fetch") &&
        !e.includes("NetworkError") &&
        !e.includes("ERR_CONNECTION_REFUSED")
    );
}

// ═══════════════════════════════════════════════════════════════════
// Mock Data
// ═══════════════════════════════════════════════════════════════════

const STUDENT_PROFILE = {
  id: 1,
  username: "student_john",
  first_name: "John",
  last_name: "Doe",
  email: "john@example.com",
  role: "student",
};

interface Course {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  price: number;
  discounted_price: number | null;
  thumbnail: string;
  category: number;
  category_name: string;
  instructor: number;
  instructor_name: string;
  duration: string;
  level: string;
  language: string;
  curriculum: Array<{
    id: number;
    title: string;
    description: string;
    video_url: string;
    duration: string;
    order: number;
    is_free: boolean;
  }>;
  students_count: number;
  rating: number;
  reviews_count: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

interface Enrollment {
  id: number;
  student: number;
  course: number;
  course_title: string;
  course_thumbnail: string | null;
  price: number;
  progress: number;
  status: string;
  payment_status: string;
  payment_transaction_id: number | null;
  enrolled_at: string;
  completed_at: string | null;
  is_completed: boolean;
  instructor_name: string;
  duration: string;
}

function makeFreeCourse(overrides: Partial<Course> = {}): Course {
  return {
    id: 101,
    title: "Introduction to Python",
    slug: "intro-to-python",
    description: "Learn Python programming from scratch. Perfect for beginners who want to start their coding journey.",
    short_description: "A beginner-friendly Python course",
    price: 0,
    discounted_price: null,
    thumbnail: "/thumbnails/python.jpg",
    category: 1,
    category_name: "Programming",
    instructor: 1,
    instructor_name: "Dr. Smith",
    duration: "4 hours",
    level: "beginner",
    language: "English",
    curriculum: [
      { id: 1, title: "Welcome & Setup", description: "Getting started", video_url: "", duration: "10 min", order: 1, is_free: true },
      { id: 2, title: "Variables & Types", description: "Core concepts", video_url: "", duration: "20 min", order: 2, is_free: false },
    ],
    students_count: 1280,
    rating: 4.7,
    reviews_count: 342,
    is_published: true,
    created_at: "2026-01-15T00:00:00Z",
    updated_at: "2026-06-01T00:00:00Z",
    ...overrides,
  };
}

function makePaidCourse(overrides: Partial<Course> = {}): Course {
  return {
    ...makeFreeCourse(),
    id: 102,
    title: "Advanced React Patterns",
    slug: "advanced-react",
    price: 49.99,
    discounted_price: 29.99,
    short_description: "Master advanced React patterns and best practices",
    level: "advanced",
    duration: "12 hours",
    students_count: 560,
    ...overrides,
  };
}

function makeEnrollment(courseId: number, overrides: Partial<Enrollment> = {}): Enrollment {
  return {
    id: 201,
    student: 1,
    course: courseId,
    course_title: courseId === 101 ? "Introduction to Python" : "Advanced React Patterns",
    course_thumbnail: null,
    price: courseId === 101 ? 0 : 49.99,
    progress: 0,
    status: "active",
    payment_status: courseId === 101 ? "completed" : "pending",
    payment_transaction_id: null,
    enrolled_at: "2026-07-24T10:00:00Z",
    completed_at: null,
    is_completed: false,
    instructor_name: "Dr. Smith",
    duration: courseId === 101 ? "4 hours" : "12 hours",
    ...overrides,
  };
}

// ═══════════════════════════════════════════════════════════════════
// Route Helpers — sets up API mocking for different test scenarios
// ═══════════════════════════════════════════════════════════════════

/**
 * Set up API mocks for an authenticated student viewing a course.
 */
async function mockStudentSession(
  page: Page,
  course: Course,
  enrollmentResponse?: Enrollment
) {
  // Profile
  await page.route("**/apis/auth/profile/", (route: Route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(STUDENT_PROFILE),
    })
  );

  // Course data (the main API call the page makes on load)
  await page.route(`**/apis/courses/${course.id}/`, (route: Route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(course),
    })
  );

  // Enrollments list (used by checkout page to find enrollment by ID)
  if (enrollmentResponse) {
    await page.route(`**/apis/students/${STUDENT_PROFILE.id}/enrollments`, (route: Route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([enrollmentResponse]),
      })
    );
  }
}

/**
 * Set up the enroll endpoint mock with a custom response handler.
 * Returns a function that can be called to verify the enroll request body.
 */
function mockEnrollEndpoint(
  page: Page,
  status: number,
  responseBody: Enrollment | { message: string }
) {
  return new Promise<{ course_id: number }>((resolve) => {
    page.route("**/apis/enrollments", async (route: Route) => {
      if (route.request().method() === "POST") {
        const body = JSON.parse(route.request().postData() || "{}");
        resolve({ course_id: body.course_id });
        return route.fulfill({
          status,
          contentType: "application/json",
          body: JSON.stringify(responseBody),
        });
      }
      // GET requests for enrollments
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });
  });
}

// ═══════════════════════════════════════════════════════════════════
// Test Suite
// ═══════════════════════════════════════════════════════════════════

test.describe("Enrollment Flow — E2E", () => {
  // ── 1. Page Load & Course Data ──────────────────────────────────

  test.describe("Page Load & Course Data", () => {
    test("displays course details for a free course", async ({ page }) => {
      const course = makeFreeCourse();
      await mockStudentSession(page, course);
      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      // Title and key metadata should be visible
      await expect(page.locator("h1")).toContainText(course.title);
      await expect(page.locator(`text=${course.instructor_name}`)).toBeVisible();
      await expect(page.locator(`text=${course.duration}`)).toBeVisible();
      await expect(page.locator(`text=${course.category_name}`)).toBeVisible();

      // Free course shows "Enroll for Free" button
      await expect(page.locator("button", { hasText: "Enroll for Free" })).toBeVisible();
    });

    test("displays course details with price for a paid course", async ({ page }) => {
      const course = makePaidCourse();
      await mockStudentSession(page, course);
      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("h1")).toContainText(course.title);

      // Paid course shows "Enroll Now — $X" button with the discounted price
      await expect(
        page.locator("button", { hasText: /Enroll Now.*\$/ })
      ).toBeVisible();

      // Discount badge should be visible
      await expect(page.locator("text=/Discounted from/i")).toBeVisible();
    });
  });

  // ── 2. Free Course Enrollment — UI State Transitions ────────────

  test.describe("Free Course Enrollment", () => {
    test("transitions through Enrolling... → enrolled state without redirecting to external payment", async ({ page }) => {
      const course = makeFreeCourse();
      const enrollment = makeEnrollment(course.id, { payment_status: "completed" });

      await mockStudentSession(page, course);

      // Intercept the enroll POST — capture the request body
      let requestBody: any = null;
      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          requestBody = JSON.parse(route.request().postData() || "{}");
          // Delay slightly so we can observe the "Enrolling..." state
          await new Promise((r) => setTimeout(r, 300));
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(enrollment),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      // ── State 1: Initial — "Enroll for Free" button ──────────────
      const enrollBtn = page.locator("button", { hasText: "Enroll for Free" });
      await expect(enrollBtn).toBeVisible();

      // ── Click enroll ─────────────────────────────────────────────
      await enrollBtn.click();

      // ── State 2: "Enrolling..." with spinner ─────────────────────
      await expect(page.locator("text=Enrolling...")).toBeVisible({ timeout: 5000 });

      // The button should be disabled during enrollment
      const enrollingBtn = page.locator("button:has-text('Enrolling...')");
      await expect(enrollingBtn).toBeDisabled();

      // Verify the spinner element is rendered
      const spinner = page.locator(".animate-spin");
      await expect(spinner).toBeVisible();

      // Verify the API request body contains the correct course_id
      expect(requestBody, "Enroll POST should have been called").not.toBeNull();
      expect(requestBody.course_id, "Enroll request should contain course_id").toBe(course.id);

      // ── State 3: Successfully enrolled ───────────────────────────
      // Free course shows success message before auto-redirect
      await expect(
        page.locator("text=Successfully enrolled! Redirecting...")
      ).toBeVisible({ timeout: 10000 });

      // Green check icon should be visible
      await expect(page.locator("svg")).toBeVisible();

      // The URL should NOT contain a payment provider domain (Stripe, PayPal, etc.)
      const currentUrl = page.url();
      expect(currentUrl).not.toContain("stripe.com");
      expect(currentUrl).not.toContain("paypal.com");
      expect(currentUrl).not.toContain("paymo");
    });

    test("does not redirect to external payment URL after enrolling in a free course", async ({ page }) => {
      const course = makeFreeCourse();
      const enrollment = makeEnrollment(course.id, { payment_status: "completed" });

      await mockStudentSession(page, course);

      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(enrollment),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });
      await page.locator("button", { hasText: "Enroll for Free" }).click();

      // Wait for the success state
      await expect(
        page.locator("text=Successfully enrolled! Redirecting...")
      ).toBeVisible({ timeout: 10000 });

      // Brief pause then check the current URL is not an external payment provider
      await page.waitForTimeout(500);

      const finalUrl = page.url();
      expect(finalUrl, "Should not redirect to Stripe").not.toContain("stripe.com");
      expect(finalUrl, "Should not redirect to PayPal").not.toContain("paypal.com");
      expect(finalUrl, "Should not redirect to Paymo").not.toContain("paymo");
    });
  });

  // ── 3. Paid Course Enrollment — UI State Transitions ────────────

  test.describe("Paid Course Enrollment", () => {
    test("transitions through Enrolling... → redirects to checkout page without redirecting to external payment", async ({ page }) => {
      const course = makePaidCourse();
      const enrollment = makeEnrollment(course.id, { payment_status: "pending" });

      await mockStudentSession(page, course, enrollment);

      // Mock enroll endpoint
      let enrollCalled = false;
      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          enrollCalled = true;
          await new Promise((r) => setTimeout(r, 300));
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(enrollment),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      // Mock the checkout page enrollment fetch
      await page.route(`**/apis/students/${STUDENT_PROFILE.id}/enrollments`, (route: Route) =>
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([enrollment]),
        })
      );

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      // ── State 1: Initial — "Enroll Now — $X" button ─────────────
      const enrollBtn = page.locator("button", { hasText: /Enroll Now/ });
      await expect(enrollBtn).toBeVisible();
      await expect(enrollBtn).toContainText("$");

      // ── Click enroll ─────────────────────────────────────────────
      await enrollBtn.click();

      // ── State 2: "Enrolling..." with spinner ─────────────────────
      await expect(page.locator("text=Enrolling...")).toBeVisible({ timeout: 5000 });
      expect(enrollCalled).toBe(true);

      // ── State 3: Redirected to checkout page ─────────────────────
      // For paid courses, the page redirects to /enroll/checkout/{enrollmentId}
      await page.waitForURL(/\/enroll\/checkout\//, { timeout: 10000 });

      // Verify we're on the checkout page, NOT an external payment URL
      const checkoutUrl = page.url();
      expect(checkoutUrl).toContain("/enroll/checkout/");
      expect(checkoutUrl).not.toContain("stripe.com");
      expect(checkoutUrl).not.toContain("paypal.com");
      expect(checkoutUrl).not.toContain("paymo");
    });

    test("checkout page displays order summary without sending user to real Stripe", async ({ page }) => {
      const course = makePaidCourse();
      const enrollment = makeEnrollment(course.id, { payment_status: "pending", price: 29.99 });

      await mockStudentSession(page, course, enrollment);

      // Mock enroll endpoint — redirects to checkout
      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(enrollment),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });
      await page.locator("button", { hasText: /Enroll Now/ }).click();

      // Wait for redirect to checkout page
      await page.waitForURL(/\/enroll\/checkout\//, { timeout: 10000 });

      // Verify checkout page shows order summary
      await expect(page.locator("text=Order Summary")).toBeVisible();

      // Course title should appear in the summary
      await expect(page.locator(`text=${course.title}`)).toBeVisible();

      // Price should be displayed
      await expect(page.locator("text=$29.99")).toBeVisible();

      // Payment method selection should be visible (not auto-redirecting to Stripe)
      await expect(page.locator("text=Select Payment Method")).toBeVisible();

      // Credit Card option (Stripe) should be available
      await expect(page.locator("text=Credit Card")).toBeVisible();

      // Verify no Stripe redirect happened
      expect(page.url()).not.toContain("stripe.com");
    });
  });

  // ── 4. Enrollment Error States ──────────────────────────────────

  test.describe("Enrollment Error States", () => {
    test("shows error message when enrollment API fails", async ({ page }) => {
      const course = makeFreeCourse();

      await mockStudentSession(page, course);

      // Mock enroll endpoint to return server error
      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ message: "Unable to process enrollment at this time." }),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      await page.locator("button", { hasText: "Enroll for Free" }).click();

      // Wait for "Enrolling..." to appear
      await expect(page.locator("text=Enrolling...")).toBeVisible({ timeout: 5000 });

      // Error message should appear
      await expect(
        page.locator("text=Unable to process enrollment at this time.")
      ).toBeVisible({ timeout: 10000 });
    });

    test("shows already enrolled message when user re-attempts enrollment", async ({ page }) => {
      const course = makeFreeCourse();

      await mockStudentSession(page, course);

      // Mock enroll endpoint to return "Already enrolled" error
      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 409,
            contentType: "application/json",
            body: JSON.stringify({ message: "Already enrolled in this course." }),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      await page.locator("button", { hasText: "Enroll for Free" }).click();

      // Should show "already enrolled" message (the hook checks for "Already enrolled" string)
      await expect(
        page.locator("text=already enrolled in this course")
      ).toBeVisible({ timeout: 10000 });
    });

    test("recovers from error state — button is clickable again after failing", async ({ page }) => {
      const course = makeFreeCourse();

      await mockStudentSession(page, course);

      let callCount = 0;
      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          callCount++;
          if (callCount === 1) {
            // First call fails
            return route.fulfill({
              status: 500,
              contentType: "application/json",
              body: JSON.stringify({ message: "Server error. Please try again." }),
            });
          }
          // Second call succeeds
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(makeEnrollment(course.id, { payment_status: "completed" })),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      const enrollBtn = page.locator("button", { hasText: "Enroll for Free" });

      // First click — should fail
      await enrollBtn.click();
      await expect(page.locator("text=Server error. Please try again.")).toBeVisible({ timeout: 10000 });

      // After the error, the button should re-appear (since 'showButton' becomes true when step is 'error')
      // Actually, the hook only shows the button when !isEnrolling && !isEnrolled.
      // At the error state, isEnrolling=false, isEnrolled=false, so showButton=true.
      // But the enroll button also relies on `error` being null to decide what to show.
      // Actually, look at the code: `showButton` = `!isEnrolling && !isEnrolled`, and `isEnrolled = step === 'enrolled_free' || step === 'enrolled_paid'`.
      // When step is 'error', both are false, so showButton is true.
      // The button is in a `{showButton && (...)}` block with `onClick={enroll}`.
      // The `error` is shown separately via `{error && (...)}`.
      // So after error, the button re-appears.
      // Brief pause to let React finish state batching before clicking again
      await page.waitForTimeout(300);
      await expect(page.locator("button", { hasText: "Enroll for Free" })).toBeVisible({ timeout: 5000 });

      // Second click — should succeed
      await page.locator("button", { hasText: "Enroll for Free" }).click();
      await expect(
        page.locator("text=Successfully enrolled! Redirecting...")
      ).toBeVisible({ timeout: 10000 });

      // The API should have been called twice
      expect(callCount).toBe(2);
    });
  });

  // ── 5. No Console Errors ────────────────────────────────────────

  test.describe("Console Error Checks", () => {
    test("course detail page loads without critical console errors", async ({ page }) => {
      const getErrors = captureConsoleErrors(page);
      const course = makeFreeCourse();

      await mockStudentSession(page, course);
      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });

      await expect(page.locator("h1")).toContainText(course.title);

      const critical = getErrors();
      expect(critical, "Should have no critical console errors").toHaveLength(0);
    });

    test("enrollment flow completes without critical console errors", async ({ page }) => {
      const getErrors = captureConsoleErrors(page);
      const course = makeFreeCourse();
      const enrollment = makeEnrollment(course.id, { payment_status: "completed" });

      await mockStudentSession(page, course);

      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 201,
            contentType: "application/json",
            body: JSON.stringify(enrollment),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });
      await page.locator("button", { hasText: "Enroll for Free" }).click();

      await expect(
        page.locator("text=Successfully enrolled! Redirecting...")
      ).toBeVisible({ timeout: 10000 });

      const critical = getErrors();
      expect(critical, "Enrollment flow should have no critical console errors").toHaveLength(0);
    });

    test("enrollment error does not cause console errors", async ({ page }) => {
      const getErrors = captureConsoleErrors(page);
      const course = makeFreeCourse();

      await mockStudentSession(page, course);

      await page.route("**/apis/enrollments", async (route: Route) => {
        if (route.request().method() === "POST") {
          return route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ message: "Enrollment failed." }),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      });

      await page.goto(`/course-details/${course.id}`, { waitUntil: "networkidle", timeout: 15000 });
      await page.locator("button", { hasText: "Enroll for Free" }).click();

      await expect(page.locator("text=Enrollment failed.")).toBeVisible({ timeout: 10000 });

      const critical = getErrors();
      expect(critical, "Enrollment error should not cause console errors").toHaveLength(0);
    });
  });
});
