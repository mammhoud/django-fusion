---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Tags: forms, crm
Status: Planned
Links:
    - CRM
---

# Custom Form — Dynamic Form Builder

> **Type:** Feature ✨
> **Description:** A flexible form builder for creating custom input forms — feedback, surveys, registrations, and data collection — integrated with the CRM system.

---

## Overview

The Custom Form feature enables administrators to:
- **Build custom forms** without coding — drag-and-drop field configuration
- **Collect structured data** from customers, employees, and site visitors
- **Integrate with CRM** — form submissions feed directly into customer records
- **Embed anywhere** — forms can be placed on any page via Wagtail snippets

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Sites** | All sites (CTC Research, LMS Demo, VResume) |
| **Color** | Violet (#8b5cf6) / Purple (#a855f7) — representing form interaction and data collection |
| **CRM Link** | Form submissions create/update CRM contact records |
| **Tech Stack** | django-fusion component system, Wagtail snippets, HTMX |

---

## Color Palette: Form Violet

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#8b5cf6` (Violet-500) | Submit buttons, active field borders |
| Surface | `#f5f3ff` / `#2e1065` | Form backgrounds (light/dark) |
| Accent | `#a855f7` (Purple-500) | Required field markers, helper text |
| Error | `#ef4444` (Red-500) | Validation errors |

---

## Field Types

- **Text Input** — Single-line text, email, URL, phone
- **Text Area** — Multi-line text for comments, descriptions
- **Select Dropdown** — Single and multi-select options
- **Checkboxes / Radio** — Binary and multiple choice
- **Date / Time** — Date picker, time selector
- **File Upload** — Document, image, and media uploads
- **Signature Pad** — Touch/click signature capture

---

## Related Docs

- → `external-integration.md` — CRM integration
- → `../../guides/development.md` — Adding form components
- → `../tasks/tasks-and-backlog.md` — Implementation task
- → `../README.md` — Master index
