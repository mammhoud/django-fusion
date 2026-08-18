"""Tests for DesignerMCPRouter auth dependency (API-key + localhost fallback)."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

pytest.importorskip("django_bolt")

from django_bolt.exceptions import HTTPException
from django_bolt.testing import TestClient
from django_fusion.plugins.designer.mcp_router import DesignerMCPRouter, _DesignerAuth

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(*, api_key: str | None = None, base_url: str = "http://testserver.local") -> TestClient:
    """Create a django-bolt TestClient for a designer-equipped API."""
    api = DesignerMCPRouter(api_key=api_key).api
    return TestClient(api, base_url=base_url, read_django_settings=False)


# ---------------------------------------------------------------------------
# API-key mode — accept / reject
# ---------------------------------------------------------------------------


class TestAPIKeyMode:
    """With an API key configured, every designer endpoint requires X-API-Key."""

    def test_no_header_rejected_get(self):
        client = _make_client(api_key="secret")
        resp = client.get("/designer/tools")
        assert resp.status_code == 403
        assert "Invalid or missing X-API-Key" in resp.text

    def test_no_header_rejected_post(self):
        client = _make_client(api_key="secret")
        resp = client.post("/designer/tools/call", json={"jsonrpc": "2.0", "method": "tools/call", "params": {}})
        assert resp.status_code == 403

    def test_wrong_key_rejected(self):
        client = _make_client(api_key="secret")
        resp = client.get("/designer/tools", headers={"X-API-Key": "wrong"})
        assert resp.status_code == 403

    def test_correct_key_accepted_get(self):
        client = _make_client(api_key="secret")
        resp = client.get("/designer/tools", headers={"X-API-Key": "secret"})
        # 503 because django-fusion designer module isn't loaded in test env,
        # but the important part is auth passed (not 403).
        assert resp.status_code != 403

    def test_correct_key_accepted_post(self):
        client = _make_client(api_key="secret")
        resp = client.post(
            "/designer/tools/call",
            json={"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "designer.preview", "arguments": {"name": "test"}}},
            headers={"X-API-Key": "secret"},
        )
        # 404 or 500 from handler — just verify auth passed
        assert resp.status_code != 403

    def test_correct_key_works_across_endpoints(self):
        """All 6 GET endpoints accept the correct key."""
        client = _make_client(api_key="secret")
        endpoints = [
            "/designer/tools",
            "/designer/component-catalog",
            "/designer/wagtail-field?field_type=char&name=test",
            "/designer/form-scaffold?class_name=TestForm",
            "/designer/table-scaffold?class_name=TestTable",
            "/designer/preview?name=test",
        ]
        for path in endpoints:
            resp = client.get(path, headers={"X-API-Key": "secret"})
            assert resp.status_code != 403, f"{path} unexpectedly rejected"


# ---------------------------------------------------------------------------
# Localhost fallback mode
# ---------------------------------------------------------------------------


class TestLocalhostFallback:
    """With no API key configured, non-localhost callers are rejected."""

    def test_non_localhost_rejected_without_key(self):
        """Host header 'testserver.local' is not localhost → 403."""
        client = _make_client()  # no api_key
        resp = client.get("/designer/tools")
        assert resp.status_code == 403
        assert "API-key authentication" in resp.text

    def test_localhost_allowed_without_key(self):
        """Host header '127.0.0.1' is localhost → auth passes."""
        client = _make_client(base_url="http://127.0.0.1")
        resp = client.get("/designer/tools")
        assert resp.status_code != 403


# ---------------------------------------------------------------------------
# Env-var resolution
# ---------------------------------------------------------------------------


class TestEnvVarResolution:
    """The designer resolves FUSION_MCP_DESIGNER_API_KEY from the environment."""

    @patch.dict(os.environ, {"FUSION_MCP_DESIGNER_API_KEY": "env-secret"}, clear=False)
    def test_env_key_used_when_no_constructor_arg(self):
        client = _make_client()  # no api_key kwarg
        resp = client.get("/designer/tools")
        assert resp.status_code == 403  # no header but key is configured
        resp2 = client.get("/designer/tools", headers={"X-API-Key": "env-secret"})
        assert resp2.status_code != 403

    def test_constructor_key_overrides_env(self):
        with patch.dict(os.environ, {"FUSION_MCP_DESIGNER_API_KEY": "env-key"}, clear=False):
            client = _make_client(api_key="explicit-key")
            resp = client.get("/designer/tools", headers={"X-API-Key": "env-key"})
            assert resp.status_code == 403  # env key rejected when explicit key set
            resp2 = client.get("/designer/tools", headers={"X-API-Key": "explicit-key"})
            assert resp2.status_code != 403

    @patch.dict(os.environ, {}, clear=True)
    def test_no_key_no_env_non_localhost_rejected(self):
        """With no key anywhere, a non-localhost host is rejected."""
        client = _make_client()
        resp = client.get("/designer/tools")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# _DesignerAuth unit tests
# ---------------------------------------------------------------------------


class TestDesignerAuthIsolation:
    """Direct unit tests on _DesignerAuth without routing."""

    def test_localhost_passes_no_key(self):
        auth = _DesignerAuth()  # no key
        auth({"headers": {"host": "127.0.0.1:8002"}})  # should not raise

    def test_remote_fails_no_key(self):
        auth = _DesignerAuth()
        with pytest.raises(HTTPException, match="API-key authentication"):
            auth({"headers": {"host": "10.0.0.1:8002"}})

    def test_remote_passes_with_key(self):
        auth = _DesignerAuth(api_key="secret")
        auth({"headers": {"host": "10.0.0.1:8002", "x-api-key": "secret"}})  # should not raise

    def test_remote_fails_wrong_key(self):
        auth = _DesignerAuth(api_key="secret")
        with pytest.raises(HTTPException, match="Invalid or missing"):
            auth({"headers": {"host": "10.0.0.1:8002", "x-api-key": "wrong"}})
