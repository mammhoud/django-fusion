# 🗺️ Feature Roadmap

> Planned features and enhancements across all Structa Cloud projects, with priority rankings and implementation timelines.

---

## Priority Legend

| Rank | Label | Meaning |
|:----:|-------|---------|
| 🔴 | P0 | Blocking — actively in development |
| 🟡 | P1 | Next up — planned for next quarter |
| 🟢 | P2 | Planned — on the roadmap |
| ⚪ | P3 | Backlog — nice to have |
| ✅ | Done | Shipped and live |

---

## Cypercloud Platform

> AI-powered platform for building and deploying business systems.

### P0 🔴 — In Development

| Feature | Description | Impact |
|---------|-------------|--------|
| **Stripe Billing** | Subscription plans (Free, Pro, Enterprise), usage-based billing, invoices | Monetization — planned Q3 2026 |
| **API Token Management** | Generate, rotate, revoke API tokens with scoped permissions | Developer access — planned Q3 2026 |
| **Customer Dashboard** | Self-service portal: billing, tokens, usage, support tickets | User experience — planned Q3 2026 |

### P1 🟡 — Next Up

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| **System Templates** | 1-click deploy: POS, CRM, LMS, Blog | P0 billing |
| **AI Prompt Library** | Shareable, reusable prompt templates with variables | — |
| **Agent Templates** | Pre-built AI agents for common tasks (support, sales, onboarding) | Prompt library |
| **Usage Analytics** | Per-model token tracking, cost breakdowns, usage graphs | P0 billing |

### P2 🟢 — Planned

| Feature | Description |
|---------|-------------|
| **App Marketplace** | Community-contributed templates, agents, and integrations |
| **Multi-tenant Isolation** | Per-customer database isolation for enterprise plans |
| **White-label Deploy** | Custom domains + branding for Pro/Enterprise tiers |
| **Webhook Integrations** | Event-driven webhooks (order.created, user.registered, etc.) |

### P3 ⚪ — Backlog

| Feature | Description |
|---------|-------------|
| **Edge Inference** | Deploy AI models to CDN edge nodes for low-latency |
| **Custom Model Fine-tuning** | Fine-tune open-source models on customer data |
| **Workflow Automations** | No-code automation builder (Zapier-style triggers + actions) |

---

## POS System

> **Formint POS Professional** is the canonical target for the next restaurant-focused POS releases. Legacy Solo/Full labels remain compatibility references during migration.

### Formint Professional launch scope

| Feature | Priority | Status | Release gate |
|---------|:--------:|:------:|--------------|
| Multi-branch management | P0 | ✅ | Offline branch operation, idempotent sync, permissions, transfers |
| Kitchen Display System | P0 | ✅ | Station routing, ticket lifecycle, timers, metrics |
| QR Menu | P0 | ✅ | Versioned localized menu, preview/publish, branch/table QR |
| Loyalty System | P1 | ✅ | Immutable points ledger, rewards, consent, reversals |
| API Access | P1 | ✅ | Versioned `/api/v1/` schemas, scoped keys, sliding-window rate limits, webhooks |
| Mobile Waiter | P1 | ✅ | Tableside orders, kitchen handoff, split/merge (`SaleGroup`), offline retry |

See the [Formint edition chain](../plans/editions/README.md) for the canonical business scope, architecture, migration gates, pricing hypotheses, and launch strategy.

> Target stack: Tauri 2 + Rust desktop shell, Astro + Alpine.js + HTMX + Tailwind UI, Django + django-fusion backend, and SQLite/PostgreSQL data layers.

### P0 🔴 — In Development

| Feature | Edition | Description |
|---------|---------|-------------|
| **POS-KO Gaming Center** | Full | Token-based gaming sessions with time tracking (committed) |

### P1 🟡 — Next Up

| Feature | Edition | Description |
|---------|---------|-------------|
| **Cloud Dashboard** | Professional/SaaS | Web-based dashboard for multi-branch management |

### ✅ Done — Shipped

| Feature | Edition | Description |
|---------|---------|-------------|
| **WebSocket Sync Events** | ☁️ | Real-time sync event broadcasting via Django Channels to bolt dashboard + Unfold admin |
| **Multi-terminal Sync** | Professional | Real-time WebSocket broadcast + pull changeset (`/sync/changes`, `/sync/ack`, `/sync/trigger`) across POS terminals |
| **Offline Queue** | Community+ | Durable `OutboxQueue` + retry/backoff/dead-letter flush (`/offline-queue/*`) — queue transactions offline, sync when back online |
| **Barcode Scanner** | Professional | Resolve scanned codes to products (`/barcode/<value>`, SKU fallback) + Code128 label SVG (`/barcode/<value>/label`) |
| **Bolt Analytics Dashboard** | ☁️ | Self-contained HTML dashboard at `/apis/data/` — 6 KPI cards, live WS updates, sync event log viewer |
| **Sync Event Log Viewer** | ☁️ | Fixed-position panel (50-entry ring buffer, collapse, reconnect indicator) on bolt + admin dashboards |
| **DataToken Sync Tagging** | 🔧 | django-fusion model for ordered sync row tagging with parent/child trees, progress tracking, auto-untag |
| **Cloud Sync Scheduler** | Full | `BranchSyncScheduler` with configurable interval, toggle, and pos-cloud push |
| **pos-cloud Makefile Targets** | ☁️ | `make cloud-run`, `cloud-dev`, `cloud-check`, `cloud-test`, `cloud-clean` |
| **POS Crest Branding** | All | Animated SVG crest logo across all editions + pos-cloud Unfold admin |
| **.env Config Files** | All | `.env` files with sensible defaults for all 4 editions (mini, solo, full, cloud) |

> 🔧 = django-fusion library  |  ☁️ = pos-cloud server

### P2 🟢 — Planned

| Feature | Edition | Description |
|---------|---------|-------------|
| **Gift Cards** | Professional+ | Digital gift card system |
| **Table Management** | Professional+ | Restaurant table layouts and order tracking |
| **Delivery Integration** | Professional+ | Integrate with delivery platforms (Talabat, HungerStation) |
| **AI Forecasting** | Professional/SaaS | Advisory demand, stock, waste, and sales recommendations |

### P3 ⚪ — Backlog

| Feature | Edition | Description |
|---------|---------|-------------|
| **Inventory Forecasting** | Professional/SaaS | Advisory demand prediction and auto-reorder recommendations |
| **Employee Scheduling** | Professional | Shift planning and time tracking |
| **Customer Display** | Professional | Customer-facing display for order confirmation |
| **Self-checkout Kiosk** | Professional/SaaS | Self-service kiosk mode |

---

## LMS (Learning Management System)

> Courses, certifications, and e-learning platform.

### P1 🟡 — Next Up

| Feature | Description |
|---------|-------------|
| **Video Hosting** | Integrated video upload + streaming for course content |
| **Quizzes & Assessments** | Multiple choice, coding challenges, auto-grading |
| **Progress Tracking** | Per-student progress dashboard with completion % |
| **Certificate Designer** | Drag-and-drop certificate template builder |
| **Email Automation** | Drip email sequences for course enrollment |

### P2 🟢 — Planned

| Feature | Description |
|---------|-------------|
| **Live Classes** | WebRTC-based live video sessions |
| **Discussion Forums** | Per-course discussion boards |
| **Peer Review** | Student peer assessment workflows |
| **Gamification** | Badges, leaderboards, XP points |
| **API Integration** | LMS as API for embedding in other platforms |

### P3 ⚪ — Backlog

| Feature | Description |
|---------|-------------|
| **SCORM/xAPI** | Industry-standard e-learning content interoperability |
| **Multi-language Courses** | Course content in multiple languages with translation management |
| **White-label** | Custom branding per organization |

---

## Portfolio (Resume Builder)

> Resume and portfolio builder.

### P1 🟡 — Next Up

| Feature | Description |
|---------|-------------|
| **ATS-Optimized Export** | Resume formats optimized for Applicant Tracking Systems |
| **Cover Letter Builder** | AI-assisted cover letter generation |
| **Portfolio Gallery** | Image/video portfolio sections |
| **Custom Domains** | Custom domain mapping for portfolio pages |

### P2 🟢 — Planned

| Feature | Description |
|---------|-------------|
| **Job Board Integration** | Auto-apply with stored resume data |
| **Analytics Dashboard** | Profile views, download counts |
| **Multi-language Resumes** | Resume in multiple languages |
| **LinkedIn Import** | Auto-populate from LinkedIn profile |

---

## Infrastructure

> Shared infrastructure improvements across all projects.

### P1 🟡 — Next Up

| Feature | Description |
|---------|-------------|
| **WebAuthn / Passkeys** | Security keys + platform passkeys for all Django sites |
| **Automated Backups** | Scheduled PostgreSQL dumps + S3 upload |
| **Health Dashboard** | Grafana + Prometheus monitoring for all services |

### P2 🟢 — Planned

| Feature | Description |
|---------|-------------|
| **Multi-region Deploy** | CloudFront CDN + regional DB replicas |
| **Blue/Green Deploy** | Zero-downtime deployment strategy |
| **Secret Rotation** | Automated API key + secret rotation |
| **Rate Limiting** | Per-endpoint rate limiting with Redis |

### P3 ⚪ — Backlog

| Feature | Description |
|---------|-------------|
| **Load Testing Suite** | Locust-based automated load testing |
| **Cost Optimization** | Resource right-sizing, spot instances |
| **Disaster Recovery** | Cross-region failover, RTO/RPO targets |

---

## django-fusion (Component Framework)

### ✅ Done — Shipped

| Feature | Description |
|---------|-------------|
| **DataToken Sync Tagging** | GenericForeignKey-based sync row tagging with parent/child tree, progress tracking, auto-untag, UUID PK support |

### P1 🟡 — Next Up

| Feature | Description |
|---------|-------------|
| **MCP Integration** | Model Context Protocol for AI-assisted development |
| **Component Storybook** | Isolated component preview + documentation |
| **Hot Reload** | Template hot reload in development |

### P2 🟢 — Planned

| Feature | Description |
|---------|-------------|
| **TypeScript Components** | First-class TypeScript component support |
| **Visual Builder** | Drag-and-drop page builder using components |
| **Component Analytics** | Usage tracking per component |

---

## Timeline

```
Q3 2026 (Jul-Sep)     Q4 2026 (Oct-Dec)     Q1 2027 (Jan-Mar)
─────────────────     ─────────────────     ─────────────────
🔴 Cypercloud P0       🟡 POS P1             🟢 POS P2
  • Stripe billing       • Multi-terminal      • Formint Professional pilot
  • API tokens           • Cloud Dashboard     • Loyalty Program
  • Customer dashboard   • Offline Queue       • Gift Cards
                       🟡 LMS P1             🟢 LMS P2
🟡 Cypercloud P1         • Video hosting       • Live classes
  • System templates     • Quizzes             • Discussion forums
  • Prompt library       • Progress tracking   • Gamification
  • Agent templates    🟡 Portfolio P1        🟢 Infrastructure P2
                       🟡 Infra P1             • Multi-region
🟡 POS P1                • WebAuthn            • Blue/Green
  • POS-KO Gaming        • Auto backups        • Rate limiting
  • Barcode scanner      • Health dashboard
```

---

## Related

| Topic | Path |
|-------|------|
| Feature matrix | [`README.md`](README.md) |
| Per-project features | [`../projects/`](../projects/) |
| Feature matrix | [`README.md`](README.md) |
