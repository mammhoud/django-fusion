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

### Hygiene fixes

Hygiene fixes are repo-internal changes that **do not affect the
published `action.yml`** — e.g. fixing a cosmetic bug in the repo's
own `make verify-release` Makefile target, updating the companion
`deploy-ci.yml` workflow, or amending this README. Hygiene is **not**
a SemVer bump.

**Default: no tag.** Land hygiene commits as ordinary commits on the
default branch with a `### Hygiene` sub-section in `CHANGELOG.md` (not
a top-level `## [vX.Y.Z]` header — those are reserved for SemVer
releases). The fix is implicitly carried by the next real SemVer
bump of the same line. `uses: ...@v1` skips hygiene entirely and
behaves identically to the prior real SemVer release.

**Why not a `vX.Y.Z+hyg.N` SemVer build-metadata tag by default?**
SemVer build metadata (the `+suffix` suffix per the [v2.0.0
spec](https://semver.org/#spec-item-10)) does not change version
precedence — `v1.0.0` and `v1.0.0+hyg.1` are precedence-equal, and
the spec was designed with exactly this use case in mind. Major
tooling (Renovate, Dependabot, npm semver) handles `+suffix` correctly
out of the box per the spec. The reason we still prefer "no tag" by
default is **cognitive overhead, not tool compatibility**: for an
action this small (one input pair, ~30 lines of `action.yml`), the
parallel naming axis buys policy clarity at the cost of forcing
every reader to mentally check the build-metadata suffix on every
`git tag --list` and `CHANGELOG` entry. The trade-off flips if the
action grows to a size where hygiene events become more interesting
than release events.

**Hygiene CHANGELOG entry shape.** Hygiene commits append a
`### Hygiene` block at the top of `CHANGELOG.md` (above the
top-level `## [vX.Y.Z]` SemVer-release headers, which remain the
canonical record for SemVer bumps). The shape:

```markdown
### Hygiene

- **2024-XX-YY** — short one-line title (matches the commit subject).
  One short paragraph describing what changed and why it doesn't
  affect the published `action.yml` (e.g. "Fix `\\u274c` rendering
  in the repo's `make verify-release` diagnostic output; published
  `action.yml` is unchanged").
- **earlier-date** — next hygiene entry, same shape.
```

> **Tip:** prefix hygiene commit subjects with `hyg:` (no space before
> description, mirroring the repo's existing Conventional-Commits
> prefix style) so `git log --grep='^hyg:'` recovers them in bulk.
> Example forward-looking subject:
> `hyg: clarify verify-release success-path output wording`.

**Exception — pointer tags.** If a hygiene fix needs a permanent
citation (third-party issue, ticket reference, audit trail), promote
it to a real SemVer PATCH bump with an explicit "no consumer-visible
behavior change" note in the `### Notes` block. The precedent is
`v1.0.1`, which recorded a one-line `Makefile` formatting fix; future
hygiene-to-pointer promotions follow the same shape.

### Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a per-version history of
behavior changes, additions, bug fixes, and hygiene entries.

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
