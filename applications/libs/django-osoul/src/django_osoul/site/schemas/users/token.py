"""
Pydantic Schemas for Token Service
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Optional as OptionalType
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator

logger = logging.getLogger(__name__)

# ============================================
# PYDANTIC SCHEMAS
# ============================================

class TokenSchemaBase(BaseModel):
    """Base token schema."""
    jti: UUID
    token_type: str
    exp: datetime
    created_at: datetime
    last_used: OptionalType[datetime] = None
    usage: str
    is_active: bool

class AccessTokenSchema(TokenSchemaBase):
    """Access token schema."""
    token: str
    expires_in: int  # Seconds until expiration

class RefreshTokenSchema(TokenSchemaBase):
    """Refresh token schema."""
    token: str
    max_age: int  # Maximum age in seconds
    can_slide: bool = False

class SimpleTokenSchema(BaseModel):
    """Simple 8-character token schema."""
    token: str
    display_token: str  # Masked version for display
    created_at: datetime
    expires_at: OptionalType[datetime] = None
    last_used: OptionalType[datetime] = None
    usage: str
    is_active: bool
    can_regenerate: bool = True

class TokenListResponse(BaseModel):
    """Response for listing tokens."""
    user_id: int
    access_tokens: List[AccessTokenSchema] = []
    refresh_tokens: List[RefreshTokenSchema] = []
    simple_tokens: List[SimpleTokenSchema] = []
    active_sessions: int = 0

class TokenPairResponse(BaseModel):
    """Response for token pair (access + refresh)."""
    access_token: AccessTokenSchema
    refresh_token: RefreshTokenSchema
    expires_in: int
    token_type: str = "Bearer"

class SimpleTokenCreateResponse(BaseModel):
    """Response for simple token creation."""
    token: SimpleTokenSchema
    raw_token: str  # Only shown once!
    message: str = "Store this token securely. It won't be shown again."

class TokenBase(BaseModel):
    """Base schema for token data."""
    id: Optional[int] = None
    jti: UUID
    token: str
    token_type: str
    user_id: int
    is_revoked: bool = False
    is_deleted: bool = False
    expires_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage: str = "api"
    session_token: Optional[str] = None
    preferences: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class AccessTokenCreate(BaseModel):
    """Schema for creating access tokens."""
    user_id: int = Field(..., description="User ID for whom the token is created")
    usage: str = Field("api", description="Token usage context: api, web, mobile")
    session_token: Optional[str] = Field(None, description="Session identifier")
    preferences: Optional[List[str]] = Field(None, description="Token preferences")
    expires_in: int = Field(3600, description="Token lifetime in seconds", gt=0)
    
    @validator('usage')
    def validate_usage(cls, v):
        allowed_usages = ['api', 'web', 'mobile']
        if v not in allowed_usages:
            raise ValueError(f'Usage must be one of: {allowed_usages}')
        return v


class RefreshTokenCreate(BaseModel):
    """Schema for creating refresh tokens."""
    user_id: int = Field(..., description="User ID for whom the token is created")
    usage: str = Field("api", description="Token usage context: api, web, mobile")
    session_token: Optional[str] = Field(None, description="Session identifier")
    preferences: Optional[List[str]] = Field(None, description="Token preferences")
    expires_in: int = Field(604800, description="Token lifetime in seconds (7 days)", gt=0)
    
    @validator('usage')
    def validate_usage(cls, v):
        allowed_usages = ['api', 'web', 'mobile']
        if v not in allowed_usages:
            raise ValueError(f'Usage must be one of: {allowed_usages}')
        return v


class TokenPair(BaseModel):
    """Schema for token pair response (access + refresh tokens)."""
    access_token: str = Field(..., description="Access token string")
    refresh_token: str = Field(..., description="Refresh token string")
    access_token_expires: datetime = Field(..., description="Access token expiration datetime")
    refresh_token_expires: datetime = Field(..., description="Refresh token expiration datetime")
    token_type: str = Field("Bearer", description="Token type for Authorization header")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenValidationResult(BaseModel):
    """Schema for token validation result."""
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: Optional[int] = Field(None, description="User ID from token")
    token_type: Optional[str] = Field(None, description="Type of token (access, refresh, etc.)")
    expires_at: Optional[datetime] = Field(None, description="Token expiration datetime")
    error: Optional[str] = Field(None, description="Error message if validation failed")
    code: Optional[str] = Field(None, description="Error code if validation failed")
    cached: bool = Field(False, description="Whether the result came from cache")
    validated_at: Optional[datetime] = Field(None, description="When validation was performed")
    
    @validator('valid')
    def validate_result(cls, v, values):
        if v and not values.get('user_id'):
            raise ValueError("Valid token must have user_id")
        return v
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class ActionTokenCreate(BaseModel):
    """Schema for creating action tokens (password reset, email verification, etc.)."""
    user_id: int = Field(..., description="User ID for the action")
    action: str = Field(..., description="Action type: verify_email, reset_password, etc.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    expires_in: int = Field(300, description="Token lifetime in seconds", gt=0)
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['verify_email', 'reset_password', 'change_email', 'two_factor', 'delete_account']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {allowed_actions}')
        return v


class ActionTokenResult(BaseModel):
    """Schema for action token generation result."""
    token: str = Field(..., description="Generated token string")
    token_id: UUID = Field(..., description="Token unique identifier (jti)")
    action: str = Field(..., description="Action type")
    expires_at: datetime = Field(..., description="Token expiration datetime")
    expires_in: int = Field(..., description="Token lifetime in seconds")
    user_id: int = Field(..., description="User ID")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class EmailVerificationToken(BaseModel):
    """Schema for email verification token data."""
    email: EmailStr = Field(..., description="Email address to verify")
    user_id: int = Field(..., description="User ID")
    expires_at: datetime = Field(..., description="Token expiration datetime")
    token: Optional[str] = Field(None, description="Generated token string")
    token_id: Optional[UUID] = Field(None, description="Token unique identifier")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenResponse(BaseModel):
    """Generic token response schema."""
    success: bool = Field(..., description="Operation success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    code: Optional[str] = Field(None, description="Error code if operation failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})
    
    @classmethod
    def success_response(cls, data: Dict[str, Any] = None) -> 'TokenResponse':
        """Create a success response."""
        return cls(
            success=True,
            data=data or {},
            timestamp=datetime.now()
        )
    
    @classmethod
    def error_response(cls, error: str, code: str = None, data: Dict[str, Any] = None) -> 'TokenResponse':
        """Create an error response."""
        return cls(
            success=False,
            error=error,
            code=code or "UNKNOWN_ERROR",
            data=data or {},
            timestamp=datetime.now()
        )


class UserTokensResponse(BaseModel):
    """Schema for user tokens list response."""
    count: int = Field(..., description="Total number of tokens")
    tokens: List[Dict[str, Any]] = Field(..., description="List of token data")
    active_count: int = Field(..., description="Number of active (non-revoked) tokens")
    user_id: Optional[int] = Field(None, description="User ID")
    
    @validator('tokens')
    def validate_tokens(cls, v):
        # Ensure each token has required fields
        for token in v:
            if 'token_type' not in token:
                raise ValueError("Each token must have a token_type")
            if 'expires_at' not in token:
                raise ValueError("Each token must have an expires_at")
        return v


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Refresh token string")
    usage: Optional[str] = Field("api", description="New token usage context")


class TokenRevokeRequest(BaseModel):
    """Schema for token revocation request."""
    token: Optional[str] = Field(None, description="Specific token to revoke")
    all_tokens: bool = Field(False, description="Revoke all user tokens")
    session_token: Optional[str] = Field(None, description="Revoke all tokens for session")
    
    @validator('token')
    def validate_token(cls, v, values):
        if not v and not values.get('all_tokens') and not values.get('session_token'):
            raise ValueError("Either token, all_tokens, or session_token must be provided")
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User email address")
    redirect_url: Optional[str] = Field(None, description="Password reset redirect URL")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    email: EmailStr = Field(..., description="Email to verify")
    user_id: Optional[int] = Field(None, description="User ID (optional)")


class EmailVerificationConfirm(BaseModel):
    """Schema for email verification confirmation."""
    token: str = Field(..., description="Email verification token")


class TokenStatistics(BaseModel):
    """Schema for token statistics."""
    total: int = Field(..., description="Total number of tokens")
    active: int = Field(..., description="Number of active tokens")
    expired: int = Field(..., description="Number of expired tokens")
    revoked: int = Field(..., description="Number of revoked tokens")
    by_type: Dict[str, int] = Field(..., description="Tokens count by type")
    by_usage: Dict[str, int] = Field(..., description="Tokens count by usage")
    generated_at: datetime = Field(..., description="When statistics were generated")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class AuthenticatedUser(BaseModel):
    """Schema for authenticated user data."""
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User's full name")
    is_email_verified: bool = Field(..., description="Email verification status")
    is_active: bool = Field(..., description="User account status")
    profile_completion: int = Field(..., ge=0, le=100, description="Profile completion percentage")
    
    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    user: AuthenticatedUser = Field(..., description="Authenticated user data")
    tokens: TokenPair = Field(..., description="Generated tokens")
    requires_verification: bool = Field(False, description="Whether email verification is required")
    message: Optional[str] = Field(None, description="Additional message")


class JWTClaims(BaseModel):
    """Schema for JWT token claims."""
    user_id: int = Field(..., description="User ID")
    token_type: str = Field(..., description="Token type")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    jti: UUID = Field(..., description="JWT ID")
    usage: Optional[str] = Field(None, description="Token usage")
    refresh_jti: Optional[UUID] = Field(None, description="Parent refresh token JWT ID")
    action: Optional[str] = Field(None, description="Action type for action tokens")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('token_type')
    def validate_token_type(cls, v):
        allowed_types = ['access', 'refresh', 'action', 'email_verification']
        if v not in allowed_types:
            raise ValueError(f'Token type must be one of: {allowed_types}')
        return v


class TokenCacheData(BaseModel):
    """Schema for cached token data."""
    token: str = Field(..., description="Token string")
    user_id: int = Field(..., description="User ID")
    valid: bool = Field(..., description="Token validity")
    validated_at: datetime = Field(..., description="When validation was performed")
    expires_at: Optional[datetime] = Field(None, description="When cache entry expires")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class BulkTokenOperation(BaseModel):
    """Schema for bulk token operations."""
    user_ids: Optional[List[int]] = Field(None, description="List of user IDs")
    token_type: Optional[str] = Field(None, description="Filter by token type")
    before_date: Optional[datetime] = Field(None, description="Filter tokens issued before date")
    action: str = Field(..., description="Operation action: revoke, delete, cleanup")
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['revoke', 'delete', 'cleanup']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {allowed_actions}')
        return v


class WebhookTokenEvent(BaseModel):
    """Schema for webhook token events."""
    event_type: str = Field(..., description="Event type")
    token_id: UUID = Field(..., description="Token JWT ID")
    user_id: int = Field(..., description="User ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})

