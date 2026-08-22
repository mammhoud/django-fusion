---
title: Shared — النواة المشتركة والعمال
description: توثيق المجلد المشترك — تطبيق Django الأساسي المشترك وعمال المهام.
navigation:
  title: Shared
  icon: i-lucide-layers
---

# Shared — النواة المشتركة والعمال

> **أسماء مرتبطة:** `shared`, `shared-worker`, `shared-scheduler`, `tasks`, `sentinel site`, `background tasks`, `Dramatiq`, `Celery`
> **الوسوم:** #project #shared #shared-core #worker #celery #dramatiq #tasks

**المسار المعياري:** `projects/www/` \
**اسم موقع Django:** `shared` ← يحل إلى `path: www` في `sites.yml` \
**المنفذ:** 5080

---

## نظرة عامة

مجلد `www/` (المدمج من `projects/shared/` و`projects/www/` السابقين) هو **كود
تطبيق Django الأساسي المشترك** المستخدم من كل مواقع Structa Cloud. يؤدي دورين:

1. **موقع sentinel** لمكدس عمال المهام المشترك (`shared-worker` + `shared-scheduler`)
2. **مكتبة مشتركة** لوحدات المهام وأدوات CI ومساعدات التشغيل التي تستهلكها كل مواقع المستأجرين

على عكس مشاريع Django الخاصة بكل موقع (precis-ctc, lms, VResume)، لا يملك
`www/` تجاوزات خاصة بالمستأجر — إنه إعداد مستقل عن الموقع يمكنه توجيه المهام
إلى قائمة **أي** موقع.

---

## الدليل

### نقطة دخول CLI

```bash
# من projects/
python www/__main__.py check        # فحص نظام Django
python www/__main__.py migrate      # تطبيق الترحيلات
python www/__main__.py shell        # قشرة Django
```

### التطوير

```bash
cd projects
make docker-up WEBSITE=www          # تشغيل كحاوية Docker
make check WEBSITE=www               # فحوصات Django
```

### نشر عامل المهام

```bash
make deploy-tasks                    # نشر shared-worker + shared-scheduler
make status-tasks                    # عرض حالة العامل
make logs-tasks                      # عرض سجلات العامل
```

---

## خريطة الكود

| المسار | الغرض | التخصيص |
|--------|-------|:---:|
| `projects/www/__init__.py` | علامة الحزمة + وثائق sentinel | 🔴 غير قابل للتخصيص |
| `projects/www/settings.py` | إعدادات Django لموقع `www` | ⚪ إعداد فقط |
| `projects/www/worker/__init__.py` | تصدير: `configure_django_for_website`, `TASK_MODULES` | 🔴 غير قابل للتخصيص |
| `projects/www/worker/apps.py` | Django AppConfig — يسجل actors Dramatiq عند `ready()` | 🔴 غير قابل للتخصيص |
| `projects/www/worker/celery.py` | تشغيل تطبيق Celery + جدولة beat | 🔴 غير قابل للتخصيص |
| `projects/www/worker/tasks.py` | تعريفات مهام Celery (نبض القلب) | 🟢 قابل للتخصيص |
| `projects/www/worker/email.py` | actors بريد Dramatiq (بقوالب + خام) | 🟢 قابل للتخصيص |
| `projects/www/worker/content.py` | actors إدارة المحتوى Dramatiq | 🟢 قابل للتخصيص |
| `projects/www/worker/decorators.py` | مزخرفات المهام المشتركة | 🔴 غير قابل للتخصيص |
| `projects/www/worker/runtime.py` | مساعدات التشغيل (`configure_django_for_website`) | 🔴 غير قابل للتخصيص |
| `projects/www/worker/modules.py` | سجل وحدات المهام (قائمة الاكتشاف التلقائي) | 🟢 قابل للتخصيص |
| `projects/www/ci/utils.py` | أدوات قبل نشر CI/CD | 🟡 تفويض |

---

## Remarks

| # | ملاحظة |
|---|--------|
| ⚠️ | موقع sentinel مسجل في `sites.yml` بأسماء بديلة: `shared`, `shared-worker`, `shared-scheduler`, `tasks`, `www`. أي منها يُستخدم كقيمة `WEBSITE=`. |
| ⚠️ | يجب ألا يضيف `www/settings.py` `_SITE_APP_DIR` — القيام بذلك سيحجب استيرادات `www.core` و`www.worker`. |
| 💡 | مجلد `www/` مُركَّب bind في حاويتي `shared-worker` و`shared-scheduler`، مما يتيح إعادة تحميل ساخن لكود المهام دون إعادة بناء صورة. |
| 🔌 | لإضافة وحدة مهام جديدة: أنشئ ملف `.py` ← سجّله في `modules.py` ← أضف اسم القائمة إلى `docker-compose.tasks.yml`. |

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/shared`](/docs/en/shared).
- راجع بنية العمال: [`/docs/en/dev/infrastructure/worker-stack`](/docs/en/dev/infrastructure/worker-stack).
