---
Object type: Architecture
Tags: architecture, websites, products, descriptions, portfolio
Status: Published
---

# Website & Application Descriptions

> **Description:** Business and architectural descriptions of every site, shared library, and infrastructure component in the Structa Cloud platform.

## Platform overview

Structa Cloud is a multi-site platform that shares a common foundation: Wagtail content management, shared templates and components, reusable libraries, and a single infrastructure layer. The primary products are CTC Research, LMS Demo, VResume, and Tinker, supported by the django-fusion and ceptor-ai libraries.

## Domain boundaries

- **CTC Research, LMS Demo, VResume** — individual product domains (research/training, courses, portfolios)
- **Shared assets and templates** — common styling and layout for all sites
- **Shared libraries** — django-fusion (components) and ceptor-ai (AI assistance)
- **Infrastructure** — proxy, databases, containers

---

## Primary websites and applications

### 1. CTC Research

**Purpose:** Research and Training Platform

Publishing research content, delivering courses, and providing training materials. Uses Wagtail's content management for a flexible educational ecosystem.

**Key features:**
- Research publication with workflows
- Course and module management
- Training materials and multimedia
- Role-based access (authors, editors, students)

### 2. LMS Demo

**Purpose:** Learning Management Demonstration

Course creation, enrollment, learner progress, and completion certificates.

**Key features:**
- Course curriculum and modules
- Enrollment records and progress tracking
- Completion certificates

### 3. VResume

**Purpose:** Portfolio and Resume builder

Professional portfolio creation with project, experience, and education sections, visual customization, and resume export.

**Key features:**
- Portfolio sections and content
- Visual customization
- Resume/PDF export

### 4. Tinker

**Purpose:** Template Customizer

Visual, code-free customization of site appearance — themes, colors, and fonts with real-time preview.

**Key features:**
- Theme selection
- Color and font customization
- Live preview and site-wide application

---

## Shared libraries

| Library | Purpose |
|---------|---------|
| **django-fusion** | Reusable Django components, routing, forms, and fragments |
| **ceptor-ai** | AI content assistance and chat integration |

---

## Infrastructure components

### 6.1 Proxy (Traefik + Nginx)

Handles SSL termination and routing via Traefik, while Nginx serves static and media files for all sites. Containerized deployment with automated service health checks.

### 6.2 Databases

PostgreSQL and Redis services shared across all sites for data persistence, caching, session storage, and background task queues.

| Service | Role |
|---------|------|
| PostgreSQL | Primary data store |
| Redis | Cache, sessions, background queues |
| Replication | High availability |
| Backup | Automated to cloud storage |

---

## Primary use cases

### Use case 1: Research publication and management

**Actor:** Researcher, institution, corporate training department

1. Researcher creates an account and accesses CTC Research
2. Creates a research article with content management
3. Adds AI-assisted content
4. Publishes and shares across sites

### Use case 2: Course management and learning delivery

**Actor:** Course creator, student, administrator

1. Course creator builds curriculum in CTC Research
2. Course becomes available on LMS Demo
3. Student enrolls, progresses, and completes with a certificate

### Use case 3: Professional portfolio creation

**Actor:** Professional, freelancer, job seeker

1. User accesses VResume and creates portfolio sections
2. Customizes appearance via Tinker (no code)
3. Adds AI-assisted content, publishes, and exports a resume

### Use case 4: Template customization without code

**Actor:** Content manager, marketing team

1. User selects a site in Tinker
2. Chooses a theme and customizes colors/fonts
3. Live preview and site-wide application

### Use case 5: AI-assisted content generation

**Actor:** Content creator, researcher

1. User triggers AI assistance in the editor
2. Provides topic and context
3. AI generates content; user reviews, edits, and publishes

### Use case 6: Multi-site administration

**Actor:** System administrator

1. Admin views site health and status
2. Manages users and roles
3. Performs updates, deploys new sites, monitors performance

### Use case 7: Integration and API usage

**Actor:** Developer, systems integrator

1. Developer authenticates an API request
2. Retrieves or updates content via API
3. Integrates with external systems

---

## Cross-cutting concerns

### Shared components and templates

All sites reuse a common set of templates, static assets, CSS themes, JavaScript components, and the django-fusion library.

### Data sharing across sites

- Shared database with schema isolation per site
- Shared cache (Redis)
- Centralized media storage
- Shared authentication with site-specific roles

### Security considerations

- HTTPS everywhere via proxy SSL termination
- Token-based API authentication
- Data privacy (GDPR-compliant)
- Role-based access control

---

## Business value and market positioning

### Value proposition

| Need | Solution |
|------|----------|
| Multi-site consistency | Shared templates and components |
| Content management | Wagtail CMS |
| Learning delivery | Integrated LMS |
| Portfolio building | VResume builder |
| Template customization | Visual customizer (no code) |
| AI enhancement | Integrated AI assistance |
| Infrastructure | Containerized deployment |

### Target market segments

| Segment | Primary Need |
|---------|-------------|
| EdTech companies | Combined CMS + LMS |
| Professional services | Research + portfolio |
| Corporate training | Content + customization |
| Digital agencies | Multi-site management |
| Individual professionals | Portfolio/resume |

### Competitive advantages

- Built-in AI content generation (competitors use add-ons or none)
- Native multi-site management
- Visual template customization (no coding)
- Complete LMS integration
- Open source

---

## Development workflow integration

The workspace is tightly integrated with planning, tracking, and product development.

- **Development flow** — Anytype Capture → Repo Path Mapping → Implementation → Validation → Review → Deployment

### Roadmap and future development

| Phase | Timeline | Focus |
|-------|----------|-------|
| Phase 1 | Q1-Q2 2026 | Platform foundation |
| Phase 2 | Q3-Q4 2026 | AI integration |
| Phase 3 | Q1-Q2 2027 | Enterprise features |
| Phase 4 | Q3-Q4 2027 | Marketplace |
| Phase 5 | 2028+ | Platform expansion |

---

## Related

- → `overview.md` — High-level architecture
- → `editions.md` — Edition boundaries
- → `../plans/startup-planner.md` — Product and business strategy
- → `../plans/operational-plan.md` — Operations and deployment
- → `../plans/risk-management.md` — Risk assessment
- → `../README.md` — Anytype hub
