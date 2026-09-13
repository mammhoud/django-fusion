---
title: Cypercloud / Syntara Platform — Feature Tracking
description: Feature lifecycle for the Cypercloud/Syntara AI platform — billing, API tokens, templates, and AI capabilities
navigation:
  title: Cypercloud / Syntara
  icon: i-lucide-cpu
object:
  type: "guide"
  id: "agenda.feature-tracking.syntara"
attributes:
  source_path: "agenda/feature-tracking/syntara.md"
  canonical_route: "/docs/en/agenda/feature-tracking/syntara"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - syntara
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 Cypercloud / Syntara Platform — Feature Tracking

> **Scope:** Feature lifecycle for the Cypercloud/Syntara AI chat and customization runtime.
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## P0 — In Development (Q3 2026)

**Stripe Billing**

| Field | Value |
|-------|-------|
| **Status** | 🟡 In Progress |
| **Priority** | P0 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q3 2026 |
| **Depends on** | — |

**Why it matters:** Subscription plans (Free, Pro, Enterprise), usage-based billing, and invoices — this is the monetization foundation for the platform.

**Scope:** Subscription plan model, Stripe integration, usage metering, invoice generation.

**Out of scope:** Usage analytics dashboard (tracked separately), refund handling.

**Acceptance criteria:**
- [ ] Free/Pro/Enterprise plan tiers configurable
- [ ] Usage-based billing with metered billing
- [ ] Invoice generation and PDF download
- [ ] Webhook handling for Stripe events

**Notes:** Highest priority — blocks System Templates and Customer Dashboard.

**Case study:** [`case-studies/stripe-billing.md`](../case-studies/stripe-billing.md)

---

**API Token Management**

| Field | Value |
|-------|-------|
| **Status** | 🟡 In Progress |
| **Priority** | P0 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q3 2026 |
| **Depends on** | — |

**Why it matters:** Generate, rotate, and revoke API tokens with scoped permissions — essential for developer access and integrations.

**Scope:** Token model with scopes, generate/rotate/revoke actions, token list UI.

**Out of scope:** OAuth provider integration, token usage analytics.

**Acceptance criteria:**
- [ ] Token creation with scope selection
- [ ] Token rotation with old token invalidation
- [ ] Token revocation
- [ ] Scoped permissions enforced on API endpoints

**Notes:** Blocks API-first integrations.

**Case study:** [`case-studies/api-token-management.md`](../case-studies/api-token-management.md)

---

**Customer Dashboard**

| Field | Value |
|-------|-------|
| **Status** | 🟡 In Progress |
| **Priority** | P0 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q3 2026 |
| **Depends on** | Stripe Billing, API Token Management |

**Why it matters:** Self-service portal for billing, tokens, usage, and support tickets — reduces support load and improves user experience.

**Scope:** Billing section, token management section, usage overview, support ticket creation.

**Out of scope:** Full support ticket system, usage analytics deep-dive.

**Acceptance criteria:**
- [ ] User can view and manage billing
- [ ] User can create and manage API tokens
- [ ] User can view usage summary
- [ ] User can submit support tickets

**Notes:** Depends on Stripe Billing and API Token Management being in place.

---

## P1 — Next Up (Q4 2026)

**System Templates**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | Stripe Billing (P0) |

**Why it matters:** 1-click deploy for POS, CRM, LMS, Blog — makes the platform instantly useful for new customers.

**Scope:** Template definitions for POS, CRM, LMS, Blog; 1-click deploy flow.

**Out of scope:** Custom template creation UI, template marketplace.

**Acceptance criteria:**
- [ ] POS template deploys a working POS system
- [ ] CRM template deploys a working CRM
- [ ] LMS template deploys a working LMS
- [ ] Blog template deploys a working blog

**Notes:** Depends on billing being live so templates can be tied to subscriptions.

---

**AI Prompt Library**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Shareable, reusable prompt templates with variables — makes AI capabilities accessible to non-technical users.

**Scope:** Prompt template model, variable system, share/import/export, library UI.

**Out of scope:** AI agent execution (tracked separately), prompt analytics.

**Acceptance criteria:**
- [ ] Create prompt templates with named variables
- [ ] Import/export prompt templates
- [ ] Browse and search prompt library
- [ ] Execute prompt with variable substitution

**Notes:** Foundational for Agent Templates.

---

**Agent Templates**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | AI Prompt Library |

**Why it matters:** Pre-built AI agents for common tasks (support, sales, onboarding) — delivers immediate value from the AI platform.

**Scope:** Agent definition model, pre-built agent templates, agent execution runtime.

**Out of scope:** Custom agent builder, agent marketplace.

**Acceptance criteria:**
- [ ] Support agent template ready to deploy
- [ ] Sales agent template ready to deploy
- [ ] Onboarding agent template ready to deploy
- [ ] Agents execute with proper context

**Notes:** Depends on AI Prompt Library for the prompt layer.

---

**Usage Analytics**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | Stripe Billing (P0) |

**Why it matters:** Per-model token tracking, cost breakdowns, usage graphs — essential for customer visibility and billing accuracy.

**Scope:** Token usage tracking per model, cost calculation, usage graphs, billing correlation.

**Out of scope:** Real-time usage streaming, multi-tenant usage aggregation.

**Acceptance criteria:**
- [ ] Track token usage per API call
- [ ] Calculate cost per model
- [ ] Show usage graph in customer dashboard
- [ ] Correlate usage with invoices

**Notes:** Depends on billing for cost calculation foundation.

---

## P2 — Planned (Q1 2027)

**App Marketplace**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | System Templates, AI Prompt Library |

**Why it matters:** Community-contributed templates, agents, and integrations — ecosystem growth and network effects.

**Scope:** Marketplace UI, submission workflow, rating/review system, install flow.

**Out of scope:** Payment processing for marketplace, curation/moderation tools.

**Acceptance criteria:**
- [ ] Users can browse marketplace
- [ ] Users can submit templates/agents
- [ ] Users can install from marketplace
- [ ] Basic rating/review system

**Notes:** Depends on System Templates and AI Prompt Library as the underlying capability.

---

**Multi-tenant Isolation**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Per-customer database isolation for enterprise plans — required for enterprise sales and security compliance.

**Scope:** Database per tenant option, tenant routing, migration per tenant.

**Out of scope:** Kubernetes-based isolation, cross-tenant analytics.

**Acceptance criteria:**
- [ ] Enterprise customers can have isolated databases
- [ ] Tenant routing works correctly
- [ ] Migrations run per tenant

**Notes:** Enterprise-tier feature.

---

**White-label Deploy**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Custom domains + branding for Pro/Enterprise tiers — brand ownership for customers.

**Scope:** Custom domain configuration, logo/brand customization, white-label UI.

**Out of scope:** Full CSS customization, mobile app branding.

**Acceptance criteria:**
- [ ] Pro/Enterprise customers can set custom domain
- [ ] Customers can upload custom logo
- [ ] UI reflects customer branding

**Notes:** Pro/Enterprise tier feature.

---

**Webhook Integrations**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | API Token Management |

**Why it matters:** Event-driven webhooks (order.created, user.registered, etc.) — enables integrations with external systems.

**Scope:** Webhook event definitions, webhook registration UI, delivery system, retry logic.

**Out of scope:** Webhook testing UI, webhook transformation/transcription.

**Acceptance criteria:**
- [ ] Define webhook events
- [ ] Users can register webhook URLs
- [ ] Webhooks delivered with retry
- [ ] Webhook delivery logging

**Notes:** Depends on API Token Management for authenticating webhook registrations.

---

## P3 — Backlog

**Edge Inference**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Deploy AI models to CDN edge nodes for low-latency — performance optimization for global users.

**Scope:** Edge deployment infrastructure, model distribution, latency measurement.

**Out of scope:** Model training at edge, edge-specific model optimization.

**Acceptance criteria:**
- [ ] Models deployable to edge nodes
- [ ] Latency improvement measurable
- [ ] Fallback to central inference works

**Notes:** Advanced performance feature.

---

**Custom Model Fine-tuning**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Fine-tune open-source models on customer data — customized AI for specific use cases.

**Scope:** Fine-tuning pipeline, customer data upload, model registry, fine-tuned model serving.

**Out of scope:** Full training infrastructure, GPU management.

**Acceptance criteria:**
- [ ] Customers can upload training data
- [ ] Fine-tuning job runs successfully
- [ ] Fine-tuned model is served

**Notes:** Advanced AI feature, requires significant infrastructure.

---

**Workflow Automations**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Syntara |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | Webhook Integrations |

**Why it matters:** No-code automation builder (Zapier-style triggers + actions) — makes the platform extensible without code.

**Scope:** Trigger/action model, visual builder UI, workflow execution engine.

**Out of scope:** Conditional logic branches, multi-step workflows with loops.

**Acceptance criteria:**
- [ ] Users can create workflows with triggers and actions
- [ ] Visual builder for workflow construction
- [ ] Workflows execute when triggers fire

**Notes:** Depends on Webhook Integrations for the trigger mechanism.

---

## Remarks & Notes

- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Priority alignment with [`feature-roadmap.md`](../../features/feature-roadmap.md) is mandatory — drift causes confusion
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
