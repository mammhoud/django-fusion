"""
Auth API schemas — Login, Register, JWT token response (Pydantic).

Endpoints:
    POST /apis/auth/login     → AuthTokenResponse | ErrorResponse (401)
    POST /apis/auth/register  → AuthTokenResponse (201) | ErrorResponse (400, 409)
    POST /apis/auth/refresh   → AuthRefreshResponse | ErrorResponse (401)
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """POST /apis/auth/login request body."""

    email: str
    password: str


class RegisterRequest(BaseModel):
    """POST /apis/auth/register request body."""

    email: str
    password: str
    first_name: str = ""
    last_name: str = ""


class UserResponse(BaseModel):
    """User info embedded in auth responses."""

    id: int
    email: str
    username: str = ""
    first_name: str = ""
    last_name: str = ""


class AuthTokenResponse(BaseModel):
    """Successful auth response (login or register) — JWT tokens."""

    access: str
    refresh: str
    user: UserResponse
    expires_in: int = 1800


class AuthRefreshRequest(BaseModel):
    """POST /apis/auth/refresh request body."""

    refresh: str


class AuthRefreshResponse(BaseModel):
    """Successful token refresh response."""

    access: str
    expires_in: int = 1800
