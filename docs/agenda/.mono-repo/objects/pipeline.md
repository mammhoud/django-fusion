---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Pipeline
Tags: pipeline, ci, cd
Status: Published
---

# Pipeline — CI/CD Workflows & Build Steps

> **Type:** Pipeline 🔄
> **Layout:** Page
> **Description:** CI/CD pipeline definitions — build, test, deploy, and security automation workflows across all projects.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Active, Inactive, Failed | Pipeline health |
| `Type` | Select | CI, CD, Test, Deploy, Lint, Security | Pipeline purpose |
| `Provider` | Select | GitHub Actions, Docker, Custom | CI/CD provider |
| `Triggers` | Multi-select | Push, PR, Schedule, Manual | What starts the pipeline |
| `Related Releases` | Relation → Release | — | Releases deployed by this |
| `Related Reference` | Relation → Reference | — | Config references |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

A Release is deployed by a Pipeline, which runs on a Reference.

| Relation | Target |
|----------|--------|
| deployed by | Pipeline |
| runs on | Reference |

---

## Related

- → `_object-types.md` — All type definitions
- → `release.md` — Release entity
- → `../references/_index.md` — Reference entity
