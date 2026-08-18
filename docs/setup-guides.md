# 🛠️ Project Setup & Build Guides

Step-by-step **setup, startup, build, and troubleshooting** guides for every
project in the monorepo. Each guide covers prerequisites, dependency install,
database migrate/seed, dev startup (with ports), verification, production
build, Docker, and common issues.

> The guides live **next to their projects** (in each project's `docs/`
> folder) so they stay accurate as the code changes. This page is the index
> that links them all together.

## Guides

| Project | Guide | Stack | Dev ports |
|---------|-------|-------|-----------|
| **Precis (unified)** | [`projects/precis/precis-main/docs/SETUP_AND_BUILD.md`](../projects/precis/precis-main/docs/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | backend :8074 · frontend :4321 |
| **Precis LMS** | [`projects/precis/precis-main/docs/SETUP_AND_BUILD.md`](../projects/precis/precis-main/docs/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | backend :5071 · frontend :3002 |
| **Landing-Fusion** | [`projects/precis/precis-landing/docs/SETUP_AND_BUILD.md`](../projects/precis/precis-landing/docs/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | backend :8074 · frontend :4321 |
| **CTC Research** | [`projects/precis/precis-ctc/docs/SETUP_AND_BUILD.md`](../projects/precis/precis-ctc/docs/SETUP_AND_BUILD.md) | Astro + Django + Wagtail + django-fusion | backend :5070 · frontend :3002 |
| **Syntara / Cypercloud** | [`projects/syntara/docs/SETUP_AND_BUILD.md`](../projects/syntara/docs/SETUP_AND_BUILD.md) | Django + Ceptor-AI + Monaco + HTMX | app :5073 · webpack HMR :5093 |
| **Formint POS (all editions)** | [`projects/formints/docs/GETTING_STARTED.md`](../projects/formints/docs/GETTING_STARTED.md) | Tauri + React + Astro + Django Ninja + Vue | Community :1420 · Pro :8767/:4321 · Cloud :8082/:8767/:4323 |
| **Loop-CRM** | [`projects/loop-crm/docs/SETUP_AND_BUILD.md`](../projects/loop-crm/docs/SETUP_AND_BUILD.md) | Django + django-fusion + Dramatiq + Astro | backend :8000 · frontend :4321 |
| **django-fusion (library)** | [`libs/django-fusion/docs/SETUP_AND_BUILD.md`](../libs/django-fusion/docs/SETUP_AND_BUILD.md) | Django/Wagtail helpers + Webpack 5 | — (library + asset build) |

## Quick decision guide

| I want to work on… | Start with |
|--------------------|------------|
| The marketing + LMS product | [Precis (unified)](../projects/precis/precis-main/docs/SETUP_AND_BUILD.md) |
| The standalone learning platform | [Precis LMS](../projects/precis/precis-main/docs/SETUP_AND_BUILD.md) |
| The landing/marketing slice | [Landing-Fusion](../projects/precis/precis-landing/docs/SETUP_AND_BUILD.md) |
| The medical research center site | [CTC Research](../projects/precis/precis-ctc/docs/SETUP_AND_BUILD.md) |
| The AI chat / template customizer | [Syntara / Cypercloud](../projects/syntara/docs/SETUP_AND_BUILD.md) |
| Any POS edition (desktop, pro, cloud) | [Formint POS](../projects/formints/docs/GETTING_STARTED.md) |
| The sales & marketing platform | [Loop-CRM](../projects/loop-crm/docs/SETUP_AND_BUILD.md) |
| Shared Django/Wagtail components | [django-fusion](../libs/django-fusion/docs/SETUP_AND_BUILD.md) |

## Common first steps (all projects)

1. **Python:** `python3 --version` (≥ 3.11) and install
   [uv](https://docs.astral.sh/uv/).
2. **Node:** `node --version` (18–22) and `npm --version`.
3. **Backend deps:** Django-based projects sync from the workspace
   `projects/pyproject.toml` (`uv sync`) — see the per-project guide.
4. **Frontend deps:** `npm install` / `pnpm install` in the project's
   `frontend/` (or `assets/` for Syntara).
5. **Database:** `make migrate` then the project's seed target
   (`make seed` / `make seed-demo` / `make populate-data`).
6. **Run:** backend dev server + frontend dev server (ports in the table above).
7. **Verify:** `make check` and `make test` per project.

## Related

- [Guides (numbered tutorials)](guides/) — first-time setup, auth, deploy
- [Plans](plans/README.md) — canonical implementation plans
- [Projects overview](overview.md) — repository structure
- [`../README.md`](../README.md) — monorepo root
