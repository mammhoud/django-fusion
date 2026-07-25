# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> History – Timeline & Filters >> stats cards display headers
- Location: tests/e2e/dashboard-core-flows.spec.ts:327:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Courses Enrolled')
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('text=Courses Enrolled')

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
  260 |     await expect(allBtn).toBeVisible();
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
> 333 |     await expect(page.locator("text=Courses Enrolled")).toBeVisible();
      |                                                         ^ Error: expect(locator).toBeVisible() failed
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
  361 |     const emptyTitle = page.locator("text=No courses to review yet");
  362 | 
  363 |     // Both should not be visible at the same time
  364 |     const hasCards = (await reviewCards.count()) > 0;
  365 |     const hasEmpty = (await emptyTitle.count()) > 0;
  366 |     expect(hasCards || hasEmpty, "Should show review cards or empty state").toBe(true);
  367 |   });
  368 | });
  369 | 
  370 | // ── 9. Wishlist Page ─────────────────────────────────────────────────
  371 | 
  372 | test.describe("Wishlist – Cards & Interactions", () => {
  373 |   test("wishlist renders course cards", async ({ page }) => {
  374 |     await page.goto("/student-dashboard/wishlist", {
  375 |       waitUntil: "networkidle",
  376 |       timeout: 15000,
  377 |     });
  378 | 
  379 |     // Wishlist loads with static data — course titles should appear
  380 |     const courseTitles = [
  381 |       "Advanced Machine Learning",
  382 |       "Full-Stack Web Development",
  383 |       "Data Science Fundamentals",
  384 |     ];
  385 | 
  386 |     for (const title of courseTitles) {
  387 |       await expect(page.locator(`text=${title}`).first()).toBeVisible();
  388 |     }
  389 |   });
  390 | 
  391 |   test("wishlist shows saved count", async ({ page }) => {
  392 |     await page.goto("/student-dashboard/wishlist", {
  393 |       waitUntil: "networkidle",
  394 |       timeout: 15000,
  395 |     });
  396 | 
  397 |     // Saved count indicator
  398 |     const savedText = page.locator("text=/\\d+ saved/");
  399 |     await expect(savedText).toBeVisible();
  400 |     expect(await savedText.textContent()).toContain("3");
  401 |   });
  402 | 
  403 |   test("remove button appears on hover and removes course", async ({ page }) => {
  404 |     await page.goto("/student-dashboard/wishlist", {
  405 |       waitUntil: "networkidle",
  406 |       timeout: 15000,
  407 |     });
  408 | 
  409 |     // First course card — hover to reveal the remove button
  410 |     const firstCard = page.locator(".card.overflow-hidden").first();
  411 |     await firstCard.hover();
  412 | 
  413 |     // Remove button (trash icon) should appear
  414 |     const removeBtn = firstCard.locator("button").filter({ has: page.locator("svg") }).first();
  415 |     await expect(removeBtn).toBeVisible();
  416 |     await expect(removeBtn.locator("svg")).toBeVisible();
  417 | 
  418 |     // Click remove and verify the course is gone
  419 |     await removeBtn.click();
  420 | 
  421 |     // Should now have 2 items (one removed)
  422 |     const savedText = page.locator("text=/\\d+ saved/");
  423 |     expect(await savedText.textContent()).toContain("2");
  424 |   });
  425 | 
  426 |   test("remove all courses shows empty state", async ({ page }) => {
  427 |     await page.goto("/student-dashboard/wishlist", {
  428 |       waitUntil: "networkidle",
  429 |       timeout: 15000,
  430 |     });
  431 | 
  432 |     // Remove all 3 courses
  433 |     const cards = page.locator(".card.overflow-hidden");
```