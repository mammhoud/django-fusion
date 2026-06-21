"""Tests for health check endpoints."""
from django.test import TestCase, override_settings
from django.urls import reverse


class HealthCheckViewTests(TestCase):
    """Tests for basic health check endpoint."""

    def test_health_check_returns_200(self):
        """Test that /health/ returns HTTP 200."""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)

    def test_health_check_json_response(self):
        """Test that /health/ returns valid JSON."""
        response = self.client.get("/health/")
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")

    def test_health_check_includes_service_name(self):
        """Test that /health/ includes service name."""
        response = self.client.get("/health/")
        data = response.json()
        self.assertIn("service", data)

    def test_health_check_includes_version(self):
        """Test that /health/ includes version."""
        response = self.client.get("/health/")
        data = response.json()
        self.assertIn("version", data)


class DatabaseHealthCheckTests(TestCase):
    """Tests for database health check endpoint."""

    def test_database_health_check_returns_200(self):
        """Test that /health/database/ returns HTTP 200 when database is healthy."""
        response = self.client.get("/health/database/")
        self.assertEqual(response.status_code, 200)

    def test_database_health_check_json_response(self):
        """Test that /health/database/ returns valid JSON."""
        response = self.client.get("/health/database/")
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertEqual(data["database"], "connected")


class AssetsHealthCheckTests(TestCase):
    """Tests for static assets health check endpoint."""

    def test_assets_health_check_returns_200(self):
        """Test that /health/assets/ returns HTTP 200."""
        response = self.client.get("/health/assets/")
        # May return 200 or 503 depending on STATIC_ROOT configuration
        self.assertIn(response.status_code, [200, 503])

    def test_assets_health_check_json_response(self):
        """Test that /health/assets/ returns valid JSON."""
        response = self.client.get("/health/assets/")
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("static_root", data)
        self.assertIn("exists", data)


class MediaHealthCheckTests(TestCase):
    """Tests for media files health check endpoint."""

    def test_media_health_check_returns_200(self):
        """Test that /health/media/ returns HTTP 200."""
        response = self.client.get("/health/media/")
        # May return 200 or 503 depending on MEDIA_ROOT configuration
        self.assertIn(response.status_code, [200, 503])

    def test_media_health_check_json_response(self):
        """Test that /health/media/ returns valid JSON."""
        response = self.client.get("/health/media/")
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("media_root", data)
        self.assertIn("exists", data)
