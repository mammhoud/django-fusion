---
title: Shared — مرجع التكوين
description: الموقع المشترك (www) — المنفذ، الأسماء المستعارة، تسجيل الموقع، الملفات الأساسية، ومتغيرات البيئة.
navigation:
  title: التكوين
  icon: i-lucide-settings
---

# Shared — مرجع التكوين

> **المنفذ:** 5080 | **الأسماء المستعارة:** shared، shared-worker، shared-scheduler، tasks

## تسجيل الموقع

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  www:
    port: 5080
    path: www
    aliases: [shared, shared-worker, shared-scheduler, tasks]
```

## الملفات الأساسية

| الملف | الغرض |
|------|---------|
| `www/settings.py` | إعدادات Django لموقع الحراسة (sentinel) |
| `www/worker/celery.py` | تهيئة تطبيق Celery + مجدول beat |
| `www/worker/tasks.py` | تعريفات مهام Celery (نبضة القلب) |
| `www/worker/email.py` | عوامل Dramatiq للبريد |
| `www/worker/content.py` | إدارة محتوى Dramatiq |
| `www/worker/modules.py` | سجل وحدات المهام |
| `www/worker/runtime.py` | `configure_django_for_website()` |
| `www/ci/utils.py` | أدوات الفحص المسبق لـ CI/CD |

## متغيرات البيئة

| المتغير | مطلوب | الغرض |
|----------|:--------:|---------|
| `DB_NAME` | — | قاعدة بيانات موقع الحراسة (افتراضي: db_ctc) |
| `DRAMATIQ_PROCESSES` | — | عمليات عامل Dramatiq |
| `DRAMATIQ_QUEUES` | — | أسماء الطوابير (مفصولة بفواصل) |

## ذات صلة

| المورد | المسار |
|----------|------|
| README المشترك | [`README.md`](./README.md) |
| الطرق المشتركة | [`shared-methods.md`](./shared-methods.md) |
| LMS shared-www | [`../lms/shared-integration.md`](../lms/shared-integration.md) |
| البنية التحتية | [`worker-stack.md`](/docs/en/dev/infrastructure/worker-stack) |

<!-- AI-generated: review needed -->
