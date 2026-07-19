# 🚀 Cypercloud — Multi-System Platform Plan

> Vision: Cypercloud evolves from an AI chat tool into a **subscription platform** where users can build, deploy, and manage multiple business systems (POS, CRM, LMS, etc.) from a single dashboard.

---

## Current State

Cypercloud is a Django + Wagtail site at `projects/cypercloud/` providing:

| Feature | Status | Description |
|---------|--------|-------------|
| AI Chat | ✅ Live | CeptorAI-powered multi-model chat (Ollama + OpenAI) |
| Streaming | ✅ Live | Server-Sent Events (SSE) for real-time AI responses |
| Conversations | ✅ Live | Persistent chat history with Django models |
| User Auth | ✅ Live | django-allauth with social + email auth |
| Admin | ✅ Live | Wagtail CMS for content management |

---

## Platform Vision: Phases

### Phase 1 — AI SaaS Foundation (Current → Q1)

**Goal**: Monetize the AI layer with subscription tiers.

```
┌─────────────────────────────────────┐
│         Cypercloud Dashboard         │
│  ┌─────────┐ ┌─────────┐ ┌───────┐  │
│  │ AI Chat │ │ Prompts │ │ Billing│  │
│  └─────────┘ └─────────┘ └───────┘  │
│  ┌─────────────────────────────────┐ │
│  │      My Systems (empty)         │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Features to add**:

- [ ] **Subscription Tiers** (Free / Pro / Enterprise)
  - Free: 50 chats/day, basic models
  - Pro: Unlimited chats, all models, custom prompts
  - Enterprise: Custom models, MCP integration, priority support
- [ ] **Stripe Billing Integration**
  - Recurring subscriptions with plan management
  - Usage-based billing for API calls
- [ ] **API Token Management**
  - Per-user API keys with rate limiting
  - OpenAI-compatible endpoint (`/v1/chat/completions`)
- [ ] **Prompt Library**
  - Save, share, and template AI prompts
  - System prompt per conversation

### Phase 2 — System Builder (Q2-Q3)

**Goal**: Let users create and deploy their own business systems from templates.

```
┌───────────────────────────────────────────┐
│          Cypercloud Dashboard              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐  │
│  │ Chat │ │Prompts│ │Billing│ │Systems  │  │
│  └──────┘ └──────┘ └──────┘ └─────────┘  │
│  ┌──────────────────────────────────────┐ │
│  │  My Systems                          │ │
│  │  ┌─────────┐ ┌─────────┐ ┌───────┐  │ │
│  │  │ My POS  │ │ My CRM  │ │My LMS │  │ │
│  │  │ 🟢 Live │ │ 🟡 Build│ │ ⚪ New│  │ │
│  │  └─────────┘ └─────────┘ └───────┘  │ │
│  └──────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

**Features to add**:

- [ ] **System Templates**
  - POS (from `projects/pos/`)
  - CRM (new template)
  - LMS (from `projects/lms/`)
  - E-commerce Store (new template)
  - Blog / Portfolio (from portfolio)
- [ ] **1-Click Deploy**
  - Fork template → customize → deploy with one button
  - Per-system subdomain: `my-pos.cypercloud.com`
  - Container isolation per tenant system
- [ ] **System Dashboard**
  - Status monitoring (up/down, health, usage)
  - Quick actions: restart, backup, upgrade
  - Log viewer per system

### Phase 3 — Full Platform (Q4+)

**Goal**: Enterprise-grade multi-tenant platform with marketplace.

```
┌──────────────────────────────────────────────────┐
│              Cypercloud Platform                  │
│                                                   │
│  ┌─────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ AI Core │ │ Deploy   │ │  App Marketplace │  │
│  │  • Chat  │ │  Engine  │ │  • POS plugins   │  │
│  │  • MCP   │ │  • K8s   │ │  • CRM modules   │  │
│  │  • RAG   │ │  • CI/CD │ │  • LMS courses   │  │
│  └─────────┘ └──────────┘ └──────────────────┘  │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  Tenant Isolation Layer                     │ │
│  │  • Per-tenant DB schemas or separate DBs    │ │
│  │  • Namespace-isolated Docker/K8s workloads  │ │
│  │  • Per-tenant Traefik routing               │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

**Features to add**:

- [ ] **App Marketplace**
  - Third-party plugins and themes
  - Revenue sharing for marketplace sales
- [ ] **Enterprise SSO**
  - SAML / OIDC integration
  - Team management and RBAC
- [ ] **Advanced AI**
  - RAG (Retrieval-Augmented Generation) per system
  - MCP (Model Context Protocol) server integration
  - Fine-tuned models per tenant
- [ ] **Global Edge**
  - Multi-region deployment
  - CDN for static assets
  - Edge AI inference

---

## Technical Architecture (Phase 2+)

```
                             ┌──────────────────────┐
                             │   Cypercloud Master   │
                             │   (Django + Wagtail)  │
                             │   :5073               │
                             └──────┬───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
            │  Tenant POS  │ │ Tenant LMS│ │ Tenant CRM  │
            │   :5081      │ │  :5082    │ │  :5083      │
            │  (Django +   │ │ (Django + │ │ (Django +   │
            │   Tauri)     │ │  Wagtail) │ │  Custom)    │
            └──────┬───────┘ └─────┬─────┘ └──────┬──────┘
                   │               │               │
                   └───────────────┼───────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     Shared Infrastructure    │
                    │  • PostgreSQL (per-tenant)   │
                    │  • Redis (shared broker)     │
                    │  • Traefik (dynamic routing) │
                    │  • MinIO (per-tenant media)  │
                    └─────────────────────────────┘
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Tenant isolation** | Database-per-tenant | Strongest isolation, easy backup/restore |
| **Container strategy** | Docker Compose per tenant | Simple, portable, no K8s overhead initially |
| **Routing** | Traefik dynamic config per tenant | Same proxy, new router per system |
| **Domain** | `<system>.<tenant>.cypercloud.com` | Predictable, wildcard SSL via Let's Encrypt |
| **Media** | MinIO per tenant bucket | S3-compatible, scalable |

---

## Database Plan

Each tenant system gets its own PostgreSQL database:

```sql
-- Per-tenant database creation
CREATE DATABASE tenant_123_pos;
CREATE DATABASE tenant_123_crm;
CREATE DATABASE tenant_123_lms;
```

The Cypercloud master database tracks:
- `tenants` — subscription tier, status, billing
- `systems` — type, subdomain, port, container, health
- `subscriptions` — Stripe customer, plan, renewal
- `api_keys` — per-tenant API tokens

---

## Implementation Roadmap

| Phase | Timeline | Key Deliverables |
|-------|----------|-----------------|
| **Phase 1** | Q1 2026 | Stripe billing, API tokens, prompt library |
| **Phase 1.5** | Q1-Q2 | User dashboard redesign, system CRUD UI |
| **Phase 2** | Q2-Q3 | System templates, 1-click deploy, monitoring |
| **Phase 2.5** | Q3-Q4 | App marketplace MVP, plugin API |
| **Phase 3** | Q4+ | Enterprise SSO, RAG, multi-region |

---

## Related Docs

| Topic | Path |
|-------|------|
| Cypercloud config | [`configuration.md`](configuration.md) |
| Cypercloud use cases | [`use-cases.md`](use-cases.md) |
| Infrastructure | [`../../infrastructure/`](../../infrastructure/) |
| Clone a site guide | [`../../guides/06-clone-site.md`](../../guides/06-clone-site.md) |
| Repo overview | [`../../repo-overview.md`](../../repo-overview.md) |
