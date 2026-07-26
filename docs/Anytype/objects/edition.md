---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Edition
Tags: edition, product, version
Status: Published
---

# Edition — Product Tier & Scope Definition

> **Type:** Edition 📦
> **Layout:** Page
> **Description:** Product tier definitions — feature scope, pricing, target audience, and lifecycle for each POS edition.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Active, Deprecated, Planned | Lifecycle stage |
| `Version` | Text | — | Current version identifier |
| `Release Date` | Date | — | When edition was/will be released |
| `FeaturesIncluded` | Relation → Feature | — | Features included in this edition |
| `FeaturesExcluded` | Relation → Feature | — | Features excluded from this edition |
| `Target Audience` | Select | Individual, Small Business, Enterprise | Who this is for |
| `Pricing Tier` | Select | Free, Starter, Professional, Enterprise | Pricing model |
| `Compatibility` | Relation → Reference | — | Technical compatibility/references |
| `Related Goals` | Relation → Goal | — | Goals this edition supports |
| `Dependencies` | Relation → Reference | — | System dependencies |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage in Knowledge Graph

```
Edition 📦 ─── FeaturesIncluded ──→ Feature ✨
    │
    ├── FeaturesExcluded ──→ Feature ✨
    ├── Compatibility ──────→ Reference 📚
    ├── Related Goals ──────→ Goal 🎯
    └── Dependencies ───────→ Reference 📚
```

---

## Related

- → `_object-types.md` — All type definitions
- → `../architecture/editions.md` — Edition architecture overview
- → `../features/comparison-matrix.md` — Feature grid
- → `../editions/` — Editions directory
