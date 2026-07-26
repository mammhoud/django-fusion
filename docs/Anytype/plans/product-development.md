---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Plan
Status: Published
Type: Roadmap
Related Plans: operational-plan, market-research
Related Goals: product-goal, technical-goal---

# Product Development Lifecycle

> **Type:** Plan 📋
> **Emoji:** 🏗️
> **Description:** The complete product development lifecycle for Structa Cloud — from idea generation through post-launch maintenance. Maps each phase to repository paths and processes.

---

## Development Phases

### 1. Idea Generation & Conceptualisation

Identify market needs for multi-site Django/Wagtail platforms. Explore AI-assisted content generation and template customisation opportunities.

| Activity | Output | Repo Reference |
|----------|--------|----------------|
| Market need identification | Feature proposals | `features/*.md` |
| Technology exploration | Technical research | `architecture/` |
| Competitive analysis | Market positioning | `plans/market-research.md` |

### 2. Market Validation

Gather feedback from potential customers, industry experts, and stakeholders.

- → `plans/market-research.md` — Market analysis and validation data
- → `tasks/tasks-and-backlog.md` — Feature request tracking

### 3. Requirements Gathering

Define technical requirements for shared templates, multi-site settings, and reusable libraries. Map milestones to repository paths.

| Area | Requirements | Repository Path |
|------|-------------|-----------------|
| Shared Templates | Component system, base templates | `projects/assets/templates/` |
| Multi-Site Settings | Django settings, middleware | `projects/configs/` |
| Reusable Libraries | django-fusion, ceptor-ai | `libs/` |
| Infrastructure | Docker, proxy, databases | `applications/` |

### 4. Design & Prototyping

Design the shared component system using django-fusion. Create proof-of-concept sites.

- **CTC Research** — Research publication platform
- **LMS Demo** — Learning management demonstration
- **VResume** — Professional portfolio builder
- **CyperCloud** — AI Chat Customizer platform

### 5. Development & Coding

Implement sites under their respective project paths. Build shared libraries.

| Site | Path | Focus |
|------|------|-------|
| CTC Research | `projects/ctc-research/` | Research content, courses |
| LMS Demo | `projects/lms/` | Course delivery, progress |
| VResume | `projects/portfolio/` | Portfolio builder |
| CyperCloud | `projects/cypercloud/` | AI chat customization |
| Tinker | `projects/tinker/` | Template customization |

### 6. Testing & Quality Assurance

Run Django checks, pytest, and Docker Compose preflight before each release.

- → `guides/deployment.md` — Pre-deployment validation
- → `architecture/overview.md` — CI/CD pipeline reference

### 7. Feedback Iteration

Collect feedback from beta testers and early adopters. Prioritize improvements in the task backlog.

- → `tasks/tasks-and-backlog.md` — Current tasks and priorities

### 8. Deployment & Launch

Coordinate with marketing, sales, and support teams. Deploy via Makefile targets.

```bash
make deploy              # Full stack deployment
make deploy-databases    # Postgres + Redis
make deploy-app          # Application services
make deploy-proxy        # Traefik proxy
```

- → `plans/marketing-strategy.md` — Go-to-market strategy
- → `guides/deployment.md` — Deployment guide

### 9. Post-Launch Support & Maintenance

Monitor logs and metrics. Maintain communication channels for user feedback and feature requests.

- → `plans/monitoring.md` — Monitoring and metrics
- → `tasks/tasks-and-backlog.md` — Issue tracking

---

## Development Workflow Integration

The Anytype knowledge graph maps directly to the repository structure:

```
Anytype Task → Repository Issue → Makefile Target → Code → PR → Deploy
```

1. A task is captured in Anytype (`tasks/`)
2. It is broken down into Makefile targets
3. Code is written in the matching project path
4. Changes are validated with tests and deployed

---

## Related Docs

- → `market-research.md` — Market analysis and validation
- → `operational-plan.md` — Operations and delivery
- → `project-guide.md` — Repository navigation guide
- → `business-model.md` — Business Model Canvas
- → `startup-planner.md` — Startup planning overview
- → `tasks/tasks-and-backlog.md` — Current tasks
- → `../README.md` — Master index
