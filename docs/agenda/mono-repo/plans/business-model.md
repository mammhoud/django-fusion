---
Object type: Workspace
Tags: business, strategy
Status: Published
---

# Business Model — Structa Cloud Canvas

> **Type:** Workspace 🏢
> **Emoji:** 💼
> **Description:** Business Model Canvas mapping key partners, activities, resources, value proposition, customer relationships, channels, customer segments, cost structure, and revenue streams.

---

## Business Model Canvas

```mermaid
graph LR
    subgraph "Key Partners"
        KP1[OSS Community]
        KP2[Docker Hub]
        KP3[Hosting Providers]
    end
    subgraph "Key Activities"
        KA1[Multi-site CMS/LMS dev]
        KA2[Component library]
    end
    subgraph "Value Proposition"
        VP1[AI-powered multi-site CMS+LMS]
        VP2[Component-based architecture]
        VP3[Self-hosted, open source]
    end
    subgraph "Customer Relationships"
        CR1[Community support]
        CR2[Enterprise SLAs]
    end
    subgraph "Channels"
        CH1[GitHub]
        CH2[Documentation]
        CH3[Community Discord]
    end
    subgraph "Customer Segments"
        CS1[EdTech companies]
        CS2[Corporate training]
        CS3[Digital agencies]
    end
    subgraph "Cost Structure"
        CO1[Infra + CI/CD]
        CO2[Maintenance]
    end
    subgraph "Revenue Streams"
        RS1[Support subscriptions]
        RS2[Enterprise licenses]
        RS3[Premium templates]
    end

    KP1 --> KA1
    KP2 --> KA1
    KA1 --> VP1
    KA2 --> VP2
    VP1 --> CR1
    VP2 --> CR2
    VP1 --> CH2
    VP2 --> CS1
    VP3 --> CS2
    CH1 --> CS3
    VP1 --> RS1
    VP2 --> RS2
    VP3 --> RS3
    CO1 --> VP1
    CO2 --> VP3
```
![Rendered diagram](/agenda/diagrams/mono-repo-plans-business-model-1.svg)

> **Gap fixed (2026-09-05):** the local `files/business-model-canvas-png_h.webp`
> and the external Windmill Digital image were both dangling. Replaced with a
> rendered canvas diagram (see [`docs/agenda/diagrams/`](../../diagrams/README.md)).

---

## Key Building Blocks

| Block | Description |
|-------|-------------|
| **Value Proposition** | AI-powered multi-site CMS + LMS platform with component-based architecture. Self-hosted open source with enterprise support options. |
| **Customer Segments** | EdTech companies, professional services, corporate training, digital agencies, individual professionals |
| **Channels** | GitHub (open source), Docker Hub, documentation site, community Discord |
| **Revenue Streams** | Professional support subscriptions, enterprise licenses, premium templates, educational pricing |
| **Key Partners** | Cloud providers, payment processors, EdTech integrators, hosting partners |
| **Cost Structure** | Development, infrastructure (CI/CD, hosting), community management, legal/compliance |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Color** | Indigo (#6366f1) — representing business value, strategic planning |
| **Tiers** | Community (Free), Professional (Subscription), Enterprise (Custom), Educational (Discounted) |
| **License** | MIT — open source core with proprietary premium features |

---

## Pricing Tiers

| Tier | Price | Features | Audience |
|------|-------|----------|----------|
| **Community** | Free | Self-hosted, full source, community support | Developers, small orgs |
| **Professional** | Subscription | Premium templates, priority support | Agencies, growing orgs |
| **Enterprise** | Custom | Dedicated support, SLA, custom dev | Large enterprises |
| **Educational** | Discounted | All features, institutional pricing | Schools, universities |

---

## Related Docs

- → `market-research.md` — Market analysis and competitor comparison
- → `operational-plan.md` — Operations and delivery
- → `product-development.md` — Product development lifecycle
- → `_legacy/free-version.md` — Free version scope
- → `_legacy/full-version.md` — Full enterprise version
- → `../README.md` — Master index
