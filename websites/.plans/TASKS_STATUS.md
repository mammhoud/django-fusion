# Tasks Status Board

## Done
- Removed deprecated `www/conf.py` from both sites.
- Added root validation commands in `Makefile` (`check-paths`, `check-sites`, `check-alliance`, package source/install checks).
- Verified path checks and site-level Django checks pass.
- Consolidated notification trigger usage by removing duplicate function in registration view and using shared service helper.

## In Progress
- Package installation validation for GitHub sources (`django-grep`, `django-osoul`, `django-rseal`) in active environment.
- URL deep import verification requiring package availability.

## Archived
- Legacy shim compatibility strategy (`www/conf.py`) is archived/retired.

## Blocked
- `make check-package-installs` fails until internal packages are installed.
- Alliance pytest task blocked until `pytest` is installable in environment.
