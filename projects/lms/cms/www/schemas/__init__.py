"""
API Schemas — Single source of truth for ctc-research ↔ next-LMS API contracts (Pydantic).

Import pattern:
    from www.schemas import (
        PaginatedResponse, SingleResponse, PaginationMeta,
        CourseResponse, CategoryResponse,
        PublicationResponse, TeamMemberResponse,
        LoginRequest, RegisterRequest, AuthTokenResponse, UserResponse,
        ContactRequest, ContactResponse,
        HealthResponse, ErrorResponse,
    )
"""

from www.schemas.core import (  # noqa: F401
    HealthResponse,
    ErrorResponse,
    PaginationMeta,
    PaginatedResponse,
    SingleResponse,
)

from www.schemas.courses import (  # noqa: F401
    CourseResponse,
    CategoryResponse,
)

from www.schemas.research import (  # noqa: F401
    PublicationResponse,
    TeamMemberResponse,
)

from www.schemas.auth import (  # noqa: F401
    LoginRequest,
    RegisterRequest,
    UserResponse,
    AuthTokenResponse,
)

from www.schemas.contact import (  # noqa: F401
    ContactRequest,
    ContactResponse,
)

from www.schemas.site_settings import (  # noqa: F401
    SocialLinkResponse,
    FooterLinkItem,
    FooterLinkGroupResponse,
    SiteIdentityResponse,
    FooterDataResponse,
    SiteSettingsResponse,
)

from www.schemas.blog import (  # noqa: F401
    BlogPostResponse,
    EventResponse,
    TestimonialResponse,
)

from www.schemas.lms import (  # noqa: F401
    FeatureResponse,
    InstructorResponse,
    FaqItem,
    DashboardCounter,
    DashboardResponse,
    ProductResponse,
)
