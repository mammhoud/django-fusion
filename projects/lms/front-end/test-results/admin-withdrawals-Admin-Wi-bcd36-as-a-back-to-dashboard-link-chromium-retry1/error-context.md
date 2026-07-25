# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin-withdrawals.spec.ts >> Admin Withdrawal Approvals — E2E >> Navigation >> has a back-to-dashboard link
- Location: tests/e2e/admin-withdrawals.spec.ts:391:9

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('a[href="/dashboard"]')
Expected: visible
Error: strict mode violation: locator('a[href="/dashboard"]') resolved to 2 elements:
    1) <a href="/dashboard" class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors↵                    text-gray-600 hover:text-gray-900 hover:bg-gray-50">…</a> aka getByRole('link', { name: 'Overview' })
    2) <a href="/dashboard" class="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-[rgb(var(--ctc-primary))] mb-3 transition-colors">…</a> aka getByRole('link', { name: 'Back to Dashboard' })

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('a[href="/dashboard"]')

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
        - complementary [ref=e25]:
          - navigation [ref=e26]:
            - link "Overview" [ref=e27] [cursor=pointer]:
              - /url: /dashboard
              - img [ref=e28]
              - text: Overview
            - link "Withdrawals" [ref=e30] [cursor=pointer]:
              - /url: /dashboard/admin/withdrawals
              - img [ref=e31]
              - text: Withdrawals
            - link "Courses" [ref=e34] [cursor=pointer]:
              - /url: /dashboard/courses
              - img [ref=e35]
              - text: Courses
            - link "Students" [ref=e37] [cursor=pointer]:
              - /url: /dashboard/enrolled-courses
              - img [ref=e38]
              - text: Students
            - link "Reviews" [ref=e40] [cursor=pointer]:
              - /url: /dashboard/review
              - img [ref=e41]
              - text: Reviews
            - link "History" [ref=e43] [cursor=pointer]:
              - /url: /dashboard/history
              - img [ref=e44]
              - text: History
        - main [ref=e46]:
          - generic [ref=e47]:
            - generic [ref=e48]:
              - link "Back to Dashboard" [ref=e49] [cursor=pointer]:
                - /url: /dashboard
                - img [ref=e50]
                - text: Back to Dashboard
              - heading "Withdrawal Approvals" [level=1] [ref=e52]
              - paragraph [ref=e53]: Review and manage instructor withdrawal requests
            - generic [ref=e54]:
              - generic [ref=e55]:
                - img [ref=e56]
                - button "all" [ref=e58] [cursor=pointer]
                - button "pending" [ref=e59] [cursor=pointer]
                - button "approved" [ref=e60] [cursor=pointer]
                - button "rejected" [ref=e61] [cursor=pointer]
                - button "completed" [ref=e62] [cursor=pointer]
                - button "cancelled" [ref=e63] [cursor=pointer]
              - button "Refresh" [ref=e64] [cursor=pointer]:
                - img [ref=e65]
                - text: Refresh
            - table [ref=e68]:
              - rowgroup [ref=e69]:
                - row "ID Instructor Amount Method Date Status Actions" [ref=e70]:
                  - columnheader "ID" [ref=e71]
                  - columnheader "Instructor" [ref=e72]
                  - columnheader "Amount" [ref=e73]
                  - columnheader "Method" [ref=e74]
                  - columnheader "Date" [ref=e75]
                  - columnheader "Status" [ref=e76]
                  - columnheader "Actions" [ref=e77]
              - rowgroup [ref=e78]:
                - row "#1 Jane Doe $200 PayPal Jul 24, 2026 Pending Approve Reject" [ref=e79]:
                  - cell "#1" [ref=e80]
                  - cell "Jane Doe" [ref=e81]
                  - cell "$200" [ref=e82]
                  - cell "PayPal" [ref=e83]
                  - cell "Jul 24, 2026" [ref=e84]
                  - cell "Pending" [ref=e85]:
                    - generic [ref=e86]: Pending
                  - cell "Approve Reject" [ref=e87]:
                    - generic [ref=e88]:
                      - button "Approve" [ref=e89] [cursor=pointer]:
                        - img [ref=e90]
                        - text: Approve
                      - button "Reject" [ref=e92] [cursor=pointer]:
                        - img [ref=e93]
                        - text: Reject
    - contentinfo [ref=e95]:
      - generic [ref=e96]:
        - generic [ref=e97]:
          - generic [ref=e98]:
            - link "CTC Research" [ref=e99] [cursor=pointer]:
              - /url: /
              - img [ref=e100]
              - generic [ref=e102]: CTC Research
            - paragraph [ref=e103]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e104]:
            - heading "Research" [level=3] [ref=e105]
            - list [ref=e106]:
              - listitem [ref=e107]:
                - link "Our Services" [ref=e108] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e109]:
                - link "Our Team" [ref=e110] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e111]:
                - link "Training Courses" [ref=e112] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e113]:
                - link "Research Blog" [ref=e114] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e115]:
            - heading "Support" [level=3] [ref=e116]
            - list [ref=e117]:
              - listitem [ref=e118]:
                - link "Contact Us" [ref=e119] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e120]:
                - link "About CTC" [ref=e121] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e122]:
                - link "FAQ" [ref=e123] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e124]:
                - link "Privacy Policy" [ref=e125] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e126]:
            - heading "Get Involved" [level=3] [ref=e127]
            - list [ref=e128]:
              - listitem [ref=e129]:
                - link "Join a Trial" [ref=e130] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e131]:
                - link "Partner With Us" [ref=e132] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e134]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e137] [cursor=pointer]:
    - img [ref=e138]
    - generic [ref=e140]: EN
  - alert [ref=e141]
```

# Test source

```ts
  297 | 
  298 |     test("shows error when approval fails", async ({ page }) => {
  299 |       await mockAdminSession(page);
  300 |       await mockWithdrawalsList(page, [makePendingWithdrawal({ id: 20, amount: 400 })]);
  301 | 
  302 |       await page.route("**/apis/withdrawals/20/approve/", (route) => {
  303 |         if (route.request().method() === "PATCH") {
  304 |           return route.fulfill({
  305 |             status: 400,
  306 |             contentType: "application/json",
  307 |             body: JSON.stringify({ message: "Withdrawal has already been processed." }),
  308 |           });
  309 |         }
  310 |         return route.continue();
  311 |       });
  312 | 
  313 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  314 | 
  315 |       await page.locator("button", { hasText: "Approve" }).click();
  316 | 
  317 |       await expect(
  318 |         page.locator("text=Withdrawal has already been processed.")
  319 |       ).toBeVisible({ timeout: 10000 });
  320 |     });
  321 |   });
  322 | 
  323 |   // ── 5. Reject Withdrawal ────────────────────────────────────────
  324 | 
  325 |   test.describe("Reject Withdrawal", () => {
  326 |     test("rejects a pending withdrawal with a reason", async ({ page }) => {
  327 |       await mockAdminSession(page);
  328 |       await mockWithdrawalsList(page, [makePendingWithdrawal({ id: 30, amount: 250 })]);
  329 | 
  330 |       let rejectPayload: any = null;
  331 |       await page.route("**/apis/withdrawals/30/reject/", (route) => {
  332 |         if (route.request().method() === "PATCH") {
  333 |           rejectPayload = route.request().postDataJSON();
  334 |           return route.fulfill({
  335 |             status: 200,
  336 |             contentType: "application/json",
  337 |             body: JSON.stringify({
  338 |               ...makePendingWithdrawal({ id: 30 }),
  339 |               status: "rejected",
  340 |               status_display: "Rejected",
  341 |             }),
  342 |           });
  343 |         }
  344 |         return route.continue();
  345 |       });
  346 | 
  347 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  348 | 
  349 |       // Click Reject to reveal the reason input
  350 |       await page.locator("button", { hasText: "Reject" }).click();
  351 | 
  352 |       // Fill in rejection reason
  353 |       const reasonInput = page.locator('input[placeholder="Reason (optional)"]');
  354 |       await expect(reasonInput).toBeVisible();
  355 |       await reasonInput.fill("Invalid account details");
  356 | 
  357 |       // Click Confirm
  358 |       await page.locator("button", { hasText: "Confirm" }).click();
  359 | 
  360 |       // Verify success
  361 |       await expect(
  362 |         page.locator("text=/Withdrawal #30 rejected/i")
  363 |       ).toBeVisible({ timeout: 10000 });
  364 |       expect(rejectPayload).toBeDefined();
  365 |     });
  366 | 
  367 |     test("cancels rejection when Cancel is clicked", async ({ page }) => {
  368 |       await mockAdminSession(page);
  369 |       await mockWithdrawalsList(page, [makePendingWithdrawal({ id: 40, amount: 175 })]);
  370 | 
  371 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  372 | 
  373 |       // Click Reject to open the inline form
  374 |       await page.locator("button", { hasText: "Reject" }).click();
  375 | 
  376 |       const reasonInput = page.locator('input[placeholder="Reason (optional)"]');
  377 |       await expect(reasonInput).toBeVisible();
  378 | 
  379 |       // Click Cancel to dismiss
  380 |       await page.locator("button", { hasText: "Cancel" }).click();
  381 | 
  382 |       // The reject form should be gone and the Reject button should reappear
  383 |       await expect(reasonInput).toHaveCount(0);
  384 |       await expect(page.locator("button", { hasText: "Reject" })).toBeVisible();
  385 |     });
  386 |   });
  387 | 
  388 |   // ── 6. Back Navigation ──────────────────────────────────────────
  389 | 
  390 |   test.describe("Navigation", () => {
  391 |     test("has a back-to-dashboard link", async ({ page }) => {
  392 |       await mockAdminSession(page);
  393 |       await mockWithdrawalsList(page, [makePendingWithdrawal()]);
  394 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  395 | 
  396 |       const backLink = page.locator('a[href="/dashboard"]');
> 397 |       await expect(backLink).toBeVisible();
      |                              ^ Error: expect(locator).toBeVisible() failed
  398 |       await expect(backLink).toContainText("Back to Dashboard");
  399 |     });
  400 |   });
  401 | 
  402 |   // ── 7. Console Errors ───────────────────────────────────────────
  403 | 
  404 |   test.describe("Console Error Checks", () => {
  405 |     test("admin withdrawals page loads without critical errors", async ({ page }) => {
  406 |       const errors = await captureConsoleErrors(page);
  407 |       await mockAdminSession(page);
  408 |       await mockWithdrawalsList(page, [makePendingWithdrawal()]);
  409 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  410 | 
  411 |       await expect(page.locator("h1")).toContainText("Withdrawal Approvals");
  412 | 
  413 |       const criticalErrors = filterNextJSWarnings(errors);
  414 |       expect(criticalErrors, "Should have no critical console errors").toHaveLength(0);
  415 |     });
  416 |   });
  417 | });
  418 | 
```