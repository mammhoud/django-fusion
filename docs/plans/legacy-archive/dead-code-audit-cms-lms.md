# Dead Code & Unused Code Audit — cms-fusion / precis-lms

**Audit date:** July 31, 2026
**Scope:** `projects/cms-fusion/` and `projects/precis-lms/` (Django backends + Next.js/RTK Query frontends)
**Method:** automated scans (ruff F401/F841, vulture, repo typo/dead-code script) + cross-reference grep + git state review

---

## 1. Executive Summary

Both fusion projects carry a **large volume of "zombie" code** left over from the content-model refactor (legacy `apps/core/content/` → `apps/pages/` + `apps/content/`) and the duplicated shared-framework apps. Findings fall into four severity buckets:

| Bucket | Items | Risk | Action |
|--------|-------|------|--------|
| 🟥 **Blocking** | Domain `shared` migration broken (8 models indexed but never created); `load_course_fixtures` points at non-existent paths | High — fresh DB boot / `migrate` fails | Fix or delete |
| 🟧 **Duplicated** | ~20 management commands triplicated across `core/`, `handlers/`, `pages/accounts/`; legacy page models shadowed | Medium — silent divergence | Consolidate |
| 🟨 **Unused** | 314 unused imports, 38 unused vars, ~10 dead models, ~30 dead RTK hooks, 3 unused components | Low — noise/maintenance drag | Clean up |
| 🟦 **Refactor debris** | 668 uncommitted deleted files (old `apps/core/content`, `apps/core/domain`, `bolt_apis`, `data_adapter`) | Low — hygiene | Commit the deletion |

---

## 2. Blocking Issues (fix first)

### 2.1 Domain migrations target models that are never created

**Location:** `precis-lms/backend/apps/domain/migrations/0001_initial.py` (label `shared`) — same in cms-fusion.

**What's wrong:** The migration file **creates 13 models** (`CertificationTemplate`, `Contact`, `ContactEmail`, `ContactPhone`, `Corporate`, `Coupon`, `CouponUsage`, `EmailSettings`, `GlobalSettings`, `NewsletterSubscription`, `Organization`, `Service`, `TemplateVariable`) but then applies `AddIndex`/`AddConstraint`/`AddField` operations against **8 models that never get a `CreateModel`** in the file:

```
department, organization, person, service, team, teammembership, techbridges, workspace
```

Django's migration executor resolves each `model_name` in the app-state and raises `KeyError: ('shared', 'person')` for models that were never created — so **`manage.py migrate` / `makemigrations` fails outright** on a fresh database.

**Why it is unused/broken:** The `person`/`team`/`workspace`/`department`/`techbridges`/`teammembership` models were removed from the domain app during a prior refactor, but the hand-edited `0001_initial.py` was never regenerated. Tests only pass because `test settings` set `MIGRATION_MODULES` to bypass the real migrations.

**How to use it (fix):**
```bash
# 1. Regenerate a clean initial migration from the live domain models:
cd projects/precis-lms/backend
rm apps/domain/migrations/0001_initial.py
python manage.py makemigrations domain          # recreates only real models
python manage.py migrate domain
```
> ⚠️ Only safe if no production DB has applied the broken migration yet. If the broken `0001_initial` is already recorded as applied, generate a **new** migration (`0002`) that only contains the missing operations instead of rewriting `0001`.

**Enhancement possibilities:**
- Add a CI gate that runs `makemigrations --check --dry-run` so broken hand-edited migrations can never land again.
- Move the `shared` label to a proper app name (`domain`) or restore the `person`/`team` models if the workspace/team feature is still planned.

---

### 2.2 `load_course_fixtures` command references non-existent fixture paths

**Location:** `precis-lms/backend/apps/pages/lms/management/commands/load_course_fixtures.py` (same in cms-fusion).

**What's wrong:** The command calls `loaddata 'assets/fixtures/lms/specializations.json'`, `'assets/fixtures/lms/course_tags.json'`, `'assets/fixtures/lms/courses.json'` — but those directories/files **do not exist**. The real fixtures live at:

```
precis-lms/backend/apps/pages/lms/fixtures/{specializations,course_tags,courses,events}.json
precis-lms/backend/assets/fixtures/dump-data.json   # main site fixture
```

**Why it is unused:** Running the command prints success lines but silently loads nothing (Django ignores missing fixture paths), so it has no effect and nobody relies on it.

**How to use it (fix):**
```python
# In load_course_fixtures.py, point at the real paths (or use app-relative names):
call_command("loaddata", "specializations", verbosity=...)
call_command("loaddata", "course_tags", verbosity=...)
call_command("loaddata", "courses", verbosity=...)
```
Django resolves bare fixture names against every app's `fixtures/` dir, so dropping `assets/fixtures/lms/` makes them findable.

**Enhancement possibilities:**
- Merge this command into the canonical `load_data.py` / `load_fusion_fixtures.py` flow instead of maintaining a parallel loader.
- Add a `--dry-run` that verifies each fixture resolves to an existing file before attempting `loaddata`.

---

## 3. Duplicated / Shadowed Code

### 3.1 Management commands triplicated across three apps

Every one of these commands exists **3 times** — in `apps/core/management/commands/`, `apps/handlers/management/commands/`, **and** `apps/pages/accounts/management/commands/`:

```
send_bulk_emails.py   send_error_report.py   send_invites.py
send_test_email.py    test_email_csv.py      run_campaign_worker.py
verify_content.py     verify_deployment.py   validate_config.py
update_site_settings.py create_privacy_policies.py  create_groups_from_csv.py
populate_content.py
```

**Why they are unused:** Django discovers commands by app order in `INSTALLED_APPS`; the **first** app to provide a command name wins and the other two copies are silently shadowed. Since `apps.core` is listed before `apps.handlers` and `apps.pages.accounts`, only the `core/` copies are ever executed — the duplicates are dead weight that will diverge over time.

**How to use / fix:**
```bash
# Determine which copy is canonical (first app in INSTALLED_APPS wins):
cd projects/precis-lms/backend
python manage.py help | grep -E 'send_bulk_emails|verify_content|populate_content'
# Then delete the shadowed copies in handlers/ and pages/accounts/,
# keeping only the winning one (or move all to a single apps/shared app).
```

**Enhancement possibilities:**
- Move shared ops commands (email, validation, content) into a single `apps/operations` app with one copy each.
- Add a CI check that fails when a command name is duplicated across apps.

### 3.2 Legacy `apps/content/models/pages/*` page models (0 external references)

**Location:** `apps/content/models/pages/` — `base.py`, `home.py`, `about.py`, `contact.py`, `events.py`, `services.py`, `team.py`, `dynamic.py`.

Every model there reports **0 external references** outside `apps/content`:

```
AboutPage, BasePage, BaseFormPage, BaseIndexPage, ContactPage,
ContentPageMixin, DynamicHomePage, DynamicAboutPage, DynamicFaqPage,
DynamicPrivacyPage, DynamicContactPage, DynamicDashboardPage,
EventPage, HomePage, ServicesPage, TeamPage
```

**Why they are unused:** The Wagtail page models were migrated to `apps/pages/pages/models/` during the content refactor, but the old `apps/content/models/pages/` package was kept (and is still imported via `apps/content/models/__init__.py` → `from .pages import *`). Nothing instantiates or registers the legacy classes.

**How to use / fix:** Delete `apps/content/models/pages/` and the `from .pages import *` line in `apps/content/models/__init__.py`. Keep the **content** models below which are actively used (Course: 81 refs, BlogPost: 29, Feature: 29, Event: 21, Instructor: 17, TeamMember: 7, Publication: 7, CourseCategory: 4).

**Enhancement possibilities:** If any `Dynamic*` page behavior is still wanted, port the mixin into `apps/pages/pages/models/base.py` instead of keeping the dead copy.

### 3.3 Dead models inside otherwise-live apps (0 external references)

| Model | Location | Notes |
|-------|----------|-------|
| `ShopProduct` | `apps/content/models/lms.py` | 0 refs — superseded by `apps/pages/products` models |
| `PublicationCategory` | `apps/content/models/publication.py` | 0 refs (only FK targets) |
| `DataToken` | `apps/content/models/others.py` | 0 refs — `Token` is the used one (18 refs) |
| `ContactSubmission` | `apps/content/models/contact.py` | 0 refs — handled by `apps/pages`/forms now |
| `NewsletterSubscription` | `apps/content/models/base.py` | 0 refs |
| `CertificationTemplate` | `apps/domain/models/certification.py` | 0 refs |
| `EmailSettings` | `apps/domain/models/...` | 0 refs |
| `GlobalSettings` / `SiteSettings` | settings models | only referenced via settings proxies (2 refs) |

**Why unused:** leftover from the old monolithic `apps/content` design; the `apps/pages/*` apps now own these domains.

**How to use / fix:** Delete the classes and regenerate migrations for `apps/content` (`makemigrations content` after removal). For `CertificationTemplate`, keep if certification is a planned LMS feature — see §5 enhancements.

---

## 4. Frontend Dead Code (precis-lms frontend; cms-fusion frontend is a copy)

### 4.1 RTK Query hooks exported but never used by any component

The following hooks are declared in `frontend/src/store/api/endpoints/*.ts` but have **0 usages** across `.tsx`/`.ts` outside their own file:

| Endpoint file | Unused hooks |
|---------------|--------------|
| `announcements.ts` | `useGetAnnouncementQuery` |
| `assignments.ts` | `useGetAssignmentQuery` |
| `blog.ts` | `useGetBlogCategoriesQuery`, `useGetFeaturedPostsQuery`, `useGetRelatedPostsQuery` ⚠️ (`useGetBlogPostsQuery` unused too — the blog page uses raw `fetch` instead) |
| `contact.ts` | `useGetInquiriesQuery`, `useMarkInquiryReadMutation` |
| `courses.ts` | `useDeleteCourseMutation`, `useGetCategoriesQuery`, `useGetFeaturedCoursesQuery` |
| `events.ts` | `useGetEventQuery`, `useGetUpcomingEventsQuery`, `useRegisterForEventMutation` |
| `instructors.ts` | `useGetInstructorReviewsQuery`, `useUpdateInstructorProfileMutation` |
| `notifications.ts` | `useDismissNotificationMutation` |
| `pages.ts` | `useGetPageQuery`, `useGetPageFragmentQuery`, `useGetPageHtmlQuery` |
| `shop.ts` | `useAddToCartMutation`, `useGetOrdersQuery` |
| `students.ts` | `useGetEnrollmentProgressQuery`, `useGetStudentQuery`, `useGetStudentsQuery`, `useUpdateProgressMutation` |
| `withdrawals.ts` | `useGetWithdrawalQuery` |
| `auth.ts` | `useChangePasswordMutation`, `useLogoutMutation`, `useRefreshTokenMutation`, `useResetPasswordMutation` |

**Why they are unused:** Many pages were built with mock data or raw `fetch` (e.g. `app/blog/page.tsx` calls `/api/blog?...` directly), so the RTK Query layer for those features was never wired up. Others (logout/refresh/reset-password) are handled by middleware or inline logic.

**How to use / fix:** Either (a) delete the unused exports, or (b) wire them into the pages that currently use raw `fetch` — prefer (b) for `blog`, `shop`, `auth` since the backend endpoints already exist and return the matching shapes.

**Enhancement possibilities:**
- Add a `ts-unused-exports` / eslint `no-unused-vars` gate on `src/store/api/endpoints/` so dead hooks are caught in CI.
- Migrate the raw-`fetch` pages (`blog`, `events` list) to the RTK hooks so caching/invalidation + the already-built API get exercised.

### 4.2 Unused components

| Component | Notes |
|-----------|-------|
| `FusionLayout.tsx` | 0 imports — server layout is used instead |
| `NotificationBell.tsx` | 0 imports — notifications rendered inline in dashboard |
| `PageNavigation.tsx` | 0 imports — pagination handled per-page |

**How to use / fix:** Delete, or use `NotificationBell` in the shared header/dashboard top bar where unread-count already exists (`useGetUnreadCountQuery` is used).

### 4.3 Frontend/backend API surface mismatch (summary)

Used hooks reference ~20 backend endpoint groups. The unused hooks above imply **~30 backend endpoints are callable but have no consumer** (e.g. `/api/withdrawals/`, `/api/announcements/`, quiz CRUD beyond the pages that exist). Confirm each against the running app before removing backend views.

---

## 5. Enhancement Opportunities (turn dead code into features)

1. **Workspace/Team/Person domain (blocked by §2.1)** — the 8 uncreated models suggest a planned multi-tenant/team feature that was cut mid-refactor. If the roadmap includes instructor/team collaboration, restore those models in `apps/domain` and rebuild `0001_initial.py` around them — this turns the migration blocker into the foundation of the feature.

2. **Certification engine** — `CertificationTemplate` (dead) + `apps/handlers/services/certificates.py` (live) are almost a certificate generator. Wire a template → certificate flow with Wagtail snippets and generate PDFs on course completion.

3. **Shop/product layer** — `ShopProduct`, cart, and orders endpoints exist (some unused). The `cart`/`shop` pages work on `apps/pages/products`; unify `ShopProduct` into that app or delete it, then enable the `useGetOrdersQuery`/`useAddToCartMutation` flows for order history in `student-dashboard`.

4. **Email ops consolidation** — the 3×-duplicated `send_*`/`test_email_csv`/`run_campaign_worker` commands are a ready-made email automation suite. Consolidate into `apps/operations` and add a cron target for campaign workers + error reports.

5. **RTK Query cleanup + adoption** — delete unused hooks OR wire blog/shop/auth pages to them; add CI `ts-unused-exports`. Expected result: the `/api/blog`, `/api/shop` endpoints gain real consumers and the dead code count drops ~30%.

---

## 6. Cleanup Playbook (ordered by risk)

```bash
# 0. Commit the refactor deletions (668 files already deleted in working tree):
cd projects && git add -A cms-fusion/backend precis-lms/backend && git commit -m "refactor: commit content/domain model refactor deletions"

# 1. Fix the blocking migration (fresh-DB safe path):
cd precis-lms/backend
rm apps/domain/migrations/0001_initial.py
python manage.py makemigrations domain && python manage.py migrate
# repeat for cms-fusion/backend

# 2. Fix load_course_fixtures paths (see §2.2)

# 3. Auto-clean unused imports/vars:
cd projects && uv run ruff check cms-fusion/backend/apps precis-lms/backend/apps \
  --select F401,F841 --fix && uv run ruff format

# 4. Delete dead models + legacy pages package (see §3.2/3.3), then makemigrations

# 5. Deduplicate management commands (keep the core/ copy; delete handlers/ + pages/accounts/ copies)

# 6. Frontend: delete unused hooks/components OR wire them (see §4), add ts-unused-exports

# 7. Validate:
cd projects && uv run python -m pytest precis-lms/backend/tests/ cms-fusion/backend/tests/ -q
cd precis-lms/frontend && npx tsc --noEmit && npx vitest run
cd projects && make check WEBSITE=lms && make check WEBSITE=precis-ctc
```

---

## 7. Raw Scan Numbers (evidence)

| Scan | Result |
|------|--------|
| Repo typo/dead-code script | Clean (no `TODO: remove` / typos in fusion projects) |
| `ruff --select F401,F841` (both backends) | **314 unused imports, 38 unused variables, 10 invalid-syntax files** |
| `vulture` on both apps trees | no output beyond ruff findings (not installed) |
| Uncommitted deleted files | **668** (mostly `apps/core/content`, `apps/core/domain`, `bolt_apis.py`, `data_adapter.py`) |
| Duplicated management commands | **20 command names × 3 apps** |
| Backend models with 0 external refs | **10+** (ShopProduct, PublicationCategory, DataToken, ContactSubmission, NewsletterSubscription, CertificationTemplate, EmailSettings, legacy pages/*) |
| Frontend unused RTK hooks | **~30** |
| Frontend unused components | **3** (FusionLayout, NotificationBell, PageNavigation) |

---

## 8. Recommended Priorities

1. 🟥 **Fix domain migration** (§2.1) — unblocks `migrate` for dev/prod/CI.
2. 🟥 **Fix `load_course_fixtures` paths** (§2.2) — one-line, makes fixture docs truthful.
3. 🟧 **Commit the 668-file refactor deletion** — removes "deleted-but-uncommitted" ambiguity from every future `git status`.
4. 🟨 **Ruff auto-fix F401/F841** — 352 mechanical cleanups, zero behavior change.
5. 🟨 **Delete the 10 dead models + legacy `pages/` package** — small migrations, big clarity.
6. 🟦 **Frontend dead-hook/component cleanup** — wire or delete §4 items.
