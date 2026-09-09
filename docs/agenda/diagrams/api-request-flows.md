# 🔄 Loop-CRM API Request Flows — UML Sequence Diagrams

> **Purpose:** Define the request/response lifecycle of the Loop-CRM data API
> surface (`/apis/core/`, `/apis/pos/`, `/apis/finance/`, `/apis/billing/`),
> including auth, tenant resolution, and error paths.
> **Status:** Active · **Owner:** Loop-CRM backend

---

## 1. Workspace discovery — `GET /apis/core/workspace/current/`

The WebSocket island and every tenant-scoped call first resolve the caller's
workspace. Auth via session cookie or `Authorization: Bearer`; the tenant is
derived from the authenticated user's membership — never from the client.

```mermaid
sequenceDiagram
    autonumber
    participant U as User / Frontend
    participant A as /apis/core/ URLs
    participant M as Auth + Tenant middleware
    participant W as WorkspaceCurrentView
    participant DB as Postgres (db_loop_crm)

    U->>A: GET /apis/core/workspace/current/
    A->>M: resolve user (session cookie / Bearer token)
    alt No valid auth
        M-->>U: 401 Unauthorized (WWW-Authenticate)
    else Authenticated
        M->>M: tenant = user.workspace membership
        M->>W: pass request (tenant-scoped queryset)
        W->>DB: SELECT workspace WHERE id = tenant.id
        DB-->>W: Workspace row
        W-->>U: 200 {"id", "name", "slug", "plan", ...}
    end
```
![Rendered diagram](/agenda/diagrams/diagrams-api-request-flows-1.svg)

**Request contract**

| Field | Value |
|-------|-------|
| **Method + path** | `GET /apis/core/workspace/current/` |
| **Auth** | Session cookie or `Authorization: Bearer <token>` |
| **Tenant source** | Server-derived from the authenticated user |
| **Success** | `200` — workspace JSON (id, name, slug, plan, settings) |
| **Failure** | `401` unauthenticated · `403` no workspace membership |
| **Headers** | Optional `Accept: application/json`; never trusts client tenant headers |

---

## 2. Dashboard KPIs — `GET /apis/core/dashboard/`

RevOps KPIs: revenue trend, deal pipeline totals, POS + deal split. Uses the
tenant-scoped workspace from request 1.

```mermaid
sequenceDiagram
    autonumber
    participant U as Frontend
    participant A as /apis/core/dashboard/
    participant S as DashboardService
    participant F as apps/finance
    participant C as apps/crm
    participant DB as Postgres

    U->>A: GET /apis/core/dashboard/?range=30d
    A->>A: tenant = workspace of authenticated user
    A->>S: compute KPIs (workspace, range)
    S->>F: revenue events (POS + deal split)
    S->>C: pipeline stages + deal values
    F-->>S: revenue rows
    C-->>S: deal totals
    S-->>A: aggregated KPI payload
    A-->>U: 200 {"revenue_trend", "deals", "pos_split", ...}
```
![Rendered diagram](/agenda/diagrams/diagrams-api-request-flows-2.svg)

---

## 3. Deal stage move — `POST /apis/core/deals/<pk>/stage/`

Kanban drag-and-drop. Validates the target stage belongs to the deal's pipeline
and records the change in the audit log.

```mermaid
sequenceDiagram
    autonumber
    participant U as Frontend (board)
    participant A as /apis/core/deals/<pk>/stage/
    participant V as DealMoveView
    participant S as StageService
    participant L as AuditLog
    participant DB as Postgres

    U->>A: POST {"stage_id": 42, "note": "moved"}
    A->>A: tenant + object permission check
    A->>V: validate stage_id in deal.pipeline.stages
    alt Stage not in pipeline
        V-->>U: 400 {"stage_id": "not a stage of this pipeline"}
    else Valid
        V->>S: move deal (old_stage -> new_stage)
        S->>DB: UPDATE deals SET stage_id
        S->>L: create AuditLog entry (actor, deal, change)
        S-->>V: updated Deal
        V-->>U: 200 {"id", "stage", "stage_order"}
    end
```
![Rendered diagram](/agenda/diagrams/diagrams-api-request-flows-3.svg)

---

## 4. POS sale ingestion — `POST /apis/pos/ingest/sales/`

Idempotent ingestion from Formints POS. Protected by `X-API-Key` (server secret)
and HMAC-signed payloads; retries use the same idempotency key.

```mermaid
sequenceDiagram
    autonumber
    participant P as Formint POS
    participant I as /apis/pos/ingest/sales/
    participant H as HMAC + API-key gate
    participant L as PosLedgerService
    participant DB as Postgres

    P->>I: POST payload (sales, items, payments) + X-API-Key + HMAC
    I->>H: verify API key + HMAC signature
    alt Invalid key/signature
        H-->>P: 401 Unauthorized
    else Valid
        H->>L: ingest (workspace from key, idempotency_key)
        L->>L: check existing PosSale by idempotency key
        alt Already ingested
            L-->>P: 200 {"status": "duplicate", "sale_id": ...}
        else New sale
            L->>DB: INSERT PosSale + PosSaleItem + PosPayment (transaction)
            L->>DB: net refunds into revenue trend
            L-->>P: 201 {"sale_id", "received": [...]}
        end
    end
```
![Rendered diagram](/agenda/diagrams/diagrams-api-request-flows-4.svg)

---

## 5. AI operation — `GET /apis/core/ai/<operation>/`

AI endpoints (catalog, consent, per-operation) require explicit user consent.
The consent gate runs before any model call; responses stream when the
operation supports it.

```mermaid
sequenceDiagram
    autonumber
    participant U as Frontend
    participant A as /apis/core/ai/<operation>/
    participant C as ConsentService
    participant M as ModelProvider
    participant DB as Postgres

    U->>A: GET /apis/core/ai/catalog/
    A-->>U: 200 {"operations": [...], "consent_required": true}
    U->>A: POST /apis/core/ai/consent/ {"accepted": true}
    A->>C: record consent (user, scope)
    C->>DB: INSERT ConsentRecord
    C-->>U: 200 {"status": "accepted"}
    U->>A: GET /apis/core/ai/summarize/?content_id=5
    A->>C: check consent
    alt No consent
        C-->>U: 403 {"consent_required": true}
    else Consent granted
        A->>M: model call (content payload)
        M-->>A: streamed response
        A-->>U: 200 stream (SSE/JSON)
    end
```
![Rendered diagram](/agenda/diagrams/diagrams-api-request-flows-5.svg)

---

## 6. Webhook delivery — outbound `apps/core` webhooks

Webhooks are signed with HMAC and retried with exponential backoff into a
dead-letter queue after max attempts.

```mermaid
sequenceDiagram
    autonumber
    participant E as EventSource (workflow action)
    participant W as WebhookService
    participant H as WebhookEndpoint (external)
    participant Q as DeadLetterQueue
    participant DB as Postgres

    E->>W: fire webhook (event_type, payload)
    W->>DB: INSERT WebhookDelivery (pending)
    loop retry with backoff (max attempts)
        W->>H: POST signed payload (X-Webhook-Signature: HMAC)
        alt 2xx
            H-->>W: accepted
            W->>DB: mark delivered
        else 4xx/5xx/timeout
            W->>W: schedule retry (backoff)
        end
    end
    W->>Q: move to dead-letter after max attempts
    Q-->>W: dlq entry recorded (manual replay possible)
```
![Rendered diagram](/agenda/diagrams/diagrams-api-request-flows-6.svg)

---

## Endpoint map

| Road | Endpoint | Method | Auth | Notes |
|------|----------|--------|------|-------|
| `/apis/core/` | `workspace/current/` | GET | session/bearer | tenant discovery |
| `/apis/core/` | `dashboard/` | GET | session/bearer | RevOps KPIs |
| `/apis/core/` | `reports/` | GET | session/bearer | report catalog |
| `/apis/core/` | `ai/` · `ai/consent/` · `ai/<op>/` | GET/POST | session/bearer + consent | AI gate |
| `/apis/core/` | `employees/` · `employees/<pk>/report/` | GET | session/bearer | HR surface |
| `/apis/core/` | `search/` | GET | session/bearer | global search |
| `/apis/core/` | `badges/` | GET | session/bearer | sidebar counters |
| `/apis/core/` | `locale/` | GET | session/bearer | i18n |
| `/apis/core/` | `board/` | GET | session/bearer | kanban payload |
| `/apis/core/` | `deals/<pk>/stage/` | POST | session/bearer | move deal |
| `/apis/pos/` | `ingest/sales/` | POST | API key + HMAC | idempotent POS ingestion |
| `/apis/billing/` | plan/account/seat surface | GET/POST | session/bearer | billing road |

> The legacy `/api/v1/` copies remain readable but carry
> `Deprecation/Sunset` headers via `APIV1DeprecationMiddleware` — new callers
> must use the `/apis/*` roads.

<!-- AI-generated: review needed -->