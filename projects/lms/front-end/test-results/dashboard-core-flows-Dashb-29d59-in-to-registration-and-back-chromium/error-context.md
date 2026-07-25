# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> Dashboard Navigation – Cross-Page >> navigate from login to registration and back
- Location: tests/e2e/dashboard-core-flows.spec.ts:481:7

# Error details

```
Error: locator.click: Error: strict mode violation: locator('a[href="/registration"]') resolved to 3 elements:
    1) <a href="/registration" class="btn-white px-4 py-2 rounded-lg font-medium text-sm">Sign Up</a> aka getByRole('link', { name: 'Sign Up', exact: true })
    2) <a href="/registration" class="text-[rgb(var(--ctc-primary))] hover:text-[rgb(var(--ctc-primary-dark))] font-medium">Sign up</a> aka getByRole('link', { name: 'Sign up', exact: true })
    3) <a href="/registration" class="text-sm text-gray-400 hover:text-white transition-colors duration-200">Join a Trial</a> aka getByRole('link', { name: 'Join a Trial' })

Call log:
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
> 485 |     await page.locator('a[href="/registration"]').click();
      |                                                   ^ Error: locator.click: Error: strict mode violation: locator('a[href="/registration"]') resolved to 3 elements:
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