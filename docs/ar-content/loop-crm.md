---
title: Loop-CRM
description: فهرس توثيق Loop-CRM — منصة المبيعات والتسويق الموحدة على Django + django-fusion.
navigation:
  title: Loop-CRM
  icon: i-lucide-users
---

# Loop-CRM

> منصة موحدة للمبيعات والتسويق (حمض Twenty DNA + حمض Postiz DNA) على
> Django + django-fusion. موقع المنتج المعياري:
> `projects/loop-crm/`.

<!-- AI-generated: review needed -->

## وثائق المنتج (معيارية، داخل المستودع)

| الوثيقة | المسار | تغطي |
|---------|--------|------|
| **نظام التصميم** | [`projects/loop-crm/docs/DESIGN_SYSTEM.md`](/docs/en/loop-crm) | رموز تصميم صناعية-وحشية/قياس عن بعد، طباعة، تخطيط، مكونات. |
| **الإعداد والبناء** | [`projects/loop-crm/docs/SETUP_AND_BUILD.md`](/docs/en/loop-crm) | تشغيل خطوة بخطوة، إعداد الخلفية والواجهة، أوامر البناء والتشغيل. |

## البيئة والإعداد

| الوثيقة | المسار | تغطي |
|---------|--------|------|
| **عقد البيئة** | [`projects/loop-crm/configs/`](/docs/en/loop-crm) | كتالوج 56 متغيراً للبيئة + المحقّق (`make validate-env`). |
| **مثال البيئة** | [`projects/loop-crm/.env.example`](/docs/en/loop-crm) | قالب بيئة نسخ-لصق. |
| **هوية الموقع** | [`projects/loop-crm/Env/_site.yml`](/docs/en/loop-crm) | النطاق والمضيفات المسموحة والتجاوزات لكل بيئة. |

## الأوامر

```bash
# من projects/loop-crm
make dev               # خادم تطوير واجهة Astro
make backend-dev       # خادم Django (Makefile الخلفية)
make check             # فحص أنواع الواجهة
make backend-check     # فحوصات نظام Django
make backend-test      # اختبارات Django
make backend-migrate   # makemigrations + migrate
make backend-seed      # بذر مساحة عمل تجريبية (demo@loop.dev / demo-pass-123)
make validate-env      # فحص البيئة مقابل عقد configs
make i18n              # makemessages + compilemessages (en, ar)

# عبر Nx (يتطلب npm install في الجذر)
make nx-check          # npx nx run loop-crm:check
npx nx run loop-crm:backend-test
```

## ملاحظات البنية

- **Render-first:** Django يعرض شاشات البيانات (جداول/نماذج fusion)؛
  غلاف Astro يمرر `/fragments` و`/api` و`/bolt` و`/accounts`.
- **مسارات API:** `/bolt/tables/{resource}` (معياري، JWT، يتطلب django_bolt)
  و`/api/v1/tables/{resource}/` (توافق، كوكي جلسة).
- **عقد جدول fusion:** صفحات الموارد render-first ومسارا API يستخدمان
  `apps.core.resource_tables.resource_table` المدعوم بـ
  `django_fusion.fragments.tables.RowGenerator`.
- **ملكية المسارات:** `apps.core.fusion` يملك مسارات المتصفح ومداخل القائمة؛
  `apps.core.navigation` يملك شجرة التنقل JSON/HTMX المشتركة.
- **تطوير بلا Redis:** فحص RESP PING يقرر؛ DEBUG يتراجع إلى ذاكرة LocMem
  + طبقة قنوات في الذاكرة عند غياب Redis.
- **i18n:** `LocaleMiddleware` + `LANGUAGES` (en/ar) + `LOCALE_PATHS`؛ النماذج
  تستخدم `gettext_lazy`.

## Remarks & Notes

- على أجهزة التطوير حيث يملك تطبيق Kiro المنفذين 8000/6379، شغّل الخلفية على
  `PORT=8001` ويتولى فحص Redis الباقي.
- النسخة الإنجليزية الكاملة: [`/docs/en/loop-crm`](/docs/en/loop-crm).
