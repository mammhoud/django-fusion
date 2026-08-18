"""Tests for the hardened django-fusion task MCP HTTP surface.

Covers the authorization policy (bearer token → staff → DEBUG), JSON-RPC
body validation, and the no-token production denial — the production-hardening
gates from ``django-fusion-tasks-mcp-plan.md`` §6.4.
"""
from __future__ import annotations

from types import SimpleNamespace

from django.test import override_settings

from django_fusion.tasks.mcp_views import _authorize, _validate_body, mcp_tools_list


def _request(*, auth: str | None = None, user=None, remote_ip: str = "10.0.0.1"):
    meta = {"REMOTE_ADDR": remote_ip}
    if auth:
        meta["HTTP_AUTHORIZATION"] = auth
    return SimpleNamespace(META=meta, user=user)


class TestValidateBody:
    def test_valid_call_body(self):
        parsed = _validate_body(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 7,
                "params": {"name": "task.queues", "arguments": {}},
            }
        )
        assert parsed["tool_name"] == "task.queues"
        assert parsed["arguments"] == {}
        assert parsed["id"] == 7

    def test_missing_name_rejected(self):
        assert "error" in _validate_body({"jsonrpc": "2.0", "params": {"arguments": {}}})

    def test_wrong_jsonrpc_rejected(self):
        assert "error" in _validate_body({"jsonrpc": "1.0", "params": {"name": "task.queues"}})

    def test_non_object_body_rejected(self):
        assert "error" in _validate_body(["not", "an", "object"])

    def test_non_dict_arguments_rejected(self):
        assert "error" in _validate_body(
            {"jsonrpc": "2.0", "params": {"name": "task.queues", "arguments": [1, 2]}}
        )

    def test_unsupported_method_rejected(self):
        assert "error" in _validate_body(
            {"jsonrpc": "2.0", "method": "initialize", "params": {"name": "task.queues"}}
        )


class TestAuthorize:
    @override_settings(FUSION_MCP_TOKEN="secret", DEBUG=False)
    def test_correct_bearer_accepted(self):
        assert _authorize(_request(auth="Bearer secret")) is None

    @override_settings(FUSION_MCP_TOKEN="secret", DEBUG=False)
    def test_wrong_bearer_rejected(self):
        assert _authorize(_request(auth="Bearer wrong")).status_code == 401

    @override_settings(FUSION_MCP_TOKEN="secret", DEBUG=False)
    def test_missing_bearer_rejected(self):
        assert _authorize(_request()).status_code == 401

    @override_settings(FUSION_MCP_TOKEN="", DEBUG=False)
    def test_staff_session_accepted_without_token(self):
        user = SimpleNamespace(is_authenticated=True, is_staff=True)
        assert _authorize(_request(user=user)) is None

    @override_settings(FUSION_MCP_TOKEN="", DEBUG=False)
    def test_non_staff_denied_without_token_in_production(self):
        user = SimpleNamespace(is_authenticated=True, is_staff=False)
        assert _authorize(_request(user=user)).status_code == 401

    @override_settings(FUSION_MCP_TOKEN="", DEBUG=True)
    def test_debug_fallback_accepted_without_token(self):
        assert _authorize(_request()) is None


class TestToolsList:
    def test_returns_full_tool_definitions(self):
        import json

        with override_settings(FUSION_MCP_TOKEN="secret", DEBUG=False):
            response = mcp_tools_list(_request(auth="Bearer secret"))
        tools = json.loads(response.content)["tools"]
        assert isinstance(tools, list)
        assert tools, "expected a non-empty tool list"
        for tool in tools:
            assert set(tool) == {"name", "description", "inputSchema"}
        names = {tool["name"] for tool in tools}
        assert "task.inspect" in names
        assert "task.workers" in names

    @override_settings(FUSION_MCP_TOKEN="secret", DEBUG=False)
    def test_list_requires_auth(self):
        assert mcp_tools_list(_request()).status_code == 401
