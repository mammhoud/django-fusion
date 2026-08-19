---
title: Syntara (Cypercloud) — Market Strategy 🔒
description: Private strategy for Syntara — AI chat + template customization runtime. MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog.
navigation:
  title: Syntara strategy 🔒
  icon: i-lucide-bot
object:
  type: "private-strategy"
  id: "docs.startup.syntara"
attributes:
  source_path: "startup/syntara.md"
  canonical_route: "/docs/en/startup/syntara"
  source_of_truth: "repository-markdown"
  owner: "syntara"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - syntara
  - cypercloud
  - ai
  - saas
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "Syntara product docs"
    to: "/docs/en/syntara"
    icon: "i-lucide-bot"
---

# 🤖 Syntara (Cypercloud) — Market Strategy 🔒

> Private · Owner: `projects/syntara/` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

## 1. Market Strategy

- **Positioning:** For teams building AI chat experiences that must match their brand and stack, **Syntara** is the AI chat + template customization runtime that discovers templates, customizes code, and streams responses from self-hosted models (Ollama) or any provider — with no vendor lock-in.
- **Wedge:** **Template discovery + code customization** — instead of another chatbot widget, Syntara owns the "find the right AI template, adapt it, run it" workflow.
- **Go-to-market:** Developer-led: open-source visibility, MCP tooling, self-hosted demo; convert to managed streaming tier.
- **Moat:** Self-hosted model support (privacy), deep template registry, and a customization pipeline competitors treat as a black box.

## 2. MVP Canvas

| Block | Answer |
|-------|--------|
| **Problem** | Generic AI chats don't fit brand/stack; template code is copy-pasted and diverges; hosted AI costs + data concerns block adoption |
| **Solution** | Template discovery + code customization + streaming chat runtime (Django + webpack frontend, Ollama-backed) |
| **Key metrics** | Templates customized per user, chat sessions, stream latency, self-host conversion rate |
| **Unfair advantage** | Full runtime + template registry + MCP integration in one monorepo; provider-agnostic |
| **Channels** | GitHub, MCP ecosystem, dev communities, enterprise pilot via infra team |
| **Revenue model** | Open-core: self-hosted free tier; managed streaming + support subscription |
| **Cost structure** | Model inference is the variable cost; infra shared with the monorepo |
| **Timeline** | MVP runtime ✅ → managed tier → enterprise self-host pilots |

## 3. TAM / SAM / SOM

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Global AI chatbot / conversational AI platform spend | ~$15–20B (2025) | 🟡 | Public conversational-AI market reports |
| SAM | Custom AI chat + template tooling for SMB/teams (EU + MENA) | ~$500M–1B | 🔴 | Segment assumption |
| SOM | Year-3: 200–500 active teams | ~$1–2M ARR | 🔴 | PLG conversion assumptions |

> **SOM logic:** PLG funnel — free self-host → 2–5% conversion to managed tier at $50–150/mo. Validate funnel with the OSS community.

## 4. SaaS Services

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| Self-hosted runtime | Chat + customization, bring-your-own model | Free (open-core) | 🟢 (product) |
| Managed streaming | Hosted chat + streaming responses | Per-seat or usage monthly | 🔴 planned |
| Template registry access | Curated AI templates + updates | Freemium → Pro | 🟡 beta |
| MCP integration pack | Connect chat to tools (Kilo/MCP) | Bundle with managed tier | 🟡 beta |

## 5. Ideal Clients

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| Startup dev lead | Building an AI feature into their product | Generic chat UX, integration time | Launch deadline for AI feature | $100–300/mo |
| Ops/Infra engineer | Must keep data self-hosted | Hosted AI data concerns | Compliance policy | $150–500/mo |
| Agency (AI vertical) | Ships chat/customizer features for clients | Repeatable runtime to reuse | New client AI project | Project + retainer |

## 6. Research Needed

- [ ] Competitive matrix: Intercom Fin, Copilot-style assistants, open-source RAG stacks — where is the customization wedge unique?
- [ ] Measure OSS self-host → managed conversion (needs a working managed tier).
- [ ] Validate pricing sensitivity for streaming/usage-based billing.
- [ ] Confirm Ollama-vs-hosted-provider split in target segments (cost + privacy trade-offs).
- [ ] Template registry research: what template types drive the most customization reuse?

## Remarks & Notes

- "Cypercloud" is the legacy name — external material should use **Syntara** (per repo naming rules), keeping `cypercloud` only where a runtime alias requires it.
- The MCP angle (`.agents/mcp/`) is a real differentiator — surface it in developer docs.
- Sizing is PLG-assumption-heavy; treat all numbers as hypotheses until the funnel is measured.
