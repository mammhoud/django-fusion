---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Goal
Tags: goal, strategy
Status: Published
---

# Goal — Strategic Objectives & Key Results

> **Type:** Goal 🎯
> **Layout:** Page
> **Description:** Strategic objectives with measurable key results — driving product, business, technical, and growth outcomes.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Active, Achieved, At Risk, Deprioritized | Current state |
| `Category` | Select | Product, Business, Technical, Design, Growth | Goal category |
| `Priority` | Select | Low, Medium, High, Critical | Importance level |
| `Target Date` | Date | — | Desired completion date |
| `Key Results` | Text (multi-line) | — | Measurable outcomes |
| `Edition` | Relation → Edition | — | Product edition alignment |
| `Related Features` | Relation → Feature | — | Features that serve this goal |
| `Related Tasks` | Relation → Task | — | Implementation tasks |
| `Related Milestones` | Relation → Milestone | — | Milestones toward this goal |
| `Related Plans` | Relation → Plan | — | Plans that address this goal |
| `Owner` | Relation → Person | — | Responsible person |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Edition | Edition |
| Related Features | Feature |
| Related Tasks | Task |
| Related Milestones | Milestone |
| Related Plans | Plan |
| Owner | Person |

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../goals/_index.md` — Goals directory
