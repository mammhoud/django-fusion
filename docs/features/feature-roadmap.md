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

> Desktop POS with Rust backend, Vue 3 frontend, Tauri shell.

### P0 🔴 — In Development

| Feature | Edition | Description |
|---------|---------|-------------|
| **POS-KO Gaming Center** | Full | Token-based gaming sessions with time tracking (committed) |

### P1 🟡 — Next Up

| Feature | Edition | Description |
|---------|---------|-------------|
| **Multi-terminal Sync** | Full | Real-time sync between multiple POS terminals |
| **Cloud Dashboard** | Full | Web-based admin dashboard for multi-store management |
| **Offline Queue** | All | Queue transactions when offline, sync when back online |
| **Barcode Scanner** | Solo+ | Native barcode scanning with camera/device scanner |

### P2 🟢 — Planned

| Feature | Edition | Description |
|---------|---------|-------------|
| **Kitchen Display** | Full | KDS integration for restaurant mode |
| **Loyalty Program** | Solo+ | Points-based loyalty with rewards |
| **Gift Cards** | Solo+ | Digital gift card system |
| **Table Management** | Full | Restaurant table layouts and order tracking |
| **Delivery Integration** | Full | Integrate with delivery platforms (Talabat, HungerStation) |

### P3 ⚪ — Backlog

| Feature | Edition | Description |
|---------|---------|-------------|
| **Inventory Forecasting** | Full | ML-based demand prediction and auto-reorder |
| **Employee Scheduling** | Full | Shift planning and time tracking |
| **Customer Display** | Solo+ | Customer-facing display for order confirmation |
| **Self-checkout Kiosk** | Full | Self-service kiosk mode |

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
  • Stripe billing       • Multi-terminal      • Kitchen Display
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
| Cypercloud platform plan | [`../projects/cypercloud/platform-plan.md`](../projects/cypercloud/platform-plan.md) |
| Per-project features | [`../projects/`](../projects/) |
| Feature matrix | [`README.md`](README.md) |
