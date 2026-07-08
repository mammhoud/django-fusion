"""
Token utilities.

Canonical import: from django_fusion.core.utils.token import generate_token, validate_token, decode_token
"""

import time
from typing import Any, Dict, Optional

try:
    from jose import JWTError, jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


def generate_token(
    payload: Dict[str, Any],
    secret: str,
    algorithm: str = "HS256",
    expires_in: int = 3600,
) -> str:
    """
    Generate JWT token.
    """
    if not JWT_AVAILABLE:
        raise ImportError("python-jose is required for token generation")

    payload = payload.copy()
    payload.update({
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()),
    })

    return jwt.encode(payload, secret, algorithm=algorithm)


def validate_token(
    token: str,
    secret: str,
    algorithms: list = None,
) -> Dict[str, Any]:
    """
    Validate JWT token.
    """
    if not JWT_AVAILABLE:
        raise ImportError("python-jose is required for token validation")

    algorithms = algorithms or ["HS256"]

    try:
        payload = jwt.decode(token, secret, algorithms=algorithms)
        return {"valid": True, "payload": payload}
    except JWTError as e:
        return {"valid": False, "error": str(e)}


def decode_token(
    token: str,
    secret: Optional[str] = None,
    algorithms: list = None,
    verify: bool = True,
) -> Dict[str, Any]:
    """
    Decode JWT token.
    """
    if not JWT_AVAILABLE:
        raise ImportError("python-jose is required for token decoding")

    algorithms = algorithms or ["HS256"]

    if verify and not secret:
        raise ValueError("Secret required for token verification")

    try:
        if verify:
            payload = jwt.decode(token, secret, algorithms=algorithms)
        else:
            # Decode without verification
            payload = jwt.get_unverified_claims(token)

        return {"success": True, "payload": payload}
    except JWTError as e:
        return {"success": False, "error": str(e)}
