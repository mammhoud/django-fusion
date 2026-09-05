---
title: نظام جدول المشروع
description: نظام تتبع الفريق، دراسات الحالة، إدارة المهام، جداول الاجتماعات وقوائم إتمام المشاريع لمنتجات Structa Cloud
navigation:
  title: نظام الجدول
  icon: i-lucide-clipboard-list
object:
  type: "guide"
  id: "agenda.readme"
attributes:
  source_path: "agenda/README.md"
  canonical_route: "/docs/en/agenda/readme"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - agenda
  - overview
  - arabic
links:
  - label: "الجدول الرئيسي"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 📋 docs/agenda/ — نظام جدول المشروع

> تتبع الفريق، دراسات الحالة، إدارة المهام، جداول الاجتماعات، وقوائم إتمام المشاريع لمنتجات Structa Cloud.

## ما يوجد في هذا الدليل

| الملف | الغرض |
|-------|--------|
| **`CONTENT_MODEL.md`** | ⭐ تعريف الجدول — مسرد مفاهيم Anytype، تقسيم الكائنات/ملفات markdown، وعقد مرجع الفريق (كل رابط يمر عبر الخطط والإنجازات). **اقرأه أولًا.** |
| **`MAIN.md`** | المركز/فهرس — كيف يرتبط كل شيء |
| **`feature-tracking.md`** | دورة حياة الميزات: Proposed → Prioritized → In Progress → Review → Shipped |
| **`case-studies.md`** | دراسات حالة تنفيذات حقيقية مع مخططات عمارة mermaid |
| **`task-tracking.md`** | لوحة مهام السبرينت — المسؤولين، الحالة، المواعيد النهائية |
| **`team-notes.md`** | ملاحظات الاجتماعات، القرارات، العقبات — ذكاء الفريق المكتوب |
| **`meeting-agenda.md`** | قوالب لتخطيط السبرينت، الاجتماع اليومي، المراجعة، ال	retrospective، مراجعة الميزة، الإغلاق |
| **`completion-checklist.md`** | قائمة تحقق إغلاق المشروع — تعريف "مكتمل" + معايير التوقيع |
| **`INDEX.md`** | فهرس Blinko-style (مُشير قديم) |

## البدء السريع

```
جديد على الجدول؟  → CONTENT_MODEL.md (التعريف، الحزم، عقد المرجع)
ميزة جديدة؟ → feature-tracking.md
مهمة جديدة؟ → task-tracking.md
اجتماع؟ → meeting-agenda.md (انسخ القالب) + team-notes.md (سجّل الملاحظات)
ميزة منشورة؟ → case-studies.md (اكتب دراسة حالة مع مخطط) + feature-tracking.md (حدّث الحالة)
خطة مكتملة؟ → CONTENT_MODEL.md § 4.2 (احذف الخطة → سجّل إنجاز ✅ Shipped)
مشروع مكتمل؟ → completion-checklist.md (شغّلها) + team-notes.md (سجّل القرار)
```

## كيف يرتبط بالباقي من docs/

```
docs/agenda/MAIN.md
├── docs/agenda/feature-tracking.md ──→ docs/features/feature-roadmap.md
├── docs/agenda/case-studies.md ──────→ docs/plans/README.md
├── docs/agenda/task-tracking.md ─────→ docs/features/feature-roadmap.md
├── docs/agenda/team-notes.md ───────→ docs/plans/README.md (القرارات الكبيرة)
├── docs/agenda/meeting-agenda.md ───→ docs/agenda/task-tracking.md
└── docs/agenda/completion-checklist.md ──→ docs/agenda/feature-tracking.md
                                                           → docs/agenda/case-studies.md
                                                           → docs/plans/README.md
```

## إلهام Anytype

تم تصميم نظام الجدول هذا ب inspire من نموذج Anytype القائم على الكائنات:

| مفهوم Anytype | ما يعادله في الجدول |
|---------------|---------------------|
| **كائن (Object)** | مهمة، ميزة، دراسة حالة، ملاحظة اجتماع |
| **نوع (Type)** | ميزة، مهمة، دراسة حالة، ملاحظة اجتماع — الفئة |
| **خصائص (Properties)** | الحالة، المسؤول، الأولوية، الموعد، السبرينت — البيانات الوصفية |
| **روابط (Links)** | الميزة → دراسة الحالة، المهمة → الميزة، الاجتماع → القرار |

مثلما تقول Anytype: "كل شيء كائن. الكائنات تسأل 'ما هذا يتعلق به؟'" — مدخلات جدولنا كائنات ترتبط ببعضها، ليس ملفات في مجلدات.

راجع: [أشياء Anytype](https://doc.anytype.io/anytype/create/objects)، [أنواع Anytype](https://doc.anytype.io/anytype/organize/types)، [خصائص Anytype](https://doc.anytype.io/anytype/organize/properties)

## المخططات

جميع مخططات العمارة والتدفق تستخدم mermaid. الأنماط:

- `graph LR/TB` — عمارة وتدفق البيانات
- `sequenceDiagram` — تسلسلات الطلب/الرد
- `stateDiagram-v2` — دورة الحياة
- `erDiagram` — نماذج البيانات

جرب المخططات مع `npm run validate-content` في `docs/docus/`.

## الصيانة

- **المالك:** قادة workspace / المنتجات
- **تكرار المراجعة:** كل سبرينت + بوابات الإصدار الرئيسية
- **أضف مدخلات عندما:** ميزات تنشر، مهام تكتمل، اجتماعات تحدث، قرارات تتخذ
- **أرشيف عندما:** المشاريع تُغَلَّق (اتبع `docs/plans/document-lifecycle.md`)

---

## ملاحظات وإرشادات

- هذا نظام عمل، ليس عبء بيروقراطي — إذا قالب لا يخدم الفريق، عدّله
- المخرجات الأكثر قيمة هي دراسات الحالة مع مخططات mermaid — هي ذكاء الفريق المؤسسي
- ربط كل شيء يرتبط بكل شيء آخر — المدخلات المعزولة تفقد قيمتها
- حافظ على المدخلات محدثة — التتبع القديم أسوأ من لا تتبع

<!-- AI-generated: review needed -->
