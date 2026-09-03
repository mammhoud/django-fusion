---
title: Case Studies Index
description: Index of all case studies in the agenda system — POS, django-fusion, and platform implementations with mermaid diagrams
navigation:
  title: Case Studies Index
  icon: i-lucide-book-open
object:
  type: "index"
  id: "case-studies.index"
attributes:
  source_path: "agenda/case-studies/INDEX.md"
  canonical_route: "/docs/en/agenda/case-studies/index"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - case-studies
  - index
  - navigation
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Feature Tracking"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
---

# 📊 Case Studies Index

> All case studies in the agenda system. Each includes architecture diagrams (mermaid), implementation details, results, and lessons learned.
> **Language:** English only — no Arabic translations planned for agenda docs.

---

## POS System

| Case Study | Priority | Status | Diagrams | Description |
|------------|:--------:|--------|:--------:|-------------|
| [Multi-terminal Sync](./pos-multi-terminal-sync.md) | P0 | Shipped | 4 | WebSocket broadcast + pull changeset across POS terminals |
| [Offline Queue](./pos-offline-queue.md) | P0 | Shipped | 4 | Durable OutboxQueue + retry/backoff/dead-letter flush |
| [QR Menu](./pos-qr-menu.md) | P0 | Shipped | 4 | Versioned localized menu, preview/publish, branch QR codes |

## django-fusion (Component Framework)

| Case Study | Priority | Status | Diagrams | Description |
|------------|:--------:|--------|:--------:|-------------|
| [DataToken Sync Tagging](./data-token-sync-tagging.md) | P1 | Shipped | 3 | GenericForeignKey sync row tagging with parent/child tree, progress tracking, auto-untag |
| [Django-Bolt Fusion](./django-bolt-fusion.md) | P0 | Historical | 4 | django-bolt API patterns across Structa Cloud + POS editions, MCP integration |

## Platform / AI

| Case Study | Priority | Status | Diagrams | Description |
|------------|:--------:|--------|:--------:|-------------|
| [Ceptor-AI](./ceptor-ai.md) | P1 | Active | 5 | AI chat client, MCP server, BEM converter, agent generation — package use cases and architecture |
| [Stripe Billing](./stripe-billing.md) | P0 | In Progress | 3 | Subscription plans (Free/Pro/Enterprise), usage-based billing, Stripe webhooks, invoice generation |
| [API Token Management](./api-token-management.md) | P0 | In Progress | 3 | Token model with scopes, generate/rotate/revoke, scope enforcement middleware, token list UI |

---

## Diagram Summary

| Diagram Type | Count | Used In |
|--------------|-------|---------|
| `graph TB/LR` | 13 | Architecture flows, package structure, deployment modes, scope enforcement |
| `sequenceDiagram` | 7 | Request/response sequences, sync protocols, token auth flow |
| `stateDiagram-v2` | 8 | Status lifecycles, workflow states, subscription lifecycle, token lifecycle |
| `erDiagram` | 1 | Data model (DataToken Sync Tagging) |
| **Total** | **29** | Across 8 case studies |

---

## Writing a New Case Study

1. Copy the template from [`../case-studies.md`](../case-studies.md)
2. Add at least one mermaid diagram (architecture or flow)
3. Include: Context → Architecture → Implementation → Results → Lessons
4. Link from `feature-tracking.md` when the feature ships
5. Add entry to this index

---

## Remarks & Notes

- All mermaid diagrams validated: 25 blocks, all well-formed
- Diagrams use 4 types: graph, sequenceDiagram, stateDiagram-v2, erDiagram
- Case studies are written in English only (no Arabic translations planned)
- Each case study links to related feature tracking entries and other case studies

<!-- AI-generated: review needed -->
