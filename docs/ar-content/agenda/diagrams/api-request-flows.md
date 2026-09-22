---
title: تدفقات طلبات Loop-CRM API — مخططات تسلسل UML
description: دورة حياة الطلب/الاستجابة لواجهة بيانات Loop-CRM، بما فيها المصادقة وتحديد المستأجر ومسارات الأخطاء.
navigation:
  title: تدفقات طلبات API
  icon: i-lucide-workflow
---

# 🔄 تدفقات طلبات Loop-CRM API — مخططات تسلسل UML

> **الغرض:** تحديد دورة حياة الطلب/الاستجابة لواجهة بيانات Loop-CRM
> (`/apis/core/`، `/apis/pos/`، `/apis/finance/`، `/apis/billing/`)،
> بما يشمل المصادقة وتحديد المستأجر ومسارات الأخطاء.
> **الحالة:** نشط · **المالك:** خلفية Loop-CRM

---

## 1. اكتشاف المساحة — `GET /apis/core/workspace/current/`

تحلّ جزيرة WebSocket وكل نداء مقصوص على مستأجر مساحة المستدعي أولاً. المصادقة
عبر كوكي الجلسة أو `Authorization: Bearer`؛ ويُستنبط المستأجر من عضوية
المستخدم المُصادَق عليه — لا من العميل أبداً.

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

**عقد الطلب**

| الحقل | القيمة |
|-------|-------|
| **الطريقة + المسار** | `GET /apis/core/workspace/current/` |
| **المصادقة** | كوكي الجلسة أو `Authorization: Bearer <token>` |
| **مصدر المستأجر** | مُستنبَط من الخادم من المستخدم المُصادَق عليه |
| **النجاح** | `200` — JSON للمساحة (id، name، slug، plan، settings) |
| **الفشل** | `401` غير مُصادَق · `403` بلا عضوية مساحة |
| **الترويسات** | `Accept: application/json` اختياري؛ ولا يثق أبداً بترويسات المستأجر من العميل |

---

## 2. مؤشرات اللوحة — `GET /apis/core/dashboard/`

مؤشرات RevOps: اتجاه الإيراد، وإجماليات خط الصفقات، وتقسيم POS + الصفقات.
يستخدم المساحة المقصوصة على المستأجر من الطلب 1.

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

## 3. نقل مرحلة الصفقة — `POST /apis/core/deals/<pk>/stage/`

السحب والإفلات في كانبان. يتحقق من أن المرحلة الهدف تنتمي إلى خط الصفقة ويسجّل
التغيير في سجل التدقيق.

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

## 4. إدخال مبيعات POS — `POST /apis/pos/ingest/sales/`

إدخال عديم الأثر (idempotent) من Formints POS. محميّ بـ `X-API-Key` (سرّ الخادم)
وحمولات موقّعة بـ HMAC؛ وتستخدم إعادات المحاولة مفتاح الأثر نفسه.

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

## 5. عملية ذكاء اصطناعي — `GET /apis/core/ai/<operation>/`

تتطلّب نقاط الذكاء الاصطناعي (الكتالوج، الموافقة، كل عملية) موافقة صريحة من
المستخدم. تُشغَّل بوابة الموافقة قبل أي نداء نموذج؛ وتتدفّق الاستجابات عندما
تدعم العملية ذلك.

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

## 6. تسليم Webhook — Webhooks صادرة من `apps/core`

تُوقَّع الـ Webhooks بـ HMAC وتُعاد محاولتها بتراجع أُسّي إلى طابور الرسائل
الميتة بعد بلوغ الحد الأقصى للمحاولات.

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

## خريطة النقاط

| المسار | النقطة | الطريقة | المصادقة | ملاحظات |
|------|----------|--------|------|-------|
| `/apis/core/` | `workspace/current/` | GET | session/bearer | اكتشاف المستأجر |
| `/apis/core/` | `dashboard/` | GET | session/bearer | مؤشرات RevOps |
| `/apis/core/` | `reports/` | GET | session/bearer | كتالوج التقارير |
| `/apis/core/` | `ai/` · `ai/consent/` · `ai/<op>/` | GET/POST | session/bearer + consent | بوابة الذكاء الاصطناعي |
| `/apis/core/` | `employees/` · `employees/<pk>/report/` | GET | session/bearer | سطح الموارد البشرية |
| `/apis/core/` | `search/` | GET | session/bearer | بحث شامل |
| `/apis/core/` | `badges/` | GET | session/bearer | عدّادات الشريط الجانبي |
| `/apis/core/` | `locale/` | GET | session/bearer | التدويل |
| `/apis/core/` | `board/` | GET | session/bearer | حمولة كانبان |
| `/apis/core/` | `deals/<pk>/stage/` | POST | session/bearer | نقل صفقة |
| `/apis/pos/` | `ingest/sales/` | POST | API key + HMAC | إدخال POS عديم الأثر |
| `/apis/billing/` | plan/account/seat surface | GET/POST | session/bearer | مسار الفوترة |

> تبقى نسخ `/api/v1/` القديمة قابلة للقراءة لكنها تحمل ترويسات
> `Deprecation/Sunset` عبر `APIV1DeprecationMiddleware` — وعلى المستدعين
> الجدد استخدام مسارات `/apis/*`.

<!-- AI-generated: review needed -->
