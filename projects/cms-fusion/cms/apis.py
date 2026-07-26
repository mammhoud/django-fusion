"""
ctc-research — django-bolt API server (bolt-exclusive, no DRF).

High-performance REST API backed by Rust's Actix Web engine (60k+ RPS).
Uses bolt-native token management with Pydantic schema contracts.

Architecture:
    next-LMS (Next.js, port 3000) → django-bolt (ctc-research, port 8087)
        → Django ORM → SQLite/PostgreSQL

Schema contracts: www/schemas/ — single source of truth for API shapes (Pydantic).
TypeScript mirror: websites/next-lms/src/types/api-schema.d.ts

Auth: www/auth.py — TokenAuthBackend validates Bearer tokens from the Token table.
"""

from __future__ import annotations

import json

from django_bolt import BoltAPI

from www.auth import (
    JWTTokenAuthBackend, TokenAuthBackend,
    extract_bearer_token, authenticate_request,
    issue_jwt_tokens, authenticate_jwt_request,
    _jwt_decode, jwt_get_user_from_payload,
)


# ── Query param helper (works with both Django HttpRequest and bolt PyRequest) ──
def _qp(request, key: str, default: str = "") -> str:
    """Get a query parameter from a request, compatible with both Django and bolt PyRequest."""
    if hasattr(request, "query"):
        return request.query.get(key, default)
    if hasattr(request, "GET"):
        return request.GET.get(key, default)
    return default


def _qp_int(request, key: str, default: int = 1) -> int:
    """Get an integer query parameter safely."""
    try:
        return int(_qp(request, key, str(default)))
    except (TypeError, ValueError):
        return default

bolt = BoltAPI(
    prefix="/apis",
    namespace="ctc-research-bolt",
    title="CTC Research API",
    version="1.0.0",
    description="High-performance API for CTC Research — serves next-LMS frontend",
)



# ═══════════════════════════════════════════════════════════════════════════
# Health
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/health")
def health_check(request):
    """GET /apis/health — Health check."""
    from www.schemas import HealthResponse
    return HealthResponse().model_dump()


# ═══════════════════════════════════════════════════════════════════════════
# Research — Publications
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/research/publications")
def list_publications(request):
    """GET /apis/research/publications — Paginated publications."""
    from www.content.models.publication import Publication
    from www.schemas import PublicationResponse, PaginationMeta, PaginatedResponse

    qs = Publication.objects.filter(is_published=True).order_by("-published_at")

    if search := _qp(request, "search"):
        qs = qs.filter(title__icontains=search)
    if category := _qp(request, "category"):
        qs = qs.filter(category__slug=category)

    page = _qp_int(request, "page", 1)
    per_page = _qp_int(request, "per_page", 20)
    total = qs.count()
    items = qs[(page - 1) * per_page : page * per_page]

    response = PaginatedResponse[PublicationResponse](
        data=[_ser_pub(p) for p in items],
        pagination=PaginationMeta(
            page=page, per_page=per_page, total=total,
            total_pages=max(1, (total + per_page - 1) // per_page),
        ),
    )
    return response.model_dump()


@bolt.get("/research/publications/<int:pk>")
def get_publication(request, pk):
    """GET /apis/research/publications/<id> — Single publication."""
    from www.content.models.publication import Publication
    from www.schemas import PublicationResponse, SingleResponse

    pub = Publication.objects.get(pk=pk, is_published=True)
    response = SingleResponse[PublicationResponse](data=_ser_pub(pub))
    return response.model_dump()


def _ser_pub(pub) -> "PublicationResponse":
    from www.schemas import PublicationResponse
    return PublicationResponse(
        id=pub.pk, title=pub.title, slug=getattr(pub, "slug", ""),
        abstract=getattr(pub, "abstract", ""), authors=getattr(pub, "authors", ""),
        category=pub.category.name if hasattr(pub, "category") and pub.category else "",
        published_at=pub.published_at.isoformat() if pub.published_at else None,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Research — Team
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/research/team")
def list_team(request):
    """GET /apis/research/team — Team members list."""
    from www.content.models.others import TeamMember
    from www.schemas import TeamMemberResponse

    members = TeamMember.objects.filter(is_active=True).order_by("sort_order", "name")
    items = [
        TeamMemberResponse(
            id=m.pk, name=m.name, title=getattr(m, "title", ""),
            bio=getattr(m, "bio", ""), email=getattr(m, "email", ""),
            photo=getattr(m, "photo", None), social_links=getattr(m, "social_links", {}),
        )
        for m in members
    ]
    return {"data": [item.model_dump() for item in items]}


# ═══════════════════════════════════════════════════════════════════════════
# Courses
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/courses")
def list_courses(request):
    """GET /apis/courses — Paginated course catalog."""
    from www.content.models.course import Course
    from www.schemas import CourseResponse, PaginationMeta, PaginatedResponse

    qs = Course.objects.filter(is_published=True).order_by("-created_at")

    if search := _qp(request, "search"):
        qs = qs.filter(title__icontains=search)
    if category := _qp(request, "category"):
        qs = qs.filter(category__slug=category)
    if skill_level := _qp(request, "skill_level"):
        qs = qs.filter(skill_level=skill_level)
    qs = qs.order_by(_qp(request, "sort", "-created_at"))

    page = _qp_int(request, "page", 1)
    per_page = _qp_int(request, "per_page", 12)
    total = qs.count()
    items = qs[(page - 1) * per_page : page * per_page]

    response = PaginatedResponse[CourseResponse](
        data=[_ser_course(c) for c in items],
        pagination=PaginationMeta(
            page=page, per_page=per_page, total=total,
            total_pages=max(1, (total + per_page - 1) // per_page),
        ),
    )
    return response.model_dump()


@bolt.get("/courses/<int:pk>")
def get_course(request, pk):
    """GET /apis/courses/<id> — Single course detail."""
    from www.content.models.course import Course
    from www.schemas import CourseResponse, SingleResponse

    course = Course.objects.get(pk=pk, is_published=True)
    response = SingleResponse[CourseResponse](data=_ser_course(course))
    return response.model_dump()


def _ser_course(c) -> "CourseResponse":
    from www.schemas import CourseResponse
    return CourseResponse(
        id=c.pk, title=c.title, slug=getattr(c, "slug", ""),
        description=getattr(c, "description", ""),
        category=c.category.name if hasattr(c, "category") and c.category else "",
        skill_level=getattr(c, "skill_level", ""),
        language=getattr(c, "language", "English"),
        price=float(getattr(c, "price", 0)),
        price_type="Free" if float(getattr(c, "price", 0)) == 0 else "Paid",
        rating=float(getattr(c, "rating", 0)),
        instructor=c.instructor.name if hasattr(c, "instructor") and c.instructor else "",
        duration=getattr(c, "duration", ""),
        enrolled_count=getattr(c, "enrolled_count", 0),
        created_at=c.created_at.isoformat() if c.created_at else None,
    )


@bolt.get("/courses/categories")
def list_categories(request):
    """GET /apis/courses/categories — Course categories."""
    from www.content.models.others import CourseCategory
    from www.schemas import CategoryResponse

    categories = CourseCategory.objects.filter(is_active=True).order_by("name")
    items = [
        CategoryResponse(
            id=c.pk, name=c.name, slug=getattr(c, "slug", ""),
            course_count=getattr(c, "course_count", 0), icon=getattr(c, "icon", ""),
        )
        for c in categories
    ]
    return {"data": [item.model_dump() for item in items]}


# ═══════════════════════════════════════════════════════════════════════════
# Auth (JWT-based, no DRF)
# ═══════════════════════════════════════════════════════════════════════════


@bolt.post("/auth/login")
def login(request):
    """POST /apis/auth/login — Authenticate and return JWT access + refresh tokens."""
    from www.schemas import LoginRequest, UserResponse, AuthTokenResponse

    body = json.loads(request.body)
    req = LoginRequest(email=body.get("email", ""), password=body.get("password", ""))

    from django.contrib.auth import authenticate
    from django.contrib.auth.models import User

    user = authenticate(request=request, username=req.email, password=req.password)
    if user is None:
        try:
            u = User.objects.get(email=req.email)
            user = authenticate(request=request, username=u.username, password=req.password)
        except User.DoesNotExist:
            pass

    if user is None:
        return {"error": "Invalid credentials"}, 401

    tokens = issue_jwt_tokens(user)
    response = AuthTokenResponse(
        access=tokens["access"],
        refresh=tokens["refresh"],
        user=UserResponse(
            id=user.pk, email=user.email, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
        ),
        expires_in=tokens["expires_in"],
    )
    return response.model_dump()


@bolt.post("/auth/register")
def register(request):
    """POST /apis/auth/register — Create account and return JWT access + refresh tokens."""
    from www.schemas import RegisterRequest, UserResponse, AuthTokenResponse

    body = json.loads(request.body)
    req = RegisterRequest(
        email=body.get("email", ""), password=body.get("password", ""),
        first_name=body.get("first_name", ""), last_name=body.get("last_name", ""),
    )

    if not req.email or not req.password:
        return {"error": "email and password are required"}, 400

    from django.contrib.auth.models import User
    if User.objects.filter(email=req.email).exists():
        return {"error": "A user with this email already exists"}, 409

    user = User.objects.create_user(
        username=req.email, email=req.email, password=req.password,
        first_name=req.first_name, last_name=req.last_name,
    )
    tokens = issue_jwt_tokens(user)
    response = AuthTokenResponse(
        access=tokens["access"],
        refresh=tokens["refresh"],
        user=UserResponse(
            id=user.pk, email=user.email, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
        ),
        expires_in=tokens["expires_in"],
    )
    return response.model_dump(), 201


@bolt.get("/auth/me", auth=[JWTTokenAuthBackend()])
def get_me(request):
    """GET /apis/auth/me — Return the authenticated user's profile.

    Requires: Authorization: Bearer <jwt-access-token>
    """
    from www.schemas import UserResponse

    # Dual-path: bolt-native request.user (fast path) or Python fallback
    user = request.user if hasattr(request, "user") and request.user else authenticate_request(request)
    if user is None:
        return {"error": "Unauthorized"}, 401

    return UserResponse(
        id=user.pk, email=user.email, username=user.username,
        first_name=user.first_name, last_name=user.last_name,
    ).model_dump()


@bolt.post("/auth/logout", auth=[JWTTokenAuthBackend()])
def logout(request):
    """POST /apis/auth/logout — Logout (stateless JWT — client discards tokens).

    Requires: Authorization: Bearer <jwt-access-token>
    JWT tokens are stateless; this endpoint simply acknowledges the logout.
    The client should discard both access and refresh tokens.
    """
    return {"status": "logged out"}


@bolt.post("/auth/refresh")
def refresh_token(request):
    """POST /apis/auth/refresh — Exchange a refresh JWT for a new access JWT.

    Request body::
        { "refresh": "<jwt-refresh-token>" }

    Returns a fresh access token.
    """
    body = json.loads(request.body)
    refresh_raw = body.get("refresh", "")

    if not refresh_raw:
        return {"error": "refresh token is required"}, 400

    # Decode and validate the refresh JWT
    payload = _jwt_decode(refresh_raw)
    if payload is None:
        return {"error": "Invalid or expired refresh token"}, 401

    token_type = payload.get("token_type")
    if token_type != "refresh":
        return {"error": "Token is not a refresh token"}, 401

    user = jwt_get_user_from_payload(payload)
    if user is None:
        return {"error": "User not found"}, 401

    # Issue a fresh access JWT (no new refresh token — rotation is handled client-side)
    tokens = issue_jwt_tokens(user)

    from www.schemas import AuthRefreshResponse, AuthTokenResponse, UserResponse
    return AuthTokenResponse(
        access=tokens["access"],
        refresh=tokens["refresh"],
        user=UserResponse(
            id=user.pk, email=user.email, username=user.username,
            first_name=user.first_name, last_name=user.last_name,
        ),
        expires_in=tokens["expires_in"],
    ).model_dump()


# ═══════════════════════════════════════════════════════════════════════════
# Contact
# ═══════════════════════════════════════════════════════════════════════════


@bolt.post("/contact/submit")
def submit_contact(request):
    """POST /apis/contact/submit — Submit contact form."""
    from www.schemas import ContactRequest, ContactResponse

    body = json.loads(request.body)
    req = ContactRequest(
        name=body.get("name", ""), email=body.get("email", ""),
        subject=body.get("subject", ""), message=body.get("message", ""),
    )

    from www.content.models.others import ContactSubmission
    sub = ContactSubmission.objects.create(
        name=req.name, email=req.email, subject=req.subject, message=req.message,
    )
    response = ContactResponse(status="ok", id=sub.pk)
    return response.model_dump(), 201

# ═══════════════════════════════════════════════════════════════════════════
# Site Settings — Wagtail-managed social links, footer, identity
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/site/settings")
def site_settings(request):
    """GET /apis/site/settings — Social links, footer data, site identity.

    Serves all Wagtail-managed site configuration to next-LMS:
      - Social media links (replaces hardcoded Social.tsx)
      - Footer data (replaces hardcoded FooterCommon.tsx, FooterOne.tsx)
      - Site identity (name, tagline, logo)
    """
    from www.content.models.settings import SocialLink, SiteSettings
    from www.schemas.site_settings import (
        SocialLinkResponse, FooterLinkItem, FooterLinkGroupResponse,
        SiteIdentityResponse, FooterDataResponse, SiteSettingsResponse,
    )

    # ── Social links ──
    social_qs = SocialLink.objects.filter(is_active=True).order_by("sort_order")
    social_links = [
        SocialLinkResponse(
            id=s.pk, platform=s.platform, label=s.label,
            url=s.url, icon_svg=s.icon_svg, icon_class=s.icon_class,
        )
        for s in social_qs
    ]

    # ── Site identity ──
    # first() returns None on empty table; guard against table-not-found (OperationalError)
    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None

    if settings:
        logo_url = settings.logo.file.url if settings.logo and settings.logo.file else None
        identity = SiteIdentityResponse(
            site_name=settings.site_name,
            site_tagline=settings.site_tagline,
            logo_url=logo_url,
        )
        footer = FooterDataResponse(
            description=settings.footer_description,
            address=settings.footer_address,
            phone=settings.footer_phone,
            email=settings.footer_email,
            copyright=settings.footer_copyright,
            google_play_url=settings.google_play_url,
            apple_store_url=settings.apple_store_url,
            privacy_policy_url=settings.privacy_policy_url,
            terms_of_use_url=settings.terms_of_use_url,
            link_groups=[
                FooterLinkGroupResponse(
                    title=group.title,
                    links=[FooterLinkItem(label=link.label, url=link.url)
                           for link in group.links.all().order_by("sort_order")],
                )
                for group in settings.footer_link_groups.all().order_by("sort_order")
            ],
        )
    else:
        identity = SiteIdentityResponse()
        footer = FooterDataResponse()

    response = SiteSettingsResponse(
        identity=identity,
        social_links=social_links,
        footer=footer,
    )
    return response.model_dump()

# ═══════════════════════════════════════════════════════════════════════════
# Blog
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/blog")
def list_blog_posts(request):
    """GET /apis/blog — Paginated blog posts."""
    from www.content.models.blog import BlogPost
    from www.schemas.blog import BlogPostResponse
    from www.schemas import PaginationMeta, PaginatedResponse

    qs = BlogPost.objects.filter(is_published=True).order_by("-published_at")

    page = _qp_int(request, "page", 1)
    per_page = _qp_int(request, "per_page", 12)
    total = qs.count()
    items = qs[(page - 1) * per_page : page * per_page]

    response = PaginatedResponse[BlogPostResponse](
        data=[BlogPostResponse(
            id=p.pk, title=p.title, slug=getattr(p, "slug", ""),
            excerpt=getattr(p, "excerpt", ""), content=getattr(p, "content", ""),
            author=getattr(p, "author", ""), category=getattr(p, "category", {}).get("name", ""),
            image_url=p.featured_image.file.url if hasattr(p, "featured_image") and p.featured_image and p.featured_image.file else None,
            published_at=p.published_at.isoformat() if p.published_at else None,
        ) for p in items],
        pagination=PaginationMeta(page=page, per_page=per_page, total=total,
            total_pages=max(1, (total + per_page - 1) // per_page)),
    )
    return response.model_dump()


# ═══════════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/events")
def list_events(request):
    """GET /apis/events — Event listings."""
    from www.content.models.blog import Event
    from www.schemas.blog import EventResponse

    events = Event.objects.filter(is_published=True).order_by("event_date")
    items = [EventResponse(
        id=e.pk, title=e.title, slug=getattr(e, "slug", ""),
        description=getattr(e, "description", ""), location=getattr(e, "location", ""),
        event_date=e.event_date.isoformat() if e.event_date else None,
        image_url=e.image.file.url if hasattr(e, "image") and e.image and e.image.file else None,
    ) for e in events]
    return {"data": [item.model_dump() for item in items]}


# ═══════════════════════════════════════════════════════════════════════════
# Testimonials
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/testimonials")
def list_testimonials(request):
    """GET /apis/testimonials — Testimonials list."""
    from www.content.models.blog import Testimonial
    from www.schemas.blog import TestimonialResponse

    testimonials = Testimonial.objects.filter(is_active=True).order_by("sort_order")
    items = [TestimonialResponse(
        id=t.pk, name=t.name, designation=getattr(t, "designation", ""),
        quote=getattr(t, "quote", ""), rating=float(getattr(t, "rating", 0)),
        avatar_url=t.avatar.file.url if hasattr(t, "avatar") and t.avatar and t.avatar.file else None,
    ) for t in testimonials]
    return {"data": [item.model_dump() for item in items]}


# ═══════════════════════════════════════════════════════════════════════════
# LMS — Features, Instructors, FAQ, Dashboard, Shop Products
# ═══════════════════════════════════════════════════════════════════════════


@bolt.get("/lms/features")
def list_features(request):
    """GET /apis/lms/features — Feature cards for home pages."""
    from www.content.models.lms import Feature
    from www.schemas.lms import FeatureResponse

    page_val = _qp(request, "page")
    qs = Feature.objects.filter(is_active=True).order_by("page", "sort_order")
    if page_val:
        qs = qs.filter(page=page_val)
    items = [FeatureResponse(
        id=f.pk, page=f.page, title=f.title, description=f.description,
        icon_url=f.icon.file.url if hasattr(f, "icon") and f.icon and f.icon.file else None,
        icon_class=getattr(f, "icon_class", ""), sort_order=f.sort_order,
    ) for f in qs]
    return {"data": [item.model_dump() for item in items]}


@bolt.get("/lms/instructors")
def list_instructors(request):
    """GET /apis/lms/instructors — Instructors list."""
    from www.content.models.lms import Instructor
    from www.schemas.lms import InstructorResponse

    instructors = Instructor.objects.filter(is_active=True).order_by("sort_order")
    items = [InstructorResponse(
        id=i.pk, name=i.name, designation=getattr(i, "designation", ""),
        bio=getattr(i, "bio", ""),
        avatar_url=i.avatar.file.url if hasattr(i, "avatar") and i.avatar and i.avatar.file else None,
        rating=float(getattr(i, "rating", 0)),
        course_count=getattr(i, "course_count", 0),
        student_count=getattr(i, "student_count", 0),
        sort_order=i.sort_order,
        social_links=getattr(i, "social_links", {}),
    ) for i in instructors]
    return {"data": [item.model_dump() for item in items]}


@bolt.get("/lms/faq")
def list_faq(request):
    """GET /apis/lms/faq — FAQ items."""
    from www.content.models.lms import Faq
    from www.schemas.lms import FaqItem

    page_val = _qp(request, "page")
    qs = Faq.objects.filter(is_active=True).order_by("page", "sort_order")
    if page_val:
        qs = qs.filter(page=page_val)
    items = [FaqItem(
        id=f.pk, page=f.page, question=f.question, answer=f.answer,
        sort_order=f.sort_order,
    ) for f in qs]
    return {"data": [item.model_dump() for item in items]}


@bolt.get("/lms/dashboard")
def get_dashboard_data(request):
    """GET /apis/lms/dashboard — Dashboard stats and lists."""
    from www.content.models.lms import DashboardCounter
    from www.schemas.lms import DashboardResponse, DashboardCounter as CounterSchema

    counters = DashboardCounter.objects.filter(is_active=True).order_by("sort_order")
    counter_items = [CounterSchema(
        id=c.pk, label=c.label, value=c.value,
        icon_class=getattr(c, "icon_class", ""),
        prefix=getattr(c, "prefix", ""), suffix=getattr(c, "suffix", ""),
    ) for c in counters]

    return DashboardResponse(counters=counter_items).model_dump()


@bolt.get("/lms/products")
def list_products(request):
    """GET /apis/lms/products — Shop product list."""
    from www.schemas.lms import ProductResponse

    # Try multiple import paths for Product model
    import importlib
    products = []
    for mod_path in ["www.content.models.shop", "www.content.models.lms", "plugins.products.models"]:
        try:
            mod = importlib.import_module(mod_path)
            Product = getattr(mod, "Product", None) or getattr(mod, "ShopProduct", None)
            if Product is not None:
                products = Product.objects.filter(is_active=True).order_by("title")
                break
        except Exception:
            continue

    items = [ProductResponse(
        id=p.pk, title=p.title, slug=getattr(p, "slug", ""),
        description=getattr(p, "description", ""),
        price=float(p.price),
        sale_price=float(p.sale_price) if getattr(p, "sale_price", None) else None,
        image_url=p.image.file.url if hasattr(p, "image") and p.image and p.image.file else None,
        category=getattr(p, "category", ""),
        rating=float(getattr(p, "rating", 0)),
        stock_status=getattr(p, "stock_status", "in_stock"),
    ) for p in products]
    return {"data": [item.model_dump() for item in items]}


@bolt.get("/lms/menu")
def get_main_menu(request):
    """GET /apis/lms/menu — Main navigation menu structure (tree).

    Returns nested structure: root items → children → mega-menus,
    matching the structure expected by the Next.js header component.
    """
    from www.content.models.lms import MenuItem
    from www.schemas.lms import MenuItemResponse, MenuGroupResponse

    qs = MenuItem.objects.filter(is_active=True, parent__isnull=True).order_by("sort_order")

    def _build_children(item):
        """Recursively build children for a menu item."""
        children = MenuItem.objects.filter(parent=item, is_active=True).order_by("sort_order")
        return [MenuGroupResponse(
            title=c.title, link=c.link,
            children=[_ser_flat(grandchild) for grandchild in
                      MenuItem.objects.filter(parent=c, is_active=True).order_by("sort_order")],
        ) for c in children] if children.exists() else []

    def _ser_flat(m):
        return MenuItemResponse(
            id=m.pk, parent_id=m.parent_id,
            title=m.title, link=m.link, menu_class=m.menu_class or "",
            badge=m.badge or "", badge_class=m.badge_class or "",
            icon=m.icon or "", sort_order=m.sort_order, is_active=m.is_active,
        )

    items = []
    for root_item in qs:
        entry = _ser_flat(root_item)
        children = _build_children(root_item)
        items.append({
            **entry.model_dump(),
            "children": [c.model_dump() for c in children] if children else [],
        })

    return {"data": items}


# ═══════════════════════════════════════════════════════════════════════════
# DRF-converted bolt endpoints — register all modular handlers
# ═══════════════════════════════════════════════════════════════════════════

from www.api.data.router import register_all_handlers
register_all_handlers(bolt)
