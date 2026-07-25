# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-core-flows.spec.ts >> Student Dashboard – Main Page >> stats cards have values
- Location: tests/e2e/dashboard-core-flows.spec.ts:236:7

# Error details

```
Error: expect(received).toBeGreaterThanOrEqual(expected)

Expected: >= 4
Received:    0
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
  236 |   test("stats cards have values", async ({ page }) => {
  237 |     await page.goto("/student-dashboard", { waitUntil: "networkidle", timeout: 15000 });
  238 | 
  239 |     // Stat values render (may show 0 when not authenticated)
  240 |     const statValues = page.locator(".text-2xl.font-bold");
  241 |     const count = await statValues.count();
> 242 |     expect(count).toBeGreaterThanOrEqual(4);
      |                   ^ Error: expect(received).toBeGreaterThanOrEqual(expected)
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
```