# Repository Cleanup and Dependency Shim Plan

## Completed in this cleanup

1. **Ignored runtime artifacts**
   - Added repository-wide log ignore rules for `*.log`, `logs/`, nested `*/logs/`, `compose/logs/*.log`, and generated diagnostic logs under `docs/`.
   - Added `libs/.venv/` so the local library workspace virtual environment is not tracked.

2. **Removed tracked log output**
   - Removed committed runtime logs from `logs/`, `compose/logs/`, `lms-demo/logs/`, and generated `.log` files under `docs/`.
   - Kept `.gitkeep` files where directories are intentionally retained.

3. **Moved Markdown documentation into `docs/`**
   - Relocated non-template Markdown files from project roots, website roots, config folders, scripts, and test folders into `docs/relocated/` while preserving their original relative paths.
   - Left Markdown files inside asset/template trees in place because those can be application content/templates instead of documentation.

4. **Removed unused root scripts and debug probes**
   - Removed unreferenced deployment helper scripts from the root `scripts/` folder.
   - Removed unreferenced root setup/debug scripts.

5. **Replaced broad fake module handling with real dependency imports**
   - Deleted `configs/fake_modules.py`, which injected fake `django_fusion` modules into `sys.modules`.
   - Removed the fake-module setup call from `ctc-research/settings.py`.
   - Added `twilio>=9.0` to the root Python dependencies so the installed `django_fusion` package can import its Twilio-backed interaction modules normally.
   - Replaced legacy application imports from fake-only paths such as `django_fusion.core.*`, `django_fusion.web.*`, and `django_fusion.comp.site` with canonical package paths (`django_fusion.models`, `django_fusion.managers`, `django_fusion.handlers`, `django_fusion.services`, `django_fusion.site`, `django_fusion.site.routes`, and `django_fusion.views`).
   - Replaced legacy `crafts_ai.http.*` imports with installed package paths under `crafts_ai.handlers` and `crafts_ai.middlewares`.
   - Replaced stale `crafts_ai.contrib.models` imports with `crafts_ai.contrib.core.models`.

6. **Cleaned library workspace metadata**
   - Removed non-existent workspace members and sources (`crafts-ai`, `django-fusion-stub`, `nawaai`) from `libs/pyproject.toml`.
   - Restored `.gitmodules` entries for the tracked `libs/django-fusion`, `libs/django-fusion`, and `libs/crafts-ai` gitlinks so submodule commands have path mappings.

7. **Documented website apps**
   - Added `docs/WEBSITE_APPLICATION_INVENTORY.md` with the apps discovered for `ctc-research`, `lms-demo`, and `VResume`.

## Remaining errors found while checking logs and running checks

### Secret key warnings

`manage.py --site=ctc-research check` reports that the development `SECRET_KEY` is too short and starts with the placeholder prefix `dev-secret-key`.

**Fix:** generate a secure key and place it in the runtime environment or local `.env` file:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Do not commit the generated key.

### Django admin inline relation error

After replacing fake `django_fusion` modules with real dependencies, `manage.py --site=ctc-research check` proceeds farther and then fails in Django admin checks with:

```text
AttributeError: 'str' object has no attribute '_meta'
```

This indicates at least one admin inline model has a foreign key whose `remote_field.model` is still an unresolved string when admin relation checks run.

**Investigation plan:**

1. Run a focused Django shell script that imports all admin modules and prints inline classes plus each inline model's foreign keys.
2. Identify fields where `field.remote_field.model` is a string.
3. Replace stale string model references with valid `app_label.ModelName` references that resolve in the installed app registry, or move the inline registration until after the target app/model is installed.
4. Add a regression check that fails if an admin inline has unresolved remote models.

### `crafts_ai` architecture drift

Several apps were importing old paths such as `crafts_ai.http.handlers.*`, while the installed package exposes handlers under `crafts_ai.handlers.*`.

**Enhancement plan:**

1. Add compatibility tests that import all project modules containing `crafts_ai` imports.
2. Prefer canonical installed-package paths instead of adding local shims.
3. If compatibility is required for older deployments, implement a small upstream compatibility module inside `crafts_ai` itself, not in this website repo.
4. Pin internal library commits in the lock file and document the expected package API surface.

## Dependency shim policy going forward

1. **No broad fake modules.** Do not inject fake packages into `sys.modules` for production app startup.
2. **Use real dependencies.** If a package import fails because an optional dependency is missing, add that dependency to `pyproject.toml` or make the upstream package lazy-import the optional provider.
3. **Local fallbacks must be narrow.** A fallback may be acceptable only for optional runtime integrations (for example, not sending SMS when Twilio settings are absent), but it must not fake Django models, managers, or app packages.
4. **Canonical imports only.** Website code should import from the current public API of internal libraries. Legacy import paths should be fixed or supported upstream.
5. **Automated import checks.** Add CI coverage for `python manage.py --site=<site> check` for every website and a static import scan for banned fake-module patterns (`sys.modules[...] =`, `types.ModuleType`, `django_fusion.core`, `django_fusion.web`, `django_fusion.comp.site`, `crafts_ai.http`).

## Next steps

1. Fix the unresolved admin inline relation discovered by Django checks.
2. Run `manage.py check` for all websites: `ctc-research`, `lms-demo`, and `vresume`.
3. Run the test suite after checks pass.
4. Keep `.gitmodules` synchronized with the `libs/` gitlinks, or intentionally remove gitlinks and consume internal packages only through `pyproject.toml` sources.
5. Add CI jobs that verify no `.log` files or root-level `.md` documentation files are committed outside approved template/content folders.

### Cross-site check results

- `ctc-research`: dependency shims are removed and import path cleanup now reaches Django admin checks. Remaining blocker is an unresolved admin inline relation (`AttributeError: 'str' object has no attribute '_meta'`) plus insecure development `SECRET_KEY` warnings.
- `lms-demo`: startup fails because `crafts_ai.models.settings.subscription.NewsletterSubscription` requires `settings.PROFILE_MODEL`, but `lms-demo` settings do not define it. Add the same explicit `PROFILE_MODEL` used by `ctc-research` or wire the real profile model if the site has one.
- `vresume`: startup fails because `INSTALLED_APPS` references `plugins.accounts.apps`, but that module does not exist under `VResume/plugins`. Either add the real accounts app package for VResume, remove that app from VResume settings, or point the app entry to the correct shared/plugin module.
