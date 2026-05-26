# Undone Tasks (Defined Remaining Work)

## A) Critical Fixes
- [ ] Ensure `django_grep` is available in the active runtime environment (fix import path/dependency).
- [ ] Fix missing `ROOT_URLCONF` in active settings profile used by both sites.
- [ ] Re-run URL wiring validation (`reverse('wagtailadmin_home')`, `reverse('wagtaildocs:index')`, `reverse('admin:index')`).

## B) Environment
- [ ] Run `make check-package-installs` until all internal packages are importable.
- [ ] Run `uv sync` in network-enabled environment.
- [ ] Install pytest in `.venv` (currently blocked by proxy/network restrictions).

## C) Website Validation Completion
- [ ] Validate Wagtail/Admin/Documents URL wiring for `ctc-research.com` after ROOT_URLCONF fix.
- [ ] Validate Wagtail/Admin/Documents URL wiring for `structa.cloud` after ROOT_URLCONF fix.
- [ ] Validate static root + bundle output paths for both websites.

## D) Alliance-Specific Completion (`structa.cloud`)
- [ ] Run Alliance targeted test:
  - `.venv/bin/python -m pytest -q structa.cloud/tests/email/test_django_rseal_integration.py`
- [ ] Validate Alliance URLs/views/services imports through test execution.

## E) Cross-Site Safety
- [ ] Validate no static/bundle path collisions between websites.
- [ ] Validate template lookup precedence across both websites.

## F) Final Readiness
- [ ] Update checklist and verification log after reruns.
- [ ] Mark final state PASS or BLOCKED with exact failing step number.
