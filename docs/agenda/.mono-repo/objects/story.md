---
Object type: Story
Tags: story, narrative, journey, founder, origin
Status: Published
---

# Story — Founder Journey & Project Narrative

> **Type:** Story 📖
> **Layout:** Page
> **Description:** Narrative record of how the project started and evolved — the founder's journey through technologies, products, packages, and platform decisions. Chronicles decisions, experiments, and lessons in chronological phases.

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Draft, Ongoing, Published, Archived | Narrative state |
| `Author` | Relation → Person | — | Who tells the story |
| `Start Date` | Date | — | When the phase/narrative began |
| `End Date` | Date | — | When the narrative concluded |
| `Phase` | Select | Foundations, Experimentation, Platform, Suite, Enterprise | Story chapter or phase |
| `Related Goals` | Relation → Goal | — | Achievements this phase drove |
| `Related Plans` | Relation → Plan | — | Plans this phase informed |
| `Related Products` | Relation → Product | — | Products born from this phase |
| `Related Features` | Relation → Feature | — | Capabilities created along the way |
| `Related Decisions` | Relation → Decision | — | Key choices recorded |
| `Tags` | Multi-select | — | Cross-cutting labels |

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Author | Person |
| Related Goals | Goal |
| Related Plans | Plan |
| Related Products | Product |
| Related Features | Feature |
| Related Decisions | Decision |

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `note.md` — Note type (for informal captures)
- → `../stories/_index.md` — Stories directory
- → `../goals/achievement-board.md` — Achievement board
- → `../plans/startup-planner.md` — Startup planning
