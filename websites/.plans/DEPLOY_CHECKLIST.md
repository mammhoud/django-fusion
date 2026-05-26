# Deployment Checklist (Defined Steps)

## Step 1 — Preconditions
- [ ] `uv sync`
- [x] Confirm `configs/settings/ENV/*.yml` exists and is readable.
- [x] Confirm root Make targets exist: `check`, `validate-config`, `build-assets`, `audit-config`, `check-paths`, `check-sites`, `check-alliance`.

## Step 2 — Root Validation
- [x] `make show-package-sources`
- [ ] `make check-package-installs`
- [x] `make audit-config`
- [x] `make validate-config`
- [x] `make check`
- [x] `make build-assets`

## Step 3 — Website Validation: `ctc-research.com`
- [x] `cd ctc-research.com && ../.venv/bin/python manage.py check`
- [ ] Verify Wagtail/Admin/Documents URL wiring. *(blocked now by missing `django_grep` package in current env for direct import check)*
- [ ] Verify static/bundle outputs are site-correct.

## Step 4 — Website Validation: `structa.cloud` (Alliance)
- [x] `cd structa.cloud && ../.venv/bin/python manage.py check`
- [x] Verify Alliance wiring under `structa.cloud/plugins/` (import/config-level validation).
- [ ] Verify Alliance URL/view/service imports resolve via targeted tests. *(blocked: pytest unavailable)*
- [ ] Verify static/bundle outputs are site-correct.

## Step 5 — Regression/Conflict Validation
- [ ] `make populate-data`
- [ ] Validate no cross-site static root or bundle path collisions.
- [ ] Validate template lookup order is deterministic across both sites.
- [ ] Run targeted tests for deployment-critical paths.

## Step 6 — Finalization
- [x] Update `PLANS_VERIFICATION.md` with done/error states.
- [ ] Close completed items in `UNDONE_TASKS.md`.
- [ ] Mark deployment readiness state: PASS / BLOCKED.
