# Structa Cloud — Installed Skills Catalog

> Reference inventory of every installed agent skill in this workspace.
> Skills live in `.agents/skills/<name>/SKILL.md` and are loaded by name.
> No new skills are downloaded here — this catalog documents what is already
> installed so contributors know what exists and when to invoke it.

<!-- AI-generated: review needed -->

## How to Find & Install More Skills

From the command line, community skills can be discovered and installed without
leaving the terminal:

```bash
npx skills find <query>              # search the community catalog
npx skills add <owner/repo> --list   # preview a repo's skills
npx skills add <owner/repo> --skill <name> --yes   # install one skill
```

Installed skills land in `.agents/skills/`. **Always confirm with the user
before installing a community skill** — they are not vetted. After install,
load it by name with the `skill` tool.

## Categories

| Category | Skills |
|----------|--------|
| **Design & UI** | `design-taste-frontend`, `design-taste-frontend-v1`, `industrial-brutalist-ui`, `minimalist-ui`, `gpt-taste`, `high-end-visual-design`, `stitch-design-taste`, `redesign-existing-projects`, `structa-industrial-ui`, `image-to-code`, `imagegen-frontend-web`, `imagegen-frontend-mobile`, `brandkit`, `shadcn`, `shadcn-ui`, `tailwind-design-system`, `frontend-design`, `vercel-react-best-practices` |
| **Content & Marketing** | `content-creator` (redirect), `content-production`, `content-strategy`, `use-case-triage` |
| **Documentation** | `documentation`, `documentation-writer`, `structa-docs`, `deployment-documentation`, `github-actions-docs`, `planning-with-files`, `writing-plans`, `executing-plans` |
| **Backend / Django** | `structa-backend`, `domain-modeling`, `python-performance-optimization`, `api-design-principles`, `explore-data` |
| **Infra & DevOps** | `container-arch-scaling`, `docker-compose`, `dockerfile-validator`, `multi-stage-dockerfile`, `devops-deployment`, `reverse-proxy`, `ssl-tls-management`, `terraform-module-library`, `templates`, `modules`, `deployment-documentation` |
| **AI / Agents / MCP** | `mcp-builder`, `context7`, `find-skills`, `skill-creator`, `brainstorming`, `enhance-prompt`, `full-output-enforcement` |
| **Testing & Verification** | `verification-before-completion`, `tdd`, `webapp-testing`, `agent-browser`, `systematic-debugging`, `explore-data` |
| **Rust / Desktop** | `rust-async-patterns` |
| **Web & UX Review** | `web-design-guidelines`, `extract-design-system` |
| **Other** | `git-commit`, `content-production`, `use-case-triage` |

## Skill Reference

### Design & UI

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `design-taste-frontend` | Anti-slop frontend skill; infers design direction, audits first on redesigns, strict pre-flight check. | Landing pages, portfolios, redesigns. |
| `design-taste-frontend-v1` | The original v1 taste-skill, preserved for backward compatibility. | Projects depending on exact v1 behavior. |
| `industrial-brutalist-ui` | Raw mechanical interfaces: Swiss typographic print + military terminal aesthetics, rigid grids, extreme type contrast, analog degradation. | Data-heavy dashboards, declassified-blueprint feel. |
| `minimalist-ui` | Clean editorial interfaces: warm monochrome, typographic contrast, flat bento grids, muted pastels. No gradients, no heavy shadows. | Editorial, calm, premium-minimal designs. |
| `gpt-taste` | Elite UX/UI + GSAP motion: strict AIDA structure, wide editorial typography, gapless bento grids, ScrollTrigger animations. | Motion-rich landing pages. |
| `high-end-visual-design` | High-end agency design: exact fonts, spacing, shadows, card structures that feel expensive; blocks cheap AI defaults. | Premium brand-level UI. |
| `stitch-design-taste` | Semantic Design System for Google Stitch; generates agent-friendly DESIGN.md files. | Stitch-based design system work. |
| `redesign-existing-projects` | Upgrades existing sites to premium quality; audits current design, identifies generic AI patterns. | Redesigning an existing live site. |
| `structa-industrial-ui` | The Structa Cloud Swiss Industrial Print design system (monorepo-personalized industrial-brutalist). | Any Structa product UI following the in-repo design language. |
| `image-to-code` | Generates design images first, analyzes them, then implements the site to match. | Visually important web tasks. |
| `imagegen-frontend-web` | Premium conversion-aware website design references; one image per section. | Landing page / marketing site design reference images. |
| `imagegen-frontend-mobile` | App-native screen concepts inside premium phone mockups. | iOS/Android/cross-platform app screens. |
| `brandkit` | High-end brand-guidelines boards, logo systems, identity decks. | Brand identity deliverables. |
| `shadcn` / `shadcn-ui` | Manage shadcn/ui components: adding, fixing, debugging, composing UI incl. chat interfaces. | Any shadcn/ui work. |
| `tailwind-design-system` | Scalable design systems with Tailwind CSS v4, design tokens, component libraries. | Tailwind v4 design systems. |
| `frontend-design` | Distinctive, intentional visual design guidance; avoids templated defaults. | New UI or reshaping existing UI. |
| `vercel-react-best-practices` | React/Next.js performance optimization from Vercel Engineering. | React/Next.js perf review or writing. |
| `web-design-guidelines` | Review UI for Web Interface Guidelines compliance, accessibility, UX. | "Review my UI", "check accessibility". |
| `extract-design-system` | Extract design primitives from a public site; generate starter token files. | Reverse-engineering a site's design tokens. |

### Content & Marketing

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `content-creator` | **Deprecated redirect** — routes to content-production (writing) or content-strategy (planning). | Legacy "content creator" requests. |
| `content-production` | Full pipeline: research → brief → draft → optimize → publish; brand voice + SEO tools. | Writing a blog post, article, guide. |
| `content-strategy` | Strategic planning: topic clusters, keyword research, content calendars. | "Content plan", "what should I write". |
| `use-case-triage` | Determine whether a processing activity needs a PIA / GDPR DPIA. | Privacy/PIA triage questions. |

### Documentation

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `documentation` | Write and maintain technical documentation; READMEs, API docs, runbooks. | "Write docs for…", "document this". |
| `documentation-writer` | Diátaxis expert: Tutorials / How-to / Reference / Explanation. | Structured multi-type documentation. |
| `structa-docs` | Repo-personalized conventions: real docs layout, ADR format, Remarks & Notes rule, AI-review markers, path sync. | **Any docs work in this monorepo.** |
| `deployment-documentation` | Document deployment processes, CI/CD, infrastructure, runbooks. | Deployment guides, infra docs. |
| `github-actions-docs` | GitHub Actions workflows: write, explain, migrate, secure, troubleshoot. | Any GitHub Actions work. |
| `planning-with-files` | Persistent file-based planning (task_plan.md, findings.md, progress.md); survives context loss. | Multi-step planning with 5+ tool calls. |
| `writing-plans` | Turn a spec into a written implementation plan before touching code. | Multi-step task with a spec. |
| `executing-plans` | Execute a written plan in a separate session with review checkpoints. | Running an approved plan. |

### Backend / Django

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `structa-backend` | Structa Cloud backend conventions: Django + Wagtail + django-fusion. | **Any backend work in this monorepo.** |
| `domain-modeling` | Build/sharpen the domain model, ubiquitous language, ADRs. | Pinning domain terminology. |
| `python-performance-optimization` | Profile + optimize Python with cProfile and memory profilers. | Slow Python, bottlenecks. |
| `api-design-principles` | REST/GraphQL API design: intuitive, scalable, maintainable. | New API design or review. |
| `explore-data` | Profile/explore a dataset: shape, quality, patterns, null rates. | New table or file, data quality checks. |

### Infra & DevOps

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `container-arch-scaling` | Containerized architecture scaling + full-stack docs for this monorepo. | Scaling or container architecture. |
| `docker-compose` | Define/run multi-container apps with Compose. | Multi-service local development. |
| `dockerfile-validator` | Validate/lint/audit Dockerfiles for security + best practices. | Dockerfile review. |
| `multi-stage-dockerfile` | Optimized multi-stage Dockerfiles for any language. | Authoring Dockerfiles. |
| `devops-deployment` | CI/CD pipelines, containerization, Kubernetes, IaC. | Pipelines, K8s, Terraform. |
| `reverse-proxy` | Configure nginx/Traefik, SSL termination, routing. | Gateway configuration. |
| `ssl-tls-management` | Let's Encrypt + internal PKI, renewal, cipher suites. | HTTPS/certificates. |
| `terraform-module-library` | Reusable Terraform modules for AWS/Azure/GCP/OCI. | IaC modules. |
| `templates` | Coder templates: scaffold, edit, push, version. | Coder workspace templates. |
| `modules` | Add a Coder module from registry.coder.com. | Coder module additions. |

### AI / Agents / MCP

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `mcp-builder` | Build MCP servers (Python FastMCP or Node SDK). | MCP server integration. |
| `context7` | Up-to-date library/framework docs via Context7 API. | Checking current API usage. |
| `find-skills` | Discover and install agent skills. | "Find a skill for X". |
| `skill-creator` | Create/edit/optimize skills, run evals. | New skill or skill improvement. |
| `brainstorming` | Explore intent, requirements, design before implementation. | **Before any creative/feature work.** |
| `enhance-prompt` | Transform vague UI ideas into polished, Stitch-optimized prompts. | Improving prompt specificity. |
| `full-output-enforcement` | Overrides LLM truncation; enforces complete output, bans placeholders. | Exhaustive, unabridged output. |

### Testing & Verification

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `verification-before-completion` | Run verification commands and confirm output before claiming completion. | **Before any "done" claim.** |
| `tdd` | Test-driven development, red-green-refactor. | Building features test-first. |
| `webapp-testing` | Playwright toolkit for local web app interaction + screenshots + logs. | Verifying local frontend behavior. |
| `agent-browser` | Browser automation CLI: navigate, fill, click, screenshot, scrape, test. | Any browser automation / QA / dogfooding. |
| `systematic-debugging` | Structured debugging before proposing fixes. | Any bug or unexpected behavior. |
| `git-commit` | Conventional-commit message generation + intelligent staging. | `/commit` requests. |

### Rust / Desktop

| Skill | Purpose | Invoke when |
|-------|---------|-------------|
| `rust-async-patterns` | Tokio, async traits, error handling, concurrency. | Async Rust applications. |

## Loading a Skill

```text
skill "industrial-brutalist-ui"
```

Load the skill by name to get its full instructions, then follow them.

## Remarks & Notes

- Skills marked with a **`*` in the category table** (e.g. `shadcn-ui`, `frontend-design`) are pre-loaded session skills; the rest are installed under `.agents/skills/`.
- Community skills are unvetted — confirm with the user before `npx skills add`.
- Keep this catalog in sync when skills are added or removed: `ls .agents/skills/` is the source of truth.
