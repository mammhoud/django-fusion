# Community Version — Standalone Public Repo (`formint-community`)

**Goal:** Ship the Community edition as a standalone open-source repo at
`github.com/mammhoud/formint-community`, renamed **Formints Community**, with
CI, a release pipeline, and the landing site pointing at it — while keeping
`formint-community/` the single canonical source.

> **Status:** The code side is complete (bundle generator + rename contract,
> landing seed sync, uniform commands). Remaining work is the GitHub publish
> checklist (C4) and the two re-run verification gates (C6.4–C6.5).

## Task C4: Publish to GitHub — external, pending

> **Prepared locally only.** These are manual GitHub operations only the
> repository owner can perform (create repo, push, metadata, health files,
> first release). Everything local — bundle generator, rename contract, landing
> seed — is complete and verified.

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
  desktop point of sale (Tauri 2 + Rust/Diesel + React 19)”, topics `pos`,
  `tauri`, `rust`, `react`, `sqlite`, website `https://structa.cloud`.
- [ ] **Step 4: Community health files** — add `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md` (AGPL-3.0 project), GitHub issue
  templates. (Optional but recommended for the public repo.)
- [ ] **Step 5: First release** — tag `v0.1.0`; the `release.yml` workflow
  builds `.dmg`/`.msi`/`.AppImage` + deb/rpm and attaches them. Verify the
  workflow's `TAURI_SIGNING_PRIVATE_KEY` secrets are configured for
  auto-updates (or remove updater config until ready).

## Task C6: Verification gates (re-run only at tagging time)

- [ ] **Step 4:** Bundle smoke — regenerate with `make community-bundle`, then
  in `formint-community/` run `pnpm install` + `pnpm test` + `cargo test` to
  prove the standalone package is self-sufficient. (Bundle already verified
  8.8 MB in C1; re-run only at tagging time.)
- [ ] **Step 5:** Landing seed — re-seed a dev landing DB and confirm the
  Formints Community card CTA points at `mammhoud/formint-community` **and**
  the `badge-offer` chip renders "Offline-first · open source" on the home
  product card and the edition card. (Seed + backend tests verified in C2;
  re-run only at tagging time.)
