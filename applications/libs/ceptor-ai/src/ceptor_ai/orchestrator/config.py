"""Configuration management — pure operators over :class:`OrchestratorConfig`.

Decomposed from the legacy :class:`ConfigLoader` class. The dataclass
:class:`OrchestratorConfig` keeps the canonical configuration state (held on
``state.config`` in :class:`~.operators.OrchestratorState`); these operators
load and validate it from various sources without holding any hidden per-call
state.

Naming intentionally omits the parent directory: callers do
``config.load_from_file(path)`` rather than ``config.config_load_from_file``.
The parent package already implies the domain.

Each loader function returns ``(OrchestratorConfig, List[str])`` so callers can
accumulate warnings explicitly. :func:`validate_config` returns the list of
errors it would raise — a small helper, ``validate_or_raise``, calls
:func:`validate_config` and raises ``ValueError`` when the list is non-empty
so existing CLI entry points keep their fail-fast behaviour.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .models import TaskStatus


# ---------------------------------------------------------------------------
# Configuration dataclass — canonical state
# ---------------------------------------------------------------------------


@dataclass
class OrchestratorConfig:
    """Orchestrator configuration."""

    base_path: str = ".kiro/specs-organized"
    default_status: str = "not_started"
    pbt_framework: str = "hypothesis"
    pbt_iterations: int = 100
    script_paths: Dict[str, str] = field(default_factory=dict)
    report_output_dir: str = "reports"
    log_level: str = "INFO"
    max_retries: int = 3
    enable_parallel: bool = True
    enable_rollback: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "base_path": self.base_path,
            "default_status": self.default_status,
            "pbt_framework": self.pbt_framework,
            "pbt_iterations": self.pbt_iterations,
            "script_paths": self.script_paths,
            "report_output_dir": self.report_output_dir,
            "log_level": self.log_level,
            "max_retries": self.max_retries,
            "enable_parallel": self.enable_parallel,
            "enable_rollback": self.enable_rollback,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrchestratorConfig":
        """Create from dictionary."""
        return cls(
            base_path=data.get("base_path", ".kiro/specs-organized"),
            default_status=data.get("default_status", "not_started"),
            pbt_framework=data.get("pbt_framework", "hypothesis"),
            pbt_iterations=data.get("pbt_iterations", 100),
            script_paths=data.get("script_paths", {}),
            report_output_dir=data.get("report_output_dir", "reports"),
            log_level=data.get("log_level", "INFO"),
            max_retries=data.get("max_retries", 3),
            enable_parallel=data.get("enable_parallel", True),
            enable_rollback=data.get("enable_rollback", True),
            enable_caching=data.get("enable_caching", True),
            cache_ttl=data.get("cache_ttl", 3600),
        )


# ---------------------------------------------------------------------------
# Loaders — each returns ``(config, warnings)`` so callers accumulate explicitly
# ---------------------------------------------------------------------------


# Map of ``ORCHESTRATOR_*`` environment variables to ``OrchestratorConfig`` keys.
_ENV_MAPPING: Dict[str, str] = {
    "ORCHESTRATOR_BASE_PATH": "base_path",
    "ORCHESTRATOR_DEFAULT_STATUS": "default_status",
    "ORCHESTRATOR_PBT_FRAMEWORK": "pbt_framework",
    "ORCHESTRATOR_PBT_ITERATIONS": "pbt_iterations",
    "ORCHESTRATOR_REPORT_OUTPUT_DIR": "report_output_dir",
    "ORCHESTRATOR_LOG_LEVEL": "log_level",
    "ORCHESTRATOR_MAX_RETRIES": "max_retries",
    "ORCHESTRATOR_ENABLE_PARALLEL": "enable_parallel",
    "ORCHESTRATOR_ENABLE_ROLLBACK": "enable_rollback",
    "ORCHESTRATOR_ENABLE_CACHING": "enable_caching",
    "ORCHESTRATOR_CACHE_TTL": "cache_ttl",
}

_INT_KEYS = {"pbt_iterations", "max_retries", "cache_ttl"}
_BOOL_KEYS = {"enable_parallel", "enable_rollback", "enable_caching"}


def load_from_file(
    file_path: str,
    config: Optional[OrchestratorConfig] = None,
) -> Tuple[OrchestratorConfig, List[str]]:
    """Load configuration from a ``.config.kiro`` JSON file.

    Returns ``(new_config, warnings)``. When ``file_path`` is missing or
    malformed, the existing ``config`` is returned unchanged with a warning
    appended — loaders never raise for parse failures.
    """
    config = config or OrchestratorConfig()
    warnings: List[str] = []

    if not os.path.isfile(file_path):
        warnings.append(f"Config file not found: {file_path}")
        return config, warnings

    try:
        with open(file_path, "r") as fh:
            data = json.load(fh)
        config = OrchestratorConfig.from_dict(data)
    except json.JSONDecodeError as exc:
        warnings.append(f"Error parsing config file: {exc}")
    except Exception as exc:
        warnings.append(f"Error loading config file: {exc}")

    return config, warnings


def load_from_env(
    config: Optional[OrchestratorConfig] = None,
) -> Tuple[OrchestratorConfig, List[str]]:
    """Overlay configuration from ``ORCHESTRATOR_*`` environment variables.

    Variables that fail type conversion produce a warning rather than failing
    the load — callers can choose whether to keep the default value or raise.
    """
    config = config or OrchestratorConfig()
    warnings: List[str] = []
    if not os.environ:
        return config, warnings

    config_dict = config.to_dict()

    for env_var, config_key in _ENV_MAPPING.items():
        if env_var not in os.environ:
            continue
        value = os.environ[env_var]

        if config_key in _INT_KEYS:
            try:
                value = int(value)
            except ValueError:
                warnings.append(
                    f"Invalid value for {env_var}: {value} (expected int)"
                )
                continue
        elif config_key in _BOOL_KEYS:
            value = value.lower() in ("true", "1", "yes")

        config_dict[config_key] = value

    return OrchestratorConfig.from_dict(config_dict), warnings


def load_from_args(
    args: Dict[str, Any],
    config: Optional[OrchestratorConfig] = None,
) -> Tuple[OrchestratorConfig, List[str]]:
    """Overlay configuration from CLI argument dict."""
    config = config or OrchestratorConfig()
    warnings: List[str] = []
    config_dict = config.to_dict()

    for key, value in args.items():
        if key in config_dict and value is not None:
            config_dict[key] = value

    return OrchestratorConfig.from_dict(config_dict), warnings


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_config(config: OrchestratorConfig) -> List[str]:
    """Validate configuration and return a list of error messages.

    Empty list means valid. Use :func:`validate_or_raise` for the legacy
    raise-on-invalid behaviour.
    """
    errors: List[str] = []

    if not config.base_path:
        errors.append("base_path is required")

    try:
        TaskStatus(config.default_status)
    except ValueError:
        errors.append(f"Invalid default_status: {config.default_status}")

    if config.pbt_iterations < 1:
        errors.append("pbt_iterations must be >= 1")

    if config.max_retries < 0:
        errors.append("max_retries must be >= 0")

    if config.cache_ttl < 0:
        errors.append("cache_ttl must be >= 0")

    return errors


def validate_warnings(config: OrchestratorConfig) -> List[str]:
    """Non-fatal advisories about the configuration (e.g. unknown frameworks)."""
    warnings: List[str] = []
    if config.pbt_framework not in ("hypothesis", "pytest", "fast-check"):
        warnings.append(f"Unknown PBT framework: {config.pbt_framework}")
    return warnings


def validate_or_raise(config: OrchestratorConfig) -> None:
    """Raise ``ValueError`` when :func:`validate_config` finds any errors."""
    errors = validate_config(config)
    if errors:
        raise ValueError(
            f"Configuration validation failed: {'; '.join(errors)}"
        )


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------


def format_summary(config: OrchestratorConfig) -> str:
    """Return a human-readable configuration summary."""
    lines = ["Configuration Summary:"]
    for key, value in config.to_dict().items():
        lines.append(f"  {key}: {value}")
    return "\n".join(lines) + "\n"
