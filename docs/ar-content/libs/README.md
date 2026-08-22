---
title: المكتبات — نظرة عامة
description: حزم Python القابلة لإعادة الاستخدام التي تشغّل كل مشاريع Structa Cloud.
navigation:
  title: المكتبات
  icon: i-lucide-library
---

# المكتبات — نظرة عامة

> حزم Python القابلة لإعادة الاستخدام التي تشغّل كل مشاريع Structa Cloud.

---

## كتالوج المكتبات

| المكتبة | المصدر | الوثائق |
|---------|--------|---------|
| **django-fusion** | `libs/django-fusion/` | [`AGENTS.md`](../../../libs/django-fusion/AGENTS.md) |
| **ceptor-ai** | `libs/ceptor-ai/` (قيد الانتظار) | مستودع خارجي |
| **django-bolt** | `libs/django-bolt/` (قيد الانتظار) | مستودع خارجي |

---

## django-fusion

نظام المكونات والتوجيه المعياري. الميزات:
- وسم قالب `{% comp %}` مع خصائص وفتحات ونطاق HTMX
- توجيه `Site`, `Application`, `Viewset`, `ModelViewset`
- `FormMixin`, `TableMixin`, `FormTableMixin`
- كتل Wagtail StreamField وsnippets وviewsets
- فحوصات الصحة (`/health/`)

📖 الوثائق الكاملة: [`libs/django-fusion/README.md`](../../../libs/django-fusion/README.md)
📖 دليل اللغة: [`django-fusion-language.md`](/docs/en/libs/django-fusion-language)

---

## ceptor-ai

عميل دردشة ذكاء اصطناعي + خادم MCP. يشغّل Syntara (مخصص دردشة الذكاء الاصطناعي).

📖 خارجي: [github.com/mammhoud/ceptor-ai](https://github.com/mammhoud/ceptor-ai)

---

## django-bolt

إطار API عالي الأداء مدعوم بـ Rust. إنتاجية تتجاوز 60 ألف طلب/ثانية.

📖 خارجي: [github.com/dj-bolt/django-bolt](https://github.com/dj-bolt/django-bolt)

---

## مراجع متقاطعة

| الموضوع | الرابط |
|---------|--------|
| Precis Landing | [`../precis/precis-landing/README.md`](/docs/en/precis) |
| Precis LMS | [`../precis/README.md`](/docs/en/precis) |
| Formints POS | [`../pos/README.md`](/docs/en/pos) |
| البنية التحتية | [`../../infrastructure/`](/docs/en/dev/infrastructure) |

## Remarks & Notes

- النسخة العربية لدليل حزمة django-fusion: [`/docs/ar/libs/django-fusion`](/docs/ar/libs/django-fusion).
- النسخة الإنجليزية الكاملة: [`/docs/en/libs`](/docs/en/libs).
