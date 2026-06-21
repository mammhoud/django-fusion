"""Spec directory scanner and indexing."""

import os
from typing import Dict, List, Optional, Tuple

from .models import SpecMetadata


class SpecScanner:
    """Scans and indexes spec directories."""

    REQUIRED_FILES = {"requirements.md", "design.md", "tasks.md"}
    OPTIONAL_FILES = {"bugfix.md", ".config.kiro"}

    def __init__(self):
        """Initialize the scanner."""
        self.specs: Dict[str, Dict[str, SpecMetadata]] = {}
        self.warnings: List[str] = []
        self.cache: Optional[Dict[str, Dict[str, SpecMetadata]]] = None

    def scan(self, base_path: str) -> Dict[str, Dict[str, SpecMetadata]]:
        """
        Scan the spec directory structure.

        Args:
            base_path: Path to .kiro/specs-organized/

        Returns:
            Dictionary mapping category -> spec_name -> SpecMetadata
        """
        self.specs = {}
        self.warnings = []

        if not os.path.isdir(base_path):
            self.warnings.append(f"Base path does not exist: {base_path}")
            return self.specs

        # Scan categories
        try:
            for entry in os.scandir(base_path):
                if entry.is_dir() and not entry.name.startswith("."):
                    category = entry.name
                    self._scan_category(base_path, category)
        except OSError as e:
            self.warnings.append(f"Error scanning base path: {e}")

        return self.specs

    def _scan_category(self, base_path: str, category: str) -> None:
        """Scan a category directory."""
        category_path = os.path.join(base_path, category)
        self.specs[category] = {}

        try:
            for entry in os.scandir(category_path):
                if entry.is_dir() and not entry.name.startswith("."):
                    spec_name = entry.name
                    self._scan_spec(base_path, category, spec_name)
        except OSError as e:
            self.warnings.append(f"Error scanning category {category}: {e}")

    def _scan_spec(self, base_path: str, category: str, spec_name: str) -> None:
        """Scan a spec directory."""
        spec_path = os.path.join(base_path, category, spec_name)

        # Validate required files
        files = self._get_spec_files(spec_path)
        missing_files = self.REQUIRED_FILES - set(files.keys())

        if missing_files:
            self.warnings.append(
                f"Spec {category}/{spec_name} missing files: {', '.join(missing_files)}"
            )

        # Create metadata
        metadata = SpecMetadata(
            category=category,
            spec_name=spec_name,
            path=spec_path,
            requirements_path=files.get("requirements.md"),
            design_path=files.get("design.md"),
            tasks_path=files.get("tasks.md"),
            bugfix_path=files.get("bugfix.md"),
            config_path=files.get(".config.kiro"),
            files=list(files.keys()),
        )

        self.specs[category][spec_name] = metadata

    def _get_spec_files(self, spec_path: str) -> Dict[str, str]:
        """Get files in a spec directory."""
        files = {}

        try:
            for entry in os.scandir(spec_path):
                if entry.is_file():
                    if entry.name in self.REQUIRED_FILES or entry.name in self.OPTIONAL_FILES:
                        files[entry.name] = entry.path
        except OSError as e:
            self.warnings.append(f"Error scanning spec {spec_path}: {e}")

        return files

    def get_spec(self, category: str, spec_name: str) -> Optional[SpecMetadata]:
        """Get metadata for a specific spec."""
        return self.specs.get(category, {}).get(spec_name)

    def get_specs_by_category(self, category: str) -> List[SpecMetadata]:
        """Get all specs in a category."""
        return list(self.specs.get(category, {}).values())

    def get_all_specs(self) -> List[SpecMetadata]:
        """Get all specs."""
        specs = []
        for category_specs in self.specs.values():
            specs.extend(category_specs.values())
        return specs

    def get_categories(self) -> List[str]:
        """Get all categories."""
        return list(self.specs.keys())

    def validate_spec_files(self, spec_path: str) -> Dict[str, bool]:
        """Validate required files in a spec directory."""
        result = {}
        for filename in self.REQUIRED_FILES | self.OPTIONAL_FILES:
            result[filename] = os.path.isfile(os.path.join(spec_path, filename))
        return result

    def get_warnings(self) -> List[str]:
        """Get all warnings from scanning."""
        return self.warnings

    def find_similar_specs(self, name: str) -> List[Tuple[str, str]]:
        """Find specs with similar names."""
        similar = []
        name_lower = name.lower()

        for category, specs in self.specs.items():
            for spec_name in specs.keys():
                if name_lower in spec_name.lower() or spec_name.lower() in name_lower:
                    similar.append((category, spec_name))

        return similar

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about discovered specs."""
        total_specs = sum(len(specs) for specs in self.specs.values())
        total_categories = len(self.specs)

        return {
            "total_specs": total_specs,
            "total_categories": total_categories,
            "categories": {
                category: len(specs) for category, specs in self.specs.items()
            },
            "warnings": len(self.warnings),
        }
