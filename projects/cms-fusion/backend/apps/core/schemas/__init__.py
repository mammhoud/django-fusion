"""
API Schemas — Single source of truth for fusion-cms ↔ next-LMS API contracts (Pydantic).

Import pattern:
    from apps.core.schemas import (
        PaginatedResponse, SingleResponse, PaginationMeta,
        CourseResponse, CategoryResponse,
        PublicationResponse, TeamMemberResponse,
        LoginRequest, RegisterRequest, AuthTokenResponse, UserResponse,
        ContactRequest, ContactResponse,
        HealthResponse, ErrorResponse,
    )
"""

from apps.core.schemas.auth import (  # noqa: F401
    AuthRefreshRequest,
    AuthRefreshResponse,
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from apps.core.schemas.blog import (  # noqa: F401
    BlogPostResponse,
    EventResponse,
    TestimonialResponse,
)
from apps.core.schemas.contact import (  # noqa: F401
    ContactRequest,
    ContactResponse,
)
from apps.core.schemas.core import (  # noqa: F401
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    PaginationMeta,
    SingleResponse,
)
from apps.core.schemas.courses import (  # noqa: F401
    CategoryResponse,
    CourseResponse,
)
from apps.core.schemas.enrollment import (  # noqa: F401
    CreateEnrollmentRequest,
    DashboardDataResponse,
    EnrollmentResponse,
    MyEnrollmentsResponse,
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
    ProgressEntryResponse,
    ProgressUpdateRequest,
)
from apps.core.schemas.lms import (  # noqa: F401
    DashboardCounter,
    DashboardResponse,
    FaqItem,
    FeatureResponse,
    InstructorResponse,
    ProductResponse,
)
from apps.core.schemas.research import (  # noqa: F401
    PublicationResponse,
    TeamMemberResponse,
)
from apps.core.schemas.site_settings import (  # noqa: F401
    FooterDataResponse,
    FooterLinkGroupResponse,
    FooterLinkItem,
    SiteIdentityResponse,
    SiteSettingsResponse,
    SocialLinkResponse,
)
