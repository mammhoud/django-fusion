---
title: Precis
description: نظام التعلم المدمج (LMS) مع واجهة التسويق والكتالوج — دورات، كتالوج، تسجيل، تقدم، ملفات تعريف، محتوى.
navigation:
  title: Precis
  icon: i-lucide-graduation-cap
---

# 🎓 Precis — نظام تعلم موحد + تسويق

> **أسماء ذات صلة:** `precis-main`، `precis-landing`، `precis-lms`، `structa`، `lms`
> **الوسوم:** #site #lms #courses #enrollment #progress #profile #catalog #marketing

**المسار المعياري:** `projects/precis/precis-main/`  
**النطاقات:** structa.cloud · lms.structa.cloud  
**المكدس:** Astro 5 + Tailwind 4 + HTMX + Alpine.js؛ Django 5.2 + Wagtail 7.4 + django-fusion

---

## نظرة عامة

Precis (الموحد) يدمج نظام التعلم (LMS) مع واجهة التسويق/الكتالوج (Landing). منتج واحد يخدم الدورات، الكتالوج، التسجيل، التقدم، الملفات الشخصية، والمحتوى — كلها عبر Django/Wagtail + Astro مع django-fusion.

---

## البنية

- **الواجهة الخلفية:** `projects/precis/precis-main/backend/` — Django + Wagtail + django-fusion
- **الواجهة الأمامية:** `projects/precis/precis-main/frontend/` — Astro 5 + Tailwind 4
- **الأصول:** `projects/precis/precis-main/assets/` — SCSS، CSS المجمع، الصور/الوسائط
- **التكوين:** `projects/precis/precis-main/configs/` — متسلسل YAML (site، admin، defaults)

---

## الميزات الرئيسية

| المجال | الميزات |
|-------|---------|
| **الدورات** | CRUD الدورات، الوحدات، الدروس، التقييمات |
| **الكتالوج** | التصفح العام، البحث، التصفية، SEO |
| **التسجيل** | التسجيل الذاتي، موافقة المعلم، المجموعات |
| **التقدم** | تتبع الإكمال، الشهادات، التحليلات |
| **الملفات الشخصية** | لوحة المتعلم، الإنجازات، المحفظة |
| **المحتوى** | Wagtail StreamField، كتل django-fusion |

---

## البدء السريع

```bash
cd projects/precis/precis-main
make dev
```

---

## الأدلة ذات الصلة

- [البنية المعمارية](/docs/ar/precis/ARCHITECTURE)
- [التكوين](/docs/ar/precis/configuration)
- [الدورات](/docs/ar/precis/courses)
- [النشر](/docs/ar/precis/deployment)
- [Precis Landing](/docs/ar/precis/precis-landing)
- [CTC Research](/docs/ar/precis/client/ctc-research)

---

## ملاحظات وإرشادات

- `precis-main` هو المنتج الموحد (دمج LMS + Landing). الأسماء المستعيرة `precis-lms` و `precis-landing` تُحل إلى `WEBSITE=precis-main`.
- `precis-landing` محتفظ بها كنسخة قديمة؛ الهوية وقت التشغيل تربط إلى `precis-main`.
- الصيانة المشتركة لـ django-fusion عبر `libs/django-fusion/`.

<!-- AI-generated: review needed -->
