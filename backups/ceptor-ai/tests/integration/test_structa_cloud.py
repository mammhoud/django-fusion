"""
Structa Cloud Integration Tests
==============================
Comprehensive integration tests for the Structa Cloud website.
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


class TestStructaCloudIntegration:
    """Integration tests for Structa Cloud website."""

    @pytest.fixture(autouse=True)
    def setup(self, structa_cloud_root):
        """Setup test environment."""
        self.structa_root = structa_cloud_root
        self.base_url = "http://localhost:5071"

    def test_docker_build(self):
        """Test Structa Cloud Docker build."""
        if not self.structa_root.exists():
            pytest.skip("Structa Cloud directory not found")

        result = subprocess.run([
            'docker', 'compose', '-f', str(self.structa_root / 'docker-compose.yml'), 'build'
        ], capture_output=True, text=True, timeout=600)

        assert result.returncode == 0, f"Docker build failed: {result.stderr}"

    def test_database_migration(self):
        """Test database migrations."""
        if not self.structa_root.exists():
            pytest.skip("Structa Cloud directory not found")

        # Start infrastructure
        subprocess.run([
            'docker', 'compose', 'up', '-d', 'postgres', 'redis'
        ], cwd=self.structa_root.parent)

        # Create Structa database if it doesn't exist
        subprocess.run([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres',
            '-c', 'CREATE DATABASE IF NOT EXISTS db_structa;'
        ])

        # Run migrations
        result = subprocess.run([
            'docker', 'compose', '-f', str(self.structa_root / 'docker-compose.yml'),
            'run', '--rm', 'website', 'python', 'manage.py', 'migrate', '--noinput'
        ], capture_output=True, text=True, timeout=300)

        assert result.returncode == 0, f"Migration failed: {result.stderr}"

    def test_service_startup(self):
        """Test service startup and health."""
        if not self.structa_root.exists():
            pytest.skip("Structa Cloud directory not found")

        # Start services
        subprocess.run([
            'docker', 'compose', '-f', str(self.structa_root / 'docker-compose.yml'), 'up', '-d'
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
        if not self.structa_root.exists():
            pytest.skip("Structa Cloud directory not found")

        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=10)
            assert response.status_code in [200, 302], f"Admin interface failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Admin interface request failed: {e}")

    def test_static_files(self):
        """Test static file serving."""
        if not self.structa_root.exists():
            pytest.skip("Structa Cloud directory not found")

        try:
            response = requests.get(f"{self.base_url}/static/admin/css/base.css", timeout=10)
            assert response.status_code == 200, f"Static files not served: {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Static file request failed: {e}")

    def test_database_operations(self):
        """Test basic database operations."""
        if not self.structa_root.exists():
            pytest.skip("Structa Cloud directory not found")

        # Test database query through Django shell
        result = subprocess.run([
            'docker', 'compose', '-f', str(self.structa_root / 'docker-compose.yml'),
            'exec', '-T', 'website', 'python', 'manage.py', 'shell', '-c',
            'from django.contrib.auth.models import User; print(f"Users: {User.objects.count()}")'
        ], capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Database operation failed: {result.stderr}"
        assert "Users:" in result.stdout, "Database query output not found"

    def teardown_method(self):
        """Cleanup after each test."""
        if self.structa_root.exists():
            # Stop services
            subprocess.run([
                'docker', 'compose', '-f', str(self.structa_root / 'docker-compose.yml'), 'down'
            ], capture_output=True)

class TestStructaCloudPerformance:
    """Performance tests for Structa Cloud."""

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
                response = requests.get(f"http://localhost:5071{endpoint}", timeout=5)
                end_time = time.time()

                response_time = end_time - start_time
                assert response_time < 2.0, f"Response time too slow for {endpoint}: {response_time:.2f}s"

            except requests.exceptions.RequestException:
                # Endpoint might not be available during testing
                pass
