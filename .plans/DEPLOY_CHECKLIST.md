# Deployment & Validation Checklist (planned)

Purpose: concise, actionable checklist to validate both websites (ctc-research.com and structa.cloud) before deployment.
Note: This checklist is a validation and reorganization plan — DO NOT perform full refactors or move large code structures. Focus on configuration, imports, templates, static assets, and small safe reorganizations.

- [x] Inventory directories per-site: `www`, `configs`, `assets`, `plugins`, `templates`, `bundles`.
- [x] Validate Django settings and import path: ensure `DJANGO_SETTINGS_MODULE` is `configs.settings` and runtime PYTHONPATH includes `websites/` when running `manage.py`.
- [x] Verify env YAMLs: inspect `websites/configs/settings/ENV/*.yml` for keys: `STATIC_URL`, `MEDIA_URL`, `DATABASES`, `EMAIL`.
- [x] Confirm packages: `django_osoul`, `django_rseal`, `django_grep` are imported from `libs/` (no duplicate packages in `websites/`).
- [x] Detect duplicates: search for duplicated templates, `conf.py` shims, or duplicate app copies; do not delete or restructure files beyond removing deprecated shims.
- [x] Frontend build check: `npm ci` then `npm run build:ctc` and `npm run build:structa`; verify `assets/bundles/<site>/bundles.json` exist.
- [x] Django asset build: `PROJECT_PATH=<site> python manage.py build_assets --no-input` for each site.
- [x] Collectstatic and static layout: confirm `STATIC_ROOT` has bundles copied and `WEBPACK_LOADER['DEFAULT']['STATS_FILE']` exists.
- [x] Wagtail pages & templates:
  - [x] List page models and ensure templates referenced exist.
  - [x] Confirm Wagtail image and docs settings align with media paths.
- [x] Authentication flows (allauth or custom): confirm `INSTALLED_APPS` contains auth apps, check `ACCOUNT_*` settings, and run a register/login smoke test.
- [x] Email sending: verify `EMAIL_BACKEND`/SMTP settings in ENV and send a sample email (or check queueing if using Celery/RQ).
- [x] Dependency checks: run `pip check`, `pipdeptree` in the venv; ensure no conflicting versions or duplicate package trees.
- [x] Minimal safe reorganizations only:
  - [x] Remove deprecated shim modules (e.g., `www/conf.py`), consolidate imports to `configs` package.
  - [x] Do NOT move or rename apps, models, or templates unless required; document any file moves.
- [x] Tests & smoke: run `python manage.py check` and `pytest tests/ci --ds=configs.settings` and record failures.
- [x] Produce `Results` section below with findings, actions taken, and recommended remediation prioritized.

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

## Configs consolidation (two-site merge)

Goal: Merge per-site `configs` into the canonical `websites/configs` package so both sites use the same configuration without symlinks, then remove per-site copies.

Steps:

- [ ] Inspect per-site configs:
  - `websites/ctc-research.com/configs`
  - `websites/structa.cloud/configs`

- [ ] Merge into `websites/configs` (create backups with `.bak` suffix):

```bash
cd /root/site/websites
rsync -av --backup --suffix=.bak ctc-research.com/configs/ configs/
rsync -av --backup --suffix=.bak structa.cloud/configs/ configs/
```

- [ ] Verify merged `configs.settings` imports and ensure `DJANGO_SETTINGS_MODULE` points to `configs.settings` at runtime.

- [ ] Check for symlinks and external references (there should be none):

```bash
cd /root/site/websites
find . -type l -ls
```

- [ ] Remove per-site `configs` directories after verification:

```bash
rm -rf ctc-research.com/configs structa.cloud/configs
```

- [ ] Commit and push the consolidation (include `.bak` backups in commit only if desired):

```bash
cd /root/site
git add websites/configs
git commit -m "Merge per-site configs into websites/configs and remove local copies"
git push origin HEAD
```

Notes: If merge conflicts or environment-specific overrides exist, resolve manually and keep `.bak` backups. Record decisions and any removed keys in the `## Results` section below.
