---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Decision
Tags: decision, adr, architecture
Status: Published
---

# Decision — Architectural Decision Records (ADR)

> **Type:** Decision ⚡
> **Layout:** Page
> **Description:** ADRs documenting the rationale, context, and trade-offs behind key technical and architectural choices.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Proposed, Accepted, Deprecated, Superseded | ADR lifecycle state |
| `Category` | Select | Architecture, Technology, Process, Security, Performance | Decision category |
| `Date` | Date | — | When the decision was made |
| `Decision Maker` | Relation → Person | — | Who made the decision |
| `Supersedes` | Relation → Decision | — | Previous decision this replaces |
| `Related Architecture` | Relation → Architecture | — | Related architecture |
| `Related Features` | Relation → Feature | — | Related features |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## ADR Format

| Section | Description |
|---------|-------------|
| **Context** | What problem are we solving? What forces are at play? |
| **Options** | What alternatives were considered? |
| **Decision** | What did we choose, and why? |
| **Consequences** | What trade-offs, risks, and benefits follow? |

---

## Usage

An Architecture is documented by a Decision, which supersedes previous Decisions and is decided by a Person.

| Relation | Target |
|----------|--------|
| documented by | Decision |
| supersedes | Decision (previous) |
| decided by | Person |

---

## Related

- → `_object-types.md` — All type definitions
- → `../decisions/_index.md` — Decisions directory
- → `people.md` — Person/Decision Maker entity
- → `../architecture/_index.md` — Architecture docs
