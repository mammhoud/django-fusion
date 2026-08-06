"""
startup.py — AppConfig.ready() startup validation for lms-fusion.com
=========================================================================
Validates critical configuration at application startup and logs warnings
for any issues found. All checks are non-fatal (the app continues to start)
but issues are logged at CRITICAL or WARNING level so they surface in logs.

Checks performed:
    1. SECRET_KEY length ≥ 50 characters
    2. SECRET_KEY is not a known default/insecure placeholder
    3. No duplicate settings across YAML configuration files
    4. URL routing resolves without errors
    5. Middleware list compatibility
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Known insecure SECRET_KEY prefixes / placeholder values
_INSECURE_KEY_PREFIXES = [
    "django-insecure-",
    "dev-secret-key",
    "change-this-in-production",
    "your-secret-key",
    "changeme",
]
_MIN_SECRET_KEY_LENGTH = 50

# Settings keys to scan for duplicates across YAML files
_AUDITED_KEYS = [
    "SECRET_KEY",
    "DJANGO_SECRET_KEY",
    "DATABASE_URL",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "EMAIL_HOST",
    "EMAIL_PORT",
    "DEBUG",
    "ALLOWED_HOSTS",
]


def _check_secret_key() -> None:
    """Validate SECRET_KEY length and that it is not a default placeholder."""
    try:
        from django.conf import settings

        secret_key: str = getattr(settings, "SECRET_KEY", "") or ""
    except Exception as exc:  # noqa: BLE001
        logger.warning("startup: could not read SECRET_KEY — %s", exc)
        return

    if len(secret_key) < _MIN_SECRET_KEY_LENGTH:
        logger.critical(
            "startup: SECRET_KEY is only %d characters long (minimum: %d). "
            "Generate a secure key with: "
            "python -c \"from django.core.management.utils import get_random_secret_key; "
            "print(get_random_secret_key())\"",
            len(secret_key),
            _MIN_SECRET_KEY_LENGTH,
        )

    for prefix in _INSECURE_KEY_PREFIXES:
        if secret_key.lower().startswith(prefix.lower()):
            logger.critical(
                "startup: SECRET_KEY starts with insecure placeholder prefix '%s'. "
                "Replace it with a securely generated key before deploying.",
                prefix,
            )
            break


def _check_duplicate_settings() -> None:
    """Detect duplicate settings keys defined across multiple YAML config files."""
    # Resolve project root: this file lives at
    # <project_root>/apps/pages/accounts/management/startup.py
    # parents: [0]=management, [1]=accounts, [2]=pages, [3]=apps, [4]=backend, [5]=project_root
    project_root = Path(__file__).resolve().parents[5]
    configs_dir = project_root / "configs"

    if not configs_dir.exists():
        logger.debug("startup: configs dir not found at %s — skipping duplicate check", configs_dir)
        return

    try:
        import yaml  # type: ignore[import]
    except ImportError:
        try:
            from dynaconf.vendor.ruamel import yaml  # type: ignore[no-redef]
        except ImportError:
            logger.debug("startup: no YAML parser available — skipping duplicate check")
            return

    key_sources: dict[str, list[str]] = {}

    for yaml_file in configs_dir.rglob("*.yml"):
        # Environment profiles (e.g. configs/Env/default/_development.yml) are
        # mutually exclusive — only the active environment's file is loaded, so
        # a key defined across several profiles is NOT a duplicate and auditing
        # them together only produces false-positive warnings on every boot.
        # _core.yml is the base config (applies to every environment) and stays
        # audited.
        rel_file = yaml_file.relative_to(project_root)
        if (
            "ENV" in rel_file.parts
            and yaml_file.stem.startswith("_")
            and yaml_file.stem != "_core"
        ):
            continue
        try:
            with yaml_file.open() as fh:
                data = yaml.safe_load(fh)
        except Exception as exc:  # noqa: BLE001
            logger.warning("startup: could not parse %s — %s", yaml_file, exc)
            continue

        if not isinstance(data, dict):
            continue

        # Flatten all environment sections (default, development, demo, production, …)
        sections: list[dict] = [v for v in data.values() if isinstance(v, dict)]
        for section in sections:
            for key in _AUDITED_KEYS:
                if key in section:
                    rel = str(rel_file)
                    key_sources.setdefault(key, [])
                    if rel not in key_sources[key]:
                        key_sources[key].append(rel)

    duplicates = {k: v for k, v in key_sources.items() if len(v) > 1}
    for key, sources in duplicates.items():
        logger.warning(
            "startup: duplicate setting '%s' found in multiple YAML files: %s",
            key,
            ", ".join(sources),
        )


def _check_url_routing() -> None:
    """Verify that URL routing resolves without errors."""
    try:
        from django.test import RequestFactory

        # Trigger URL resolver initialisation — this surfaces misconfigured urlconfs
        from django.urls import NoReverseMatch, get_resolver, reverse

        resolver = get_resolver()
        # Access the url_patterns property to force resolution
        _ = resolver.url_patterns
        logger.debug("startup: URL routing resolved successfully (%d top-level patterns)", len(_))
    except Exception as exc:  # noqa: BLE001
        logger.critical("startup: URL routing failed to resolve — %s", exc, exc_info=True)


def _check_middleware_compatibility() -> None:
    """Check that the middleware list does not contain obvious incompatibilities."""
    try:
        from django.conf import settings

        middleware: list[str] = list(getattr(settings, "MIDDLEWARE", []))
    except Exception as exc:  # noqa: BLE001
        logger.warning("startup: could not read MIDDLEWARE setting — %s", exc)
        return

    middleware_set = set(middleware)

    # SecurityMiddleware should be first
    if middleware and middleware[0] != "django.middleware.security.SecurityMiddleware":
        if "django.middleware.security.SecurityMiddleware" in middleware_set:
            logger.warning(
                "startup: SecurityMiddleware is not the first entry in MIDDLEWARE. "
                "It should be listed first for correct security header injection."
            )

    # SessionMiddleware must come before AuthenticationMiddleware
    session_mw = "django.contrib.sessions.middleware.SessionMiddleware"
    auth_mw = "django.contrib.auth.middleware.AuthenticationMiddleware"
    if session_mw in middleware_set and auth_mw in middleware_set:
        if middleware.index(session_mw) > middleware.index(auth_mw):
            logger.warning(
                "startup: SessionMiddleware must appear before AuthenticationMiddleware "
                "in MIDDLEWARE."
            )

    # CommonMiddleware / LocaleMiddleware ordering hint
    common_mw = "django.middleware.common.CommonMiddleware"
    locale_mw = "django.middleware.locale.LocaleMiddleware"
    if common_mw in middleware_set and locale_mw in middleware_set:
        if middleware.index(locale_mw) > middleware.index(common_mw):
            logger.debug(
                "startup: LocaleMiddleware is listed after CommonMiddleware. "
                "For i18n URL prefix support, LocaleMiddleware should come before CommonMiddleware."
            )

    logger.debug("startup: middleware compatibility check passed (%d entries)", len(middleware))


def run_startup_checks() -> None:
    """
    Run all startup validation checks.

    Called from HandlersConfig.ready(). All checks are non-fatal — the
    application continues to start regardless of findings, but issues are
    logged so they surface in monitoring.
    """
    logger.debug("startup: running startup checks …")

    try:
        _check_secret_key()
    except Exception as exc:  # noqa: BLE001
        logger.error("startup: SECRET_KEY check raised an unexpected error — %s", exc, exc_info=True)

    try:
        _check_duplicate_settings()
    except Exception as exc:  # noqa: BLE001
        logger.error("startup: duplicate settings check raised an unexpected error — %s", exc, exc_info=True)

    try:
        _check_url_routing()
    except Exception as exc:  # noqa: BLE001
        logger.error("startup: URL routing check raised an unexpected error — %s", exc, exc_info=True)

    try:
        _check_middleware_compatibility()
    except Exception as exc:  # noqa: BLE001
        logger.error("startup: middleware check raised an unexpected error — %s", exc, exc_info=True)

    logger.debug("startup: startup checks complete")
