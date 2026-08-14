"""Tests for the safe django-fusion MCP designer surface."""

import json
from types import SimpleNamespace

import pytest
from django.template import Engine
from django.test import RequestFactory
from django_fusion.comp._init import Component, components
from django_fusion.plugins.designer.handlers import (
    designer_component_catalog,
    designer_form_scaffold,
    designer_preview,
    designer_table_scaffold,
    designer_validate,
    designer_wagtail_field,
)
from django_fusion.plugins.designer.tools import MCP_DESIGNER_TOOLS
from django_fusion.plugins.designer.views import (
    designer_tools_call,
    designer_tools_list,
)


@pytest.fixture(autouse=True)
def reset_components():
    original = dict(components._components)
    original_ambiguous = set(components._ambiguous_aliases)
    components.reset()
    yield
    components.reset()
    components._components.update(original)
    components._ambiguous_aliases.update(original_ambiguous)


def _user(*, authenticated=True, staff=False, superuser=False):
    return SimpleNamespace(
        is_authenticated=authenticated,
        is_staff=staff,
        is_superuser=superuser,
    )


def test_catalog_exposes_registered_components_only():
    template = SimpleNamespace(template=Engine().from_string("<p>{{ props.title }}</p>"))
    components.register(Component("hero", template, frozenset()))

    result = designer_component_catalog(query="hero")

    assert result["count"] == 1
    assert result["components"][0]["name"] == "hero"


def test_wagtail_field_is_schema_driven_and_does_not_apply_changes():
    result = designer_wagtail_field(
        field_type="choice",
        name="audience",
        choices=[["all", "Everyone"]],
        required=True,
    )

    assert result["field"]["class"] == "ChoiceBlock"
    assert result["field"]["kwargs"]["choices"] == [["all", "Everyone"]]
    assert result["write_required"] is True


def test_form_scaffold_rejects_unsafe_identifiers():
    with pytest.raises(ValueError, match="Python identifier"):
        designer_form_scaffold("Bad;Form", [])


def test_form_and_table_scaffolds_are_deterministic_review_only_code():
    form = designer_form_scaffold(
        "SignupForm",
        [{"name": "email", "type": "email", "required": True}],
    )
    table = designer_table_scaffold(
        "UserTable",
        [{"name": "email", "label": "Email", "orderable": True}],
    )

    assert "email = forms.EmailField" in form["code"]
    assert "email = tables.Column" in table["code"]
    assert form["write_required"] is True
    assert table["write_required"] is True


def test_validate_returns_non_applied_result():
    result = designer_validate(
        {"kind": "django_form", "class_name": "ContactForm", "fields": []}
    )

    assert result["valid"] is True
    assert result["applied"] is False


def test_validate_wagtail_field_ignores_dispatch_kind():
    result = designer_validate(
        {"kind": "wagtail_field", "field_type": "char", "name": "title"}
    )

    assert result["valid"] is True
    assert result["draft"]["field"]["name"] == "title"


def test_scaffolds_reject_unapproved_base_classes():
    with pytest.raises(ValueError, match="approved"):
        designer_form_scaffold("ContactForm", [], base="UserForm")
    with pytest.raises(ValueError, match="approved"):
        designer_table_scaffold("UserTable", [], base="SecretTable")


def test_preview_accepts_registered_component_and_json_props_only():
    template = SimpleNamespace(template=Engine().from_string("<p>{{ props.title }}</p>"))
    components.register(Component("hero", template, frozenset()))

    result = designer_preview("hero", {"title": "Hello"})

    assert result["html"] == "<p>Hello</p>"
    assert "raw template" in result["security_note"]


def test_preview_rejects_unregistered_template_name():
    with pytest.raises(ValueError, match="registered component"):
        designer_preview("{{ unsafe }}")


def test_preview_rejects_non_json_props():
    template = SimpleNamespace(template=Engine().from_string("<p>ok</p>"))
    components.register(Component("hero", template, frozenset()))

    with pytest.raises(ValueError, match="JSON-compatible"):
        designer_preview("hero", {"object": object()})
    with pytest.raises(ValueError, match="props must be an object"):
        designer_preview("hero", False)


def test_tool_metadata_uses_mcp_input_schemas_and_read_only_annotations():
    assert set(MCP_DESIGNER_TOOLS) == {
        "designer.component_catalog",
        "designer.website_audit",
        "designer.webapp_enhancement_plan",
        "designer.wagtail_field",
        "designer.form_scaffold",
        "designer.table_scaffold",
        "designer.validate",
        "designer.preview",
    }
    for tool in MCP_DESIGNER_TOOLS.values():
        assert tool["inputSchema"]["type"] == "object"
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["destructiveHint"] is False


def test_endpoint_requires_staff_user():
    request = RequestFactory().post("/designer/tools/")
    request.user = _user(authenticated=False)

    response = designer_tools_list(request)

    assert response.status_code == 403


def test_endpoint_lists_tools_for_staff_user():
    request = RequestFactory().post(
        "/designer/tools/",
        data='{"jsonrpc":"2.0","method":"tools/list","id":1}',
        content_type="application/json",
    )
    request.user = _user(staff=True)

    response = designer_tools_list(request)

    assert response.status_code == 200
    payload = json.loads(response.content)
    assert payload["jsonrpc"] == "2.0"
    assert len(payload["result"]["tools"]) == len(MCP_DESIGNER_TOOLS)


def test_tools_list_requires_standard_json_rpc_request():
    request = RequestFactory().post(
        "/designer/tools/",
        data='{"jsonrpc":"2.0","method":"tools/list","id":3}',
        content_type="application/json",
    )
    request.user = _user(staff=True)

    response = designer_tools_list(request)
    payload = json.loads(response.content)

    assert response.status_code == 200
    assert payload["result"]["tools"]


def test_endpoint_rejects_non_json_rpc_requests():
    request = RequestFactory().post(
        "/designer/call/",
        data='{"id":7,"params":{"name":"designer.component_catalog","arguments":{}}}',
        content_type="application/json",
    )
    request.user = _user(staff=True)

    response = designer_tools_call(request)

    assert response.status_code == 400
    assert "jsonrpc" in json.loads(response.content)["error"]["message"]


def test_endpoint_rejects_unknown_method():
    request = RequestFactory().post(
        "/designer/call/",
        data='{"jsonrpc":"2.0","method":"tools/list","id":7,"params":{}}',
        content_type="application/json",
    )
    request.user = _user(staff=True)

    response = designer_tools_call(request)

    assert response.status_code == 400
    assert "method" in json.loads(response.content)["error"]["message"]


def test_endpoint_rejects_malformed_params_and_arguments():
    for body, message in (
        (
            {"jsonrpc": "2.0", "method": "tools/call", "id": 8, "params": []},
            "params must be an object",
        ),
        (
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 9,
                "params": {"name": "designer.component_catalog", "arguments": []},
            },
            "arguments must be an object",
        ),
    ):
        request = RequestFactory().post(
            "/designer/call/",
            data=json.dumps(body),
            content_type="application/json",
        )
        request.user = _user(staff=True)

        response = designer_tools_call(request)

        assert response.status_code == 400
        assert message in json.loads(response.content)["error"]["message"]


def test_endpoint_calls_catalog_for_staff_user():
    request = RequestFactory().post(
        "/designer/call/",
        data='{"jsonrpc":"2.0","method":"tools/call","id":7,"params":{"name":"designer.component_catalog","arguments":{}}}',
        content_type="application/json",
    )
    request.user = _user(staff=True)

    response = designer_tools_call(request)

    assert response.status_code == 200
    payload = json.loads(response.content)
    assert payload["id"] == 7
    assert "components" in payload["result"]
