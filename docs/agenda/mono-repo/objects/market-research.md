---
Object type: Market Research
Tags: market-research, product, validation
Status: Published
---

# Market Research — Object Type

> **Description:** Evidence-based research about a market, customer segment, competitor category, pricing hypothesis, or product decision.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Active, Published, Archived |
| `Type` | Select | Product, Edition, Country, Competitor, Pricing |
| `Editions` | Relation → Edition | Editions covered by the research |
| `Related Plans` | Relation → Plan | Decisions informed by the research |
| `Evidence` | Text | Sources, interviews, pilots, or observed signals |
| `Validation Questions` | Text | Questions still requiring customer evidence |
| `Tags` | Multi-select | Region, segment, product, and lifecycle labels |

## Use

Create one object for a focused research question. Separate observed evidence from assumptions, record the target edition and geography, and link the resulting decision to a Plan or Goal. Do not present unverified market size or pricing as fact.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../plans/pos-market-research.md` — POS edition research
- → `edition.md` — Edition object type
