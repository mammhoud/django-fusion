#!/usr/bin/env python
"""
VResume Pages Testing Runner
=============================

Comprehensive test runner for all VResume pages and endpoints.
Tracks results with detailed reporting and performance metrics.

Features:
- Tests all main pages (Home, About, Resume, Portfolio, Blog, Contact)
- Tests modal endpoints (Project detail, Blog detail)
- Tests form submissions (Contact form, Newsletter subscription)
- Tests error cases (404s, validation errors)
- Tracks performance metrics (response time, content length)
- Generates detailed JSON reports

Usage:
    python -m tests.runner
    python -m tests.runner --base-url http://custom-url:8000
    python -m tests.runner --verbose
    python -m tests.runner --output json
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from pathlib import Path

# Configuration
DEFAULT_BASE_URL = "http://localhost:8000"
PAGES_BASE = "/pages/"
TIMEOUT = 10
REPORT_DIR = Path(__file__).parent.parent / "test_reports"

# Test results tracking
results = {
    "timestamp": datetime.now().isoformat(),
    "base_url": DEFAULT_BASE_URL,
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
    },
    "performance": {
        "total_time": 0,
        "avg_time": 0,
        "min_time": 0,
        "max_time": 0,
    }
}


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    PURPLE = '\033[0;35m'
    BOLD = '\033[1m'
    NC = '\033[0m'


class TestRunner:
    """Main test execution engine"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VResume-Test-Runner/1.0'
        })

    def test_request(
        self,
        name: str,
        method: str,
        url: str,
        expected_status: int = 200,
        headers: Dict = None,
        data: Dict = None,
        is_htmx: bool = False,
        skip_reason: Optional[str] = None,
    ) -> Dict:
        """Execute a single test request and track results"""

        test_result = {
            "name": name,
            "method": method,
            "url": url,
            "expected_status": expected_status,
            "timestamp": datetime.now().isoformat(),
        }

        # Handle skipped tests
        if skip_reason:
            test_result["skipped"] = True
            test_result["skip_reason"] = skip_reason
            return test_result

        try:
            # Prepare headers
            request_headers = headers or {}
            if is_htmx:
                request_headers["HX-Request"] = "true"

            # Make request
            start_time = time.time()
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(
                    url, headers=request_headers, data=data, timeout=TIMEOUT
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed_time = time.time() - start_time

            # Record results
            test_result["status_code"] = response.status_code
            test_result["elapsed_time"] = round(elapsed_time, 3)
            test_result["content_length"] = len(response.content)
            test_result["passed"] = response.status_code == expected_status

            # Add response details
            if response.status_code >= 400:
                test_result["error_message"] = response.text[:200]

            # Get content type
            test_result["response_type"] = response.headers.get("content-type", "unknown")

            if self.verbose:
                status = "✓" if test_result["passed"] else "✗"
                print(f"  {status} {name} ({response.status_code})")

            return test_result

        except requests.exceptions.Timeout:
            test_result["passed"] = False
            test_result["error"] = "Request timeout"
            if self.verbose:
                print(f"  ✗ {name} (TIMEOUT)")
            return test_result
        except requests.exceptions.ConnectionError:
            test_result["passed"] = False
            test_result["error"] = "Connection error"
            if self.verbose:
                print(f"  ✗ {name} (CONNECTION ERROR)")
            return test_result
        except Exception as e:
            test_result["passed"] = False
            test_result["error"] = str(e)
            if self.verbose:
                print(f"  ✗ {name} (ERROR: {str(e)[:50]})")
            return test_result

    def run_tab_tests(self):
        """Test all tab views"""
        if self.verbose:
            print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
            print(f"{Colors.BLUE}TESTING TAB VIEWS{Colors.NC}")
            print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

        # Test main pages - use root URL and query parameters for tabs
        tabs = [
            ("Home", "/", {}),
            ("About", "/?tab=about", {}),
            ("Resume", "/?tab=resume", {}),
            ("Portfolio", "/?tab=portfolio", {}),
            ("Blog", "/?tab=blog", {}),
            ("Contact", "/?tab=contact", {}),
        ]

        for tab_name, path, params in tabs:
            url = urljoin(self.base_url, path)
            
            # Full page load
            result = self.test_request(
                f"Tab: {tab_name} (Full Page)",
                "GET",
                url,
                expected_status=200,
            )
            results["tests"].append(result)

            # HTMX fragment
            result = self.test_request(
                f"Tab: {tab_name} (HTMX Fragment)",
                "GET",
                url,
                expected_status=200,
                is_htmx=True,
            )
            results["tests"].append(result)

    def run_modal_tests(self):
        """Test modal endpoints"""
        if self.verbose:
            print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
            print(f"{Colors.BLUE}TESTING MODAL ENDPOINTS{Colors.NC}")
            print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

        # Project detail - test with common project IDs
        for project_id in ["1", "2"]:
            result = self.test_request(
                f"Project Detail: {project_id}",
                "GET",
                urljoin(self.base_url, f"project/{project_id}/"),
                expected_status=200,
                is_htmx=True,
            )
            results["tests"].append(result)

        # Blog detail - test with common blog IDs
        for blog_id in [1, 2]:
            result = self.test_request(
                f"Blog Detail: ID {blog_id}",
                "GET",
                urljoin(self.base_url, f"blog/{blog_id}/"),
                expected_status=200,
                is_htmx=True,
            )
            results["tests"].append(result)

    def run_form_tests(self):
        """Test form submissions"""
        if self.verbose:
            print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
            print(f"{Colors.BLUE}TESTING FORM SUBMISSIONS{Colors.NC}")
            print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

        # Valid contact form
        result = self.test_request(
            "Contact Form: Valid Submission",
            "POST",
            urljoin(self.base_url, "contact/submit/"),
            expected_status=200,
            data={
                "fullname": "John Doe",
                "email": "john@example.com",
                "message": "Test message",
            },
            is_htmx=True,
        )
        results["tests"].append(result)

        # Missing name
        result = self.test_request(
            "Contact Form: Missing Name",
            "POST",
            urljoin(self.base_url, "contact/submit/"),
            expected_status=400,
            data={"email": "john@example.com", "message": "Test message"},
            is_htmx=True,
        )
        results["tests"].append(result)

        # Missing email
        result = self.test_request(
            "Contact Form: Missing Email",
            "POST",
            urljoin(self.base_url, "contact/submit/"),
            expected_status=400,
            data={"fullname": "John Doe", "message": "Test message"},
            is_htmx=True,
        )
        results["tests"].append(result)

        # Missing message
        result = self.test_request(
            "Contact Form: Missing Message",
            "POST",
            urljoin(self.base_url, "contact/submit/"),
            expected_status=400,
            data={"fullname": "John Doe", "email": "john@example.com"},
            is_htmx=True,
        )
        results["tests"].append(result)

    def run_subscription_tests(self):
        """Test newsletter subscription"""
        if self.verbose:
            print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
            print(f"{Colors.BLUE}TESTING NEWSLETTER SUBSCRIPTION{Colors.NC}")
            print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

        # Valid subscription
        result = self.test_request(
            "Subscribe: Valid Email",
            "POST",
            urljoin(self.base_url, "subscribe/"),
            expected_status=200,
            data={"email": f"subscriber-{int(time.time())}@example.com"},
            is_htmx=True,
        )
        results["tests"].append(result)

        # Duplicate subscription
        email = f"duplicate-{int(time.time())}@example.com"
        self.test_request(
            "Subscribe: First Time",
            "POST",
            urljoin(self.base_url, "subscribe/"),
            expected_status=200,
            data={"email": email},
            is_htmx=True,
        )

        result = self.test_request(
            "Subscribe: Duplicate Email",
            "POST",
            urljoin(self.base_url, "subscribe/"),
            expected_status=200,
            data={"email": email},
            is_htmx=True,
        )
        results["tests"].append(result)

        # Empty email
        result = self.test_request(
            "Subscribe: Empty Email",
            "POST",
            urljoin(self.base_url, "subscribe/"),
            expected_status=400,
            data={"email": ""},
            is_htmx=True,
        )
        results["tests"].append(result)

    def run_error_tests(self):
        """Test error cases"""
        if self.verbose:
            print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
            print(f"{Colors.BLUE}TESTING ERROR CASES{Colors.NC}")
            print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

        # Invalid tab
        result = self.test_request(
            "Error: Invalid Tab",
            "GET",
            urljoin(self.base_url, "invalid-tab/"),
            expected_status=404,
        )
        results["tests"].append(result)

        # Invalid project
        result = self.test_request(
            "Error: Invalid Project ID",
            "GET",
            urljoin(self.base_url, "project/nonexistent/"),
            expected_status=404,
            is_htmx=True,
        )
        results["tests"].append(result)

        # Invalid blog
        result = self.test_request(
            "Error: Invalid Blog ID",
            "GET",
            urljoin(self.base_url, "blog/9999/"),
            expected_status=404,
            is_htmx=True,
        )
        results["tests"].append(result)

    def run_all_tests(self):
        """Run all test suites"""
        self.run_tab_tests()
        self.run_modal_tests()
        self.run_form_tests()
        self.run_subscription_tests()
        self.run_error_tests()

    def generate_report(self, output_format: str = "json"):
        """Generate test report"""
        # Calculate summary
        total = len(results["tests"])
        passed = sum(1 for t in results["tests"] if t.get("passed", False))
        skipped = sum(1 for t in results["tests"] if t.get("skipped", False))
        failed = total - passed - skipped

        results["summary"]["total"] = total
        results["summary"]["passed"] = passed
        results["summary"]["failed"] = failed
        results["summary"]["skipped"] = skipped

        # Performance stats
        times = [t.get("elapsed_time", 0) for t in results["tests"] if "elapsed_time" in t]
        if times:
            results["performance"]["total_time"] = round(sum(times), 3)
            results["performance"]["avg_time"] = round(sum(times) / len(times), 3)
            results["performance"]["min_time"] = round(min(times), 3)
            results["performance"]["max_time"] = round(max(times), 3)

        # Print summary
        print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {Colors.GREEN}{passed} ✓{Colors.NC}")
        print(f"Failed: {Colors.RED}{failed} ✗{Colors.NC}")
        if skipped:
            print(f"Skipped: {Colors.YELLOW}{skipped} ⊘{Colors.NC}")
        print(f"Success Rate: {Colors.GREEN}{(passed/total*100):.1f}%{Colors.NC}")

        # Performance stats
        if times:
            print(f"\n{Colors.CYAN}Performance:{Colors.NC}")
            print(f"  Total Time: {results['performance']['total_time']}s")
            print(f"  Avg Response Time: {results['performance']['avg_time']}s")
            print(f"  Min Response Time: {results['performance']['min_time']}s")
            print(f"  Max Response Time: {results['performance']['max_time']}s")

        # Failed tests details
        failed_tests = [t for t in results["tests"] if not t.get("passed", False) and not t.get("skipped", False)]
        if failed_tests:
            print(f"\n{Colors.RED}Failed Tests:{Colors.NC}")
            for test in failed_tests:
                print(f"  - {test['name']}")
                if "error" in test:
                    print(f"    Error: {test['error']}")
                if "error_message" in test:
                    print(f"    Response: {test['error_message']}")

        # Save report
        REPORT_DIR.mkdir(exist_ok=True)
        report_file = REPORT_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{Colors.GREEN}✓ Detailed report saved to: {report_file}{Colors.NC}")

        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="VResume Pages Testing Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tests.runner
  python -m tests.runner --base-url http://custom-url:8000
  python -m tests.runner --verbose
  python -m tests.runner --output json
        """
    )

    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL for testing (default: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BOLD}VResume Pages Testing Runner{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"Base URL: {Colors.YELLOW}{args.base_url}{Colors.NC}")
    print(f"Started: {Colors.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}")

    # Update base URL in results
    results["base_url"] = args.base_url

    try:
        runner = TestRunner(base_url=args.base_url, verbose=args.verbose)
        
        # Check server connectivity
        print(f"\n{Colors.BLUE}Checking server connectivity...{Colors.NC}")
        try:
            response = runner.session.get(
                urljoin(args.base_url, "/pages/home/"),
                timeout=5
            )
            print(f"{Colors.GREEN}✓ Server is running{Colors.NC}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error: Cannot connect to {args.base_url}{Colors.NC}")
            print(f"{Colors.YELLOW}Make sure the Django development server is running:{Colors.NC}")
            print(f"  cd v1")
            print(f"  python manage.py runserver")
            sys.exit(1)

        # Run tests
        runner.run_all_tests()
        runner.generate_report(output_format=args.output)

        print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BOLD}Testing Complete!{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")

        # Exit with appropriate code
        failed = results["summary"]["failed"]
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Testing interrupted by user{Colors.NC}")
        runner.generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {e}{Colors.NC}")
        runner.generate_report()
        sys.exit(1)


if __name__ == "__main__":
    main()
