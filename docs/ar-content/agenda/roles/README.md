---
title: الأدوار — خطط عمل مختصرة
description: خطة مختصرة لكل فرد: المهام، ومعنى الاكتمال، ومن يتحقق منها.
navigation:
  title: الأدوار
  icon: i-lucide-users
object:
  type: "index"
  id: "agenda.roles"
attributes:
  source_path: "agenda/roles/README.md"
  canonical_route: "/docs/ar/agenda/roles"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - roles
  - team
links:
  - label: "لوحة المهام"
    to: "/ar/agenda/task-tracking"
    icon: "i-lucide-list-checks"
---

# الأدوار — خطط عمل مختصرة

> **العربية:** خطة مختصرة لكل فرد. تحتوي كل خطة على مهامه فقط، ومعنى "مكتمل"،
> ومن يتحقق منها. القواعد العامة للفريق في
> [`../../../agenda/task-tracking.md`](../../../agenda/task-tracking.md) § سير التحقق من المهام.
>
> **English:** One short plan per person — that person's tasks, what "done"
> looks like, and who validates it. Team-wide rules live in the task board.
>
> **آخر تحديث:** 2026-09-12

## الفريق

| الفرد | الدور | الخطة | يتحقق من |
|---|---|---|---|
| **Mahmoud** | مدير عام + مطوّر شامل | [`mahmoud-gm.md`](./mahmoud-gm.md) | المحفظة، الإيراد، النطاق |
| **Moustafa** | مدير منتج + تسويق | [`moustafa-pm.md`](./moustafa-pm.md) | خارطة الطريق، القبول، الادعاءات |
| **Yahia** | واجهات أمامية + تصميم تجربة | [`yahia-frontend.md`](./yahia-frontend.md) | المسودات التصميمية، الشاشات |
| **Asmaa** | تطوير البيانات | [`asmaa-data.md`](./asmaa-data.md) | المقاييس، الأدلة |

يشارك `Dariia` في المحتوى والتوثيق وليس له قائمة مهام دائمة.

## القالب (خمسة أسطر، لا أكثر)

كل خطة دور هي: **الهدف** → **جدول المهام** → **يعمل مع** → **متعطّل؟** ولا شيء
غير ذلك. أي قسم يتجاوز شاشة واحدة مكانه [`../../../plans/`](../../../plans/README.md).

## صفوف المهام تُتحقَّق ولا تُبلَّغ

كل صف يسمّي **المتحقِّق** — من يفحص عمود "يكتمل عندما" ويعلّم المهمة مكتملة.
لا أحد يتحقق من مهمته بنفسه. الأزواج ثابتة:

| نوع المهمة | المنفّذ | المتحقِّق |
|---|---|---|
| منتج / مواصفة / نص | Yahia، Asmaa، Dariia | **Moustafa** |
| واجهة / مسار | Yahia | **Moustafa** (القصد) + **Mahmoud** (الاتجاه) |
| مقياس / دليل | Asmaa | **Moustafa** (الادعاءات) + **Mahmoud** (الإيراد) |
| خلفية / تسليم | Mahmoud | **Moustafa** (القبول) |
| الادعاءات قبل النشر | Moustafa | **Mahmoud** (التوقيع النهائي) |

## ذو صلة

- → [`../../../agenda/task-tracking.md`](../../../agenda/task-tracking.md) — لوحة المهام وسير التحقق
- → [`../../../agenda/completion-checklist.md`](../../../agenda/completion-checklist.md) — تعريف الاكتمال
- → [`../../../agenda/.mono-repo/plans/team.md`](../../../agenda/.mono-repo/plans/team.md) — خطة عمل الفريق
