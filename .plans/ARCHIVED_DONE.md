# Archived Completed Items

- Removed deprecated `www/conf.py` shims from both websites.
- Added root operational checks in `Makefile`.
- Added phased plan docs under `websites/.plans/`.
- Consolidated notification trigger helper to shared service implementation.
- Added fixture split files:
  - `tests/fixtures/models_fixture.json`
  - `tests/fixtures/dumped_data_fixture.json`
- Added data populator entry script:
  - `tests/data_populator.py`
- Dev server startup confirmed with sqlite-oriented fallback settings and guarded URL imports.
