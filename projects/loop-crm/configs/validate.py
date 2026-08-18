"""Environment validation for Loop-CRM.

Checks a loaded environment mapping against the catalog in ``env.py`` and
reports missing/invalid values. Used by the ``make validate-env`` target and
CI; never requires Django to be installed.
"""

from __future__ import annotations

import os
from typing import Iterable

from .env import ENV_VARS, REQUIRED_ENV_VARS, describe, env_defaults

KNOWN = {name for name, _, _ in ENV_VARS}


def validate_environment(
    env: dict[str, str] | None = None,
    *,
    required: Iterable[str] = REQUIRED_ENV_VARS,
    production: bool = False,
) -> list[str]:
    """Validate an environment mapping (defaults to ``os.environ``).

    Returns a list of human-readable problems (empty when valid). When
    ``production`` is true, ``DJANGO_DEBUG`` must be ``0`` and required vars
    must not hold placeholder values.
    """
    env = dict(os.environ if env is None else env)
    problems: list[str] = []

    for name in required:
        value = env.get(name, "")
        if not value or value == "change-me":
            problems.append(f"{name} is missing or unset (required).")

    if production:
        if env.get("DJANGO_DEBUG", "1") != "0":
            problems.append("DJANGO_DEBUG must be 0 in production.")
        for name in ("DJANGO_SECRET_KEY", "FUSION_BOLT_JWT_SECRET"):
            if env.get(name, "") in ("loop-crm-dev-secret-key", "change-me-to-a-long-random-secret"):
                problems.append(f"{name} still uses a dev placeholder.")

    # Unknown project-prefixed variables are worth surfacing as warnings;
    # the rest of the shell environment (PATH, CONDA_*, rvm_*, ...) is noise.
    _project_prefixes = (
        "DJANGO_", "POSTGRES_", "REDIS_", "LOOP_", "FUSION_", "ACCOUNT_",
        "DEFAULT_FROM_", "EMAIL_", "GITHUB_", "GOOGLE_", "LINKEDIN_",
        "X_", "SOCIAL_", "GMAIL_", "OUTLOOK_", "DEMO_", "PUBLIC_",
        "BACKEND_URL", "CSRF_", "SECURE_", "SITE_ID", "LANGUAGE_",
        "TIME_ZONE", "USE_POSTGRES", "DB_ENGINE", "PORT", "ALLOWED_HOSTS",
    )
    # Shared workspace vars set by the repo shell/compose (legitimate for
    # every product, not specific to Loop-CRM).
    _shared = {
        "ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS", "CORS_ALLOWED_ORIGINS",
        "EMAIL_HOST", "EMAIL_PORT", "EMAIL_USE_TLS", "SMTP_SERVER",
        "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_RECIPIENT", "DEBUG",
        "ENVIRONMENT", "LOG_LEVEL", "LOG_FORMAT", "MEDIA_ROOT",
        "STATIC_ROOT", "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME_CRM",
        "DB_NAME_CTC", "DB_NAME_LMS", "DB_NAME_VRESUME",
        "FUSION_WEBPACK_WORKSPACE", "FEATURE_AI_ENABLED", "FEATURE_MCP_SERVER",
    }
    unknown = sorted(
        name for name in set(env) - KNOWN - _shared
        if any(name.startswith(prefix) for prefix in _project_prefixes)
    )
    if unknown:
        problems.append(f"Unknown Loop-CRM variables: {', '.join(unknown)}")

    return problems


def render_env_example() -> str:
    """Render a full ``.env.example`` from the catalog (section-commented)."""
    lines: list[str] = []
    lines.append("# ================================================================")
    lines.append("# Loop-CRM — Environment Configuration (generated from configs/env.py)")
    lines.append("# ================================================================")
    lines.append("# Copy to .env and fill in values. Runtime reads os.environ;")
    lines.append("# backend/settings.py seeds defaults via configs.site.")
    lines.append("# ================================================================")
    last_section = ""
    for name, default, purpose in ENV_VARS:
        section = _section_for(name)
        if section != last_section:
            lines.append("")
            lines.append(f"# ── {section} ─{'─' * max(0, 50 - len(section))}")
            last_section = section
        lines.append(f"# {purpose}")
        value = "" if default in ("", None) else str(default)
        lines.append(f"{name}={value}")
    lines.append("")
    return "\n".join(lines)


def _section_for(name: str) -> str:
    for marker, section in (
        ("DJANGO_", "Core Django"),
        ("POSTGRES_", "Database"),
        ("DB_", "Database"),
        ("REDIS_", "Redis"),
        ("LOOP_", "Ports"),
        ("FUSION_RENDER", "Fusion"),
        ("ACCOUNT_", "Allauth"),
        ("EMAIL_", "Email"),
        ("DEFAULT_FROM", "Email"),
        ("GITHUB_", "Social login"),
        ("GOOGLE_", "Social login"),
        ("LINKEDIN_", "Social publishing"),
        ("X_", "Social publishing"),
        ("SOCIAL_", "Social publishing"),
        ("GMAIL_", "Email sync"),
        ("OUTLOOK_", "Email sync"),
        ("DEMO_", "Demo state"),
        ("FUSION_BOLT_", "django-bolt API"),
        ("PUBLIC_", "Frontend"),
        ("BACKEND_URL", "Frontend"),
        ("PORT", "Frontend"),
    ):
        if name.startswith(marker):
            return section
    return "Other"


if __name__ == "__main__":  # pragma: no cover
    import sys

    problems = validate_environment()
    if problems:
        print("Loop-CRM environment problems:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    print("Loop-CRM environment OK.")
