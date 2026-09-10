---
Object type: Reference
Tags: reference, api, specification, technical, documentation
Status: Active
---

# Reference — Technical Facts & Specifications

> **Description:** API, CLI, database, configuration, i18n, schema, or SDK facts. The authoritative source for technical specifications.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Published, Deprecated |
| `Category` | Select | API, CLI, Database, Configuration, i18n, Schema, SDK |
| `Related Editions` | Relation → Edition | Editions the reference applies to |
| `Version` | Text | Documented version |
| `Related Architecture` | Relation → Architecture | System context |
| `Related Pipelines` | Relation → Pipeline | Automation that validates the reference |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Record verifiable facts — endpoint contracts, config keys, schema fields, version numbers. Update when the underlying system changes. Link to architecture for context and features for usage examples.

## Graph

Reference → Related Editions → Edition · Reference → Related Architecture → Architecture · Reference → Related Pipelines → Pipeline.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../references/_index.md` — References directory
- → `api.md` — API object type