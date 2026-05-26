# Deployment & Validation Checklist (planned)

Purpose: concise, actionable checklist to validate both websites (ctc-research.com and structa.cloud) before deployment.
Note: This checklist is a validation and reorganization plan — DO NOT perform full refactors or move large code structures. Focus on configuration, imports, templates, static assets, and small safe reorganizations.

- [ ] Inventory directories per-site: `www`, `configs`, `assets`, `plugins`, `templates`, `bundles`.
- [ ] Validate Django settings and import path: ensure `DJANGO_SETTINGS_MODULE` is `configs.settings` and runtime PYTHONPATH includes `websites/` when running `manage.py`.
- [ ] Verify env YAMLs: inspect `websites/configs/settings/ENV/*.yml` for keys: `STATIC_URL`, `MEDIA_URL`, `DATABASES`, `EMAIL`.
- [ ] Confirm packages: `django_osoul`, `django_rseal`, `django_grep` are imported from `libs/` (no duplicate packages in `websites/`).
- [ ] Detect duplicates: search for duplicated templates, `conf.py` shims, or duplicate app copies; do not delete or restructure files beyond removing deprecated shims.
- [ ] Frontend build check: `npm ci` then `npm run build:ctc` and `npm run build:structa`; verify `assets/bundles/<site>/bundles.json` exist.
- [ ] Django asset build: `PROJECT_PATH=<site> python manage.py build_assets --no-input` for each site.
- [ ] Collectstatic and static layout: confirm `STATIC_ROOT` has bundles copied and `WEBPACK_LOADER['DEFAULT']['STATS_FILE']` exists.
- [ ] Wagtail pages & templates:
  - [ ] List page models and ensure templates referenced exist.
  - [ ] Confirm Wagtail image and docs settings align with media paths.
- [ ] Authentication flows (allauth or custom): confirm `INSTALLED_APPS` contains auth apps, check `ACCOUNT_*` settings, and run a register/login smoke test.
- [ ] Email sending: verify `EMAIL_BACKEND`/SMTP settings in ENV and send a sample email (or check queueing if using Celery/RQ).
- [ ] Dependency checks: run `pip check`, `pipdeptree` in the venv; ensure no conflicting versions or duplicate package trees.
- [ ] Minimal safe reorganizations only:
  - [ ] Remove deprecated shim modules (e.g., `www/conf.py`), consolidate imports to `configs` package.
  - [ ] Do NOT move or rename apps, models, or templates unless required; document any file moves.
- [ ] Tests & smoke: run `python manage.py check` and `pytest tests/ci --ds=configs.settings` and record failures.
- [ ] Produce `Results` section below with findings, actions taken, and recommended remediation prioritized.

## Commands

```bash
cd /root/site/websites
# Frontend
npm ci
npm run build:ctc
npm run build:structa

# Django assets
PROJECT_PATH=ctc-research.com python manage.py build_assets --no-input
PROJECT_PATH=structa.cloud python manage.py build_assets --no-input

# Validate
python manage.py check --settings=configs.settings
python manage.py collectstatic --no-input --settings=configs.settings
python -m pytest tests/ci -q --ds=configs.settings
```

## Results

- Record outputs and fixes here after running checks.

## Notes / Constraints
- This plan emphasizes safe reorganization: prefer fixing import paths, removing small deprecated shim files, updating `configs`, and documenting changes. Avoid large structural refactors in this pass.
