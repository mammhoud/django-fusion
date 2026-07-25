# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-ctc-theme.spec.ts >> Cross-page CTC Theme Consistency >> No indigo or purple Tailwind classes anywhere in dashboard
- Location: tests/e2e/dashboard-ctc-theme.spec.ts:221:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
Call log:
  - navigating to "http://localhost:3457/dashboard/quiz", waiting until "networkidle"

```

# Test source

```ts
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
  228 |       "/dashboard/courses",
  229 |       "/dashboard/enrolled-courses",
  230 |       "/dashboard/quiz",
  231 |     ];
  232 | 
  233 |     for (const path of samplePages) {
> 234 |       await page.goto(path, { waitUntil: "networkidle" });
      |                  ^ Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
  235 |       const html = await page.content();
  236 | 
  237 |       const indigoCount = (html.match(/\bindigo-/g) || []).length;
  238 |       const purpleCount = (html.match(/\bpurple-/g) || []).length;
  239 | 
  240 |       expect(indigoCount, `${path} should have zero indigo- classes`).toBe(0);
  241 |       expect(purpleCount, `${path} should have zero purple- classes`).toBe(0);
  242 |     }
  243 |   });
  244 | 
  245 |   test("btn-primary buttons render with correct CTC teal color", async ({
  246 |     page,
  247 |   }) => {
  248 |     await page.goto("/dashboard", { waitUntil: "networkidle" });
  249 | 
  250 |     // Find the first btn-primary button and check its computed background
  251 |     const btn = page.locator(".btn-primary").first();
  252 |     if (await btn.isVisible({ timeout: 3000 }).catch(() => false)) {
  253 |       const bgColor = await btn.evaluate((el) =>
  254 |         getComputedStyle(el).backgroundColor
  255 |       );
  256 |       // rgb(0, 161, 179) is the CTC primary teal
  257 |       expect(bgColor).toBe("rgb(0, 161, 179)");
  258 |     }
  259 |   });
  260 | });
  261 | 
```