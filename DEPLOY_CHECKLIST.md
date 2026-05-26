# Websites Deployment & File-check Plan

Purpose: step-by-step checklist to validate both websites (ctc-research.com and structa.cloud), assets, configs, and packages. Follow each step and record results.

## Checklist

1. Inventory directories
- Confirm `www`, `configs`, `assets`, `plugins`, `templates`, `bundles` exist for each site.

2. Validate Django configs
- Check `DJANGO_SETTINGS_MODULE` points to `configs.settings`.
- Verify `websites/configs/base` files load without import errors.

3. Verify environment YAMLs
- Inspect `websites/configs/settings/ENV/*.yml` for required keys (STATIC_URL, MEDIA_URL, DATABASES).

4. Check package imports
- Ensure `django_osoul` and `django_rseal` are imported from `libs/` (no duplicate copies in `websites/`).

5. Detect duplicated files/packages
- Search for duplicate `conf.py`, shim modules, or duplicated templates across `plugins/` and `www/core/`.

6. Verify webpack & npm build
- From `websites/` run `npm ci` and `npm run build:all`.
- Confirm `assets/bundles/*/bundles.json` exist for both sites.

7. Run Django `build_assets`
- Run: `python manage.py build_assets --no-input` (or `npm run build:assets:ctc` / `build:assets:structa`).

8. Check `collectstatic` & bundles
- Confirm `STATIC_ROOT` contains static files and bundles were copied to `STATIC_ROOT/bundles`.
- Verify `WEBPACK_LOADER['DEFAULT']['STATS_FILE']` path exists.

9. Review Wagtail templates & static
- Ensure templates live in `templates/`, plugin templates in `plugins/*/templates`, and no duplicates override unexpectedly.
- Confirm Wagtail settings (`WAGTAILIMAGES_*`) align with media/static layout.

10. Run tests and smoke checks
- `python -m pytest tests/ci --ds=configs.settings` (or `pytest -q`).
- Run `python manage.py check`.

11. Produce findings
- Create a short report with: failures, missing bundles, duplicate files, mismatched STATIC_ROOT, commands run and outputs.

12. Apply fixes (optional)
- Remove deprecated shims (e.g., `www/conf.py`) and update `SPECIFICATION.md` and `Makefile` if necessary.

## Commands (copyable)

```bash
cd /root/site/websites
# Build frontend bundles
npm ci
npm run build:all

# Build Django assets for each site
python manage.py build_assets --no-input

# Check Django config and collectstatic
python manage.py check --settings=configs.settings
python manage.py collectstatic --no-input --settings=configs.settings

# Run CI tests
python -m pytest tests/ci -q
```

## Notes
- For Docker deployments ensure `RUNNING_ENV=docker` and that volume mounts expose `assets/bundles` to the web server.
- Keep `libs/django-osoul` and `libs/django-rseal` as single source-of-truth packages (editable installs in workspace).
- After running the checklist, update this file with results and any remediation steps taken.

---

## What I changed

- Removed files: deleted the redundant shim files at:
	- `websites/ctc-research.com/www/conf.py`
	- `websites/structa.cloud/www/conf.py`
	- `websites/www/conf.py`

## Quick findings (high priority)

- **Settings package:** The project uses a central `configs` package under `websites/configs`. See asset/static configuration in `websites/configs/base/assets.py`.
- **Assets build:** Webpack + Django build is wired up:
	- npm scripts and per-site build targets in `websites/package.json`.
	- Django management command `build_assets` implemented at `websites/www/apps/management/commands/build_assets.py`.
	- `Makefile` targets call the management command; see `websites/Makefile`.
- **Static configuration:** `STATIC_ROOT`, `STATICFILES_DIRS`, `BUNDLES_DIR`, and `WEBPACK_LOADER` are defined in `websites/configs/base/assets.py`. Directories are created at import time and `bundles.json` presence toggles the loader class.
- **Packages (no duplicates):** `django-osoul` and `django-rseal` live in `libs/` and are imported as workspace packages (`django_osoul`, `django_rseal`). I found no duplicate package directories under `websites/`.
- **Deprecated shim removal:** The removed `www/conf.py` files were re-export shims of `django_osoul`/`django_rseal` config objects. Removing them reduces module shadowing risk.
- **Project wiring:** `DJANGO_SETTINGS_MODULE` is `configs.settings` (set in `websites/www/asgi.py`, `manage.py` and test scripts). `websites/configs/base/assets.py` is the canonical place for static/bundles settings.

## Risks & recommendations

- **Validate settings import path:** Ensure runtime PYTHONPATH includes the `websites/` package when running Django (usually satisfied when running `manage.py` from `websites/`). If you execute from another CWD, set `PYTHONPATH` or run via the project `manage.py` wrapper.
- **Bundles location (Docker):** `assets.py` changes `BUNDLES_DIR` when `RUNNING_ENV == docker`. Confirm Docker Compose mounts and web server static file roots map to the same paths.
- **Collectstatic / Whitenoise / Gunicorn:** Confirm `STATIC_ROOT` used by Gunicorn/uWSGI and the static server (nginx/traefik or whitenoise) match. If using whitenoise, verify middleware ordering.
- **Wagtail templates & static:** Confirm templates use `{% static %}` and that bundle paths line up with `WEBPACK_LOADER['DEFAULT']['BUNDLE_DIR_NAME']`.
- **Tests & CI:** Run CI tests that exercise `build_assets` and `collectstatic`. If workspace editable installs are used, verify packaging in CI (pyproject or pip editable flags).

## Concrete next validation steps (per-site)

From the `websites/` folder perform these steps and record outputs:

1) Prepare environment

```bash
cd /root/site/websites
# ensure python venv active and node available
```

2) Frontend build (webpack)

```bash
npm ci
npm run build:ctc    # build ctc-research.com bundles
npm run build:structa # build structa.cloud bundles
```

Verify: `assets/bundles/ctc-research.com/bundles.json` and `assets/bundles/structa.cloud/bundles.json` exist and `publicPath` points to `/static/`.

3) Django asset build & collectstatic (per site)

```bash
# for ctc
PROJECT_PATH=ctc-research.com python manage.py build_assets --no-input
# for structa
PROJECT_PATH=structa.cloud python manage.py build_assets --no-input
```

Verify: `STATIC_ROOT` contains `bundles/<site>/` and static files copied. Confirm `WEBPACK_LOADER['DEFAULT']['STATS_FILE']` path exists.

4) Config & tests

```bash
python manage.py check --settings=configs.settings
python manage.py collectstatic --no-input --settings=configs.settings
python -m pytest tests/ci -q --ds=configs.settings
```

Record any errors, missing files, or mismatches.

## Suggested organization / code-review notes

- **Centralize env docs:** Keep env yml samples under `websites/configs/settings/ENV/` and avoid committing production secrets — use secret manager or `.env.production` with documented deploy steps.
- **Avoid local shims:** Do not add `conf.py` re-export shims inside `www/` or app folders; prefer importing `configs` directly.
- **Bundle output clarity:** Keep per-site subpaths consistent; document expected runtime mapping in `websites/SPECIFICATION.md` and add a verification script for `bundles.json` publicPath.
- **Plugin templates vs core templates:** Search for duplicate templates across `plugins/` and `www/core/templates` and consolidate overrides explicitly (plugin overrides should be minimal and documented).
- **Document build flow:** Add `websites/docs/DEPLOY.md` (or update `websites/SPECIFICATION.md`) describing the full build+deploy steps (npm, `build_assets`, `collectstatic`, restart server, nginx mounts verification).

## Detailed prompt (automated verification / CI script)

Use this prompt to drive an automated verification or to ask me to run the full check here:

"Run a full deployment verification for the `websites` workspace:

1. From `websites/` run `npm ci` then `npm run build:all` and confirm successful webpack exit codes and that `assets/bundles/*/bundles.json` exist for `ctc-research.com` and `structa.cloud`.
2. For each site run `PROJECT_PATH=<site> python manage.py build_assets --no-input` with `DJANGO_SETTINGS_MODULE=configs.settings` and verify `collectstatic` completes and files appear in `STATIC_ROOT`.
3. Confirm `STATIC_ROOT` and `BUNDLES_DIR` match the nginx/traefik mount points in `docker-compose.yml` and `compose/*` files.
4. Run `python manage.py check` and the CI pytest tests to ensure no runtime import/path errors for `django_osoul` and `django_rseal`.
5. Produce a short report listing: bundle paths, `STATIC_ROOT`, `STATICFILES_DIRS`, webpack loader `STATS_FILE`, and any missing files or errors."

---

If you want I can run the full build & verification now (requires node + venv), finish the Wagtail/template conflict review, and produce a prioritized remediation report and `websites/docs/DEPLOY.md`.

## Wagtail, pages, authentication, email, and dependency checks

Add these per-site checks to ensure pages, Wagtail, and authentication flows are deploy-ready.

1) Inspect pages and Wagtail models
- List Wagtail page models and verify they inherit from `Page`/`RoutablePageMixin` where expected.
- Check `www/core` and `plugins/*/models.py` for custom page models, hooks, and index routes.
- Verify templates referenced by pages exist under `templates/` or `plugins/*/templates/`.

Commands:
```bash
cd /root/site/websites
# find page models
grep -R "class .*Page" -n www plugins || true
# list templates referenced
grep -R "render\(|template_name\|template\_name" -n www plugins || true
```

2) Verify `django-allauth` (or custom auth) and login/registration flows
- Confirm `django-allauth` (or equivalent) is in `INSTALLED_APPS` and settings like `ACCOUNT_EMAIL_VERIFICATION`, `ACCOUNT_AUTHENTICATION_METHOD`, `LOGIN_REDIRECT_URL` are defined.
- Check social login adapters and providers under `plugins/` or `configs`.
- Run a local smoke test to register a user and confirm the expected redirect and email invite flow.

Commands:
```bash
cd /root/site/websites
python manage.py shell --settings=configs.settings -c "from django.conf import settings; print([a for a in settings.INSTALLED_APPS if 'allauth' in a or 'accounts' in a])"
# manual smoke: create user and check email send in console/email backend
```

3) Audit third-party packages and custom integrations
- Produce a list of third-party apps used by the sites (`INSTALLED_APPS`) and map which features they provide (authentication, payments, search, wagtail add-ons).
- Verify there are no conflicting packages (two different Wagtail add-ons providing same template names or signal handlers).

Commands:
```bash
cd /root/site/websites
python - <<'PY'
from django.conf import settings
print('\n'.join(settings.INSTALLED_APPS))
PY
# or inspect pyproject.toml / package manifests for pinned versions
```

4) Verify email sending and notification functions
- Check `EMAIL_BACKEND`, SMTP settings (HOST, PORT, USER, PASSWORD), and queuing (RQ/Celery) configuration in `configs/settings/ENV/*`.
- Test sending a sample email via Django shell and verify delivery or that the email task is queued.

Commands:
```bash
cd /root/site/websites
python manage.py shell --settings=configs.settings -c "from django.core.mail import send_mail; send_mail('Test','Body','from@example.com',['to@example.com'],fail_silently=False)"
# If using Celery/RQ, ensure worker is running and test the queued task.
```

5) Dependency check and duplicate detection
- Run `pip list` / `pip freeze` inside the project's venv and compare with `pyproject.toml` and `websites/package.json`.
- Use `pip check` to detect incompatible packages and `pipdeptree` to view dependency graph (install it if required).
- Search for duplicate package directories (e.g., another copy of `django_osoul` under `websites/`), which can cause import confusion.

Commands:
```bash
source .venv/bin/activate
pip list
pip check || true
pip install pipdeptree || true
pipdeptree | head -n 200
find . -type d -name "django_osoul" -o -name "django-rseal" || true
```

6) Report and remediate
- Record any failures (missing templates, failing email, dependency conflicts) and prioritize fixes.
- Common remediations: update `INSTALLED_APPS` ordering, remove duplicate packages, pin versions in `pyproject.toml`, ensure `EMAIL_BACKEND` is set for production.

Add results to this file under a `## Results` section after running the checks.
