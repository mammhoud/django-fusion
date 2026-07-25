# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> Enrolled Courses – Filters & Search >> filter buttons render and activate on click
- Location: tests/e2e/dashboard-core-flows.spec.ts:249:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('button').filter({ hasText: 'All' })
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('button').filter({ hasText: 'All' })

```

```yaml
- banner:
  - link "CTC Research":
    - /url: /
  - navigation:
    - link "Home":
      - /url: /
    - link "About":
      - /url: /about-us
    - link "Services":
      - /url: /services
    - link "Team":
      - /url: /team
    - link "Courses":
      - /url: /courses
    - link "Blog":
      - /url: /blog
    - link "Contact":
      - /url: /contact
  - link "Log In":
    - /url: /login
  - link "Sign Up":
    - /url: /registration
- main:
  - heading "Welcome Back" [level=1]
  - paragraph: Sign in to your account
  - text: Username
  - textbox "Username":
    - /placeholder: Enter your username
  - text: Password
  - textbox "Password":
    - /placeholder: Enter your password
  - button
  - checkbox "Remember me"
  - text: Remember me
  - link "Forgot password?":
    - /url: "#"
  - button "Sign In"
  - paragraph:
    - text: Don't have an account?
    - link "Sign up":
      - /url: /registration
- contentinfo:
  - link "CTC Research":
    - /url: /
  - paragraph: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
  - heading "Research" [level=3]
  - list:
    - listitem:
      - link "Our Services":
        - /url: /services
    - listitem:
      - link "Our Team":
        - /url: /team
    - listitem:
      - link "Training Courses":
        - /url: /courses
    - listitem:
      - link "Research Blog":
        - /url: /blog
  - heading "Support" [level=3]
  - list:
    - listitem:
      - link "Contact Us":
        - /url: /contact
    - listitem:
      - link "About CTC":
        - /url: /about-us
    - listitem:
      - link "FAQ":
        - /url: /faq
    - listitem:
      - link "Privacy Policy":
        - /url: /privacy
  - heading "Get Involved" [level=3]
  - list:
    - listitem:
      - link "Join a Trial":
        - /url: /registration
    - listitem:
      - link "Partner With Us":
        - /url: /contact
  - paragraph: © 2026 CTC Research. All rights reserved.
- button "Select language": EN
- alert
```

# Test source

```ts
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
  236 |   test("stats cards have values", async ({ page }) => {
  237 |     await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });
  238 | 
  239 |     // Stat values render (may show 0 when not authenticated)
  240 |     const statValues = page.locator(".text-2xl.font-bold");
  241 |     const count = await statValues.count();
  242 |     expect(count).toBeGreaterThanOrEqual(4);
  243 |   });
  244 | });
  245 | 
  246 | // ── 6. Enrolled Courses Page ─────────────────────────────────────────
  247 | 
  248 | test.describe("Enrolled Courses – Filters & Search", () => {
  249 |   test("filter buttons render and activate on click", async ({ page }) => {
  250 |     await page.goto("/student-dashboard/enrolled-courses", {
  251 |       waitUntil: "networkidle",
  252 |       timeout: 15000,
  253 |     });
  254 | 
  255 |     // Filter buttons: All, Active, Completed
  256 |     const allBtn = page.locator("button", { hasText: "All" });
  257 |     const activeBtn = page.locator("button", { hasText: "Active" });
  258 |     const completedBtn = page.locator("button", { hasText: "Completed" });
  259 | 
> 260 |     await expect(allBtn).toBeVisible();
      |                          ^ Error: expect(locator).toBeVisible() failed
  261 |     await expect(activeBtn).toBeVisible();
  262 |     await expect(completedBtn).toBeVisible();
  263 | 
  264 |     // "All" should be active by default (bg-teal / text-white)
  265 |     await expect(allBtn).toHaveClass(/text-white/);
  266 |     await expect(allBtn).toHaveClass(/ctc-primary/);
  267 | 
  268 |     // Click "Active" — it should become active, "All" should become inactive
  269 |     await activeBtn.click();
  270 |     await expect(activeBtn).toHaveClass(/text-white/);
  271 |     await expect(activeBtn).toHaveClass(/ctc-primary/);
  272 |     await expect(allBtn).not.toHaveClass(/text-white/);
  273 | 
  274 |     // Click "Completed" — it should become active, "Active" should become inactive
  275 |     await completedBtn.click();
  276 |     await expect(completedBtn).toHaveClass(/text-white/);
  277 |     await expect(completedBtn).toHaveClass(/ctc-primary/);
  278 |     await expect(activeBtn).not.toHaveClass(/text-white/);
  279 |   });
  280 | 
  281 |   test("search input accepts text", async ({ page }) => {
  282 |     await page.goto("/student-dashboard/enrolled-courses", {
  283 |       waitUntil: "networkidle",
  284 |       timeout: 15000,
  285 |     });
  286 | 
  287 |     const searchInput = page.locator('input[placeholder="Search courses..."]');
  288 |     await expect(searchInput).toBeVisible();
  289 | 
  290 |     await searchInput.fill("Machine Learning");
  291 |     expect(await searchInput.inputValue()).toBe("Machine Learning");
  292 |   });
  293 | 
  294 |   test("stats cards display headers", async ({ page }) => {
  295 |     await page.goto("/student-dashboard/enrolled-courses", {
  296 |       waitUntil: "networkidle",
  297 |       timeout: 15000,
  298 |     });
  299 | 
  300 |     // Stats should be visible
  301 |     await expect(page.locator("text=Total Enrolled")).toBeVisible();
  302 |     await expect(page.locator("text=In Progress")).toBeVisible();
  303 |     await expect(page.locator("text=Completed")).toBeVisible();
  304 |   });
  305 | });
  306 | 
  307 | // ── 7. History Page ──────────────────────────────────────────────────
  308 | 
  309 | test.describe("History – Timeline & Filters", () => {
  310 |   test("activity filter dropdown exists", async ({ page }) => {
  311 |     await page.goto("/student-dashboard/history", {
  312 |       waitUntil: "networkidle",
  313 |       timeout: 15000,
  314 |     });
  315 | 
  316 |     // Filter select should exist
  317 |     const filterSelect = page.locator("select");
  318 |     await expect(filterSelect).toBeVisible();
  319 | 
  320 |     // Has expected options
  321 |     const options = await filterSelect.locator("option").allTextContents();
  322 |     expect(options.length).toBeGreaterThanOrEqual(4);
  323 |     expect(options).toContain("All Activity");
  324 |     expect(options).toContain("Completed");
  325 |   });
  326 | 
  327 |   test("stats cards display headers", async ({ page }) => {
  328 |     await page.goto("/student-dashboard/history", {
  329 |       waitUntil: "networkidle",
  330 |       timeout: 15000,
  331 |     });
  332 | 
  333 |     await expect(page.locator("text=Courses Enrolled")).toBeVisible();
  334 |     await expect(page.locator("text=Hours Learned")).toBeVisible();
  335 |   });
  336 | 
  337 |   test("timeline line is rendered", async ({ page }) => {
  338 |     await page.goto("/student-dashboard/history", {
  339 |       waitUntil: "networkidle",
  340 |       timeout: 15000,
  341 |     });
  342 | 
  343 |     // The timeline uses a vertical line (w-0.5 bg-gray-200) via absolute positioning
  344 |     // We check that the timeline section is in the DOM
  345 |     const timelineIcons = page.locator("svg").first();
  346 |     await expect(timelineIcons).toBeVisible();
  347 |   });
  348 | });
  349 | 
  350 | // ── 8. Reviews Page ──────────────────────────────────────────────────
  351 | 
  352 | test.describe("Reviews – Star Rating & Submit", () => {
  353 |   test("empty state shows when no courses to review", async ({ page }) => {
  354 |     await page.goto("/student-dashboard/reviews", {
  355 |       waitUntil: "networkidle",
  356 |       timeout: 15000,
  357 |     });
  358 | 
  359 |     // Either review cards or empty state will show
  360 |     const reviewCards = page.locator("button", { hasText: "Submit Review" });
```