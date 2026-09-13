---
title: Setup & Build
description: Step-by-step setup, startup, build, and troubleshooting guides for every project in the monorepo.
navigation:
  title: Setup
  icon: i-lucide-wrench
object:
  type: "guide"
  id: "guide.setup"
attributes:
  source_path: "guides/02-setup.md"
  canonical_route: "/docs/en/guides/02-setup"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - setup
  - build
  - workflows
  - ci
links:
  - label: "Project awareness"
    to: "/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Quickstart"
    to: "/guides/01-quickstart"
    icon: "i-lucide-zap"
  - label: "Auth"
    to: "/guides/03-auth"
    icon: "i-lucide-lock"
---

# 🔧 Setup & Build

> Step-by-step **setup, startup, build, and troubleshooting** guides for every project in the monorepo. Each guide covers prerequisites, dependency install, database migrate/seed, dev startup (with ports), verification, production build, Docker, and common issues.

The guides live **next to their projects** (in each project's `docs/` folder) so they stay accurate as the code changes. This page is the index that links them all together.

## 📋 Project Setup Guides

| Project | Guide | Stack | Dev Ports |
|---------|-------|-------|-----------|
| **Precis (unified LMS + landing)** | [`projects/precis/docs/precis-main/SETUP_AND_BUILD.md`](../projects/precis/docs/precis-main/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | dev backend :8074 · dev frontend :4321 · Docker frontend :3000 |
| **Precis Landing** | [`projects/precis/docs/precis-landing/SETUP_AND_BUILD.md`](../projects/precis/docs/precis-landing/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | backend :8074 · frontend :4321 |
| **CTC Research** | [`projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md`](../projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | backend :5070 · frontend :3002 |
| **Syntara / Cypercloud** | [`projects/syntara/docs/SETUP_AND_BUILD.md`](../projects/syntara/docs/SETUP_AND_BUILD.md) | Django + Ceptor-AI + Monaco + HTMX | app :5073 · webpack HMR :5093 |
| **Formint POS (all editions)** | [`projects/formints/docs/GETTING_STARTED.md`](../projects/formints/docs/GETTING_STARTED.md) | Tauri + React + Astro + Django Ninja + Vue | Community :1420 · Pro :8767/:4321 · Cloud :8082/:8767/:4323 |
| **Loop-CRM** | [`projects/loop-crm/docs/SETUP_AND_BUILD.md`](../projects/loop-crm/docs/SETUP_AND_BUILD.md) | Django + django-fusion + Dramatiq + Astro | backend :8000 · frontend :4321 |
| **django-fusion (library)** | [`libs/django-fusion/docs/SETUP_AND_BUILD.md`](../libs/django-fusion/docs/SETUP_AND_BUILD.md) | Django/Wagtail helpers + Webpack 5 | — (library + asset build) |

## 🎯 Quick Decision Guide

| I want to work on… | Start with |
|--------------------|------------|
| The marketing + LMS product | [Precis (unified)](../projects/precis/docs/precis-main/SETUP_AND_BUILD.md) |
| A historical LMS alias | [Precis Main deployment](precis/deployment.md) — `precis-lms`/`lms` are compatibility aliases, not a separate stack |
| The landing/marketing slice | [Precis Landing](../projects/precis/docs/precis-landing/SETUP_AND_BUILD.md) |
| The medical research center site | [CTC Research](../projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md) |
| The AI chat / template customizer | [Syntara / Cypercloud](../projects/syntara/docs/SETUP_AND_BUILD.md) |
| Any POS edition (desktop, pro, cloud) | [Formint POS](../projects/formints/docs/GETTING_STARTED.md) |
| The sales & marketing platform | [Loop-CRM](../projects/loop-crm/docs/SETUP_AND_BUILD.md) |
| Shared Django/Wagtail components | [django-fusion](../libs/django-fusion/docs/SETUP_AND_BUILD.md) |

## ⚡ Common First Steps (All Projects)

1. **Python:** `python3 --version` (≥ 3.11) and install [uv](https://docs.astral.sh/uv/).
2. **Node:** `node --version` (18–22) and `npm --version`.
3. **Backend deps:** Django-based projects sync from the workspace `projects/pyproject.toml` (`uv sync`) — see the per-project guide.
4. **Frontend deps:** `npm install` / `pnpm install` in the project's `frontend/` (or `assets/` for Syntara).
5. **Database:** `make migrate` then the project's seed target (`make seed` / `make seed-demo` / `make populate-data`).
6. **Run:** backend dev server + frontend dev server (ports in the table above).
7. **Verify:** `make check` and `make test` per project.

## 🛠️ Workflows & CI

### GitHub Actions

#### `deploy-ci.yml`

Located at `.github/workflows/deploy-ci.yml`.

Triggers on changes to:
- `Makefile` and `Makefile.*`
- `.github/workflows/deploy-ci.yml`
- `.github/actions/deploy-preflight/**`
- `**/docker-compose*.yml` and `*.yaml`
- `libs/**/*.md`
- `application/scripts/staging/check_markdown_links.py`

Jobs:

1. **preflight** — runs the local Composite Action `.github/actions/deploy-preflight` to validate Docker daemon and `make deploy-ci`.
2. **markdown-links** — runs `application/scripts/staging/check_markdown_links.py` to validate Markdown cross-links.

#### `check-extras.yml`

Located at `.github/workflows/check-extras.yml`.

Validates that any `uv add "pkg[extras]"` / `pip install "pkg[extras]"` line in `libs/**/docs/` matches the extras declared in the corresponding `pyproject.toml`.

### Makefile Delegation

The root `Makefile` is a thin entrypoint that delegates site work to `projects/Makefile`.

```bash
# Run a target for a specific site
cd projects
make check WEBSITE=precis-ctc
make docker-up WEBSITE=lms
make test WEBSITE=vresume
```

Common targets:

| Target | Purpose |
|---|---|
| `check` | Django system checks |
| `docker-up` | Build and start a site container |
| `docker-down` | Stop site containers |
| `docker-health-check` | Health-check running containers |
| `tests-unit` | Unit tests |
| `tests-integration` | Integration tests |

### Recommended Enhancements

1. Add a `docs.yml` workflow that runs `npm --prefix docs run build` to validate Docus routes and locales on every docs PR.
2. Pin `actions/checkout` and `actions/setup-python` to specific hashes for supply-chain security.
3. Keep `make -C docs serve` as the canonical local Docus preview command.

## ## Remarks & Notes

- Per-project `SETUP_AND_BUILD.md` files are the authoritative source for each project.
- This index is maintained for cross-project discovery; project-level docs take precedence.
- `AGENTS.md` and Makefiles in each project are the source of truth for paths and commands.
- For the monorepo-wide quickstart (clone → `uv sync` → `just install` → deploy), see [Quickstart](guides/01-quickstart.md).

<!-- AI-generated: review needed -->