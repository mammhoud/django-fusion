# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin-withdrawals.spec.ts >> Admin Withdrawal Approvals — E2E >> Withdrawals Table Display >> renders pending withdrawals in a table
- Location: tests/e2e/admin-withdrawals.spec.ts:197:9

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Jane Doe')
Expected: visible
Error: strict mode violation: locator('text=Jane Doe') resolved to 2 elements:
    1) <td class="px-4 py-3 font-medium text-gray-900">Jane Doe</td> aka getByRole('cell', { name: 'Jane Doe' }).first()
    2) <td class="px-4 py-3 font-medium text-gray-900">Jane Doe</td> aka getByRole('cell', { name: 'Jane Doe' }).nth(1)

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for locator('text=Jane Doe')

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
                - row "#2 Alice Johnson $500 Bank Transfer Jul 24, 2026 Pending Approve Reject" [ref=e95]:
                  - cell "#2" [ref=e96]
                  - cell "Alice Johnson" [ref=e97]
                  - cell "$500" [ref=e98]
                  - cell "Bank Transfer" [ref=e99]
                  - cell "Jul 24, 2026" [ref=e100]
                  - cell "Pending" [ref=e101]:
                    - generic [ref=e102]: Pending
                  - cell "Approve Reject" [ref=e103]:
                    - generic [ref=e104]:
                      - button "Approve" [ref=e105] [cursor=pointer]:
                        - img [ref=e106]
                        - text: Approve
                      - button "Reject" [ref=e108] [cursor=pointer]:
                        - img [ref=e109]
                        - text: Reject
                - row "#3 Jane Doe $150 PayPal Jul 24, 2026 Pending Approve Reject" [ref=e111]:
                  - cell "#3" [ref=e112]
                  - cell "Jane Doe" [ref=e113]
                  - cell "$150" [ref=e114]
                  - cell "PayPal" [ref=e115]
                  - cell "Jul 24, 2026" [ref=e116]
                  - cell "Pending" [ref=e117]:
                    - generic [ref=e118]: Pending
                  - cell "Approve Reject" [ref=e119]:
                    - generic [ref=e120]:
                      - button "Approve" [ref=e121] [cursor=pointer]:
                        - img [ref=e122]
                        - text: Approve
                      - button "Reject" [ref=e124] [cursor=pointer]:
                        - img [ref=e125]
                        - text: Reject
    - contentinfo [ref=e127]:
      - generic [ref=e128]:
        - generic [ref=e129]:
          - generic [ref=e130]:
            - link "CTC Research" [ref=e131] [cursor=pointer]:
              - /url: /
              - img [ref=e132]
              - generic [ref=e134]: CTC Research
            - paragraph [ref=e135]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e136]:
            - heading "Research" [level=3] [ref=e137]
            - list [ref=e138]:
              - listitem [ref=e139]:
                - link "Our Services" [ref=e140] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e141]:
                - link "Our Team" [ref=e142] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e143]:
                - link "Training Courses" [ref=e144] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e145]:
                - link "Research Blog" [ref=e146] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e147]:
            - heading "Support" [level=3] [ref=e148]
            - list [ref=e149]:
              - listitem [ref=e150]:
                - link "Contact Us" [ref=e151] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e152]:
                - link "About CTC" [ref=e153] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e154]:
                - link "FAQ" [ref=e155] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e156]:
                - link "Privacy Policy" [ref=e157] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e158]:
            - heading "Get Involved" [level=3] [ref=e159]
            - list [ref=e160]:
              - listitem [ref=e161]:
                - link "Join a Trial" [ref=e162] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e163]:
                - link "Partner With Us" [ref=e164] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e166]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e169] [cursor=pointer]:
    - img [ref=e170]
    - generic [ref=e172]: EN
  - alert [ref=e173]
```

# Test source

```ts
  117 | // ═══════════════════════════════════════════════════════════════════
  118 | 
  119 | async function mockAdminSession(page: import("@playwright/test").Page) {
  120 |   await page.route("**/apis/auth/profile/", (route) =>
  121 |     route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(ADMIN_PROFILE) })
  122 |   );
  123 | }
  124 | 
  125 | async function mockWithdrawalsList(
  126 |   page: import("@playwright/test").Page,
  127 |   withdrawals: Withdrawal[],
  128 |   count?: number
  129 | ) {
  130 |   await page.route("**/apis/withdrawals/*", (route) => {
  131 |     const url = route.request().url();
  132 |     // Match the paginated list endpoint (NOT the summary endpoint)
  133 |     if (url.includes("/apis/withdrawals/") && !url.includes("/summary/") && !url.includes("/create/")) {
  134 |       // Skip detail/cancel/approve/reject routes — those are handled separately
  135 |       if (url.match(/\/withdrawals\/\d+\/(cancel|approve|reject)\//)) return route.continue();
  136 |       // Skip single-item detail routes
  137 |       if (url.match(/\/withdrawals\/\d+\/$/)) return route.continue();
  138 |       // Paginated list
  139 |       return route.fulfill({
  140 |         status: 200,
  141 |         contentType: "application/json",
  142 |         body: JSON.stringify({
  143 |           results: withdrawals,
  144 |           count: count ?? withdrawals.length,
  145 |           next: null,
  146 |           previous: null,
  147 |         }),
  148 |       });
  149 |     }
  150 |     return route.continue();
  151 |   });
  152 | }
  153 | 
  154 | // ═══════════════════════════════════════════════════════════════════
  155 | // Test Suite
  156 | // ═══════════════════════════════════════════════════════════════════
  157 | 
  158 | test.describe("Admin Withdrawal Approvals — E2E", () => {
  159 |   // ── 1. Auth & Access Control ─────────────────────────────────────
  160 | 
  161 |   test.describe("Auth & Access Control", () => {
  162 |     test("admin sees the withdrawal approvals page", async ({ page }) => {
  163 |       await mockAdminSession(page);
  164 |       await mockWithdrawalsList(page, [
  165 |         makePendingWithdrawal({ id: 1, amount: 200 }),
  166 |         makePendingWithdrawal({ id: 2, amount: 350, instructor_name: "Bob Smith" }),
  167 |       ]);
  168 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  169 | 
  170 |       await expect(page.locator("h1")).toContainText("Withdrawal Approvals");
  171 |       await expect(page.locator("text=Review and manage instructor withdrawal requests")).toBeVisible();
  172 |     });
  173 | 
  174 |     test("instructor is denied access to admin withdrawals page", async ({ page }) => {
  175 |       await page.route("**/apis/auth/profile/", (route) =>
  176 |         route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(INSTRUCTOR_PROFILE) })
  177 |       );
  178 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
  179 | 
  180 |       await expect(page.locator("text=This page is only available for administrators")).toBeVisible();
  181 |       await expect(page.locator("text=Withdrawal Approvals")).toHaveCount(0);
  182 |     });
  183 | 
  184 |     test("unauthenticated user is denied access", async ({ page }) => {
  185 |       await page.route("**/apis/auth/profile/", (route) =>
  186 |         route.fulfill({ status: 401, contentType: "application/json", body: "{}" })
  187 |       );
  188 |       await page.goto("/dashboard/admin/withdrawals", { waitUntil: "networkidle", timeout: 15000 });
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
> 217 |       await expect(page.locator("text=Jane Doe")).toBeVisible();
      |                                                   ^ Error: expect(locator).toBeVisible() failed
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
```