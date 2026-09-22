# ceptor-ai — Full Project Enhancement Plan

Repo: [mammhoud/ceptor-ai](https://github.com/mammhoud/ceptor-ai) (default branch: `generic`, 511 commits)
Companion document: `django-fusion-enhancements.md` (the `django_fusion` library this monorepo consumes as a git submodule under `application/libs/django-fusion/`)

This is a large deployment monorepo (~123 MB checked out), not a library: it owns `application/` (precis-ctc, lms, VResume, crm, cypercloud), `compose/`, `proxy/`, `databases/`, a `Makefile` with `push`/`push-libs` targets, and a 22 MB `docs/` tree. Everything below is based on the actual file tree and file contents pulled from the `generic` branch, plus one live, read-only fetch of `https://ctc-research.com/auth/register/`.

---

## 0. Scope note — please read before assigning follow-ups

I have **read-only, unauthenticated access** to the public GitHub repo and to public URLs. I do **not** have:
- A `GITHUB_TOKEN`/PAT, so I cannot run `make push` or `make push-libs` — both already exist in the Makefile and require `github=<token>` in `.env` (see §3).
- SSH or server access, so I cannot read `precis-ctc`'s server-side logs, restart containers, or run `docker compose up` against production.
- Any ability to submit the actual signup form (I can fetch the page, not POST credentials through it) — see §5 for exactly what I could and couldn't verify.

Everything in this document is either (a) a direct finding from the repo tree/files, (b) a finding from the one live page fetch, or (c) a proposed change for someone with push/deploy access to apply. I'm not reporting anything as "fixed" or "deployed" unless I could verify it directly.

---

## 1. Biggest finding: `docs/` has years of duplicate, split-by-spelling content

`docs/` is 22 MB and contains the same topics split across multiple differently-named locations. Examples pulled directly from the tree:

| Topic | Duplicate locations |
|---|---|
| CTC Research site | `docs/precis-ctc/` (8 KB) **and** `docs/ctc-research.com/` (324 KB) |
| Structa Cloud | `docs/structa-cloud/` (8 KB) **and** `docs/structa.cloud/` (316 KB) **and** `docs/structa.cloud.png` (2.1 MB) |
| django-fusion | `docs/django-fusion/` (8 KB dir) **and** `docs/customizer-django-fusion-components.md` (20 KB) **and** `docs/django-fusion.png` (3.2 MB) |
| django-osoul | `docs/customizer-django-osoul-components.md` (20 KB) **and** `docs/django-osoul.png` (3.2 MB) **and** `docs/DJANGO_OSOUL_VIEWSETS.md` (12 KB) |
| django-grep / django-rseal | `docs/django-grep.png` (3.1 MB), `docs/django-rseal.png` (3.1 MB) — no matching markdown, i.e. orphaned images |
| ceptor-ai itself | `docs/ceptor-ai/` (8 KB) **and** root-level `docs.md`, `README.md`, `AGENTS.md`, `PROMPTS.md` all also describing it |

Root level compounds this: `AUTH_REGISTER_COMPLETE_FIX.md`, `AUTH_REGISTER_FIX_SUMMARY.md`, and `FINAL_AUTH_REGISTER_SUMMARY.md` are three separate files documenting what looks like the *same* incident (see §5). Plus `CHANGES_MADE.md`, `DEPLOYMENT_GUIDE.md`, `FORMS_TABLES_INTEGRATION_SUMMARY.md`, `FUSION_ROUTING_STRUCTURE.md`, `TINKER_INTEGRATION.md`, and a stray `README.md.bak` sitting next to the live `README.md`.

**Just the four PNG diagrams above (`django-fusion.png`, `django-grep.png`, `django-osoul.png`, `django-rseal.png`, `structa.cloud.png`) total ~14.7 MB committed to git** — architecture diagrams like these should be generated (Mermaid, as recommended in the django-fusion companion doc §3.3) or stored outside version control, not committed as multi-megabyte PNGs that bloat every clone forever.

This pattern repeats one level down: `application/cypercloud/` alone has its own `API.md`, `CONFIGURATION_SUMMARY.txt`, `DEPLOYMENT.md`, `DEPLOYMENT_LOG.md`, `DEPLOYMENT_STATUS.md`, `DYNACONF_SETUP.md`, `INDEX.md`, `MAKEFILE.md`, plus its own `docs/` — the same "three files for one topic" problem, just scoped to one app.

### 1.1 Dedup methodology (apply per app + per top-level docs/ folder)

1. **Pick a canonical topic list** — one doc per subject, not one per spelling variant. Use the numbered scheme in §2 below.
2. **Diff before merging.** For each duplicate pair (e.g. `docs/precis-ctc/` vs `docs/ctc-research.com/`), diff the content; don't assume the newer mtime is the correct one — check which one the current code/URLs actually match.
3. **Move images out of git history weight**, or at minimum compress/resize them; a 3 MB architecture PNG is almost never necessary at full resolution for docs.
4. **Redirect, don't silently delete** — leave a one-line stub at the old path (`This moved to docs/05-ctc-research.md`) for one release cycle so any open links/bookmarks don't 404 outright.
5. **Do this per-repo**, since the task explicitly calls out "each docs server or repo" — apply the same methodology inside `application/cypercloud/docs/` and any other nested `docs/` folder independently; don't assume top-level dedup cascades down automatically.

---

## 2. Unified, numbered docs/prompts/agents tree for this repo

Same numbering convention as the django-fusion companion doc, with a `CA-0NN` prefix (ceptor-ai) so IDs don't collide across repos.

```
docs/
├── INDEX.md                        # CA-000 — map only
├── 01-getting-started.md           # CA-001
├── 02-architecture.md              # CA-002  (absorbs architecture-notes.md, WEBSITE_ARCHITECTURE.md)
├── 03-deployment.md                # CA-003  (absorbs deployment.md, deployment_flow.md, DEPLOYMENT_GUIDE.md)
├── 04-routing.md                   # CA-004  (renamed from ROUTING.md)
├── 05-components-and-fragments.md  # CA-005  (renamed from COMPONENTS_AND_FRAGMENTS.md)
├── 06-django-fusion-integration.md # CA-006  (merges docs/django-fusion/, customizer-django-fusion-components.md, django-fusion.png → one Mermaid diagram)
├── 07-django-osoul-integration.md  # CA-007  (merges customizer-django-osoul-components.md, DJANGO_OSOUL_VIEWSETS.md, django-osoul.png)
├── 08-application/
│   ├── ctc-research.md             # CA-008  (merges docs/precis-ctc/, docs/ctc-research.com/)
│   ├── lms.md                 # CA-009
│   ├── vresume.md                  # CA-010
│   ├── crm.md                      # CA-011
│   └── cypercloud.md                   # CA-012  (merges application/cypercloud/*.md + application/cypercloud/docs/)
├── 09-troubleshooting/
│   ├── auth-register.md            # CA-013  (merges the 3 AUTH_REGISTER_*.md root files — see §5)
│   └── error-resolution-log.md     # CA-014  (renamed from error-resolution-log.md, kept as append-only log)
├── 10-configuration.md             # CA-015  (merges docs/configs/, docs/setup/)
├── 11-proxy-and-tls.md             # CA-016  (renamed from proxy/LETSENCRYPT.md + proxy/README.md summary)
├── 12-migration-record.md          # CA-017  (renamed from migration-record.md — append-only history, keep as-is)
└── legacy/                         # docs/archives/, docs/guides/, docs/reference/, docs/websites/ — triage, don't delete blind
```

Root stays minimal:

```
/
├── README.md          # CA-000-root — what this monorepo is, links to docs/INDEX.md
├── AGENTS.md           # CA-AG-000 — canonical paths + per-app pointers
├── PROMPTS.md          # CA-PR-000 — numbered prompt index (see §2.1)
├── CHANGELOG.md         # keep, append-only
```
Delete or fold into the numbered tree above: `README.md.bak`, `AUTH_REGISTER_COMPLETE_FIX.md`, `AUTH_REGISTER_FIX_SUMMARY.md`, `FINAL_AUTH_REGISTER_SUMMARY.md`, `CHANGES_MADE.md`, `DEPLOYMENT_GUIDE.md` (→ CA-003), `FORMS_TABLES_INTEGRATION_SUMMARY.md` (→ merge into django-fusion's own FORMS_TABLES doc, this content belongs in the library repo, not here), `FUSION_ROUTING_STRUCTURE.md` (→ CA-006), `TINKER_INTEGRATION.md` (→ CA-012), `docs.md` (→ replaced by `docs/INDEX.md`).

### 2.1 Per-app AGENTS.md/PROMPTS.md — already a good pattern, keep it

Each of `application/{precis-ctc,lms,VResume}/` already has its own `AGENTS.md` and `PROMPTS.md`. That's the right instinct — keep it, but make each one link back to the root `AGENTS.md`/`PROMPTS.md` with the `CA-0NN` doc IDs above instead of duplicating explanation. `crm` and `cypercloud` don't yet follow this pattern (`crm` has neither; `cypercloud` has a sprawl of its own docs instead) — bring them in line:

```
application/<app>/
├── AGENTS.md     # links to root AG-000 + docs/08-application/<app>.md
├── PROMPTS.md    # app-specific prompts only; generic ones stay at root
```

### 2.2 Usage guide & remarks (same convention as django-fusion companion doc)

- Every `CA-0NN` doc should open with a **"Applies to"** line naming the exact app/service/compose file it documents, since this is a multi-app monorepo and ambiguity here is exactly how duplication happened in the first place.
- Code hints: any `docker-compose` or `Makefile` snippet quoted in docs must be copy-pasted from the real file with a comment noting the source path (`# compose/docker-compose.applications.yml`) — this repo's Makefile is 48 KB; don't let docs drift from it the way django-fusion's docs drifted from its source.
- `> Remark:` blockquotes for anything environment-specific (needs `GITHUB_TOKEN`, needs a specific `.env`, only applies to `docker-compose.prod.yml` vs `.local.yml`) — this repo has 5 separate compose files (`applications`, `docs`, `local`, `prod`, `tasks`) plus 4 more under `proxy/` (`caddy`, `nginx`, `traefik`, default) and 1 under `databases/`; docs must be explicit about which compose file a given instruction targets.

---

## 3. `make push` / `make push-libs` — already implemented, here's what's there and what to check

Good news: this isn't something to build from scratch. The Makefile already has exactly what was asked for, at lines ~921-1013:

- **`make push`** — pushes the current branch of the monorepo to `origin`, authenticating via a token, then automatically chains into `push-libs`.
- **`make push-libs`** — iterates every directory under `application/libs/*/` (currently `django-fusion` and `ceptor-ai`), commits any local changes in each as a submodule, and pushes each one to its own GitHub repo on the `generic` branch (`git push ... HEAD:generic`).
- **`make push-lib LIB=<name>`** — same, but for a single named lib.
- **`require-github-token`** — a shared gate: it looks for a token in `$GITHUB_TOKEN`/`$GH_TOKEN` env vars, or a `github=` key in `.env`, `projects/.env`, or `proxy/.env`, and hard-fails with a clear error listing exactly where it looked if none is found.

This already matches the request ("make commands for push and push-libs at all repo to generic branch"). What I'd still check/tighten, since I can't run it myself without a token:

1. **`application/libs/ceptor-ai` and `application/libs/django-fusion` are empty directories in the tarball I fetched** — they're real git submodules that only materialize with `git submodule update --init`, which a plain tarball download skips. Confirm `.gitmodules` (present at root) points both at the correct `generic` branch and that `push-libs`' hardcoded `case` statement (django-fusion/ceptor-ai → specific URLs) stays in sync if a third lib is ever added — right now adding a new lib directory silently hits the `*) echo "⏭️ Unknown lib — skipping"` branch, which is safe but easy to miss in output.
2. **Self-reference:** `application/libs/ceptor-ai` pointing back at this same repo (`ceptor-ai`) as a submodule of itself is unusual — worth a one-line comment in the Makefile or `.gitmodules` explaining why (likely: a pinned/vendored copy for a specific deployment, distinct from the working tree), so a future maintainer doesn't "fix" it into a real cycle.
3. **`.gitignore` already ignores `application/libs/`** (lines 73 and 77: `application/libs/` and `application/libs/*`) — this is correct for a submodule directory and matches what was asked for ("add libs to main gitignore file"). No change needed there; it's already done. If anything, the duplicate line (`application/libs/` and `application/libs/*`) can be collapsed to one.
4. **Before anyone runs `make push`/`make push-libs` for real**, do a dry run: `git -C application/libs/django-fusion status` and `git -C application/libs/ceptor-ai status` to confirm each submodule is on the `generic` branch and has no unexpected divergence from its remote before letting the Makefile force a commit+push.

I did not run any of this — it needs a real `GITHUB_TOKEN` and someone comfortable pushing to production-linked repos.

---

## 4. `compose/docker-compose.applications.yml` — reviewed

```yaml
include:
  - ./../application/precis-ctc/docker-compose.yml
  - ./../application/lms/docker-compose.yml
  - ./../application/VResume/docker-compose.yml
  - ./../application/crm/docker-compose.yml
  - ./../application/cypercloud/docker-compose.yml
  # - ./../application/customizer/docker-compose.yml  # Customizer not available
```

Findings:
- Clean `include:`-based composition, one compose file per app — good pattern, keep it.
- The commented-out `customizer` line is dead weight; either remove it or replace the comment with a tracked TODO/issue reference so it's clear whether that app is planned or abandoned.
- This file has no top-level `networks:`/`volumes:` of its own (comment says they're defined in the root compose) — worth confirming `docker-compose.yml` at repo root is the one always loaded alongside this file (e.g. via `-f docker-compose.yml -f compose/docker-compose.applications.yml`), and documenting that invocation explicitly in CA-003 (deployment doc) rather than leaving it implied.
- Suggest a `docs/03-deployment.md` (CA-003) table mapping: compose file → which app(s) it includes → which `.env` it reads → which Makefile target invokes it (the root Makefile already has `proxy`, `services`, `databases` targets calling sub-Makefiles — document that chain once, here, instead of re-explaining it in every app's own docs).

---

## 5. `https://ctc-research.com/auth/register/` — live check result

I fetched the page directly (read-only GET, no form submission possible from here). Result: **HTTP 200, page renders correctly** — a full "Create Account" form (username, email, password, confirm password, terms checkbox, Sign Up button) with client-side validation hints, and a working link to `/auth/login/`.

This matches what's already claimed in the repo's own `AUTH_REGISTER_COMPLETE_FIX.md`: routing was fixed to use a custom `AllauthSignupView` wrapping `PageHandler` (instead of raw `allauth.account.views.SignupView`), a duplicate import in `plugins/accounts/urls.py` was removed, and `register.html` was fixed to extend `base_auth.html`. My live check is consistent with that fix having landed — the page is not broken today.

**One real issue I did spot on the live page:** the "I agree to the privacy policy & terms" checkbox links to `#` — a dead anchor instead of an actual privacy-policy/terms page. That's a small but real bug (and a compliance gap if there's supposed to be a real terms page) worth its own entry in CA-013.

**What I could not check** (needs server/log access I don't have): whether an actual POST to this form succeeds end-to-end (account creation, email verification dispatch, DB write) — the page rendering fine doesn't guarantee the full flow works. Also could not read the site's actual error logs mentioned in the request. If a maintainer can run `docker compose -f compose/docker-compose.applications.yml logs precis-ctc --tail=200` (or the app's own `application/precis-ctc/logs/` directory, which exists in the tree), that would answer it directly — I'd be glad to help interpret the output if it's pasted in.

**Recommendation:** since `AUTH_REGISTER_COMPLETE_FIX.md`, `AUTH_REGISTER_FIX_SUMMARY.md`, and `FINAL_AUTH_REGISTER_SUMMARY.md` all describe what reads as the same incident at different stages, consolidate them into the single `docs/09-troubleshooting/auth-register.md` (CA-013) proposed in §2, append a dated "confirmed still working as of {date}, dead ToS link open" note, and delete the three root-level files.

---

## 6. django-fusion components as default templates/tags ("unfold")

The request asks to make django-fusion components the default template tags across the applications, referencing "unfold." Based on the repo tree, each app (`precis-ctc`, `lms`, `VResume`) already has its own `templates/`, `plugins/`, `assets/` — and `docs/customizer-django-fusion-components.md` plus `docs/FUSION_ROUTING_STRUCTURE.md` already describe some of this wiring. Concretely, to make `{% comp %}` (django-fusion's component tag, documented in the companion repo's `COMPONENT_TAG.md`) the default across apps:

1. Confirm `django_fusion` is in every app's `INSTALLED_APPS` (`application/{precis-ctc,lms,VResume,crm,cypercloud}/settings.py`) with `{% load components %}` available globally — consider adding it to Django's `builtins` in `TEMPLATES` settings so every template gets `{% comp %}` without an explicit `{% load %}`, matching the "default" ask.
2. Audit each app's existing templates for `{% include %}` calls that should become `{% comp "path" / %}` per `AGENTS.md`'s own guidance ("Prefer `{% comp "path" / %}` over `{% include "path" %}` for static paths") — this is a mechanical, greppable migration (`grep -rn "{% include" application/*/templates`), not a redesign.
3. Document the resulting per-app component inventory in `docs/08-application/<app>.md` (CA-008–CA-012) rather than a separate "unfold" doc, so component usage lives next to the app it's used in.
4. If "Unfold" refers to the third-party `django-unfold` admin theme rather than a custom concept — worth confirming with whoever wrote the original request, since I found no reference to a package named `unfold` anywhere in either repo's `pyproject.toml`/`uv.lock`. I'm flagging this rather than guessing, since silently assuming the wrong meaning here would waste real implementation effort.

---

## 7. Suggested execution order

1. **§5 first** — consolidate the three AUTH_REGISTER docs into one, fix the dead ToS link, and get someone with log access to confirm the full POST flow (registration, not just page load) actually works.
2. **§1 + §2** — dedup `docs/`, adopt the numbered `CA-0NN` tree, strip the ~14.7 MB of committed PNGs down to Mermaid or compressed images.
3. **§3** — before ever running `make push`/`make push-libs` for real, do the submodule status dry run described in §3.4, then have someone with a valid `GITHUB_TOKEN` run it.
4. **§4** — document the compose/Makefile invocation chain once in CA-003 instead of leaving it implicit.
5. **§6** — mechanical `{% include %}` → `{% comp %}` audit, app by app, once docs are stable enough to record the result.
6. Cross-check against the companion `django-fusion-enhancements.md` §3 prompts wherever this repo's docs currently duplicate library-level content (e.g. `FORMS_TABLES_INTEGRATION_SUMMARY.md` here should point at django-fusion's own `docs/06-forms-and-tables.md`, not restate it).

---

## 8. What I did not do, and why

- **Did not run `make push` or `make push-libs`.** No `GITHUB_TOKEN`; running it without one fails cleanly at `require-github-token`, and running it *with* a borrowed token from this environment isn't something I'd do without explicit, in-the-moment confirmation from someone authorized to push to these repos.
- **Did not redeploy anything.** No server/SSH/docker access to the host(s) running `ctc-research.com`.
- **Did not read production logs.** Only a public page fetch was possible; §5 spells out exactly what that did and didn't confirm.
- **Did not delete any files.** All dedup/deletion suggestions in §1–§2 are recommendations for someone with write access to apply and review, not changes I've made.

If you'd like, I can draft the actual consolidated `docs/09-troubleshooting/auth-register.md` content from the three existing AUTH_REGISTER files, or draft the CI-friendly `.gitmodules`/submodule dry-run check as a script — say which one and I'll produce it as a file next.
