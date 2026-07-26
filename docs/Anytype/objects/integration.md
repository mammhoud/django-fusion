---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Integration
Tags: integration
Status: Published
---

# Integration — Third-Party Connectors

> **Type:** Integration 🔗
> **Layout:** Page
> **Description:** External service connectors — payment gateways, email/SMS providers, CRM, auth, and analytics.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Active, Planned, Deprecated, Broken | Integration health |
| `Category` | Select | Payment, CRM, Email, SMS, Analytics, Auth, Storage | Service type |
| `Provider` | Text | — | Service provider name |
| `Auth Type` | Select | API Key, OAuth, JWT, Basic | Authentication method |
| `Edition` | Relation → Edition | — | Which edition(s) include this |
| `Related API` | Relation → API | — | API endpoints used |
| `Related Feature` | Relation → Feature | — | Related features |
| `Related Pipeline` | Relation → Pipeline | — | Deployment/config pipeline |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

```
Feature ✨ ── needs ──→ Integration 🔗 ── connects ──→ External Service
                               │
                               └── exposes ──→ API 📡
```

---

## Related

- → `_object-types.md` — All type definitions
- → `../integrations/` — Integrations directory
- → `api.md` — API entity
- → `feature.md` — Feature entity
- → `pipeline.md` — Pipeline entity
