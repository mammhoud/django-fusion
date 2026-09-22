---
Object type: Plan
Tags: analytics, metrics, data
Status: Published
---

# Data Analyst Plans

> **Scope:** Metrics, analytics, evidence tracking, pilot validation, and data-driven decisions across Structa Cloud products
> **Updated:** 2026-08-25

---

## Core responsibilities

### 1. Evidence-backed claims validation
**Source:** `docs/plans/marketing-claims.md`
**Rule:** Objective claims require evidence before publication

| Claim Level | Meaning | Publication Rule |
|-------------|---------|------------------|
| Capability | Product designed/implemented to do something | Say "supports"/"includes" only when release evidence exists |
| Pilot Evidence | Observed in named internal/customer pilot | Include scope, date, sample, limitation |
| Measured Claim | Reproducible benchmark/operational metric | Include method, baseline, environment, review date |
| Regulated Claim | Compliance/legal outcome | Require local specialist/legal review |

### 2. Approved positioning language

| Claim | Audience | Evidence Required | Safe Wording Now |
|-------|----------|-------------------|------------------|
| Arabic-first | MENA restaurant operators | RTL, translation, invoice UX tests | "Designed for Arabic and bilingual restaurant workflows." |
| Offline-first | Operators with unstable connectivity | Offline/reconnect acceptance tests | "Continue core operations during interruptions and reconcile later." |
| KDS | Restaurant operators | KDS workflow and pilot evidence | "Route and prioritize kitchen tickets across stations." |
| Multi-branch | Chains and franchises | Branch permissions, publishing, sync tests | "Manage branch operations from a shared control view." |
| Loyalty | Customer-focused restaurants | Ledger, reversal, and consent tests | "Build repeat-visit programs with an auditable rewards ledger." |
| API access | Partners and developers | Versioned schema, auth, rate-limit tests | "Integrate through a versioned API without direct database access." |
| Local-to-cloud path | Growing operators | Migration and restore pilot | "Start locally and move to managed cloud services when ready." |

### 3. Claims Requiring Evidence Before Use
- "Guaranteed uptime" or numerical availability
- "X% faster checkout/KDS/preparation"
- "Fully compliant" with ZATCA, UAE FTA, VAT, or another regulator
- "Saves X%" or "increases revenue/retention by X%"
- "Market leader," "best," "only," or comparative competitor claims
- "Production-ready" for a feature still marked planned or in migration
- Pricing/margin promises not validated against support, hosting, payment, storage costs

---

## 📋 Evidence Record Template

```text
Claim:
Audience:
Release/version:
Evidence type: capability | pilot | measured | regulated
Source or test:
Sample/environment:
Limitations:
Owner:
Confidence:
Review date:
Approval:
```

---

## 🔬 Analytics & Metrics Tracking

### Product-Level Metrics

| Product | Key Metrics | Data Source | Review Cadence |
|---------|-------------|-------------|----------------|
| **Formint Community** | Active installs, offline session duration, sync success rate | Local SQLite + telemetry (opt-in) | Monthly |
| **Formint Professional** | Restaurant count, terminal count, order volume, sync latency | Django backend + PostgreSQL | Weekly |
| **Formint Cloud** | Tenant count, terminal count, uptime, API latency, churn | Django + Channels + Redis | Daily |
| **Precis LMS** | Course enrollments, completion rates, active learners, cert issued | Wagtail + Django analytics | Weekly |
| **Precis Landing** | Catalog views, search conversion, SEO rankings, lead gen | Astro + analytics middleware | Weekly |
| **CTC Research** | Publication views, multi-lang engagement, media downloads | Wagtail + custom analytics | Monthly |
| **Syntara** | Chat sessions, template customizations, provider usage, token costs | Django + AI provider logs | Weekly |
| **Loop-CRM** | Workspace count, contact records, campaign sends, social posts | Django + Channels + social APIs | Weekly |

### Cross-Product Metrics

| Metric | Definition | Products | Target |
|--------|------------|----------|--------|
| **Deployment success rate** | Successful deploys / total attempts | All Django products | > 99% |
| **Test coverage** | Lines covered / total lines (backend) | All Django products | > 80% |
| **Build time** | CI pipeline duration | All products | < 10 min |
| **Security vulnerabilities** | Critical/high CVEs in dependencies | All products | 0 critical, < 5 high |
| **Documentation freshness** | Days since last update | All docs | < 30 days |

---

## 📈 Pilot & Experiment Tracking

### Active Pilots

| Pilot | Product | Start Date | Sample | Status | Owner |
|-------|---------|------------|--------|--------|-------|
| Offline-first reconciliation | Formint Community | 2026-07-15 | 3 restaurants | In progress | Formint team |
| KDS multi-station routing | Formint Pro | 2026-08-01 | 1 chain (5 stations) | Planned | Formint team |
| Arabic RTL invoice UX | Formint Cloud | 2026-08-10 | 2 MENA pilots | Planned | Formint team |
| Multi-branch sync | Formint Cloud | 2026-08-20 | 1 franchise (3 branches) | Planned | Formint team |
| LMS course completion analytics | Precis LMS | 2026-08-01 | All courses | In progress | Precis team |
| AI template customization | Syntara | 2026-07-20 | 50 users | In progress | AI team |

### Experiment Framework

1. **Hypothesis:** Clear, measurable statement
2. **Metric:** Primary + guardrail metrics defined upfront
3. **Sample:** Power calculation, randomization method
4. **Duration:** Fixed timeline with early-stop rules
5. **Analysis:** Pre-registered analysis plan
6. **Decision:** Ship / iterate / kill criteria

---

## 🔧 Data Infrastructure

### Current Stack

| Layer | Technology | Products |
|-------|------------|----------|
| **Primary DB** | PostgreSQL 16 | All Django products |
| **Cache/Queue** | Redis | All Django products (Dramatiq broker) |
| **Local/Offline** | SQLite (Diesel/Rust) | Formint Community, Standard, Client |
| **Analytics** | Custom Django models + Wagtail | Precis, Formint Pro/Cloud, CTC |
| **AI/ML** | Ollama + OpenAI-compatible | Syntara |
| **Export/BI** | CSV/JSON API endpoints | All products |

### Data Access Patterns

- **Real-time:** Django ORM, Channels WebSocket (Formint Cloud)
- **Batch/Analytics:** Management commands, Dramatiq tasks
- **Export:** REST API endpoints with versioned schemas
- **Privacy:** Tenant-scoped queries, GDPR-compliant deletion

---

## 📋 Data Analyst Workflows

### Weekly
- [ ] Review pilot progress & evidence collection
- [ ] Validate new claims against evidence register
- [ ] Update metric dashboards (if applicable)
- [ ] Sync with product leads on data needs

### Per Release
- [ ] Collect release evidence for capability claims
- [ ] Run benchmark comparisons (baseline vs new)
- [ ] Document limitations & confidence intervals
- [ ] Update marketing-claims.md with new evidence

### Quarterly
- [ ] Full claims register review & re-approval
- [ ] Pilot graduation / termination decisions
- [ ] Metric target recalibration
- [ ] Compliance evidence audit (ZATCA, VAT, etc.)

---

## 🔗 Cross-References

- **Marketing Claims Register:** `docs/plans/marketing-claims.md` — authoritative claims & evidence
- **Plan Registry:** `docs/plans/README.md` — all engineering plans with metrics gates
- **Recommendations:** `docs/recommendations.md` — prioritized actions with verification
- **Document Lifecycle:** `docs/plans/document-lifecycle.md` — status, ownership, archive policy
- **Formint Editions:** `docs/plans/editions/README.md` — edition-specific metrics

---

## Remarks & Notes

- Data analyst role spans product analytics, pilot validation, and marketing claim evidence
- All evidence must be traceable to source (test, pilot, benchmark, regulatory review)
- Arabic/English parity applies to metrics dashboards and reports
- Coordinate with dev team for instrumentation & data pipeline changes
- Privacy/GDPR: tenant isolation, consent tracking, right to deletion

<!-- AI-generated: review needed -->

---

## 🇸🇦 ملخّص عربي — خطط محلل البيانات

> **النطاق:** المقاييس، والتحليلات، والتحقق من الأدلة، وتصديق التجارب
> التجريبية، والقرارات المبنية على البيانات.

### مستويات الأدلة وقاعدة النشر

| المستوى | المعنى | قاعدة النشر |
|---|---|---|
| قدرة | المنتج مصمم/منفَّذ ليفعل شيئاً | قل "يدعم/يتضمن" فقط عند وجود دليل إصدار |
| أدلة تجربة | لوحظ في تجربة داخلية/عميل مسماة | اذكر النطاق والتاريخ والعينة والحدود |
| قياس منشور | معيار قابل للتكرار أو مقياس تشغيلي | اذكر الطريقة والأساس والبيئة وتاريخ المراجعة |
| ادعاء منظَّم | نتيجة امتثال/قانونية | يلزم مراجعة مختص محلي/قانوني |

### المقاييس الرئيسية لكل منتج (الإيقاع)

- **Formint احترافي:** عدد المطاعم والطرفيات وحجم الطلبات وزمن المزامنة — أسبوعي.
- **Formint سحابي:** المستأجرون والجاهزية وزمن استجابة API والتسرّب — يومي.
- **Precis نظام التعلّم:** التسجيلات ومعدلات الإكمال والمتعلّمون النشطون — أسبوعي.
- **Loop-CRM:** مساحات العمل وجهات الاتصال والحملات والمنشورات — أسبوعي.
- **عبر المنتجات:** نجاح النشر > 99%، وتغطية اختبارات > 80%، وصفر ثغرات حرجة.

### ادعاءات تمنع قبل توفر الدليل

ضمانات الجاهزية أو النِسب، و"أسرع بـ X%"، و"متوافق كلياً" مع الجهات التنظيمية،
و"الأفضل/الوحيد"، و"جاهز للإنتاج" لميزة مخططة، ووعود تسعير غير مدققة.

> السجل الرسمي للادعاءات: `docs/plans/marketing-claims.md` — هذا الملف يعرّف
> المستويات والصياغة الآمنة فقط.