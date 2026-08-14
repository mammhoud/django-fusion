# Community Version — Standalone Public Repo (`formint-community`)

> **For agentic workers:** Execute tasks in order. Most of the code work is
> done; the remaining tasks are the publish checklist and verification gates.

**Goal:** Ship the Community edition (`formint-community/`) as a standalone open-source
repo at `github.com/mammhoud/formint-community`, renamed to **Formints
Community**, with CI, a release pipeline, and the landing site pointing at it —
while keeping `formint-community/` the single canonical source.

**Status (9 Aug 2026):** Community plan `01-community.md` tasks A1–A5 complete
(Rust `refund_sale`, refund UI, offline-first banner, e2e, docs note). The
bundle generator, rename, and landing seed update are implemented — including
the **offline-first badge** (`offer_label: "Offline-first · open source"`) and
**refund flow** (see [Shipped surface](#shipped-surface) below). Remaining tasks
are the GitHub publish checklist (C4–C6).

## Shipped surface

### Offline-first badge

- Landing seed (`seed_pages.py`): the Community edition carries
  `offer_label: "Offline-first · open source"`, rendered as a `badge-offer`
  chip on the edition card (`/products/formint-pos/`) **and** on the home page
  product card (`index.astro` derives it from the first offer-bearing
  edition).
- In-app: `useOfflineMode` hook surfaces the offline state as a calm top
  banner ("Offline mode — data stays on this device") whenever the OS reports
  the device offline.
- Verified: landing backend tests assert the badge text, the capability cards,
  and the API `offer_label`; the home page HTML renders the `badge-offer` chip.

### Refund flow

- **UI:** Transactions → a completed sale exposes **Refund** → confirm dialog
  (`refundTarget` / `refunding` state) → `invoke('refund_sale', { saleId })` →
  local state flips the row to `Refunded` (no stale reload) + toast feedback.
- **Rust:** `sales::refund_sale` (`src-tauri/src/operations/sales.rs`) marks
  `sales.status = "refunded"`. Only `completed` sales; idempotent (a second
  refund on the same sale errors "already refunded"); missing sales error.
- **Coverage:** Rust unit tests (`refund_sale_*`), `Transactions.test.tsx`,
  and `e2e/refund.spec.ts` (shipped in the bundle).

## Rename contract (hard)

| Field | In-repo (`formint-community/`) | Community version |
|-------|-----------------------|-------------------|
| Repo | `projects/formints/formint-community/` | `github.com/mammhoud/formint-community` |
| Package name | `formint-pos` | `formint-community` |
| Tauri product | `Formint` | `Formints Community` |
| Tauri identifier | `com.mammhoud.pos` | `com.mammhoud.formint-community` |
| Window title | `Formint` | `Formints Community` |
| Release artifacts | `pos-ko_*` | `formint-community_*` |
| License | AGPL-3.0 | AGPL-3.0 (unchanged) |

## Architecture

```
formint-community/ (canonical Community source)
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

- [x] Copy `formint-community/` → `formint-community/` excluding generated dirs by path
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
- [x] Community edition carries the **offline-first badge**
      (`offer_label: "Offline-first · open source"`) — `badge-offer` chip on
      the edition card **and** the home page product card (data-driven from
      the first offer-bearing edition).
- [x] “What Formints POS ships” capability cards include **Offline-first mode**
      and **Refunds & returns** (feature grid + edition bullets + comparison
      table all cover both).
- [x] Verified no remaining `mammhoud/formint-pos` refs in landing backend; no
      test asserts the old URL.

## Task C3: Uniform commands — **done**

- [x] `projects/formints/Makefile` v4.0: uniform `-install/-check/-test/-run/-stop/-clean`
      per edition (community/standard/pro/cloud/client/sdk) + `test-all` +
      `community-bundle`.
- [x] `formintC/Makefile`: added missing `test` target (oxlint + vue-tsc).
- [x] `projects/Makefile`: `website-formints` / `website-pos` delegation.

## Task C4: Publish to GitHub — **external, pending**

> **Prepared locally only.** These steps are manual GitHub operations that only
> the repository owner can perform (create repo, push, metadata, health files,
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

- [x] **Step 1:** `projects/formints/docs/architecture/editions.md` — the
      standalone note row is present and kept accurate.
- [x] **Step 2:** `projects/formints/CHANGELOG.md` — Community version entry
      added (bundle generator, rename contract, landing sync).
- [x] **Step 3:** Landing “View on GitHub” routes point at
      `mammhoud/formint-community` (already the seed); `projects/formints/README.md`
      edition links are documented.

## Task C6: Verification gates (run before tagging)

- [x] **Step 1:** Community unit tests — 43 files, 427 passed (1 skipped).
- [x] **Step 2:** Rust tests — `refund_sale` + full suite green.
- [x] **Step 3:** e2e — refund spec included; green.
- [ ] **Step 4:** Bundle smoke — regenerate with `make community-bundle`, then in
      `formint-community/` run `pnpm install` + `pnpm test` + `cargo test` to
      prove the standalone package is self-sufficient. (Bundle already verified
      8.8 MB in C1; re-run only at tagging time.)
- [ ] **Step 5:** Landing seed — re-seed a dev landing DB and confirm the
      Formints Community card CTA points at `mammhoud/formint-community` **and**
      the `badge-offer` chip renders "Offline-first · open source" on the home
      product card and the edition card. (Seed + backend tests verified in C2;
      re-run only at tagging time.)

## Self-Review

1. **Single source of truth:** all feature changes land in `formint-community/`; the
   bundle is generated, never hand-edited (`COMMUNITY.md` marker enforces this).
2. **No monorepo leakage:** generated dirs are excluded by path segment, so the
   public repo never contains `node_modules`, cargo `target`, DBs, or logs.
3. **Rename completeness:** package/product/identifier/title/artifacts all
   covered; README is standalone (no `../precis/landi/...` relative links).
4. **Back-compat:** legacy `formint-*`/`mini-*`/`server-*`/`cloud-*` make
   aliases still resolve to the right editions.

## Execution Handoff

**Recommended:** run C4–C6 inline (publish steps are manual GitHub operations
that only the repo owner can perform); C6 verification can be run by a
subagent. The code side (C1–C3) is complete and verified.
