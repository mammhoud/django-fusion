# Community Version — Standalone Public Repo (`formint-community`)

> **For agentic workers:** Execute tasks in order. Most of the code work is
> done; the remaining tasks are the publish checklist and verification gates.

**Goal:** Ship the Community edition (`formintA/`) as a standalone open-source
repo at `github.com/mammhoud/formint-community`, renamed to **Formints
Community**, with CI, a release pipeline, and the landing site pointing at it —
while keeping `formintA/` the single canonical source.

**Status (9 Aug 2026):** Community plan `01-community.md` tasks A1–A5 complete
(Rust `refund_sale`, refund UI, offline-first banner, e2e, docs note). The
bundle generator, rename, and landing seed update are implemented. Remaining
tasks are the GitHub publish checklist (C4–C6).

## Rename contract (hard)

| Field | In-repo (`formintA/`) | Community version |
|-------|-----------------------|-------------------|
| Repo | `projects/formints/formintA/` | `github.com/mammhoud/formint-community` |
| Package name | `formint-pos` | `formint-community` |
| Tauri product | `Formint` | `Formints Community` |
| Tauri identifier | `com.mammhoud.pos` | `com.mammhoud.formint-community` |
| Window title | `Formint` | `Formints Community` |
| Release artifacts | `pos-ko_*` | `formint-community_*` |
| License | AGPL-3.0 | AGPL-3.0 (unchanged) |

## Architecture

```
formintA/ (canonical Community source)
   │  make community-bundle
   ▼
scripts/publish/community-bundle.cjs
   │  fs.cpSync with segment exclusions (node_modules, target, dist, gen,
   │  screenshots, .venv, dbs, logs) + rename patches + workflows
   ▼
formint-community/  (standalone package — git init + push to GitHub)
   ├── README.md            standalone (no ../monorepo links)
   ├── COMMUNITY.md         generated marker + rename table
   ├── .gitignore           standalone ignores
   ├── .github/workflows/   i18n, visual-regression, release (artifacts renamed)
   └── src-tauri/tauri.conf.json  productName Formints Community, id com.mammhoud.formint-community
```

## Task C1: Bundle generator — **done**

`scripts/publish/community-bundle.cjs` + `make community-bundle` / `make
community-version` in `projects/formints/Makefile`.

- [x] Copy `formintA/` → `formint-community/` excluding generated dirs by path
      segment (`node_modules`, `dist`, `target`, `gen`, `screenshots`, `.astro`,
      `test-results`, `playwright-report`, `.venv`, `.git`, `.DS_Store`) and
      files (`restaurant.db*`, `appmap.log`, `.env`).
- [x] Rename `package.json` name → `formint-community` (+ repository/homepage).
- [x] Rename `tauri.conf.json` → productName **Formints Community**, identifier
      **com.mammhoud.formint-community**, window title, bundle descriptions.
- [x] Rename `Cargo.toml` package/productName refs.
- [x] Patch `.github/workflows/*.yml` artifact names `pos-ko_*` →
      `formint-community_*`.
- [x] Write standalone `README.md`, `.gitignore`, `COMMUNITY.md` marker.
- [x] Verify: bundle is 8.8 MB, no `target`/`node_modules`/`dist` inside.

## Task C2: Landing seed sync — **done**

- [x] `seed_pages.py`: all four `github.com/mammhoud/formint-pos` links →
      `github.com/mammhoud/formint-community` (hero repo CTA, Community edition
      card CTA, “View on GitHub”, team-card link).
- [x] Verified no remaining `mammhoud/formint-pos` refs in landing backend; no
      test asserts the old URL.

## Task C3: Uniform commands — **done**

- [x] `projects/formints/Makefile` v4.0: uniform `-install/-check/-test/-run/-stop/-clean`
      per edition (community/standard/pro/cloud/client/sdk) + `test-all` +
      `community-bundle`.
- [x] `formintC/Makefile`: added missing `test` target (oxlint + vue-tsc).
- [x] `projects/Makefile`: `website-formints` / `website-pos` delegation.

## Task C4: Publish to GitHub

- [ ] **Step 1: Create the repo** — new public repo `mammhoud/formint-community`
      (AGPL-3.0 license template).
- [ ] **Step 2: Initialize + push**
  ```bash
  cd projects/formints/formint-community
  git init
  git add .
  git commit -m "feat: Formints Community — offline-first open-source POS (from structa.cloud monorepo)"
  git branch -M main
  git remote add origin https://github.com/mammhoud/formint-community.git
  git push -u origin main
  ```
- [ ] **Step 3: Enable repo metadata** — description “Free, offline-first
      desktop point of sale (Tauri 2 + Rust/Diesel + React 19)”, topics
      `pos`, `tauri`, `rust`, `react`, `sqlite`, website `https://structa.cloud`.
- [ ] **Step 4: Community health files** — add `CONTRIBUTING.md`,
      `CODE_OF_CONDUCT.md`, `SECURITY.md` (AGPL-3.0 project), GitHub issue
      templates. (Optional but recommended for the public repo.)
- [ ] **Step 5: First release** — tag `v0.1.0`; the `release.yml` workflow
      builds `.dmg`/`.msi`/`.AppImage` + deb/rpm and attaches them. Verify the
      workflow's `TAURI_SIGNING_PRIVATE_KEY` secrets are configured for
      auto-updates (or remove updater config until ready).

## Task C5: Docs & changelog sync

- [ ] **Step 1:** In `docs/architecture/editions.md`, the standalone note row is
      already present — keep it accurate after any rename drift.
- [ ] **Step 2:** Update `projects/formints/CHANGELOG.md` with a Community
      version entry (bundle generator, rename contract, landing sync).
- [ ] **Step 3:** Link the community repo from the landing “View on GitHub”
      routes (already the seed) and from `projects/formints/README.md` if it
      lists edition links.

## Task C6: Verification gates (run before tagging)

- [ ] **Step 1:** Community unit tests — `cd projects/formints/formintA && pnpm test`
- [ ] **Step 2:** Rust tests — `cd formintA/src-tauri && cargo test`
- [ ] **Step 3:** e2e — `cd formintA && pnpm test:e2e` (refund spec included)
- [ ] **Step 4:** Bundle smoke — regenerate with `make community-bundle`, then in
      `formint-community/` run `pnpm install` + `pnpm test` + `cargo test` to
      prove the standalone package is self-sufficient.
- [ ] **Step 5:** Landing seed — re-seed a dev landing DB and confirm the
      Formints Community card CTA points at `mammhoud/formint-community`.

## Self-Review

1. **Single source of truth:** all feature changes land in `formintA/`; the
   bundle is generated, never hand-edited (`COMMUNITY.md` marker enforces this).
2. **No monorepo leakage:** generated dirs are excluded by path segment, so the
   public repo never contains `node_modules`, cargo `target`, DBs, or logs.
3. **Rename completeness:** package/product/identifier/title/artifacts all
   covered; README is standalone (no `../landing-fusion/...` relative links).
4. **Back-compat:** legacy `formint-*`/`mini-*`/`server-*`/`cloud-*` make
   aliases still resolve to the right editions.

## Execution Handoff

**Recommended:** run C4–C6 inline (publish steps are manual GitHub operations
that only the repo owner can perform); C6 verification can be run by a
subagent. The code side (C1–C3) is complete and verified.
