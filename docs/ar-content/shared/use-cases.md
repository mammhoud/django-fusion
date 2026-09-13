---
title: 🎯 Shared — حالات الاستخدام
description: كيف يُستخدم نواة Django المشتركة www/ عبر كل مواقع Structa Cloud وعمّال الخلفية.
navigation:
  title: حالات الاستخدام
  icon: i-lucide-lightbulb
---

# 🎯 Shared — حالات الاستخدام

> كيف تُستخدم نواة Django المشتركة `www/` عبر كل مواقع Structa Cloud وعمّال الخلفية.

---

## ما الذي يوفّره WWW

مجلد `www/` في `projects/www/` هو **نواة Django المشتركة** — كود يستخدمه كل موقع
في المستودع. وهو ليس موقعاً مستقلاً بل أساس قابل لإعادة الاستخدام.

| المكوّن | المسار | الغرض |
|-----------|------|---------|
| **الإعدادات** | `projects/www/settings.py` | تكوين موقع الحراسة لعمّال المهام المشتركة |
| **العامل** | `projects/www/worker/` | اكتشاف مهام Dramatiq + Celery |
| **وحدات المهام** | `projects/www/worker/modules.py` | وحدات مهام الخلفية المسجَّلة |
| **CI** | `projects/www/ci/` | تكوين CI مشترك |

---

## حالة الاستخدام 1: عامل خلفية مشترك

**المشكلة**: كل موقع Django يحتاج مهام خلفية (بريد، ذكاء اصطناعي، مزامنة). وتشغيل عمّال منفصلين لكل موقع مُهدِر.

**الحل**: مكدّس عامل مشترك واحد يخدم كل المواقع.

```
┌────────────────────────────────────────────────┐
│          shared-worker (Dramatiq)               │
│          shared-scheduler (Celery Beat)          │
│                                                  │
│  Routes tasks per site via queue routing:        │
│    precis-ctc queue  → precis-ctc DB         │
│    lms queue           → lms DB                  │
│    portfolio queue     → portfolio DB            │
│    cypercloud queue    → cypercloud DB           │
└────────────────────────────────────────────────┘
```

### كيف يعمل

```python
# projects/www/worker/modules.py
TASK_MODULES = [
    "ceptor_ai.tasks",                      # AI model tasks
    "ceptor_ai.workflows.tasks",            # Workflow automation
    "ceptor_ai.services.communication.tasks",  # Email/notifications
]
```

يكتشف العامل هذه الوحدات تلقائياً عند البدء. وتتضمّن كل مهمة توجيه طابور حتى
تصل إلى قاعدة بيانات الموقع الصحيح.

### النشر

```bash
make deploy-tasks           # Start shared-worker + shared-scheduler
make deploy-tasks TASKS_DB_NAME=db_lms  # Override default DB
```

---

## حالة الاستخدام 2: إعداد موقع Django جديد

**المشكلة**: إضافة موقع Django جديد تتطلّب إعدادات قوالبية وتكوين URL وتسجيل موقع.

**الحل**: انسخ من الأنماط المشتركة — `www/settings.py` هو مرجع الحراسة.

### خطوة بخطوة

```python
# projects/<new-site>/settings.py
# 1. Import shared settings
from configs.settings import *

# 2. Register the site
from configs.site import configure_site_environment
configure_site_environment("new-site", module="CMS", default_port=5080)

# 3. Add site-specific apps
LOCAL_APPS = ["new_site.pages", "new_site.plugins"]
INSTALLED_APPS += LOCAL_APPS
```

### ما الذي يوفّره WWW تلقائياً

| المكوّن | كيف |
|-----------|-----|
| `INSTALLED_APPS` | django-fusion، Wagtail، allauth، ceptor-ai |
| `MIDDLEWARE` | الأمان، الجلسات، CSRF، المصادقة، الرسائل |
| `TEMPLATES` | عناصر وسوم المكوّنات، مجلدات القوالب المشتركة |
| `DATABASES` | PostgreSQL (إنتاج) أو SQLite (تطوير) |
| `STATIC/MEDIA` | ملفات ثابتة مشتركة + خادم وسائط Nginx |

---

## حالة الاستخدام 3: معالجة مهام مستقلة عن الموقع

**المشكلة**: وحدة `ceptor_ai.tasks` ترسل بريداً — لكن وفق أي تكوين SMTP لأي موقع؟

**الحل**: يحلّ العامل المشترك تكوين كل موقع وقت تنفيذ المهمة.

```python
# www/worker/__init__.py
# At task dispatch:
#   1. Read queue name → determine site
#   2. Load site-specific settings (email backend, API keys)
#   3. Execute task with correct site context
```

هذا يتيح لعامل واحد معالجة:
- رسائل تأكيد التسجيل في LMS
- تدفّق استجابات الذكاء الاصطناعي في Cypercloud
- توليد PDF في Portfolio
- رسائل إشعار CTC Research

كل ذلك من `make deploy-tasks` واحد.

---

## حالة الاستخدام 4: الاختبار بمعزلٍ

**المشكلة**: اختبار وحدات `www.worker` يتطلّب بيئة Django دون موقع حقيقي.

**الحل**: يوفّر `www/settings.py` تكوين حراسة بسيطاً لاختبارات الوحدة.

```python
# tests/unit/test_worker.py
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "www.settings"

import django
django.setup()

from www.worker.modules import TASK_MODULES
assert "ceptor_ai.tasks" in TASK_MODULES
```

---

## حالة الاستخدام 5: خط أنابيب CI للكود المشترك

**المشكلة**: تغييرات `www/` تؤثر على كل المواقع — نحتاج بوابة CI سريعة.

**الحل**: يُحمَّل موقع الحراسة بلا أي تبعيات خاصة بموقع.

```bash
# Minimal CI check — no real DB, no Wagtail pages needed
python projects/www/__main__.py check  # Django system checks
python projects/www/__main__.py shell -c "from www.worker.modules import TASK_MODULES; print(TASK_MODULES)"
```

---

## متى لا تستخدم WWW

| لا تفعل | افعل بدلاً من ذلك |
|-------|-----------|
| إضافة صفحات/نماذج خاصة بموقع إلى `www/` | أضِفها إلى `projects/<site>/www/` |
| ترميز تكوين خاص بموقع في `www/settings.py` | استخدم إعدادات Dynaconf لكل موقع |
| تسجيل مهام خاصة بموقع في `www/worker/` | سجّلها في `tasks.py` الخاص بالموقع ووجّهها عبر الطابور |
| تركيب `www/` كموقع مستقل | فهو مكتبة، لا موقع قابل للنشر |

---

## ذات صلة

| الموضوع | المسار |
|-------|------|
| تكوين WWW | [`configuration.md`](./configuration.md) |
| دليل استنساخ موقع | [`clone-site`](/docs/ar/guides/clone-site) |
| بيئة الخلفية | [`back-env/`](/docs/en/dev/back-env/) |
| django-fusion | [`django-fusion`](/docs/ar/libs/django-fusion) |
| تكوينات POS | [`configuration`](/docs/en/pos/configuration) |

<!-- AI-generated: review needed -->
