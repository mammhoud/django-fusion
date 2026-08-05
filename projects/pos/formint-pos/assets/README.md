# Formint Shared Assets

This directory is the single source for Formint images, icons, fonts, styles, scripts, static files, manifests, and representative fixtures.

## Rules

- Keep one canonical source file per image, icon, and font.
- Keep licenses and attribution beside third-party fonts or imagery.
- Frontend imports source assets through stable aliases such as `@assets/images` and `@assets/styles`.
- Backend may collect or expose `static/` and a generated manifest, but does not own page layout markup.
- Do not store secrets, databases, dependency directories, or compiled build output here.
- Do not remove an asset until usage search and visual tests pass.

## Planned directories

```text
images/ icons/ fonts/ styles/ scripts/ static/ manifests/ fixtures/
```

Phase 1 starts with the contract only; assets are migrated in small, verified families from the preserved POS sources.
