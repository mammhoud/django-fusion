# Deploy Preflight Composite Action

Runs the project-level preflight gate (`make deploy-ci` by default) as a CI
lint step. Exits non-zero on any preflight failure so misconfig surfaces as
a CI lint failure rather than a mid-deploy abort.

The action wraps three phases shipped in the repo's `Makefile`:

1. `check-docker` — confirms the Docker daemon is reachable.
2. `preflight-network` — lints the `$(NETWORKS)` list against Docker's
   network-name identifier spec (`^[a-zA-Z0-9][a-zA-Z0-9_.-]*$`).
3. `deploy-preflight` — validates `DEPLOY_ORDER` against
   `VALID_DEPLOY_ORDERS` + parses the compose files listed in
   `PREFLIGHT_COMPOSE_FILES`.

`deploy-ci` chains the latter two gates; all three run inside a single
`make` invocation so transitive `validate-deploy-order` and
`create-networks` dependencies are visited exactly once via Make's
prereq dedup.

## Inputs

| Name                | Required | Default      | Description                                                                                |
|---------------------|----------|--------------|--------------------------------------------------------------------------------------------|
| `make-target`       | No       | `deploy-ci`  | The Make target to invoke. Callers with their own convention (e.g. `lint-deploy`) can swap. |
| `working-directory` | No       | `.`          | Path (relative to repo root) where the Makefile lives. Useful for monorepos whose Makefile lives in `infra/`, `apps/`, etc. |

## Required preconditions

- A `Makefile` defining a target matching the `make-target` input,
  located at the `working-directory` input (default: repo root). The
  `make-target` default `deploy-ci` works out of the box for any repo
  that adopts the same conventions used in `structa.cloud/Makefile`.
- A reachable `docker` daemon. The action runs `docker version` up
  front so a missing daemon fails immediately with a clear error
  rather than masked inside the Makefile's `check-docker` probe.

## Usage

```yaml
- uses: actions/checkout@v4

# Default: runs `make deploy-ci` from the repo root.
- uses: ./.github/actions/deploy-preflight

# Custom target: runs whatever the caller named.
- uses: ./.github/actions/deploy-preflight
  with:
    make-target: lint-deploy

# Non-root Makefile: point at e.g. infra/Makefile.
- uses: ./.github/actions/deploy-preflight
  with:
    working-directory: infra
```

## Releases

This action follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).
Tags are created on the default branch only; the latest tag within `vMAJOR`
floats when a new `vMAJOR.x.y` is pushed (GitHub's standard floated-major
convention).

### Pinning strategies

```yaml
# Pinned to an exact tag - safest, no surprise major-version bumps.
- uses: your-org/deploy-preflight@v1.0.0

# Floated on a major version - picks up the latest v1.x.y patches
# automatically without ever jumping to v2. Use when you trust the
# maintainer to keep v1.x backward-compatible.
- uses: your-org/deploy-preflight@v1

# Local path - bypasses the published tag entirely. Used by
# `.github/workflows/deploy-ci.yml` in this repo's own lint workflow.
- uses: ./.github/actions/deploy-preflight
```

### Upgrade + breaking-change policy

- **Patch version (v1.0.x)**: bug fixes, dependency bumps, internal
  refactors. **No behavior change** for callers. Auto-safe to take
  on float.
- **Minor version (v1.x.0)**: **backward-compatible** additions -
  new optional inputs, new diagnostic output. Existing inputs and
  behavior stay unchanged. Auto-safe to take on float.
- **Major version (vX.0.0)**: **breaking changes** - input renames,
  input removals, behavior changes to existing inputs, removal of
  default values callers relied on. Pin to a specific tag and review
  the CHANGELOG entry before bumping.

### Tagging convention

- Tags are created on the default branch at the head of the action
  directory. GitHub resolves `your-org/deploy-preflight@v1` to the
  latest `v1.x.y` tag.
- Always annotate: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`. Annotated
  tags surface in the GitHub Releases UI and in `git show vX.Y.Z`.
- Any README / CHANGELOG updates MUST land on the tagged commit so
  the docs match the released code (no "the docs say v1.1 but the
  code is v1.0" drift).

### Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a per-version history of
behavior changes, additions, and bug fixes.

## Why a Composite Action?

The preflight gates (`check-docker`, `preflight-network`,
`deploy-preflight`) are the project-level source of truth for
"safe to deploy". Wrapping them as a Composite Action means every repo
in this workspace — and external repos adopting the same conventions —
can drop in `uses: ./deploy-preflight` with a single line instead of
duplicating the 3-step inline workflow.

## Companion lint workflow

The repo also ships `.github/workflows/deploy-ci.yml` which calls this
action as a path-scoped lint job (PR / push / manual dispatch). It
serves as the canonical, in-repo wiring example for the action.
