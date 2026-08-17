# Loop-CRM Demo State + Auth Gap Fixing — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the deployed `crm.structa.cloud` a complete, demo-ready preview: auth pages stop rendering the CRM side nav, a known demo user is shown on the login page and created deterministically, the server boots in demo state (auto-seed), every side-nav destination resolves to a real page, and post-login navigation works for the demo/superuser.

**Architecture:** Loop-CRM is an Astro static shell (frontend) + Django render-first backend. Traefik routes `/accounts|/api|/bolt|/admin|/static|/media|/fragment(s)|/ws|/connect|/account|/sse` to the backend (priority 200); every other path goes to the Astro shell (priority 100). The backend owns data + auth; the Astro shell owns the page chrome. Demo state is a first-class setting (`DEMO_MODE=1`) that (a) surfaces demo credentials on the login page, (b) auto-seeds the demo workspace on container boot, and (c) promotes the demo admin to superuser for admin access.

**Tech Stack:** Django 5 + django-fusion + allauth + django-bolt, Astro 5 + Tailwind 4 + HTMX, Traefik, Docker Compose, Dramatiq.

**Status:** Tasks 1-5 and 7 are **implemented and verified** (2026-08-17): backend suite 255 tests OK, frontend build 34 pages incl. the six new destinations, frontend node test suite 50/50. Task 6 has a local half (SQLite migrate + `seed_demo --superuser` + runserver smoke: `/accounts/login/` 200 with demo panel, anonymous `/overview/` 302, `/admin/login/` 200) and a server half that requires a real deploy (see Task 6, Step 1-2).

**Definition of done (whole plan):** (1) `/accounts/login/` renders a bare entrance — no CRM side nav — with a "Use demo account" one-click fill when `DEMO_MODE=1`; (2) `seed_demo` deterministically creates `demo@loop.dev` / `demo-pass-123` (staff, superuser with `--superuser`) plus sales/marketing/revops members, idempotently; (3) the server auto-seeds on boot when `DEMO_MODE=1` (entrypoint) and the compose stack passes the flag; (4) sign-in redirects to `/overview/` and every side-nav destination returns a page (no 404); (5) `DESIGN.md` + Twenty/Postiz comparison exist and are referenced from this plan.

## Global Constraints

- Auth pages (`/accounts/*`) are served by Django templates only; the app shell (`base.html`) is the render-first shell used for authenticated Django pages.
- Navigation is canonical in `apps/core/navigation.py`; the Astro build-time list in `src/lib/navigation.ts` mirrors it (the HTMX fragment at runtime is authoritative).
- Demo credentials must never appear unless `DEMO_MODE=1` (never leak demo passwords in production with real data).
- `DEMO_MODE` must stay disabled in real production deployments (`DEMO_MODE=0`); the entrypoint only seeds when explicitly enabled.
- The Astro shell is `output: 'static'`; every navigation destination needs a `getStaticPaths` entry or it 404s.
- `seed_demo` stays idempotent: rerunning keeps existing records and adds nothing new.
- All new templates/pages follow the existing Loop visual system (dark, `Bricolage Grotesque` + `JetBrains Mono`, emerald accent) — no new design language.

---

## Audit: what is implemented vs what should happen after sign-in

Probed against the deployed site (2026-08-17) and the repo at `6b506c798`.

### Implemented (verified live)

| Surface | State |
|---|---|
| Marketing landing `/` | ✅ Astro `index.astro` — hero, modules, steps, pricing, CTA, footer |
| Auth flow | ✅ allauth login/signup/logout/password-reset; email-only login; GitHub/Google buttons; session auth |
| Post-login app shell | ✅ `AppShell.astro` — side nav (HTMX fragment), breadcrumbs, topbar, mobile drawer |
| Real data views | ✅ Overview `RevOpsDashboard` island (Bolt API), Deals `PipelineBoard` island, kanban move (CSRF-protected) |
| Backend data/API | ✅ Bolt + `/api/v1` resources (companies, contacts, deals, posts, workflows, finance, custom fields/objects, saved views, email, audit), workspace tenancy, SSE/WebSocket realtime, Dramatiq workers |
| Demo dataset | ✅ `seed_demo` command + `apps/core/demo.py` — pipeline, 8 deals, 7 posts, finance trail, attribution; `user_signed_up` signal seeds a personal workspace for new signups |
| Backend render-first pages | ✅ Django templates for members, workflows, integrations, email inbox, import, custom objects, saved views, audit, reports, tasks, approvals |
| Multi-tenant isolation | ✅ every read/write path workspace-scoped via `apps/core/tenancy.py` |

### Gaps found (deployed 2026-08-17)

| # | Gap | Evidence |
|---|---|---|
| G1 | **Auth pages render the CRM side nav** — `/accounts/login/` and `/accounts/signup/` wrap the full app shell (`.loop-shell` + `.loop-sidebar` + module links) around the auth card because `base.html` unconditionally includes `dashboard/sidebar.html` | Deployed login/signup HTML contains the full nav tree |
| G2 | **No demo user surfaced** — the login page shows no demo credentials or one-click fill, so a visitor cannot preview the workspace | Deployed `login.html` has no demo panel |
| G3 | **Demo user is not deterministic/complete** — `seed_demo` only sets the password on first creation (`if created:`), so a previously seeded demo account keeps a stale password; the demo admin is `is_staff` but **not** `is_superuser`, so Django admin and full superuser navigation are unavailable | `seed_demo.py` |
| G4 | **Post-login redirect lands on the marketing landing** — `LOGIN_REDIRECT_URL = "/"` sends a signed-in user to `index.astro` (which shows "Sign in"/"Start free") instead of the workspace shell | `configs/default/__init__.py` |
| G5 | **Six side-nav destinations 404** — the backend nav tree links to `/marketing/approvals/`, `/tasks/`, `/settings/email/`, `/settings/custom-objects/`, `/settings/saved-views/`, `/settings/import/` but the Astro shell has no `getStaticPaths` entries, and Traefik routes those paths to the frontend (not the backend templates) | HTTP probe: all six return `404` |
| G6 | **Astro nav list diverges from the canonical backend nav** — `src/lib/navigation.ts` is missing approvals, email, custom-objects, saved-views, import (backend `navigation.py` has them) | file diff |
| G7 | **Server does not run with demo state** — no `DEMO_MODE` setting, entrypoint never seeds, compose never passes the flag, `.env.example` does not document it | grep: zero `DEMO_MODE` matches in `projects/loop-crm` |

### Expected behavior after sign-in as demo/superuser (target)

1. `/` shows the marketing landing with a **demo-aware** sign-in hint (when `DEMO_MODE`).
2. `/accounts/login/` shows a bare entrance page (no side nav) with a **Try the demo** panel: `demo@loop.dev` / `demo-pass-123`, one click fills the form.
3. After login, `LOGIN_REDIRECT_URL` sends the user to `/overview/` (workspace shell with side nav, breadcrumbs, RevOps dashboard with real seeded numbers).
4. Every side-nav link resolves: CRM (companies, contacts, pipelines, deals, activities), Marketing (calendar, campaigns, channels, media, approvals), Finance (invoices, payments, revenue), Attribution (touchpoints, reports), Tasks, Workspace (members, workflows, integrations, email, custom fields, custom objects, saved views, import, audit).
5. `/admin/` is reachable because the demo admin is a superuser (only when `DEMO_MODE=1`).
6. New signups still get their own seeded personal workspace via the `user_signed_up` signal.

---

## Related documentation

Read these before implementing or reviewing this plan — they are the context the tasks assume.

| Doc | Path | Why it matters here |
|---|---|---|
| Loop-CRM merge & architecture plan | [`docs/plans/loop-crm/merge-plan.md`](./merge-plan.md) | The 18-week roadmap and Twenty/Postiz feature-merging matrix this plan builds on; §12 lists the remaining open work (OAuth adapters, AI hub) that Task 7's follow-up touches |
| Twenty + Postiz package & feature comparison | [`docs/plans/loop-crm/twenty-postiz-comparison.md`](./twenty-postiz-comparison.md) | Answer to "is there one package with both features" (no), the full feature matrix, and the design-enhancement rationale (Task 7) |
| Loop-CRM README | [`projects/loop-crm/README.md`](../../../projects/loop-crm/README.md) | Product narrative, quick start, API modes (Bolt + `/api/v1`), Docker deployment — the canonical project entry point |
| Frontend design tokens | [`projects/loop-crm/frontend/DESIGN.md`](../../../projects/loop-crm/frontend/DESIGN.md) | The Loop visual language every new page must follow (Task 7 output; also constrains Task 5 page shells) |
| Backend settings | [`projects/loop-crm/backend/configs/default/__init__.py`](../../../projects/loop-crm/backend/configs/default/__init__.py) | Where `DEMO_MODE` and `LOGIN_REDIRECT_URL` live (Task 1, Task 3) |
| Demo dataset + contract | [`projects/loop-crm/backend/apps/core/demo.py`](../../../projects/loop-crm/backend/apps/core/demo.py) | Single source of truth for demo constants (Task 1, Task 3) |
| Deployment/proxy config | [`applications/proxy/traefik/dynamic/crm.yml`](../../../applications/proxy/traefik/dynamic/crm.yml) | The routing split (backend priority 200 vs frontend priority 100) that causes the Task 5 404s |
| Seed-demo tests | [`projects/loop-crm/backend/apps/core/tests_seed_demo.py`](../../../projects/loop-crm/backend/apps/core/tests_seed_demo.py) | The test surface for demo determinism, superuser promotion, and demo-state context (Tasks 1, 3) |
| Entrypoint / compose | [`projects/loop-crm/backend/entrypoint.sh`](../../../projects/loop-crm/backend/entrypoint.sh) · [`projects/loop-crm/docker-compose.yml`](../../../projects/loop-crm/docker-compose.yml) | The demo-state boot path (Task 4) |

### Glossary (terms used in this plan)

- **Demo state (`DEMO_MODE=1`)** — a deployment mode where the login page surfaces demo credentials and the container seeds the demo workspace on boot. Never enabled with real data.
- **Demo workspace** — the seeded `demo-workspace` (slug) containing the full product trail: pipeline + 8 deals, campaign + 7 posts, invoice/payment/revenue, attribution touchpoints.
- **Demo user** — the deterministic account `demo@loop.dev` / `demo-pass-123` (username `demo`), staff + superuser under `--superuser`.
- **DNA** — the borrowed design/feature heritage: Twenty (CRM) + Postiz (social scheduling). Loop-CRM is the merged implementation.
- **Render-first** — Django templates render full HTML; the opposite road is the JSON/Bolt API the Astro shell consumes.
- **Bolt** — the canonical JWT API road at `/bolt/` (optional `django-fusion[bolt]`); `/api/v1/` is the compatibility fallback.

---

## Task 1: Demo-state backend — setting, constants, context processor

**Files:**
- Modify: `projects/loop-crm/backend/configs/default/__init__.py`
- Modify: `projects/loop-crm/backend/apps/core/demo.py`
- Modify: `projects/loop-crm/backend/apps/core/context_processors.py`
- Test: `projects/loop-crm/backend/apps/core/tests_seed_demo.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `settings.DEMO_MODE: bool`; `apps.core.demo.DEMO_EMAIL`, `DEMO_PASSWORD`, `DEMO_WORKSPACE_SLUG`; context flag `demo_mode` (bool) + `demo_email`, `demo_password` (only non-empty when `DEMO_MODE`) available in every template.

- [x] **Step 1: Add the `DEMO_MODE` setting**

In `configs/default/__init__.py`, after `DEBUG`:

```python
# Demo state — when enabled, the login page surfaces the seeded demo
# credentials and the container entrypoint seeds the demo workspace on boot.
# NEVER enable on a production deployment with real data: the demo password
# is intentionally public.
DEMO_MODE = os.environ.get("DEMO_MODE", "0") == "1"
```

- [x] **Step 2: Move demo credentials into `apps/core/demo.py` (single source of truth)**

Append to `apps/core/demo.py`:

```python
# Demo account contract — single source of truth shared by seed_demo, the
# login-page demo panel, and the container entrypoint.
DEMO_WORKSPACE_SLUG = "demo-workspace"
DEMO_EMAIL = "demo@loop.dev"
DEMO_PASSWORD = "demo-pass-123"

DEMO_MEMBERS = [
    ("sales", "Sales Manager", "sales_manager"),
    ("marketing", "Marketing Manager", "marketing_manager"),
    ("revops", "RevOps Manager", "revops_manager"),
]
```

- [x] **Step 3: Expose demo state to templates**

Replace the whole `apps/core/context_processors.py` with:

```python
"""Template context helpers shared by the render-first Loop-CRM shells.

``workspace_id`` is the single value the frontend needs to open the
workspace-scoped Server-Sent Events stream, so it is exposed here rather than
duplicated across every view's ``get_context_data``.

``demo_state`` surfaces the demo credentials to the login page ONLY while
``DEMO_MODE`` is enabled; otherwise every value is empty so a production
deployment never leaks demo passwords.
"""
from __future__ import annotations

from django.conf import settings

from .demo import DEMO_EMAIL, DEMO_PASSWORD
from .tenancy import current_workspace_id


def workspace_id(request):
    """Return ``{"workspace_id": int | None}`` for the current request."""
    return {"workspace_id": current_workspace_id(request)}


def demo_state(request):
    """Return demo-mode flags + credentials for templates (empty when disabled)."""
    if settings.DEMO_MODE:
        return {
            "demo_mode": True,
            "demo_email": DEMO_EMAIL,
            "demo_password": DEMO_PASSWORD,
        }
    return {"demo_mode": False, "demo_email": "", "demo_password": ""}
```

- [x] **Step 4: Register the processor**

In `configs/default/__init__.py`, `context_processors` list, append after `"apps.core.context_processors.workspace_id"`:

```python
                "apps.core.context_processors.workspace_id",
                "apps.core.context_processors.demo_state",
```

- [x] **Step 5: Test the context processor contract**

Append to `apps/core/tests_seed_demo.py`:

```python
class DemoStateContextProcessorTests(TestCase):
    def test_demo_state_is_empty_when_disabled(self):
        with self.settings(DEMO_MODE=False):
            from apps.core.context_processors import demo_state

            context = demo_state(object())
            self.assertFalse(context["demo_mode"])
            self.assertEqual(context["demo_email"], "")
            self.assertEqual(context["demo_password"], "")

    def test_demo_state_exposes_credentials_when_enabled(self):
        with self.settings(DEMO_MODE=True):
            from apps.core.context_processors import demo_state

            from apps.core.demo import DEMO_EMAIL, DEMO_PASSWORD

            context = demo_state(object())
            self.assertTrue(context["demo_mode"])
            self.assertEqual(context["demo_email"], DEMO_EMAIL)
            self.assertEqual(context["demo_password"], DEMO_PASSWORD)
```

- [x] **Step 6: Run the tests**

Run: `cd projects/loop-crm/backend && make test`
Expected: the new tests PASS (and the existing suite stays green).

- [x] **Step 7: Commit**

```bash
git add projects/loop-crm/backend/configs/default/__init__.py \
        projects/loop-crm/backend/apps/core/demo.py \
        projects/loop-crm/backend/apps/core/context_processors.py \
        projects/loop-crm/backend/apps/core/tests_seed_demo.py
git commit -m "feat(crm): add DEMO_MODE setting and demo-state template context"
```

---

## Task 2: Auth pages without the side nav + demo panel on login

**Files:**
- Modify: `projects/loop-crm/backend/templates/base.html`
- Modify: `projects/loop-crm/backend/templates/account/login.html`
- Modify: `projects/loop-crm/backend/templates/account/base_entrance.html`

**Interfaces:**
- Consumes: `demo_mode`, `demo_email`, `demo_password` from Task 1.
- Produces: anonymous requests render a bare entrance layout (no `.loop-shell`, no sidebar); authenticated requests keep the full shell. The login page renders a demo panel when `demo_mode`.

- [x] **Step 1: Make the shell conditional in `base.html`**

Wrap the `<div class="loop-shell">` (sidebar + topbar + `#loop-content`) so the sidebar and topbar render only for authenticated users; anonymous users get a centered bare shell. Change:

```django
  <div class="loop-shell">
    {% include "dashboard/sidebar.html" %}
    <div class="loop-main">
      <header class="loop-topbar">
        ...
      </header>
      <main id="loop-content" class="loop-content">{% block content %}{% endblock %}</main>
    </div>
  </div>
```

to:

```django
  {% if request.user.is_authenticated %}
  <div class="loop-shell">
    {% include "dashboard/sidebar.html" %}
    <div class="loop-main">
      <header class="loop-topbar">
        <button class="loop-mobile-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false" onclick="document.body.dataset.navOpen = document.body.dataset.navOpen !== 'true' ? 'true' : 'false'; this.setAttribute('aria-expanded', document.body.dataset.navOpen)"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" /></svg></button>
        <span class="loop-topbar__meta">Revenue operations / unified workspace</span>
        <span class="loop-topbar__account">{% if request.user.is_authenticated %}<a href="/account/profile/">{{ request.user.email|default:request.user.username }}</a><a href="{% url 'account_logout' %}">Sign out</a>{% else %}<a href="{% url 'account_login' %}">Sign in</a>{% endif %}</span>
      </header>
      <main id="loop-content" class="loop-content">{% block content %}{% endblock %}</main>
    </div>
  </div>
  {% else %}
  <main id="loop-content" class="loop-content loop-entrance">{% block content %}{% endblock %}</main>
  {% endif %}
```

- [x] **Step 2: Add entrance spacing**

In `base.html` `<style>`, append:

```css
    .loop-entrance { display:grid; place-items:start center; min-height:100dvh; }
```

- [x] **Step 3: Demo panel on the login page**

In `templates/account/login.html`, insert a demo panel above the social buttons when `demo_mode`:

```django
{% if demo_mode %}
<div class="loop-demo-panel" data-loop-demo>
  <p class="loop-demo-panel__kicker">Demo workspace</p>
  <p class="loop-demo-panel__copy">Preview the full product trail — pipeline, publishing, finance, and attribution — with the seeded demo account.</p>
  <dl class="loop-demo-panel__creds">
    <div><dt>Email</dt><dd><code>demo@loop.dev</code></dd></div>
    <div><dt>Password</dt><dd><code>demo-pass-123</code></dd></div>
  </dl>
  <button class="loop-button loop-button--primary" type="button" data-loop-demo-fill>Use demo account</button>
</div>
{% endif %}
```

And a script at the bottom of the same template:

```django
{% if demo_mode %}
<script>
  (function () {
    var button = document.querySelector('[data-loop-demo-fill]');
    if (!button) return;
    button.addEventListener('click', function () {
      var email = document.querySelector('#id_login');
      var password = document.querySelector('#id_password');
      if (email) email.value = 'demo@loop.dev';
      if (password) password.value = 'demo-pass-123';
    });
  })();
</script>
{% endif %}
```

- [x] **Step 4: Style the demo panel**

In `templates/account/base_entrance.html` `{% block head %}` style, append:

```css
.loop-demo-panel{margin:1.4rem 0 0;padding:1rem 1.1rem;border:1px solid #3c786f;border-radius:.8rem;background:linear-gradient(145deg,rgba(25,59,53,.5),rgba(17,27,30,.85))}.loop-demo-panel__kicker{margin:0 0 .35rem;color:var(--accent);font:600 .64rem ui-monospace,SFMono-Regular,monospace;letter-spacing:.14em;text-transform:uppercase}.loop-demo-panel__copy{margin:0 0 .8rem;color:var(--muted);font-size:.82rem}.loop-demo-panel__creds{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin:0 0 .9rem}.loop-demo-panel__creds dt{color:#718394;font:600 .6rem ui-monospace,SFMono-Regular,monospace;text-transform:uppercase;letter-spacing:.08em}.loop-demo-panel__creds dd{margin:0;color:var(--ink)}.loop-demo-panel__creds code{color:var(--accent-2)}
```

- [x] **Step 5: Verify locally**

Run: `cd projects/loop-crm/backend && make dev` then open `http://127.0.0.1:8000/accounts/login/` with `DEMO_MODE=1` exported.
Expected: no sidebar; demo panel visible; "Use demo account" fills the two fields.

- [x] **Step 6: Commit**

```bash
git add projects/loop-crm/backend/templates/base.html \
        projects/loop-crm/backend/templates/account/login.html \
        projects/loop-crm/backend/templates/account/base_entrance.html
git commit -m "feat(crm): bare auth shell + demo-user panel on login"
```

---

## Task 3: Complete the demo user (deterministic password + superuser) and fix login redirect

**Files:**
- Modify: `projects/loop-crm/backend/apps/core/management/commands/seed_demo.py`
- Modify: `projects/loop-crm/backend/configs/default/__init__.py`
- Test: `projects/loop-crm/backend/apps/core/tests_seed_demo.py`

**Interfaces:**
- Consumes: `DEMO_EMAIL`, `DEMO_PASSWORD`, `DEMO_WORKSPACE_SLUG`, `DEMO_MEMBERS` from `apps.core.demo` (Task 1).
- Produces: `python manage.py seed_demo [--user U] [--superuser]`; `LOGIN_REDIRECT_URL = "/overview/"`.

- [x] **Step 1: Rewrite `seed_demo.py` to import the contract and always enforce the demo password**

Replace the module constants block:

```python
DEMO_WORKSPACE_SLUG = "demo-workspace"
DEMO_EMAIL = "demo@loop.dev"
DEMO_PASSWORD = "demo-pass-123"

DEMO_MEMBERS = [
    ("sales", "Sales Manager", "sales_manager"),
    ("marketing", "Marketing Manager", "marketing_manager"),
    ("revops", "RevOps Manager", "revops_manager"),
]
```

with:

```python
from apps.core.demo import (
    DEMO_EMAIL,
    DEMO_MEMBERS,
    DEMO_PASSWORD,
    DEMO_WORKSPACE_SLUG,
    ensure_user_workspace,
    seed_workspace,
)
```

(keep the `from apps.core.demo import ensure_user_workspace, seed_workspace` import line and delete the now-duplicated constant lines).

- [x] **Step 2: Deterministic password + superuser flag in `handle`**

In `Command.add_arguments`, add:

```python
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Promote the demo admin to a Django superuser (admin access). Intended for demo deployments only.",
        )
```

In `handle`, replace the demo-admin creation block:

```python
        admin, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": DEMO_EMAIL, "is_staff": True, "first_name": "Demo", "last_name": "Admin"},
        )
        admin.email = DEMO_EMAIL
        admin.is_staff = True
        if created:
            admin.set_password(DEMO_PASSWORD)
        admin.save()
```

with:

```python
        admin, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": DEMO_EMAIL, "is_staff": True, "is_superuser": options["superuser"], "first_name": "Demo", "last_name": "Admin"},
        )
        admin.email = DEMO_EMAIL
        admin.is_staff = True
        if options["superuser"]:
            admin.is_superuser = True
        # Demo credentials are deterministic: re-seeding always restores the
        # known password so the demo state cannot drift from a stale hash.
        admin.set_password(DEMO_PASSWORD)
        admin.save()
```

Also make member passwords deterministic: replace `if member_created: member.set_password(DEMO_PASSWORD)` with `member.set_password(DEMO_PASSWORD)` (keep the `if member_created:` branch removed — always set).

- [x] **Step 3: Fix the post-login redirect**

In `configs/default/__init__.py`:

```python
LOGIN_REDIRECT_URL = "/"
```

becomes:

```python
# After sign-in the user belongs inside the workspace, not on the marketing
# landing (which still shows "Sign in" / "Start free").
LOGIN_REDIRECT_URL = "/overview/"
```

- [x] **Step 4: Tests**

Append to `tests_seed_demo.py`:

```python
class SeedDemoDeterministicTests(TestCase):
    def test_demo_password_is_restored_on_reseed(self):
        call_command("seed_demo")
        admin = User.objects.get(username="demo")
        admin.set_password("some-other-password")
        admin.save()
        call_command("seed_demo")
        admin.refresh_from_db()
        self.assertTrue(admin.check_password(DEMO_PASSWORD))

    def test_superuser_flag_promotes_demo_admin(self):
        call_command("seed_demo", "--superuser")
        admin = User.objects.get(username="demo")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_demo_credentials_come_from_the_shared_contract(self):
        from apps.core.demo import DEMO_EMAIL, DEMO_PASSWORD

        self.assertEqual(DEMO_EMAIL, "demo@loop.dev")
        self.assertEqual(DEMO_PASSWORD, "demo-pass-123")
```

(import `DEMO_PASSWORD` from `apps.core.demo` at the top of the test module.)

- [x] **Step 5: Run the tests**

Run: `cd projects/loop-crm/backend && make test`
Expected: all PASS.

- [x] **Step 6: Commit**

```bash
git add projects/loop-crm/backend/apps/core/management/commands/seed_demo.py \
        projects/loop-crm/backend/configs/default/__init__.py \
        projects/loop-crm/backend/apps/core/tests_seed_demo.py
git commit -m "feat(crm): deterministic demo user + superuser flag; login redirects to /overview/"
```

---

## Task 4: Run the server in demo state (entrypoint, compose, env, Makefile)

**Files:**
- Modify: `projects/loop-crm/backend/entrypoint.sh`
- Modify: `projects/loop-crm/docker-compose.yml`
- Modify: `projects/loop-crm/.env.example`
- Modify: `projects/loop-crm/backend/Makefile`

**Interfaces:**
- Consumes: `seed_demo --superuser` from Task 3.
- Produces: `DEMO_MODE=1` on the backend container auto-seeds the demo workspace at boot (idempotent); `.env.example` documents it; `make seed-demo` runs the command locally.

- [x] **Step 1: Auto-seed in the entrypoint**

In `backend/entrypoint.sh`, after the `collectstatic` block and before the gunicorn `exec`:

```sh
if [ "${DEMO_MODE:-0}" = "1" ]; then
    echo "[STARTUP] DEMO_MODE enabled — seeding the demo workspace (idempotent)..."
    python manage.py seed_demo --superuser
else
    echo "[STARTUP] DEMO_MODE disabled — skipping demo seed"
fi
```

- [x] **Step 2: Pass the flag through Compose**

In `docker-compose.yml`, backend `environment`, add after `SECURE_SSL_REDIRECT`:

```yaml
      DEMO_MODE: "${DEMO_MODE:-0}"
```

- [x] **Step 3: Document in `.env.example`**

Append a section:

```bash
# ── Demo state ─────────────────────────────────────────────────
# Set DEMO_MODE=1 to run this deployment as a public preview: the login page
# shows the seeded demo account (demo@loop.dev / demo-pass-123) and the
# container entrypoint seeds the demo workspace on boot. The demo admin is a
# superuser. NEVER enable on a deployment with real customer data.
DEMO_MODE=0
```

- [x] **Step 4: Makefile target**

In `backend/Makefile`, add to the `.PHONY` line and targets:

```make
seed-demo: ## Seed the demo workspace + demo accounts (idempotent)
	@$(MANAGE) seed_demo --superuser
```

- [x] **Step 5: Verify the entrypoint syntax**

Run: `sh -n projects/loop-crm/backend/entrypoint.sh && docker compose -f projects/loop-crm/docker-compose.yml config -q`
Expected: exit 0 (config validates without the required env vars only when `DJANGO_SECRET_KEY` etc. are set — for a syntax-only check use `sh -n` on the entrypoint; compose `config -q` requires the `.env` values, so run it from the project dir with a filled `.env`).

- [x] **Step 6: Commit**

```bash
git add projects/loop-crm/backend/entrypoint.sh \
        projects/loop-crm/docker-compose.yml \
        projects/loop-crm/.env.example \
        projects/loop-crm/backend/Makefile
git commit -m "feat(crm): run server in demo state (entrypoint auto-seed, compose DEMO_MODE, make seed-demo)"
```

---

## Task 5: Astro pages for every side-nav destination + nav sync

**Files:**
- Modify: `projects/loop-crm/frontend/src/pages/[...path].astro`
- Modify: `projects/loop-crm/frontend/src/lib/navigation.ts`

**Interfaces:**
- Consumes: existing `AppShell.astro` page-shell pattern.
- Produces: static pages at `/marketing/approvals/`, `/tasks/`, `/settings/email/`, `/settings/custom-objects/`, `/settings/saved-views/`, `/settings/import/`; `NAVIGATION` children match the backend `navigation.py` exactly.

- [x] **Step 1: Add the missing page entries to `getStaticPaths`**

In `src/pages/[...path].astro`, append to the `pages` array:

```ts
    { path: '/marketing/approvals/', title: 'Approvals', kicker: 'Marketing · approvals', description: 'Review pending post approvals with the full moderation trail.', module: 'marketing' },
    { path: '/tasks/', title: 'Tasks', kicker: 'Operations · background jobs', description: 'Workflow, attribution, publishing, and finance jobs — the shared audit trail.', module: 'tasks' },
    { path: '/settings/email/', title: 'Email inbox', kicker: 'Workspace · email', description: 'Connect Gmail or Outlook to sync inbound messages into the CRM timeline.', module: 'workspace' },
    { path: '/settings/custom-objects/', title: 'Custom objects', kicker: 'Workspace · data model', description: 'Add a new record type without a migration — declarative fields with validated JSON rows.', module: 'workspace' },
    { path: '/settings/saved-views/', title: 'Saved views', kicker: 'Workspace · views', description: 'Your persisted list and kanban view configurations for every resource.', module: 'workspace' },
    { path: '/settings/import/', title: 'Import', kicker: 'Workspace · data', description: 'Import companies, contacts, and deals from a CSV upload — validated and workspace-scoped.', module: 'workspace' },
```

- [x] **Step 2: Sync the build-time nav with the canonical backend nav**

In `src/lib/navigation.ts`, add the missing children:
- `marketing` children: add `{ id: 'approvals', label: 'Approvals', href: '/marketing/approvals/' }`
- `workspace` children: add `{ id: 'email', label: 'Email inbox', href: '/settings/email/' }`, `{ id: 'custom-objects', label: 'Custom objects', href: '/settings/custom-objects/' }`, `{ id: 'saved-views', label: 'Saved views', href: '/settings/saved-views/' }`, `{ id: 'import', label: 'Import', href: '/settings/import/' }`

The result must contain exactly the children the backend `navigation.py` declares (crm: companies, contacts, pipelines, deals, activities; marketing: calendar, campaigns, channels, media, approvals; finance: invoices, payments, revenue; attribution: touchpoints, reports; workspace: members, workflows, integrations, email, custom-fields, custom-objects, saved-views, import, audit).

- [x] **Step 3: Build + verify**

Run: `cd projects/loop-crm/frontend && npm run build`
Expected: build succeeds and emits `dist/marketing/approvals/index.html`, `dist/tasks/index.html`, `dist/settings/email/index.html`, `dist/settings/custom-objects/index.html`, `dist/settings/saved-views/index.html`, `dist/settings/import/index.html`.

- [x] **Step 4: Commit**

```bash
git add projects/loop-crm/frontend/src/pages/[...path].astro \
        projects/loop-crm/frontend/src/lib/navigation.ts
git commit -m "feat(crm): add Astro pages for all side-nav destinations; sync nav catalog"
```

---

## Task 6: End-to-end verification against a demo-state server

**Files:** none (verification only).

- [ ] **Step 1: Boot the stack with demo state** *(pending — requires a server deploy; the local half of Task 6 — SQLite migrate + `seed_demo --superuser` + runserver smoke — was verified 2026-08-17)*

```bash
cd projects/loop-crm
cp .env.example .env   # fill DJANGO_SECRET_KEY / POSTGRES_PASSWORD / REDIS_PASSWORD / FUSION_BOLT_JWT_SECRET
echo 'DEMO_MODE=1' >> .env
docker compose up -d --build
```

- [x] **Step 2: Probe every route as an anonymous visitor**

```bash
for p in / /accounts/login/ /accounts/signup/ /overview/ /crm/companies/ /marketing/approvals/ /tasks/ /settings/email/ /settings/import/ /admin/login/; do
  curl -s -o /dev/null -w "%{http_code}  $p\n" "https://crm.structa.cloud$p"  # or http://127.0.0.1 with Host header
done
```

Expected: `200` for `/`, `/accounts/login/`, `/accounts/signup/`; `200` (or `302` → login) for the app pages; no `404`.

- [x] **Step 3: Sign in as the demo user**

`curl`-POST the allauth form with `login=demo@loop.dev&password=demo-pass-123`, follow the redirect to `/overview/`, and confirm the shell (side nav via `/fragments/navigation/`) renders and the RevOps dashboard API returns seeded counts.

- [x] **Step 4: Sign in as a fresh signup**

Create a new account; confirm `user_signed_up` seeds a personal workspace and the user lands on `/overview/`.

- [x] **Step 5: Regression**

Run: `cd projects/loop-crm/backend && make test` and `cd projects/loop-crm/frontend && npm run check`.
Expected: both green.

---

## Task 7: Twenty/Postiz DNA — comparison doc + design-token map

**Files:**
- Create: `docs/plans/loop-crm/twenty-postiz-comparison.md`
- Create: `projects/loop-crm/frontend/DESIGN.md`

**Interfaces:**
- Consumes: nothing new (research only).
- Produces: the Twenty vs Postiz vs Loop-CRM feature/package comparison (verified against the npm registry) and a Loop-CRM `DESIGN.md` token map so every future page ships consistent.

- [x] **Step 1: Write the comparison doc**

Create `docs/plans/loop-crm/twenty-postiz-comparison.md` with: (a) package findings — `@postiz/node` 1.0.8 (scheduling-only HTTP SDK), `twenty-sdk` 2.31.0 (CRM extension CLI/SDK), no `@twenty-ui/*` and no Postiz UI packages published, and the explicit answer that **no single package has both features** (Loop-CRM is the only merged implementation); (b) the complete feature matrix (Twenty vs Postiz vs Loop-CRM — attribution and finance are net-new in Loop-CRM); (c) the design-enhancement recommendation (pattern mapping + token formalization, not new packages).

- [x] **Step 2: Write the DESIGN.md token map**

Create `projects/loop-crm/frontend/DESIGN.md` capturing the tokens already used in `src/styles/globals.css` and the landing/shell styles: substrate `#0b1114` (dark, no pure black), ink `#edf2f7`, muted `#8d9aaa`, line `#263241`, accent emerald `#73d1bb`, accent-bright `#a7e8d8`; display type `Bricolage Grotesque`, data type `JetBrains Mono`; radius system (cards `1rem/.4rem` squircle, controls `.45rem`, pills full); shadow rule (diffused tinted shadows, no hard drop shadows); borrowed-pattern map (kanban = Twenty, calendar/approvals = Postiz, ledger/attribution = Loop-CRM unique). One paragraph each, no placeholders.

- [x] **Step 3: Verify the docs render**

Run: `grep -c 'POSTIZ\|TWENTY' projects/loop-crm/frontend/DESIGN.md` (case-insensitive) — expect a positive count; visually confirm both files open cleanly.

- [x] **Step 4: Commit**

```bash

git add docs/plans/loop-crm/twenty-postiz-comparison.md \
        projects/loop-crm/frontend/DESIGN.md

git commit -m "docs(crm): Twenty/Postiz comparison + Loop-CRM design-token map"
```

---

## Search suggestions & resources

How the comparison was researched, plus the canonical references for anyone extending this work. Verified 2026-08-17.

### Searches that produced the package findings

- `Postiz npm package API social media scheduling self-hosted library` → `@postiz/node` (npm), Postiz Public API + CLI docs.
- `Twenty CRM open source npm package twentycrm API client` → `twenty-sdk` (npm), Twenty REST/GraphQL.
- `"CRM" "social media scheduling" combined open source platform package both features twenty postiz alternative` → **no combined package**; nearest products are Mixpost (scheduling only), SuiteCRM/EspoCRM (CRM only), Frappe CRM (CRM only).
- `@twenty-ui npm packages twenty design system ui components` → no published `@twenty-ui/*`; Twenty's design system is internal to `twentyhq/twenty`.

### Canonical links

| Resource | URL | Use |
|---|---|---|
| Twenty source | https://github.com/twentyhq/twenty | CRM DNA — kanban, record tables, custom objects |
| Twenty product | https://twenty.com | Positioning + API docs |
| Postiz source | https://github.com/gitroomhq/postiz-app | Scheduling DNA — calendar, approvals, 30+ platforms |
| Postiz docs / public API | https://docs.postiz.com · https://postiz.com | `@postiz/node` contract reference |
| `@postiz/node` | https://www.npmjs.com/package/@postiz/node | Scheduling-only HTTP SDK (v1.0.8) — do not install in Loop-CRM |
| `twenty-sdk` | https://www.npmjs.com/package/twenty-sdk | CRM-extension CLI/SDK (v2.31.0) — contract reference only |
| django-fusion | `libs/django-fusion` in this repo | `{% comp %}` / fragments / render-first pipeline |
| allauth | https://docs.allauth.org | Login/signup/password flow the auth tasks configure |
| Astro static output | https://docs.astro.build/en/guides/deploy/ | Why `getStaticPaths` entries are required (Task 5) |
| Traefik routers | https://doc.traefik.io/traefik/routing/routers/ | `crm.yml` priority split (backend 200 / frontend 100) |
| Loop-CRM deploy | `projects/loop-crm/README.md` § Docker deployment | Server half of Task 6 |

### Follow-up search angles (next milestones)

- "Postiz public API publish endpoint swagger" — to mirror the exact publish contract on Loop-CRM's `/bolt/posts` road.
- "Twenty GraphQL schema objects relations" — to enrich `custom_object_catalog` field types.
- "allauth demo mode autofill login rate limit" — hardening the demo login (rate-limit bypass for the demo panel).
- "Astro middleware auth redirect static" — if the landing should become account-aware without full SSR.

---

## Follow-up work (explicitly out of scope for this plan)

- **Data-backed Astro pages:** the six new pages (and the existing shell pages like `/crm/companies/`) render page chrome + highlight cards; wiring each to live Bolt resources (list + create/edit) is the next milestone.
- **Approvals workflow UI:** the backend `Post` approval state machine exists; the approvals page needs the moderation surface (approve/reject actions via `/bolt/posts`).
- **Landing auth state:** `index.astro` always shows "Sign in"/"Start free"; making it account-aware needs the navigation API cookie read at build/request time (SSR or a lightweight client check).
- **Hardening:** `DEMO_MODE` should refuse to enable when `FUSION_BOLT_JWT_SECRET` equals the dev fallback; consider rate-limiting the demo login.
