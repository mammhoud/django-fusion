---
title: Team Notes
description: Meeting notes, decisions, blockers, and team communication log — the project's institutional memory
navigation:
  title: Team Notes
  icon: i-lucide-notebook-pen
object:
  type: "guide"
  id: "agenda.team-notes"
attributes:
  source_path: "agenda/team-notes.md"
  canonical_route: "/docs/en/agenda/team-notes"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - team-notes
  - decisions
  - meetings
  - log
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Meeting Agenda"
    to: "/agenda/meeting-agenda"
    icon: "i-lucide-calendar"
  - label: "Feature Tracking"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
---

# 📝 Team Notes — Meeting Notes, Decisions & Blockers

> **Purpose:** The team's written memory — meeting notes, key decisions, blockers, and notable events. Searchable, date-stamped, and linked to features and tasks.
> **Last updated:** 2026-08-31

---

## 📋 Note Entry Format

Every entry should be date-stamped and categorized:

```markdown
### YYYY-MM-DD — [Meeting type / Event] — [Brief title]

**Attendees:** @member1, @member2, @member3

**Topic / Agenda:** [What this meeting/event was about]

**Key points:**
- Point 1
- Point 2

**Decisions made:**
- Decision 1 — [rationale if notable]
- Decision 2

**Action items:**
- [ ] @assignee — Task description — due YYYY-MM-DD
- [ ] @assignee — Task description — due YYYY-MM-DD

**Blockers / Risks:**
- Blocker description — owner: @member

**Links:**
- Related feature: [`feature-tracking.md`](../feature-tracking.md) § Feature Name
- Related task: [`task-tracking.md`](../task-tracking.md) § Task Title
- Related plan: [`plans/path.md`](../plans/path.md)
- Meeting agenda: [`meeting-agenda.md`](../meeting-agenda.md)
```

---

## 🗓️ Meeting Notes Log

### 2026-08-31 — Project Kickoff — Agenda System Setup

**Attendees:** Workspace team

**Topic / Agenda:** Setting up the project agenda tracking system — feature tracking, case studies, task tracking, team notes, completion checklist, and meeting templates.

**Key points:**
- Anytype documentation was reviewed as a reference for object-based knowledge management
- Anytype uses Objects, Types, Properties, and Links as its core model — analogous to how we track Features, Tasks, and Decisions
- The agenda system mirrors this: Features are Types, Tasks are Objects with Properties (status, assignee, due), and links connect everything
- Mermaid diagrams are the standard for architecture documentation in case studies
- Docus frontmatter with object/attributes/tags/links is the canonical format for all docs

**Decisions made:**
- Agenda system files live in `docs/agenda/` with a MAIN.md hub
- Feature tracking mirrors the priority roadmap in `features/feature-roadmap.md`
- Every shipped feature should have a case study with at least one mermaid diagram
- Task tracking is sprint-based and maps to features
- Team notes capture decisions that affect multiple files

**Action items:**
- [x] Create `docs/agenda/MAIN.md` — hub/index — Done
- [x] Create `docs/agenda/feature-tracking.md` — feature lifecycle tracking — Done
- [x] Create `docs/agenda/case-studies.md` — case study template with mermaid — Done
- [x] Create `docs/agenda/task-tracking.md` — sprint task board — Done
- [x] Create `docs/agenda/team-notes.md` — meeting notes and decisions — Done
- [ ] Create `docs/agenda/meeting-agenda.md` — meeting templates — Pending
- [ ] Create `docs/agenda/completion-checklist.md` — project closeout checklist — Pending
- [ ] Add initial active features to feature-tracking.md — Pending
- [ ] Add initial sprint tasks to task-tracking.md — Pending

**Blockers / Risks:**
- None at this stage — system is being stood up

**Links:**
- Related plan: [`plans/README.md`](../plans/README.md)
- Related roadmap: [`features/feature-roadmap.md`](../features/feature-roadmap.md)
- Anytype docs reference: [Objects](https://doc.anytype.io/anytype/create/objects), [Types](https://doc.anytype.io/anytype/organize/types), [Properties](https://doc.anytype.io/anytype/organize/properties)

### 2026-09-03 — Infrastructure & Docs Workstreams — Worker Assets, Coder Deploy, Shared Assets, Anytype Research

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Four approved workstreams: (1) minimize assets data in scheduler/worker containers, (2) verify + redeploy Coder, (3) audit shared assets dir between precis-ctc and precis-main with fallback, (4) research anytype.io and record agenda/project-separation extensibility.

**Key points:**
- Shared tasks stack (`projects/docker-compose.tasks.yml`) bind-mounted the whole monorepo `projects/assets` tree into worker+scheduler; CTC tools compose mounted the media tree into scheduler+worker even though only the worker needs it
- Docker host had no Postgres/Redis/Coder running; Precis scheduler had crashed at boot waiting on Redis
- CTC settings `MEDIA_ROOT` default resolved to a stray precis-local rendition tree (`projects/precis/assets/media/ctc-research`, 380K) while compose, docstring, and CHANGELOG all cite the monorepo tree (`projects/assets/media/ctc-research`, 139M) as canonical
- `tests/test_shared_media.py` still asserted the retired `application/proxy` shared-proxy topology; the live contract is `assets-proxy` in `application/tools`
- Anytype (anytype-ts repo + doc.anytype.io) reviewed: objects/types/properties/relations + Queries vs Collections + per-space type isolation are the transferable concepts

**Decisions made:**
- Worker/scheduler containers should stay minimal: no assets/media data except where a task genuinely writes media (CTC worker keeps its mount; scheduler never needs it)
- CTC local-dev `MEDIA_ROOT` default should match the canonical monorepo shared tree; containers override via env var
- The shared-assets contract (per-site staticfiles + per-host nginx fallback to shared roots) is validated by the rewritten `tests/test_shared_media.py`
- Anytype findings recorded as a proposal doc, not an integration commitment

**Action items:**
- [x] Remove assets/media binds from shared worker/scheduler + CTC scheduler — Done (2026-09-03)
- [x] Deploy Postgres/Redis + Coder; restart Precis scheduler — Done (2026-09-03)
- [x] Fix CTC MEDIA_ROOT default; run manage.py check — Done (2026-09-03)
- [x] Rewrite tests/test_shared_media.py to assets-proxy topology — Done (26/26 pass, 2026-09-03)
- [x] Write docs/agenda/anytype-extensibility.md proposal — Done (2026-09-03)
- [ ] Review Anytype proposal items (#3 templates, #4 relation lint first) and schedule into a sprint — Pending

**Blockers / Risks:**
- None blocking; stray 380K rendition tree at `projects/precis/assets/media/ctc-research` is leftover runtime data from the old default — safe to leave (gitignored) or delete after confirmation

**Links:**
- Related proposal: [`anytype-extensibility.md`](./anytype-extensibility.md)
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2 (2026-09-03 rows)
- Related test: [`tests/test_shared_media.py`](../../tests/test_shared_media.py)

---

## ✍️ Adding New Notes

When you have a meeting or make a significant decision:

1. **Copy the entry format** above
2. **Date it** with the meeting date
3. **Categorize** — Meeting type (Sprint Planning, Standup, Review, Retro, Decision, Incident)
4. **Link out** — Reference the relevant feature, task, or plan
5. **Note action items** with assignees and due dates
6. **Note blockers** with owners

---

## 🔍 Searching Notes

| What you're looking for | Search in |
|------------------------|-----------|
| A decision about feature X | `rg "Feature Name" docs/agenda/team-notes.md` |
| Who was assigned task Y | `rg "Task title" docs/agenda/team-notes.md` |
| When a blocker was raised | `rg "Blocked" docs/agenda/team-notes.md` |
| What was decided in sprint N | `rg "Sprint N" docs/agenda/team-notes.md` |

---

## 🔗 Related

| Topic | Path |
|-------|------|
| Meeting agenda templates | [./meeting-agenda.md](./meeting-agenda.md) |
| Feature tracking (decisions affect features) | [./feature-tracking.md](./feature-tracking.md) |
| Task tracking (decisions affect tasks) | [./task-tracking.md](./task-tracking.md) |
| Plans registry (major decisions become plans) | [`../plans/README.md`](../plans/README.md) |

---

## 🔄 Maintenance

- **Add notes after:** Every meeting, every significant decision, every incident
- **Update notes when:** Action items complete, blockers resolve, decisions change
- **Reference in PRs:** Link to the relevant note when a PR implements a decision
- **Archive old notes:** When a project closes, move notes to an archive section or file

---

## Remarks & Notes

- Team notes are not a replacement for detailed plans — they're the decision log
- If a decision affects multiple files, write it here AND update a plan
- Action items without owners and due dates are just wishes — always assign them
- The note format is intentionally lightweight — don't over-engineer it

<!-- AI-generated: review needed -->
