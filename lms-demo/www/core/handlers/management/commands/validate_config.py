"""
validate_config management command
===================================
Audits configuration for duplicate settings between YAML configs and .env,
warns on insecure SECRET_KEY values, and documents precedence rules.

Precedence rule:
    .env values take precedence over YAML defaults.
    Dynaconf loads YAML files first, then .env overrides them via pydantic-settings
    (env_file=".env") and Dynaconf's load_dotenv=True. The effective value is
    always the one from .env when both sources define the same key.

Usage:
    uv run python manage.py validate_config
    uv run python manage.py validate_config --export-effective
"""

import logging
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand

# Use dynaconf's vendored ruamel.yaml since PyYAML may not be installed separately.
# dynaconf bundles ruamel.yaml under dynaconf.vendor.ruamel.yaml.
try:
    import yaml  # type: ignore[import]
except ImportError:
    from dynaconf.vendor.ruamel import yaml  # type: ignore[no-redef]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keys to audit for duplicates
# ---------------------------------------------------------------------------
# These are the settings that are known to appear in both YAML configs and .env.
# Extend this list if new shared keys are added.
AUDITED_KEYS = [
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
    "EMAIL_USE_TLS",
    "EMAIL_USE_SSL",
    "EMAIL_USER",
    "EMAIL_PASSWORD",
    "EMAIL_STRATEGY",
    "DEFAULT_FROM_EMAIL",
    "ALLOWED_HOSTS",
    "DEBUG",
]

# Insecure SECRET_KEY prefixes / known defaults
INSECURE_KEY_PREFIXES = [
    "django-insecure-",
    "dev-secret-key",
    "change-this-in-production",
    "your-secret-key",
]
MIN_SECRET_KEY_LENGTH = 50


def _load_env_file(env_path: Path) -> dict[str, str]:
    """
    Parse a .env file and return a dict of key → value.

    .env values take precedence over YAML defaults (see module docstring).
    """
    env_vars: dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    with env_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()
    return env_vars


def _collect_yaml_keys(configs_dir: Path) -> dict[str, list[str]]:
    """
    Walk all YAML files under configs_dir and collect which keys appear in them.

    Returns a mapping of key → [list of yaml file paths that define it].
    """
    key_sources: dict[str, list[str]] = {}

    for yaml_file in configs_dir.rglob("*.yml"):
        try:
            with yaml_file.open() as fh:
                data = yaml.safe_load(fh)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not parse %s: %s", yaml_file, exc)
            continue

        if not isinstance(data, dict):
            continue

        # Flatten all environment sections (default, development, demo, production, …)
        all_sections: list[dict] = []
        for section_value in data.values():
            if isinstance(section_value, dict):
                all_sections.append(section_value)

        for section in all_sections:
            for key in AUDITED_KEYS:
                # Direct key match
                if key in section:
                    key_sources.setdefault(key, [])
                    rel = str(yaml_file.relative_to(configs_dir.parent))
                    if rel not in key_sources[key]:
                        key_sources[key].append(rel)
                # Also check nested SECURITY block for ALLOWED_HOSTS
                if key == "ALLOWED_HOSTS" and "SECURITY" in section:
                    security = section["SECURITY"]
                    if isinstance(security, dict) and "ALLOWED_HOSTS" in security:
                        key_sources.setdefault(key, [])
                        rel = str(yaml_file.relative_to(configs_dir.parent))
                        if rel not in key_sources[key]:
                            key_sources[key].append(rel)

    return key_sources


def _check_secret_key(secret_key: str | None) -> list[str]:
    """
    Return a list of warning messages for an insecure or missing SECRET_KEY.
    """
    warnings: list[str] = []
    if not secret_key:
        warnings.append("SECRET_KEY / DJANGO_SECRET_KEY is not set.")
        return warnings

    for prefix in INSECURE_KEY_PREFIXES:
        if secret_key.lower().startswith(prefix.lower()):
            warnings.append(
                f"SECRET_KEY starts with insecure prefix '{prefix}'. "
                "Generate a new key with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
            )

    if len(secret_key) < MIN_SECRET_KEY_LENGTH:
        warnings.append(
            f"SECRET_KEY is only {len(secret_key)} characters long "
            f"(minimum recommended: {MIN_SECRET_KEY_LENGTH})."
        )

    return warnings


class Command(BaseCommand):
    help = (
        "Audit configuration for duplicate settings between YAML configs and .env, "
        "and warn on insecure SECRET_KEY values.\n\n"
        "Precedence: .env values override YAML defaults. "
        "Dynaconf loads YAML files first; pydantic-settings then applies .env on top."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--export-effective",
            action="store_true",
            default=False,
            help="Print the effective (resolved) value for each audited key.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Locate project root (lms-demo/)
        # File is at: <project_root>/apps/handlers/management/commands/validate_config.py
        # parents: [0]=commands, [1]=management, [2]=handlers, [3]=apps, [4]=project_root
        project_root = Path(__file__).resolve().parents[4]  # …/lms-demo
        configs_dir = project_root / "configs"
        env_path = project_root / ".env"

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Configuration Audit ===\n"))
        self.stdout.write(f"Project root : {project_root}")
        self.stdout.write(f"Configs dir  : {configs_dir}")
        self.stdout.write(f".env file    : {env_path}\n")

        # ------------------------------------------------------------------
        # 1. Load .env
        # ------------------------------------------------------------------
        env_vars = _load_env_file(env_path)
        self.stdout.write(
            self.style.SUCCESS(f"Loaded {len(env_vars)} variables from .env")
        )

        # ------------------------------------------------------------------
        # 2. Collect YAML key definitions
        # ------------------------------------------------------------------
        yaml_key_sources = _collect_yaml_keys(configs_dir)

        # ------------------------------------------------------------------
        # 3. Detect duplicates (key defined in both .env AND at least one YAML)
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("\n--- Duplicate Settings ---"))
        duplicates_found = False

        for key in AUDITED_KEYS:
            in_env = key in env_vars
            in_yaml = key in yaml_key_sources

            if in_env and in_yaml:
                duplicates_found = True
                yaml_files = ", ".join(yaml_key_sources[key])
                msg = (
                    f"DUPLICATE: '{key}' is defined in both .env AND YAML "
                    f"({yaml_files}). "
                    # .env values take precedence over YAML defaults
                    ".env value takes precedence (YAML value is ignored at runtime)."
                )
                self.stdout.write(self.style.WARNING(f"  ⚠  {msg}"))
                logger.warning(msg)

        if not duplicates_found:
            self.stdout.write(self.style.SUCCESS("  ✓  No duplicate settings detected."))

        # ------------------------------------------------------------------
        # 4. SECRET_KEY security check
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("\n--- SECRET_KEY Validation ---"))

        # Prefer DJANGO_SECRET_KEY (the field name used in MainSettings),
        # fall back to SECRET_KEY.
        secret_key = env_vars.get("DJANGO_SECRET_KEY") or env_vars.get("SECRET_KEY")

        # Also check the Django runtime value if Django is already configured.
        try:
            from django.conf import settings as django_settings

            runtime_key = getattr(django_settings, "SECRET_KEY", None)
            if runtime_key and not secret_key:
                secret_key = runtime_key
        except Exception:  # noqa: BLE001
            pass

        sk_warnings = _check_secret_key(secret_key)
        if sk_warnings:
            for w in sk_warnings:
                self.stdout.write(self.style.ERROR(f"  ✗  {w}"))
                logger.critical("SECRET_KEY issue: %s", w)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓  SECRET_KEY looks secure (length={len(secret_key)})."
                )
            )

        # ------------------------------------------------------------------
        # 5. Optional: export effective values
        # ------------------------------------------------------------------
        if options["export_effective"]:
            self.stdout.write(self.style.MIGRATE_HEADING("\n--- Effective Configuration ---"))
            self.stdout.write(
                "  (Values shown are from .env when present; YAML default otherwise.)\n"
            )
            for key in AUDITED_KEYS:
                # .env takes precedence over YAML defaults
                if key in env_vars:
                    source = ".env"
                    value = env_vars[key]
                elif key in yaml_key_sources:
                    source = f"YAML ({yaml_key_sources[key][0]})"
                    value = "<see YAML file>"
                else:
                    source = "not set"
                    value = ""

                # Mask sensitive values
                display_value = value
                if any(s in key.upper() for s in ("PASSWORD", "SECRET", "TOKEN", "KEY")):
                    display_value = "***" if value else "(empty)"

                self.stdout.write(f"  {key:<30} = {display_value:<30}  [{source}]")

        # ------------------------------------------------------------------
        # 6. Summary
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("\n--- Summary ---"))
        self.stdout.write(
            "Precedence rule: .env values override YAML defaults.\n"
            "  Dynaconf loads YAML files first (configs/settings/ENV/*.yml),\n"
            "  then pydantic-settings applies .env on top via env_file='.env'.\n"
            "  The effective runtime value is always the .env value when both\n"
            "  sources define the same key.\n"
        )

        if duplicates_found or sk_warnings:
            self.stdout.write(
                self.style.WARNING(
                    "Audit complete with warnings. Review the items above."
                )
            )
            logger.warning("Configuration audit completed with warnings.")
        else:
            self.stdout.write(self.style.SUCCESS("Audit complete. No issues found."))
            logger.info("Configuration audit completed successfully.")
