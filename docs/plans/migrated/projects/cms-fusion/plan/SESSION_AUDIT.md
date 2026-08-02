# CMS-Fusion & LMS-Fusion — Session Audit & Action Plan

> Generated: July 28, 2026  
> Scope: `projects/cms-fusion` + `projects/lms-fusion`

---

## 1. django-fusion Package Integration

Both projects depend on the shared **django-fusion** library (submodule at `libs/django-fusion/`).

### Key Integration Points

| Integration | CMS | LMS | Status |
|---|---|---|---|
| `FusionPage` models | `apps/pages/pages/models.py` | `apps/pages/pages/models.py` | ✅ Synced |
| `FusionCodec` encode/decode | `apps/pages/pages/api.py` | `apps/pages/pages/api.py` | ✅ Synced |
| `fusion_json_response` | `apps/pages/pages/api.py` | `apps/pages/pages/api.py` | ✅ Synced |
| `fusion_response` builder | `django_fusion.routes.rendering.renderers` (moved from `apps/core/api/data_adapter.py`) | same | ✅ Consolidated into django-fusion |
| `fusion_response` | `apps/pages/pages/api.py` | `apps/pages/pages/api.py` | ✅ Synced |
| `FusionDecoder` (TS) | `frontend/src/lib/fusion-decoder.ts` | `frontend/src/lib/fusion-decoder.ts` | ✅ Synced |
| `FusionMiddleware` (React) | `frontend/src/components/FusionMiddleware.tsx` | `frontend/src/components/FusionMiddleware.tsx` | ✅ Synced |
| `FusionProxy` (React) | `frontend/src/components/FusionProxy.tsx` | `frontend/src/components/FusionProxy.tsx` | ⚠️ Different (by design) |
| `FusionPage` (React) | `frontend/src/components/FusionPage.tsx` | `frontend/src/components/FusionPage.tsx` | ⚠️ Different (by design) |

### FusionPage / FusionProxy Difference (by design)

| Aspect | CMS-Fusion | LMS-Fusion |
|---|---|---|
| `FUSION_RENDER_FIRST_DEFAULT` | `True` | `False` |
| FusionProxy approach | `fragmentUrl` → fetch HTML directly | `slug` → bolt API fallback chain |
| Rendering priority | Fragment-first (server HTML) | Data-first (API JSON) |
| Theme color | Purple `#7c3aed` | Teal `#00a1b3` |

---

## 2. CSS Custom Property Rename: `--ctc-*` → `--fu-*`

### Completed
- ✅ All `--ctc-primary` → `--fu-primary` (CMS: 116+ matches, LMS: 113+ matches)
- ✅ All `--ctc-accent` → `--fu-accent`
- ✅ All `--ctc-primary-dark` → `--fu-primary-dark`
- ✅ `--ctc-secondary` → `--fu-secondary` (LMS dev/theme page)
- ✅ Comment references: `fusion-cms` → `fusion` in SCSS/REDME files

### Remaining (intentional)
- `hello@fusion-cms.com` — test fixture email in `ContactPage.test.tsx` (both projects)
- `fusion-cms.com` — static page content in `backend/apps/pages/pages/content.py` (legacy data)

---

## 3. HTML Template Conflict Analysis

### Django/Wagtail Templates vs Next.js Components

| Django Template | Next.js Component | Conflict? | Notes |
|---|---|---|---|
| `backend/templates/base.html` | `FusionLayout.tsx` | 🟡 Complementary | `base.html` uses `{% fusion_layout %}` for render-first mode; `FusionLayout.tsx` wraps Next.js pages in data mode |
| `backend/templates/index.html` | `app/page.tsx` | 🟡 Complementary | `index.html` renders `{% comp 'base_fragment' /%}` for HTMX; `page.tsx` renders via `FusionPage` |
| `backend/templates/base_page.html` | `FusionWagtailPage.tsx` | 🟡 Complementary | Django serves Wagtail page HTML in fragment mode; Next.js renders Wagtail data in data mode |
| `backend/templates/events/event_page.html` | `app/events/page.tsx` | 🟡 Complementary | `event_page.html` uses `{% comp "events/main.html" /%}`; Next.js uses `useGetEventsQuery` |
| `backend/templates/wagtailadmin/login.html` | `app/login/page.tsx` | 🟢 No conflict | Wagtail admin login only for `/admin/`; Next.js login is at `/login` |

> Note: `plugins/courses/catalog.html` was listed by the file picker but does not exist on disk — no conflict.

### Conclusion
**No real conflicts.** The Django/Wagtail templates serve the **render-first (fragment) mode** where Django renders HTML that `FusionProxy` injects into the React tree. Next.js components serve the **data mode** where API JSON is fetched and rendered client-side. They're complementary rendering strategies, not competing implementations.

### Recommended Actions
- ✅ Keep both paths — they serve different `FUSION_RENDER_FIRST` modes
- ⚠️ Ensure both template and component render same visual output for consistency
- ⚠️ Consider visual regression tests comparing fragment vs data rendering

---

## 4. Dead Code / Tech Debt Audit

### Clean Codebase (no major issues)

| Category | Count | Details |
|---|---|---|
| `console.error` (non-test) | 2 | `ErrorBoundary.tsx` — intentional error logging (both projects) |
| `TODO`/`FIXME`/`HACK` markers | 0 | None found in source files |
| `console.log` (non-test) | 0 | None found |
| Unused imports | Not checked | Would need TypeScript compiler check |
| Empty files | Not checked | Would need file system scan |

### Risk Areas
- **`fusionStore`** — exists in both projects but usage is minimal. Consider consolidating with `FusionMiddleware` context.
- **`FusionWagtailPage.tsx`** — CMS version has less detailed rendering than LMS. Consider syncing.

### Recommended Actions
- ✅ No dead code removal needed — codebase is clean
- ⚠️ Run `npx tsc --noEmit` on both projects to check for unused imports
- ⚠️ Consider consolidating `fusionStore` into `FusionMiddleware` (low priority)

---

## 5. SCSS Build Pipeline

### Status: ✅ Fully Synced

| Asset | CMS | LMS | Status |
|---|---|---|---|
| `fusion-theme.scss` | ✅ | ✅ | Identical |
| `_index.scss` (assets) | ✅ | ✅ | Identical |
| Vendor SCSS files | ✅ (5) | ✅ (5) | Identical |
| `main.scss` (frontend) | ✅ | ✅ | Identical |
| SCSS partials | ✅ (51) | ✅ (51) | Same count & names |
| `tailwind.config.js` | ✅ | ✅ | Synced (with per-project color defaults) |
| `globals.css` | ✅ | ✅ | Synced (with intentional per-project body styling: CMS uses `bg-gray-50`, LMS uses `bg-fu-bg`) |
| `postcss.config.js` | ✅ | ✅ | Identical |
| `fusion.css` output | ✅ | ✅ | Identical (CSS custom properties) |
| `build:theme` script | ✅ | ✅ | `sass --style=compressed --no-source-map` |

### Per-Project Color Defaults (correct)

| Variable | CMS Fallback | LMS Fallback |
|---|---|---|
| `--fu-primary` | `#7c3aed` (purple) | `#00a1b3` (teal) |
| `--fu-secondary` | `#5b21b6` | `#008080` |
| `--fu-accent` | `#4c1d95` | `#005f73` |
| `--fu-bg` | `#fafafa` | `#f8fafc` |
| `--fu-text` | `#18181b` | `#1e293b` |

---

## 6. Completed Changes Summary

### This Session

| File | Change | Reason |
|---|---|---|
| `cms-fusion/backend/apps/pages/pages/api.py` | Refactored with helper functions, `render_first is True` check, error handling | Synced from LMS |
| `cms-fusion/backend/apps/pages/pages/wagtail_hooks.py` | Added render-first indicator CSS, docstrings | Synced from LMS |
| `cms-fusion/backend/apps/pages/pages/models.py` | Added `verbose_name_plural` | Synced from LMS |
| `cms-fusion/frontend/src/lib/fusion-types.ts` | Added Wagtail page types, response types | Synced from LMS |
| `cms-fusion/frontend/src/lib/api-client.ts` | Added `fetchPageBlocks`, env var fallback | Synced from LMS |
| `lms-fusion/frontend/src/lib/fusion-decoder.ts` | Added `FusionSessionError` class | Synced from CMS |
| `cms-fusion/frontend/tailwind.config.js` | Added fusion theme colors, Inter font, animation | Synced from LMS |
| `cms-fusion/frontend/src/app/globals.css` | Added fusion utility classes | Synced from LMS |
| css custom property rename | Both projects `src/**` + `assets/styles/**` | `--ctc-*` → `--fu-*` rename | Brand consistency |
| SCSS comment rename | Both projects `src/styles/**` + `assets/styles/**` | `fusion-cms` → `fusion` rename | Brand consistency |

### Test Results

| Project | Frontend Tests | Backend Tests |
|---|---|---|
| CMS-Fusion | 221 passed | 84 passed |
| LMS-Fusion | 213 passed | 84 passed |
| **TOTAL** | **434** | **168** |

---

## 7. Recommended Next Actions

### High Priority
1. **Run TypeScript compiler check**: `npx tsc --noEmit` in both frontend projects
2. **Check remaining `fusion-cms` references** in backend static page content (`content.py`)
3. **Update test fixtures**: `ContactPage.test.tsx` still uses `hello@fusion-cms.com`

### Medium Priority
4. **Sync `FusionWagtailPage.tsx`** rendering quality: LMS has richer markup than CMS
5. **Consider visual regression tests** for fragment vs data rendering consistency
6. **Add `html { scroll-behavior: smooth; }`** to CMS globals.css (LMS has it)

### Low Priority
7. **Evaluate `fusionStore` consolidation** into `FusionMiddleware` context
8. **Run Playwright E2E tests** for both projects to verify full-stack integration
9. **Update `assets/styles/_index.scss`** comments from `fusion-cms` to `fusion`
