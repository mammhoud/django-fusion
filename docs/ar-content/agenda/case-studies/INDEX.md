---
title: فهرس دراسات الحالة
description: فهرس كل دراسات الحالة في نظام الأجندة — POS وdjango-fusion وتنفيذات المنصة مع مخططات mermaid
navigation:
  title: فهرس دراسات الحالة
  icon: i-lucide-book-open
object:
  type: "index"
  id: "case-studies.index"
attributes:
  source_path: "agenda/case-studies/INDEX.md"
  canonical_route: "/docs/ar/agenda/case-studies/index"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - case-studies
  - index
  - navigation
links:
  - label: "الرئيسية"
    to: "/docs/ar/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "تتبّع الميزات"
    to: "/docs/ar/agenda/feature-tracking"
    icon: "i-lucide-target"
---

# 📊 فهرس دراسات الحالة

> كل دراسات الحالة في نظام الأجندة. وتتضمّن كل واحدة مخططات بنية معمارية (mermaid)، وتفاصيل التنفيذ، والنتائج، والدروس المستفادة.
> **اللغة:** كانت السياسة أن دراسات الحالة إنجليزية فقط (بلا ترجمات عربية). وهذا الملف مرآة عربية أُضيفت لاحقاً، ويبقى النص الإنجليزي هو المصدر.

---

## نظام POS

| دراسة الحالة | الأولوية | الحالة | المخططات | الوصف |
|------------|:--------:|--------|:--------:|-------------|
| [مزامنة المحطات المتعددة](./pos-multi-terminal-sync.md) | P0 | مُشحونة | 4 | بث WebSocket + سحب changeset عبر محطات POS |
| [طابور عدم الاتصال](./pos-offline-queue.md) | P0 | مُشحونة | 3 | OutboxQueue متين + تدفّق إعادة المحاولة/التراجع/الرسائل الميتة |
| [قائمة QR](./pos-qr-menu.md) | P0 | مُشحونة | 4 | قائمة مُصدَّرة بلغات متعددة، معاينة/نشر، وأكواد QR للفروع |

## django-fusion (إطار المكوّنات)

| دراسة الحالة | الأولوية | الحالة | المخططات | الوصف |
|------------|:--------:|--------|:--------:|-------------|
| [وسم مزامنة DataToken](./data-token-sync-tagging.md) | P1 | مُشحونة | 3 | وسم صفوف المزامنة عبر GenericForeignKey مع شجرة أب/ابن، وتتبّع التقدّم، وإزالة الوسم تلقائياً |
| [Django-Bolt Fusion](./django-bolt-fusion.md) | P0 | تاريخية | 4 | أنماط django-bolt API عبر Structa Cloud وإصدارات POS، وتكامل MCP |

## المنصة / الذكاء الاصطناعي

| دراسة الحالة | الأولوية | الحالة | المخططات | الوصف |
|------------|:--------:|--------|:--------:|-------------|
| [Ceptor-AI](./ceptor-ai.md) | P1 | نشطة | 5 | عميل دردشة ذكاء اصطناعي، خادم MCP، محوّل BEM، توليد الوكلاء — حالات استخدام الحزمة والبنية |
| [فوترة Stripe](./stripe-billing.md) | P0 | قيد التنفيذ | 3 | خطط الاشتراك (Free/Pro/Enterprise)، الفوترة حسب الاستخدام، Webhooks Stripe، توليد الفواتير |
| [إدارة رموز API](./api-token-management.md) | P0 | قيد التنفيذ | 3 | نموذج الرمز مع النطاقات، التوليد/التدوير/الإبطال، وسيط فرض النطاق، واجهة قائمة الرموز |

---

## ملخّص المخططات

| نوع المخطط | العدد | يُستخدم في |
|--------------|-------|---------|
| `graph TB/LR` | 13 | تدفقات البنية، بنية الحزم، أوضاع النشر، فرض النطاق |
| `sequenceDiagram` | 7 | تسلسلات الطلب/الاستجابة، بروتوكولات المزامنة، تدفّق مصادقة الرمز |
| `stateDiagram-v2` | 8 | دورات حياة الحالة، حالات سير العمل، دورة حياة الاشتراك، دورة حياة الرمز |
| `erDiagram` | 1 | نموذج البيانات (وسم مزامنة DataToken) |
| **الإجمالي** | **29** | عبر 8 دراسات حالة |

---

## كتابة دراسة حالة جديدة

1. انسخ القالب من [`../case-studies.md`](../case-studies.md)
2. أضِف مخطط mermaid واحداً على الأقل (بنية أو تدفّق)
3. تضمين: السياق ← البنية ← التنفيذ ← النتائج ← الدروس
4. اربطها من ملف المنتج في `../feature-tracking/` عند شحن الميزة
5. أضِف مدخلاً إلى هذا الفهرس
6. أعِد عرض صور المخططات: `node docs/scripts/render-agenda-diagrams.mjs`
   (تخرج ملفات SVG في `docs/public/agenda/diagrams/` — انظر
   [`../diagrams/README.md`](../diagrams/README.md))

---

## ملخّص المخططات (حزمة العرض)

كل كتلة mermaid في دراسات حالة هذا الفهرس تُعرَض إلى SVG تحت
`docs/public/agenda/diagrams/` وتُشار إليها داخلياً بعد كل كتلة. والحزمة الكاملة
(مخططات API UML، ومخططات Django/Rust ERD، وBlinko SurrealDB) في
[`../diagrams/README.md`](../diagrams/README.md).

---

## ملاحظات وإرشادات

- كل مخططات mermaid مُتحقَّق منها وسليمة الصياغة
- تستخدم المخططات أربعة أنواع: graph، وsequenceDiagram، وstateDiagram-v2، وerDiagram
- كُتبت دراسات الحالة بالإنجليزية فقط بحسب السياسة؛ وتُضاف المرايا العربية تدريجياً (هذا الملف مثال)
- كل دراسة حالة تربط إلى مدخلات تتبّع الميزات ذات الصلة ودراسات أخرى

<!-- AI-generated: review needed -->
