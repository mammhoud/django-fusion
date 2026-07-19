# 📁 Dev Archive — Historical Development Records

> ⚠️ **Internal cross-references may be broken** after reorganization. This directory is git-ignored and for local dev reference only.
> Formerly `docs/archives/` — renamed to `docs/dev/` for clarity.

---

## Directory Structure

```
dev/
├── deployment/           # Production deployment records & guides
│   ├── production/       # 70+ deployment reports, summaries, verification logs
│   └── guides/           # Legacy deployment guides (obsolete patterns)
├── sessions/             # Development session records
│   ├── completion/       # Phase completion reports, handoff docs, execution logs
│   └── summaries/        # Session summaries, notes, status snapshots
├── phases/               # Phase-by-phase implementation reports (PHASE4–PHASE14)
├── plans/                # Development plans, tasks, and status tracking
│   ├── NEXT_STEPS.md     # Pending work items
│   ├── STATUS.md         # Current status overview
│   ├── TASK_TRACKER_FINAL.md  # Completed task inventory
│   ├── TASK_COMPLETION_SUMMARY.md  # Summary of delivered tasks
│   └── old-todos/        # Archived todo lists from legacy structure
├── pre-restructure/      # Pre-rename documentation snapshots
│   ├── ctc-research/     # CTC Research docs (pre core/ → projects/ rename)
│   ├── lms-demo/         # LMS demo docs (pre lms-demo/ → lms/ rename)
│   ├── vresume/          # VResume docs (pre VResume/ → portfolio/ rename)
│   ├── structa-cloud/    # structa.cloud docs (pre core/ → projects/ rename)
│   ├── shared/           # Shared configs (pre core/ consolidation)
│   └── ai/               # Legacy AI docs (pre agents/ + prompts/ merge)
└── technical/            # Technical reference archives
    ├── architecture/     # System architecture diagrams & analysis
    ├── auth/             # Authentication implementation records
    ├── components/       # Component design & UI patterns
    ├── development/      # Dev workflow, setup guides, troubleshooting
    └── infrastructure/   # Infrastructure configuration records
```

---

## What's Here vs Main Docs

| Content Type | dev/ (this dir) | Main docs/ |
|-------------|-----------------|------------|
| **Purpose** | Historical record, dev reference | Published documentation site |
| **Git** | Git-ignored (`.gitignore`) | Tracked |
| **Audience** | Developers working on the repo | Users & contributors |
| **Structure** | Phase/session-based | Topic/project-based |
| **Current?** | Snapshots from past phases | Live, updated docs |

---

## Project Version Map (Current State)

| Project | Path | Status | Last Major Change |
|---------|------|--------|-------------------|
| LMS | `projects/lms/` | ✅ Active | Renamed from lms-demo (2026-07) |
| Portfolio | `projects/portfolio/` | ✅ Active | Renamed from VResume (2026-07) |
| Cypercloud | `projects/cypercloud/` | ✅ Active | Renamed from tinker (2026-07) |
| CTC Research | `projects/ctc-research/` | 🔄 Merged into LMS | Docs consolidated |
| POS | `projects/pos/` | ✅ Active | 3-edition system + POS-KO |
| WWW (Shared) | `projects/www/` | ✅ Active | Shared core + sentinel site |
| Libs | `libs/` | ✅ Active | Git submodules at repo root |
| django-fusion | `libs/django-fusion/` | ✅ Active | Submodule: mammhoud/django-fusion |
| ceptor-ai | `libs/ceptor-ai/` | ✅ Active | Submodule: mammhoud/ceptor-ai |

---

## Status Plan — What's Done vs Not Done

### ✅ Done (Implemented)

| Area | What | When |
|------|------|------|
| Infra restructuring | `core/` → `projects/`, `libs/` at repo root | 2026-07-19 |
| POS 3-edition system | Minimal, Solo, Full editions | 2026-07-19 |
| POS-KO Gaming Center | Token-based gaming sessions | 2026-07-19 |
| Cloud CRM | Solo sync + Full master | 2026-07-19 |
| Docs reorganization | 85+ pages with per-project structure | 2026-07-19 |
| Template cleanup | 60+ deduplicated templates | 2026-06-30 |
| CI gates | Markdown link + extras validation | 2026-07-01 |
| Django portal | Shared viewsets across POS editions | 2026-07-19 |
| Settings inlining | Per-site Dynaconf configs | 2026-06-30 |

### 🔄 In Progress / Planned

| Area | What | Priority |
|------|------|----------|
| Cypercloud platform | Phase 1: Stripe billing + API tokens | 🔴 High |
| Cypercloud platform | Phase 2: System builder (POS, CRM, LMS templates) | 🟡 Medium |
| Feature matrix completion | database.md for Cypercloud + POS | 🟢 Low |
| POS Full polish | Multi-terminal stress testing | 🟡 Medium |
| django-fusion MCP | Model Context Protocol integration | 🟢 Low |
| WebAuthn/Passkeys | All Django sites | 🟢 Low |
| Multi-region deploy | CDN + edge inference | 🟢 Low |

### 🔀 Mergeable Content

| Priority | What | Recommendation |
|:--------:|------|----------------|
| 🔴 | 7 session summaries → 1 timeline | Merge into `sessions/timeline.md` |
| 🟡 | 12 phase reports → 1 phase-log.md | Consolidate duplicates |
| 🟡 | 5 pre-restructure snapshots | Archive as reference (don't merge — useful for diff history) |
| 🟢 | 10 deployment reports | Can consolidate into 3-4 topic-based pages |

---

## Naming Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| `PHASE<N>_*.md` | `PHASE4_COMPLETE_STATUS_REPORT.md` | Phase completion docs |
| `SESSION_*.md` | `SESSION_SUMMARY.md` | Session records |
| `*_COMPLETE*.md` | `PROJECT_MODERNIZATION_COMPLETE.md` | Milestone markers |
| UPPER_SNAKE | `FINAL_IMPLEMENTATION_REPORT.md` | Reports |
| `*.txt` | `EXECUTION_LOG.txt` | Logs/status |
| `README.md` | Directory index | Overview files |
| `old-*` | `old-todos/` | Archived/moved content |

---

## Quick Navigation

| Section | What to find |
|---------|-------------|
| [`deployment/`](deployment/) | Production deploy logs, certificate setup, audit reports |
| [`sessions/`](sessions/) | Dev session records, completion reports, handoff docs |
| [`phases/`](phases/) | Phase-by-phase implementation history |
| [`plans/`](plans/) | Task lists, next steps, status tracking |
| [`pre-restructure/`](pre-restructure/) | Pre-rename project docs (historical reference) |
| [`technical/`](technical/) | Architecture, auth, components, dev workflow, infrastructure |

---

→ [Back to main docs](../)
