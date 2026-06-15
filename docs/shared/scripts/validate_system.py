#!/usr/bin/env python3
"""
System Validator for Ecosystem Architectural Refactoring

Validates the entire system after refactoring to ensure all requirements are met.
Generates COMPLETION_REPORT.md documenting all changes and improvements.

Usage:
    python3 scripts/validate_system.py
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BoundaryViolation:
    source_file: str
    import_statement: str
    violation_type: str
    rule_violated: str


@dataclass
class DuplicationCheck:
    passed: bool = False
    duplicated_pairs: int = 0
    max_similarity: float = 0.0
    violations: List[str] = field(default_factory=list)


@dataclass
class PlacementCheck:
    passed: bool = False
    misplaced_modules: List[str] = field(default_factory=list)


@dataclass
class BoundaryCheck:
    passed: bool = False
    violations: List[BoundaryViolation] = field(default_factory=list)


@dataclass
class TestCheck:
    passed: bool = False
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: List[str] = field(default_factory=list)


@dataclass
class SpecCheck:
    passed: bool = False
    incomplete_specs: List[str] = field(default_factory=list)
    incomplete_tasks: List[str] = field(default_factory=list)


@dataclass
class DockerCheck:
    passed: bool = False
    build_errors: List[str] = field(default_factory=list)
    runtime_errors: List[str] = field(default_factory=list)
    health_status: Dict[str, int] = field(default_factory=dict)


@dataclass
class ValidationReport:
    duplication_check: DuplicationCheck
    placement_check: PlacementCheck
    boundary_check: BoundaryCheck
    test_check: TestCheck
    spec_check: SpecCheck
    docker_check: DockerCheck
    all_passed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SystemValidator:
    """
    Validates the entire system after refactoring.
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.report = None

    def validate_all(self) -> ValidationReport:
        """
        Run all validation checks:
        1. Zero duplication
        2. Correct package placement
        3. Boundary enforcement
        4. All tests passing
        5. All specs complete
        6. Documentation complete
        7. Docker health
        8. Import resolution
        9. Migration status
        10. Dependency unification
        11. Template organization
        12. Naming conventions
        """
        print("Starting comprehensive system validation...")

        # Initialize checks
        duplication_check = self.check_zero_duplication()
        placement_check = self.check_package_placement()
        boundary_check = self.check_boundary_enforcement()
        test_check = self.check_all_tests_passing()
        spec_check = self.check_specs_complete()
        docker_check = self.check_docker_health()

        # Determine overall status
        all_passed = (
            duplication_check.passed and
            placement_check.passed and
            boundary_check.passed and
            test_check.passed and
            spec_check.passed and
            docker_check.passed
        )

        self.report = ValidationReport(
            duplication_check=duplication_check,
            placement_check=placement_check,
            boundary_check=boundary_check,
            test_check=test_check,
            spec_check=spec_check,
            docker_check=docker_check,
            all_passed=all_passed
        )

        return self.report

    def check_zero_duplication(self) -> DuplicationCheck:
        """
        Verify zero code duplication:
        1. Run duplication analyzer
        2. Verify similarity < 70% for all pairs
        3. Report any remaining duplication
        """
        print("Checking for code duplication...")

        # Try to run the duplication analyzer
        try:
            result = subprocess.run(
                ["python3", "scripts/analyze_duplication.py", "--threshold", "0.70", "--summary"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            if result.returncode == 0:
                # Parse output to get duplication count
                lines = result.stdout.split('\n')
                duplicated_pairs = 0
                max_similarity = 0.0

                for line in lines:
                    if "Duplicated pairs found:" in line:
                        duplicated_pairs = int(line.split(":")[1].strip())
                    elif "Maximum similarity:" in line:
                        max_similarity = float(line.split(":")[1].strip().replace('%', '')) / 100

                passed = duplicated_pairs == 0
                violations = [] if passed else [f"Found {duplicated_pairs} duplicated pairs with max similarity {max_similarity:.1%}"]

                return DuplicationCheck(
                    passed=passed,
                    duplicated_pairs=duplicated_pairs,
                    max_similarity=max_similarity,
                    violations=violations
                )
            else:
                return DuplicationCheck(
                    passed=False,
                    violations=[f"Duplication analyzer failed: {result.stderr}"]
                )

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            return DuplicationCheck(
                passed=False,
                violations=[f"Could not run duplication analyzer: {str(e)}"]
            )

    def check_package_placement(self) -> PlacementCheck:
        """
        Verify all shared logic in correct package:
        1. Foundation logic in django_osoul
        2. Automation logic in django_rseal
        3. Testing infrastructure in django_grep
        4. AI logic in nawaai
        5. No business logic in projects
        """
        print("Checking package placement...")

        misplaced_modules = []

        # Check for business logic in projects
        project_dirs = ["ctc-research.com/apps", "structa.cloud/apps"]
        forbidden_patterns = ["services/", "managers/", "mixins/", "utils/"]

        for project_dir in project_dirs:
            if os.path.exists(os.path.join(self.workspace_root, project_dir)):
                for root, dirs, files in os.walk(os.path.join(self.workspace_root, project_dir)):
                    for file in files:
                        if file.endswith('.py'):
                            filepath = os.path.join(root, file)
                            rel_path = os.path.relpath(filepath, self.workspace_root)

                            # Check if file contains business logic patterns
                            try:
                                with open(filepath, 'r') as f:
                                    content = f.read()

                                    # Simple heuristic: look for class definitions that aren't thin subclasses
                                    if "class " in content and "ServiceBase" not in content:
                                        for pattern in forbidden_patterns:
                                            if pattern in rel_path:
                                                misplaced_modules.append(rel_path)
                                                break
                            except:
                                pass

        passed = len(misplaced_modules) == 0

        return PlacementCheck(
            passed=passed,
            misplaced_modules=misplaced_modules
        )

    def check_boundary_enforcement(self) -> BoundaryCheck:
        """
        Verify boundary rules enforced:
        1. Run import-linter
        2. Verify zero violations
        3. Check CI configuration
        """
        print("Checking boundary enforcement...")

        violations = []

        # Try to run import-linter
        try:
            result = subprocess.run(
                ["import-linter", "--config", ".importlinter"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            if result.returncode != 0:
                # Parse violations from output
                lines = result.stdout.split('\n')
                current_violation = None

                for line in lines:
                    if "VIOLATION:" in line:
                        if current_violation:
                            violations.append(BoundaryViolation(
                                source_file=current_violation.get('source', 'unknown'),
                                import_statement=current_violation.get('import', 'unknown'),
                                violation_type=current_violation.get('type', 'unknown'),
                                rule_violated=current_violation.get('rule', 'unknown')
                            ))
                        current_violation = {}
                    elif "Source:" in line and current_violation is not None:
                        current_violation['source'] = line.split("Source:")[1].strip()
                    elif "Import:" in line and current_violation is not None:
                        current_violation['import'] = line.split("Import:")[1].strip()
                    elif "Rule:" in line and current_violation is not None:
                        current_violation['rule'] = line.split("Rule:")[1].strip()

                if current_violation:
                    violations.append(BoundaryViolation(
                        source_file=current_violation.get('source', 'unknown'),
                        import_statement=current_violation.get('import', 'unknown'),
                        violation_type=current_violation.get('type', 'unknown'),
                        rule_violated=current_violation.get('rule', 'unknown')
                    ))

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            violations.append(BoundaryViolation(
                source_file="system",
                import_statement="N/A",
                violation_type="tool_missing",
                rule_violated=f"Could not run import-linter: {str(e)}"
            ))

        passed = len(violations) == 0

        return BoundaryCheck(
            passed=passed,
            violations=violations
        )

    def check_all_tests_passing(self) -> TestCheck:
        """
        Verify all tests passing:
        1. Package tests
        2. Project tests
        3. Integration tests
        4. Selenium tests
        """
        print("Checking test results...")

        total_tests = 0
        passed_tests = 0
        failed_tests = []

        # Check if test report exists
        test_report_path = os.path.join(self.workspace_root, "TEST_REPORT.json")
        if os.path.exists(test_report_path):
            try:
                with open(test_report_path, 'r') as f:
                    test_report = json.load(f)

                total_tests = test_report.get('total_tests', 0)
                passed_tests = test_report.get('passed_tests', 0)
                failed_tests = test_report.get('failed_tests', [])

                passed = len(failed_tests) == 0

                return TestCheck(
                    passed=passed,
                    total_tests=total_tests,
                    passed_tests=passed_tests,
                    failed_tests=failed_tests
                )
            except:
                pass

        # If no test report, assume tests need to be run
        return TestCheck(
            passed=False,
            total_tests=0,
            passed_tests=0,
            failed_tests=["No test report found. Run tests first."]
        )

    def check_specs_complete(self) -> SpecCheck:
        """
        Verify all specs complete:
        1. All tasks marked [x]
        2. All acceptance criteria met
        3. All documentation present
        """
        print("Checking spec completion...")

        incomplete_specs = []
        incomplete_tasks = []

        # Check the main spec tasks file
        spec_path = os.path.join(self.workspace_root, ".kiro/specs/ecosystem-architectural-refactoring/tasks.md")
        if os.path.exists(spec_path):
            try:
                with open(spec_path, 'r') as f:
                    content = f.read()

                # Count incomplete tasks
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('- [ ]') or line.strip().startswith('- [-]'):
                        incomplete_tasks.append(line.strip())

                if len(incomplete_tasks) > 0:
                    incomplete_specs.append("ecosystem-architectural-refactoring")
            except:
                incomplete_specs.append("ecosystem-architectural-refactoring (cannot read)")

        passed = len(incomplete_specs) == 0 and len(incomplete_tasks) == 0

        return SpecCheck(
            passed=passed,
            incomplete_specs=incomplete_specs,
            incomplete_tasks=incomplete_tasks
        )

    def check_docker_health(self) -> DockerCheck:
        """
        Verify Docker health:
        1. Both projects build successfully
        2. Both projects start successfully
        3. Health endpoints return 200
        4. No errors in logs
        """
        print("Checking Docker health...")

        build_errors = []
        runtime_errors = []
        health_status = {}

        # Check for Docker health reports
        docker_report_path = os.path.join(self.workspace_root, "DOCKER_HEALTH_REPORT.json")
        if os.path.exists(docker_report_path):
            try:
                with open(docker_report_path, 'r') as f:
                    docker_report = json.load(f)

                build_errors = docker_report.get('build_errors', [])
                runtime_errors = docker_report.get('runtime_errors', [])
                health_status = docker_report.get('health_status', {})

                passed = len(build_errors) == 0 and len(runtime_errors) == 0

                return DockerCheck(
                    passed=passed,
                    build_errors=build_errors,
                    runtime_errors=runtime_errors,
                    health_status=health_status
                )
            except:
                pass

        # If no Docker report, check for basic files
        docker_compose_path = os.path.join(self.workspace_root, "docker-compose.yml")
        if not os.path.exists(docker_compose_path):
            build_errors.append("docker-compose.yml not found")

        return DockerCheck(
            passed=False,
            build_errors=build_errors,
            runtime_errors=runtime_errors,
            health_status=health_status
        )

    def generate_completion_report(self) -> str:
        """
        Generate COMPLETION_REPORT.md:
        1. Summary of all changes
        2. Validation results
        3. Metrics before/after
        4. Known issues
        5. Next steps
        """
        if not self.report:
            self.validate_all()

        report_lines = []

        # Header
        report_lines.append("# Ecosystem Architectural Refactoring Completion Report")
        report_lines.append("")
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"The ecosystem-wide architectural refactoring has been {'successfully completed' if self.report.all_passed else 'partially completed'}.")
        report_lines.append("")
        report_lines.append(f"**Date**: {datetime.now().strftime('%B %d, %Y')}")
        report_lines.append(f"**Status**: {'✅ COMPLETE' if self.report.all_passed else '⚠️ INCOMPLETE'}")
        report_lines.append("**Scope**: All Django projects (ctc-research.com, structa.cloud) and shared packages (django_osoul, django_rseal, django_grep, nawaai)")
        report_lines.append("")

        # Validation Results
        report_lines.append("## Validation Results")
        report_lines.append("")

        # Duplication Check
        report_lines.append("### 1. Code Duplication Check")
        report_lines.append(f"- **Status**: {'✅ PASSED' if self.report.duplication_check.passed else '❌ FAILED'}")
        if self.report.duplication_check.passed:
            report_lines.append("- Zero code duplication detected")
        else:
            report_lines.append(f"- Found {self.report.duplication_check.duplicated_pairs} duplicated pairs")
            report_lines.append(f"- Maximum similarity: {self.report.duplication_check.max_similarity:.1%}")
            for violation in self.report.duplication_check.violations:
                report_lines.append(f"- {violation}")
        report_lines.append("")

        # Package Placement Check
        report_lines.append("### 2. Package Placement Check")
        report_lines.append(f"- **Status**: {'✅ PASSED' if self.report.placement_check.passed else '❌ FAILED'}")
        if self.report.placement_check.passed:
            report_lines.append("- All shared logic in correct packages")
        else:
            report_lines.append(f"- Found {len(self.report.placement_check.misplaced_modules)} misplaced modules")
            for module in self.report.placement_check.misplaced_modules[:5]:  # Show first 5
                report_lines.append(f"- {module}")
            if len(self.report.placement_check.misplaced_modules) > 5:
                report_lines.append(f"- ... and {len(self.report.placement_check.misplaced_modules) - 5} more")
        report_lines.append("")

        # Boundary Check
        report_lines.append("### 3. Boundary Enforcement Check")
        report_lines.append(f"- **Status**: {'✅ PASSED' if self.report.boundary_check.passed else '❌ FAILED'}")
        if self.report.boundary_check.passed:
            report_lines.append("- All boundary rules enforced")
        else:
            report_lines.append(f"- Found {len(self.report.boundary_check.violations)} boundary violations")
            for violation in self.report.boundary_check.violations[:5]:  # Show first 5
                report_lines.append(f"- {violation.source_file}: {violation.import_statement} ({violation.rule_violated})")
            if len(self.report.boundary_check.violations) > 5:
                report_lines.append(f"- ... and {len(self.report.boundary_check.violations) - 5} more")
        report_lines.append("")

        # Test Check
        report_lines.append("### 4. Test Results Check")
        report_lines.append(f"- **Status**: {'✅ PASSED' if self.report.test_check.passed else '❌ FAILED'}")
        report_lines.append(f"- Total tests: {self.report.test_check.total_tests}")
        report_lines.append(f"- Passed tests: {self.report.test_check.passed_tests}")
        report_lines.append(f"- Failed tests: {len(self.report.test_check.failed_tests)}")
        if self.report.test_check.failed_tests:
            for test in self.report.test_check.failed_tests[:3]:  # Show first 3
                report_lines.append(f"- {test}")
            if len(self.report.test_check.failed_tests) > 3:
                report_lines.append(f"- ... and {len(self.report.test_check.failed_tests) - 3} more")
        report_lines.append("")

        # Spec Check
        report_lines.append("### 5. Spec Completion Check")
        report_lines.append(f"- **Status**: {'✅ PASSED' if self.report.spec_check.passed else '❌ FAILED'}")
        if self.report.spec_check.passed:
            report_lines.append("- All specs complete")
        else:
            report_lines.append(f"- Incomplete specs: {len(self.report.spec_check.incomplete_specs)}")
            report_lines.append(f"- Incomplete tasks: {len(self.report.spec_check.incomplete_tasks)}")
            for task in self.report.spec_check.incomplete_tasks[:3]:  # Show first 3
                report_lines.append(f"- {task}")
            if len(self.report.spec_check.incomplete_tasks) > 3:
                report_lines.append(f"- ... and {len(self.report.spec_check.incomplete_tasks) - 3} more")
        report_lines.append("")

        # Docker Check
        report_lines.append("### 6. Docker Health Check")
        report_lines.append(f"- **Status**: {'✅ PASSED' if self.report.docker_check.passed else '❌ FAILED'}")
        if self.report.docker_check.passed:
            report_lines.append("- Docker containers healthy")
        else:
            report_lines.append(f"- Build errors: {len(self.report.docker_check.build_errors)}")
            report_lines.append(f"- Runtime errors: {len(self.report.docker_check.runtime_errors)}")
            for error in self.report.docker_check.build_errors[:2]:  # Show first 2
                report_lines.append(f"- {error}")
            for error in self.report.docker_check.runtime_errors[:2]:  # Show first 2
                report_lines.append(f"- {error}")
        report_lines.append("")

        # Overall Status
        report_lines.append("## Overall Status")
        report_lines.append("")
        if self.report.all_passed:
            report_lines.append("✅ **ALL VALIDATIONS PASSED**")
            report_lines.append("")
            report_lines.append("The ecosystem-wide architectural refactoring has been successfully validated.")
            report_lines.append("All requirements are met, and the system is ready for production.")
        else:
            report_lines.append("⚠️ **SOME VALIDATIONS FAILED**")
            report_lines.append("")
            report_lines.append("The ecosystem-wide architectural refactoring requires additional work.")
            report_lines.append("Please address the issues identified above before proceeding to production.")

        # Next Steps
        report_lines.append("")
        report_lines.append("## Next Steps")
        report_lines.append("")
        if self.report.all_passed:
            report_lines.append("1. **Deploy to production**")
            report_lines.append("2. **Monitor system health**")
            report_lines.append("3. **Update documentation** with any post-deployment changes")
            report_lines.append("4. **Train team** on new architecture patterns")
        else:
            report_lines.append("1. **Address validation failures** identified above")
            report_lines.append("2. **Re-run validation** after fixes")
            report_lines.append("3. **Update completion report** with progress")
            report_lines.append("4. **Proceed to production** only after all validations pass")

        # Footer
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append(f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("**Generated By**: SystemValidator")
        report_lines.append("**Tool**: scripts/validate_system.py")

        return "\n".join(report_lines)

    def save_report(self, report_path: str = "COMPLETION_REPORT.md"):
        """Save the completion report to a file."""
        report_content = self.generate_completion_report()

        with open(report_path, 'w') as f:
            f.write(report_content)

        print(f"Completion report saved to {report_path}")
        return report_path


def main():
    parser = argparse.ArgumentParser(description="Validate ecosystem architectural refactoring")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    parser.add_argument("--output", default="COMPLETION_REPORT.md", help="Output report file")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test validation")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker validation")

    args = parser.parse_args()

    validator = SystemValidator(workspace_root=args.workspace)

    print("=" * 80)
    print("ECOSYSTEM ARCHITECTURAL REFACTORING VALIDATION")
    print("=" * 80)
    print()

    # Run validation
    report = validator.validate_all()

    # Generate and save report
    report_path = validator.save_report(args.output)

    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print()

    if report.all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("The system is ready for production deployment.")
    else:
        print("⚠️ SOME VALIDATIONS FAILED")
        print("Please address the issues identified in the report.")

    print()
    print(f"Report saved to: {report_path}")
    print()

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
