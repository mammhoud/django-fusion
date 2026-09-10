---
Object type: Component
Tags: component, ui-component, formint, design-system
Status: Active
Related Features: pos-system
Related Styles: design-tokens
---

# Formint Design System — Shared UI Package

> **Description:** The shared UI package for Formints (`projects/formints/packages/design-system/`) — reusable components and tokens across the POS editions.

## Scope

- Shared React/Astro components for Community/Standard/Pro frontends
- Theme system (see the POS theme case study: `../blog/2026-07-24-pos-theme-system.md`)

## Rules

- Reuse over duplication across editions; edition-specific behavior via props/config, not forks
- Tokens come from the shared style system

## Related

- → `django-fusion-components.md` — Backend component framework
- → `../styles/design-tokens.md` — Design tokens
- → `../objects/component.md` — Component object type