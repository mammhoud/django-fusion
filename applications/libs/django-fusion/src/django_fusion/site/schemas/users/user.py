"""
Pydantic v2 Schemas for User Model and Operations
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

# Type aliases
UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=150, pattern=r'^[a-zA-Z0-9_]+$')]
PasswordStr = Annotated[str, StringConstraints(min_length=8)]
NameStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
PhoneStr = Annotated[str, StringConstraints(min_length=10, max_length=20, pattern=r'^\+?[0-9\s\-\(\)]+$')]


# ==================== ENUMS ====================

class UserOrderBy(str, Enum):
    """Enum for user ordering options."""
    EMAIL_ASC = "email"
    EMAIL_DESC = "-email"
    NAME_ASC = "name"
    NAME_DESC = "-name"
    DATE_JOINED_ASC = "date_joined"
    DATE_JOINED_DESC = "-date_joined"
    LAST_LOGIN_ASC = "last_login"
    LAST_LOGIN_DESC = "-last_login"
    PROFILE_COMPLETION_ASC = "profile_completion"
    PROFILE_COMPLETION_DESC = "-profile_completion"


class UserStatus(str, Enum):
    """Enum for user status filtering."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    ALL = "all"


class UserRole(str, Enum):
    """Enum for user roles."""
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"
    SUPERUSER = "superuser"


# ==================== BASE SCHEMAS ====================

class GroupSchema(BaseModel):
    """Schema for Django Group."""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class TokenBaseSchema(BaseModel):
    """Base schema for token data."""
    id: Optional[int] = None
    jti: UUID
    token: Optional[str] = None
    token_type: str
    user_id: int
    usage: str = "api"
    session_token: Optional[str] = None
    preferences: List[str] = Field(default_factory=list)
    is_revoked: bool = False
    is_deleted: bool = False
    expires_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserBaseSchema(BaseModel):
    """Base user schema with common fields."""
    id: Optional[int] = None
    email: EmailStr
    name: Optional[NameStr] = None
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[PhoneStr] = None
    
    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    """Schema for user creation."""
    email: EmailStr = Field(..., description="User email address")
    password: PasswordStr = Field(..., description="User password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    name: Optional[NameStr] = Field(None, description="User's full name")
    first_name: Optional[str] = Field(None, max_length=150, description="First name")
    last_name: Optional[str] = Field(None, max_length=150, description="Last name")
    phone_number: Optional[PhoneStr] = Field(None, description="Phone number in international format")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Preferred timezone")
    send_verification_email: bool = Field(True, description="Send email verification")
    groups: Optional[List[int]] = Field(None, description="Group IDs to assign")
    
    @field_validator('email')
    @classmethod
    def validate_email_unique(cls, v: str) -> str:
        """Validate email uniqueness."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=v.lower()).exists():
            raise ValueError('Email already registered')
        return v.lower()
    
    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'UserCreateSchema':
        """Validate that passwords match."""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v:
            # Remove non-digit characters except plus sign
            cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
            if not (10 <= len(cleaned) <= 15):
                raise ValueError('Phone number must be 10-15 digits')
            return cleaned
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code."""
        from django.conf import settings
        valid_languages = [code for code, _ in getattr(settings, 'LANGUAGES', [('en', 'English')])]
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {valid_languages}')
        return v


class UserDetailSchema(UserBaseSchema):
    """Detailed user schema."""
    is_email_verified: bool = Field(False, description="Email verification status")
    email_verified_at: Optional[datetime] = None
    is_phone_verified: bool = Field(False, description="Phone verification status")
    profile_completion: int = Field(0, ge=0, le=100, description="Profile completion percentage")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Preferred timezone")
    is_active: bool = Field(True, description="Account active status")
    is_staff: bool = Field(False, description="Staff status")
    is_admin: bool = Field(False, description="Admin status")
    is_superuser: bool = Field(False, description="Superuser status")
    last_login: Optional[datetime] = None
    date_joined: datetime
    last_password_change: Optional[datetime] = None
    failed_login_attempts: int = Field(0, description="Failed login attempts")
    account_locked_until: Optional[datetime] = None
    groups: List[GroupSchema] = Field(default_factory=list)
    token_id: Optional[int] = Field(None, description="Current refresh token ID")
    
    @field_validator('email_verified_at', 'last_login', 'last_password_change', 'account_locked_until', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime fields."""
        if v is None or isinstance(v, datetime):
            return v
        try:
            return datetime.fromisoformat(v) if isinstance(v, str) else None
        except ValueError:
            return None
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        if self.name:
            return self.name
        elif self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.email.split('@')[0]
    
    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    """Schema for updating user information."""
    name: Optional[NameStr] = Field(None, description="Full name")
    first_name: Optional[str] = Field(None, max_length=150, description="First name")
    last_name: Optional[str] = Field(None, max_length=150, description="Last name")
    phone_number: Optional[PhoneStr] = Field(None, description="Phone number")
    language: Optional[str] = Field(None, description="Preferred language")
    timezone: Optional[str] = Field(None, description="Preferred timezone")
    is_active: Optional[bool] = Field(None, description="Account active status")
    groups: Optional[List[int]] = Field(None, description="Group IDs")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v:
            cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
            if not (10 <= len(cleaned) <= 15):
                raise ValueError('Phone number must be 10-15 digits')
            return cleaned
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code."""
        if v is not None:
            from django.conf import settings
            valid_languages = [code for code, _ in getattr(settings, 'LANGUAGES', [('en', 'English')])]
            if v not in valid_languages:
                raise ValueError(f'Language must be one of: {valid_languages}')
        return v


class UserProfileUpdateSchema(BaseModel):
    """Schema for updating user profile (self-update)."""
    name: Optional[NameStr] = Field(None, description="Full name")
    first_name: Optional[str] = Field(None, max_length=150, description="First name")
    last_name: Optional[str] = Field(None, max_length=150, description="Last name")
    phone_number: Optional[PhoneStr] = Field(None, description="Phone number")
    language: Optional[str] = Field(None, description="Preferred language")
    timezone: Optional[str] = Field(None, description="Preferred timezone")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v:
            cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
            if not (10 <= len(cleaned) <= 15):
                raise ValueError('Phone number must be 10-15 digits')
            return cleaned
        return v


class ChangePasswordSchema(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(..., description="Current password")
    new_password: PasswordStr = Field(..., description="New password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @model_validator(mode='after')
    def validate_passwords(self) -> 'ChangePasswordSchema':
        """Validate passwords."""
        if self.new_password != self.confirm_password:
            raise ValueError('New passwords do not match')
        if self.current_password == self.new_password:
            raise ValueError('New password must be different from current password')
        return self


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirmSchema(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: PasswordStr = Field(..., description="New password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'PasswordResetConfirmSchema':
        """Validate that passwords match."""
        if self.new_password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class EmailVerificationRequestSchema(BaseModel):
    """Schema for email verification request."""
    email: EmailStr = Field(..., description="Email to verify")


class EmailVerificationConfirmSchema(BaseModel):
    """Schema for email verification confirmation."""
    token: str = Field(..., description="Email verification token")


# ==================== FILTER SCHEMAS ====================

class UserFilterSchema(BaseModel):
    """Schema for filtering users."""
    search: Optional[str] = Field(None, description="Search query")
    email: Optional[EmailStr] = Field(None, description="Filter by email")
    name: Optional[str] = Field(None, description="Filter by name")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_email_verified: Optional[bool] = Field(None, description="Filter by email verification")
    is_staff: Optional[bool] = Field(None, description="Filter by staff status")
    is_admin: Optional[bool] = Field(None, description="Filter by admin status")
    is_superuser: Optional[bool] = Field(None, description="Filter by superuser status")
    language: Optional[str] = Field(None, description="Filter by language")
    group_id: Optional[int] = Field(None, description="Filter by group ID")
    group_name: Optional[str] = Field(None, description="Filter by group name")
    date_joined_from: Optional[datetime] = Field(None, description="Date joined from")
    date_joined_to: Optional[datetime] = Field(None, description="Date joined to")
    last_login_from: Optional[datetime] = Field(None, description="Last login from")
    last_login_to: Optional[datetime] = Field(None, description="Last login to")
    profile_completion_min: Optional[int] = Field(None, ge=0, le=100, description="Min profile completion")
    profile_completion_max: Optional[int] = Field(None, ge=0, le=100, description="Max profile completion")
    
    @field_validator('profile_completion_max')
    @classmethod
    def validate_profile_completion_range(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        """Validate profile completion range."""
        if v is not None and info.data.get('profile_completion_min') is not None:
            if v < info.data['profile_completion_min']:
                raise ValueError('profile_completion_max must be >= profile_completion_min')
        return v


class UserOrderSchema(BaseModel):
    """Schema for ordering users."""
    order_by: UserOrderBy = Field(UserOrderBy.DATE_JOINED_DESC, description="Order by field")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for pagination."""
        return (self.page - 1) * self.page_size


# ==================== AUTHENTICATION SCHEMAS ====================

class LoginSchema(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    remember_me: bool = Field(False, description="Remember login session")


class RegisterSchema(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email")
    password: PasswordStr = Field(..., description="Password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    name: Optional[NameStr] = Field(None, description="Full name")
    first_name: Optional[str] = Field(None, max_length=150, description="First name")
    last_name: Optional[str] = Field(None, max_length=150, description="Last name")
    phone_number: Optional[PhoneStr] = Field(None, description="Phone number")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Preferred timezone")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    auto_login: bool = Field(True, description="Automatically login after registration")
    send_verification_email: bool = Field(True, description="Send verification email")
    
    @model_validator(mode='after')
    def validate_registration(self) -> 'RegisterSchema':
        """Validate registration data."""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        
        # Check email uniqueness
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=self.email.lower()).exists():
            raise ValueError('Email already registered')
        
        return self


class EnableDisableUserSchema(BaseModel):
    """Schema for enabling/disabling users."""
    user_id: int = Field(..., description="User ID")
    action: str = Field(..., description="Action: enable or disable")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate action."""
        if v not in ['enable', 'disable']:
            raise ValueError('Action must be either "enable" or "disable"')
        return v


class EnableDisableUserResponseSchema(BaseModel):
    """Response schema for enable/disable operations."""
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="User ID")
    new_status: bool = Field(..., description="New active status")
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== RESPONSE SCHEMAS ====================

class LoginResponseSchema(BaseModel):
    """Schema for login response."""
    user: UserDetailSchema = Field(..., description="User information")
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    access_token_expires: datetime = Field(..., description="Access token expiration")
    refresh_token_expires: datetime = Field(..., description="Refresh token expiration")
    token_type: str = Field("Bearer", description="Token type")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    requires_verification: bool = Field(False, description="Email verification required")
    session_id: Optional[str] = Field(None, description="Session identifier")


class RegisterResponseSchema(BaseModel):
    """Schema for registration response."""
    user: UserDetailSchema = Field(..., description="User information")
    tokens: Optional[LoginResponseSchema] = Field(None, description="Authentication tokens")
    verification_required: bool = Field(..., description="Email verification required")
    verification_sent: bool = Field(..., description="Verification email sent")
    message: str = Field(..., description="Response message")


class PaginatedResponseSchema(BaseModel):
    """Schema for paginated responses."""
    count: int = Field(..., description="Total number of items")
    next: Optional[int] = Field(None, description="Next page number")
    previous: Optional[int] = Field(None, description="Previous page number")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    results: List[Any] = Field(..., description="List of items")
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total_count: int,
        page: int,
        page_size: int
    ) -> 'PaginatedResponseSchema':
        """Create paginated response."""
        total_pages = (total_count + page_size - 1) // page_size
        
        return cls(
            count=total_count,
            next=page + 1 if page < total_pages else None,
            previous=page - 1 if page > 1 else None,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            results=items,
        )


class UserListResponseSchema(PaginatedResponseSchema):
    """Schema for user list response."""
    results: List[UserDetailSchema] = Field(..., description="List of users")


class TokenResponseSchema(BaseModel):
    """Schema for token response."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    
    @classmethod
    def success(cls, data: Optional[Dict[str, Any]] = None) -> 'TokenResponseSchema':
        """Create success response."""
        return cls(success=True, data=data or {})
    
    @classmethod
    def error(cls, error: str, code: Optional[str] = None) -> 'TokenResponseSchema':
        """Create error response."""
        return cls(success=False, error=error, code=code or "UNKNOWN_ERROR")


class ProfileCompletionSchema(BaseModel):
    """Schema for profile completion details."""
    total: int = Field(..., ge=0, le=100, description="Total completion percentage")
    details: Dict[str, bool] = Field(..., description="Completion details")
    missing_fields: List[str] = Field(default_factory=list, description="Missing required fields")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class UserStatisticsSchema(BaseModel):
    """Schema for user statistics."""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Active users")
    verified_users: int = Field(..., description="Email verified users")
    staff_users: int = Field(..., description="Staff users")
    admin_users: int = Field(..., description="Admin users")
    superuser_users: int = Field(..., description="Superuser users")
    verification_rate: float = Field(..., ge=0, le=100, description="Email verification rate")
    avg_profile_completion: float = Field(..., ge=0, le=100, description="Average profile completion")
    registrations_today: int = Field(..., description="Registrations today")
    active_today: int = Field(..., description="Users active today")
    generated_at: datetime = Field(default_factory=datetime.now)


class UserExportRequestSchema(BaseModel):
    """Schema for user export request."""
    format: str = Field("csv", description="Export format: csv, json, excel")
    include_inactive: bool = Field(False, description="Include inactive users")
    fields: List[str] = Field(
        default_factory=lambda: ["id", "email", "name", "is_active", "date_joined"],
        description="Fields to include"
    )
    filters: Optional[UserFilterSchema] = Field(None, description="Filter criteria")


class UserBulkOperationSchema(BaseModel):
    """Schema for bulk user operations."""
    user_ids: List[int] = Field(..., description="User IDs to operate on")
    action: str = Field(..., description="Action: activate, deactivate, delete, send_verification")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate bulk action."""
        allowed_actions = ['activate', 'deactivate', 'delete', 'send_verification', 'assign_group']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {allowed_actions}')
        return v


class UserBulkOperationResponseSchema(BaseModel):
    """Schema for bulk operation response."""
    action: str = Field(..., description="Action performed")
    total: int = Field(..., description="Total users processed")
    successful: int = Field(..., description="Successful operations")
    failed: int = Field(..., description="Failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now)


# ==================== TOKEN SCHEMAS ====================

class TokenSchema(TokenBaseSchema):
    """Detailed token schema."""
    user: Optional[UserDetailSchema] = Field(None, description="Token owner")
    parent_token: Optional[TokenBaseSchema] = Field(None, description="Parent token")
    children: List[TokenBaseSchema] = Field(default_factory=list, description="Child tokens")
    
    class Config:
        from_attributes = True


class TokenRefreshSchema(BaseModel):
    """Schema for token refresh."""
    refresh_token: str = Field(..., description="Refresh token")
    usage: str = Field("api", description="New token usage")


class TokenRevokeSchema(BaseModel):
    """Schema for token revocation."""
    token: Optional[str] = Field(None, description="Specific token to revoke")
    all_tokens: bool = Field(False, description="Revoke all user tokens")
    session_token: Optional[str] = Field(None, description="Revoke session tokens")
    
    @model_validator(mode='after')
    def validate_input(self) -> 'TokenRevokeSchema':
        """Validate that at least one revocation method is specified."""
        if not self.token and not self.all_tokens and not self.session_token:
            raise ValueError('Must specify at least one revocation method')
        return self


class TokenListResponseSchema(PaginatedResponseSchema):
    """Schema for token list response."""
    results: List[TokenSchema] = Field(..., description="List of tokens")


# ==================== EVENT & WEBHOOK SCHEMAS ====================

class UserEventSchema(BaseModel):
    """Schema for user events."""
    event_type: str = Field(..., description="Event type")
    user_id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    timestamp: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")


class WebhookUserEventSchema(BaseModel):
    """Schema for webhook user events."""
    event: str = Field(..., description="Event name")
    data: UserEventSchema = Field(..., description="Event data")
    webhook_id: str = Field(..., description="Webhook identifier")
    signature: Optional[str] = Field(None, description="Event signature")
    timestamp: datetime = Field(default_factory=datetime.now)
