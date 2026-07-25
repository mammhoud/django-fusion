# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> Wishlist – Cards & Interactions >> wishlist renders course cards
- Location: tests/e2e/dashboard-core-flows.spec.ts:373:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Advanced Machine Learning').first()
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('text=Advanced Machine Learning').first()

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
  - heading "404" [level=1]
  - heading "This page could not be found." [level=2]
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
> 387 |       await expect(page.locator(`text=${title}`).first()).toBeVisible();
      |                                                           ^ Error: expect(locator).toBeVisible() failed
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
  434 |     const cardCount = await cards.count();
  435 |     expect(cardCount).toBe(3);
  436 | 
  437 |     for (let i = 0; i < cardCount; i++) {
  438 |       // Re-query the first card each iteration since DOM updates
  439 |       const firstCard = page.locator(".card.overflow-hidden").first();
  440 |       await firstCard.hover();
  441 |       const removeBtn = firstCard.locator("button").filter({ has: page.locator("svg") }).first();
  442 |       await removeBtn.click();
  443 |     }
  444 | 
  445 |     // After removing all, the empty state should appear
  446 |     await expect(page.locator("text=Your wishlist is empty")).toBeVisible();
  447 |   });
  448 | 
  449 |   test("each course card has price and level badge", async ({ page }) => {
  450 |     await page.goto("/student-dashboard/wishlist", {
  451 |       waitUntil: "networkidle",
  452 |       timeout: 15000,
  453 |     });
  454 | 
  455 |     // Each card should have a price and a level badge
  456 |     const prices = page.locator(".text-lg.font-bold");
  457 |     const priceCount = await prices.count();
  458 |     expect(priceCount).toBeGreaterThanOrEqual(3);
  459 | 
  460 |     // Level badges exist
  461 |     const badges = page.locator("text=/Beginner|Intermediate|Advanced/");
  462 |     expect(await badges.count()).toBeGreaterThanOrEqual(3);
  463 |   });
  464 | 
  465 |   test("View Course button links to course details", async ({ page }) => {
  466 |     await page.goto("/student-dashboard/wishlist", {
  467 |       waitUntil: "networkidle",
  468 |       timeout: 15000,
  469 |     });
  470 | 
  471 |     // Each card has a "View Course" link
  472 |     const viewLinks = page.locator('a[href*="/course-details/"]');
  473 |     expect(await viewLinks.count()).toBeGreaterThanOrEqual(3);
  474 |     await expect(viewLinks.first()).toContainText("View Course");
  475 |   });
  476 | });
  477 | 
  478 | // ── 10. Cross-Page Navigation ─────────────────────────────────────────
  479 | 
  480 | test.describe("Dashboard Navigation – Cross-Page", () => {
  481 |   test("navigate from login to registration and back", async ({ page }) => {
  482 |     await page.goto("/login", { waitUntil: "networkidle", timeout: 15000 });
  483 | 
  484 |     // Login page → Sign up link → Registration page
  485 |     await page.locator('a[href="/registration"]').click();
  486 |     await page.waitForURL("**/registration");
  487 |     await expect(page.locator("h1")).toContainText("Create Account");
```