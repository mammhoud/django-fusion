"""In-process authenticated endpoint coverage for the optional Bolt runtime."""

from __future__ import annotations

import time

import jwt
import pytest
from django_bolt.auth import IsAuthenticated
from django_bolt.testing import AsyncTestClient
from django_fusion.plugins.apis.auth import BoltTokenConfig
from django_fusion.plugins.apis.bolt import build_bolt_api


@pytest.mark.asyncio
async def test_authenticated_bolt_endpoint_accepts_jwt_and_api_key():
    secret = "in-process-bolt-test-secret-with-32-bytes"
    api_key = "in-process-api-key"
    api = build_bolt_api(
        prefix="/bolt",
        title="Fusion In-process Test API",
        token_config=BoltTokenConfig(secret=secret, api_key=api_key),
    )
    assert api is not None
    auth_backends = api.fusion_auth

    @api.get("/protected", auth=auth_backends, guards=[IsAuthenticated()])
    async def protected(request):
        return {"authenticated": True}

    async with AsyncTestClient(api, read_django_settings=False) as client:
        anonymous = await client.get("/bolt/protected")
        assert anonymous.status_code in (401, 403)

        api_key_response = await client.get(
            "/bolt/protected",
            headers={"X-API-Key": api_key},
        )
        assert api_key_response.status_code == 200
        assert api_key_response.json() == {"authenticated": True}

        now = int(time.time())
        token = jwt.encode(
            {
                "sub": "fusion-test-user",
                "iat": now,
                "exp": now + 300,
            },
            secret,
            algorithm="HS256",
        )
        jwt_response = await client.get(
            "/bolt/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert jwt_response.status_code == 200
        assert jwt_response.json() == {"authenticated": True}
