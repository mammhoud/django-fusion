---
title: 🔧 الطرق المشتركة — أدوات عبر المشاريع
description: الكود والأدوات والطرق المشتركة المتاحة لكل مشاريع Structa Cloud من projects/www/.
navigation:
  title: الطرق المشتركة
  icon: i-lucide-puzzle
---

# 🔧 الطرق المشتركة — أدوات عبر المشاريع

> كود وأدوات وطرق مشتركة متاحة لكل مشاريع Structa Cloud من `projects/www/`.

---

## ما معنى «مشترك»

مجلد `projects/www/` يوفّر كوداً يستهلكه كل موقع Django في المستودع. وهو ليس
موقعاً مستقلاً — بل **الأساس المشترك** الذي تبني عليه كل المواقع.

---

## المكوّنات المشتركة المتاحة

### عمّال الخلفية

| الوحدة | المسار | المستخدِم |
|--------|------|---------|
| تطبيق Celery | `www/worker/celery.py` | كل المواقع (تهيئة طابور المهام) |
| Celery beat | `www/worker/celery.py` | كل المواقع (المهام المجدولة) |
| عوامل Dramatiq | `www/worker/email.py` | كل المواقع (إرسال البريد) |
| عوامل Dramatiq | `www/worker/content.py` | كل المواقع (إدارة المحتوى) |
| سجل المهام | `www/worker/modules.py` | كل المواقع (الاكتشاف التلقائي للمهام) |
| زخارف المهام | `www/worker/decorators.py` | كل المواقع (أدوات مهام مشتركة) |
| أدوات وقت التشغيل | `www/worker/runtime.py` | كل المواقع (`configure_django_for_website`) |

### أدوات CI

| الوحدة | المسار | المستخدِم |
|--------|------|---------|
| أدوات الفحص المسبق | `www/ci/utils.py` | سير عمل نشر GitHub Actions |
| فحوصات الصحة | `www/ci/utils.py` | أوامر فحص صحة Docker |

---

## كيف تستخدم المواقع الطرق المشتركة

### 1. اكتشاف المهام

```python
# Every site's worker picks up tasks from the shared registry
# projects/www/worker/modules.py
TASK_MODULES = [
    "ceptor_ai.tasks",                      # AI model tasks
    "ceptor_ai.workflows.tasks",            # Workflow automation
    "ceptor_ai.services.communication.tasks",  # Email/notifications
]
```

### 2. إرسال البريد (كل المواقع)

```python
# projects/www/worker/email.py
# All sites use this for:
# - LMS enrollment confirmation emails
# - Cypercloud AI response notifications
# - Portfolio PDF generation completion
# - Password reset emails (allauth)
# - Order confirmation emails (POS Cloud CRM)

import dramatiq

@dramatiq.actor(queue_name="email")
def send_templated_email(site_id, template_name, context, recipients):
    """Send templated email with site-specific settings."""
    site = get_site(site_id)
    with site.settings_context():
        send_mail(
            subject=render_template(template_name, context),
            body=render_template(f"{template_name}.txt", context),
            from_email=site.email_from,
            recipient_list=recipients,
        )
```

### 3. إدارة المحتوى (كل المواقع)

```python
# projects/www/worker/content.py
@dramatiq.actor(queue_name="content")
def generate_ai_content(site_id, prompt_template, context):
    """Generate AI content with site-specific model config."""
    site = get_site(site_id)
    model = site.ai_config.get("default_model", "gemma3:4b")
    return ceptor_client.chat(prompt_template, context, model=model)
```

### 4. تهيئة وقت التشغيل

```python
# projects/www/worker/runtime.py
def configure_django_for_website(site_name: str):
    """Configure Django settings for a specific site at runtime.
    
    This lets a single worker process handle tasks for
    multiple sites by swapping settings context per task.
    """
    os.environ["DJANGO_SITE"] = site_name
    # Reload settings with site-specific overrides
    ...
```

---

## كيف تضيف طريقة مشتركة جديدة

### الخطوة 1: أنشئ الوحدة

```python
# projects/www/worker/my_new_tasks.py
import dramatiq

@dramatiq.actor(queue_name="my_queue")
def my_shared_task(site_id, *args, **kwargs):
    """Task available to ALL sites."""
    site = get_site(site_id)
    with site.settings_context():
        # Task logic here
        pass
```

### الخطوة 2: سجّلها في سجل المهام

```python
# projects/www/worker/modules.py
TASK_MODULES = [
    # ... existing modules ...
    "www.worker.my_new_tasks",  # ← Add here
]
```

### الخطوة 3: أضِف الطابور إلى Docker Compose

```yaml
# application/compose/docker-compose.tasks.yml
services:
  shared-worker:
    environment:
      DRAMATIQ_QUEUES: "email,content,my_queue"  # ← Add queue name
```

### الخطوة 4: وثّق الطريقة هنا

أضِف مدخلاً إلى جدول «المكوّنات المشتركة المتاحة» أعلاه.

---

## مصفوفة الاستخدام لكل موقع

| الطريقة المشتركة | LMS | Portfolio | Cypercloud | CTC Research | POS Cloud |
|:---|---:|:---:|:---:|:---:|:---:|
| إرسال البريد | ✅ | ✅ | ✅ | ✅ | ✅ |
| إدارة المحتوى | ✅ | ❌ | ✅ | ❌ | ❌ |
| مهام نماذج الذكاء الاصطناعي | ❌ | ❌ | ✅ | ❌ | ❌ |
| توليد PDF | ❌ | ✅ | ❌ | ❌ | ❌ |
| مزامنة Cloud CRM | ❌ | ❌ | ❌ | ❌ | ✅ |
| الفحص المسبق لـ CI | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## نشر العامل

يُنشر العاملون المشتركون كجزء من مكدّس البنية التحتية:

```bash
# Deploy the shared task worker stack
make deploy-tasks

# Check worker status
make status-tasks

# View worker logs
make logs-tasks
```

حاوية العامل تُركّب `projects/www/` ربطاً لإعادة تحميل كود المهام دون إعادة بناء الصورة.

---

## ذات صلة

| الموضوع | المسار |
|------|------|
| README المشترك | [`README.md`](./README.md) |
| تكوين Shared | [`configuration.md`](./configuration.md) |
| تفاصيل مكدّس العمل | [`worker-stack.md`](/docs/en/dev/infrastructure/worker-stack) |
| تكوينات لكل مشروع | [`/docs/en/`](/docs/en/) |

<!-- AI-generated: review needed -->
