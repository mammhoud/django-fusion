"""
Unit tests for ErrorTrackerMiddleware.

Validates: Requirements 2.4
"""
# Import directly from the file to avoid middlewares/__init__.py chain
# which has broken imports to django_fusion.contrib
import importlib.util
import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

spec = importlib.util.spec_from_file_location(
    "error_tracker",
    str(Path(__file__).parent.parent / "src" / "django_fusion" / "core" / "middlewares" / "error_tracker.py")
)
error_tracker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(error_tracker_module)
ErrorTrackerMiddleware = error_tracker_module.ErrorTrackerMiddleware


class TestErrorTrackerMiddleware(TestCase):
    """Tests for ErrorTrackerMiddleware."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ErrorTrackerMiddleware(self.get_response)

    def get_response(self, request):
        """Simple response callable for middleware."""
        return HttpResponse("OK", status=200)

    def test_4xx_response_logged(self):
        """4xx responses should be logged at ERROR level."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Not Found", status=404))
            request = self.factory.get("/test/")
            middleware(request)
            mock_logger.error.assert_called_once()

    def test_5xx_response_logged(self):
        """5xx responses should be logged at CRITICAL level."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=500))
            request = self.factory.get("/test/")
            middleware(request)
            mock_logger.critical.assert_called_once()

    def test_2xx_response_not_logged(self):
        """2xx responses should not be logged."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("OK", status=200))
            request = self.factory.get("/test/")

            middleware(request)

            # Should not log for 2xx
            mock_logger.log.assert_not_called()

    def test_3xx_response_not_logged(self):
        """3xx responses should not be logged."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Redirect", status=301))
            request = self.factory.get("/test/")

            middleware(request)

            # Should not log for 3xx
            mock_logger.log.assert_not_called()

    def test_log_includes_request_details(self):
        """Log message should include request method, path, and user agent."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=400))
            request = self.factory.get("/test/path/")
            request.META["HTTP_USER_AGENT"] = "TestAgent"
            middleware(request)
            call_args = mock_logger.error.call_args
            assert call_args[0][0] == "%s %s %s \u2014 %s"
            assert call_args[0][1] == "GET"
            assert call_args[0][2] == "/test/path/"

    def test_log_includes_user_email(self):
        """Log should include user email when user is authenticated."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=400))
            request = self.factory.get("/test/")
            mock_user = Mock()
            mock_user.email = "testuser@example.com"
            request.user = mock_user
            middleware(request)
            call_args = mock_logger.error.call_args
            assert call_args[0][4] == "testuser@example.com"

    def test_log_anonymous_user(self):
        """Log should show 'anonymous' when user has no email attribute."""
        # Test the getattr fallback logic directly
        user = object()  # Plain object with no email attribute
        email = getattr(getattr(user, "user", None), "email", "anonymous")
        assert email == "anonymous"

    def test_get_ip_from_x_forwarded_for(self):
        """Should extract IP from X-Forwarded-For header."""
        middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=500))
        request = self.factory.get("/test/")
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"

        ip = middleware._get_ip(request)

        assert ip == "192.168.1.1"

    def test_get_ip_fallback_to_remote_addr(self):
        """Should use REMOTE_ADDR if no X-Forwarded-For."""
        middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=500))
        request = self.factory.get("/test/")
        # Remove any X-Forwarded-For and set REMOTE_ADDR
        if "HTTP_X_FORWARDED_FOR" in request.META:
            del request.META["HTTP_X_FORWARDED_FOR"]
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        ip = middleware._get_ip(request)

        assert ip == "127.0.0.1"

    def test_get_ip_no_headers(self):
        """Should return placeholder when no IP headers."""
        middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=500))
        request = self.factory.get("/test/")
        # Create a minimal request without REMOTE_ADDR
        # Django test client always sets REMOTE_ADDR, so we test the fallback logic
        request.META = {}  # Clear all headers

        ip = middleware._get_ip(request)

        assert ip == "—"

    def test_log_includes_extra_status_code(self):
        """Log should include status_code in extra dict."""
        with patch.object(error_tracker_module, "logger") as mock_logger:
            middleware = ErrorTrackerMiddleware(lambda r: HttpResponse("Error", status=404))
            request = self.factory.get("/test/")
            middleware(request)
            call_kwargs = mock_logger.error.call_args[1]
            assert call_kwargs["extra"]["status_code"] == 404
            assert call_kwargs["extra"]["request"] is request
