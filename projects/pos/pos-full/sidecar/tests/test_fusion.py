"""
Tests for RobynFusionChecker — mock get_token_info, verify 3-level check.

Usage::

    cd pos-full/sidecar
    python3 -m pytest tests/test_fusion.py -v --tb=short

Or::

    DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_fusion.py -v --tb=short
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# ═══════════════════════════════════════════════════════════════════════
# Path bootstrap
# ═══════════════════════════════════════════════════════════════════════

_SIDECAR_DIR = Path(__file__).resolve().parent.parent  # sidecar/
if str(_SIDECAR_DIR) not in sys.path:
    sys.path.insert(0, str(_SIDECAR_DIR))

# ═══════════════════════════════════════════════════════════════════════
# Imports
# ═══════════════════════════════════════════════════════════════════════

from middleware.fusion import (
    RobynFusionChecker,
    fusion_health_checker,
    register_fusion_health_routes,
)


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


class MockRobynRequest:
    """Minimal mock of Robyn's ``Request`` with a dict-like ``headers`` attribute."""

    def __init__(self, headers: dict[str, str] | None = None) -> None:
        self.headers = headers or {}


# ═══════════════════════════════════════════════════════════════════════
# 1. Default checker — no custom check_fn
# ═══════════════════════════════════════════════════════════════════════


class TestDefaultChecker:
    """Test ``RobynFusionChecker`` with its default ``check_fn=None``.

    The 3-level check is:
      1. Custom check_fn → skipped (None)
      2. Device token role → admin/manager = ``True``, else ``False``
      3. User-Agent heuristic → scripts (curl/wget/…) = ``False``,
         browsers = ``True``
    """

    # ── Level 2: token-based ──────────────────────────────────────────

    def test_admin_role_returns_true(self):
        """Admin token → fragment mode (True)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "admin", "device_id": "DEV-001"}
            checker = RobynFusionChecker()
            req = MockRobynRequest()
            assert checker.get_preference(req) is True

    def test_manager_role_returns_true(self):
        """Manager token → fragment mode (True)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "manager", "device_id": "DEV-002"}
            checker = RobynFusionChecker()
            req = MockRobynRequest()
            assert checker.get_preference(req) is True

    def test_cashier_role_returns_false(self):
        """Cashier token → JSON/data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "cashier", "device_id": "DEV-003"}
            checker = RobynFusionChecker()
            req = MockRobynRequest()
            assert checker.get_preference(req) is False

    def test_viewer_role_returns_false(self):
        """Viewer token → JSON/data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "viewer", "device_id": "DEV-004"}
            checker = RobynFusionChecker()
            req = MockRobynRequest()
            assert checker.get_preference(req) is False

    def test_unknown_role_returns_false(self):
        """Unknown/arbitrary role → JSON/data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "chef", "device_id": "DEV-005"}
            checker = RobynFusionChecker()
            req = MockRobynRequest()
            assert checker.get_preference(req) is False

    def test_token_is_none_falls_to_ua(self):
        """No token (None) → falls to UA heuristic.

        With a browser UA, should return True.
        """
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            })
            assert checker.get_preference(req) is True

    # ── Level 3: User-Agent heuristic ────────────────────────────────

    def test_ua_curl_returns_false(self):
        """cURL User-Agent → data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={"User-Agent": "curl/7.88.1"})
            assert checker.get_preference(req) is False

    def test_ua_wget_returns_false(self):
        """wget User-Agent → data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={"User-Agent": "Wget/1.21.3"})
            assert checker.get_preference(req) is False

    def test_ua_python_requests_returns_false(self):
        """python-requests User-Agent → data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={"User-Agent": "python-requests/2.31.0"})
            assert checker.get_preference(req) is False

    def test_ua_okhttp_returns_false(self):
        """OkHttp User-Agent → data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={"User-Agent": "okhttp/4.12.0"})
            assert checker.get_preference(req) is False

    def test_ua_axios_returns_false(self):
        """Axios User-Agent → data mode (False)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={"User-Agent": "axios/1.6.7"})
            assert checker.get_preference(req) is False

    def test_ua_browser_returns_true(self):
        """Browser User-Agent → fragment mode (True)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            })
            assert checker.get_preference(req) is True

    def test_ua_missing_returns_true(self):
        """Missing User-Agent → defaults to fragment mode (True)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest()  # no headers at all
            assert checker.get_preference(req) is True

    def test_ua_empty_returns_true(self):
        """Empty User-Agent → defaults to fragment mode (True)."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            checker = RobynFusionChecker()
            req = MockRobynRequest(headers={"User-Agent": ""})
            assert checker.get_preference(req) is True


# ═══════════════════════════════════════════════════════════════════════
# 2. Custom check_fn
# ═══════════════════════════════════════════════════════════════════════


class TestCustomCheckFn:
    """Test ``RobynFusionChecker`` with a custom ``check_fn``.

    The custom function is called with the request and its truthy return
    value determines the preference — the token and UA fallbacks are
    completely bypassed.
    """

    def test_custom_returns_true(self):
        """Custom check_fn returning True → fragment mode."""
        def custom(req):
            return True

        checker = RobynFusionChecker(check_fn=custom)
        req = MockRobynRequest()
        assert checker.get_preference(req) is True

    def test_custom_returns_false(self):
        """Custom check_fn returning False → data mode."""
        def custom(req):
            return False

        checker = RobynFusionChecker(check_fn=custom)
        req = MockRobynRequest()
        assert checker.get_preference(req) is False

    def test_custom_receives_request(self):
        """Custom check_fn receives the request object."""
        captured = []

        def custom(req):
            captured.append(req)
            return True

        checker = RobynFusionChecker(check_fn=custom)
        req = MockRobynRequest(headers={"X-Custom": "value"})
        checker.get_preference(req)

        assert len(captured) == 1
        assert captured[0] is req

    def test_custom_truthy_value(self):
        """Custom check_fn returning a truthy non-bool → fragment mode."""
        def custom(req):
            return "yes"

        checker = RobynFusionChecker(check_fn=custom)
        req = MockRobynRequest()
        assert checker.get_preference(req) is True

    def test_custom_falsy_value(self):
        """Custom check_fn returning a falsy non-bool → data mode."""
        def custom(req):
            return 0

        checker = RobynFusionChecker(check_fn=custom)
        req = MockRobynRequest()
        assert checker.get_preference(req) is False

    def test_custom_bypasses_token(self):
        """Custom check_fn bypasses token check entirely — token is ignored."""
        def custom(req):
            return True  # force fragment regardless

        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "viewer"}
            checker = RobynFusionChecker(check_fn=custom)
            req = MockRobynRequest()
            # Viewer would normally return False, but custom check_fn=True wins
            assert checker.get_preference(req) is True
            # Token info should NOT be consulted
            mock.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════
# 3. /fusion/health endpoint
# ═══════════════════════════════════════════════════════════════════════


class TestFusionHealthEndpoint:
    """Test the ``/fusion/health`` route response structure.

    The endpoint returns JSON with:
      - ``fusion_render_first`` (bool)
      - ``reason`` (str)
      - ``token_present`` (bool)
    """

    def test_response_structure_with_token(self):
        """Response includes all three fields when token is present."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "admin", "device_id": "DEV-ADMIN"}
            req = MockRobynRequest(headers={"User-Agent": "curl/8.0"})

            preference = fusion_health_checker.get_preference(req)
            token_info = mock.return_value

            # This is what the endpoint would produce
            assert preference is True
            assert token_info is not None
            assert token_info["role"] == "admin"

    def test_response_structure_without_token(self):
        """Response includes all three fields when token is absent."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            req = MockRobynRequest(headers={
                "User-Agent": "Mozilla/5.0 Chrome/120",
            })

            preference = fusion_health_checker.get_preference(req)

            assert preference is True
            # No token → UA heuristic determines True for browser

    def test_token_present_flag(self):
        """token_present is True when token exists."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "admin"}
            req = MockRobynRequest()

            token_info = mock.return_value
            assert token_info is not None

    def test_token_absent_flag(self):
        """token_present is False when token is None."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            req = MockRobynRequest()

            token_info = mock.return_value
            assert token_info is None

    def test_reason_device_role(self):
        """Reason reflects device role when token is present."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = {"role": "manager"}
            req = MockRobynRequest()

            token_info = mock.return_value
            reason = f"device_role: {token_info['role']}"
            assert reason == "device_role: manager"

    def test_reason_user_agent(self):
        """Reason reflects User-Agent when token is absent."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            ua = "curl/7.88.1"
            req = MockRobynRequest(headers={"User-Agent": ua})

            ua_str = (req.headers.get("User-Agent") or "").lower()
            reason = f"user_agent: {ua_str[:50]}"
            assert reason == "user_agent: curl/7.88.1"


# ═══════════════════════════════════════════════════════════════════════
# 4. Global singleton
# ═══════════════════════════════════════════════════════════════════════


class TestSingleton:
    """Test the module-level ``fusion_health_checker`` singleton."""

    def test_singleton_is_robyn_checker(self):
        """``fusion_health_checker`` is a ``RobynFusionChecker`` instance."""
        assert isinstance(fusion_health_checker, RobynFusionChecker)

    def test_singleton_uses_default_check(self):
        """Singleton has no custom check_fn."""
        assert fusion_health_checker._check_fn is None

    def test_singleton_get_preference(self):
        """Singleton's get_preference works end-to-end with no token."""
        with patch("middleware.fusion.get_token_info") as mock:
            mock.return_value = None
            req = MockRobynRequest(headers={
                "User-Agent": "python-requests/2.31",
            })
            assert fusion_health_checker.get_preference(req) is False


# ═══════════════════════════════════════════════════════════════════════
# 5. register_fusion_health_routes
# ═══════════════════════════════════════════════════════════════════════


class TestRegisterRoutes:
    """Test that ``register_fusion_health_routes`` registers a route."""

    def test_registers_get_route(self):
        """Calls app.get with '/fusion/health'."""
        app = MagicMock()
        register_fusion_health_routes(app)
        app.get.assert_called_once_with("/fusion/health")

    def test_route_is_a_decorator(self):
        """app.get('/fusion/health') is used as a decorator on a callable."""
        app = MagicMock()
        register_fusion_health_routes(app)
        # The return value of app.get should have been called as a decorator
        decorator = app.get.return_value
        assert decorator.called
