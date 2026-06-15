"""
ParserDetector: Scans the ecosystem for all custom parsers and serializers.

A "parser" is a function/class that takes a string/bytes input and returns a structured object.
A "serializer" is a function/class that takes a structured object and returns a string/bytes.

Looks for:
- Classes named *Parser, *Serializer, *Decoder, *Encoder
- Functions named parse_*, serialize_*, from_string, to_string, loads, dumps
- Django REST Framework serializers
- Pydantic models with parse methods
- Marshmallow/Ninja schemas
"""

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

SCAN_DIRS = [
    "ctc-research.com/apps",
    "structa.cloud/apps",
    "venv/libs/django-osoul/src",
    "venv/libs/django-rseal/src",
    "venv/libs/django-grep/src",
    "venv/libs/nawaai/crafts_ai",
]

# Class name patterns that indicate a parser
PARSER_CLASS_PATTERNS = re.compile(
    r"^(\w*(Parser|Decoder)\w*)$", re.IGNORECASE
)

# Class name patterns that indicate a serializer
SERIALIZER_CLASS_PATTERNS = re.compile(
    r"^(\w*(Serializer|Encoder)\w*)$", re.IGNORECASE
)

# Function name patterns for parsers
PARSER_FUNC_PATTERNS = re.compile(
    r"^(parse_\w+|from_string|loads)$"
)

# Function name patterns for serializers
SERIALIZER_FUNC_PATTERNS = re.compile(
    r"^(serialize_\w+|to_string|dumps)$"
)

# Base classes that indicate a schema/serializer
SCHEMA_BASE_CLASSES = {
    "Schema",          # Ninja/marshmallow
    "BaseModel",       # Pydantic
    "Serializer",      # DRF
    "ModelSerializer", # DRF
}


@dataclass
class ParserInfo:
    """Information about a discovered parser or serializer."""
    name: str
    kind: str  # "parser", "serializer", "schema", "encoder"
    file_path: str
    line_number: int
    input_type: str
    output_type: str
    has_pretty_printer: bool = False
    pretty_printer_name: Optional[str] = None
    docstring: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)


@dataclass
class ParserInventory:
    """Complete inventory of parsers and serializers."""
    parsers: List[ParserInfo] = field(default_factory=list)
    serializers: List[ParserInfo] = field(default_factory=list)
    schemas: List[ParserInfo] = field(default_factory=list)

    @property
    def all_items(self) -> List[ParserInfo]:
        return self.parsers + self.serializers + self.schemas


class ParserDetector:
    """
    Scans the ecosystem for all custom parsers and serializers.

    Detects:
    - Custom parser classes (*Parser, *Decoder)
    - Custom serializer classes (*Serializer, *Encoder)
    - Ninja/marshmallow Schema subclasses
    - Pydantic BaseModel subclasses (in schema files)
    - Standalone parse_*/serialize_* functions
    """

    def __init__(self, scan_dirs: Optional[List[str]] = None):
        self.scan_dirs = scan_dirs or SCAN_DIRS
        self.inventory = ParserInventory()

    def find_all_parsers(self) -> List[ParserInfo]:
        """Find all parsers across the codebase."""
        self._scan_all()
        return self.inventory.parsers

    def find_all_serializers(self) -> List[ParserInfo]:
        """Find all serializers across the codebase."""
        self._scan_all()
        return self.inventory.serializers

    def get_full_inventory(self) -> ParserInventory:
        """Get the complete inventory of parsers and serializers."""
        self._scan_all()
        return self.inventory

    def _scan_all(self):
        """Scan all configured directories."""
        # Reset to avoid double-counting
        self.inventory = ParserInventory()

        for scan_dir in self.scan_dirs:
            if not os.path.exists(scan_dir):
                continue
            for root, dirs, files in os.walk(scan_dir):
                # Skip non-source directories
                dirs[:] = [
                    d for d in dirs
                    if d not in ("__pycache__", ".git", "migrations", "node_modules")
                ]
                for filename in files:
                    if not filename.endswith(".py"):
                        continue
                    filepath = os.path.join(root, filename)
                    self._scan_file(filepath)

    def _scan_file(self, filepath: str):
        """Scan a single Python file for parsers and serializers."""
        try:
            source = Path(filepath).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=filepath)
        except (SyntaxError, UnicodeDecodeError):
            return

        # Collect all class and function definitions at module level and nested
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._process_class(node, filepath, source)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node, filepath)

    def _get_base_class_names(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names from a class definition."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.attr}")
        return bases

    def _get_docstring(self, node) -> Optional[str]:
        """Extract docstring from a node."""
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            return node.body[0].value.value.strip()
        return None

    def _infer_input_output(self, node: ast.ClassDef, kind: str) -> tuple:
        """Infer input/output types from class structure."""
        if kind == "parser":
            return ("str", "structured object")
        elif kind == "serializer":
            return ("structured object", "str")
        elif kind == "schema":
            return ("dict/JSON", "validated object")
        elif kind == "encoder":
            return ("object", "JSON str")
        return ("unknown", "unknown")

    def _process_class(self, node: ast.ClassDef, filepath: str, source: str):
        """Process a class definition to detect parsers/serializers."""
        name = node.name
        bases = self._get_base_class_names(node)
        docstring = self._get_docstring(node)
        line = node.lineno

        # Check if it's a parser class by name
        if PARSER_CLASS_PATTERNS.match(name):
            # Exclude third-party base classes (e.g., ArgumentParser)
            if not self._is_third_party_parser(name, bases):
                info = ParserInfo(
                    name=name,
                    kind="parser",
                    file_path=filepath,
                    line_number=line,
                    input_type="str",
                    output_type="structured object",
                    docstring=docstring,
                    base_classes=bases,
                )
                self._check_pretty_printer(info, node, source)
                self.inventory.parsers.append(info)
            return

        # Check if it's a serializer/encoder class by name
        if SERIALIZER_CLASS_PATTERNS.match(name):
            info = ParserInfo(
                name=name,
                kind="serializer",
                file_path=filepath,
                line_number=line,
                input_type="structured object",
                output_type="str/bytes",
                docstring=docstring,
                base_classes=bases,
            )
            self.inventory.serializers.append(info)
            return

        # Check if it's a schema (Ninja Schema, marshmallow, Pydantic)
        schema_bases = set(bases) & SCHEMA_BASE_CLASSES
        if schema_bases and self._is_schema_file(filepath):
            info = ParserInfo(
                name=name,
                kind="schema",
                file_path=filepath,
                line_number=line,
                input_type="dict/JSON",
                output_type="validated object",
                docstring=docstring,
                base_classes=bases,
            )
            self.inventory.schemas.append(info)

    def _is_third_party_parser(self, name: str, bases: List[str]) -> bool:
        """Check if this is a third-party parser we should skip."""
        third_party = {"ArgumentParser", "ConfigParser", "HTMLParser", "XMLParser"}
        if name in third_party:
            return True
        # Skip if it inherits from known third-party parsers
        if any(b in third_party for b in bases):
            return True
        return False

    def _is_schema_file(self, filepath: str) -> bool:
        """Check if this file is a schema/serializer file."""
        path_lower = filepath.lower()
        return any(
            keyword in path_lower
            for keyword in ["schema", "serializer", "schemas"]
        )

    def _check_pretty_printer(self, info: ParserInfo, node: ast.ClassDef, source: str):
        """Check if a parser has a corresponding pretty printer."""
        # Look for pretty_print, to_string, serialize methods in the class
        for item in ast.walk(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fname = item.name
                if any(
                    keyword in fname.lower()
                    for keyword in ["pretty_print", "to_string", "serialize", "dumps", "format"]
                ):
                    info.has_pretty_printer = True
                    info.pretty_printer_name = fname
                    return

        # Also check if there's a standalone pretty_print function in the same file
        # by looking for functions named pretty_print_<parser_name> or similar
        parser_lower = info.name.lower().replace("parser", "").replace("_", "")
        pp_patterns = [
            f"pretty_print_{parser_lower}",
            f"format_{parser_lower}",
            f"serialize_{parser_lower}",
            f"{parser_lower}_to_string",
        ]
        for pattern in pp_patterns:
            if pattern in source.lower():
                info.has_pretty_printer = True
                info.pretty_printer_name = pattern
                return

    def _process_function(self, node, filepath: str):
        """Process a function definition to detect standalone parse/serialize functions."""
        name = node.name

        if PARSER_FUNC_PATTERNS.match(name):
            docstring = self._get_docstring(node)
            info = ParserInfo(
                name=name,
                kind="parser_function",
                file_path=filepath,
                line_number=node.lineno,
                input_type="str",
                output_type="structured object",
                docstring=docstring,
            )
            self.inventory.parsers.append(info)

        elif SERIALIZER_FUNC_PATTERNS.match(name):
            docstring = self._get_docstring(node)
            info = ParserInfo(
                name=name,
                kind="serializer_function",
                file_path=filepath,
                line_number=node.lineno,
                input_type="structured object",
                output_type="str",
                docstring=docstring,
            )
            self.inventory.serializers.append(info)


def generate_inventory_report(inventory: ParserInventory) -> str:
    """Generate a markdown report from the inventory."""
    lines = []
    lines.append("# Parser and Serializer Inventory")
    lines.append("")
    lines.append("Generated by `scripts/detect_parsers.py`")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Custom Parsers**: {len(inventory.parsers)}")
    lines.append(f"- **Custom Serializers**: {len(inventory.serializers)}")
    lines.append(f"- **Schemas (Ninja/Pydantic/marshmallow)**: {len(inventory.schemas)}")
    lines.append(f"- **Total**: {len(inventory.all_items)}")
    lines.append("")

    # Parsers
    if inventory.parsers:
        lines.append("## Custom Parsers")
        lines.append("")
        lines.append("| Name | File | Line | Input Type | Output Type | Has Pretty Printer |")
        lines.append("|------|------|------|------------|-------------|-------------------|")
        for p in inventory.parsers:
            pp = f"✅ `{p.pretty_printer_name}`" if p.has_pretty_printer else "❌ Missing"
            lines.append(
                f"| `{p.name}` | `{p.file_path}` | {p.line_number} "
                f"| {p.input_type} | {p.output_type} | {pp} |"
            )
        lines.append("")

    # Serializers
    if inventory.serializers:
        lines.append("## Custom Serializers / Encoders")
        lines.append("")
        lines.append("| Name | File | Line | Input Type | Output Type |")
        lines.append("|------|------|------|------------|-------------|")
        for s in inventory.serializers:
            lines.append(
                f"| `{s.name}` | `{s.file_path}` | {s.line_number} "
                f"| {s.input_type} | {s.output_type} |"
            )
        lines.append("")

    # Schemas
    if inventory.schemas:
        lines.append("## Schemas (Ninja / Pydantic / marshmallow)")
        lines.append("")
        lines.append("These are data validation schemas, not string parsers.")
        lines.append("They validate structured data (dicts/JSON) into typed objects.")
        lines.append("")
        lines.append("| Name | File | Line | Base Classes |")
        lines.append("|------|------|------|--------------|")
        for s in inventory.schemas:
            bases = ", ".join(s.base_classes) if s.base_classes else "—"
            lines.append(
                f"| `{s.name}` | `{s.file_path}` | {s.line_number} | {bases} |"
            )
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    detector = ParserDetector()
    inventory = detector.get_full_inventory()

    print(f"Found {len(inventory.parsers)} parsers")
    print(f"Found {len(inventory.serializers)} serializers")
    print(f"Found {len(inventory.schemas)} schemas")
    print()

    print("=== PARSERS ===")
    for p in inventory.parsers:
        pp = f"(pretty_printer: {p.pretty_printer_name})" if p.has_pretty_printer else "(NO pretty printer)"
        print(f"  {p.name} @ {p.file_path}:{p.line_number} {pp}")

    print()
    print("=== SERIALIZERS ===")
    for s in inventory.serializers:
        print(f"  {s.name} @ {s.file_path}:{s.line_number}")

    print()
    print("=== SCHEMAS (sample) ===")
    for s in inventory.schemas[:5]:
        print(f"  {s.name} @ {s.file_path}:{s.line_number}")
    if len(inventory.schemas) > 5:
        print(f"  ... and {len(inventory.schemas) - 5} more")
