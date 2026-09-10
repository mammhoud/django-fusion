---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: API
Tags: api, reference
Status: Published
---

# API — Endpoint Definitions & Schemas

> **Type:** API 📡
> **Layout:** Page
> **Description:** REST endpoints, GraphQL queries, WebSocket events, and webhook receivers across all POS editions and web applications.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Stable, Beta, Deprecated, Experimental | API maturity |
| `Method` | Select | GET, POST, PUT, PATCH, DELETE | HTTP method |
| `Endpoint` | Text | — | URL path |
| `Auth Required` | Boolean | — | Whether authentication is needed |
| `Rate Limited` | Boolean | — | Whether rate limiting applies |
| `Version` | Text | — | API version |
| `Edition` | Relation → Edition | — | Which edition(s) include this |
| `Related Features` | Relation → Feature | — | Related feature |
| `Related Components` | Relation → Component | — | Related UI component |
| `Related Integrations` | Relation → Integration | — | Related external integration |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

A Component calls an API, which integrates an Integration and implements a Feature.

| Relation | Target |
|----------|--------|
| calls | API |
| integrates | Integration |
| implements | Feature |

---

## Related

- → `_object-types.md` — All type definitions
- → `component.md` — Component entity
- → `integration.md` — Integration entity
- → `feature.md` — Feature entity
