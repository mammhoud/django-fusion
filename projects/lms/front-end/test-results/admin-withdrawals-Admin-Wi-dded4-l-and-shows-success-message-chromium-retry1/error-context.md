# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin-withdrawals.spec.ts >> Admin Withdrawal Approvals — E2E >> Approve Withdrawal >> approves a pending withdrawal and shows success message
- Location: tests/e2e/admin-withdrawals.spec.ts:259:9

# Error details

```
Error: locator.click: Error: strict mode violation: locator('button').filter({ hasText: 'Approve' }) resolved to 2 elements:
    1) <button class="px-3 py-1.5 text-sm rounded-lg transition-all font-medium capitalize bg-white border border-gray-200 text-gray-600 hover:bg-gray-50">approved</button> aka getByRole('button', { name: 'approved' })
    2) <button title="Approve withdrawal" class="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50">…</button> aka getByRole('button', { name: 'Approve', description: 'Approve withdrawal' })

Call log:
  - waiting for locator('button').filter({ hasText: 'Approve' })

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
                - row "#10 Jane Doe $300 PayPal Jul 24, 2026 Pending Approve Reject" [ref=e79]:
                  - cell "#10" [ref=e80]
                  - cell "Jane Doe" [ref=e81]
                  - cell "$300" [ref=e82]
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
  189 | 
  190 |       await expect(page.locator("text=This page is only available for administrators")).toBeVisible();
  191 |     });
  192 |   });
  193 | 
  194 |   // ── 2. Withdrawals Table ────────────────────────────────────────
  195 | 
  196 |   test.describe("Withdrawals Table Display", () => {
  197 |     test("renders pending withdrawals in a table", async ({ page }) => {
  198 |       await mockAdminSession(page);
  199 |       const withdrawals = [
  200 |         makePendingWithdrawal({ id: 1, amount: 200 }),
  201 |         makePendingWithdrawal({ id: 2, amount: 500, instructor_name: "Alice Johnson", payment_method: "bank_transfer", payment_method_display: "Bank Transfer" }),
  202 |         makePendingWithdrawal({ id: 3, amount: 150 }),
  203 |       ];
  204 |       await mockWithdrawalsList(page, withdrawals);
  205 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  206 | 
  207 |       // Table rows for each withdrawal
  208 |       const rows = page.locator("tbody tr");
  209 |       await expect(rows).toHaveCount(3);
  210 | 
  211 |       // Amounts
  212 |       await expect(page.locator("text=$200")).toBeVisible();
  213 |       await expect(page.locator("text=$500")).toBeVisible();
  214 |       await expect(page.locator("text=$150")).toBeVisible();
  215 | 
  216 |       // Instructor names
  217 |       await expect(page.locator("text=Jane Doe")).toBeVisible();
  218 |       await expect(page.locator("text=Alice Johnson")).toBeVisible();
  219 |     });
  220 | 
  221 |     test("shows empty state when no withdrawals exist", async ({ page }) => {
  222 |       await mockAdminSession(page);
  223 |       await mockWithdrawalsList(page, [], 0);
  224 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  225 | 
  226 |       await expect(page.locator("text=No withdrawals found")).toBeVisible();
  227 |     });
  228 |   });
  229 | 
  230 |   // ── 3. Status Filters ───────────────────────────────────────────
  231 | 
  232 |   test.describe("Status Filters", () => {
  233 |     test("filter buttons toggle active state", async ({ page }) => {
  234 |       await mockAdminSession(page);
  235 |       await mockWithdrawalsList(page, [makePendingWithdrawal()]);
  236 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  237 | 
  238 |       // "all" should be active by default
  239 |       const allBtn = page.locator("button", { hasText: "all" });
  240 |       await expect(allBtn).toHaveClass(/text-white/);
  241 | 
  242 |       // Click "pending"
  243 |       const pendingBtn = page.locator("button", { hasText: "pending" });
  244 |       await pendingBtn.click();
  245 |       await expect(pendingBtn).toHaveClass(/text-white/);
  246 |       await expect(allBtn).not.toHaveClass(/text-white/);
  247 | 
  248 |       // Click "approved"
  249 |       const approvedBtn = page.locator("button", { hasText: "approved" });
  250 |       await approvedBtn.click();
  251 |       await expect(approvedBtn).toHaveClass(/text-white/);
  252 |       await expect(pendingBtn).not.toHaveClass(/text-white/);
  253 |     });
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
> 289 |       await approveBtn.click();
      |                        ^ Error: locator.click: Error: strict mode violation: locator('button').filter({ hasText: 'Approve' }) resolved to 2 elements:
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
```