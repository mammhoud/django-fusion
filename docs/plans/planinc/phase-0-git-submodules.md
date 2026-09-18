# Phase 0 — Git Remotes & Submodule Setup

**Status:** Completed  
**Scope:** Workspace root (`/home`), all product directories  
**Owner:** Infrastructure / DevOps

---

## Objective

Establish the canonical Git topology for the Structa Cloud monorepo: one root
workspace repository (`mammhoud/workspace`) with each product directory
registered as an independent submodule pointing to its own GitHub repository.
All branches are named `generic`.

---

## Repository Map

| Submodule path | GitHub URL | Branch |
|---|---|---|
| `libs/django-fusion` | `https://github.com/mammhoud/django-fusion.git` | `generic` |
| `projects/CRM` | `https://github.com/mammhoud/crm.git` | `generic` |
| `projects/CMS` | `https://github.com/mammhoud/cms.git` | `generic` |
| `projects/POS` | `https://github.com/mammhoud/pos.git` | `generic` |
| `projects/Clients/ctc-research` | `https://github.com/mammhoud/ctc-research.git` | `generic` |
| `application/tools/PlanInc` | `https://github.com/mammhoud/PlanInc.git` | `generic` |

---

## Steps Completed

### 1. Workspace root remote

```bash
# Root repo remote renamed from stale structa.cloud to workspace
git remote set-url origin https://github.com/mammhoud/workspace.git
git branch -M generic
git push -u origin generic
```

### 2. Each product directory initialised as a standalone repo

For each product directory (CRM, CMS, POS, ctc-research, PlanInc):

```bash
cd <dir>
git init
git branch -M generic
git remote add origin https://x-access-token:<TOKEN>@github.com/mammhoud/<repo>.git
git add .
git commit -m "Initial commit: <Product> module"
git push -u origin generic
```

Key notes:
- The workspace token (`ghp_FPM0...`) is reused as the `x-access-token`
  authenticator for all sub-repos.
- `ctc-research` origin was corrected from the workspace URL to
  `mammhoud/ctc-research.git` via `git remote set-url`.
- `planing/` inside `PlanInc/` is itself a nested git repo (Blinko upstream);
  it was excluded from the PlanInc commit via `git rm --cached planing`.

### 3. `.gitmodules` final state (`/home/.gitmodules`)

```ini
[submodule "libs/django-fusion"]
    path = libs/django-fusion
    url = https://github.com/mammhoud/django-fusion.git
    branch = generic

[submodule "projects/CRM"]
    path = projects/CRM
    url = https://github.com/mammhoud/crm.git
    branch = generic

[submodule "projects/CMS"]
    path = projects/CMS
    url = https://github.com/mammhoud/cms.git
    branch = generic

[submodule "projects/POS"]
    path = projects/POS
    url = https://github.com/mammhoud/pos.git
    branch = generic

[submodule "projects/Clients/ctc-research"]
    path = projects/Clients/ctc-research
    url = https://github.com/mammhoud/ctc-research.git
    branch = generic

[submodule "application/tools/PlanInc"]
    path = application/tools/PlanInc
    url = https://github.com/mammhoud/PlanInc.git
    branch = generic
```

### 4. Directory renames committed

The workspace commit `c5571fd0` renamed:
- `projects/syntara/` → `projects/CMS/`
- `projects/loop-crm/` → `projects/CRM/`
- `projects/formints/` → `projects/POS/`

6 140 files changed. Pushed to both `origin` (workspace) and
`structa-cloud` remotes.

---

## Verification

```bash
# Confirm root remote
cd /home && git remote -v
# origin  https://github.com/mammhoud/workspace.git

# Confirm submodule table
cat /home/.gitmodules

# Confirm each sub-repo remote
cd /home/projects/CRM && git remote -v
cd /home/projects/CMS && git remote -v
cd /home/projects/POS && git remote -v
cd /home/projects/Clients/ctc-research && git remote -v
cd /home/application/tools/PlanInc && git remote -v
```

---

## Notes & Gotchas

- The `structa-cloud` remote (pointing to `mammhoud/structa.cloud.git` with
  the embedded token) is preserved as a secondary push target on the workspace
  root. It is not a submodule entry.
- `projects/structa.cloud/` no longer exists in the filesystem; it was merged
  into the workspace root. The `.gitmodules` entry for it was removed.
- `application/tools/planing/planing` was an orphaned nested submodule
  pointer; the `.git/modules` entry and config section were cleaned up.
- Never force-push `main`/`master` on the GitHub repos — always use `generic`.
