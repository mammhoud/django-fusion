#!/usr/bin/env python3
"""
Duplicate Code Scanner for Django Libs Monorepo

This script scans django-fusion, ceptor-ai, django-seed (nawaai), and django-fusion
packages for duplicate classes, functions, and modules using AST parsing.

Generates a DUPLICATE_AUDIT.md file with findings.
"""

import ast
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class Symbol:
    """Represents a code symbol (class, function, or constant)."""
    name: str
    type: str  # "class", "function", "constant", "module"
    file_path: str
    line_number: int

    def __hash__(self):
        return hash((self.name, self.type))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type


@dataclass
class DuplicateEntry:
    """Represents a duplicate code entry."""
    symbol_name: str
    symbol_type: str
    locations: List[str] = field(default_factory=list)
    canonical_location: str = ""
    action: str = ""
    notes: str = ""


class DuplicateScanner:
    """Scans Python packages for duplicate code symbols."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.packages = ["django-fusion", "ceptor-ai", "django-seed", "django-fusion"]
        self.symbols: Dict[Tuple[str, str], List[Symbol]] = defaultdict(list)

    def scan_all_packages(self):
        """Scan all packages for symbols."""
        for package in self.packages:
            package_path = self.base_path / package
            if package_path.exists():
                print(f"Scanning {package}...")
                self.scan_package(package, package_path)
            else:
                print(f"Warning: {package} not found at {package_path}")

    def scan_package(self, package_name: str, package_path: Path):
        """Scan a single package for symbols."""
        # Look for Python files in src/ directory
        src_path = package_path / "src"
        if not src_path.exists():
            # Fallback to package root for django-seed structure
            src_path = package_path

        for py_file in src_path.rglob("*.py"):
            # Skip __pycache__, .venv, tests, migrations
            if any(skip in py_file.parts for skip in ["__pycache__", ".venv", "tests", "migrations", ".git"]):
                continue

            self.scan_file(package_name, py_file)

    def scan_file(self, package_name: str, file_path: Path):
        """Scan a single Python file for symbols."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                symbol = None

                if isinstance(node, ast.ClassDef):
                    symbol = Symbol(
                        name=node.name,
                        type="class",
                        file_path=str(file_path.relative_to(self.base_path)),
                        line_number=node.lineno
                    )

                elif isinstance(node, ast.FunctionDef):
                    # Skip private functions (starting with _)
                    if not node.name.startswith('_'):
                        symbol = Symbol(
                            name=node.name,
                            type="function",
                            file_path=str(file_path.relative_to(self.base_path)),
                            line_number=node.lineno
                        )

                elif isinstance(node, ast.Assign):
                    # Check for module-level constants (UPPERCASE names)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            symbol = Symbol(
                                name=target.id,
                                type="constant",
                                file_path=str(file_path.relative_to(self.base_path)),
                                line_number=node.lineno
                            )

                if symbol:
                    key = (symbol.name, symbol.type)
                    self.symbols[key].append(symbol)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def find_duplicates(self) -> List[DuplicateEntry]:
        """Find symbols that appear in multiple packages."""
        duplicates = []

        for (name, symbol_type), symbols in self.symbols.items():
            if len(symbols) > 1:
                # Check if symbols are in different packages
                packages_with_symbol = set()
                for symbol in symbols:
                    package = symbol.file_path.split('/')[0]
                    packages_with_symbol.add(package)

                if len(packages_with_symbol) > 1:
                    # This is a duplicate across packages
                    locations = [f"{s.file_path}:{s.line_number}" for s in symbols]

                    # Determine canonical location based on design rules
                    canonical = self.determine_canonical_location(name, symbol_type, symbols)
                    action = self.determine_action(name, symbol_type, symbols)
                    notes = self.generate_notes(name, symbol_type, symbols)

                    entry = DuplicateEntry(
                        symbol_name=name,
                        symbol_type=symbol_type,
                        locations=locations,
                        canonical_location=canonical,
                        action=action,
                        notes=notes
                    )
                    duplicates.append(entry)

        # Sort by symbol name for consistent output
        duplicates.sort(key=lambda x: x.symbol_name)
        return duplicates

    def determine_canonical_location(self, name: str, symbol_type: str, symbols: List[Symbol]) -> str:
        """Determine the canonical location for a symbol based on design rules."""
        # Foundation utilities → django-fusion
        foundation_patterns = [
            "BaseModel", "TimeStampedModel", "SoftDeleteMixin", "UUIDPrimaryKeyModel",
            "slugify", "truncate", "strip_html", "success_response", "error_response",
            "format_relative", "validate_email", "validate_phone", "AjaxResponseMixin",
            "MessageMixin"
        ]

        # Automation features → ceptor-ai
        automation_patterns = [
            "EmailLog", "EmailService", "Seeder", "guessers", "providers",
            "send_invitations", "orchestrator", "email_tools", "pipelines", "routes",
            "contrib", "admin_site", "email_admin", "cache"
        ]

        # AI/MCP features → nawaai
        ai_patterns = [
            "AIIntegration", "MCPServer", "SimpleSeeder", "craftsai"
        ]

        # UI components → django-fusion
        if "comp" in name.lower():
            for symbol in symbols:
                if "django-fusion" in symbol.file_path:
                    return symbol.file_path
            return symbols[0].file_path

        # Check patterns
        for pattern in foundation_patterns:
            if pattern.lower() in name.lower():
                for symbol in symbols:
                    if "django-fusion" in symbol.file_path:
                        return symbol.file_path

        for pattern in automation_patterns:
            if pattern.lower() in name.lower():
                for symbol in symbols:
                    if "ceptor-ai" in symbol.file_path:
                        return symbol.file_path

        for pattern in ai_patterns:
            if pattern.lower() in name.lower():
                for symbol in symbols:
                    if "django-seed" in symbol.file_path or "nawaai" in symbol.file_path:
                        return symbol.file_path

        # Default: return first occurrence
        return symbols[0].file_path

    def determine_action(self, name: str, symbol_type: str, symbols: List[Symbol]) -> str:
        """Determine the action to take for a duplicate."""
        canonical = self.determine_canonical_location(name, symbol_type, symbols)

        actions = []
        for symbol in symbols:
            if symbol.file_path == canonical:
                package = symbol.file_path.split('/')[0]
                actions.append(f"Keep {package}")
            else:
                package = symbol.file_path.split('/')[0]
                actions.append(f"remove {package}")

        return ", ".join(actions)

    def generate_notes(self, name: str, symbol_type: str, symbols: List[Symbol]) -> str:
        """Generate notes about the duplicate."""
        if symbol_type == "class":
            if "Model" in name or "Mixin" in name:
                return "Foundation model/mixin"
            elif "Service" in name:
                return "Service class"
            elif "Test" in name:
                return "Test class"
        elif symbol_type == "function":
            if "validate" in name.lower():
                return "Validator function"
            elif "format" in name.lower() or "slugify" in name.lower():
                return "Utility function"

        return f"{symbol_type.capitalize()} duplicate"

    def generate_markdown_report(self, duplicates: List[DuplicateEntry]) -> str:
        """Generate a markdown report of duplicates."""
        report = []
        report.append("# Duplicate Code Audit Report")
        report.append("")
        report.append("This report identifies duplicate code symbols across django-fusion, ceptor-ai, django-seed (nawaai), and django-fusion packages.")
        report.append("")
        report.append(f"**Total Duplicates Found**: {len(duplicates)}")
        report.append("")
        report.append("## Duplicate Code Audit Table")
        report.append("")
        report.append("| Symbol Name | Type | Current Locations | Canonical Location | Action | Notes |")
        report.append("|-------------|------|-------------------|-------------------|--------|-------|")

        for entry in duplicates:
            locations_str = "<br>".join(entry.locations)
            report.append(
                f"| {entry.symbol_name} | {entry.symbol_type} | {locations_str} | "
                f"{entry.canonical_location} | {entry.action} | {entry.notes} |"
            )

        report.append("")
        report.append("## Summary by Package")
        report.append("")

        # Count duplicates by package
        package_counts = defaultdict(int)
        for entry in duplicates:
            for location in entry.locations:
                package = location.split('/')[0]
                package_counts[package] += 1

        for package, count in sorted(package_counts.items()):
            report.append(f"- **{package}**: {count} duplicate symbols")

        report.append("")
        report.append("## Elimination Strategy")
        report.append("")
        report.append("1. **Foundation utilities** → django-fusion (keep osoul, remove from grep)")
        report.append("2. **Automation features** → ceptor-ai (keep rseal, remove from grep/seed)")
        report.append("3. **AI/MCP features** → nawaai (keep nawaai, rseal imports optionally)")
        report.append("4. **UI components** → django-fusion/comp/ (move from grep/rseal)")
        report.append("5. **Testing utilities** → django-fusion (new purpose, remove old code)")

        return "\n".join(report)


def main():
    """Main entry point."""
    # Determine base path (libs directory)
    script_dir = Path(__file__).parent
    base_path = script_dir.parent / "libs"

    if not base_path.exists():
        print(f"Error: libs directory not found at {base_path}")
        return

    print("=" * 60)
    print("Duplicate Code Scanner for Django Libs Monorepo")
    print("=" * 60)
    print()

    scanner = DuplicateScanner(base_path)
    scanner.scan_all_packages()

    print()
    print("Finding duplicates...")
    duplicates = scanner.find_duplicates()

    print(f"Found {len(duplicates)} duplicate symbols")
    print()

    # Generate report
    report = scanner.generate_markdown_report(duplicates)

    # Save to DUPLICATE_AUDIT.md
    output_path = base_path / "DUPLICATE_AUDIT.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {output_path}")
    print()
    print("=" * 60)
    print("Scan complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
