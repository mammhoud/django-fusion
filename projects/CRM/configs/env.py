"""Loop-CRM environment variable catalog.

Single source of truth for the environment contract. Every variable the
project reads lives here with its default (matching ``configs.default``) and
a one-line purpose. ``.env.example`` is generated from this table, and
``validate_environment()`` checks a loaded env against it.

Runtime behavior: Django settings read ``os.environ`` directly;
``configs.site.configure_site_environment()`` seeds safe defaults with
``os.environ.setdefault``. Compose/.env overrides always win.
"""

from __future__ import annotations

from typing import Any

#: (name, default, purpose) — defaults mirror backend/configs/default and
#: backend/configs/site so the catalog never drifts from runtime behavior.
ENV_VARS: tuple[tuple[str, Any, str], ...] = (
    # ── Core Django ────────────────────────────────────────────────────────
    ("DJANGO_DEBUG", "1", "Django DEBUG flag (1/0). Enables Redis fallbacks to LocMem/in-memory."),
    ("DJANGO_SECRET_KEY", "loop-crm-dev-secret-key", "Django SECRET_KEY. Set a long random value outside dev."),
    ("DJANGO_ALLOWED_HOSTS", "*", "Comma-separated allowed hosts."),
    ("CSRF_TRUSTED_ORIGINS", "", "Comma-separated trusted origins for POST across hosts."),
    ("DJANGO_SECURE_SSL_REDIRECT", "0", "Redirect HTTP → HTTPS (1/0). Enable behind TLS."),
    ("SITE_ID", "1", "Django sites framework site id."),
    ("LANGUAGE_CODE", "en-us", "Default language code (see also locale catalogs)."),
    ("TIME_ZONE", "UTC", "Default timezone."),

    # ── Database ──────────────────────────────────────────────────────────
    ("USE_POSTGRES", "0", "1 switches local dev from SQLite to PostgreSQL."),
    ("POSTGRES_DB", "loop_crm", "PostgreSQL database name."),
    ("POSTGRES_USER", "loop_crm", "PostgreSQL role."),
    ("POSTGRES_PASSWORD", "", "PostgreSQL password."),
    ("POSTGRES_HOST", "127.0.0.1", "PostgreSQL host."),
    ("POSTGRES_PORT", "5432", "PostgreSQL port."),
    ("DB_ENGINE", "django.db.backends.sqlite3", "Alternative full DB engine path."),

    # ── Redis (cache + channels + Dramatiq) ───────────────────────────────
    ("REDIS_URL", "redis://127.0.0.1:6379/0", "Redis URL (cache). Set to disable dev fallbacks."),
    ("REDIS_HOST", "127.0.0.1", "Redis host when REDIS_URL is unset."),
    ("REDIS_PORT", "6379", "Redis port when REDIS_URL is unset."),
    ("REDIS_PASSWORD", "", "Redis password when REDIS_URL is unset."),
    ("REDIS_DB", "0", "Redis DB index offset for Loop-CRM's private block."),

    # ── Ports / dev servers ───────────────────────────────────────────────
    ("LOOP_BACKEND_PORT", "8000", "Django dev server port (backend Makefile DEFAULT_PORT)."),
    ("LOOP_FRONTEND_PORT", "4321", "Astro dev server port (frontend/.env PORT)."),

    # ── Fusion render mode ────────────────────────────────────────────────
    ("FUSION_RENDER_FIRST", "0", "1 = Django renders full HTML; 0 = Astro renders from APIs."),

    # ── Allauth / email ───────────────────────────────────────────────────
    ("ACCOUNT_EMAIL_VERIFICATION", "optional", "allauth email verification policy."),
    ("DEFAULT_FROM_EMAIL", "Loop CRM <noreply@structa.cloud>", "From address for outbound email."),
    ("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend", "Email backend (console in dev)."),
    ("EMAIL_REDIRECT_BASE", "", "Override the email OAuth redirect base host."),

    # ── Social login (GitHub + Google) ────────────────────────────────────
    ("GITHUB_CLIENT_ID", "", "GitHub OAuth client id (empty hides the button)."),
    ("GITHUB_CLIENT_SECRET", "", "GitHub OAuth client secret."),
    ("GOOGLE_CLIENT_ID", "", "Google OAuth client id (empty hides the button)."),
    ("GOOGLE_CLIENT_SECRET", "", "Google OAuth client secret."),

    # ── Social publishing (LinkedIn + X) ──────────────────────────────────
    ("LINKEDIN_CLIENT_ID", "", "LinkedIn connector client id."),
    ("LINKEDIN_CLIENT_SECRET", "", "LinkedIn connector client secret."),
    ("X_CLIENT_ID", "", "X (Twitter) connector client id."),
    ("X_CLIENT_SECRET", "", "X (Twitter) connector client secret."),
    ("SOCIAL_REDIRECT_BASE", "", "Override the social OAuth callback host."),

    # ── Email sync (Gmail + Outlook) ──────────────────────────────────────
    ("GMAIL_CLIENT_ID", "", "Gmail connector client id."),
    ("GMAIL_CLIENT_SECRET", "", "Gmail connector client secret."),
    ("OUTLOOK_CLIENT_ID", "", "Outlook connector client id."),
    ("OUTLOOK_CLIENT_SECRET", "", "Outlook connector client secret."),

    # ── Stripe SaaS billing ───────────────────────────────────────────────
    ("STRIPE_SECRET_KEY", "", "Stripe secret key (empty disables checkout/portal/webhook)."),
    ("STRIPE_PUBLISHABLE_KEY", "", "Stripe publishable key (public, for the checkout client)."),
    ("STRIPE_WEBHOOK_SECRET", "", "Stripe webhook signing secret (verifies inbound events)."),

    # ── Demo state ────────────────────────────────────────────────────────
    ("DEMO_MODE", "0", "1 exposes the seeded demo account on the login page. Never in production."),

    # ── django-bolt API (optional) ────────────────────────────────────────
    ("FUSION_BOLT_ENABLED", "1", "Enable the canonical /bolt API road."),
    ("FUSION_BOLT_JWT_SECRET", "loop-crm-dev-secret-key", "JWT signing secret for the bolt road."),
    ("FUSION_BOLT_JWT_ALGORITHM", "HS256", "JWT algorithm."),
    ("FUSION_BOLT_TOKEN_TTL", "3600", "Access token TTL (seconds)."),
    ("FUSION_BOLT_REFRESH_TTL", "2592000", "Refresh token TTL (seconds)."),
    ("FUSION_BOLT_API_KEY", "", "Optional second machine credential (X-API-Key)."),
    ("FUSION_BOLT_API_KEY_HEADER", "X-API-Key", "Header name for the machine credential."),
    ("FUSION_BOLT_JWT_ISSUER", "loop-crm", "JWT issuer claim."),
    ("FUSION_BOLT_JWT_AUDIENCE", "", "JWT audience claim."),

    # ── Frontend (Astro; read by astro.config.mjs + the Redux store) ──────
    ("PORT", "4321", "Astro dev server port (frontend/.env)."),
    ("BACKEND_URL", "http://127.0.0.1:8000", "Django backend origin the Astro proxy forwards to."),
    ("PUBLIC_SITE_URL", "https://crm.structa.cloud", "Canonical public site URL (SEO/sitemap)."),
    ("PUBLIC_BACKEND_URL", "http://127.0.0.1:8000", "Browser-visible backend base for the data-API road."),
    ("PUBLIC_API_PREFIX", "/bolt", "Canonical API prefix (frontend store)."),
    ("PUBLIC_API_FALLBACK_PREFIX", "/api/v1", "Fallback API prefix when bolt is unavailable. /api/v1 is deprecated; prefer /apis/core/."),
)

#: Variables that must be set (or have a non-empty value) outside local dev.
REQUIRED_ENV_VARS: tuple[str, ...] = (
    "DJANGO_SECRET_KEY",
    "DJANGO_ALLOWED_HOSTS",
    "FUSION_BOLT_JWT_SECRET",
)

#: Frontend-only variables (belong in frontend/.env, not the backend .env).
FRONTEND_ENV_VARS: tuple[str, ...] = (
    "PORT",
    "BACKEND_URL",
    "PUBLIC_SITE_URL",
    "PUBLIC_BACKEND_URL",
    "PUBLIC_API_PREFIX",
    "PUBLIC_API_FALLBACK_PREFIX",
)

_VAR_MAP = {name: (default, purpose) for name, default, purpose in ENV_VARS}


def env_defaults() -> dict[str, str]:
    """Return every backend variable with its default as strings (for seeding
    ``os.environ`` or generating ``.env.example``)."""
    return {name: "" if default is None else str(default) for name, default, _ in ENV_VARS}


def describe(name: str) -> tuple[str, str] | None:
    """Return (default, purpose) for a variable, or None if unknown."""
    return _VAR_MAP.get(name)
