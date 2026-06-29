# Changelog

All notable changes to this Composite Action are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [v1.0.1] — fix makefile verify-release ❌ rendering

### Fixed

- `make verify-release` no longer prints a literal `\u274c` text
  string when the tag is missing on origin — the diagnostic echo
  line now uses raw UTF-8 ❌ to match the existing 🛡️ convention
  on the `deploy-ci` recipe. This was an oversight from the v1.0.0
  publish cleanup: one of the byte-escape-to-UTF8 anchors in the
  multi-line replace didn't match the actual byte layout, leaving
  a single `\u274c` literal in the file. The unfixed output would
  have made the missing-tag failure mode invisible in `make -n`
  dry-run review of CI logs (cosmetic only: the recipe still exits
  1 on a missing tag and the verify-release smoke still surfaces
  genuine deploy-ci failures).

### Notes

- The **published `action.yml`** is byte-identical between `v1.0.0`
  and `v1.0.1`; this patch bumps the tag purely to record the
  post-publish hygiene fix in repo-internal release-verification
  tooling. Consumers resolving `@v1` will now land on `v1.0.1`;
  consumers pinned at `@v1.0.0` continue to resolve the pre-fix
  commit (no behaviour difference for them — they get the same
  action.yml either way).

## [v1.0.0] — initial public release

### Features

- **`make-target` input** (default `deploy-ci`): the Make target to
  invoke. Callers who use a different preflight convention (e.g.
  `lint-deploy`) can swap the target without forking the action.
- **`working-directory` input** (default `.`): path relative to repo
  root where the Makefile lives. Lets monorepo callers whose Makefile
  lives under `infra/`, `apps/`, etc. point at it directly.
- **Built-in `docker version` precheck**: fails fast with a clear
  error on a missing/unreachable Docker daemon rather than masking
  the failure inside the Makefile's `check-docker` probe.

### Internals

- Composite Action type (`runs.using: 'composite'`).
- Two `shell: bash` steps, both inheriting `working-directory`.
- Companion workflow `.github/workflows/deploy-ci.yml` ships as the
  canonical in-repo wiring example (path-scoped PR/push lint).
