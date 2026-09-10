---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Configuration
Tags: configuration, setup
Status: Published
---

# Configuration — Environment & Build Settings

> **Type:** Configuration ⚙️
> **Layout:** Page
> **Description:** Environment variables, build settings, database config, proxy setup, and deployment parameters.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Category` | Select | Environment, Build, Database, Proxy, Auth, Deployment | Config category |
| `Platform` | Multi-select | macOS, Linux, Windows, Docker | Target platform |
| `Required` | Boolean | — | Whether this configuration is mandatory |
| `Default Value` | Text | — | Default value if not overridden |
| `Related Editions` | Relation → Edition | — | Which edition(s) this applies to |
| `Related Guides` | Relation → Guide | — | Guide that references this config |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Related Editions | Edition |
| Related Guides | Guide |

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../guides/configuration.md` — Configuration guide
- → `../guides/install/_index.md` — Install guides
