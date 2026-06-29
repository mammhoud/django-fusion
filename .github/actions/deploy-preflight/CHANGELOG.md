# Changelog

All notable changes to this Composite Action are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/)
and this project adheres to [Semantic Versioning](https://semver.org/).

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
