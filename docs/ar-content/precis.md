---
title: Precis — منتج نظام التعلم + التسويق الموحّد
description: فهرس التوثيق المعياري لمنتج Precis (precis-main) بما في ذلك غلاف التسويق/الكتالوج المدمج ومراجع Precis Landing القديمة.
navigation:
  title: Precis
  icon: i-lucide-graduation-cap
---

# 🎓 Precis — منتج نظام التعلم + التسويق الموحّد

> **المسار المعياري:** `projects/precis/precis-main/` · **اسم الموزّع:** `WEBSITE=precis-main` (الأسماء البديلة `precis-lms`, `precis-landing` تُوجّه هنا أيضاً)

Precis هي منصة التعلم الموحدة: **LMS** (دورات، تسجيل، تقدم، ملف شخصي) مدمج مع
**غلاف التسويق/الكتالوج** (صفحات Wagtail، أسعار، مدونة). دُمجت قاعدتا الكود في
بيئة تشغيل واحدة لخدمة الجمهورين بمكدس Django + Astro واحد.

## 📚 فهرس التوثيق

| المنطقة | الوثيقة | ملاحظات |
|---------|---------|---------|
| البنية | [`ARCHITECTURE.md`](/docs/en/precis/architecture) | تصميم LMS + التسويق المدمج في المستودع |
| CMS / البناء | [`cms-builder.md`](/docs/en/precis) | باني CMS قائم على الأصول (قيد التطوير) |
| الإعداد | [`configuration.md`](/docs/en/precis) | الإعدادات ومتغيرات البيئة وربط Dynaconf |
| الدورات | [`courses.md`](/docs/en/precis) | نموذج دورة LMS والتسجيل والتقدم |
| النشر | [`deployment.md`](/docs/en/precis) | مكدس Compose الموحّد وفحوصات الصحة ومسارات الإدارة |
| واجهة التسويق | [`precis-landing/frontend.md`](/docs/en/precis) | غلاف Astro وجسر الهيكل وHTMX |
| API خلفية التسويق | [`precis-landing/backend-api.md`](/docs/en/precis) | عقد render-first + واجهة البيانات |
| دليل الوكيل/الإدارة | [`../dev/infrastructure/precis-main-proxy-admin.md`](/docs/en/dev/infrastructure) | أهداف Traefik الحالية لـ structa.cloud وlms.structa.cloud |
| موقع أبحاث CTC | [`../precis-ctc/README.md`](/docs/en/precis-ctc) | موقع مركز الأبحاث المستقل في مجموعة Precis |

## 🧭 التسمية والأسماء البديلة

| الاسم | الحالة | يُوجَّه إلى |
|-------|--------|-------------|
| `precis-main` | ✅ معياري | `projects/precis/precis-main/` |
| `precis-lms` | ⚠️ اسم بديل قديم | `precis-main` (مدمج) |
| `precis-landing` / Precis Landing | ⚠️ اسم بديل قديم | `precis-main` (مدمج) |

## 🏗️ أين يُستخدم django-fusion

Precis هو المستهلك المرجعي للإطار المشترك: مكونات `{% comp %}` وتوجيه
`Viewset`/`ModelViewset` وكتل Wagtail StreamField والشظايا ونطاق HTMX كلها
من `libs/django-fusion/`. راجع [دليل الحزمة](/docs/ar/libs/django-fusion).

## 🚀 الأعمال والاستراتيجية

استراتيجية السوق ولوحة MVP وTAM/SAM/SOM والعملاء المثاليون وقائمة أبحاث Precis
في [قسم الشركة الناشئة](/docs/en/startup/precis) 🔒.

## Remarks & Notes

- دليل `precis-landing/` القديم في المستودع **نسخة محفوظة**؛ الموزّع يوجّه هويته
  إلى `precis-main`. فضّل مسارات `precis-main` في العمل الجديد.
- `precis-lms/` دُمج وأُزيل من الشجرة؛ تاريخ git هو الأرشيف.
- وثائق التسويق تصف عقد render-first/data-API — حافظ على المسارين (HTML الخادم
  + HTMX + JSON لـ Astro) عند تغيير أي منهما.
- النسخة الإنجليزية الكاملة: [`/docs/en/precis`](/docs/en/precis).
