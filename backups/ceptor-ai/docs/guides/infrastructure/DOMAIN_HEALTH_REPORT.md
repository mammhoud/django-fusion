# Domain Health Report

**Date**: July 7, 2026
**Status**: ✅ Resolved (consolidated)
**Replaces**: the previous root-level `DOMAIN_RECHECK_REPORT.md`, `RECHECK_INDEX.md`, `DOMAIN_TESTS_SUMMARY.md`, `DOMAIN_REACHABILITY_TEST_GUIDE.md`, and `TESTS_EXECUTION_RESULTS.md` (all now removed from the repo root — superseded by this single document).

---

## TL;DR

| Item                                | Status     | Owner       | Notes                                                                     |
| ----------------------------------- | ---------- | ----------- | ------------------------------------------------------------------------- |
| VResume `/blog/list/` 500 error     | ✅ Resolved | Code (this PR) | Stale template reference in `BlogPostListView` fixed.                    |
| CTC `/research/` 404                | 🟡 Pending | CMS admin   | Missing Wagtail page — create in admin, not a code issue.                 |
| CTC `/about/` 404                   | 🟢 N/A     | —           | Page exists; verify the menu/footer links if you still see 404s.           |
| `.env` split between `proxy/` and root | ✅ Resolved | Code (this PR) | Traefik now reads DNS provider + API key from the **base repo** `.env`. |

Infrastructure (DNS, TLS, server, security headers) was already healthy in the previous recheck and is unchanged.

---

## 1. VResume 500 on `/blog/list/` — **Fixed**

### Root cause

`applications/VResume/www/pages/blog/views.py::BlogPostListView` set:

```python
template_name = "blog/standalone/blog_index.html"
```

…but the template directory `applications/VResume/templates/blog/standalone/` does not exist on disk. The only blog templates that exist for VResume are `blog/fragments/post_list.html` and `blog/fragments/post_detail.html`. The result: every request to `/blog/list/` raised `TemplateDoesNotExist` and the upstream ASGI server (uvicorn) returned HTTP 500.

Because the root URL `/` issues a 302 → `./blog/list/`, **all** VResume traffic was 500ing, not just the blog path. That matched the report's "Total service outage" finding.

### Fix

Point `BlogPostListView` at the shared blog index template, which is the same one CTC and LMS-Demo use:

```python
# applications/VResume/www/pages/blog/views.py
class BlogPostListView(ListView):
    model = BlogPost
    # The legacy path `blog/standalone/blog_index.html` was orphaned when
    # the standalone blog tree was consolidated into the shared asset
    # template. Point to the shared `blog/blog_index.html` (the same one
    # used by CTC and LMS-Demo) so /blog/list/ renders instead of 500'ing.
    template_name = "blog/blog_index.html"
    context_object_name = "posts"
    paginate_by = 5
    ...
```

This works because VResume's template search path already includes `applications/assets/templates/`, where the shared `blog/blog_index.html` lives. The `BlogListComponent` (FragmentComponent) at `/blog/list/` is unchanged and continues to serve the HTMX fragment.

### Verification checklist (post-deploy)

```bash
# 1. Re-run the quick check
./tests/quick_curl_checks.sh

# 2. Confirm the redirect chain returns 200
curl -sL -o /dev/null -w "%{http_code} -> %{url_effective}\n" https://vresume.structa.cloud/

# 3. Spot-check the rendered HTML for a <ul class="post__list"> marker
curl -sL https://vresume.structa.cloud/blog/list/ | grep -c 'post__list'
```

Expected: `200`, `200`, `>=1`.

---

## 2. CTC `/research/` and `/about/` — **Not a code issue**

CTC's `applications/ctc-research/www/urls.py` ends with `path('', include(wagtail_urls))` inside `i18n_patterns(...)`. That means every URL not matched by an explicit redirect falls through to the Wagtail page tree — i.e. **Wagtail pages, not Django views, own these paths**.

- `/about/` — the Wagtail "About" page exists. If the live site still 404s, the page is unpublished in the CMS. Publish it via the Wagtail admin (`/admin/pages/`).
- `/research/` — there is no Wagtail "Research" page. Create one as a child of the site root in the Wagtail admin. Until that page exists, `/research/` will continue to 404, and that is correct behavior, not a bug.

No code change is appropriate here. Adding hardcoded Django views in `www/urls.py` would shadow future Wagtail pages and break the CMS workflow.

---

## 3. `.env` consolidation — base repo is now the source of truth

### Previous state

Two `.env` files carried proxy-related secrets:

- `proxy/.env` — `CF_DNS_API_TOKEN`, `CF_API_EMAIL`, `CF_API_KEY`, `LETSENCRYPT_EMAIL` (gitignored, holds real creds)
- `.env` (root) — Django/DB/Redis/email/app config

This split meant a fresh checkout had to know about two different `.env` files to get the proxy working.

### New state

The **root `.env` is the single source of truth** for:

- `DNS_PROVIDER` — selects the Traefik DNS-01 plugin (default: `cloudflare`)
- `CF_DNS_API_TOKEN` — Cloudflare scoped API token (preferred)
- `CF_API_EMAIL` / `CF_API_KEY` — Cloudflare global key fallback (legacy)
- `LETSENCRYPT_EMAIL` — ACME registration email

All four are now documented in `.env.example` at the repo root.

### How the proxy uses it

`proxy/docker-compose.traefik.yml` loads env files in this order:

```yaml
env_file:
  - path: ../.env    # base repo — canonical, required for new deployments
    required: false
  - path: ./.env     # legacy fallback for existing deployments
    required: false
```

> **Run docker-compose from the `proxy/` directory** so the `../.env` path resolves to the repo root. Example:
>
> ```bash
> cd proxy
> docker compose -f docker-compose.traefik.yml up -d
> ```
>
> If you invoke compose from a different working directory, set an explicit absolute path instead, e.g. `path: /home/structa.cloud/.env`.

### Migration steps for an existing host

```bash
# 1. Copy the new vars from the base repo .env.example into the existing /.env
cat .env.example | grep -E '^(DNS_PROVIDER|CF_|LETSENCRYPT_EMAIL)' >> .env

# 2. (Optional) Once the proxy is reading from /.env successfully, you can
#    delete proxy/.env. The docker-compose entry stays as a fallback until
#    then, so the order is safe to roll out.
rm proxy/.env
```

---

## 4. Remaining runtime / monitoring notes

These were unchanged from the previous recheck and are listed for context only.

- **DNS resolution** ✅ for both `vresume.structa.cloud` and `ctc-research.com` (same IP `187.77.166.222`).
- **TLS** ✅ valid certificates via Let's Encrypt (DNS-01, Cloudflare). HSTS enabled at 2 years.
- **Server** ✅ uvicorn ASGI, response time < 70 ms.
- **Security headers** ✅ HSTS, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy all present.
- **HTMX / CSRF** ✅ `hx-headers='{"x-csrftoken": "..."}'` observed in CTC's HTML.

The test scripts that produced the original measurements are still useful and were preserved (only the `.md` reports were consolidated):

- `tests/quick_curl_checks.sh` — < 1 min smoke test
- `tests/domain_reachability_curl.sh` — full curl diagnostic
- `tests/test_domain_reachability.py` — Python comprehensive suite

> **Provenance note** (carried over from the now-deleted `TESTS_EXECUTION_RESULTS.md`):
> the Python suite had a `KeyError: 'total_css_references'` bug in its
> error-path return dicts. That was fixed in-place by adding the missing
> key to all return statements in `test_style_tags()`. If the symptom
> reappears, that's the first place to look.

---

## 5. Reproducible verification

After deploying the VResume fix and the `.env` change:

```bash
# Quick (30s)
cd /home/structa.cloud && ./tests/quick_curl_checks.sh

# Full curl (2-3m)
cd /home/structa.cloud && ./tests/domain_reachability_curl.sh

# Python (3-5m)
cd /home/structa.cloud && python3 tests/test_domain_reachability.py
```

All three should now report VResume green, matching CTC.

---

## 6. Change log (this report)

| Date       | Change                                                                                  | Files                                                                                              |
| ---------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 2026-07-07 | Fixed VResume `/blog/list/` 500: `BlogPostListView.template_name` → `blog/blog_index.html` | `applications/VResume/www/pages/blog/views.py`                                                     |
| 2026-07-07 | Added `DNS_PROVIDER`, `CF_DNS_API_TOKEN`, `CF_API_EMAIL`, `CF_API_KEY`, `LETSENCRYPT_EMAIL` to root `.env.example` | `.env.example`                                                                                     |
| 2026-07-07 | Updated `proxy/docker-compose.traefik.yml` to load `../.env` (with `proxy/.env` as fallback) | `proxy/docker-compose.traefik.yml`                                                                 |
| 2026-07-07 | Removed redundant root reports; consolidated into this single doc                        | Deleted: `DOMAIN_RECHECK_REPORT.md`, `RECHECK_INDEX.md`, `DOMAIN_TESTS_SUMMARY.md`, `DOMAIN_REACHABILITY_TEST_GUIDE.md`, `TESTS_EXECUTION_RESULTS.md` |
| 2026-07-07 | Added this consolidated report                                                          | `docs/infrastructure/DOMAIN_HEALTH_REPORT.md`                                                       |
