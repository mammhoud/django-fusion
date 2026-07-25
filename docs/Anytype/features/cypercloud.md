---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Tags:
    - cypercloud
    - ai
    - cloud
Status: Planned
Edition: Cloud
---

# CyperCloud — AI Chat Customizer Platform

> **Type:** Feature ✨
> **Platform:** Cypercloud interface — customize AI chat behavior, appearance, and content for each site.

---

## Overview

CyperCloud is the AI Chat Customizer platform that enables users to:
- **Customize AI chat** behavior and personality per-site
- **Manage prompts** and response templates for each application context
- **Configure AI model** selection and parameters
- **Brand the chat interface** to match each site's color scheme and tone

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Repopath** | `projects/cypercloud/` |
| **Color** | Cyan (#06b6d4) / Sky blue (#0ea5e9) — representing AI intelligence and cloud integration |
| **Platforms** | Web (localhost:5073) |
| **Auth** | django-allauth + django-fusion auth mixins |
| **AI Engine** | ceptor-ai library (MCP server, agent generation) |

---

## Color Palette: CyperCloud Cyan

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#06b6d4` (Cyan-500) | AI chat bubbles, active prompts, accent buttons |
| Surface | `#ecfeff` / `#164e63` | Chat panels (light/dark) |
| Accent | `#0ea5e9` (Sky-500) | Links, model selector highlights |
| Background | `#f0f9ff` / `#0c4a6e` | Main chat area |

---

## Key Capabilities

- **Chat Interface** — Customizable AI chat widget embedded in any site
- **Prompt Management** — Save, version, and reuse prompt templates across sites
- **Model Configuration** — Select AI model, temperature, max tokens per deployment
- **Brand Integration** — Match chat colors to site theme (teal default, blue corporate, etc.)
- **Analytics** — Track chat usage, popular queries, satisfaction ratings

---

## Related Features

- → `../architecture/website-descriptions.md` — Site descriptions
- → `../../libs/ceptor-ai/AGENTS.md` — AI engine details
- → `integration.md` — Platform integration
- → `../README.md` — Master index
