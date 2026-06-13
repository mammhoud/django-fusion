#!/usr/bin/env python3
"""
Demo script to show how to run tests for both websites.
This script demonstrates the usage of the test scripts we created.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Demonstrate test script usage."""
    print("="*60)
    print("Test Script Demonstration")
    print("="*60)

    scripts_dir = Path("scripts")

    print("\nAvailable Test Scripts:")
    print("1. scripts/run_all_tests.py - Run all tests for both websites")
    print("2. scripts/verify_test_parity.py - Verify test parity between websites")

    print("\nUsage Examples:")
    print("\n1. Run all tests:")
    print("   $ python3 scripts/run_all_tests.py")
    print("   This will:")
    print("   - Run tests for all packages (django_osoul, django_rseal, django_grep, nawaai)")
    print("   - Run tests for ctc-research.com")
    print("   - Run tests for structa.cloud")
    print("   - Verify test parity between websites")
    print("   - Generate TEST_REPORT.json")

    print("\n2. Verify test parity only:")
    print("   $ python3 scripts/verify_test_parity.py")
    print("   This will:")
    print("   - Count tests in both projects")
    print("   - Compare test structures")
    print("   - Check for parity issues")
    print("   - Generate TEST_PARITY_REPORT.json")

    print("\n3. Run with verbose output:")
    print("   $ python3 scripts/run_all_tests.py --verbose")

    print("\n4. Run tests for specific project:")
    print("   $ cd ctc-research.com && uv run pytest tests/ -v")
    print("   $ cd structa.cloud && uv run pytest tests/ -v")

    print("\nExpected Output:")
    print("- Test counts for both websites")
    print("- Pass/fail/skip statistics")
    print("- Parity verification results")
    print("- JSON report files")

    print("\nTo actually run the tests, execute:")
    print("$ python3 scripts/run_all_tests.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
