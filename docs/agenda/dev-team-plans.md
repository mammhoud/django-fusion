---
Object type: Plan
Tags: development, engineering, roadmap
Status: Published
---

# Development Team Plans

> **Scope:** What engineering delivers across Structa Cloud products, in priority order.
> **Owner:** Mahmoud (General Manager)
> **Updated:** 2026-09-12
>
> **This file tracks outcomes, not implementation.** Commands, frameworks, file
> paths, and environment setup deliberately live in the engineering guides
> ([`docs/guides/`](../guides/README.md), [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md))
> and each product's own documentation — not in the agenda.

---

## Active vertical slices (priority order)

| # | Product | Priority | Delivered | Next gate | Owner |
|---|---------|:--------:|-----------|-----------|-------|
| 1 | Formint edition chain | P0 | Community, Standard, Client complete | Professional: sync + invoicing • Cloud: multi-tenant SaaS | Moustafa |
| 2 | Precis Landing | P0 | Render-first public site live | Ongoing content work | Moustafa |
| 3 | Precis LMS (unified) | P1 | Learning + marketing shell shipped | Deployment and build gates | Yahia |
| 4 | CTC Research | Active | Content, multi-language catalogs, media, deploy | Publish gates: email parity, redeploy validation | Asmaa |
| 5 | Syntara | Active | AI chat and customizer shipped | Live provider credentials for real AI calls | Mahmoud |
| 6 | Loop-CRM | Active | Merge complete at feature level | Operational only: live provider credentials, realtime hardening on the deployed stack, demo-state server verification | Mahmoud |
| 7 | django-fusion (shared framework) | P2 | Components, fragments, tasks, config cascade | Task/MCP consolidation, routing unification | Yahia |

**Key plans:** [`docs/plans/README.md`](../plans/README.md) is the registry — this
file never states plan status on its own.

---

## ✅ Implementation status truth — 2026-09-12

> "Delivered" means it exists and works in the current tree. "Still open" is
> planned or blocked. "Couldn't add" records work intentionally deferred **with
> the reason** — usually a deploy or a credential, not a missing feature.

| Product | Delivered | Still open | Couldn't add (reason) |
|---------|-----------|------------|-----------------------|
| **Loop-CRM** | Workspace tenancy + roles, CRM pipeline/board, marketing publishing + connectors, attribution, finance ledger, billing/subscriptions, Wagtail landing, workflows, realtime events, AI hub (consent-gated), EN/AR locale | Live provider credentials, realtime hardening, demo-state server check | Deploy-gated: needs the deployed stack and provider secrets |
| **Precis LMS** | Wagtail content + learning backend, unified marketing shell | Deployment/build gates, builder surfaces | — |
| **Precis Landing** | Render-first public site | — | — |
| **CTC Research** | Multi-language catalogs, media serving, deploy pipeline | Publish gates (email parity, redeploy validation) | Deploy-gated |
| **Syntara** | Chat app, model routing, token tracking, customizer | Live AI provider credentials | Local model works; hosted providers need keys |
| **Formint Professional** | Back office + sync, finance ledger groundwork, create/edit screens | Invoicing and reports, client onboarding funnel | — |
| **Formint Cloud** | Multi-tenant backend, realtime API road | Tenant SaaS scale-out, kitchen display, realtime sync | — |
| **Formint Community / Standard / Client** | Offline-first desktop POS editions | Cloud API integration for Client | — |
| **django-fusion** | Component, fragment, task, and config systems | Task/MCP tooling, AI routing consolidation | P2 — not yet scheduled |

---

## 🧱 Backend delivery workstreams — P1

| Workstream | Target editions | Status |
|---|---|---|
| Invoicing — guided creation and editing | Professional, Cloud | Planned |
| Reports — sales, tax, inventory | Professional, Cloud | Planned |
| Unified theme settings across editions | All editions | Planned |
| Cross-team data change coordination | All editions | Planned |
| Client onboarding funnel | Standard, Professional, Cloud | Planned |
| Payment provider integration | Professional, Cloud | Planned |
| LMS: contact collection, workspace provisioning + billing, AI chat metering | Precis LMS | Open |

**Recurring delivery cadence**

| Review | Cadence | Team |
|--------|---------|------|
| Contract review | Weekly | Engineering |
| Data change review | Weekly | Engineering |
| Backward-compatibility check | Bi-weekly | Engineering |
| Performance review | Bi-weekly | Engineering |
| Security dependency audit | Weekly | Engineering |
| Cross-team data impact | Monthly | Engineering + Product |

**Verification rule:** a workstream is only complete when its outcome is checked
by someone other than the owner — see
[`task-tracking.md`](task-tracking.md) § Validating Tasks with the Team.

---

## 📋 Current engineering priorities

| Priority | Action | What proves it |
|----------|--------|----------------|
| P0 | Formint edition chain — next executable slice | Edition acceptance checks |
| P0 | Precis Landing content work — keep the rendering contract | Public pages render correctly |
| P1 | Precis LMS — close frontend and deployment gates | Site checks and builds green |
| P1 | Repository cleanup — don't delete compatibility sources early | Reference scan |
| P2 | Shared framework — task and AI routing consolidation | Framework checks green |
| P2 | Docs maintenance — link validation, stale reference removal | Validator runs clean |

---

## 🔗 Cross-References

- **Plan registry:** [`docs/plans/README.md`](../plans/README.md)
- **Priorities:** [`docs/recommendations.md`](../recommendations.md)
- **Architecture:** [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Engineering guides:** [`docs/guides/README.md`](../guides/README.md)
- **Claims evidence:** [`docs/plans/marketing-claims.md`](../plans/marketing-claims.md)

---

## Remarks & Notes

- Product `AGENTS.md` files are the local source of truth for conventions
- Plans live in `docs/plans/` only — never in `docs/dev/plans/`, `projects/*/docs/`, or a migrated-plans folder
- Completed plans are deleted once superseded; git history is the archive
- Anything a reader would need to *type* belongs in the guides, not here

<!-- AI-generated: review needed -->

---

## 🇸🇦 ملخّص عربي — خطط فريق التطوير

> **النطاق:** ما ينفّذه فريق الهندسة عبر منتجات Structa Cloud، مرتّباً بالأولوية.
> هذا الملف يتابع **النتائج** لا التفاصيل التقنية: الأوامر والأطر والمسارات
> البرمجية مكانها أدلّة الهندسة ووثائق كل منتج.

### سلاسل المنتجات النشطة

| المنتج | الأولوية | ما سُلّم | البوابة التالية | المسؤول |
|---|---|---|---|---|
| سلسلة إصدارات Formint | P0 | المجتمع والقياسي والعميل مكتملة | الاحترافي: المزامنة والفوترة • السحابي: تعدد المستأجرين | مصطفى |
| Precis Landing | P0 | الموقع العام الحيّ | عمل محتوى مستمر | مصطفى |
| Precis الموحّد (التعلّم + التسويق) | P1 | واجهة التعلّم والتسويق | بوابات النشر والبناء | يحيى |
| مركز CTC البحثي | نشط | المحتوى وتعدّد اللغات والوسائط | بوابات النشر: تكافؤ البريد والتحقق من النشر | أسماء |
| Syntara | نشط | المحادثة وأداة التخصيص | بيانات اعتماد مزوّدي الذكاء الاصطناعي الحيّة | محمود |
| Loop-CRM | نشط | اكتمل على مستوى الميزات | بوابات تشغيلية فقط | محمود |
| django-fusion (الإطار المشترك) | P2 | المكوّنات والمهام وسلسلة الإعداد | توحيد المهام والتوجيه | يحيى |

### قاعدة التحقق

لا يُعدّ أي عمل مكتملاً حتى يتحقق منه شخص آخر غير منفّذه، مع تسجيل الدليل —
انظر [`task-tracking.md`](task-tracking.md) § بوابة التحقق مع الفريق.

> المصدر الرسمي لسجل الخطط: `docs/plans/README.md` — لا تخترع حالة الخطة هنا.
