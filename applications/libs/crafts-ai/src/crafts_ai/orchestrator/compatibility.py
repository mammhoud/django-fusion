"""Backward compatibility layer for spec file formats."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SpecFormatVersion(Enum):
    """Supported spec file format versions."""

    V1 = "1.0"  # Original format
    V2 = "2.0"  # Current format with enhanced features


@dataclass
class FormatCompatibilityInfo:
    """Information about format compatibility."""

    current_version: SpecFormatVersion
    supported_versions: List[SpecFormatVersion]
    deprecated_features: List[str]
    migration_paths: Dict[str, str]


class CompatibilityLayer:
    """Handles backward compatibility for spec file formats."""

    def __init__(self):
        """Initialize the compatibility layer."""
        self.current_version = SpecFormatVersion.V2
        self.supported_versions = [SpecFormatVersion.V1, SpecFormatVersion.V2]
        self.deprecated_features = [
            "old_task_format",
            "legacy_requirement_ids",
        ]
        self.migration_paths = {
            "V1": "V2",
        }

    def detect_format_version(self, content: str) -> SpecFormatVersion:
        """
        Detect the format version of a spec file.

        Args:
            content: The content of the spec file

        Returns:
            The detected format version
        """
        # Check for V2 markers
        if "**Validates:" in content or "**Property" in content:
            return SpecFormatVersion.V2

        # Default to V1
        return SpecFormatVersion.V1

    def is_format_supported(self, version: SpecFormatVersion) -> bool:
        """
        Check if a format version is supported.

        Args:
            version: The format version to check

        Returns:
            True if the version is supported, False otherwise
        """
        return version in self.supported_versions

    def get_compatibility_info(self) -> FormatCompatibilityInfo:
        """
        Get information about format compatibility.

        Returns:
            FormatCompatibilityInfo with current and supported versions
        """
        return FormatCompatibilityInfo(
            current_version=self.current_version,
            supported_versions=self.supported_versions,
            deprecated_features=self.deprecated_features,
            migration_paths=self.migration_paths,
        )

    def migrate_format(
        self, content: str, from_version: SpecFormatVersion, to_version: SpecFormatVersion
    ) -> str:
        """
        Migrate spec file content from one format version to another.

        Args:
            content: The content to migrate
            from_version: The source format version
            to_version: The target format version

        Returns:
            The migrated content
        """
        if from_version == to_version:
            return content

        if from_version == SpecFormatVersion.V1 and to_version == SpecFormatVersion.V2:
            return self._migrate_v1_to_v2(content)

        # No migration path available
        return content

    def _migrate_v1_to_v2(self, content: str) -> str:
        """
        Migrate from V1 format to V2 format.

        Args:
            content: The V1 format content

        Returns:
            The V2 format content
        """
        # V1 to V2 migration is minimal since V2 is backward compatible
        # Just ensure new sections are present if needed
        return content

    def check_deprecated_features(self, content: str) -> List[Tuple[str, str]]:
        """
        Check for deprecated features in spec content.

        Args:
            content: The spec file content

        Returns:
            List of (feature_name, suggestion) tuples for deprecated features
        """
        deprecated_found = []

        for feature in self.deprecated_features:
            if feature in content:
                suggestion = self._get_migration_suggestion(feature)
                deprecated_found.append((feature, suggestion))

        return deprecated_found

    def _get_migration_suggestion(self, feature: str) -> str:
        """
        Get migration suggestion for a deprecated feature.

        Args:
            feature: The deprecated feature name

        Returns:
            Migration suggestion
        """
        suggestions = {
            "old_task_format": "Use new task format with [x] or [ ] checkboxes",
            "legacy_requirement_ids": "Use new requirement ID format (R1, R2, etc.)",
        }
        return suggestions.get(feature, "Please update to the latest format")

    def validate_format_compatibility(self, content: str, expected_version: Optional[SpecFormatVersion] = None) -> Tuple[bool, List[str]]:
        """
        Validate that spec content is compatible with expected format.

        Args:
            content: The spec file content
            expected_version: The expected format version (None = any supported version)

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        # Detect format version
        detected_version = self.detect_format_version(content)

        # Check if version is supported
        if not self.is_format_supported(detected_version):
            return False, [f"Format version {detected_version.value} is not supported"]

        # Check if detected version matches expected version
        if expected_version and detected_version != expected_version:
            warnings.append(
                f"Expected format version {expected_version.value}, "
                f"but detected {detected_version.value}"
            )

        # Check for deprecated features
        deprecated = self.check_deprecated_features(content)
        for feature, suggestion in deprecated:
            warnings.append(f"Deprecated feature '{feature}': {suggestion}")

        return True, warnings

    def get_format_migration_path(self, from_version: SpecFormatVersion, to_version: SpecFormatVersion) -> Optional[List[SpecFormatVersion]]:
        """
        Get the migration path from one format version to another.

        Args:
            from_version: The source format version
            to_version: The target format version

        Returns:
            List of versions in the migration path, or None if no path exists
        """
        if from_version == to_version:
            return [from_version]

        # Simple linear migration path
        if from_version == SpecFormatVersion.V1 and to_version == SpecFormatVersion.V2:
            return [SpecFormatVersion.V1, SpecFormatVersion.V2]

        return None

    def supports_feature_detection(self) -> bool:
        """
        Check if feature detection is supported.

        Returns:
            True if feature detection is supported
        """
        return True

    def detect_management_script_version(self, script_output: str) -> Optional[str]:
        """
        Detect the version of a management script based on its output.

        Args:
            script_output: The output from a management script

        Returns:
            The detected version, or None if version cannot be determined
        """
        # Check for version markers in script output
        if "v2" in script_output.lower() or "version 2" in script_output.lower():
            return "2.0"

        if "v1" in script_output.lower() or "version 1" in script_output.lower():
            return "1.0"

        # Default to latest version
        return "2.0"

    def is_management_script_compatible(self, script_version: str) -> bool:
        """
        Check if a management script version is compatible.

        Args:
            script_version: The version of the management script

        Returns:
            True if the script version is compatible
        """
        # Support both v1 and v2 scripts
        return script_version in ["1.0", "2.0"]
