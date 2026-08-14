# django-fusion — LLM, AI Components & MCP Enhancement Plan

> **Status:** Planned — architecture and delivery gates defined; runtime provider integrations are not yet claimed complete.
> **Owner:** django-fusion core team with project owners
> **Created:** 2026-08-10
> **Scope:** `libs/django-fusion/`, `projects/precis/main/`, `projects/precis/landi/`, `projects/formints/`
> **Parent plan:** [`django-fusion-tasks-mcp-plan.md`](django-fusion-tasks-mcp-plan.md)

## 1. Purpose

This plan adds the LLM and AI-component layer requested for django-fusion's
background-task and MCP architecture. It covers:

- provider-neutral LLM routing for OpenAI-compatible, Anthropic-compatible, and
  other approved providers;
- explicit capability levels for cost, latency, and reasoning quality;
- MCP tools for AI-assisted component and model design;
- asynchronous execution through `django_fusion.tasks`;
- deterministic caching and optional streaming for long-running generation;
- project-owned adoption in Precis, Landing-Fusion, and Formint; and
- security, privacy, approval, observability, and test gates.

This is an implementation plan, not evidence that every provider, model, MCP
transport, or project task described below is already deployed.

## 2. Decisions and boundaries

### 2.1 Do not install an unverified package from the proposal

The pasted proposal names packages such as `mcp-django-server`,
`django-ninja-mcp`, `drf-mcp`, and `django-mcp-integration`. None becomes an
automatic dependency from this document. Before implementation, verify package
existence, maintenance, license, Django compatibility, transport support,
security model, and transitive dependencies. Prefer the existing
`django_fusion.tasks` MCP surface unless a separately reviewed package provides
clear value.

The initial implementation should not require Django Ninja or Django REST
Framework. Project APIs remain project-owned, consistent with the existing LMS
and Landing-Fusion boundaries.

### 2.2 Keep task execution and LLM access separate

`django_fusion.tasks` owns enqueueing, retries, scheduling, status, and audit
logging. A new LLM gateway owns provider selection, request normalization,
redaction, budgets, response validation, caching, and provider errors.

```text
Django view / MCP request
        │
        ├── read-only or dry-run AI request ──► LLM gateway
        │                                      ├─ policy + budget
        │                                      ├─ cache lookup
        │                                      └─ provider adapter
        │
        └── long-running request ────────────► django_fusion.tasks
                                               └─ LLM gateway in worker
```

LLM calls must never be made directly from model `save()` methods, migrations,
request middleware, or unrestricted MCP handlers.

### 2.3 AI output is advisory by default

Generated models, views, templates, schemas, and component suggestions are
proposals. They must not be written into the repository, applied as migrations,
or executed as code without an explicit, authenticated approval workflow.

The first release supports:

- structured suggestions;
- code and schema previews;
- validation diagnostics;
- downloadable or reviewable artifacts; and
- task status and retry.

The first release does not support arbitrary shell commands, automatic
migration execution, unrestricted file writes, or production deployment from
an MCP tool.

## 3. Current state and target state

### 3.1 Existing capabilities

| Capability | Current evidence | Plan status |
|---|---|---|
| Unified task decorator/registry | `libs/django-fusion/src/django_fusion/tasks/` | Existing surface; integration verification required |
| In-process task backend | `django_fusion.tasks.backends.inprocess` | Existing/test backend |
| Dramatiq backend | `django_fusion.tasks.backends.dramatiq` | Existing surface; production verification required |
| Task MCP definitions | `django_fusion.tasks.mcp_tools` | Existing task-management tools |
| Task MCP handlers/views | `mcp_handlers.py`, `mcp_views.py` | Existing surface; auth and deployment gates remain |
| Project task modules | Precis, Landing-Fusion, and Formint plan targets | Planned adoption |
| Provider-neutral LLM gateway | No canonical gateway identified | Not started |
| AI model-level registry | Not started | Planned |
| Generation cache | Not started as a django-fusion contract | Planned |
| Generation streaming | No canonical project contract | Planned |

### 3.2 Target modules

The exact module names may change after implementation review, but ownership
should remain clear:

```text
libs/django-fusion/src/django_fusion/ai/
├── __init__.py
├── config.py              # validated settings and capability levels
├── gateway.py             # provider-neutral generate/stream interface
├── registry.py            # provider and model capability registry
├── providers/
│   ├── base.py            # adapter protocol and normalized response types
│   ├── openai_compatible.py
│   ├── anthropic.py
│   └── mock.py             # deterministic tests, no network
├── cache.py               # canonical request keys and privacy-aware cache
├── schemas.py             # structured output contracts
├── policy.py              # allowlists, budgets, redaction, approvals
└── errors.py

libs/django-fusion/src/django_fusion/tasks/
├── ai_tasks.py            # queued generation and validation jobs
└── mcp_ai_tools.py        # AI MCP tool schemas and safe handlers
```

Provider adapters should be optional dependencies. Importing django-fusion
must continue to work when no LLM SDK is installed.

## 4. Provider-neutral LLM gateway

### 4.1 Adapter contract

Every provider adapter implements the same normalized contract:

```python
class LLMProvider(Protocol):
    name: str

    def generate(
        self,
        *,
        messages: Sequence[Message],
        model: str,
        response_schema: JsonSchema | None = None,
        max_tokens: int,
        temperature: float,
        timeout_seconds: float,
    ) -> GenerationResult: ...

    def stream(
        self,
        *,
        messages: Sequence[Message],
        model: str,
        max_tokens: int,
        temperature: float,
        timeout_seconds: float,
    ) -> Iterator[GenerationChunk]: ...
```

The implementation must normalize:

- provider and model name;
- request ID and correlation ID;
- text and structured output;
- finish reason;
- token usage when available;
- latency;
- safety or refusal metadata;
- retryable versus permanent errors; and
- cost estimate when pricing data is configured.

Provider-specific response objects must not leak into project task modules.

### 4.2 Provider policy

Initial provider categories:

| Category | Examples | Use |
|---|---|---|
| OpenAI-compatible | OpenAI or an approved compatible endpoint | General reasoning, structured output, embeddings if later approved |
| Anthropic-compatible | Anthropic or an approved compatible endpoint | Long-context analysis and content review |
| Code/reasoning provider | Approved code-focused provider | Code and schema suggestions after evaluation |
| Local/mock | Deterministic mock first; Ollama later if approved | Tests, local development, privacy-sensitive experiments |

Provider selection must be capability- and policy-driven, not hardcoded by a
view. A task asks for a capability such as `component_design` or
`content_review`; the registry resolves the provider and model allowed for the
environment, tenant, data class, and budget.

No API key may be committed. Settings use environment variables or the existing
secret-management mechanism. Logs must never include keys, authorization
headers, complete prompts containing personal data, or full generated secrets.

### 4.3 Capability levels

Use stable product-level names and environment-configurable model mappings:

```python
class AIModelLevel(str, Enum):
    BASIC = "basic"          # low cost, short tasks
    STANDARD = "standard"    # default balanced path
    ADVANCED = "advanced"    # complex reasoning or code review
    ENTERPRISE = "enterprise"  # explicitly enabled, highest controls
```

A registry entry contains:

```text
level, provider, model, capabilities, max_tokens, temperature,
timeout_seconds, daily_budget, allowed_data_classes, structured_output,
streaming, and enabled environments
```

Do not copy obsolete model names from the proposal into production defaults.
Model identifiers, pricing, and availability change. Keep them in deployment
configuration and test with a mock provider.

Fallback rules:

1. reject requests whose data class or budget is not allowed;
2. choose the configured model for the requested capability and level;
3. fall back only to an explicitly approved compatible model;
4. return a typed `ProviderUnavailable` or `BudgetExceeded` result when no safe
   fallback exists; and
5. never silently downgrade an enterprise request to a public provider.

## 5. Structured AI operations

### 5.1 `generate_ai_component`

Purpose: produce a reviewable Django component proposal from requirements.

Inputs:

- requirements;
- component type (`model`, `form`, `view`, `template`, `serializer`, or
  `test`);
- project identifier and allowed app boundary;
- model level;
- optional output schema/version; and
- whether the request is synchronous, queued, or streaming.

Outputs:

- normalized proposal ID;
- provider/model metadata;
- generated files as non-executable text artifacts;
- explanation and assumptions;
- validation warnings;
- required dependencies; and
- approval state (`draft`, `needs_review`, `approved`, `rejected`).

The tool must not modify a checkout. A later project-owned approval command may
apply a reviewed patch after path and content checks.

### 5.2 `define_ai_model`

Purpose: suggest a Django data model from business requirements.

Required safeguards:

- output is a schema proposal, never an applied migration;
- validate field types, nullability, indexes, uniqueness, relationships, and
  PII classification;
- identify destructive or irreversible changes;
- include a migration impact report;
- require human approval before generating a migration artifact; and
- run project checks in an isolated worker before approval.

### 5.3 `design_component`

Purpose: choose a component structure and implementation strategy for an
existing project boundary.

The response should include:

- recommended component type;
- relevant existing django-fusion primitives;
- project-owned files to touch;
- accessibility and security checks;
- tests to add;
- estimated token/cost class; and
- rejected alternatives with reasons when useful.

The tool must prefer existing components and canonical imports over generating
new abstractions.

### 5.4 Content-specific operations

Project-owned tasks may expose safe content operations such as:

- Precis: draft course descriptions, summarize lesson content, or suggest SEO
  metadata for review;
- Landing-Fusion: draft newsletter or blog metadata, warm approved page cache,
  and generate preview copy for editorial review; and
- Formint: produce read-only sales/report explanations and anomaly summaries.

AI must not publish content, change prices, alter inventory, approve a refund,
or send a campaign without a separate explicit product workflow.

## 6. MCP integration

### 6.1 Existing task MCP boundary

The existing task MCP surface remains the canonical administrative layer:

- `task.inspect`
- `task.queues`
- `task.history`
- `task.retry`
- `task.trigger`
- `task.stats`
- `task.purge`
- `task.workers`

AI-generation tools are a separate namespace and must use the task API for work
that exceeds a safe request timeout.

Proposed tools:

- `ai.models.list` — list enabled capabilities and levels, never secrets;
- `ai.component.generate` — create a reviewable proposal;
- `ai.model.suggest` — create a schema proposal and migration impact report;
- `ai.component.validate` — run static/project validation in a sandbox;
- `ai.generation.inspect` — inspect status, usage, and redacted output metadata;
- `ai.generation.cancel` — cancel an eligible queued request; and
- `ai.generation.approve` — only after project authentication and authorization.

### 6.2 MCP request rules

Every MCP request must have:

- JSON-RPC request ID and correlation ID;
- authenticated principal;
- project and tenant/branch scope where applicable;
- tool allowlist and argument schema validation;
- request size and timeout limits;
- audit event with redacted arguments;
- idempotency key for mutating or queueing operations; and
- typed errors rather than raw provider exceptions.

MCP endpoints must not be exposed with a blanket `csrf_exempt` and no
authentication in production. The existing view layer requires a reviewed auth
middleware/decorator before production exposure. Read-only local development
may use a clearly documented local-only mode.

### 6.3 Client connections

Supported clients are documented by transport after implementation:

- local development: Django test client or `http://127.0.0.1` only;
- Claude Desktop or another MCP client: authenticated HTTP MCP transport when
  the client supports it;
- custom LLM applications: use the project API/client boundary, not direct
  database access; and
- VS Code/Freebuff: connect through a documented authenticated MCP or project
  API endpoint, never through an internal Docker hostname.

A deployment URL is configuration, not a hardcoded assumption. Each project
must publish its environment-specific MCP base URL in deployment documentation
without committing credentials.

## 7. Caching and optimization

### 7.1 Deterministic cache keys

Do not use Python's built-in `hash(prompt)` for persistent caching because it is
process-randomized and unsuitable for cross-worker keys. Build a canonical JSON
request containing the provider-independent inputs, then hash it with SHA-256:

```text
cache_key = fusion:ai:v1:<sha256(canonical_request)>
```

The canonical request includes prompt/schema versions, capability, model level,
selected model, temperature, relevant project version, and safe context IDs.
It excludes secrets and raw personal data where a stable redacted representation
is sufficient.

### 7.2 Cache policy

- default TTL is capability-specific and configurable;
- cache only responses marked cacheable by policy;
- do not cache private or regulated content in a shared cache without tenant
  isolation and encryption;
- invalidate when prompt/schema/model versions change;
- record hit/miss and latency metrics without logging the full prompt; and
- allow an authenticated purge by cache key or generation ID.

Caching is an optimization, never the source of truth for generated content.

## 8. Streaming

Streaming is a project API concern, not a requirement that a background task
return a Python generator through a queue. Use:

- a synchronous provider stream for short interactive requests;
- an authenticated SSE/WebSocket or equivalent project endpoint for browser
  clients; and
- queued task status plus persisted chunks/artifacts for long-running work.

Streaming requirements:

- bounded output and idle timeouts;
- disconnect cancellation where supported;
- no partial artifact is marked approved;
- safe retry semantics with a generation ID;
- redacted audit metadata; and
- a final structured result after the stream closes.

MCP transport streaming support must be verified against the selected client;
do not assume that a generic JSON-RPC POST accepts a generator response.

## 9. Per-project adoption plan

### 9.1 Precis LMS

Owner: `projects/precis/main/backend/`.

Candidate task modules:

```text
apps/content/tasks.py       # content summaries and approved metadata drafts
apps/learning/tasks.py      # reports, certificates, course maintenance
apps/handlers/tasks.py      # email and notification orchestration
```

Initial AI scope:

- course-description and SEO metadata drafts;
- progress-report explanations;
- editorial review of uploaded content; and
- async email/notification work through `django_fusion.tasks`.

Required tests cover permissions, PII redaction, course ownership, task retry,
structured output validation, and no-publish-without-approval behavior.

### 9.2 Landing-Fusion

Owner: `projects/precis/landi/backend/`.

Candidate task modules:

```text
apps/content/tasks.py      # blog metadata and editorial drafts
apps/learning/tasks.py     # learning/catalog maintenance where applicable
apps/handlers/tasks.py     # newsletter/contact notification orchestration
```

Initial AI scope:

- blog and page metadata drafts;
- newsletter copy drafts that remain unpublished;
- approved page-cache warming; and
- contact/newsletter notifications through the unified email task.

The Astro frontend may consume generation status through a project-owned API,
but it must retain the existing render/data boundary and must not embed provider
SDKs or secrets in browser code.

### 9.3 Formint POS

Owner: `projects/formints/`; apply edition boundaries from the canonical edition
plans.

- Community and Standard remain Rust/Diesel-first and do not require a Django
  or LLM sidecar for core offline operation.
- Pro and Cloud may use `django_fusion.tasks` for sync, reports, notifications,
  and approved AI advisory workflows.
- AI must be read-only for sales, stock, prices, refunds, and sync until a
  separately approved command workflow exists.
- DataToken and sync records remain authoritative for reconciliation; generated
  text never becomes a synchronization event by itself.

Candidate operations:

- explain daily sales or inventory reports;
- draft purchasing or waste insights for operator review; and
- summarize branch anomalies using permission-scoped data.

## 10. Configuration contract

Use namespaced environment-backed settings. The exact secret provider may vary
by deployment, but these names should remain stable:

```text
FUSION_AI_ENABLED=false
FUSION_AI_DEFAULT_LEVEL=standard
FUSION_AI_PROVIDER=mock
FUSION_AI_ALLOWED_PROVIDERS=mock
FUSION_AI_TIMEOUT_SECONDS=30
FUSION_AI_MAX_OUTPUT_TOKENS=4000
FUSION_AI_DAILY_BUDGET=0
FUSION_AI_CACHE_ENABLED=false
FUSION_AI_CACHE_TTL_SECONDS=3600
FUSION_MCP_ENABLED=false
FUSION_MCP_BASE_URL=
FUSION_MCP_TOKEN=
FUSION_AI_OPENAI_API_KEY=
FUSION_AI_ANTHROPIC_API_KEY=
FUSION_AI_DEEPSEEK_API_KEY=
```

Defaults must be safe:

- mock provider or disabled in tests and local environments;
- no provider key required to import the package;
- no external network call during unit tests;
- no MCP mutation tools enabled by default; and
- zero budget means no paid provider request, not unlimited usage.

## 11. Dependencies and rollout

### 11.1 Dependency decision gate

Before adding SDKs, record:

1. package name and pinned compatible version range;
2. Python/Django compatibility;
3. license and maintenance evidence;
4. sync and async client behavior;
5. timeout/retry support;
6. structured output and streaming support;
7. security and data-retention implications; and
8. package size and deployment impact.

Use optional dependency groups such as `ai-openai`, `ai-anthropic`, and
`ai-local` only after approval. The mock provider and core schemas remain in
the base package.

### 11.2 Delivery phases

| Phase | Deliverable | Status |
|---|---|:---:|
| A | Freeze architecture, data classes, policy, and threat model | Planned |
| B | Add mock provider, capability registry, and deterministic structured schemas | Planned |
| C | Add cache key/version policy and redacted usage metrics | Planned |
| D | Add one approved provider adapter behind an optional dependency | Planned |
| E | Add queued generation/validation tasks | Planned |
| F | Add read-only AI MCP tools and authenticated local endpoint | Planned |
| G | Integrate one Precis and one Landing-Fusion editorial workflow | Planned |
| H | Integrate Formint read-only reporting for Pro/Cloud only | Planned |
| I | Add streaming endpoint and client verification | Planned |
| J | Security, cost, load, failure, and rollback review | Planned |
| K | Enable production providers per project with explicit budgets | Planned |

## 12. Security and governance gates

- Authenticated MCP endpoint with project/tenant/branch authorization.
- Provider and model allowlists; no user-supplied arbitrary provider URL.
- Prompt and output size limits, timeouts, rate limits, and per-project budgets.
- Redaction/classification before external provider calls.
- No secrets or full sensitive prompts in task logs, cache keys, traces, or
  browser payloads.
- Generated code is inert text until reviewed and validated in isolation.
- Human approval for migrations, repository writes, publishing, campaigns,
  prices, stock, refunds, and sync mutations.
- Retention and deletion policy for prompts, outputs, artifacts, and provider
  metadata.
- Provider outage and quota exhaustion return actionable typed errors.
- Kill switch per project, provider, level, and tool namespace.

## 13. Testing and observability

### django-fusion tests

- provider adapter normalization with the mock provider;
- model-level selection and fallback policy;
- schema validation and malformed provider output;
- deterministic cache keys and version invalidation;
- redaction and forbidden data classes;
- timeout, retry, cancellation, and budget handling;
- queued task status transitions;
- MCP tool allowlists, authentication, idempotency, and typed errors; and
- streaming disconnect and final-result behavior.

### Project tests

- Precis course/content permission and approval flows;
- Landing-Fusion editorial draft and publish separation;
- Formint report scope, offline behavior, and no mutation guarantees;
- frontend status/loading/error/timeout states; and
- clean install without optional provider SDKs.

### Metrics

Record provider-neutral metrics:

```text
fusion_ai_requests_total{project,capability,provider,level,status}
fusion_ai_latency_seconds{project,capability,provider}
fusion_ai_tokens_total{project,provider,model}
fusion_ai_cache_total{project,capability,result=hit|miss}
fusion_ai_budget_denied_total{project,level}
fusion_ai_approval_total{project,operation,result}
```

Do not expose raw prompts, completions, API keys, or personal data in metric
labels.

## 14. Success criteria

- [ ] Provider-neutral gateway imports without optional SDKs installed.
- [ ] Mock provider gives deterministic tests for every AI operation.
- [ ] Capability levels and provider mappings are environment-configured.
- [ ] OpenAI-compatible and one additional approved provider pass adapter tests.
- [ ] All long-running generation uses `django_fusion.tasks` and has status,
      retry, cancellation, and audit behavior.
- [ ] Cache keys are canonical SHA-256 keys with versioned invalidation.
- [ ] Streaming is verified with a real supported client and bounded timeouts.
- [ ] AI MCP tools are authenticated, allowlisted, schema-validated, and
      disabled by default in production until approved.
- [ ] Precis and Landing-Fusion have one reviewed editorial AI workflow each.
- [ ] Formint Pro/Cloud has read-only advisory reporting without changing POS
      authority or DataToken synchronization.
- [ ] No generated code, model, migration, content, campaign, price, stock, or
      refund is applied without explicit approval.
- [ ] Cost, privacy, outage, and rollback runbooks are complete.

## 15. Related plans

| Plan | Path |
|---|---|
| Unified tasks and task MCP | [`django-fusion-tasks-mcp-plan.md`](django-fusion-tasks-mcp-plan.md) |
| django-fusion enhancements | [`django-fusion-enhancements.md`](django-fusion-enhancements.md) |
| Worker consolidation | [`../repository/worker-consolidation.md`](../repository/worker-consolidation.md) |
| Landing-Fusion plan | [`../precis/landi/README.md`](../precis/landi/README.md) |
| Precis product handoff | [`../../../projects/precis/main/README.md`](../../../projects/precis/main/README.md) |
| Precis backend guidance | [`../../../projects/precis/main/backend/AGENTS.md`](../../../projects/precis/main/backend/AGENTS.md) |
| Formint Professional plan | [`../pos/formint-pos-professional-plan.md`](../pos/formint-pos-professional-plan.md) |
| POS editions index | [`../editions/README.md`](../editions/README.md) |
| Plan registry | [`../README.md`](../README.md) |

*Update this document only when implementation evidence, dependency decisions,
and verification results are available.*
