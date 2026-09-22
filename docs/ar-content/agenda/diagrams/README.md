---
title: مخططات الأجندة — الأصول المعروضة والمصادر
description: كل مخططات الأجندة — صور SVG معروضة مع مصادر mermaid — تدفقات طلبات API، ومخططات ERD لنماذج Django، وعلاقات Rust/SQLite، وBlinko SurrealDB
navigation:
  title: المخططات
  icon: i-lucide-git-branch
object:
  type: "index"
  id: "agenda.diagrams"
attributes:
  source_path: "agenda/diagrams/README.md"
  canonical_route: "/docs/ar/agenda/diagrams"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - diagrams
  - agenda
  - api
  - erd
links:
  - label: "الرئيسية"
    to: "/docs/ar/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "فهرس دراسات الحالة"
    to: "/docs/en/agenda/case-studies/index"
    icon: "i-lucide-book-open"
---

# 📊 مخططات الأجندة — الأصول المعروضة والمصادر

> **الغرض:** مقرّ واحد لكل مخطط يستخدمه نظام الأجندة. يوجد كل مخطط في شكلين:
> **صورة معروضة** (SVG، قابلة للعرض في أي مكان — GitHub، Docus، استيراد Anytype)
> و**مصدر mermaid** الخاص به (قابل للتحرير، مُدار بالإصدارات).
> **الحالة:** نشط · **المالك:** Workspace

---

## أصول المخططات

تقع الصور المعروضة في `docs/public/agenda/diagrams/` وتُقدَّم على
`/agenda/diagrams/<name>.svg`. مصادر mermaid أدناه هي المعيارية — حرِّر
المصدر، أعِد العرض، واستبدل الصورة.

| المخطط | الصورة المعروضة | مصدر Mermaid | يغطّي |
|---------|---------------|----------------|--------|
| تدفقات طلبات Loop-CRM API | [![API flows](/agenda/diagrams/diagrams-api-request-flows-1.svg)](/agenda/diagrams/diagrams-api-request-flows-1.svg) | [api-request-flows.md](./api-request-flows.md) | تسلسلات الطلب/الاستجابة مع ترويسات المصادقة والمستأجر |
| مخطط Django ERD — Loop-CRM | [![Loop-CRM ERD](/agenda/diagrams/diagrams-django-loop-crm-er-1.svg)](/agenda/diagrams/diagrams-django-loop-crm-er-1.svg) | [django-loop-crm-er.md](./django-loop-crm-er.md) | المساحة، CRM، المالية، POS، الفوترة، الإسناد، التسويق |
| مخطط Rust SQLite ERD — Formint Community | [![Rust SQLite ERD](/agenda/diagrams/diagrams-rust-sqlite-er-1.svg)](/agenda/diagrams/diagrams-rust-sqlite-er-1.svg) | [rust-sqlite-er.md](./rust-sqlite-er.md) | مخطط Diesel مع العلاقات وخريطة الوحدات |
| Blinko SurrealDB | [![Blinko SurrealDB](/agenda/diagrams/diagrams-blinko-surrealdb-1.svg)](/agenda/diagrams/diagrams-blinko-surrealdb-1.svg) | [blinko-surrealdb.md](./blinko-surrealdb.md) | طوبولوجيا خدمة ملاحظات Blinko وتدفّق بيانات SurrealDB |
| مخططات دراسات الحالة (القائمة) | لكل دراسة حالة | ملفات دراسات الحالة | مزامنة POS، طابور عدم الاتصال، قائمة QR، ceptor-ai، data-token، stripe، api-token |

---

## كيف تعيد العرض

```bash
# 1. Edit the mermaid block in the source doc
# 2. Encode and render (mermaid.ink):
code='...mermaid...'
b64=$(printf '%s' "$code" | base64 -w0)
curl -s "https://mermaid.ink/svg/$b64" -o docs/public/agenda/diagrams/<name>.svg
```

أو استخدم سكربت العرض المحلي (يتطلّب `node` + `curl`):

```bash
node docs/scripts/render-agenda-diagrams.mjs
```

---

## ذو صلة

- [فهرس دراسات الحالة](/docs/en/agenda/case-studies/index) — مخططات كل دراسة حالة
- [تتبّع الميزات](/docs/ar/agenda/feature-tracking) — المحور؛ والميزات نفسها في `../feature-tracking/<product>.md`
- [نموذج المحتوى](/docs/ar/agenda/content-model) — أين تقع المخططات في تقسيم الحزم

<!-- AI-generated: review needed -->
