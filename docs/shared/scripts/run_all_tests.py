#!/usr/bin/env python3
"""
Script to run all tests for both websites (structa.cloud and ctc-research.com)
and verify test count parity between both projects.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TestRunner:
    """Run tests for both websites and verify parity."""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.ctc_dir = self.base_dir / "ctc-research.com"
        self.structa_dir = self.base_dir / "structa.cloud"
        self.results = {
            "ctc-research": {"passed": 0, "failed": 0, "skipped": 0, "total": 0, "test_files": 0},
            "structa.cloud": {"passed": 0, "failed": 0, "skipped": 0, "total": 0, "test_files": 0}
        }

    def run_tests_for_project(self, project_name: str, project_dir: Path) -> bool:
        """Run tests for a specific project."""
        print(f"\n{'='*60}")
        print(f"Running tests for {project_name}")
        print(f"{'='*60}")

        if not project_dir.exists():
            print(f"Error: Project directory not found: {project_dir}")
            return False

        os.chdir(project_dir)

        try:
            # Run pytest with verbose output and capture results
            cmd = ["uv", "run", "pytest", "tests/", "-v", "--tb=short"]
            print(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse pytest output
            self.parse_pytest_output(project_name, result.stdout, result.stderr)

            # Print summary
            print(f"\nTest Summary for {project_name}:")
            print(f"  Passed: {self.results[project_name]['passed']}")
            print(f"  Failed: {self.results[project_name]['failed']}")
            print(f"  Skipped: {self.results[project_name]['skipped']}")
            print(f"  Total: {self.results[project_name]['total']}")
            print(f"  Test Files: {self.results[project_name]['test_files']}")

            if result.returncode == 0:
                print(f"✓ All tests passed for {project_name}")
                return True
            else:
                print(f"✗ Some tests failed for {project_name}")
                if result.stderr:
                    print(f"Stderr: {result.stderr[:500]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"✗ Test execution timed out for {project_name}")
            return False
        except Exception as e:
            print(f"✗ Error running tests for {project_name}: {e}")
            return False
        finally:
            os.chdir(self.base_dir)

    def parse_pytest_output(self, project_name: str, stdout: str, stderr: str):
        """Parse pytest output to extract test counts."""
        # Count test files
        test_files = len(list(Path(project_name).glob("tests/**/*.py")))
        self.results[project_name]["test_files"] = test_files

        # Parse summary line like: "=== 8 passed, 4 skipped in 1.23s ==="
        summary_pattern = r"=== (\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?(?:, (\d+) errors)? in"

        for line in stdout.split('\n'):
            if "===" in line and ("passed" in line or "failed" in line):
                match = re.search(summary_pattern, line)
                if match:
                    passed = int(match.group(1) or 0)
                    failed = int(match.group(2) or 0)
                    skipped = int(match.group(3) or 0)
                    # errors = int(match.group(4) or 0)

                    self.results[project_name]["passed"] = passed
                    self.results[project_name]["failed"] = failed
                    self.results[project_name]["skipped"] = skipped
                    self.results[project_name]["total"] = passed + failed + skipped
                    break

        # If no summary found, try to count from test results
        if self.results[project_name]["total"] == 0:
            passed = stdout.count("PASSED")
            failed = stdout.count("FAILED")
            skipped = stdout.count("SKIPPED")
            self.results[project_name]["passed"] = passed
            self.results[project_name]["failed"] = failed
            self.results[project_name]["skipped"] = skipped
            self.results[project_name]["total"] = passed + failed + skipped

    def verify_test_parity(self) -> bool:
        """Verify that both websites have similar test counts."""
        print(f"\n{'='*60}")
        print("Verifying Test Parity")
        print(f"{'='*60}")

        ctc = self.results["ctc-research"]
        structa = self.results["structa.cloud"]

        print(f"ctc-research.com: {ctc['total']} total tests ({ctc['passed']} passed, {ctc['failed']} failed, {ctc['skipped']} skipped)")
        print(f"structa.cloud: {structa['total']} total tests ({structa['passed']} passed, {structa['failed']} failed, {structa['skipped']} skipped)")

        parity_issues = []

        # Check if both have tests
        if ctc['total'] == 0:
            parity_issues.append("ctc-research.com has no tests")
        if structa['total'] == 0:
            parity_issues.append("structa.cloud has no tests")

        # Check for significant disparity (more than 50% difference)
        if ctc['total'] > 0 and structa['total'] > 0:
            ratio = max(ctc['total'], structa['total']) / min(ctc['total'], structa['total'])
            if ratio > 1.5:  # More than 50% difference
                parity_issues.append(f"Test count disparity too high: {ctc['total']} vs {structa['total']} (ratio: {ratio:.2f})")

        # Check if both have similar test file counts
        if abs(ctc['test_files'] - structa['test_files']) > 5:
            parity_issues.append(f"Test file count disparity: {ctc['test_files']} vs {structa['test_files']}")

        if parity_issues:
            print("\n✗ Test parity issues found:")
            for issue in parity_issues:
                print(f"  - {issue}")
            return False
        else:
            print("\n✓ Test parity verified")
            return True

    def run_package_tests(self) -> bool:
        """Run tests for all packages."""
        print(f"\n{'='*60}")
        print("Running Package Tests")
        print(f"{'='*60}")

        packages = [
            ("django_fusion", "venv/libs/django-fusion"),
            ("crafts_ai", "venv/libs/crafts-ai"),
            ("django_fusion", "venv/libs/django-fusion"),
            ("crafts_ai", "applications/libs/crafts-ai")
        ]

        all_passed = True

        for package_name, package_path in packages:
            package_dir = self.base_dir / package_path
            if not package_dir.exists():
                print(f"Warning: Package directory not found: {package_dir}")
                continue

            print(f"\nRunning tests for {package_name}...")
            os.chdir(package_dir)

            try:
                cmd = ["uv", "run", "pytest", "tests/", "-v", "--tb=short"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180  # 3 minute timeout per package
                )

                if result.returncode == 0:
                    print(f"✓ All tests passed for {package_name}")
                else:
                    print(f"✗ Some tests failed for {package_name}")
                    all_passed = False
                    if result.stdout:
                        print(f"Output: {result.stdout[-500:]}")

            except subprocess.TimeoutExpired:
                print(f"✗ Test execution timed out for {package_name}")
                all_passed = False
            except Exception as e:
                print(f"✗ Error running tests for {package_name}: {e}")
                all_passed = False
            finally:
                os.chdir(self.base_dir)

        return all_passed

    def generate_report(self) -> Dict:
        """Generate a comprehensive test report."""
        report = {
            "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
            "projects": self.results,
            "summary": {
                "all_projects_passed": self.results["ctc-research"]["failed"] == 0 and self.results["structa.cloud"]["failed"] == 0,
                "test_parity_verified": self.verify_test_parity(),
                "total_tests": self.results["ctc-research"]["total"] + self.results["structa.cloud"]["total"],
                "total_passed": self.results["ctc-research"]["passed"] + self.results["structa.cloud"]["passed"],
                "total_failed": self.results["ctc-research"]["failed"] + self.results["structa.cloud"]["failed"],
                "total_skipped": self.results["ctc-research"]["skipped"] + self.results["structa.cloud"]["skipped"]
            }
        }

        return report

    def save_report(self, report: Dict):
        """Save test report to file."""
        report_file = self.base_dir / "TEST_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nTest report saved to: {report_file}")

    def run(self) -> bool:
        """Main execution method."""
        print("="*60)
        print("Running All Tests for Both Websites")
        print("="*60)

        # Run package tests first
        packages_passed = self.run_package_tests()
        if not packages_passed:
            print("\n✗ Some package tests failed")
            # Continue with project tests anyway

        # Run project tests
        ctc_passed = self.run_tests_for_project("ctc-research", self.ctc_dir)
        structa_passed = self.run_tests_for_project("structa.cloud", self.structa_dir)

        # Verify test parity
        parity_verified = self.verify_test_parity()

        # Generate report
        report = self.generate_report()
        self.save_report(report)

        # Overall success
        overall_success = (
            packages_passed and
            ctc_passed and
            structa_passed and
            parity_verified
        )

        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Package Tests: {'✓ PASSED' if packages_passed else '✗ FAILED'}")
        print(f"ctc-research.com Tests: {'✓ PASSED' if ctc_passed else '✗ FAILED'}")
        print(f"structa.cloud Tests: {'✓ PASSED' if structa_passed else '✗ FAILED'}")
        print(f"Test Parity: {'✓ VERIFIED' if parity_verified else '✗ NOT VERIFIED'}")
        print(f"\nOverall: {'✓ ALL TESTS PASSED AND PARITY VERIFIED' if overall_success else '✗ SOME TESTS FAILED OR PARITY ISSUES'}")

        return overall_success


def main():
    """Main entry point."""
    runner = TestRunner()

    try:
        success = runner.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
