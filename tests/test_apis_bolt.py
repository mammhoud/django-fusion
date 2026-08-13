"""Tests for the optional django-fusion Bolt API plugin."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django_fusion.plugins.apis.auth import (
    BoltTokenConfig,
    FusionTokenError,
    TokenUserError,
    extract_bearer_token,
    token_payload,
    user_token_payload,
    verify_token_user,
)
from django_fusion.plugins.apis.bolt import build_bolt_api, is_bolt_installed


def test_bolt_stub_is_detected_as_unavailable_or_real_runtime_is_usable():
    api = build_bolt_api()
    if is_bolt_installed():
        assert api is not None
        assert callable(api.get)
    else:
        assert api is None


def test_extract_bearer_token_is_case_insensitive():
    assert extract_bearer_token({"authorization": "Bearer abc"}) == "abc"
    assert extract_bearer_token({"Authorization": "Bearer xyz"}) == "xyz"
    assert extract_bearer_token({"Authorization": "Basic abc"}) is None
    assert extract_bearer_token({}) is None


def test_token_config_does_not_issue_without_a_secret():
    with pytest.raises(FusionTokenError, match="SECRET"):
        BoltTokenConfig(secret="").issue("user-1")


def test_token_payload_round_trip_when_jwt_is_installed():
    pytest.importorskip("jwt")
    config = BoltTokenConfig(secret="test-secret-with-at-least-32-bytes", issuer="tests", ttl_seconds=120)
    result = token_payload("user-1", role="admin", config=config)

    assert result["token_type"] == "Bearer"
    assert result["expires_in"] == 120
    assert result["role"] == "admin"
    claims = config.decode(result["token"])
    assert claims["sub"] == "user-1"
    assert claims["role"] == "admin"
    assert claims["iss"] == "tests"


def test_user_token_verification_requires_a_live_django_user():
    pytest.importorskip("jwt")
    config = BoltTokenConfig(secret="test-secret-with-at-least-32-bytes", issuer="tests")
    user = User.objects.create_user(username="fusion-user", email="fusion@example.com")
    token = user_token_payload(user, config=config)["token"]
    assert verify_token_user(token, config=config).pk == user.pk

    user.is_active = False
    user.save(update_fields=["is_active"])
    with pytest.raises(TokenUserError, match="inactive"):
        verify_token_user(token, config=config)


def test_token_payload_allows_a_bounded_ttl_override():
    pytest.importorskip("jwt")
    config = BoltTokenConfig(secret="test-secret-with-at-least-32-bytes", ttl_seconds=120)
    result = token_payload("user-1", ttl_seconds=300, config=config)
    assert result["expires_in"] == 300
