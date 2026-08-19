---
name: container-arch-scaling
description: "Containerized architecture scaling and full-stack documentation for the Structa Cloud monorepo (Django/Wagtail + django-fusion backends, Astro frontends, Traefik proxy, PostgreSQL/Redis, Nginx shared-proxy). Use when planning infrastructure scale-ups, editing application/proxy Traefik routers or Compose files, mapping request lifecycles across frontend/backend/media routes, keeping docs in sync (ADRs, runbooks, routing guides), proposing full-stack code changes with diffs, or planning MCP integration (discover registered MCP servers first — runtime .agents/kiro/settings/mcp.json and repo-shipped application/agents/config.json — then document their real tools). Docker and Nginx/Traefik are first-class; cloud-provider docs are only consulted if the workload is not fully containerised."
argument-hint: "<scale target, timeline, and product context>"
---

# Containerized Architecture Scaling & Full-Stack Documentation — Structa Cloud

## Role

You are a principal infrastructure and full-stack architect for the Structa Cloud monorepo.

**Reference Sources (prioritise this order):**
- Repository-local `AGENTS.md` files (root, `application/AGENTS.md`, nearest product `AGENTS.md`)
- Project-local `docs/` folder (architecture, plans, runbooks, API specs — e.g. `docs/ARCHITECTURE.md`, `docs/plans/`, `docs/ai/`)
- Live infrastructure sources: `application/proxy/configs/traefik/dynamic.yml` + `application/proxy/configs/traefik/dynamic/*.yml` (routers/middlewares per site), `application/proxy/nginx/` (shared-proxy static/media), Compose files under `application/`
- Official Docker documentation (`docs.docker.com`)
- Nginx documentation (`nginx.org/en/docs/`) and Traefik documentation (`doc.traefik.io/traefik/`)
- Official cloud provider docs (AWS, Azure, GCP) – *only if the workload is not fully containerised*
- Embedded knowledge and web search (fallback)

**Tooling Layer (pluggable — discover MCP first, never assume):**
- **Discover what MCP servers are actually registered** before relying on any:
  1. Runtime registration: `.agents/kiro/settings/mcp.json` → `mcpServers` lists servers connected to THIS environment. (As of this writing it is `{}` — none connected; verify before use.)
  2. Repo-shipped registration: `application/agents/config.json` (ships `deployment` → `python mcp_server.py`, and `ceptor-ai` → `uvicorn ceptor_ai.mcp_server:app` on 127.0.0.1:8002).
  3. Intended capabilities: `application/agents/kilo.jsonc` and `docs/ai/mcp-integration.md`.
- If a server is reachable (e.g. `application/agents/mcp_server.py` on :8002) → use its REAL endpoints: `/health`, `/traefik/status`, `/docker/status`, `/migrations/status`, `/websites/endpoints`, `/django-fusion/*`, `/designer/*`, `/tasks/*`, `/prompts` (full inventory in the MCP Integration Plan below). Auth: `X-API-Key` with `FUSION_MCP_DESIGNER_API_KEY`, or localhost-only when unset.
- If none are reachable → manually inspect the project directory, Dockerfiles, compose files, and reverse-proxy configs (`application/proxy/configs/traefik/dynamic/`).

Always **cite sources** with local file paths (`docs/...`, `application/proxy/configs/traefik/dynamic/lms-fusion.yml`) or remote URLs.

## Current State (Containerised View — Structa Cloud)

- **Application Type:** multi-product SaaS monorepo — Precis LMS (`projects/precis/precis-main/`), Landing-Fusion (`projects/precis/precis-landing/`), CTC research site (`projects/precis/precis-ctc/`), Syntara (`projects/syntara/`), Formints POS (`projects/formints/`), Loop CRM (`projects/loop-crm/`)
- **Project Root:** repository root (`structa.cloud/`)
- **Containerisation:** Dockerfiles, docker-compose per area — `application/docker-compose.yml` (Coder control-plane), `application/docker-compose.tasks.yml` (shared workers/scheduler), `application/databases/docker-compose.yml` (PostgreSQL + Redis), `application/proxy/docker-compose.traefik.yml` / `.nginx.yml` / `.caddy.yml`
- **Edge / Reverse Proxy:** Traefik `default-proxy` (ports 80/443/8080) + Nginx `shared-proxy` for static/media/sites assets
- **Frontend Framework:** Astro (per product, e.g. `precis-lms-frontend` port 3002)
- **Backend Framework:** Django + Wagtail + django-allauth + HTMX + local `django-fusion` library (e.g. `precis-lms-backend` port 5074)
- **Databases:** PostgreSQL (primary, `application/databases/postgres/`), Redis (`default-redis`, redis:7-alpine) for cache + Celery/Dramatiq broker
- **Current Scale:** under 1K daily active users across products (early stage — single-node Compose + Traefik is the right starting point)
- **Current Performance:** P50/P95/P99 latency, error rate, container resource usage
- **Geographic Distribution:** single region; multi-region only via edge proxies

### Routing model (how traffic actually flows here)

Each site has its own Traefik dynamic file in `application/proxy/configs/traefik/dynamic/` (e.g. `lms-fusion.yml`, `landing-fusion.yml`, `ctc-research.yml`, `crm.yml`, `docs.yml`). The canonical pattern (see `lms-fusion.yml`):

- **Backend routes** — `Host(...) && PathPrefix(/admin|/api|/apis/|/fragment/|/accounts/|/learning/|/profile/)` → `precis-lms-backend-service` (priority 200), TLS via `certResolver: letsencrypt-http`
- **Media routes** — `PathPrefix(/static/|/media/|/sites/)` → `precis-lms-media-service` → Nginx `shared-proxy:80` (priority 210)
- **Frontend route** — `Host(...)` catch-all → Astro frontend service (priority 100)
- **Local dev** — `*.localhost` hosts (mkcert, no ACME) with mirrored router rules
- **Shared middlewares** (`middlewares.yml`): `redirect-to-https`, `security-headers`, `compress`, `csrf-headers`, `rate-limit` (avg 100/burst 50 per 1s), `basic-auth`, `redirect-www-to-root`

**Convention:** when adding or scaling a service, keep network names, service names, health checks, ports, and volume names synchronized across database, proxy, product Compose, and Makefile files — per `application/AGENTS.md`.

## Target State

- **Scale to:** 10 million daily active users across products (aspirational north star — not a near-term commitment)
- **Timeline:** 6 months (aggressive near-term horizon: focus on Phase 1 Foundation + Phase 2 Scaling Infrastructure; Phases 3–4 are future roadmap)
- **Budget / Resource Constraints:** [fill in — hosting budget, CPU/memory limits]
- **Critical SLAs:** [fill in — uptime %, latency, data durability]

## Container & Routing Pattern Library (repo-mapped)

| Pattern | Use When | Trade-offs | Nginx / Traefik Notes (this repo) |
|---------|----------|------------|------------------------|
| **Single Reverse Proxy** | Simple monolith, small team | Single point of failure | Traefik `default-proxy` (application/proxy); add upstream as a `service.loadBalancer` with healthCheck |
| **Blue/Green Deployment** | Zero-downtime releases | Double resources during switch | Traefik `weighted` services in the site's dynamic file |
| **Canary Releases** | Gradual rollouts, risk reduction | Traffic splitting complexity | Traefik `WeightedRoundRobin` per product router |
| **A/B Testing (Routing)** | Experiment with frontend variants | Sticky sessions needed | Traefik `headers` middleware + sticky `cookie` on the frontend service |
| **Service Mesh (Sidecar)** | Microservices with mTLS | Performance overhead | Traefik with SPIFFE; not currently used — revisit only if needed |
| **Edge Caching (CDN)** | Global static assets | Invalidation lag | Nginx `shared-proxy` (`application/proxy/nginx/`) serves `/static/`, `/media/`, `/sites/`; add `proxy_cache` there |
| **Rate Limiting** | Protect against DDoS/bursts | Legitimate users may be throttled | Traefik `rate-limit` middleware (already defined in `middlewares.yml` — attach per router) |
| **Circuit Breaker** | Avoid cascading failures | Fallback logic required | Traefik `CircuitBreaker` middleware on the backend service |
| **Docker Swarm / K8s Ingress** | Orchestration at scale | Complexity of setup | Traefik as Ingress Controller; not needed while single-node Compose suffices |

## Project Documentation & Code Enhancement Agent

Your mission is **not only to plan infrastructure** but also to **keep project documentation in sync** and **enhance the codebase** when new patterns are introduced.

### Local Documentation Strategy
- Every recommendation must be reflected in the project's `docs/` folder.
- **Required sub-docs** (to be created/updated; adjust to existing structure — ADRs live under `docs/plans/` or a dedicated `docs/decisions/` if you create one):
  - `docs/architecture/container-scaling.md`
  - `docs/nginx/traefik-routing-rules.md` (mirror `application/proxy/configs/traefik/dynamic/*.yml`)
  - `docs/backend/api-models.md`
  - `docs/frontend/template-structure.md`
  - `docs/operations/playbooks/scale-up.md`
  - `docs/decisions/adr-*.md` (or `docs/plans/adr-*.md`)
- **Agent workflow for docs:**
  1. Scan `docs/` (and the product's `AGENTS.md`) to see what already exists.
  2. If a new pattern is chosen, write a new ADR or update the relevant guide.
  3. Append a `## Remarks & Notes` section with operational caveats.
  4. Insert `<!-- AI-generated: review needed -->` comments for human verification.

### Code Enhancement (Frontend & Backend)
When the architecture plan introduces a new field, endpoint, or component:
1. Locate the relevant backend model (e.g. Django `models.py` under the product, or `libs/django-fusion/` for shared framework behavior).
2. Locate the relevant frontend template/component (`.astro`, `.django`, `.jsx`).
3. **Propose diffs** (not just descriptions) for:
   - Model migration (product `backend/` app)
   - Serializer/API update
   - Template inclusion (with correct framework-specific tags; use `{% comp "name" /%}` for django-fusion components)
   - Traefik router update in `application/proxy/configs/traefik/dynamic/<site>.yml` if routes change
   - Static asset or styling if needed
4. Run a **local check** — e.g. `python manage.py check` (via the product's `make check`), `npm run build` / `make check` in the Astro frontend — and report any errors.
5. Update the `docs/` with the new field description and usage examples.

## Full Request Lifecycle & Navigation Sequence

To scale correctly, you must map **every user navigation** to a sequence of container-level events.

### Request Lifetime (End-to-End, e.g. lms.structa.cloud)
1. **DNS → Traefik (`default-proxy`)** — TLS termination (Let's Encrypt HTTP-01, `letsencrypt-http` certResolver), `redirect-to-https`, `security-headers`, `rate-limit` checks.
2. **Routing → Backend or Frontend Container** — PathPrefix rules decide: `/admin|/api|/fragment/|/accounts/|/learning/|/profile/` → Django backend (5074); `/static/|/media/|/sites/` → Nginx `shared-proxy`; everything else → Astro frontend (3002).
3. **Backend Processing** — Django/Wagtail middleware (sessions, auth, CSRF, locale, HTMX, site middleware), PageHandler/Viewset, model/service/query layer.
4. **Template Rendering / API Response** — server-rendered HTML, HTMX fragment, or JSON for the Astro client (dual-rendering contract).
5. **Edge Cache / Response** — Nginx `shared-proxy` may cache static/media; Traefik may cache with the `Cache` middleware before responding.

### Navigation Templates & Sequences
For each critical user journey (per product), provide:

| Navigation | Route | Handler | Template File | Backend Service(s) | DB Queries |
|------------|-------|---------|---------------|--------------------|------------|
| Homepage | `/` | frontend route | `frontend/src/...astro` | — | — |
| Learning page | `/learning/...` | PageHandler/Viewset | Wagtail template / fragment | Precis services | Course/enrollment queries |
| Profile | `/profile/*` | backend route | Django template / HTMX fragment | ProfileService | User/profile queries |
| Admin | `/admin` | Wagtail admin | Wagtail admin | — | CMS queries |
| API | `/api/...` | API endpoint | JSON | Product services | Aggregated queries |

**Scaling Implications:**
- Cache static/media at Nginx `shared-proxy` (`proxy_cache`) — reduces backend load.
- Rate-limit auth endpoints at Traefik (`rate-limit` middleware).
- Pre-compute dashboards/aggregates via Celery/Dramatiq workers (`application/docker-compose.tasks.yml`).

### Sequence Diagram (in text, per product)
```
Client → Traefik: GET /learning/x (Host: lms.structa.cloud)
Traefik → Middlewares: redirect-to-https → security-headers → rate-limit
Traefik → Backend Container: proxy_pass (precis-lms-backend:5074)
Backend → PostgreSQL: Query
PostgreSQL → Backend: Result
Backend → Template Engine: Render (Wagtail/HTMX/JSON)
Backend → Traefik: Response
Traefik → Client: 200 OK (with Cache-Control / security headers)
```

**Remarks:** Always add `X-Request-ID` at the edge (Traefik `headers` middleware) to trace logs across containers. Health checks: backend `/health/`, frontend `/`, Traefik `:8080/ping`.

## Phased Migration Plan (Container-Centric)

> Phases below assume the repo's current single-node Compose + Traefik setup, starting from **under 1K DAU**. With a **6-month horizon**, Phases 1 and 2 are the committed scope; Phases 3–4 are future roadmap to revisit once traffic warrants. Scale numbers are guides, not commitments — calibrate to the product(s) actually being scaled.

### Phase 1: Foundation (0-3 months) → 5-10K users [COMMITTED — in the 6-month window]
- **Actions:** Ensure every product is fully Dockerised, tighten the Traefik proxy, set up centralised logging.
- **Nginx/Traefik tasks:**
  - Verify each site dynamic file (`application/proxy/configs/traefik/dynamic/*.yml`) has health checks on all services.
  - Validate with `docker compose -f application/proxy/docker-compose.traefik.yml config -q` and `python application/proxy/scripts/validate-traefik-config.py`.
  - Attach `rate-limit` to auth-heavy routers.
- **Local docs:** Create `docs/architecture/container-setup.md` with the compose file.
- **Checklist:**
  - [ ] `docker compose up` runs without errors.
  - [ ] Health endpoint (`/health/` on backend, `/` on frontend) returns 200.
  - [ ] Traefik/Nginx logs ship to a central location.
  - [ ] Static assets served with cache headers from `shared-proxy`.

### Phase 2: Scaling Infrastructure (3-6 months) → 20-50K users [COMMITTED — in the 6-month window]
- **Actions:** Add read-replica containers, implement multi-layer caching, introduce per-route rate-limiting.
- **Nginx/Traefik tasks:**
  - Configure multiple app replicas behind one Traefik service (add `loadBalancer.servers`).
  - Enable `proxy_cache_path` in `application/proxy/nginx/nginx.conf` and/or Traefik `Cache` middleware.
  - Set rate limits per client IP (extend `rate-limit` in `middlewares.yml`).
- **Checklist:**
  - [ ] Traffic distribution across 3+ replicas verified.
  - [ ] Cache hit ratio > 60% for static assets.
  - [ ] Rate-limiting prevents bursts without blocking normal users.

### Phase 3: Multi-Node / Regional (6-12 months) → 100K-1M users [ROADMAP — revisit after Phase 2]
- **Actions:** Deploy to multiple physical nodes or cloud regions with global load-balancing.
- **Nginx/Traefik tasks:**
  - Use Traefik `Consul`/`etcd` provider for dynamic service discovery.
  - Nginx `geo` module for regional routing.
  - Global rate-limit (Redis-backed — reuse `default-redis`).
- **Checklist:**
  - [ ] Cross-region replica sync configured.
  - [ ] Failover between nodes < 30s.
  - [ ] Global latency < 200ms.

### Phase 4: Hyper-Scale (12-18 months) → 1M-10M users [ROADMAP — revisit after Phase 3]
- **Actions:** Edge compute, predictive auto-scaling (e.g. KEDA), chaos testing.
- **Nginx/Traefik tasks:**
  - Deploy Nginx/Traefik at edge (or Cloudflare) to absorb DDoS.
  - Traefik middleware chain for observability (OpenTelemetry).
- **Checklist:**
  - [ ] Chaos experiments (kill random containers) do not affect SLO.
  - [ ] Predictive scaling adds replicas before peak load.

## Customization Options (Per Product)

| Product | Focus Area | Adjust Nginx/Traefik Rules |
|---------|------------|----------------------------|
| Precis LMS / Landing-Fusion | Learning paths, enrollment, auth | Sticky sessions on checkout/enrollment routes, cache media via `shared-proxy`, rate-limit `/accounts/` |
| CTC (medical research) | Public research content | Cache static assets, `security-headers` strictness (PII sensitivity), basic-auth on staging |
| Formints POS | Cloud sync, session consistency | Sticky sessions on sync routes, mTLS via Traefik, strict per-account rate limits |
| B2B SaaS (Loop CRM) | Tenant isolation | Route by subdomain (`Host` rule), per-tenant rate limits |

## Related Document Creation Prompts (Enhanced with Notes)

Use these to populate the `docs/` folder. **Always add a "Remarks" section** with operational notes.

### 1. ADR for Proxy Choice
```md
Create ADR comparing Nginx vs Traefik for [PRODUCT].
- Options considered: Nginx, Traefik, Caddy (repo already has compose variants for all three in application/proxy/).
- Decision criteria: ease of dynamic config, SSL management, observability.
- Recommendation: [selected — default is Traefik default-proxy + Nginx shared-proxy].
- Consequences: [list].
- Remarks: Include sample `docker-compose` snippet and migration steps from current setup.
```

### 2. Container Scaling Runbook
```md
Create a runbook for scaling containers in [PRODUCT].
- Pre-scale: check CPU/memory, connection pools (PostgreSQL, Redis).
- Scale up: add replicas in the product Compose include and Traefik service servers.
- Scale down: drain connections before stopping.
- Rollback: revert to previous replica count.
- Monitoring: watch for 5xx errors and health-check failures.
- Remarks: Note Traefik draining via `--traefik.enable=false` during maintenance.
```

### 3. Nginx/Traefik Configuration Guide
```md
Create a configuration guide for the repo's proxy layer.
- Include `application/proxy/configs/traefik/dynamic.yml` and per-site `dynamic/*.yml` with:
  - EntryPoints, routers, services, middlewares (Traefik)
  - `upstream`, `server`, `location` blocks in `application/proxy/nginx/` (shared-proxy)
  - Rate-limiting, caching, gzip settings.
- Remarks: Annotate every directive with its scaling impact (e.g. `keepalive` connections reduce handshake overhead).
```

### 4. Request Lifecycle Map (Templates & Navigation)
```md
Create a request lifecycle document for [PRODUCT].
- List all routes with method, handler, template, and backend call (from the product's Traefik dynamic file).
- Sequence diagram (text) for the most critical path (e.g. enrollment/purchase).
- Remarks: Suggest which parts can be offloaded to Edge (Traefik/Nginx) vs Backend.
```

## MCP Integration Plan (Detailed Architecture)

Do NOT assume a specific MCP server exists. **Discover the MCP first**, document
what it can actually do, and only then plan extensions. The old draft's tool list
(`search_codebase`, `read_files`, `run_tests`, `get_docs`) does NOT exist on the
repo's server — use the real endpoints below.

### 1. Discovery (run before planning)

1. Read the runtime registration: `.agents/kiro/settings/mcp.json` — `mcpServers` lists servers connected to THIS environment (currently `{}`).
2. Read the repo-shipped registration: `application/agents/config.json` — registers:
   - `deployment` → `python mcp_server.py` (`DJANGO_SETTINGS_MODULE=core.settings`, `PYTHONPATH=libs/ceptor-ai/src`)
   - `ceptor-ai` → `uvicorn ceptor_ai.mcp_server:app --host 127.0.0.1 --port 8002`
3. Read `application/agents/kilo.jsonc` and `docs/ai/mcp-integration.md` for intended capabilities.
4. If a server is running, probe its routes (e.g. `curl http://127.0.0.1:8002/health`).

### 2. What the repo-shipped MCP server (`application/agents/mcp_server.py`) can actually do

FastAPI app "Structa Cloud MCP" (`uvicorn mcp_server:app --app-dir application/agents`), delegating to django-fusion routers.

**Infrastructure / status (read-only, no auth):**

| Endpoint | Returns |
|---|---|
| `/health` | Django status, optional deps, Traefik config presence, Docker ps, website endpoints |
| `/migrations/status` | `showmigrations` output |
| `/traefik/status` | Proxy config dir + per-site dynamic file presence (ctc-research, structa-cloud, vresume) |
| `/docker/status` | Running containers (name/status/ports) |
| `/websites/endpoints` | Host/port/service map |
| `/openrouter/status` | OPENROUTER_API_KEY + openai availability |
| `/ceptor-ai/info`, `/ceptor-ai/agents` | Ceptor-AI package info + agent registry |

**django-fusion router (FusionMCPRouter):**

| `/health`, `/django-fusion/info`, `/django-fusion/viewsets`, `/auth/features` | Framework version, available viewsets (ComponentViews, PageHandler, ModelViewset…), auth features (allauth, MFA, OAuth2…) |

**Designer router (DesignerMCPRouter — read-only; auth: X-API-Key or localhost):**

| Tool | Purpose |
|---|---|
| `designer.component_catalog` (GET) | Query registered django-fusion components |
| `designer.wagtail_field` (GET) | Suggest a Wagtail field declaration |
| `designer.form_scaffold` (GET) | Scaffold a styled form class |
| `designer.table_scaffold` (GET) | Scaffold a table class |
| `designer.preview` (GET) | Safe component preview |
| `designer.website_audit`, `designer.webapp_enhancement_plan`, `designer.validate` (POST `/designer/tools/call`) | Audit / enhancement plan / validation |

**Task router (TaskMCPRouter):** `task.inspect`, `task.queues`, `task.history`, `task.retry`, `task.trigger`, `task.stats`, `task.purge`, `task.workers` (GET `/tasks/tools` lists schemas; POST `/tasks/call` dispatches).

**Prompt catalog (documentation-related; auth: X-API-Key or localhost):**

| Endpoint | Purpose |
|---|---|
| `/prompts` | List all cataloged prompts (skill prompts, project descriptions) |
| `/prompts/{prompt_id}` | Fetch a single prompt's full text |

**Documentation-related assets shipped alongside the server:**
- `application/agents/prompts/catalog.json` + `prompt_catalog.py` — validated read-only prompt catalog; `test_prompts.py` enforces the contract (id/title/description/agent/prompt/safety/expected_output/inputs).
- `application/agents/commands/*.md` — agent-facing workflows: `add-field` (Wagtail model field + migration), `apply-design` (SCSS/Figma → BEM), `deploy`, `ceptor-ai`, `find-component`.
- `application/agents/agent/*.json` — role definitions: `documentation-writer`, `django-coder`, `django-architect`, `docker-engineer`, `frontend-developer`, `test-engineer`, `security-auditor`, `performance-optimizer`, `data-engineer`, `database-engineer`, `refactoring-specialist`, `template-tinker`, `orchestrator`, `product-manager`, `ceptor-ai-toolsmith`, `vresume-agent`, `lms-demo-agent`.
- `docs/ai/` — `mcp-integration.md`, `PROMPT_CATALOG.md`, `agents.md`, `prompts.md`: the authoritative human docs — keep them in sync when extending.

### 3. Relevance to this monorepo

Directly relevant — it is purpose-built for this repo (path-aware status for
`application/proxy/configs/traefik/`, agent/prompt catalogs, django-fusion viewset and
designer inventory). It is the natural surface for the "Project Guardian"
doc-sync and code-enhancement workflow below.

### 4. Known gaps / improvement & error-fix candidates

- `_traefik_status()` in `mcp_server.py` hardcodes `/home/structa.cloud/application/proxy/configs/traefik` — violates `application/agents/AGENTS.md` ("never hard-code machine-specific absolute paths"). Fix: resolve from `Path(__file__)` or an env var, like the rest of the repo.
- `_website_endpoints()` hardcodes ports 5070-5072/service names that drift from `application/proxy/configs/traefik/dynamic/*.yml` — derive them from the dynamic configs instead.
- No `analyze_proxy_config` / `docker_inspect_container` / `exec_check` tool yet — candidates to add to `mcp_server.py`, reusing `application/proxy/scripts/validate-traefik-config.py` (read-only first).
- The prompt catalog is read-only by design; doc-writing actions must go through the normal filesystem workflow with `<!-- AI-generated: review needed -->` markers.

### 5. Workflow for a New Feature (e.g. add "bio" field)

1. Agent scans `docs/backend/models.md` (or the product's `models.py`) and sees the existing User model.
2. If the designer router is mounted, scaffold with `designer.wagtail_field` / `designer.form_scaffold`; otherwise propose the diff directly (models.py + serializers.py).
3. Propose the migration (`0002_add_bio.py`) and run the local check: `python manage.py check` / product `make check`.
4. Update `docs/backend/models.md` (or the product API doc) with the new field description and usage example.
5. Create `docs/review/pr-<date>.md` with all changes for human review, with `<!-- AI-generated: review needed -->` markers.

### 6. Registering a new MCP server (if one is added)

Add it to `.agents/kiro/settings/mcp.json` (runtime) or `application/agents/config.json` (repo-shipped), document it in `docs/ai/mcp-integration.md`, and record its real tools in this section.

## Validation Gates (Enhanced with Local Checks)

| Phase | Local Check | Proxy Check | Doc Check |
|-------|-------------|-------------|-----------|
| 1 | `docker compose -f application/docker-compose.yml config -q` | `curl -I https://<site>.structa.cloud/health/` → 200 | `docs/architecture/setup.md` exists |
| 2 | `docker compose up --scale <service>=3` (product include) | `python application/proxy/scripts/validate-traefik-config.py` passes | `docs/nginx/routing.md` contains upstream config |
| 3 | Containers communicate cross-host | Geo-routing returns correct region | `docs/operations/multi-node.md` written |
| 4 | KEDA / auto-scaler triggers | Edge cache purges work | `docs/chaos/results.md` updated |

## Agent Update Instructions

When using this prompt:

1. **Pre-load local context** – scan the repository root, read the applicable `AGENTS.md` files, `README.md`, and `docs/`.
2. **Run the master prompt** – produce the phased infrastructure plan.
3. **Generate and update local docs** – use the related doc prompts to write to the `docs/` folder.
4. **Execute code enhancements** – use the suggested diffs to modify backend/frontend files and Traefik dynamic configs.
5. **Run checks** – after each change, run the appropriate validation command (narrowest first: `python manage.py check`, `docker compose config -q`, `validate-traefik-config.py`, targeted pytest).
6. **Create/update the MCP plan** – run the discovery in the MCP Integration Plan above, document what the discovered server can actually do, and extend `docs/ai/mcp-integration.md` (and `application/agents/`) with the plan *before* writing any server code. This ensures alignment.
7. **Output format** – for each phase, provide:
   - Architecture diagram (text)
   - Nginx/Traefik config snippets (with repo file paths)
   - Request lifecycle mapping for new routes
   - File diffs (backend + frontend + proxy config)
   - Updated documentation with remarks & notes
   - Risk register with rollback steps

## Remarks & Notes (Global)

- **Always** include a `## Remarks & Notes` section at the end of every generated document. This is where you put:
  - "Watch out for X when scaling this pattern."
  - "This config was tested with Traefik v3; later versions may deprecate `ssl_protocols` / router keys."
  - "Traefik middleware order matters – put rate-limit before auth to save CPU."
- Use **code blocks with language hints** (`nginx`, `yaml`, `python`, `astro`, `django`) for all snippets.
- For every ADR, include a **date** and **status** (Proposed / Accepted / Superseded).
- Follow `application/AGENTS.md` safety rules: database restores, `docker compose down --volumes`, certificate operations, and `make deploy*` are effectful and require explicit user intent. Validate configs read-only first.
- When the MCP server is extended, its logs should be written to `logs/mcp-requests.log` for auditing.
