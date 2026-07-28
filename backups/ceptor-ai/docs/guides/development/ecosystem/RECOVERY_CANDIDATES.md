# Recovery Candidates

Generated: 2026-04-16 09:21:30

## Summary

- Total deleted Python files scanned: 1034
- **High priority** (still referenced — would cause ImportError): 1
- Medium priority (important logic, not currently imported): 147
- Low priority (replaced by new architecture): 886

## High Priority — Still Referenced (Action Required)

These files are still imported somewhere in the current codebase.
Leaving them missing will cause `ImportError` at runtime.

### `ctc-research.com/apps/pages/tasks.py`

- **Deleted commit**: `d68807b55483c777c349df2bbb0115280ce4761b`
- **Deleted date**: 2025-12-07 22:56:45 +0200
- **References found** (2):
  - `/root/site/structa.cloud/apps/pages/signals/user.py`
  - `/root/site/ctc-research.com/apps/pages/signals/user.py`

## Medium Priority — Important Logic (Review Recommended)

These files contained business logic (services, managers, etc.) but are
not currently imported. They may have been intentionally replaced.

- `ctc-research.com/apps/LMS/_managers/course.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/LMS/_managers/enrollment.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/LMS/_managers/lesson.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/LMS/_services/course.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/LMS/_services/enrollment.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/handlers/management/commands/sync_xellent.py` (deleted: 2026-03-29)
- `ctc-research.com/apps/handlers/managers/profile.py` (deleted: 2025-12-11)
- `ctc-research.com/apps/handlers/models/forms/submission.py` (deleted: 2026-04-14)
- `ctc-research.com/apps/handlers/models/manage/tags.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/handlers/models/profiles/contact.py` (deleted: 2025-12-14)
- `ctc-research.com/apps/handlers/models/profiles/person.py` (deleted: 2025-12-13)
- `ctc-research.com/apps/handlers/models/profiles/profile.py` (deleted: 2025-12-11)
- `ctc-research.com/apps/handlers/models/profiles/setting.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/handlers/services/_userSelector.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/handlers/services/user.py` (deleted: 2025-12-12)
- `ctc-research.com/apps/handlers/site/mixins.py` (deleted: 2026-04-14)
- `ctc-research.com/apps/handlers/wagtail_hooks.py` (deleted: 2026-02-18)
- `ctc-research.com/apps/module/_managers/peoples.py` (deleted: 2025-12-07)
- `ctc-research.com/apps/module/_managers/user.py` (deleted: 2025-12-09)
- `ctc-research.com/apps/module/_services/token.py` (deleted: 2025-12-07)
- `ctc-research.com/apps/pages/backends/adapters.py` (deleted: 2025-10-24)
- `ctc-research.com/projects/CI/services/payments.py` (deleted: 2026-02-28)
- `ctc-research.com/projects/EXT/_managers/token.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/_managers/user.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/_services/token.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/payloads/adapters/account.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/payloads/adapters/social.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/payloads/managers/base.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/payloads/managers/cache.py` (deleted: 2025-12-11)
- `ctc-research.com/projects/EXT/payloads/managers/manager.py` (deleted: 2025-12-11)
- _(and 117 more — see full list below)_

## Low Priority — Replaced by New Architecture

There are 886 low-priority deleted files (migrations, `__init__.py`,
old app structure files). These were intentionally removed as part of the
architectural refactoring and do not need recovery.

## Recovery Instructions

For each high-priority file, run:
```bash
python scripts/recover_code.py recover <original_path> <target_path>
```

Example:
```bash
python scripts/recover_code.py recover \
  ctc-research.com/apps/handlers/managers/profile.py \
  ctc-research.com/apps/accounts/managers/profile.py
```