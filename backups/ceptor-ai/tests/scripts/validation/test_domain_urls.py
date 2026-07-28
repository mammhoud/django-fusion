#!/usr/bin/env python3
"""
Domain URL Testing Script
Tests all configured domains for both CTC Research and Structa Cloud
"""

import sys
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Test configurations
DOMAINS_TO_TEST = {
    'CTC Research': [
        'http://ctc-research.com',
        'http://www.ctc-research.com',
        'http://arch.ctc-research.com',
        'http://localhost:5070',
    ],
    'Structa Cloud': [
        'http://core.structa.cloud',
        'http://structa.cloud',
        'http://www.structa.cloud',
        'http://localhost:5071',
    ]
}

# Health check endpoints
HEALTH_ENDPOINTS = {
    'http://localhost:5070': '/health/',
    'http://localhost:5071': '/health/',
}

# Static/Media endpoints to test
ASSET_PATHS = [
    '/static/',
    '/media/',
]


def check_url(url: str, timeout: int = 10) -> Tuple[bool, int, str]:
    """
    Check a URL and return success status, status code, and message.

    Args:
        url: URL to check
        timeout: Request timeout in seconds

    Returns:
        Tuple of (success, status_code, message)
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            verify=False,  # Skip SSL verification for local testing
            headers={'Host': urlparse(url).netloc}
        )

        if response.status_code == 200:
            return True, response.status_code, "OK"
        elif 300 <= response.status_code < 400:
            return True, response.status_code, f"Redirect to {response.url}"
        else:
            return False, response.status_code, f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection Error"
    except Exception as e:
        return False, 0, f"Error: {str(e)}"


def check_health_endpoint(base_url: str, endpoint: str) -> Tuple[bool, str]:
    """
    Check a health check endpoint.

    Args:
        base_url: Base URL of the service
        endpoint: Health check endpoint path

    Returns:
        Tuple of (success, message)
    """
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                return True, f"Healthy (version: {data.get('version', 'unknown')})"
            else:
                return False, f"Unhealthy: {data}"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_result(label: str, success: bool, message: str):
    """Print a test result."""
    status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
    print(f"{status} {label:50} {message}")


def main():
    """Run all domain tests."""
    print_header("Domain URL Testing Suite")

    all_passed = True
    results: Dict[str, List[Tuple[str, bool, str]]] = {}

    # Test each domain group
    for group_name, urls in DOMAINS_TO_TEST.items():
        print(f"\n{YELLOW}Testing {group_name}:{RESET}")
        results[group_name] = []

        for url in urls:
            success, status_code, message = check_url(url)
            results[group_name].append((url, success, message))

            if not success:
                all_passed = False

            print_result(url, success, message)

    # Test health endpoints
    print_header("Health Check Endpoints")

    for base_url, endpoint in HEALTH_ENDPOINTS.items():
        success, message = check_health_endpoint(base_url, endpoint)

        if not success:
            all_passed = False

        print_result(f"{base_url}{endpoint}", success, message)

    # Test asset paths (just check if they're accessible, 404 is OK)
    print_header("Asset Path Accessibility")

    for base_url in ['http://localhost:5070', 'http://localhost:5071']:
        for asset_path in ASSET_PATHS:
            url = f"{base_url}{asset_path}"
            success, status_code, message = check_url(url)
            # For asset paths, 404 is acceptable (means path is routed correctly)
            is_ok = success or status_code == 404
            print_result(url, is_ok, message if success else f"HTTP {status_code} (OK)")

    # Summary
    print_header("Test Summary")

    total_tests = sum(len(urls) for urls in DOMAINS_TO_TEST.values()) + len(HEALTH_ENDPOINTS)
    passed_tests = sum(1 for group_results in results.values() for _, success, _ in group_results if success)
    passed_tests += sum(1 for base_url, endpoint in HEALTH_ENDPOINTS.items() if check_health_endpoint(base_url, endpoint)[0])

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {GREEN}{passed_tests}{RESET}")
    print(f"Failed: {RED}{total_tests - passed_tests}{RESET}")

    if all_passed:
        print(f"\n{GREEN}✓ All tests passed!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}✗ Some tests failed!{RESET}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
