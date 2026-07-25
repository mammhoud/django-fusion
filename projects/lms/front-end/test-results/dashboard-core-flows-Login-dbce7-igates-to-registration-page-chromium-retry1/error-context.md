# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> Login Page – Interactions >> sign-up link navigates to registration page
- Location: tests/e2e/dashboard-core-flows.spec.ts:131:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('a[href="/registration"]')
Expected: visible
Error: strict mode violation: locator('a[href="/registration"]') resolved to 3 elements:
    1) <a href="/registration" class="btn-white px-4 py-2 rounded-lg font-medium text-sm">Sign Up</a> aka getByRole('link', { name: 'Sign Up', exact: true })
    2) <a href="/registration" class="text-[rgb(var(--ctc-primary))] hover:text-[rgb(var(--ctc-primary-dark))] font-medium">Sign up</a> aka getByRole('link', { name: 'Sign up', exact: true })
    3) <a href="/registration" class="text-sm text-gray-400 hover:text-white transition-colors duration-200">Join a Trial</a> aka getByRole('link', { name: 'Join a Trial' })

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('a[href="/registration"]')

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e2]:
    - banner [ref=e3]:
      - generic [ref=e5]:
        - link "CTC Research" [ref=e6] [cursor=pointer]:
          - /url: /
          - img [ref=e7]
          - generic [ref=e9]: CTC Research
        - navigation [ref=e10]:
          - link "Home" [ref=e11] [cursor=pointer]:
            - /url: /
          - link "About" [ref=e12] [cursor=pointer]:
            - /url: /about-us
          - link "Services" [ref=e13] [cursor=pointer]:
            - /url: /services
          - link "Team" [ref=e14] [cursor=pointer]:
            - /url: /team
          - link "Courses" [ref=e15] [cursor=pointer]:
            - /url: /courses
          - link "Blog" [ref=e16] [cursor=pointer]:
            - /url: /blog
          - link "Contact" [ref=e17] [cursor=pointer]:
            - /url: /contact
        - generic [ref=e19]:
          - link "Log In" [ref=e20] [cursor=pointer]:
            - /url: /login
          - link "Sign Up" [ref=e21] [cursor=pointer]:
            - /url: /registration
    - main [ref=e22]:
      - generic [ref=e24]:
        - generic [ref=e25]:
          - img [ref=e26]
          - heading "Welcome Back" [level=1] [ref=e28]
          - paragraph [ref=e29]: Sign in to your account
        - generic [ref=e30]:
          - generic [ref=e31]:
            - generic [ref=e32]: Username
            - textbox "Username" [active] [ref=e33]:
              - /placeholder: Enter your username
          - generic [ref=e34]:
            - generic [ref=e35]: Password
            - generic [ref=e36]:
              - textbox "Password" [ref=e37]:
                - /placeholder: Enter your password
              - button [ref=e38] [cursor=pointer]:
                - img [ref=e39]
          - generic [ref=e42]:
            - generic [ref=e43]:
              - checkbox "Remember me" [ref=e44]
              - text: Remember me
            - link "Forgot password?" [ref=e45] [cursor=pointer]:
              - /url: "#"
          - button "Sign In" [ref=e46] [cursor=pointer]
          - paragraph [ref=e47]:
            - text: Don't have an account?
            - link "Sign up" [ref=e48] [cursor=pointer]:
              - /url: /registration
    - contentinfo [ref=e49]:
      - generic [ref=e50]:
        - generic [ref=e51]:
          - generic [ref=e52]:
            - link "CTC Research" [ref=e53] [cursor=pointer]:
              - /url: /
              - img [ref=e54]
              - generic [ref=e56]: CTC Research
            - paragraph [ref=e57]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e58]:
            - heading "Research" [level=3] [ref=e59]
            - list [ref=e60]:
              - listitem [ref=e61]:
                - link "Our Services" [ref=e62] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e63]:
                - link "Our Team" [ref=e64] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e65]:
                - link "Training Courses" [ref=e66] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e67]:
                - link "Research Blog" [ref=e68] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e69]:
            - heading "Support" [level=3] [ref=e70]
            - list [ref=e71]:
              - listitem [ref=e72]:
                - link "Contact Us" [ref=e73] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e74]:
                - link "About CTC" [ref=e75] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e76]:
                - link "FAQ" [ref=e77] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e78]:
                - link "Privacy Policy" [ref=e79] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e80]:
            - heading "Get Involved" [level=3] [ref=e81]
            - list [ref=e82]:
              - listitem [ref=e83]:
                - link "Join a Trial" [ref=e84] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e85]:
                - link "Partner With Us" [ref=e86] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e88]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e91] [cursor=pointer]:
    - img [ref=e92]
    - generic [ref=e94]: EN
  - alert [ref=e95]
```

# Test source

```ts
  35  |       !e.includes("404")
  36  |   );
  37  | }
  38  | 
  39  | // ── Helpers: quick assertions ─────────────────────────────────────────
  40  | async function assertPageLoaded(
  41  |   page: import("@playwright/test").Page,
  42  |   name: string,
  43  |   expectedStatus = 200
  44  | ) {
  45  |   const response = await page.waitForLoadState("networkidle", { timeout: 15000 }).then(() => null, () => null);
  46  |   // Check no 404 in body
  47  |   const bodyText = await page.textContent("body").catch(() => "");
  48  |   expect(
  49  |     bodyText?.includes("404") && bodyText?.includes("Not Found"),
  50  |     `${name} should not show a 404 error`
  51  |   ).toBe(false);
  52  | }
  53  | 
  54  | // ── Test Data ─────────────────────────────────────────────────────────
  55  | const AUTH_PAGES = [
  56  |   { path: "/login", name: "Login Page" },
  57  |   { path: "/registration", name: "Registration Page" },
  58  | ] as const;
  59  | 
  60  | const STUDENT_DASHBOARD_PAGES = [
  61  |   { path: "/student-dashboard", name: "Student Dashboard" },
  62  |   { path: "/student-dashboard/enrolled-courses", name: "Enrolled Courses" },
  63  |   { path: "/student-dashboard/history", name: "Activity History" },
  64  |   { path: "/student-dashboard/reviews", name: "My Reviews" },
  65  |   { path: "/student-dashboard/wishlist", name: "Wishlist" },
  66  | ] as const;
  67  | 
  68  | // ── 1. Auth Page Smoke Tests ──────────────────────────────────────────
  69  | 
  70  | test.describe("Auth Pages – Smoke Tests", () => {
  71  |   for (const { path, name } of AUTH_PAGES) {
  72  |     test(`${name} renders without console errors`, async ({ page }) => {
  73  |       const errors = await captureConsoleErrors(page);
  74  |       await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });
  75  |       expect(filterNextJSWarnings(errors), `${name} should have no console errors`).toHaveLength(0);
  76  |     });
  77  | 
  78  |     test(`${name} has key form elements`, async ({ page }) => {
  79  |       await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });
  80  | 
  81  |       // Logo / heading should be visible
  82  |       await expect(page.locator("h1")).toBeVisible();
  83  |       expect(await page.locator("input").count()).toBeGreaterThanOrEqual(2);
  84  | 
  85  |       // Submit button exists
  86  |       const submitBtn = page.locator('button[type="submit"]');
  87  |       await expect(submitBtn).toBeVisible();
  88  |       expect(await submitBtn.textContent()).toContain(
  89  |         path === "/login" ? "Sign" : "Create"
  90  |       );
  91  |     });
  92  |   }
  93  | });
  94  | 
  95  | // ── 2. Login Page Specifics ───────────────────────────────────────────
  96  | 
  97  | test.describe("Login Page – Interactions", () => {
  98  |   test("password toggle reveals and hides password", async ({ page }) => {
  99  |     await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });
  100 | 
  101 |     const passwordInput = page.locator('input[type="password"]');
  102 |     await expect(passwordInput).toBeVisible();
  103 | 
  104 |     // Click the eye toggle button
  105 |     const toggleBtn = page.locator('button[type="button"]').filter({ has: page.locator("svg") }).first();
  106 |     await toggleBtn.click();
  107 | 
  108 |     // Input should now be text type
  109 |     await expect(page.locator('input[type="text"]')).toBeVisible();
  110 |     await expect(page.locator('input[type="password"]')).toHaveCount(0);
  111 | 
  112 |     // Click again to hide
  113 |     await toggleBtn.click();
  114 |     await expect(page.locator('input[type="password"]')).toBeVisible();
  115 |   });
  116 | 
  117 |   test("sign in button is enabled with valid inputs", async ({ page }) => {
  118 |     await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });
  119 | 
  120 |     const emailInput = page.locator("#email");
  121 |     const passwordInput = page.locator("#password");
  122 |     const submitBtn = page.locator('button[type="submit"]');
  123 | 
  124 |     await emailInput.fill("test@example.com");
  125 |     await passwordInput.fill("password123");
  126 | 
  127 |     await expect(submitBtn).toBeEnabled();
  128 |     expect(await submitBtn.textContent()).toContain("Sign In");
  129 |   });
  130 | 
  131 |   test("sign-up link navigates to registration page", async ({ page }) => {
  132 |     await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });
  133 | 
  134 |     const signUpLink = page.locator('a[href="/registration"]');
> 135 |     await expect(signUpLink).toBeVisible();
      |                              ^ Error: expect(locator).toBeVisible() failed
  136 | 
  137 |     await signUpLink.click();
  138 |     await page.waitForURL("**/registration");
  139 |     await expect(page.locator("h1")).toContainText("Create Account");
  140 |   });
  141 | });
  142 | 
  143 | // ── 3. Registration Page Specifics ────────────────────────────────────
  144 | 
  145 | test.describe("Registration Page – Interactions", () => {
  146 |   test("password mismatch shows error message", async ({ page }) => {
  147 |     await page.goto("/registration", { waitUntil: "networkidle", timeout: 15000 });
  148 | 
  149 |     const passwordInput = page.locator('input[type="password"]').first();
  150 |     const confirmInput = page.locator('input[type="password"]').nth(1);
  151 | 
  152 |     await passwordInput.fill("password123");
  153 |     await confirmInput.fill("different");
  154 | 
  155 |     // Error text should appear
  156 |     const errorText = page.locator("text=Passwords do not match");
  157 |     await expect(errorText).toBeVisible();
  158 | 
  159 |     // Submit button should be disabled
  160 |     const submitBtn = page.locator('button[type="submit"]');
  161 |     await expect(submitBtn).toBeDisabled();
  162 |   });
  163 | 
  164 |   test("role selection buttons toggle active state", async ({ page }) => {
  165 |     await page.goto("/registration", { waitUntil: "networkidle", timeout: 15000 });
  166 | 
  167 |     const studentBtn = page.locator("button", { hasText: "Learn as Student" });
  168 |     const instructorBtn = page.locator("button", { hasText: "Teach as Instructor" });
  169 | 
  170 |     // Click student
  171 |     await studentBtn.click();
  172 |     await expect(studentBtn).toHaveClass(/ctc-primary/);
  173 | 
  174 |     // Click instructor
  175 |     await instructorBtn.click();
  176 |     await expect(instructorBtn).toHaveClass(/ctc-primary/);
  177 |     // Student should no longer have active class
  178 |     await expect(studentBtn).not.toHaveClass(/ctc-primary/);
  179 |   });
  180 | 
  181 |   test("confirm password border turns red on mismatch", async ({ page }) => {
  182 |     await page.goto("/registration", { waitUntil: "networkidle", timeout: 15000 });
  183 | 
  184 |     const passwordInput = page.locator('input[type="password"]').first();
  185 |     const confirmInput = page.locator('input[type="password"]').nth(1);
  186 | 
  187 |     await passwordInput.fill("password123");
  188 |     await confirmInput.fill("different");
  189 | 
  190 |     // Confirm input should have the border-red-500 class
  191 |     await expect(confirmInput).toHaveClass(/border-red-500/);
  192 |   });
  193 | });
  194 | 
  195 | // ── 4. Student Dashboard Page Smoke Tests ─────────────────────────────
  196 | 
  197 | test.describe("Student Dashboard – Page Integrity", () => {
  198 |   for (const { path, name } of STUDENT_DASHBOARD_PAGES) {
  199 |     test(`${name} loads without 404 errors`, async ({ page }) => {
  200 |       const errors = await captureConsoleErrors(page);
  201 |       await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });
  202 | 
  203 |       // The page may show a loading skeleton (no auth) — that's fine
  204 |       // Just ensure it's not a 404 or blank page
  205 |       const bodyText = await page.textContent("body").catch(() => "");
  206 |       expect(bodyText?.length ?? 0, `${name} should have page content`).toBeGreaterThan(20);
  207 |       expect(bodyText?.includes("404") && bodyText?.includes("Not Found")).toBe(false);
  208 | 
  209 |       const criticalErrors = filterNextJSWarnings(errors);
  210 |       expect(criticalErrors, `${name} should have no critical console errors`).toHaveLength(0);
  211 |     });
  212 | 
  213 |     test(`${name} has a title heading`, async ({ page }) => {
  214 |       await page.goto(path, { waitUntil: "networkidle", timeout: 15000 });
  215 | 
  216 |       // Every dashboard page has an h1
  217 |       const heading = page.locator("h1");
  218 |       await expect(heading).toBeVisible();
  219 |       expect(await heading.textContent()).toBeTruthy();
  220 |     });
  221 |   }
  222 | });
  223 | 
  224 | // ── 5. Student Dashboard – Main Page ─────────────────────────────────
  225 | 
  226 | test.describe("Student Dashboard – Main Page", () => {
  227 |   test("quick navigation links are present", async ({ page }) => {
  228 |     await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });
  229 | 
  230 |     // Quick nav links should render
  231 |     const navLinks = page.locator('a[href*="/student-dashboard/"]');
  232 |     const count = await navLinks.count();
  233 |     expect(count).toBeGreaterThanOrEqual(4); // At least 4 quick nav links
  234 |   });
  235 | 
```