#!/usr/bin/env python
"""
Test Runner Script for ctc-research.com and structa.cloud

This script runs comprehensive tests for both websites using django-fusion
and generates detailed reports.

Usage:
    python test_runner.py --website ctc-research     # Run ctc-research.com tests
    python test_runner.py --website structa          # Run structa.cloud tests
    python test_runner.py --website all              # Run all tests
    python test_runner.py --selenium                 # Include Selenium tests
    python test_runner.py --property                 # Include property-based tests
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
WEBSITES = {
    "ctc-research": {
        "path": "ctc-research.com",
        "domain": "ctc-research.com",
        "port": 5070,
    },
    "structa": {
        "path": "structa.cloud",
        "domain": "structa.cloud",
        "port": 5070,
    },
}

REPORTS_DIR = Path("docs/reports")
SCRIPTS_DIR = Path("docs/scripts")


def run_command(cmd, cwd=None, capture=True):
    """Run a shell command and return output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    return result


def run_tests(website, test_type="all", verbose=True):
    """Run tests for a specific website."""
    website_config = WEBSITES[website]
    website_path = website_config["path"]

    print(f"\n{'='*60}")
    print(f"Running tests for {website_config['domain']}")
    print(f"{'='*60}\n")

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    # Add test markers
    if test_type == "unit":
        cmd.extend(["-m", "not selenium and not property"])
    elif test_type == "selenium":
        cmd.extend(["-m", "selenium"])
    elif test_type == "property":
        cmd.extend(["-m", "property"])

    # Add test paths
    test_path = f"{website_path}/tests/"

    if test_type == "selenium":
        test_path = f"{website_path}/tests/selenium/"

    cmd.append(test_path)

    # Run tests
    result = run_command(cmd)

    return result


def run_health_check(website):
    """Run health check tests for a website."""
    website_config = WEBSITES[website]

    print(f"\nRunning health checks for {website_config['domain']}...")

    # Test basic health endpoint
    cmd = [
        "curl",
        "-sf",
        f"http://localhost:{website_config['port']}/health/",
    ]
    result = run_command(cmd, capture=True)

    health_results = {
        "basic": result.returncode == 0,
        "output": result.stdout.strip() if result.stdout else "",
    }

    # Test database health
    cmd = [
        "curl",
        "-sf",
        f"http://localhost:{website_config['port']}/health/database/",
    ]
    result = run_command(cmd, capture=True)
    health_results["database"] = result.returncode == 0

    # Test assets health
    cmd = [
        "curl",
        "-sf",
        f"http://localhost:{website_config['port']}/health/assets/",
    ]
    result = run_command(cmd, capture=True)
    health_results["assets"] = result.returncode == 0

    return health_results


def generate_test_report(website, test_result, health_results):
    """Generate a test report for a website."""
    website_config = WEBSITES[website]

    report = {
        "website": website_config["domain"],
        "timestamp": datetime.now().isoformat(),
        "tests_passed": test_result.returncode == 0,
        "exit_code": test_result.returncode,
        "output": test_result.stdout[-5000:] if test_result.stdout else "",
        "errors": test_result.stderr[-2000:] if test_result.stderr else "",
        "health_checks": health_results,
    }

    return report


def save_report(website, report):
    """Save test report to docs/reports."""
    website_config = WEBSITES[website]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create filename in snake_case
    filename = f"test_report_{website}_{timestamp}.json"
    filepath = REPORTS_DIR / filename

    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save report
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {filepath}")

    # Also save as latest
    latest_filename = f"test_report_{website}_latest.json"
    latest_filepath = REPORTS_DIR / latest_filename

    with open(latest_filepath, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Latest report saved to: {latest_filepath}")

    return filepath


def create_text_report(website, report):
    """Create a human-readable text report."""
    website_config = WEBSITES[website]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = f"test_report_{website}_{timestamp}.txt"
    filepath = REPORTS_DIR / filename

    content = f"""
================================================================================
TEST REPORT FOR {website_config['domain'].upper()}
================================================================================

Generated: {report['timestamp']}
Website: {website_config['domain']}
Port: {website_config['port']}

--------------------------------------------------------------------------------
TEST RESULTS
--------------------------------------------------------------------------------

Tests Passed: {'Yes' if report['tests_passed'] else 'No'}
Exit Code: {report['exit_code']}

--------------------------------------------------------------------------------
HEALTH CHECKS
--------------------------------------------------------------------------------

Basic Health: {'✓ PASS' if report['health_checks'].get('basic') else '✗ FAIL'}
Database Health: {'✓ PASS' if report['health_checks'].get('database') else '✗ FAIL'}
Assets Health: {'✓ PASS' if report['health_checks'].get('assets') else '✗ FAIL'}

--------------------------------------------------------------------------------
TEST OUTPUT (Last 5000 chars)
--------------------------------------------------------------------------------

{report['output']}

--------------------------------------------------------------------------------
ERRORS (Last 2000 chars)
--------------------------------------------------------------------------------

{report['errors']}

================================================================================
"""

    with open(filepath, "w") as f:
        f.write(content)

    # Also save as latest
    latest_filename = f"test_report_{website}_latest.txt"
    latest_filepath = REPORTS_DIR / latest_filename

    with open(latest_filepath, "w") as f:
        f.write(content)

    print(f"Text report saved to: {filepath}")

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Test Runner for ctc-research.com and structa.cloud"
    )
    parser.add_argument(
        "--website",
        choices=["ctc-research", "structa", "all"],
        default="all",
        help="Website to test",
    )
    parser.add_argument(
        "--test-type",
        choices=["all", "unit", "selenium", "property"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--selenium",
        action="store_true",
        help="Include Selenium tests",
    )
    parser.add_argument(
        "--property",
        action="store_true",
        help="Include property-based tests",
    )
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Skip health checks",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Verbose output",
    )

    args = parser.parse_args()

    # Determine test type
    test_type = args.test_type
    if args.selenium:
        test_type = "selenium"
    elif args.property:
        test_type = "property"

    # Determine websites to test
    websites_to_test = []
    if args.website == "all":
        websites_to_test = ["ctc-research", "structa"]
    else:
        websites_to_test = [args.website]

    # Run tests for each website
    all_reports = []

    for website in websites_to_test:
        # Run tests
        test_result = run_tests(website, test_type, args.verbose)

        # Run health checks (if not skipped)
        health_results = {}
        if not args.skip_health:
            try:
                health_results = run_health_check(website)
            except Exception as e:
                print(f"Health check failed: {e}")
                health_results = {"error": str(e)}

        # Generate and save report
        report = generate_test_report(website, test_result, health_results)
        all_reports.append(report)

        save_report(website, report)
        create_text_report(website, report)

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for report in all_reports:
        status = "PASSED" if report["tests_passed"] else "FAILED"
        print(f"{report['website']}: {status}")

    # Return exit code
    if all(r["tests_passed"] for r in all_reports):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
