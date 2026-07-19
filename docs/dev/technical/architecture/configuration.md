# Configuration System

VResume uses a sophisticated, multi-layered configuration system built on **Pydantic Settings** and **Dynaconf**. This allows for type-safe settings, environment-specific overrides, and automatic runtime detection.

## 🏗️ How it Works

The configuration is managed by the `MainSettings` class in `v1/configs/settings/conf.py`. It aggregates settings from several sources in a specific order of precedence.

### Layered Configuration (Precedence)

1.  **Environment Variables**: OS-level environment variables (e.g., `DJANGO_DEBUG=True`).
2.  **.env File**: Located at `v1/.env`.
3.  **Secrets**: `v1/configs/settings/ENV/.secrets.yml` (Git-ignored).
4.  **Environment Overrides**: `v1/configs/settings/ENV/_production.yml` or `_development.yml` based on `SERVER_ENV`.
5.  **Module Specific**: `database.yml`, `security.yml`, `email.yml`, etc.
6.  **Core Defaults**: `_core.yml` and class defaults in `conf.py`.

## 📂 Configuration Files

All YAML configuration files are located in `v1/configs/settings/ENV/`.

| File | Purpose |
| :--- | :--- |
| `_core.yml` | General Django and Wagtail settings (Site name, timezone, etc.) |
| `database.yml` | DB connection strings and engine selection |
| `security.yml` | CSRF, CORS, and security headers |
| `email.yml` | SMTP and transactional email settings |
| `storage.yml` | Media and static file storage (Local vs S3) |
| `celery.yml` / `rq.yml` | Task queue and Redis configurations |
| `.secrets.yml` | **Sensitive** credentials (API keys, DB passwords) |

## 🚀 Runtime Detection

VResume automatically detects where it's running:
-   **Local**: Standard physical machine/VM.
-   **Docker**: Detected via `/.dockerenv` or environment flags.
-   **Kubernetes**: Detected via service host environment variables.

This detection affects default behaviors like `HOST`, `PORT`, and service discovery (e.g., connecting to `db` host instead of `localhost`).

## 🛠️ Developer Usage

### Accessing Settings in Code

Always import the singleton `settings` instance:

```python
from configs.settings import settings

# Access core fields (type-safe)
debug_mode = settings.DEBUG

# Access dynamic YAML settings
site_title = settings.WAGTAIL_SITE_NAME

# Using the .get() helper (with defaults)
api_key = settings.get("CUSTOM_API_KEY", default="fallback")
```

### Adding New Settings

1.  **If it's a core setting**: Add a `Field` to the `MainSettings` class in `conf.py`.
2.  **If it's a module setting**: Add the key-value pair to the appropriate `.yml` file in `v1/configs/settings/ENV/`.
3.  **If it's sensitive**: Add it to `.secrets.yml` or the `.env` file.

## 📊 Summary Command

You can view the current active configuration and environment status by running:

```bash
make check-env
```
(Note: This command prints a formatted summary of the active environment and any configuration warnings.)
