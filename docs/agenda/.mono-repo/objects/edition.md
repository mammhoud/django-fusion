---
Object type: Edition
Tags: edition, product, pos, community, professional, saas
Status: Active
---

# Edition — Product Scope

> **Description:** A customer-facing product tier with defined capabilities, audience, pricing hypothesis, compatibility, and market evidence.

## Current editions

| Edition | Scope | Audience |
|---|---|---|
| Community | Free/self-hosted core POS | Small operators, developers, evaluators |
| Formint Professional | Offline restaurant operations and premium workflows | Growing restaurants, cafés, cloud kitchens, chains |
| POS Cloud | Hosted tenants, branches, analytics, billing, and managed services | Chains, franchises, and operators wanting remote management |

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Active, Deprecated, Planned |
| `Version` | Text | Current version identifier |
| `Release Date` | Date | Release or target date |
| `Related Features` | Relation → Feature | Features included in this edition |
| `Excluded Features` | Relation → Feature | Features intentionally outside this edition |
| `Target Audience` | Select | Individual, Small Business, Enterprise |
| `Pricing Tier` | Select | Free, Starter, Professional, Enterprise |
| `Compatibility` | Relation → Reference | Technical compatibility |
| `Related Goals` | Relation → Goal | Strategic goals |
| `Related Research` | Relation → Market Research | Evidence behind scope and pricing |
| `Related Plans` | Relation → Plan | Product and delivery plans |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Create one Edition object per current customer-facing tier. Link each edition to its features, research, plans, and compatibility references.

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relation guide
- → `../architecture/editions.md` — Canonical boundaries
- → `../plans/pos-market-research.md` — Market evidence
- → `../plans/formint-pos-professional-plan.md` — Professional plan
- → `../products/formint-pos.md` — Product description
