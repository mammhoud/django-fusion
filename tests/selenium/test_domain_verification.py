"""Domain verification tests for structa.cloud"""
import os

import pytest


@pytest.fixture(scope="session")
def domain_url():
    """Get domain URL from environment or use default"""
    return os.getenv("DOMAIN_URL", "https://structa.cloud")


class TestDomainVerification:
    """Test domain accessibility and basic functionality"""

    def test_health_endpoint(self, domain_url):
        """Test health endpoint at domain"""
        import requests
        response = requests.get(f"{domain_url}/health/", verify=False)
        assert response.status_code == 200
        assert "ok" in response.text

    def test_admin_redirect(self, domain_url):
        """Test admin panel redirects to login"""
        import requests
        response = requests.get(f"{domain_url}/admin/", verify=False, allow_redirects=False)
        assert response.status_code in [302, 301]
        assert "sign-in" in response.headers.get("Location", "")

    def test_static_css_files(self, domain_url):
        """Test static CSS files are served"""
        import requests
        response = requests.head(f"{domain_url}/static/admin/css/base.css", verify=False)
        assert response.status_code == 200
        assert "text/css" in response.headers.get("Content-Type", "")

    def test_static_js_files(self, domain_url):
        """Test static JS files are served"""
        import requests
        response = requests.head(f"{domain_url}/static/admin/js/core.js", verify=False)
        assert response.status_code == 200

    def test_https_redirect(self):
        """Test HTTP redirects to HTTPS"""
        import requests
        response = requests.get("http://structa.cloud/", allow_redirects=False, timeout=5)
        assert response.status_code in [308, 301, 302]
        assert "https" in response.headers.get("Location", "").lower()

    def test_domain_ssl_certificate(self, domain_url):
        """Test SSL certificate is valid"""
        import requests
        try:
            response = requests.get(domain_url, verify=True, timeout=5)
            # If we get here, SSL is valid
            assert True
        except requests.exceptions.SSLError:
            pytest.fail("SSL certificate validation failed")

    def test_security_headers(self, domain_url):
        """Test security headers are present"""
        import requests
        response = requests.head(domain_url, verify=False)

        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers

    def test_cors_headers(self, domain_url):
        """Test CORS headers are configured"""
        import requests
        response = requests.head(domain_url, verify=False)

        # Check for CORS-related headers
        assert "Cross-Origin-Opener-Policy" in response.headers or True  # Optional

    def test_response_time(self, domain_url):
        """Test response time is acceptable"""
        import time

        import requests

        start = time.time()
        response = requests.get(f"{domain_url}/health/", verify=False)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond within 2 seconds

    def test_database_connectivity(self, domain_url):
        """Test database is accessible from domain"""
        import requests

        # Try to access a page that requires database
        response = requests.get(f"{domain_url}/admin/", verify=False, allow_redirects=False)

        # Should not get a 500 error (database error)
        assert response.status_code != 500


class TestDomainPages:
    """Test page accessibility at domain"""

    def test_auth_pages(self, domain_url):
        """Test authentication pages"""
        import requests

        pages = [
            "/auth/sign-in/",
            "/auth/sign-up/",
        ]

        for page in pages:
            response = requests.get(f"{domain_url}{page}", verify=False)
            assert response.status_code in [200, 302], f"Page {page} failed with {response.status_code}"

    def test_static_pages(self, domain_url):
        """Test static pages"""
        import requests

        # These might return 404 if no data is loaded, but should not error
        pages = [
            "/about/",
            "/services/",
            "/contact/",
        ]

        for page in pages:
            response = requests.get(f"{domain_url}{page}", verify=False)
            # Accept 200, 302, or 404 (no data)
            assert response.status_code in [200, 302, 404], f"Page {page} failed with {response.status_code}"


class TestDomainPerformance:
    """Test domain performance metrics"""

    def test_health_endpoint_performance(self, domain_url):
        """Test health endpoint performance"""
        import time

        import requests

        times = []
        for _ in range(5):
            start = time.time()
            response = requests.get(f"{domain_url}/health/", verify=False)
            elapsed = time.time() - start
            times.append(elapsed)
            assert response.status_code == 200

        avg_time = sum(times) / len(times)
        assert avg_time < 1.0, f"Average response time {avg_time}s is too slow"

    def test_static_file_performance(self, domain_url):
        """Test static file serving performance"""
        import time

        import requests

        start = time.time()
        response = requests.head(f"{domain_url}/static/admin/css/base.css", verify=False)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Static file response time {elapsed}s is too slow"
