#!/usr/bin/env python3
"""Cross-check RTK endpoint exports against page imports for POS frontends."""

from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Regex patterns ---------------------------------------------------------------

# Matches: export const { ... } = someApi;
DESTRUCTURED_EXPORT_RE = re.compile(
    r"export\s+const\s*\{\s*([^}]+)\s*\}\s*=\s*\w+Api",
    re.DOTALL | re.MULTILINE,
)

# Matches: export type/interface Foo {}
TYPE_EXPORT_RE = re.compile(
    r"export\s+(?:type|interface)\s+(\w+)",
    re.MULTILINE,
)

# Matches: export const Foo = ... / export function Foo ... / export class Foo ...
NAMED_EXPORT_RE = re.compile(
    r"export\s+(?:const|let|var|function|class|enum)\s+(\w+)",
    re.MULTILINE,
)

# Matches: export { Foo, Bar }
LIST_EXPORT_RE = re.compile(
    r"export\s*\{\s*([^}]+)\s*\}(?:\s*from\s*['\"][^'\"]+['\"])?",
    re.DOTALL | re.MULTILINE,
)

# Page imports from endpoint files: import { ... } from '../store/api/endpoints/NAME'
IMPORT_RE = re.compile(
    r"import\s+(?:type\s+)?\{\s*([^}]+)\s*\}\s+from\s+['\"]([^'\"]*store/api/endpoints/([^'\"]+))['\"]",
    re.DOTALL | re.MULTILINE,
)


def split_names(text: str) -> set[str]:
    """Split a comma-separated list of identifiers, ignoring `as` aliases."""
    names: set[str] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        # Strip comments if any
        part = part.split("//")[0].strip()
        # Handle `Foo as Bar`
        if " as " in part:
            part = part.split(" as ")[0].strip()
        names.add(part)
    return names


def extract_endpoint_exports(file_path: Path) -> set[str]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    names: set[str] = set()

    for m in DESTRUCTURED_EXPORT_RE.finditer(content):
        names.update(split_names(m.group(1)))

    for m in TYPE_EXPORT_RE.finditer(content):
        names.add(m.group(1))

    for m in NAMED_EXPORT_RE.finditer(content):
        names.add(m.group(1))

    for m in LIST_EXPORT_RE.finditer(content):
        names.update(split_names(m.group(1)))

    return names


def extract_page_imports(file_path: Path) -> list[tuple[str, set[str]]]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    results: list[tuple[str, set[str]]] = []
    for m in IMPORT_RE.finditer(content):
        imported = m.group(1)
        endpoint_name = m.group(3)
        results.append((endpoint_name, split_names(imported)))
    return results


def audit_edition(edition_dir: Path) -> dict:
    endpoints_dir = edition_dir / "src" / "store" / "api" / "endpoints"
    pages_dir = edition_dir / "src" / "pages"

    # Endpoint file -> exported names
    endpoint_exports: dict[str, set[str]] = {}
    endpoint_files = sorted(endpoints_dir.glob("*.ts"))
    for ep in endpoint_files:
        endpoint_exports[ep.stem] = extract_endpoint_exports(ep)

    # Collect all exported names across files to detect duplicates
    name_to_files: dict[str, list[str]] = defaultdict(list)
    for stem, names in endpoint_exports.items():
        for n in names:
            name_to_files[n].append(stem)

    # Page file -> imports
    page_imports: dict[str, list[tuple[str, set[str]]]] = {}
    for page in sorted(pages_dir.glob("*.tsx")):
        page_imports[page.name] = extract_page_imports(page)

    # Cross-check
    mismatches: list[dict] = []
    for page_name, imports in page_imports.items():
        for endpoint_name, names in imports:
            if endpoint_name not in endpoint_exports:
                mismatches.append({
                    "page": page_name,
                    "endpoint": endpoint_name,
                    "type": "missing_endpoint",
                    "names": sorted(names),
                })
                continue
            available = endpoint_exports[endpoint_name]
            missing = [n for n in names if n not in available]
            if missing:
                mismatches.append({
                    "page": page_name,
                    "endpoint": endpoint_name,
                    "type": "missing_export",
                    "names": missing,
                })

    # Find names exported by multiple endpoint files
    duplicates = {n: files for n, files in name_to_files.items() if len(files) > 1}

    # Find exports never imported by any page
    imported_names: set[str] = set()
    for imports in page_imports.values():
        for _, names in imports:
            imported_names.update(names)

    unused: dict[str, list[str]] = defaultdict(list)
    for stem, names in endpoint_exports.items():
        for n in names:
            if n not in imported_names:
                unused[stem].append(n)

    return {
        "edition": edition_dir.name,
        "endpoint_exports": {k: sorted(v) for k, v in endpoint_exports.items()},
        "duplicates": {k: v for k, v in sorted(duplicates.items(), key=lambda x: x[0])},
        "mismatches": mismatches,
        "unused": {k: v for k, v in sorted(unused.items()) if v},
    }


def main() -> None:
    editions = ["pos-solo", "pos-full"]
    for edition in editions:
        edition_dir = ROOT / edition
        if not edition_dir.exists():
            print(f"## {edition}: not found\n")
            continue
        result = audit_edition(edition_dir)
        print(f"## Edition: {result['edition']}")
        print()
        if result["mismatches"]:
            print(f"### ❌ Mismatches ({len(result['mismatches'])})")
            for m in result["mismatches"]:
                if m["type"] == "missing_endpoint":
                    print(f"- `{m['page']}` imports `{', '.join(m['names'])}` from missing endpoint `{m['endpoint']}`")
                else:
                    print(f"- `{m['page']}` imports `{', '.join(m['names'])}` from `{m['endpoint']}` but they are not exported there")
            print()
        else:
            print("### ✅ No mismatched imports found")
            print()

        if result["duplicates"]:
            print(f"### ⚠️ Duplicate exports across endpoint files")
            for name, files in result["duplicates"].items():
                print(f"- `{name}` exported by: {', '.join(files)}")
            print()

        if result["unused"]:
            print(f"### ℹ️ Exports never imported by any page (possible dead code)")
            for stem, names in result["unused"].items():
                print(f"- `{stem}.ts`: {', '.join(names)}")
            print()


if __name__ == "__main__":
    main()
