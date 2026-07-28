#!/usr/bin/env python3
"""
Script to verify test parity between structa.cloud and ctc-research.com
Ensures both websites have similar test counts and coverage.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TestParityVerifier:
    """Verify test parity between two projects."""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.ctc_dir = self.base_dir / "ctc-research.com"
        self.structa_dir = self.base_dir / "structa.cloud"

    def count_tests_in_project(self, project_name: str, project_dir: Path) -> Dict:
        """Count tests in a project using pytest discovery."""
        print(f"Counting tests in {project_name}...")

        if not project_dir.exists():
            print(f"Error: Project directory not found: {project_dir}")
            return {"total": 0, "files": 0, "modules": 0}

        os.chdir(project_dir)

        try:
            # Use pytest to discover tests without running them
            cmd = ["uv", "run", "pytest", "tests/", "--collect-only", "-q"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse output to count tests
            test_count = 0
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('='):
                    test_count += 1

            # Count test files
            test_files = len(list(Path("tests").glob("**/*.py")))

            # Count test modules (files with test_ prefix or Test class)
            test_modules = 0
            for test_file in Path("tests").glob("**/*.py"):
                with open(test_file, 'r') as f:
                    content = f.read()
                    if "def test_" in content or "class Test" in content:
                        test_modules += 1

            os.chdir(self.base_dir)

            return {
                "total": test_count,
                "files": test_files,
                "modules": test_modules,
                "discovery_output": result.stdout[:500] if result.stdout else ""
            }

        except Exception as e:
            print(f"Error counting tests for {project_name}: {e}")
            os.chdir(self.base_dir)
            return {"total": 0, "files": 0, "modules": 0}

    def analyze_test_structure(self, project_name: str, project_dir: Path) -> Dict:
        """Analyze test structure and categories."""
        print(f"Analyzing test structure for {project_name}...")

        if not project_dir.exists():
            return {"categories": {}, "test_types": {}}

        os.chdir(project_dir)

        categories = {}
        test_types = {"unit": 0, "integration": 0, "functional": 0}

        try:
            # Look for test files and categorize them
            for test_file in Path("tests").glob("**/*.py"):
                rel_path = str(test_file.relative_to("tests"))

                # Categorize by directory
                category = "root"
                if "/" in rel_path:
                    category = rel_path.split("/")[0]

                categories[category] = categories.get(category, 0) + 1

                # Try to determine test type from filename or content
                filename = test_file.name.lower()
                if "integration" in filename or "integration" in rel_path.lower():
                    test_types["integration"] += 1
                elif "functional" in filename or "functional" in rel_path.lower():
                    test_types["functional"] += 1
                else:
                    test_types["unit"] += 1

            os.chdir(self.base_dir)

            return {
                "categories": categories,
                "test_types": test_types
            }

        except Exception as e:
            print(f"Error analyzing test structure for {project_name}: {e}")
            os.chdir(self.base_dir)
            return {"categories": {}, "test_types": {}}

    def compare_test_counts(self, ctc_stats: Dict, structa_stats: Dict) -> List[str]:
        """Compare test counts and return issues."""
        issues = []

        # Compare total test counts
        ctc_total = ctc_stats["total"]
        structa_total = structa_stats["total"]

        if ctc_total == 0:
            issues.append("ctc-research.com has no discovered tests")
        if structa_total == 0:
            issues.append("structa.cloud has no discovered tests")

        if ctc_total > 0 and structa_total > 0:
            ratio = max(ctc_total, structa_total) / min(ctc_total, structa_total)
            if ratio > 2.0:  # More than 100% difference
                issues.append(f"Test count disparity too high: {ctc_total} vs {structa_total} (ratio: {ratio:.2f})")

        # Compare test file counts
        ctc_files = ctc_stats["files"]
        structa_files = structa_stats["files"]

        if abs(ctc_files - structa_files) > 10:
            issues.append(f"Test file count disparity: {ctc_files} vs {structa_files}")

        # Compare test module counts
        ctc_modules = ctc_stats["modules"]
        structa_modules = structa_stats["modules"]

        if abs(ctc_modules - structa_modules) > 5:
            issues.append(f"Test module count disparity: {ctc_modules} vs {structa_modules}")

        return issues

    def compare_test_structure(self, ctc_structure: Dict, structa_structure: Dict) -> List[str]:
        """Compare test structure and return issues."""
        issues = []

        # Compare test categories
        ctc_cats = set(ctc_structure["categories"].keys())
        structa_cats = set(structa_structure["categories"].keys())

        missing_in_structa = ctc_cats - structa_cats
        missing_in_ctc = structa_cats - ctc_cats

        if missing_in_structa:
            issues.append(f"Test categories missing in structa.cloud: {missing_in_structa}")
        if missing_in_ctc:
            issues.append(f"Test categories missing in ctc-research.com: {missing_in_ctc}")

        # Compare test type distribution
        ctc_types = ctc_structure["test_types"]
        structa_types = structa_structure["test_types"]

        for test_type in ["unit", "integration", "functional"]:
            ctc_count = ctc_types.get(test_type, 0)
            structa_count = structa_types.get(test_type, 0)

            if ctc_count > 0 and structa_count == 0:
                issues.append(f"{test_type.title()} tests missing in structa.cloud")
            elif structa_count > 0 and ctc_count == 0:
                issues.append(f"{test_type.title()} tests missing in ctc-research.com")

        return issues

    def run(self) -> bool:
        """Main execution method."""
        print("="*60)
        print("Verifying Test Parity Between Websites")
        print("="*60)

        # Count tests in both projects
        ctc_stats = self.count_tests_in_project("ctc-research.com", self.ctc_dir)
        structa_stats = self.count_tests_in_project("structa.cloud", self.structa_dir)

        # Analyze test structure
        ctc_structure = self.analyze_test_structure("ctc-research.com", self.ctc_dir)
        structa_structure = self.analyze_test_structure("structa.cloud", self.structa_dir)

        # Print statistics
        print(f"\nTest Statistics:")
        print(f"ctc-research.com: {ctc_stats['total']} tests, {ctc_stats['files']} files, {ctc_stats['modules']} modules")
        print(f"structa.cloud: {structa_stats['total']} tests, {structa_stats['files']} files, {structa_stats['modules']} modules")

        print(f"\nTest Categories:")
        print(f"ctc-research.com: {ctc_structure['categories']}")
        print(f"structa.cloud: {structa_structure['categories']}")

        print(f"\nTest Types:")
        print(f"ctc-research.com: {ctc_structure['test_types']}")
        print(f"structa.cloud: {structa_structure['test_types']}")

        # Compare and find issues
        count_issues = self.compare_test_counts(ctc_stats, structa_stats)
        structure_issues = self.compare_test_structure(ctc_structure, structa_structure)

        all_issues = count_issues + structure_issues

        if all_issues:
            print(f"\n✗ Test parity issues found ({len(all_issues)}):")
            for issue in all_issues:
                print(f"  - {issue}")

            # Generate recommendations
            print(f"\nRecommendations:")
            if ctc_stats["total"] < structa_stats["total"]:
                print(f"  - Add {structa_stats['total'] - ctc_stats['total']} tests to ctc-research.com")
            elif structa_stats["total"] < ctc_stats["total"]:
                print(f"  - Add {ctc_stats['total'] - structa_stats['total']} tests to structa.cloud")

            # Check for missing categories
            ctc_cats = set(ctc_structure["categories"].keys())
            structa_cats = set(structa_structure["categories"].keys())

            missing_cats = ctc_cats.symmetric_difference(structa_cats)
            if missing_cats:
                print(f"  - Align test categories: {missing_cats}")

            return False
        else:
            print(f"\n✓ Test parity verified")
            print(f"  - Both projects have similar test counts")
            print(f"  - Test structures are aligned")
            print(f"  - Test categories match")
            return True

    def generate_parity_report(self) -> Dict:
        """Generate a parity report."""
        ctc_stats = self.count_tests_in_project("ctc-research.com", self.ctc_dir)
        structa_stats = self.count_tests_in_project("structa.cloud", self.structa_dir)

        ctc_structure = self.analyze_test_structure("ctc-research.com", self.ctc_dir)
        structa_structure = self.analyze_test_structure("structa.cloud", self.structa_dir)

        count_issues = self.compare_test_counts(ctc_stats, structa_stats)
        structure_issues = self.compare_test_structure(ctc_structure, structa_structure)

        report = {
            "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
            "ctc_research": {
                "test_count": ctc_stats["total"],
                "file_count": ctc_stats["files"],
                "module_count": ctc_stats["modules"],
                "categories": ctc_structure["categories"],
                "test_types": ctc_structure["test_types"]
            },
            "structa_cloud": {
                "test_count": structa_stats["total"],
                "file_count": structa_stats["files"],
                "module_count": structa_stats["modules"],
                "categories": structa_structure["categories"],
                "test_types": structa_structure["test_types"]
            },
            "parity_issues": {
                "count_issues": count_issues,
                "structure_issues": structure_issues,
                "total_issues": len(count_issues) + len(structure_issues)
            },
            "parity_verified": len(count_issues) + len(structure_issues) == 0
        }

        return report

    def save_parity_report(self, report: Dict):
        """Save parity report to file."""
        report_file = self.base_dir / "TEST_PARITY_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nParity report saved to: {report_file}")


def main():
    """Main entry point."""
    verifier = TestParityVerifier()

    try:
        # Run verification
        parity_verified = verifier.run()

        # Generate and save report
        report = verifier.generate_parity_report()
        verifier.save_parity_report(report)

        sys.exit(0 if parity_verified else 1)
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
