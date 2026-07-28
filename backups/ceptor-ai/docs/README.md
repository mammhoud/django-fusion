# Structa Cloud Documentation

This is the canonical entrypoint for documentation for the Structa Cloud multi-site Django/Wagtail monorepo.

## Start here

| Topic | Documentation |
|---|---|
| Getting started | [First-time setup](guides/development/FIRST_TIME_SETUP.md), [development quickstart](guides/development/quickstart.md), and [setup start page](setup/00_START_HERE.md) |
| Websites | [Websites overview](websites/README.md), [CTC Research](websites/ctc-research/index.md), [LMS Demo](websites/lms-demo/index.md), and [VResume](websites/vresume/index.md) |
| AI tooling | [AI tooling overview](ai/README.md), [AI setup](ai/setup.md), and [AI task prompts](ai/prompt_tasks.md) |
| Local libraries | [Local libraries overview](libs/README.md), [library integration guide](guides/LIBS_INTEGRATION.md), and [packages overview](libs/README.md) |
| Deployment | [Deployment overview](deployment.md), [deployment quick start](guides/deployment/QUICK_START.md), and [deployment guide](guides/deployment/deployment_guide.md) |
| Testing | [Testing guide](guides/development/testing_guide.md), [auth testing](reference/auth/testing.md), and [shared testing notes](reference/shared/README.md) |
| Template customization | [Template customization guide](reference/design/customization.md), [components guide](reference/design/components.md), and [template flow architecture](reference/architecture/templates_flow.md) |

## Repository map

- `applications/` contains the Django sites, shared settings, shared frontend assets, reusable local libraries, scripts, tasks, and build tooling.
- `docs/websites/` contains current site-specific documentation entrypoints.
- `docs/archives/` contains historical reports, status snapshots, session notes, and completion summaries that may no longer describe current commands.

## Legacy indexes

Older index files now point back here:

- [docs/INDEX.md](INDEX.md)
- [docs/_INDEX.md](_INDEX.md)
- [docs/index.md](index.md)

---

## Documentation Tree

```
docs/
├── README.md              # this entrypoint
├── _sidebar.md            # Docsify navigation
├── _navbar.md
├── index.md               # redirect to README.md
├── guides/                # practical guides (deployment, development, operations)
│   ├── deployment/
│   ├── development/
│   ├── getting-started/
│   ├── infrastructure/
│   └── user-guide/
├── reference/             # architecture, auth, design, shared resources, monorepo
│   ├── architecture/
│   ├── auth/
│   ├── design/
│   ├── monorepo/
│   └── shared/
├── websites/              # per-site documentation
├── libs/                  # local library documentation
├── ai/                    # AI assistant documentation
├── upcoming/              # upcoming specs
├── archives/             # historical reports
├── changelog/             # changelog
├── per-app-docs/          # per-app docs standards
├── configs/               # configuration docs
├── fixes/                 # error fixes
└── tasks/                 # task notes
```

> **Note:** The active navigation structure is minimal (`guides/`, `reference/`, `websites/`, `libs/`, `ai/`, `upcoming/`, `archives/`). Legacy directories (`development/`, `infrastructure/`, `auth/`, `design/`, `shared/`, `user_guide/`, `ecosystem/`, `monorepo/`) have been moved into `guides/` and `reference/`.
