---
Object type: Story
Tags: story, narrative, journey, founder, origin, django, platform, startup
Status: Published
Author: people/mahmoud.md
Phase: Enterprise
Related Plans: startup-planner, product-development, project-workspace
Related Products: formint-pos
---

# Starting the Project — The Founder's Journey

> **Description:** The story of how the Structa Cloud project and mono repository began — from a first Django experiment through small sites, scalability learnings, an AI-driven component stack, the django-fusion package, and finally a desktop + cloud platform.

---

## Preface

Every large platform starts with a single experiment. This is the record of how this project started, the technologies explored, the lessons learned about scalability, and how a personal learning journey grew into a component system, a CMS-driven platform, and a desktop-plus-cloud product suite. It is told as a story with clear phases so it can be read as a narrative, tracked as achievements, and linked back to goals and plans.

---

## Phase 1 — Foundations: learning Django by building small sites

The project began by learning **Django**. Rather than studying in isolation, the approach was to build real, small sites immediately.

**What happened:**

| Step | Detail |
|------|--------|
| First framework | Django as the core backend |
| First products | Small websites implemented end-to-end |
| Learning method | Build-first; each small site deepened understanding of routing, models, views, and templates |

**Lesson:** The fastest way to learn a framework is to ship small, working sites. This built the confidence and foundation that later scaled into a full platform.

---

## Phase 2 — Experimentation: exploring the frontend and live data

Next the focus turned to the frontend and real-time behavior, experimenting with the surrounding JavaScript and server-sent event stack.

**What happened:**

| Technology / idea | What was explored |
|-------------------|-------------------|
| **htmx** | Server-driven interactions with minimal JavaScript |
| **Alpine.js** | Lightweight client-side reactivity |
| **WebSockets** | Small live apps built and completed |

**Lessons:**

- htmx and Alpine.js keep the frontend simple by pushing logic to the server and sprinkling lightweight interactivity.
- WebSocket apps taught the fundamentals of real-time communication and led to later support for server-sent events (SSE).

**Outcome:** Several small WebSocket-based apps were completed, and the team gained a working feel for building interactive, live applications.

---

## Phase 3 — Foundations of scalability and multi-tenancy

This phase moved from "make it work" to "make it scale." The focus was on what actually makes an application scalable, especially at the database layer.

**What happened:**

| Topic | What was learned |
|-------|------------------|
| Scalable database design | How databases behave under growth, and what makes an app scalable |
| Multi-tenancy | Adding multiple tenants at the database level so one deployment serves many customers safely |
| Authentication | User registration and login with **OAuth** and the **django-allauth** package |

**Lessons:**

- Scalability is largely decided early, by how data is modeled and how tenants are isolated.
- Multi-tenant databases let one platform serve many customers with shared infrastructure.
- Authentication is a solved problem in Django — standard packages like allauth cover registration and OAuth cleanly.

**Outcome:** A clear mental and technical model of how a shared platform can host many customers, which later informed the SaaS and cloud editions.

---

## Phase 4 — The backend, APIs, AI, and agentic development

The backend became more than a plain web application. Django grew into an integrated backend that served APIs, connected to newly developed packages, and adopted AI and agentic workflows.

**What happened:**

| Focus | Detail |
|-------|--------|
| Django as backend | Central backend serving data and logic |
| API packages | Integration with newly developed API packages |
| AI stack | Introduction of AI-assisted features |
| Agentic development | Agents and MCP (Model Context Protocol) workflows |

**Outcome:** The backend became an API-powered, AI-capable service — the bridge between the data layer and increasingly intelligent product features.

---

## Phase 5 — First products: LMS, websites, and CRM

With the foundation in place, the first real products were built, one after another.

**What happened:**

| Product | What was built |
|---------|----------------|
| **Small LMS** | A first learning management system |
| **Website pages** | Marketing and company web pages |
| **CRM with admin panel** | A CRM backed by a Django admin panel |
| **Full CRM** | Complete CRM backend with a full frontend and custom themes |
| **Complete LMS** | A full LMS with complete user registration |
| **Agents + MCP** | Agent workflows added on top |

**Lesson:** A shared backend pattern (Django) let each product reuse the same skills, auth, and data approach, so building each successive product got faster.

---

## Phase 6 — django-fusion: the component system

The biggest turning point was the creation of **django-fusion**, a package that wraps components and makes building anything faster and more consistent.

**What it does:**

| Capability | Detail |
|------------|--------|
| Component system | Reusable building-block components across the platform |
| Easier component requests | Components can be requested/rendered simply and uniformly |
| Rich component content | A component can contain data, a table, an htmx request, or server-sent events (SSE) |
| Backend/frontend separation | A component can be added to a project split as backend and frontend |
| Reuse across products | Used to build POS and LMS completely, and the company website pages |

**Impact:** django-fusion became the shared layer that made every subsequent product faster to build and easier to maintain.

---

## Phase 7 — CMS-driven sites and an AI-enabled fast dev cycle

The final product-level step was making every website content-driven and adaptive with AI.

**What happened:**

| Capability | Detail |
|------------|--------|
| **Wagtail as CMS** | Wagtail integrated as the content management system into each website |
| **Per-page content** | Every page has manageable, structured content |
| **Flexible AI** | AI can change a component, its fields, data flow, and design |
| **Fast development cycle** | AI-assisted editing makes iterating on pages quick |

**Outcome:** The platform became a CMS-driven, AI-flexible system where design, content, and data flow can be adapted quickly — the foundation of a fast development cycle for the whole company.

---

## Phase 8 — Desktop, cloud, and platform engineering

The last phase turned the web platform into a full product suite with desktop and cloud presence.

**What happened:**

| Focus | Detail |
|-------|--------|
| **POS Suite** | The POS extended to a desktop application |
| **Tauri** | Desktop app built with Tauri |
| **Cloud** | POS integrated with cloud services |
| **Frontend project** | A dedicated frontend project with a familiar, related tech stack |
| **Documentation** | Full documentation written for the projects |
| **Workspace development (Coder)** | The workspace is developed and hosted on the server as a coding workspace via Coder |

**Outcome:** The project is now a platform — web, desktop, and cloud — with reusable components, AI flexibility, documentation, and a server-hosted development workspace.

---

## Phase 9 — Forge → Formint: The Great Rename

The journey from Forge to Formint was not just a name change — it was a strategic pivot from a temporary development label to a permanent product identity.

**What happened:**

| Step | Detail |
|------|--------|
| **Forge as development speed** | Used `pos-mini`, `pos-solo`, `pos-full` as internal labels to move fast during development |
| **Forge as feature source** | Built features under Forge labels, testing ideas quickly without worrying about naming |
| **Formint as product identity** | When the product vision crystallized, created Formint as the permanent customer-facing brand |
| **Migration strategy** | Developed a controlled transfer from Forge capabilities into Formint Professional |
| **Old names for speed** | Kept old names in development for fast iteration, changed to new names for public release |
| **Open for opinion** | Made the naming decision open for team input before finalizing the public identity |

**Development approach:**

| Phase | Name Used | Purpose |
|-------|-----------|---------|
| Early development | `pos-mini`, `pos-solo`, `pos-full` | Fast prototyping, no naming pressure |
| Feature building | Forge labels | Quick iteration, feature experiments |
| Product definition | Formint | Permanent identity, customer-facing |
| Public release | Formint Professional, POS Cloud | Market-ready naming |

**Lessons:**

- Using temporary names during development enables speed — you don't waste time on branding before the product vision is clear.
- The rename from Forge to Formint was a strategic decision, not just cosmetic — it signaled the shift from experiment to product.
- Making naming decisions open for team input builds ownership and ensures the name resonates with everyone.
- Old names stay in development context; new names are for the public.

**Outcome:** The product now has a clear, permanent identity (Formint) while the development process used temporary names (Forge) to maintain velocity. The migration was controlled, documented, and open for team input.

---

## Phase 10 — Publishing the journey

With the product identity established, the focus shifted to sharing the story and inviting community input.

**What happened:**

| Step | Detail |
|------|--------|
| **Story documentation** | Wrote the founder journey as a narrative |
| **Achievement tracking** | Linked phases to goals and measurable outcomes |
| **Open for opinion** | Made the story and naming open for community feedback |
| **Publishing decision** | Decided what to publish and what to keep internal |

**Publishing principles:**

- Share the journey, not just the destination
- Be open about decisions and invite input
- Keep internal development details separate from public narrative
- Let the community shape the final presentation

**Outcome:** The story is now a living document that invites participation while maintaining a clear narrative arc from experiment to platform.

---

## Timeline summary

| Phase | Theme | Key outcome |
|-------|-------|-------------|
| 1 | Foundations | Django skills; first small sites |
| 2 | Experimentation | htmx, Alpine.js, WebSockets explored |
| 3 | Scalability | Multi-tenancy, OAuth/allauth |
| 4 | Backend & AI | APIs, AI stack, agents, MCP |
| 5 | First products | LMS, websites, CRM |
| 6 | django-fusion | Shared component system |
| 7 | CMS & AI | Wagtail + flexible AI dev cycle |
| 8 | Platform | Tauri desktop, cloud, documentation, Coder workspace |
| 9 | Forge → Formint | Great rename, controlled migration, open input |
| 10 | Publishing | Story documentation, community input |

---

## What this means now

The mono repository is the unified home of all these experiments, products, and packages. Every phase — from a single Django experiment to a desktop-and-cloud platform — lives in one repository, documented and traceable back to the goals and achievements on the board.

---

## Related

- → `../goals/achievement-board.md` — Phase-by-phase achievement tracker
- → `./notes/start-up-journal.md` — Raw working notes
- → `../plans/startup-planner.md` — Product and business strategy
- → `../plans/product-development.md` — Development lifecycle
- → `../plans/project-workspace.md` — Portfolio workspace
- → `../products/formint-pos.md` — POS product description
- → `../objects/story.md` — Story object type
- → `../README.md` — Anytype hub
