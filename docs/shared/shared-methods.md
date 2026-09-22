# 🔧 Shared Methods — Cross-Project Utilities

> Shared code, utilities, and methods available to ALL Structa Cloud projects from `projects/www/`.

---

## What "Shared" Means

The `projects/www/` directory provides code consumed by every Django site in the monorepo. It's not a standalone website — it's the **shared foundation** that all sites build on.

---

## Available Shared Components

### Background Workers

| Module | Path | Used By |
|--------|------|---------|
| Celery app | `www/worker/celery.py` | All sites (task queue bootstrap) |
| Celery beat | `www/worker/celery.py` | All sites (scheduled tasks) |
| Dramatiq actors | `www/worker/email.py` | All sites (email dispatch) |
| Dramatiq actors | `www/worker/content.py` | All sites (content management) |
| Task registry | `www/worker/modules.py` | All sites (task autodiscovery) |
| Task decorators | `www/worker/decorators.py` | All sites (shared task utils) |
| Runtime helpers | `www/worker/runtime.py` | All sites (`configure_django_for_website`) |

### CI Utilities

| Module | Path | Used By |
|--------|------|---------|
| Preflight utils | `www/ci/utils.py` | GitHub Actions deploy workflow |
| Health checks | `www/ci/utils.py` | Docker health check commands |

---

## How Sites Use Shared Methods

### 1. Task Discovery

```python
# Every site's worker picks up tasks from the shared registry
# projects/www/worker/modules.py
TASK_MODULES = [
    "ceptor_ai.tasks",                      # AI model tasks
    "ceptor_ai.workflows.tasks",            # Workflow automation
    "ceptor_ai.services.communication.tasks",  # Email/notifications
]
```

### 2. Email Dispatch (All Sites)

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

### 3. Content Management (All Sites)

```python
# projects/www/worker/content.py
@dramatiq.actor(queue_name="content")
def generate_ai_content(site_id, prompt_template, context):
    """Generate AI content with site-specific model config."""
    site = get_site(site_id)
    model = site.ai_config.get("default_model", "gemma3:4b")
    return ceptor_client.chat(prompt_template, context, model=model)
```

### 4. Runtime Bootstrap

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

## How to Add a New Shared Method

### Step 1: Create the module

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

### Step 2: Register in the task registry

```python
# projects/www/worker/modules.py
TASK_MODULES = [
    # ... existing modules ...
    "www.worker.my_new_tasks",  # ← Add here
]
```

### Step 3: Add queue to Docker Compose

```yaml
# application/compose/docker-compose.tasks.yml
services:
  shared-worker:
    environment:
      DRAMATIQ_QUEUES: "email,content,my_queue"  # ← Add queue name
```

### Step 4: Document the method here

Add an entry to the "Available Shared Components" table above.

---

## Per-Site Usage Matrix

| Shared Method | LMS | Portfolio | Cypercloud | CTC Research | POS Cloud |
|:---|---:|:---:|:---:|:---:|:---:|
| Email dispatch | ✅ | ✅ | ✅ | ✅ | ✅ |
| Content management | ✅ | ❌ | ✅ | ❌ | ❌ |
| AI model tasks | ❌ | ❌ | ✅ | ❌ | ❌ |
| PDF generation | ❌ | ✅ | ❌ | ❌ | ❌ |
| Cloud CRM sync | ❌ | ❌ | ❌ | ❌ | ✅ |
| CI preflight | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## Worker Deployment

Shared workers are deployed as part of the infrastructure stack:

```bash
# Deploy the shared task worker stack
make deploy-tasks

# Check worker status
make status-tasks

# View worker logs
make logs-tasks
```

The worker container bind-mounts `projects/www/` for hot-reload of task code without image rebuild.

---

## Related

| Topic | Path |
|------|------|
| Shared README | [`README.md`](README.md) |
| Shared configuration | [`configuration.md`](configuration.md) |
| Worker stack details | [`../../infrastructure/worker-stack.md`](../../infrastructure/worker-stack.md) |
| Per-project configs | [`../`](../) |
