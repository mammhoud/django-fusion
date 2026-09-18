# Precis documentation and verification changes

> **Scope:** `projects/precis/`
> **Status:** Active change ledger

<!-- AI-generated: review needed -->

This ledger records changes by concern rather than mixing frontend, backend,
operations, and documentation edits into one undifferentiated history.

## 1. CTC localization and content delivery

- The CTC backend localized page API resolves explicit `?lang=` values for
  `en`, `sv`, `fr`, `de`, `es`, `ar`, and `pt-br`.
- The static Astro shell now reads the query locale before stored preferences
  when setting `<html lang>` and `dir`.
- The About page hydrates visible hero, mission, skills, FAQ, CTA, and directory
  content from `/apis/pages/about/?lang=<code>` so a static English build does
  not mask a localized backend response.
- Arabic uses `dir="rtl"`; other supported locales use `dir="ltr"`.
- A Playwright locale suite covers all seven locale codes and asserts Arabic
  mission content is visible, not merely that the API responds.

## 2. E2E and browser verification

- Node E2E defaults now target the public CTC deployment. Local compose URLs
  remain available through explicit `E2E_BACKEND_URL` and `E2E_FRONTEND_URL`.
- Playwright defaults to `https://ctc-research.com` and does not start a local
  Astro server unless local E2E variables are supplied.
- The repository has no Selenium harness or Selenium dependency. Playwright is
  the maintained browser-equivalent check for this project; adding a second
  browser stack would duplicate coverage and package management.
- The existing node E2E contract covers health, page APIs, fragments, courses,
  public pages, and live course details.

## 3. Documentation consolidation

- Product-local docs moved under `projects/precis/docs/`:
  - `precis-main/`
  - `precis-landing/`
  - `precis-ctc/`
- The central index, relationship map, and duplicate register make source
  ownership explicit.
- Public reader-facing docs remain under the root `docs/` tree and link to the
  central project-local docs instead of duplicating implementation guides.

## 4. Validation record

| Check | Result |
|---|---|
| CTC API locale probe, seven locales | Passed |
| CTC public node E2E | Passed: 12/12 |
| Astro type/check diagnostics | Passed: 0 errors, 0 warnings, 0 hints |
| Playwright test discovery | Passed; locale suite included |
| Live CTC home/about/courses | HTTP 200 |

## Remarks & Notes

- API localization and browser-visible localization are separate contracts; both must be tested.
- A green API response does not prove that a static Astro page rendered the requested language.
- Browser tests require an installed Playwright browser. Selenium is intentionally not introduced because no Selenium suite exists in this project.
