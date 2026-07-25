# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> Wishlist – Cards & Interactions >> remove button appears on hover and removes course
- Location: tests/e2e/dashboard-core-flows.spec.ts:403:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.hover: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('.card.overflow-hidden').first()

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
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
        - heading "404" [level=1] [ref=e25]
        - heading "This page could not be found." [level=2] [ref=e27]
    - contentinfo [ref=e28]:
      - generic [ref=e29]:
        - generic [ref=e30]:
          - generic [ref=e31]:
            - link "CTC Research" [ref=e32] [cursor=pointer]:
              - /url: /
              - img [ref=e33]
              - generic [ref=e35]: CTC Research
            - paragraph [ref=e36]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e37]:
            - heading "Research" [level=3] [ref=e38]
            - list [ref=e39]:
              - listitem [ref=e40]:
                - link "Our Services" [ref=e41] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e42]:
                - link "Our Team" [ref=e43] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e44]:
                - link "Training Courses" [ref=e45] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e46]:
                - link "Research Blog" [ref=e47] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e48]:
            - heading "Support" [level=3] [ref=e49]
            - list [ref=e50]:
              - listitem [ref=e51]:
                - link "Contact Us" [ref=e52] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e53]:
                - link "About CTC" [ref=e54] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e55]:
                - link "FAQ" [ref=e56] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e57]:
                - link "Privacy Policy" [ref=e58] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e59]:
            - heading "Get Involved" [level=3] [ref=e60]
            - list [ref=e61]:
              - listitem [ref=e62]:
                - link "Join a Trial" [ref=e63] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e64]:
                - link "Partner With Us" [ref=e65] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e67]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e70] [cursor=pointer]:
    - img [ref=e71]
    - generic [ref=e73]: EN
  - alert [ref=e74]
```

# Test source

```ts
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
> 411 |     await firstCard.hover();
      |                     ^ Error: locator.hover: Test timeout of 30000ms exceeded.
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
  488 | 
  489 |     // Registration page → Sign in link → Login page
  490 |     await page.locator('a[href="/login"]').click();
  491 |     await page.waitForURL("**/login");
  492 |     await expect(page.locator("h1")).toContainText("Welcome Back");
  493 |   });
  494 | 
  495 |   test("student dashboard quick nav links lead to sub-pages", async ({ page }) => {
  496 |     await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });
  497 | 
  498 |     // Click "My Courses" quick nav link
  499 |     const myCoursesLink = page.locator('a[href="/student-dashboard/enrolled-courses"]');
  500 |     if (await myCoursesLink.isVisible()) {
  501 |       await myCoursesLink.click();
  502 |       await page.waitForURL("**/student-dashboard/enrolled-courses");
  503 |       await expect(page.locator("h1")).toContainText("My Courses");
  504 |     }
  505 |   });
  506 | });
  507 | 
```