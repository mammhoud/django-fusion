# Analyzer test fixtures

## `page_card_grid.html`

A real, unmodified fragment used by `tests/analyzer/test_views.py`'s
`TestAnalyzeViewEndToEnd` to feed the analyzer genuine consumer markup rather
than a synthetic snippet.

- **Upstream:** `projects/CMS/templates/fragments/page_card_grid.html`
- **Copied:** 2026-09-28, byte-for-byte (no edits)

The copy exists so the test runs in a standalone `django-fusion` checkout. The
original fixture walked up the directory tree looking for a
`customizer/templates/fragments/` path, which no longer exists after the CMS
project was reorganized — so the end-to-end test silently skipped everywhere.

If the upstream fragment changes in a way that matters to the analyzer,
re-copy it and note the date here.
