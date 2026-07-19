# ⚙️ Shared Worker Stack

> Deployment, configuration, and architecture of the shared background task workers (Celery + Dramatiq) that serve all Structa Cloud sites.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Network                          │
│                                                          │
│  ┌─────────────────────┐  ┌───────────────────────────┐ │
│  │  shared-worker       │  │  shared-scheduler          │ │
│  │  (Dramatiq)          │  │  (Celery Beat)             │ │
│  │                      │  │                            │ │
│  │  Queues:             │  │  Scheduled tasks:          │ │
│  │   • email            │  │   • hourly heartbeat       │ │
│  │   • content          │  │   • daily cleanup          │ │
│  │   • ai               │  │   • weekly reports         │ │
│  │                      │  │                            │ │
│  │  Bind-mount:         │  │  Bind-mount:               │ │
│  │   projects/www/ →    │  │   projects/www/ →          │ │
│  │   /app/www/          │  │   /app/www/                │ │
│  └─────────┬────────────┘  └───────────┬───────────────┘ │
│            │                            │                  │
│            └──────────┬─────────────────┘                  │
│                       │                                    │
│              ┌────────▼────────┐                          │
│              │    PostgreSQL    │                          │
│              │    :5432         │                          │
│              │                  │                          │
│              │  db_ctc         │                          │
│              │  db_lms         │                          │
│              │  db_vresume     │                          │
│              │  db_cypercloud  │                          │
│              └─────────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

---

## Deployment

### Quick Start

```bash
# Deploy the full task worker stack
make deploy-tasks

# Override default database
make deploy-tasks TASKS_DB_NAME=db_lms

# Check status
make status-tasks

# View logs
make logs-tasks
```

### Docker Compose

```yaml
# applications/compose/docker-compose.tasks.yml
services:
  shared-worker:
    image: structa-cloud-worker:latest
    container_name: shared-worker
    restart: unless-stopped
    environment:
      DB_NAME: "${TASKS_DB_NAME:-db_ctc}"
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: "${POSTGRES_USER:-postgres}"
      DB_PASSWORD: "${POSTGRES_PASSWORD:-postgres}"
      DRAMATIQ_PROCESSES: 4
      DRAMATIQ_QUEUES: "email,content,ai"
    volumes:
      - ../../projects/www:/app/www:ro        # Task code (hot-reload)
      - ../../projects/configs:/app/configs:ro # Shared configs
    networks:
      - structa-network
    depends_on:
      postgres:
        condition: service_healthy

  shared-scheduler:
    image: structa-cloud-worker:latest
    container_name: shared-scheduler
    restart: unless-stopped
    command: celery -A www.worker.celery beat
    environment:
      DB_NAME: "${TASKS_DB_NAME:-db_ctc}"
      DB_HOST: postgres
      CELERY_BEAT_SCHEDULE: |
        {
          "heartbeat": {"task": "www.worker.tasks.heartbeat", "schedule": 3600},
          "cleanup": {"task": "www.worker.tasks.cleanup", "schedule": 86400}
        }
    volumes:
      - ../../projects/www:/app/www:ro
      - ../../projects/configs:/app/configs:ro
    networks:
      - structa-network
```

---

## Task Routing

The shared worker routes tasks to the correct site's database using queue-based routing.

### Queue → Site Mapping

| Queue | Site | Database |
|-------|------|----------|
| `ctc-research` | CTC Research | `db_ctc` |
| `lms` | Structa LMS | `db_lms` |
| `portfolio` | VResume | `db_vresume` |
| `cypercloud` | Cypercloud | `db_cypercloud` |
| `email` | All (site-agnostic) | Per-task `site_id` |
| `content` | All (site-agnostic) | Per-task `site_id` |
| `ai` | Cypercloud only | `db_cypercloud` |

### How Routing Works

```python
# projects/www/worker/runtime.py
def configure_django_for_website(site_name: str):
    """
    Swap Django settings at runtime so a single worker process
    can handle tasks from multiple sites.

    Called at the start of every site-specific task.
    """
    import os
    os.environ["DJANGO_SITE"] = site_name
    # Reload settings with the target site's database and config
    django.setup()

# Usage in a task:
@dramatiq.actor(queue_name="email")
def send_enrollment_email(site_id: int, student_id: int, course_id: int):
    configure_django_for_website(f"site_{site_id}")
    student = Student.objects.get(id=student_id)
    course = Course.objects.get(id=course_id)
    send_mail(...)
```

---

## Task Modules

### Registered Modules

```python
# projects/www/worker/modules.py
TASK_MODULES = [
    "ceptor_ai.tasks",                      # AI model inference
    "ceptor_ai.workflows.tasks",            # Workflow automation
    "ceptor_ai.services.communication.tasks",  # Email + notifications
]
```

### Available Task Types

| Module | Task | Queue | Description |
|--------|------|-------|-------------|
| `email.py` | `send_templated_email` | `email` | Templated email with site-specific SMTP |
| `email.py` | `send_raw_email` | `email` | Raw email without template |
| `content.py` | `generate_ai_content` | `content` | AI content generation with site model |
| `content.py` | `sync_content` | `content` | Cross-site content sync |
| `tasks.py` | `heartbeat` | `celery` | Hourly worker health check |
| `tasks.py` | `cleanup` | `celery` | Daily stale data cleanup |

---

## Adding a New Task

### 1. Create the task module

```python
# projects/www/worker/notifications.py
import dramatiq
from www.worker.runtime import configure_django_for_website

@dramatiq.actor(queue_name="notifications")
def send_push_notification(site_id: int, user_id: int, message: str):
    configure_django_for_website(f"site_{site_id}")
    from accounts.models import User
    user = User.objects.get(id=user_id)
    push_service.send(user.device_token, message)
```

### 2. Register the module

```python
# projects/www/worker/modules.py — add to TASK_MODULES
TASK_MODULES = [
    # ... existing ...
    "www.worker.notifications",  # ← NEW
]
```

### 3. Add the queue

```yaml
# applications/compose/docker-compose.tasks.yml — add to DRAMATIQ_QUEUES
DRAMATIQ_QUEUES: "email,content,ai,notifications"  # ← NEW
```

### 4. Deploy

```bash
make deploy-tasks     # Rebuild + restart worker stack
```

---

## Scheduler (Celery Beat)

### Heartbeat Task

```python
# projects/www/worker/tasks.py
from celery import shared_task

@shared_task
def heartbeat():
    """Hourly health check — verifies worker can reach DB."""
    from django.db import connection
    connection.ensure_connection()
    return {"status": "ok", "timestamp": timezone.now().isoformat()}
```

### Schedule Configuration

| Task | Schedule | Purpose |
|------|----------|---------|
| `heartbeat` | Every 60 minutes | Worker health verification |
| `cleanup` | Every 24 hours | Remove expired sessions, stale locks |
| `sync_metrics` | Every 6 hours | Sync usage metrics to analytics |

---

## Monitoring

### Health Check

```bash
# Via Makefile
make status-tasks

# Manual Docker health check
docker inspect shared-worker --format='{{.State.Health.Status}}'

# Check queue lengths
docker exec shared-worker dramatiq --broker redis://redis:6379 queues
```

### Logs

```bash
# Real-time logs
make logs-tasks

# Filter by queue
docker logs shared-worker 2>&1 | grep "email"

# Last 100 lines
docker logs --tail 100 shared-worker
```

---

## Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| Tasks stuck in queue | Redis connection | `docker exec shared-worker redis-cli -h redis PING` |
| DB connection errors | Postgres health | `docker exec postgres pg_isready` |
| Task code not updating | Bind mount | Restart container: `make deploy-tasks` |
| Wrong site DB used | `DJANGO_SITE` env | Check `configure_django_for_website()` call |
| Celery beat not firing | Scheduler logs | `docker logs shared-scheduler --tail 50` |

---

## Related

| Topic | Path |
|------|------|
| Shared methods | [`../projects/shared/shared-methods.md`](../projects/shared/shared-methods.md) |
| Shared configuration | [`../projects/shared/configuration.md`](../projects/shared/configuration.md) |
| Infrastructure overview | [`README.md`](README.md) |
| Deployment guide | [`deployment.md`](deployment.md) |
| Backend environment | [`../back-env/settings-reference.md`](../back-env/settings-reference.md) |
