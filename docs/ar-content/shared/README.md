---
title: النواة المشتركة والعمال
description: نواة Django المشتركة، عمال Dramatiq، مجدول APScheduler، وموقع السنتينيل لمونوريبو Structa Cloud.
navigation:
  title: Shared
  icon: i-lucide-cpu
---

# ⚙️ النواة المشتركة والعمال

> **أسماء ذات صلة:** `shared`، `shared-worker`، `shared-scheduler`، `tasks`، `موقع السنتينيل`، `مهام خلفية`، `Dramatiq`، `Celery`
> **الوسوم:** #project #shared #shared-core #worker #celery #dramatiq #tasks

**المسار المعياري:** `projects/www/`  
**اسم مستعار موقع Django:** `shared` → يُحل إلى `path: www` في `sites.yml`  
**المنفذ:** 5080

---

## نظرة عامة

يوفر المشروع `shared` نواة Django مشتركة، عمال Dramatiq للمهام الخلفية، مجدول APScheduler للمهام الدورية، وموقع "سنتينيل" مركزي للصحة والمراقبة عبر مونوريبو Structa Cloud.

---

## المكونات

| المكون | التقنية | الغرض |
|-----------|----------|---------|
| **Shared Core** | Django + django-fusion | النماذج المشتركة، الإعدادات، الوسيط |
| **Shared Worker** | Dramatiq + Redis | تنفيذ المهام الخلفية |
| **Shared Scheduler** | APScheduler | تنفيذ المهام الدورية |
| **Sentinel Site** | Django + django-fusion | الصحة، المراقبة، لوحة الإدارة |

---

## البنية التحتية

- **PostgreSQL** — قاعدة البيانات الأساسية
- **Redis** — وسيط Dramatiq، التخزين المؤقت، الجلسات
- **Dramatiq** — عامل المهام الأساسي
- **APScheduler** — جدولة المهام الدورية

---

## الأدلة ذات الصلة

- [التكوين](/docs/ar/shared/configuration)
- [الطرق المشتركة](/docs/ar/shared/shared-methods)
- [حالات الاستخدام](/docs/ar/shared/use-cases)

---

## ملاحظات وإرشادات

- المشروع `shared` هو "موقع السنتينيل" — لا يحتوي على منطق أعمال المنتج، بل يوفر البنية التحتية المشتركة.
- عمال Dramatiq يستخدمون Redis كوسيط؛ المهام مجدولة عبر APScheduler.
- لا تشغل الهجرات أو أوامر تدميرية ضد بيئة مشتركة دون موافقة صريحة.

<!-- AI-generated: review needed -->
