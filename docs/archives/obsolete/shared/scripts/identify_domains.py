#!/usr/bin/env python3
"""
Domain Identifier for Ecosystem Architectural Refactoring

This script analyzes code to identify domain boundaries and detects cross-domain leakage.
It identifies modules that mix multiple domains and suggests how to split them.
"""

import ast
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class CrossDomainLeak:
    """Represents a module that mixes multiple domains."""
    module_path: str
    primary_domain: str
    leaked_domains: List[str]
    leaked_symbols: List[str]


class DomainIdentifier:
    """Analyzes code to identify domain boundaries and responsibilities."""

    DOMAIN_KEYWORDS = {
        "accounts": ["user", "auth", "login", "signup", "role", "permission", "group", "person"],
        "content": ["page", "post", "article", "cms", "wagtail", "blog", "content"],
        "lms": ["course", "lesson", "enrollment", "progress", "certificate", "lms"],
        "alliance": ["course", "lesson", "enrollment", "progress", "certificate", "alliance"],
        "messaging": ["message", "notification", "email", "chat", "messaging"],
        "cart": ["cart", "checkout", "order", "payment", "purchase"],
        "forms": ["form", "submission", "field", "validation"],
    }

    def __init__(self):
        self.domain_cache: Dict[str, str] = {}
        self.cross_domain_leaks: List[CrossDomainLeak] = []

    def identify_domain(self, module_path: str) -> str:
        """Identify which domain a module belongs to based on path and content."""
        # Check cache first
        if module_path in self.domain_cache:
            return self.domain_cache[module_path]

        # Check path-based domain identification
        path_lower = module_path.lower()
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if f"/{domain}/" in path_lower or f"\\{domain}\\" in path_lower:
                    self.domain_cache[module_path] = domain
                    return domain

        # If no domain found in path, return "unknown"
        self.domain_cache[module_path] = "unknown"
        return "unknown"

    def detect_cross_domain_leakage(self, directory: str) -> List[CrossDomainLeak]:
        """Detect modules that mix multiple domains."""
        leaks = []
        directory = Path(directory)

        for py_file in directory.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            module_path = str(py_file)
            primary_domain = self.identify_domain(module_path)

            if primary_domain == "unknown":
                continue

            # Extract symbols and their domains
            leaked_domains = set()
            leaked_symbols = []

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, FileNotFoundError):
                continue

            # Check for imports from other domains
            for domain, keywords in self.DOMAIN_KEYWORDS.items():
                if domain == primary_domain:
                    continue

                for keyword in keywords:
                    # Look for imports or references to other domains
                    patterns = [
                        rf"from\s+.*{keyword}.*import",
                        rf"import\s+.*{keyword}",
                        rf"class\s+\w*{keyword.capitalize()}\w*",
                        rf"def\s+\w*{keyword}\w*",
                    ]

                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            leaked_domains.add(domain)
                            leaked_symbols.append(match.group(0))

            if leaked_domains:
                leaks.append(CrossDomainLeak(
                    module_path=module_path,
                    primary_domain=primary_domain,
                    leaked_domains=list(leaked_domains),
                    leaked_symbols=leaked_symbols[:5]  # Limit to first 5 symbols
                ))

        self.cross_domain_leaks = leaks
        return leaks

    def suggest_split(self, module_path: str) -> List[Dict]:
        """Suggest how to split a multi-domain module."""
        suggestions = []

        # Find the leak for this module
        leak = None
        for l in self.cross_domain_leaks:
            if l.module_path == module_path:
                leak = l
                break

        if not leak:
            return suggestions

        # Suggest splitting into separate files
        base_path = Path(module_path).parent
        base_name = Path(module_path).stem

        for domain in leak.leaked_domains:
            new_path = base_path / f"{base_name}_{domain}.py"
            suggestions.append({
                "original_module": module_path,
                "target_domain": domain,
                "new_module_path": str(new_path),
                "symbols_to_move": leak.leaked_symbols
            })

        return suggestions

    def _should_skip_file(self, filepath: Path) -> bool:
        """Determine if a file should be skipped from analysis."""
        skip_patterns = [
            "__pycache__",
            "migrations",
            "test",
            "tests",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis",
            ".venv",
            "node_modules"
        ]

        file_str = str(filepath)
        return any(pattern in file_str for pattern in skip_patterns)


def main():
    """Main function to run domain identifier."""
    import argparse

    parser = argparse.ArgumentParser(description='Detect cross-domain leakage')
    parser.add_argument('directory', help='Directory to scan for cross-domain leakage')
    parser.add_argument('--output', '-o', help='Output file for leaks')

    args = parser.parse_args()

    identifier = DomainIdentifier()
    print(f"Scanning {args.directory} for cross-domain leakage...")
    leaks = identifier.detect_cross_domain_leakage(args.directory)

    if leaks:
        print(f"\nFound {len(leaks)} modules with cross-domain leakage:")
        for i, leak in enumerate(leaks, 1):
            print(f"\n{i}. {leak.module_path}")
            print(f"   Primary domain: {leak.primary_domain}")
            print(f"   Leaked domains: {', '.join(leak.leaked_domains)}")
            print(f"   Sample symbols: {', '.join(leak.leaked_symbols[:3])}")

        # Write to file if output specified
        if args.output:
            with open(args.output, 'w') as f:
                f.write("# Cross-Domain Leakage Report\n\n")
                for i, leak in enumerate(leaks, 1):
                    f.write(f"## {i}. {leak.module_path}\n")
                    f.write(f"**Primary Domain:** {leak.primary_domain}\n\n")
                    f.write(f"**Leaked Domains:** {', '.join(leak.leaked_domains)}\n\n")
                    f.write(f"**Sample Symbols:**\n")
                    for symbol in leak.leaked_symbols[:5]:
                        f.write(f"- {symbol}\n")
                    f.write("\n")
    else:
        print("No cross-domain leakage detected!")


if __name__ == "__main__":
    main()
