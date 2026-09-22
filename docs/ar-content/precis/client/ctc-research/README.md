---
title: CTC Research
description: الموقع المؤسسي لمركز الأبحاث الطبية ونشر الأبحاث — الاستراتيجية التحريرية، سير النشر، حالة العميل.
navigation:
  title: CTC Research
  icon: i-lucide-flask-conical
---

# 🏥 CTC Research — مركز الأبحاث الطبية

> **أسماء ذات صلة:** `ctc`، `precis-ctc`، `ctc-research.com`
> **الوسوم:** #site #medical #research #publishing #editorial

**المسار المعياري:** `projects/precis/precis-ctc/`  
**النطاق:** ctc-research.com  
**المكدس:** Astro + Django + Wagtail + django-fusion

---

## نظرة عامة

CTC Research هو الموقع المؤسسي لمركز الأبحاث الطبية — منصة للنشر الأكاديمي، استراتيجية المحتوى التحريري، وعرض حالات العملاء. منتج مستقل منفصل عن وقت تشغيل Precis LMS.

---

## البنية

- **الواجهة الخلفية:** `projects/precis/precis-ctc/backend/` — Django + Wagtail + django-fusion
- **الواجهة الأمامية:** `projects/precis/precis-ctc/frontend/` — Astro
- **الأصول:** `projects/precis/precis-ctc/assets/` — SCSS، CSS، الصور
- **التكوين:** `projects/precis/precis-ctc/configs/` — متسلسل YAML

---

## الميزات الرئيسية

| المجال | الميزات |
|-------|---------|
| **الاستراتيجية التحريرية** | ICP، أبحاث السوق، مجموعات المواضيع، القياس |
| **سير النشر** | بوابات المراجعة، التوطين، التحقق من الإصدار، التراجع |
| **حالة العميل** | دراسات الحالة، الشهادات، معرض البحث |
| **نظام التصميم** | Industrial Brutalist / Swiss Print (fu-* tokens) |

---

## البدء السريع

```bash
cd projects/precis/precis-ctc
make dev
```

---

## الأدلة ذات الصلة

- [الاستراتيجية التحريرية](/docs/ar/precis/client/ctc-research/content-strategy)
- [سير النشر والإنتاج](/docs/ar/precis/client/ctc-research/publishing-and-production)
- [الإنتاج العميل](/docs/ar/precis/client/ctc-research/client-production)
- [Precis Main](/docs/ar/precis)

---

## ملاحظات وإرشادات

- CTC Research هو منتج مستقل — لا يشارك وقت تشغيل قاعدة البيانات مع Precis Main.
- يتم توجيه `WEBSITE=ctc` / `WEBSITE=precis-ctc` إلى `projects/precis/precis-ctc/`.
- نظام التصميم يتبع Industrial Brutalist / Swiss Print مع رموز fu-*.

<!-- AI-generated: review needed -->
