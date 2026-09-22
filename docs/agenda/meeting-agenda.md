---
title: Meeting Agenda
description: Ready-to-use meeting agenda templates — sprint planning, standup, review, retrospective, feature review, and project closeout
navigation:
  title: Meeting Agenda
  icon: i-lucide-calendar
object:
  type: "guide"
  id: "agenda.meeting-agenda"
attributes:
  source_path: "agenda/meeting-agenda.md"
  canonical_route: "/docs/en/agenda/meeting-agenda"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - meetings
  - agenda
  - templates
  - sprint
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Task Tracking"
    to: "/agenda/task-tracking"
    icon: "i-lucide-check-square"
  - label: "Team Notes"
    to: "/agenda/team-notes"
    icon: "i-lucide-notebook-pen"
---

# 🗓️ Meeting Agenda — Templates for Every Meeting Type

> **Purpose:** Reusable agenda templates for sprint planning, daily standup, sprint review, retrospective, feature review, and project closeout. Copy the template, fill it in, and record notes in `team-notes.md`.
> **Last updated:** 2026-08-31

---

## 📋 How to Use These Templates

1. **Copy the template** for your meeting type
2. **Fill in** dates, attendees, and specifics
3. **Run the meeting** using the agenda as your guide
4. **Record notes** in `team-notes.md` with the date and meeting type

---

## 1. Sprint Planning

**When:** Start of each sprint
**Duration:** 1–2 hours (adjust to team size)
**Attendees:** Full team

### Agenda

```
## Sprint [N] Planning — [Date]

**Sprint dates:** [Start] to [End]
**Goal:** [One-sentence sprint goal]

---

### 1. Review previous sprint (10 min)
- What was completed?
- What carried over and why?
- Any lessons to apply?

### 2. Review current feature status (10 min)
- Features in `feature-tracking.md` — what's In Progress, what's Blocked?
- Any features ready to move to Review or Shipped?

### 3. Capacity check (5 min)
- Team availability this sprint (vacations, other work)
- Available person-days/hours

### 4. Prioritize and select tasks (30–60 min)
- Pull tasks from `task-tracking.md` Backlog
- Assign priority (P0/P1/P2/P3)
- Assign tasks to team members
- Confirm estimates

### 5. Identify risks and blockers (10 min)
- Any external dependencies?
- Any technical risks?
- Any scope concerns?

### 6. Confirm sprint goal and commit (5 min)
- Restate the sprint goal
- Team confirms commitment

---

**Action items:**
- [ ] @assignee — Task — due [date]
- [ ] @assignee — Task — due [date]

**Notes:** Record in `team-notes.md` as "Sprint Planning"
```

---

## 2. Daily Standup

**When:** Every day (same time)
**Duration:** 15 minutes max
**Attendees:** Full team (or representative)

### Agenda

```
## Daily Standup — [Date]

---

### Each person answers (1–2 min each):

1. **What did I complete yesterday?**
   - [Task/feature completed]
   - Any relevant links (PR, commit, deployment)

2. **What am I working on today?**
   - [Task/feature in progress]
   - Current status from `task-tracking.md`

3. **Any blockers or risks?**
   - [Blocker description] — owner: @person if external
   - [Risk description]

---

**Blockers raised:** [List any — these need immediate attention]
**Notes:** Record briefly in `team-notes.md` as "Daily Standup"
```

> **Keep it short.** If a topic needs discussion, take it offline or schedule a separate conversation.

---

## 3. Sprint Review

**When:** End of each sprint
**Duration:** 1 hour
**Attendees:** Full team + stakeholders (if applicable)

### Agenda

```
## Sprint [N] Review — [Date]

**Sprint:** [Start] to [End]

---

### 1. Demo completed work (30–40 min)
- Walk through each shipped feature
- Show case study entries if written
- Demonstrate in live environment / staging

### 2. Review metrics (10 min)
- Tasks completed vs planned (from `task-tracking.md`)
- Features moved to Shipped (from `feature-tracking.md`)
- Any carried-over tasks and why

### 3. Collect feedback (10 min)
- Stakeholder feedback
- Team feedback on the work
- Any quality concerns

### 4. Plan next steps (10 min)
- What moves to the next sprint?
- Any immediate follow-ups from this sprint's work?

---

**Action items:**
- [ ] @assignee — Task — due [date]

**Notes:** Record in `team-notes.md` as "Sprint Review"
```

---

## 4. Retrospective

**When:** End of each sprint (can combine with review or separate)
**Duration:** 45–60 minutes
**Attendees:** Full team

### Agenda

```
## Sprint [N] Retrospective — [Date]

---

### 1. Set the stage (5 min)
- Remind the team: this is a safe space
- Focus on processes, not people
- Goal: identify 1–3 concrete improvements

### 2. Gather data (10 min)
- What went well this sprint?
- What didn't go well?
- What surprised us?

### 3. Generate insights (10 min)
- Why did things go well?
- Why didn't things go well?
- Patterns or root causes?

### 4. Decide what to do (15 min)
- Pick 1–3 action items for the next sprint
- Each action item needs: owner, description, due date
- These become tasks in `task-tracking.md`

### 5. Close (5 min)
- Summarize the action items
- Thank the team

---

**Action items for next sprint:**
- [ ] @assignee — Improvement — due [date]
- [ ] @assignee — Improvement — due [date]

**Notes:** Record in `team-notes.md` as "Sprint Retrospective"
```

---

## 5. Feature Review

**When:** When a feature moves to Review status in `feature-tracking.md`
**Duration:** 30–60 minutes
**Attendees:** Feature owner, reviewer(s), stakeholder(s) if needed

### Agenda

```
## Feature Review — [Feature Name]

**Feature:** [Feature name from `feature-tracking.md`]
**Current status:** Review
**Owner:** @person

---

### 1. Feature overview (5 min)
- What does this feature do?
- What problem does it solve?
- Link to feature entry in `feature-tracking.md`

### 2. Implementation walkthrough (15–20 min)
- Architecture: show any relevant mermaid diagram
- Key decisions made during implementation
- Code walkthrough of critical paths

### 3. Verification (10 min)
- Acceptance criteria from feature entry — check each one
- Test results
- Any edge cases or known limitations

### 4. Documentation check (5 min)
- Is there a case study entry in `case-studies.md`?
- Is the feature roadmap updated?
- Is the plans registry updated?

### 5. Decision (5 min)
- Approve → move to Shipped
- Revise → return to In Progress with notes
- Defer → move back to Review with a reason

---

**Decision:** [Approve / Revise / Defer]

**If revise:**
- [ ] @owner — Required changes — due [date]

**Notes:** Record in `team-notes.md` as "Feature Review — [Feature Name]"
```

---

## 6. Project Closeout

**When:** When a project or major feature set is complete
**Duration:** 30–60 minutes
**Attendees:** Project owner, team, stakeholders

### Agenda

```
## Project Closeout — [Project/Feature Set Name]

**Project:** [Name]
**Completion date:** [Date]
**Owner:** @person

---

### 1. Confirm completion (10 min)
- Run through `completion-checklist.md`
- Confirm all features marked Shipped in `feature-tracking.md`
- Confirm all tasks marked Done in `task-tracking.md`

### 2. Review deliverables (10 min)
- Case studies written? (in `case-studies.md`)
- Plans updated? (in `plans/README.md`)
- Roadmap updated? (in `features/feature-roadmap.md`)
- Documentation validated?

### 3. Lessons learned (15 min)
- What went well?
- What would we do differently?
- Any surprises or unexpected outcomes?

### 4. Handoff / next steps (10 min)
- Is there ongoing maintenance?
- Are there follow-on features?
- Who owns ongoing support?

### 5. Closeout decision (5 min)
- Officially close the project
- Archive any temporary tracking

---

**Closeout decision:** [Confirmed / Pending items]

**Follow-on items:**
- [ ] @assignee — Task — due [date]

**Notes:** Record in `team-notes.md` as "Project Closeout — [Project Name]"
```

---

## 🔄 Template Customization

| Template | Typical cadence | Key output |
|----------|----------------|------------|
| Sprint Planning | Every sprint start | Committed task list with assignees |
| Daily Standup | Daily | Blocker awareness |
| Sprint Review | Every sprint end | Demo + feedback + metrics |
| Retrospective | Every sprint end | 1–3 process improvements |
| Feature Review | Per feature completion | Shipped decision |
| Project Closeout | Per project completion | Closeout confirmation |

> **Adjust durations** to your team size and meeting norms. The content matters more than the timing.

---

## 🔗 Related

| Topic | Path |
|-------|------|
| Agenda content model (definition + reference contract) | [./CONTENT_MODEL.md](./CONTENT_MODEL.md) |
| Task tracking (use during planning/standup) | [./task-tracking.md](./task-tracking.md) |
| Feature tracking (use during planning/review) | [./feature-tracking.md](./feature-tracking.md) |
| Team notes (record all meetings here) | [./team-notes.md](./team-notes.md) |
| Completion checklist (use during closeout) | [./completion-checklist.md](./completion-checklist.md) |

---

## Remarks & Notes

- Templates are starting points — adapt them to your team's actual needs
- The most important output of any meeting is **action items with owners and due dates**
- If a meeting doesn't produce action items or decisions, question whether it was needed
- Always record notes in `team-notes.md` — even a short summary is better than nothing

<!-- AI-generated: review needed -->
