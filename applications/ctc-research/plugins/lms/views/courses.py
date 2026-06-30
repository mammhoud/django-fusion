import logging

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, TemplateView
from django_osoul.site import PageHandler
from django_osoul.views import FilterMixin, SearchMixin
from ceptor_ai.models import CachingStorage

from ..models import Course, CourseEnrollmentLead, CourseTag

logger = logging.getLogger(__name__)


class FrontCourseDetailView(PageHandler, TemplateView):
    page_title = "Course"
    template_name = "course.html"
    template = "base_page.html"
    layout_path = "learning/skeleton.html"

    # Cache configuration
    CACHE_TIMEOUT = 1800  # 30 minutes for page cache
    USE_PAGE_CACHE = True  # Toggle page-level caching

    def get_cache_key(self, slug: str) -> str:
        """Generate cache key for this view."""
        # Include user-specific data if needed
        user_id = self.request.user.id if self.request.user.is_authenticated else 'anonymous'
        return f"course_view:{slug}:user:{user_id}:lang:{self.request.LANGUAGE_CODE}"

    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        """Add caching headers and handle dispatch."""
        response = super().dispatch(request, *args, **kwargs)

        # Add cache control headers
        if self.USE_PAGE_CACHE and not request.user.is_staff:
            response['Cache-Control'] = f'public, max-age={self.CACHE_TIMEOUT}'
            response['X-Cache-Status'] = 'enabled'
        else:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['X-Cache-Status'] = 'disabled'

        return response

    def get_course_context(self, slug: str) -> dict:
        """
        Get course context with caching at multiple levels.

        Args:
            slug: Course slug

        Returns:
            Context dictionary
        """
        # Try to get complete course details from cache
        course_details = Course.get_course_details(slug)

        if not course_details:
            # Fallback to database if cache misses
            logger.warning(f"Cache miss for course details: {slug}")
            course = get_object_or_404(Course, slug=slug, is_published=True)

            # Cache for next request
            Course.get_cached_course(slug)

            return {
                'course': course,
                'course_description': course.description,
                'course_modules': Course.get_course_modules(course),
                'instructor': course.instructor if hasattr(course, 'instructor') else None,
                'is_cached': False,
            }

        # Add cache status to context
        course_details['is_cached'] = True

        return course_details

    def get_context_data(self, **kwargs):
        """Get context data with caching support."""
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("slug")

        if not slug:
            return context

        try:
            # Get course context (with caching)
            course_context = self.get_course_context(slug)

            # Update main context
            context.update(course_context)

            # Add additional context
            context.update({
                'page_title': f"{course_context['course'].title} - Course",
                'meta_description': course_context['course'].description[:160] if course_context['course'].description else '',
                # 'canonical_url': self.request.build_absolute_uri(),
            })

            # Log cache status
            if course_context.get('is_cached'):
                logger.info(f"Served cached course: {slug}")
            else:
                logger.info(f"Served fresh course: {slug}")

        except Exception as e:
            logger.error(f"Error in FrontCourseDetailView for slug {slug}: {e}")
            # Fallback to traditional method
            course = get_object_or_404(Course, slug=slug, is_published=True)
            context.update({
                'course': course,
                'course_description': course.description,
                'course_modules': Course.get_course_modules(course),
                'is_cached': False,
            })

        return context

    def get(self, request, *args, **kwargs):
        """Handle GET request with caching."""
        # Check if page cache is enabled
        if self.USE_PAGE_CACHE and not request.user.is_staff:
            cache_key = self.get_cache_key(kwargs.get("slug"))
            cached_response = CachingStorage.cache_get(
                model_name='page_response',
                identifier=cache_key,
                suffix='html'
            )

            if cached_response:
                logger.info(f"Serving cached page for: {cache_key}")
                return cached_response

        # Generate fresh response
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)

        # Cache the response if enabled
        if self.USE_PAGE_CACHE and not request.user.is_staff:
            cache_key = self.get_cache_key(kwargs.get("slug"))
            CachingStorage.cache_set(
                model_name='page_response',
                identifier=cache_key,
                data=response,
                suffix='html',
                timeout=self.CACHE_TIMEOUT
            )

        return response


# Alternative: View with fragment caching
class FrontCourseDetailFragmentView(PageHandler, TemplateView):
    page_title = "Course"
    template_name = "course_fragment.html"
    template = "base_page.html"
    layout_path = "learning/skeleton.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("slug")

        # Get course with caching
        course = Course.get_cached_course(slug)
        if not course:
            course = get_object_or_404(Course, slug=slug, is_published=True)

        # Cache fragments separately
        fragments = {
            'course_header': self.get_course_header_fragment(course),
            'course_modules': self.get_modules_fragment(course),
            'course_sidebar': self.get_sidebar_fragment(course),
        }

        context.update({
            'course': course,
            'fragments': fragments,
        })

        return context

    def get_course_header_fragment(self, course):
        """Get cached header fragment."""
        def fetch_header():
            return {
                'title': course.title,
                'instructor': course.instructor,
                'rating': course.get_average_rating(),
                'enrollment_count': course.enrollments.count(),
                'duration': course.get_duration_display(),
            }

        return CachingStorage.cache_get_or_set(
            model_name='course_fragment',
            identifier=course.id,
            fetch_callback=fetch_header,
            suffix='header',
            timeout=900  # 15 minutes
        )

    def get_modules_fragment(self, course):
        """Get cached modules fragment."""
        return Course.get_course_modules(course)

    def get_sidebar_fragment(self, course):
        """Get cached sidebar fragment."""
        def fetch_sidebar():
            return {
                'price': course.price,
                'discount': course.discount_price,
                'requirements': list(course.requirements.all()),
                'last_updated': course.updated_at,
                'support_available': course.has_support,
            }

        return CachingStorage.cache_get_or_set(
            model_name='course_fragment',
            identifier=course.id,
            fetch_callback=fetch_sidebar,
            suffix='sidebar',
            timeout=900
        )
class CourseSearchView(SearchMixin, FilterMixin, ListView):
    """
    Search and filter view for courses with caching support.

    Uses SearchMixin and FilterMixin from django-osoul for declarative
    search/filter configuration while preserving the existing caching logic.
    """

    model = Course
    template_name = "courses/search.html"
    context_object_name = "courses"
    paginate_by = 12

    # SearchMixin configuration
    search_fields = ["title", "short_description", "description"]
    search_template = "courses/_search_results.html"  # HTMX partial

    # FilterMixin configuration
    filter_fields = [
        ("language", "language"),
        ("difficulty", "difficulty_level"),
        ("instructor", "instructor__username"),
    ]

    def get_queryset(self):
        """Get cached or fresh search results."""
        query = self.request.GET.get("q", "").strip()
        page = self.request.GET.get("page", 1)

        # Build filters from GET parameters
        filters = self._build_filters()

        # Get cached results
        cached_results = Course.get_cached_search_results(
            query=query, filters=filters, page=page, per_page=self.paginate_by
        )

        # Store cache metadata in request
        self.request.cache_hit = cached_results.get("from_cache", False)

        return cached_results["courses"]

    def _build_filters(self):
        """Build filter dictionary from request parameters."""
        filters = {}

        # Language filter
        if language := self.request.GET.get("language"):
            filters["language"] = language

        # Difficulty filter
        if difficulty := self.request.GET.get("difficulty"):
            filters["difficulty"] = difficulty

        # Specialization filter
        if specialization := self.request.GET.get("specialization"):
            filters["specialization"] = specialization

        # Price filter
        if price_range := self.request.GET.get("price"):
            filters["price_range"] = price_range

        # Duration filter
        if duration := self.request.GET.get("duration"):
            filters["duration"] = duration

        # Featured filter
        if featured := self.request.GET.get("featured"):
            filters["featured"] = featured == "true"

        # Certificate filter
        if certificate := self.request.GET.get("certificate"):
            filters["has_certificate"] = certificate == "true"

        # Instructor filter
        if instructor := self.request.GET.get("instructor"):
            filters["instructor"] = instructor

        return filters

    def get_context_data(self, **kwargs):
        """Add search context to template."""
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q", "")
        page_obj = context.get("page_obj")

        # Get filter options for template
        filter_options = self._get_filter_options()

        # Get cached results metadata
        cached_results = Course.get_cached_search_results(
            query=query,
            filters=self._build_filters(),
            page=self.request.GET.get("page", 1),
            per_page=self.paginate_by,
        )

        context.update(
            {
                "query": query,
                "search_url": self.request.path,
                "filter_options": filter_options,
                "active_filters": self._build_filters(),
                "total_results": cached_results.get("total_count", 0),
                "cache_hit": getattr(self.request, "cache_hit", False),
                "show_filters": True,
                "page_title": f"Search Courses - {query}"
                if query
                else "Browse Courses",
            }
        )

        return context

    def _get_filter_options(self):
        """Get available filter options for template."""
        from django.db.models import Count

        # Get unique languages
        languages = (
            Course.objects.filter(is_published=True, is_active=True)
            .values_list("language", flat=True)
            .distinct()
        )

        # Get difficulty levels
        difficulties = (
            Course.objects.filter(is_published=True, is_active=True)
            .values_list("difficulty_level", flat=True)
            .distinct()
        )

        # Get specializations with course counts
        from .models import Specialization  # Import if needed

        specializations = (
            Specialization.objects.annotate(
                course_count=Count(
                    "courses",
                    filter=models.Q(
                        courses__is_published=True, courses__is_active=True
                    ),
                )
            )
            .filter(course_count__gt=0)
            .values("slug", "title", "course_count")
        )

        # Price ranges
        price_ranges = [
            {
                "value": "free",
                "label": "Free",
                "count": Course.objects.filter(price=0, is_published=True).count(),
            },
            {
                "value": "paid",
                "label": "Paid",
                "count": Course.objects.filter(price__gt=0, is_published=True).count(),
            },
            {
                "value": "discounted",
                "label": "Discounted",
                "count": Course.objects.filter(
                    discount_percentage__gt=0, is_published=True
                ).count(),
            },
        ]

        # Duration ranges
        duration_ranges = [
            {
                "value": "short",
                "label": "Short (< 10h)",
                "count": Course.objects.filter(
                    duration__lte=10, is_published=True
                ).count(),
            },
            {
                "value": "medium",
                "label": "Medium (10-30h)",
                "count": Course.objects.filter(
                    duration__gt=10, duration__lte=30, is_published=True
                ).count(),
            },
            {
                "value": "long",
                "label": "Long (> 30h)",
                "count": Course.objects.filter(
                    duration__gt=30, is_published=True
                ).count(),
            },
        ]

        return {
            "languages": list(languages),
            "difficulties": list(difficulties),
            "specializations": list(specializations),
            "price_ranges": price_ranges,
            "duration_ranges": duration_ranges,
        }

# -------------------------------------------------------------------
# API ENDPOINT FOR FILTERED SEARCH
# -------------------------------------------------------------------
class CourseSearchAPIView(ListView):
    """
    API endpoint for course search with JSON response.
    """

    model = Course
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        """Return JSON response with search results."""
        query = request.GET.get("q", "").strip()
        page = request.GET.get("page", 1)

        # Build filters
        filters = self._build_filters(request)

        # Get cached results
        results = Course.get_cached_search_results(
            query=query, filters=filters, page=page, per_page=self.paginate_by
        )

        # Prepare response data
        response_data = {
            "success": True,
            "query": query,
            "filters": filters,
            "cache_hit": results.get("from_cache", False),
            "total": results["total_count"],
            "page": results["page_obj"].number,
            "pages": results["page_obj"].paginator.num_pages,
            "courses": [
                {
                    "id": course.id,
                    "title": course.title,
                    "slug": course.slug,
                    "short_description": course.short_description,
                    "image_url": course.image.file.url if course.image else None,
                    "instructor": course.instructor.get_full_name()
                    if course.instructor
                    else None,
                    "price": float(course.current_price),
                    "original_price": float(course.original_price)
                    if course.original_price
                    else None,
                    "discount_percentage": float(course.discount_percentage),
                    "duration": course.duration,
                    "difficulty": course.difficulty_level,
                    "language": course.language,
                    "rating": float(course.average_rating),
                    "reviews_count": course.reviews_count,
                    "url": course.url,
                    "is_featured": course.is_featured,
                    "has_certificate": course.has_certificate,
                }
                for course in results["courses"]
            ],
        }

        return JsonResponse(response_data, safe=False)

    def _build_filters(self, request):
        """Build filters from request parameters."""
        filters = {}

        # Map API parameters to filter keys
        param_map = {
            "language": "language",
            "difficulty": "difficulty",
            "specialization": "specialization",
            "price": "price_range",
            "duration": "duration",
            "featured": "featured",
            "certificate": "has_certificate",
            "instructor": "instructor",
        }

        for param, filter_key in param_map.items():
            if value := request.GET.get(param):
                filters[filter_key] = value

        return filters


# -------------------------------------------------------------------
# HTMX ENROLLMENT & WISHLIST VIEWS (Supporting CoursesPage)
# -------------------------------------------------------------------

@login_required
@require_http_methods(["GET"])
def course_enrollment_form(request: HttpRequest, course_id: int) -> HttpResponse:
    """Display enrollment form modal (AJAX response)."""
    course = get_object_or_404(Course, id=course_id, is_active=True)

    context = {
        "course": course,
    }

    return render(request, "learning/_course_enrollment_modal.html", context)


@login_required
@require_http_methods(["POST"])
def course_enrollment_create(request: HttpRequest, course_id: int) -> HttpResponse:
    """Create course enrollment lead (AJAX response)."""
    course = get_object_or_404(Course, id=course_id, is_active=True)

    full_name = request.POST.get("full_name", request.user.get_full_name())
    email = request.POST.get("email", request.user.email)
    phone = request.POST.get("phone", "")

    # Create or update enrollment lead
    enrollment, created = CourseEnrollmentLead.objects.get_or_create(
        course=course,
        email=email,
        defaults={
            "full_name": full_name,
            "phone": phone,
            "status": CourseEnrollmentLead.Status.PENDING,
        }
    )

    if not created:
        enrollment.phone = phone
        enrollment.save()

    context = {
        "enrollment": enrollment,
        "created": created,
    }

    return render(request, "learning/_course_enrollment_success.html", context)


@login_required
@require_http_methods(["POST"])
def course_wishlist_toggle(request: HttpRequest, course_id: int) -> HttpResponse:
    """Toggle course in user wishlist (AJAX response)."""
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # TODO: Implement wishlist functionality with custom user model
    # For now, placeholder response

    context = {
        "course": course,
        "is_wishlisted": False,
    }

    return render(request, "learning/_course_wishlist_button.html", context)
