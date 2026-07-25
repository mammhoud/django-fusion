# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-ctc-theme.spec.ts >> Dashboard Pages – CTC Teal Theme >> Quiz Attempts (/dashboard/attempts)
- Location: tests/e2e/dashboard-ctc-theme.spec.ts:120:9

# Error details

```
TimeoutError: page.goto: Timeout 15000ms exceeded.
Call log:
  - navigating to "http://localhost:3457/dashboard/attempts", waiting until "networkidle"

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
    - main [ref=e22]
    - contentinfo [ref=e30]:
      - generic [ref=e31]:
        - generic [ref=e32]:
          - generic [ref=e33]:
            - link "CTC Research" [ref=e34] [cursor=pointer]:
              - /url: /
              - img [ref=e35]
              - generic [ref=e37]: CTC Research
            - paragraph [ref=e38]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e39]:
            - heading "Research" [level=3] [ref=e40]
            - list [ref=e41]:
              - listitem [ref=e42]:
                - link "Our Services" [ref=e43] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e44]:
                - link "Our Team" [ref=e45] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e46]:
                - link "Training Courses" [ref=e47] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e48]:
                - link "Research Blog" [ref=e49] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e50]:
            - heading "Support" [level=3] [ref=e51]
            - list [ref=e52]:
              - listitem [ref=e53]:
                - link "Contact Us" [ref=e54] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e55]:
                - link "About CTC" [ref=e56] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e57]:
                - link "FAQ" [ref=e58] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e59]:
                - link "Privacy Policy" [ref=e60] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e61]:
            - heading "Get Involved" [level=3] [ref=e62]
            - list [ref=e63]:
              - listitem [ref=e64]:
                - link "Join a Trial" [ref=e65] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e66]:
                - link "Partner With Us" [ref=e67] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e69]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e72] [cursor=pointer]:
    - img [ref=e73]
    - generic [ref=e75]: EN
  - alert [ref=e76]
```

# Test source

```ts
  27  | }
  28  | 
  29  | const DASHBOARD_PAGES: DashboardPage[] = [
  30  |   {
  31  |     path: "/dashboard",
  32  |     name: "Main Dashboard",
  33  |     expectedClasses: ["card-gradient", "btn-primary", "progress-fill"],
  34  |     forbiddenClasses: ["indigo-", "purple-"],
  35  |   },
  36  |   {
  37  |     path: "/dashboard/courses",
  38  |     name: "Courses List",
  39  |     expectedClasses: ["btn-primary", "card-gradient"],
  40  |     forbiddenClasses: ["indigo-", "purple-"],
  41  |   },
  42  |   {
  43  |     path: "/dashboard/courses/new",
  44  |     name: "New Course",
  45  |     expectedClasses: ["btn-primary", "input-field"],
  46  |     forbiddenClasses: ["indigo-", "purple-"],
  47  |   },
  48  |   {
  49  |     path: "/dashboard/quiz",
  50  |     name: "Quiz Dispatcher",
  51  |     expectedClasses: ["btn-primary"],
  52  |     forbiddenClasses: ["indigo-", "purple-"],
  53  |   },
  54  |   {
  55  |     path: "/dashboard/enrolled-courses",
  56  |     name: "Enrolled Courses",
  57  |     expectedClasses: ["card-gradient", "progress-fill", "progress-track"],
  58  |     forbiddenClasses: ["indigo-", "purple-"],
  59  |   },
  60  |   {
  61  |     path: "/dashboard/review",
  62  |     name: "Review",
  63  |     expectedClasses: ["btn-primary"],
  64  |     forbiddenClasses: ["indigo-", "purple-"],
  65  |   },
  66  |   {
  67  |     path: "/dashboard/history",
  68  |     name: "History",
  69  |     expectedClasses: ["btn-primary"],
  70  |     forbiddenClasses: ["indigo-", "purple-"],
  71  |   },
  72  |   {
  73  |     path: "/dashboard/profile",
  74  |     name: "Profile",
  75  |     expectedClasses: ["btn-primary", "input-field"],
  76  |     forbiddenClasses: ["indigo-", "purple-"],
  77  |   },
  78  |   {
  79  |     path: "/dashboard/attempts",
  80  |     name: "Quiz Attempts",
  81  |     expectedClasses: ["btn-primary"],
  82  |     forbiddenClasses: ["indigo-", "purple-"],
  83  |   },
  84  |   {
  85  |     path: "/dashboard/student-manage",
  86  |     name: "Student Management",
  87  |     expectedClasses: ["btn-primary", "progress-fill"],
  88  |     forbiddenClasses: ["indigo-", "purple-"],
  89  |   },
  90  |   {
  91  |     path: "/dashboard/withdraw",
  92  |     name: "Withdraw",
  93  |     expectedClasses: ["btn-primary", "input-field"],
  94  |     forbiddenClasses: ["indigo-", "purple-"],
  95  |   },
  96  |   {
  97  |     path: "/dashboard/announcement",
  98  |     name: "Announcement",
  99  |     expectedClasses: ["btn-primary"],
  100 |     forbiddenClasses: ["indigo-", "purple-"],
  101 |   },
  102 |   {
  103 |     path: "/dashboard/assignment",
  104 |     name: "Assignment",
  105 |     expectedClasses: ["btn-primary"],
  106 |     forbiddenClasses: ["indigo-", "purple-"],
  107 |   },
  108 |   {
  109 |     path: "/dashboard/courses/1/edit",
  110 |     name: "Edit Course",
  111 |     expectedClasses: ["btn-primary", "input-field"],
  112 |     forbiddenClasses: ["indigo-", "purple-"],
  113 |   },
  114 | ];
  115 | 
  116 | // ── Tests ────────────────────────────────────────────────────────────
  117 | 
  118 | test.describe("Dashboard Pages – CTC Teal Theme", () => {
  119 |   for (const page of DASHBOARD_PAGES) {
  120 |     test(`${page.name} (${page.path})`, async ({ page: browserPage }) => {
  121 |       const consoleErrors: string[] = [];
  122 |       browserPage.on("console", (msg) => {
  123 |         if (msg.type() === "error") consoleErrors.push(msg.text());
  124 |       });
  125 | 
  126 |       // Navigate and wait for network idle
> 127 |       const response = await browserPage.goto(page.path, {
      |                                          ^ TimeoutError: page.goto: Timeout 15000ms exceeded.
  128 |         waitUntil: "networkidle",
  129 |         timeout: 15000,
  130 |       });
  131 | 
  132 |       // ── Assertion 1: HTTP 200 ──
  133 |       expect(response?.status(), `${page.name} should return 200`).toBe(200);
  134 | 
  135 |       // ── Assertion 2: No console errors ──
  136 |       const filteredErrors = consoleErrors.filter(
  137 |         (e) =>
  138 |           !e.includes(" hydration ") &&
  139 |           !e.includes("Warning:") &&
  140 |           !e.includes("next")
  141 |       );
  142 |       expect(
  143 |         filteredErrors,
  144 |         `${page.name} should have no console errors (found: ${filteredErrors.join("; ")})`
  145 |       ).toHaveLength(0);
  146 | 
  147 |       // Get the full HTML to search for CSS classes
  148 |       const html = await browserPage.content();
  149 |       const bodyText = await browserPage.textContent("body");
  150 | 
  151 |       // ── Assertion 3: Expected CTC teal classes present ──
  152 |       for (const cls of page.expectedClasses) {
  153 |         const hasClass = html.includes(cls);
  154 |         expect(
  155 |           hasClass,
  156 |           `${page.name} should contain CSS class "${cls}" (CTC teal theme)`
  157 |         ).toBe(true);
  158 |       }
  159 | 
  160 |       // ── Assertion 4: No forbidden old-theme classes ──
  161 |       for (const cls of page.forbiddenClasses) {
  162 |         const hasForbidden = html.includes(cls);
  163 |         expect(
  164 |           hasForbidden,
  165 |           `${page.name} should NOT contain forbidden class "${cls}"`
  166 |         ).toBe(false);
  167 |       }
  168 | 
  169 |       // ── Assertion 5: Page has meaningful content (not empty/error) ──
  170 |       expect(
  171 |         bodyText?.length ?? 0,
  172 |         `${page.name} should have page content`
  173 |       ).toBeGreaterThan(50);
  174 | 
  175 |       // ── Assertion 6: No "404" or "Not Found" in body ──
  176 |       if (bodyText) {
  177 |         expect(
  178 |           bodyText.includes("404") || bodyText.includes("Not Found"),
  179 |           `${page.name} should not show 404 error`
  180 |         ).toBe(false);
  181 |       }
  182 |     });
  183 |   }
  184 | });
  185 | 
  186 | // ── Cross-page consistency tests ──────────────────────────────────────
  187 | 
  188 | test.describe("Cross-page CTC Theme Consistency", () => {
  189 |   test("CTC primary CSS variables are defined", async ({ page }) => {
  190 |     await page.goto("/dashboard", { waitUntil: "networkidle" });
  191 | 
  192 |     // Verify the CTC teal custom properties are set on :root
  193 |     const ctcPrimary = await page.evaluate(() =>
  194 |       getComputedStyle(document.documentElement).getPropertyValue("--ctc-primary").trim()
  195 |     );
  196 |     const ctcPrimaryDark = await page.evaluate(() =>
  197 |       getComputedStyle(document.documentElement).getPropertyValue("--ctc-primary-dark").trim()
  198 |     );
  199 | 
  200 |     expect(ctcPrimary).toBe("0 161 179");
  201 |     expect(ctcPrimaryDark).toBe("0 122 136");
  202 |   });
  203 | 
  204 |   test("All dashboard pages share consistent sidebar navigation", async ({
  205 |     page,
  206 |   }) => {
  207 |     await page.goto("/dashboard", { waitUntil: "networkidle" });
  208 | 
  209 |     // Sidebar links should use /dashboard/* paths
  210 |     const sidebarLinks = await page.$$eval(
  211 |       'nav a[href*="/dashboard"]',
  212 |       (links) => links.map((l) => (l as HTMLAnchorElement).getAttribute("href"))
  213 |     );
  214 | 
  215 |     expect(sidebarLinks.length).toBeGreaterThanOrEqual(3);
  216 |     for (const href of sidebarLinks) {
  217 |       expect(href).toMatch(/^\/dashboard/);
  218 |     }
  219 |   });
  220 | 
  221 |   test("No indigo or purple Tailwind classes anywhere in dashboard", async ({
  222 |     page,
  223 |   }) => {
  224 |     // Sample 4 key pages — if all pass, the full per-page tests above
  225 |     // already verify all 14 individually.
  226 |     const samplePages = [
  227 |       "/dashboard",
```