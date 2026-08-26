---
title: CTC Research — التوثيق
description: فهرس التوثيق المعياري لموقع CTC Research (precis-ctc) — الأدلة والمحتوى والنشر والاستراتيجية والبنية والأوامر.
navigation:
  title: CTC Research
  icon: i-lucide-heart-pulse
---

# 🏥 وثائق CTC Research

> **مسار المنتج المعياري:** `projects/precis/precis-ctc/`
> **هوية التشغيل:** `precis-ctc`
> **الهوية العامة:** `ctc-research.com`
> **أسماء الموزّع:** `WEBSITE=ctc`, `WEBSITE=precis-ctc`, `WEBSITE=ctc-website`, `WEBSITE=ctc-research.com`

<!-- AI-generated: review needed -->

CTC Research هو موقع مركز الأبحاث الطبية والتعلم المستقل في مجموعة منتجات
Precis. له خلفية Django/Wagtail خاصة، وواجهة Astro، وخدمات Compose، وقاعدة
بيانات CTC، وتعيين وسائط مشترك، ومسارات وكيل. ليس نفس بيئة تشغيل منتج
`precis-main` الموحّد.

## الأدلة

- [فهرس وثائق المشروع](../../projects/precis/docs/precis-ctc/README.md)
- [خريطة المحتوى](../../projects/precis/docs/precis-ctc/CONTENTS.md)
- [سجل المكونات ومكونات الواجهة](../../projects/precis/docs/precis-ctc/COMPONENTS.md)
- [بنية القوالب](../../projects/precis/docs/precis-ctc/TEMPLATES.md)
- [الإعداد والبناء](../../projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md)
- [البيئة وإعادة النشر](../../projects/precis/docs/precis-ctc/ENVIRONMENT.md)
- [سجل التحسينات](../../projects/precis/docs/precis-ctc/ENHANCEMENTS.md)
- [حالات وتقنيات التعلم](../../projects/precis/docs/precis-ctc/LEARNING_CASES.md)
- [سجل التغييرات](../../projects/precis/precis-ctc/CHANGELOG.md)
- [خطة النشر](../plans/repository/ctc-research-publish-2026-08-18.md)

## المحتوى والنشر

- [استراتيجية المحتوى، ICP وأبحاث السوق](content-strategy.md)
- [سير النشر وملاحظات الإنتاج](publishing-and-production.md)
- [موقع عميل الإنتاج — دراسة حالة](client-production.md)

## استراتيجية الشركة الناشئة 🔒

- [استراتيجية سوق CTC Research](../startup/precis-ctc.md) — التموضع التجاري،
  ICP المشتري، TAM/SAM/SOM، العروض، وقائمة الأبحاث
- [استراتيجية المحفظة الكاملة](../startup/STRATEGY.md) — السيد الموحّد

## البنية في لمحة

```text
ctc-research.com
  ├─ Traefik: HTTPS/النطاق/توجيه المسار
  ├─ واجهة Astro: الصفحات العامة وغلاف التعلم
  ├─ خلفية Django/Wagtail: الصفحات وAPI والشظايا والمصادقة والتعلم
  ├─ عامل + مجدول Dramatiq: حدود التنفيذ غير المتزامن
  ├─ PostgreSQL: db_precis_ctc
  ├─ Redis: التخزين المؤقت ووسيط المهام
  └─ shared-proxy/Nginx:
       /media/ctc-research/
       /static/bundles/ctc-research/
       /sites/ctc-research/static/
```

## الأوامر الشائعة

```bash
cd projects/precis/precis-ctc
make check
make frontend-check
make redeploy

cd projects
make check WEBSITE=precis-ctc
make redeploy-with-stack WEBSITE=precis-ctc
```

## Remarks & Notes

- مسار نظام الملفات `projects/precis/precis-ctc/` معياري. لا تنشئ كوداً جديداً
  تحت مسارات تاريخية مثل `projects/precis-ctc/` أو `projects/precis/lms-ctc/`.
- المحتوى الطبي والقانوني وحقوق الصور والترجمة العامة يتطلب مراجعة مالك CTC
  قبل النشر الإنتاجي.
- النسخة الإنجليزية الكاملة: [`/docs/en/precis-ctc`](/docs/en/precis-ctc).
