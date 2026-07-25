# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin-withdrawals.spec.ts >> Admin Withdrawal Approvals — E2E >> Reject Withdrawal >> rejects a pending withdrawal with a reason
- Location: tests/e2e/admin-withdrawals.spec.ts:326:9

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: expect(locator).toBeVisible() failed

Locator: locator('input[placeholder="Reason (optional)"]')
Expected: visible
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('input[placeholder="Reason (optional)"]')

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
  - complementary:
    - navigation:
      - link "Overview":
        - /url: /dashboard
      - link "Withdrawals":
        - /url: /dashboard/admin/withdrawals
      - link "Courses":
        - /url: /dashboard/courses
      - link "Students":
        - /url: /dashboard/enrolled-courses
      - link "Reviews":
        - /url: /dashboard/review
      - link "History":
        - /url: /dashboard/history
  - main:
    - link "Back to Dashboard":
      - /url: /dashboard
    - heading "Withdrawal Approvals" [level=1]
    - paragraph: Review and manage instructor withdrawal requests
    - button "all"
    - button "pending"
    - button "approved"
    - button "rejected"
    - button "completed"
    - button "cancelled"
    - button "Refresh"
    - table:
      - rowgroup:
        - row "ID Instructor Amount Method Date Status Actions":
          - columnheader "ID"
          - columnheader "Instructor"
          - columnheader "Amount"
          - columnheader "Method"
          - columnheader "Date"
          - columnheader "Status"
          - columnheader "Actions"
      - rowgroup:
        - row "#30 Jane Doe $250 PayPal Jul 24, 2026 Pending Approve Reject":
          - cell "#30"
          - cell "Jane Doe"
          - cell "$250"
          - cell "PayPal"
          - cell "Jul 24, 2026"
          - cell "Pending"
          - cell "Approve Reject":
            - button "Approve"
            - button "Reject"
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
  254 |   });
  255 | 
  256 |   // ── 4. Approve Withdrawal ───────────────────────────────────────
  257 | 
  258 |   test.describe("Approve Withdrawal", () => {
  259 |     test("approves a pending withdrawal and shows success message", async ({ page }) => {
  260 |       await mockAdminSession(page);
  261 |       const pending = makePendingWithdrawal({ id: 10, amount: 300 });
  262 |       await mockWithdrawalsList(page, [pending]);
  263 | 
  264 |       // Mock approve endpoint
  265 |       let approveCalled = false;
  266 |       await page.route("**/apis/withdrawals/10/approve/", (route) => {
  267 |         if (route.request().method() === "PATCH") {
  268 |           approveCalled = true;
  269 |           return route.fulfill({
  270 |             status: 200,
  271 |             contentType: "application/json",
  272 |             body: JSON.stringify({
  273 |               ...pending,
  274 |               status: "approved",
  275 |               status_display: "Approved",
  276 |               processed_by: 99,
  277 |               processed_at: "2026-07-25T12:00:00Z",
  278 |             }),
  279 |           });
  280 |         }
  281 |         return route.continue();
  282 |       });
  283 | 
  284 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  285 | 
  286 |       // Click Approve
  287 |       const approveBtn = page.locator("button", { hasText: "Approve" });
  288 |       await expect(approveBtn).toBeVisible();
  289 |       await approveBtn.click();
  290 | 
  291 |       // Verify success message
  292 |       await expect(
  293 |         page.locator("text=/Withdrawal #10 approved successfully/i")
  294 |       ).toBeVisible({ timeout: 10000 });
  295 |       expect(approveCalled).toBe(true);
  296 |     });
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
> 354 |       await expect(reasonInput).toBeVisible();
      |                                 ^ Error: expect(locator).toBeVisible() failed
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
  397 |       await expect(backLink).toBeVisible();
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