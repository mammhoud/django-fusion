---
title: Structa Cloud — Company Profile 🔒
description: Company overview, mission, vision, core focus areas, product ecosystem, technology stack, and competitive advantages of Structa Cloud — aligned with the real monorepo product set.
navigation:
  title: Company profile 🔒
  icon: i-lucide-building-2
object:
  type: "private-profile"
  id: "docs.startup.company-profile"
attributes:
  source_path: "startup/company-profile.md"
  canonical_route: "/docs/en/startup/company-profile"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - company-profile
  - vision
  - mission
  - private
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Product profiles 🔒"
    to: "/startup/product-profiles"
    icon: "i-lucide-boxes"
  - label: "Revenue model 🔒"
    to: "/startup/revenue-model"
    icon: "i-lucide-chart-line"
---

# 🏢 Structa Cloud — Company Profile 🔒

> **Internal only.** One company narrative for investors, partners, and the
> executive deck. Product names below map to real monorepo paths; anything
> marked 🔴 is a vision product, not shipped code.

<!-- AI-generated: review needed -->

## Overview

Structa Cloud is a technology company focused on building intelligent software
platforms that simplify business operations, digital experiences, education,
research, and content management. The company develops SaaS products,
AI-powered solutions, and enterprise platforms for organizations seeking
scalable and modern digital infrastructure.

## Mission

Build intelligent products that help organizations operate, learn, publish,
collaborate, and grow.

## Vision

Become a leading provider of cloud software and AI-powered business platforms
across the Middle East and international markets.

## Core Focus Areas

- **Business Operations** — CRM, customer success, marketing, support, finance, HR
- **Education** — learning platforms, training systems, certification systems
- **Research** — academic research, scientific publishing, medical research
- **Digital Experience** — CMS, website builder, landing pages, knowledge platforms
- **Artificial Intelligence** — AI agents, workflow automation, knowledge retrieval, content generation

## Product Ecosystem

| Product | Status | Monorepo path | What it is |
|---------|--------|---------------|------------|
| 🎓 Precis (LMS + landing) | 🟢 live | `projects/structa.cloud/` | Learning platform + marketing/catalog shell in one stack |
| 🤝 Loop-CRM | 🟢 live | `projects/loop-crm/` | Unified sales + marketing CRM |
| 💳 Formint POS | 🟢 live | `projects/formints/` | Offline-first multi-edition restaurant/café POS |
| 🤖 Syntara (Cypercloud) | 🟡 beta | `projects/syntara/` | AI chat + template customization runtime |
| 🧩 django-fusion | 🟢 live | `libs/django-fusion/` | Shared development framework powering all Django products |
| 🎨 Precis CMS | 🔴 vision | — | Enterprise content management system |
| 🛠️ Precis Builder | 🔴 vision | — | Website & application generation platform |
| 🔬 Precis Research | 🔴 vision | — | Academic research & publishing platform (CTC sample is the seed) |

> Vision products are profiled in [`product-profiles.md`](product-profiles.md);
> never present them as shipped code in external materials.

### Reference samples — agentic coding with Precis

> Built through agentic coding on the Precis stack and kept as seeds/references
> rather than commercial products:
>
> 🏥 **CTC Research** (`projects/precis/precis-ctc/`) — a sample medical research
> center site (ctc-research.com) produced with agentic coding + Precis, showing
> the EN/AR publishing workflow and production pipeline. It seeds the
> 🔬 Precis Research vision product (see [`precis-ctc.md`](precis-ctc.md)).

## Technology Stack

- **Backend** — Python, Django, Wagtail, PostgreSQL, Redis
- **Frontend** — Astro, HTMX, Alpine.js, Tailwind CSS
- **Infrastructure** — Docker, Docker Compose, Traefik/Nginx, Kubernetes-ready
- **AI** — LLM integration, RAG, AI agents, MCP (Model Context Protocol), knowledge systems

## Competitive Advantages

- **Unified product ecosystem** — one monorepo, one component system, one deploy story
- **AI-native architecture** — MCP and agent tooling built into the framework
- **Multi-tenant platform** — shared Django foundation across every product
- **Self-hosting & data ownership** — customers keep their data, no vendor lock-in
- **Modular framework** — django-fusion accelerates every product
- **Rapid deployment** — one Compose/Traefik stack deploys the whole portfolio

## Future Vision

Structa Cloud aims to create an interconnected software ecosystem where every
product shares a common identity, AI layer, analytics layer, and automation
engine — a seamless experience across all business and educational workflows.

## Remarks & Notes

- Product names and live/vision status must stay in sync with
  [`docs/startup/README.md`](README.md) and the per-product strategy docs.
- This section is private by policy; strip the 🔒 markers and vision gaps before
  any external publication.
- The 25-slide executive deck that quotes this profile lives at
  [`presentation.md`](presentation.md).
