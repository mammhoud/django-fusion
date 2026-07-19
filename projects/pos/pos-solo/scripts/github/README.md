# scripts/github/ — GitHub CI Utilities

Scripts used exclusively in **GitHub Actions workflows** and related CI/CD automation.

## Contents

| Script | Purpose | Used by |
|--------|---------|---------|
| `diff-i18n.cjs` | Compare translation gaps between PR base and head branches | `.github/workflows/i18n.yml` |
| `encode-keystore-for-github.sh` | Base64-encode Android keystore for GitHub Secrets | manual (release setup) |

## Enhancement Ideas

- **`release-draft.cjs`** — auto-generate GitHub Release draft from `CHANGELOG.md`
- **`notarize-macos.sh`** — notarize macOS builds for Apple's Gatekeeper
- **`sign-windows.ps1`** — sign Windows MSI/EXE with a code-signing certificate
- **`release-upload.cjs`** — upload all platform artifacts to a GitHub Release via `gh` CLI
- **`pr-labeler.cjs`** — auto-label PRs based on changed files (frontend/backend/docs)
