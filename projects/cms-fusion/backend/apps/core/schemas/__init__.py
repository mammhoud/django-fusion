"""
API Schemas — Single source of truth for ctc-research ↔ next-LMS API contracts (Pydantic).

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

from apps.core.schemas.core import (  # noqa: F401
    HealthResponse,
    ErrorResponse,
    PaginationMeta,
    PaginatedResponse,
    SingleResponse,
)

from apps.core.schemas.courses import (  # noqa: F401
    CourseResponse,
    CategoryResponse,
)

from apps.core.schemas.research import (  # noqa: F401
    PublicationResponse,
    TeamMemberResponse,
)

from apps.core.schemas.auth import (  # noqa: F401
    LoginRequest,
    RegisterRequest,
    UserResponse,
    AuthTokenResponse,
    AuthRefreshRequest,
    AuthRefreshResponse,
)

from apps.core.schemas.contact import (  # noqa: F401
    ContactRequest,
    ContactResponse,
)

from apps.core.schemas.site_settings import (  # noqa: F401
    SocialLinkResponse,
    FooterLinkItem,
    FooterLinkGroupResponse,
    SiteIdentityResponse,
    FooterDataResponse,
    SiteSettingsResponse,
)

from apps.core.schemas.blog import (  # noqa: F401
    BlogPostResponse,
    EventResponse,
    TestimonialResponse,
)

from apps.core.schemas.enrollment import (  # noqa: F401
    EnrollmentResponse,
    CreateEnrollmentRequest,
    MyEnrollmentsResponse,
    ProgressEntryResponse,
    ProgressUpdateRequest,
    DashboardDataResponse,
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)

from apps.core.schemas.lms import (  # noqa: F401
    FeatureResponse,
    InstructorResponse,
    FaqItem,
    DashboardCounter,
    DashboardResponse,
    ProductResponse,
)
