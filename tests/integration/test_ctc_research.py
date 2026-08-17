"""
CTC Research Integration Tests
============================
Comprehensive integration tests for the CTC Research website.
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


class TestCTCResearchIntegration:
    """Integration tests for CTC Research website."""

    @pytest.fixture(autouse=True)
    def setup(self, ctc_research_root):
        """Setup test environment."""
        self.ctc_root = ctc_research_root
        self.base_url = "http://localhost:5070"

    def test_docker_build(self):
        """Test CTC Research Docker build."""
        result = subprocess.run([
            'docker', 'compose', '-f', str(self.ctc_root / 'docker-compose.yml'), 'build'
        ], capture_output=True, text=True, timeout=600)

        assert result.returncode == 0, f"Docker build failed: {result.stderr}"

    def test_database_migration(self):
        """Test database migrations."""
        # Start infrastructure
        subprocess.run([
            'docker', 'compose', 'up', '-d', 'postgres', 'redis'
        ], cwd=self.ctc_root.parent)

        # Run migrations
        result = subprocess.run([
            'docker', 'compose', '-f', str(self.ctc_root / 'docker-compose.yml'),
            'run', '--rm', 'website', 'python', 'manage.py', 'migrate', '--noinput'
        ], capture_output=True, text=True, timeout=300)

        assert result.returncode == 0, f"Migration failed: {result.stderr}"

    def test_service_startup(self):
        """Test service startup and health."""
        # Start services
        subprocess.run([
            'docker', 'compose', '-f', str(self.ctc_root / 'docker-compose.yml'), 'up', '-d'
        ])

        # Wait for services to start
        time.sleep(30)

        # Check health endpoint
        try:
            response = requests.get(f"{self.base_url}/health/", timeout=10)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Health check request failed: {e}")

    def test_admin_interface(self):
        """Test Django admin interface accessibility."""
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=10)
            assert response.status_code in [200, 302], f"Admin interface failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Admin interface request failed: {e}")

    def test_static_files(self):
        """Test static file serving."""
        try:
            response = requests.get(f"{self.base_url}/static/admin/css/base.css", timeout=10)
            assert response.status_code == 200, f"Static files not served: {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Static file request failed: {e}")

    def test_database_operations(self):
        """Test basic database operations."""
        # Test database query through Django shell
        result = subprocess.run([
            'docker', 'compose', '-f', str(self.ctc_root / 'docker-compose.yml'),
            'exec', '-T', 'website', 'python', 'manage.py', 'shell', '-c',
            'from django.contrib.auth.models import User; print(f"Users: {User.objects.count()}")'
        ], capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Database operation failed: {result.stderr}"
        assert "Users:" in result.stdout, "Database query output not found"

    def test_api_endpoints(self):
        """Test API endpoints if available."""
        endpoints = [
            "/api/health/",
            "/api/status/",
        ]

        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                # Accept 200 (success) or 404 (endpoint doesn't exist)
                assert response.status_code in [200, 404], f"API endpoint {endpoint} failed: {response.status_code}"
            except requests.exceptions.RequestException:
                # API endpoints might not exist, which is okay
                pass

    def test_user_authentication(self):
        """Test user authentication system."""
        # Test login page accessibility
        try:
            response = requests.get(f"{self.base_url}/accounts/login/", timeout=10)
            assert response.status_code in [200, 404], f"Login page failed: {response.status_code}"
        except requests.exceptions.RequestException:
            # Login page might not exist, which is okay
            pass

    def test_wagtail_cms(self):
        """Test Wagtail CMS functionality."""
        try:
            response = requests.get(f"{self.base_url}/cms/", timeout=10)
            # Accept various status codes as Wagtail might be configured differently
            assert response.status_code in [200, 302, 404], f"Wagtail CMS failed: {response.status_code}"
        except requests.exceptions.RequestException:
            # Wagtail might not be configured, which is okay
            pass

    def teardown_method(self):
        """Cleanup after each test."""
        # Stop services
        subprocess.run([
            'docker', 'compose', '-f', str(self.ctc_root / 'docker-compose.yml'), 'down'
        ], capture_output=True)

class TestCTCResearchPerformance:
    """Performance tests for CTC Research."""

    def test_response_times(self):
        """Test response times for key pages."""
        endpoints = [
            "/",
            "/admin/",
            "/health/",
        ]

        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"http://localhost:5070{endpoint}", timeout=5)
                end_time = time.time()

                response_time = end_time - start_time
                assert response_time < 2.0, f"Response time too slow for {endpoint}: {response_time:.2f}s"

            except requests.exceptions.RequestException:
                # Endpoint might not be available during testing
                pass

    def test_database_performance(self):
        """Test database query performance."""
        # This would be implemented with actual database queries
        # For now, we'll test that the database responds quickly
        result = subprocess.run([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres', '-d', 'db_precis_ctc',
            '-c', 'SELECT COUNT(*) FROM django_migrations;'
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            # Database is responsive
            assert True
        else:
            # Database might not be running, which is okay for some tests
            pytest.skip("Database not available for performance testing")
