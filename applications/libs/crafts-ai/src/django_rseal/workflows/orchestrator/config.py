"""Configuration management."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict

from .models import TaskStatus


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


class ConfigLoader:
    """Loads configuration from various sources."""

    def __init__(self):
        """Initialize the config loader."""
        self.config = OrchestratorConfig()
        self.warnings: list[str] = []

    def load_from_file(self, file_path: str) -> OrchestratorConfig:
        """Load configuration from .config.kiro file."""
        if not os.path.isfile(file_path):
            self.warnings.append(f"Config file not found: {file_path}")
            return self.config

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.config = OrchestratorConfig.from_dict(data)
        except json.JSONDecodeError as e:
            self.warnings.append(f"Error parsing config file: {e}")
        except Exception as e:
            self.warnings.append(f"Error loading config file: {e}")

        return self.config

    def load_from_env(self) -> OrchestratorConfig:
        """Load configuration from environment variables."""
        env_mapping = {
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

        config_dict = self.config.to_dict()

        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]

                # Type conversion
                if config_key in ("pbt_iterations", "max_retries", "cache_ttl"):
                    try:
                        value = int(value)
                    except ValueError:
                        self.warnings.append(
                            f"Invalid value for {env_var}: {value} (expected int)"
                        )
                        continue
                elif config_key in ("enable_parallel", "enable_rollback", "enable_caching"):
                    value = value.lower() in ("true", "1", "yes")

                config_dict[config_key] = value

        self.config = OrchestratorConfig.from_dict(config_dict)
        return self.config

    def load_from_args(self, args: Dict[str, Any]) -> OrchestratorConfig:
        """Load configuration from command-line arguments."""
        config_dict = self.config.to_dict()

        for key, value in args.items():
            if key in config_dict and value is not None:
                config_dict[key] = value

        self.config = OrchestratorConfig.from_dict(config_dict)
        return self.config

    def validate_config(self) -> bool:
        """Validate configuration."""
        errors = []

        # Validate base_path
        if not self.config.base_path:
            errors.append("base_path is required")

        # Validate default_status
        try:
            TaskStatus(self.config.default_status)
        except ValueError:
            errors.append(f"Invalid default_status: {self.config.default_status}")

        # Validate pbt_framework
        if self.config.pbt_framework not in ("hypothesis", "pytest", "fast-check"):
            self.warnings.append(
                f"Unknown PBT framework: {self.config.pbt_framework}"
            )

        # Validate pbt_iterations
        if self.config.pbt_iterations < 1:
            errors.append("pbt_iterations must be >= 1")

        # Validate max_retries
        if self.config.max_retries < 0:
            errors.append("max_retries must be >= 0")

        # Validate cache_ttl
        if self.config.cache_ttl < 0:
            errors.append("cache_ttl must be >= 0")

        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

        return True

    def get_config(self) -> OrchestratorConfig:
        """Get current configuration."""
        return self.config

    def get_warnings(self) -> list[str]:
        """Get configuration warnings."""
        return self.warnings

    def log_config_summary(self) -> str:
        """Get configuration summary."""
        summary = "Configuration Summary:\n"
        for key, value in self.config.to_dict().items():
            summary += f"  {key}: {value}\n"
        return summary
