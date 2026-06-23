"""
Additional Utility Schemas for Advanced Token Operations
"""

from enum import Enum
from typing import Literal, Optional


class TokenStatus(str, Enum):
    """Enum for token status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DELETED = "deleted"


class TokenUsageStats(BaseModel):
    """Schema for token usage statistics."""
    token_type: str
    count: int
    active_count: int
    avg_lifetime: Optional[float] = Field(None, description="Average lifetime in seconds")
    most_common_usage: Optional[str] = Field(None, description="Most common usage pattern")
    
    @validator('avg_lifetime')
    def format_avg_lifetime(cls, v):
        if v:
            return round(v, 2)
        return v


class UserTokenSummary(BaseModel):
    """Schema for user token summary."""
    user_id: int
    email: EmailStr
    total_tokens: int
    active_tokens: int
    has_valid_refresh_token: bool
    last_token_activity: Optional[datetime]
    token_types: Dict[str, int]
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenAuditLog(BaseModel):
    """Schema for token audit log entry."""
    id: int
    token_id: UUID
    user_id: int
    action: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    details: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda dt: dt.isoformat()})


class RateLimitInfo(BaseModel):
    """Schema for rate limiting information."""
    limit: int = Field(..., description="Maximum allowed requests")
    remaining: int = Field(..., description="Remaining requests")
    reset_time: datetime = Field(..., description="When the rate limit resets")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenSecurityCheck(BaseModel):
    """Schema for token security assessment."""
    token_id: UUID
    security_score: int = Field(..., ge=0, le=100, description="Security score out of 100")
    issues: List[str] = Field(default_factory=list, description="Security issues found")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    last_security_check: datetime = Field(..., description="When security check was performed")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class MultiFactorAuthRequest(BaseModel):
    """Schema for multi-factor authentication request."""
    user_id: int
    method: Literal['email', 'sms', 'app']
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    ip_address: Optional[str] = Field(None, description="Client IP address")


class MultiFactorAuthResponse(BaseModel):
    """Schema for multi-factor authentication response."""
    success: bool
    token: Optional[str] = Field(None, description="MFA token")
    expires_at: Optional[datetime] = Field(None, description="MFA token expiration")
    delivery_method: Optional[str] = Field(None, description="How MFA was delivered")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class SessionInfo(BaseModel):
    """Schema for session information."""
    session_id: str
    user_id: int
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_type: Optional[str]
    active_tokens: int
    is_current: bool = Field(False, description="Whether this is the current session")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenHealthCheck(BaseModel):
    """Schema for token system health check."""
    database: bool = Field(..., description="Database connectivity")
    cache: bool = Field(..., description="Cache connectivity")
    jwt_signing: bool = Field(..., description="JWT signing capability")
    total_tokens: int = Field(..., description="Total tokens in system")
    expired_tokens: int = Field(..., description="Number of expired tokens")
    avg_response_time: Optional[float] = Field(None, description="Average response time in ms")
    last_cleanup: Optional[datetime] = Field(None, description="Last cleanup operation")
    status: Literal['healthy', 'degraded', 'unhealthy']
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenExportFormat(str, Enum):
    """Enum for token export formats."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class TokenExportRequest(BaseModel):
    """Schema for token export request."""
    user_id: Optional[int] = Field(None, description="Export tokens for specific user")
    token_type: Optional[str] = Field(None, description="Filter by token type")
    date_from: Optional[datetime] = Field(None, description="Export tokens from date")
    date_to: Optional[datetime] = Field(None, description="Export tokens to date")
    format: TokenExportFormat = Field(TokenExportFormat.JSON, description="Export format")
    include_revoked: bool = Field(False, description="Include revoked tokens")
    include_expired: bool = Field(False, description="Include expired tokens")
    
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})


class TokenImportRequest(BaseModel):
    """Schema for token import request."""
    tokens: List[Dict[str, Any]] = Field(..., description="Tokens to import")
    skip_existing: bool = Field(True, description="Skip tokens that already exist")
    validate_before_import: bool = Field(True, description="Validate tokens before import")


class BatchTokenOperationResult(BaseModel):
    """Schema for batch token operation result."""
    total: int = Field(..., description="Total operations attempted")
    successful: int = Field(..., description="Successful operations")
    failed: int = Field(..., description="Failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details")
    duration: float = Field(..., description="Operation duration in seconds")