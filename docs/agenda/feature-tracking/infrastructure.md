---
title: Infrastructure — Feature Tracking
description: Feature lifecycle for shared infrastructure — security, backups, observability, and deployment reliability
navigation:
  title: Infrastructure
  icon: i-lucide-server
object:
  type: "guide"
  id: "agenda.feature-tracking.infrastructure"
attributes:
  source_path: "agenda/feature-tracking/infrastructure.md"
  canonical_route: "/docs/en/agenda/feature-tracking/infrastructure"
  source_of_truth: "repository-markdown"
  owner: "infrastructure"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - infrastructure
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 Infrastructure — Feature Tracking

> **Scope:** Feature lifecycle for the shared platform infrastructure (PostgreSQL, Redis, proxy, deployment).
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## P1 — Next Up (Q4 2026)

**WebAuthn / Passkeys**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Security keys + platform passkeys for all Django sites — modern authentication security.

**Scope:** WebAuthn integration, passkey registration/authentication, fallback to password.

**Out of scope:** Hardware security key management, biometric enrollment.

**Acceptance criteria:**
- [ ] Passkey registration on Django sites
- [ ] Passkey authentication works
- [ ] Fallback to password
- [ ] Works across all Django products

**Notes:** Cross-product security feature.

---

**Automated Backups**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Scheduled PostgreSQL dumps + S3 upload — data protection and disaster recovery foundation.

**Scope:** Backup scheduling, PostgreSQL dump, S3 upload, retention policy, restore testing.

**Out of scope:** Point-in-time recovery, cross-region backups.

**Acceptance criteria:**
- [ ] Daily backups scheduled
- [ ] PostgreSQL dumps created
- [ ] Dumps uploaded to S3
- [ ] Retention policy configurable
- [ ] Restore tested

**Notes:** Foundational infrastructure feature.

---

**Health Dashboard**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Grafana + Prometheus monitoring for all services — observability.

**Scope:** Prometheus metrics collection, Grafana dashboards, alert rules, service discovery.

**Out of scope:** Log aggregation, distributed tracing.

**Acceptance criteria:**
- [ ] Prometheus scraping all services
- [ ] Grafana dashboards for key metrics
- [ ] Alert rules configured
- [ ] Service discovery working

**Notes:** Observability feature.

---

## P2 — Planned (Q1 2027)

**Multi-region Deploy**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** CloudFront CDN + regional DB replicas — latency and availability for global users.

**Scope:** Multi-region deployment, CDN configuration, DB replication, region routing.

**Out of scope:** Active-active databases, cross-region failover automation.

**Acceptance criteria:**
- [ ] Services deployable to multiple regions
- [ ] CloudFront CDN configured
- [ ] Regional DB replicas
- [ ] Region routing works

**Notes:** Scalability feature.

---

**Blue/Green Deploy**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Zero-downtime deployment strategy — reliability and safety.

**Scope:** Blue/green environment setup, traffic switching, rollback, health checks.

**Out of scope:** Canary deployments, gradual rollout.

**Acceptance criteria:**
- [ ] Blue/green environments
- [ ] Traffic switchable
- [ ] Rollback works
- [ ] Health checks before switch

**Notes:** Deployment reliability feature.

---

**Secret Rotation**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Automated API key + secret rotation — security best practice.

**Scope:** Secret storage, rotation scheduling, automated rotation, rollback.

**Out of scope:** Manual secret management UI, secret versioning.

**Acceptance criteria:**
- [ ] Secrets stored securely
- [ ] Rotation scheduled
- [ ] Automated rotation works
- [ ] Rollback available

**Notes:** Security feature.

---

**Rate Limiting**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Per-endpoint rate limiting with Redis — protect services from abuse.

**Scope:** Rate limit definitions, Redis-based counting, per-endpoint configuration, response headers.

**Out of scope:** Global rate limiting, user-based rate limiting.

**Acceptance criteria:**
- [ ] Rate limits definable per endpoint
- [ ] Redis-based counting
- [ ] Rate limit headers in response
- [ ] 429 responses on limit exceeded

**Notes:** Protection feature.

---

## P3 — Backlog

**Load Testing Suite**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Locust-based automated load testing — performance validation.

**Scope:** Locust test definitions, test execution, result reporting, CI integration.

**Out of scope:** Real-time load testing, stress testing.

**Acceptance criteria:**
- [ ] Locust tests defined
- [ ] Tests executable
- [ ] Results reported
- [ ] CI integration

**Notes:** Performance validation feature.

---

**Cost Optimization**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Resource right-sizing, spot instances — cost reduction.

**Scope:** Resource utilization analysis, right-sizing recommendations, spot instance usage.

**Out of scope:** Cost forecasting, budget alerts.

**Acceptance criteria:**
- [ ] Utilization analyzed
- [ ] Right-sizing recommendations
- [ ] Spot instances used where appropriate

**Notes:** Cost optimization feature.

---

**Disaster Recovery**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Infrastructure |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | Automated Backups, Multi-region Deploy |

**Why it matters:** Cross-region failover, RTO/RPO targets — business continuity.

**Scope:** Failover procedures, RTO/RPO definition, cross-region replication, DR testing.

**Out of scope:** Automated failover, multi-region active-active.

**Acceptance criteria:**
- [ ] RTO/RPO targets defined
- [ ] Cross-region replication
- [ ] Failover procedures documented
- [ ] DR test conducted

**Notes:** Depends on Automated Backups and Multi-region Deploy.

---

## Remarks & Notes

- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Priority alignment with [`feature-roadmap.md`](../../features/feature-roadmap.md) is mandatory — drift causes confusion
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
