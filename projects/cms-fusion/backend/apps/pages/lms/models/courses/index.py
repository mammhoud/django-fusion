import logging

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock

logger = logging.getLogger(__name__)
from apps.core.content.models.pages.base import BaseIndexPage
from apps.pages.lms.models.courses.detail import Specialization
from apps.pages.lms.models.courses.info import Course
from apps.pages.lms.models.courses.tag import CourseTag


class CoursesPage(BaseIndexPage):
    """
    🧭 Enhanced Index Page for displaying Courses
    -------------------------------------------------
    Features:
      - Inherits from BaseIndexPage for unified styling, footer, and pagination
      - Editors can manually select courses (via snippets)
      - Integrates with PaginatedBaseView for consistent frontend pagination
      - Automatically includes active Specializations in context
      - Filters courses by is_published status
    """

    page_title = _("Courses Page")
    fragment_name = "courses.main"
    template = "base_page.html"
    head = StreamField(
        [
            (
                "page_title",
                blocks.StructBlock(
                    [
                        (
                            "page_title_background",
                            SimpleImageBlock(
                                template="blocks/media/image_lite.html",
                                label=_("Page Title Background"),
                            ),
                        ),
                        (
                            "page_title",
                            blocks.CharBlock(
                                required=True, max_length=200, label=_("Page Title")
                            ),
                        ),
                        (
                            "breadcrumb_home_text",
                            blocks.CharBlock(
                                default="Home", max_length=50, label=_("Breadcrumb Home Text")
                            ),
                        ),
                    ],
                    icon="image",
                    label=_("Page Title Section"),
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
        max_length=1,
        verbose_name=_("Header Section"),
    )



    # === Editor-Selectable Courses ===
    selected_courses = ParentalManyToManyField(
        Course,
        blank=True,
        related_name="displayed_in_index",
        help_text=_(
            "Select which courses to display on this page. Only published courses will be shown."
        ),
    )

    # === Intro Text ===
    introduction = RichTextField(
        blank=True,
        help_text=_("Text describing the page or highlighting available courses."),
        verbose_name=_("Introduction"),
    )

    # === Panels ===
    content_panels = [
        FieldPanel("head"),
        MultiFieldPanel(
            [
                FieldPanel(
                    "selected_courses",
                    widget=forms.CheckboxSelectMultiple,
                    heading=_("Select Courses"),
                ),
                FieldPanel("introduction"),
            ],
            heading=_("Courses Configuration"),
        ),
    ] + BaseIndexPage.content_panels

    class Meta:
        app_label = "lms"
        verbose_name = _("Courses Page")
        verbose_name_plural = _("Courses Pages")

    def get_published_courses(self, queryset):
        """
        Filter queryset to only include published courses.

        Args:
            queryset: QuerySet of Course objects

        Returns:
            QuerySet of published Course objects
        """
        try:
            return queryset.filter(is_published=True)
        except Exception as e:
            logger.error(
                f"[get_published_courses] Failed to filter published courses: {e}",
                exc_info=True,
            )
            return queryset.none()

    # === Data Provider ===
    def get_listed_items(self):
        """
        Return either:
        - the manually selected courses that are published, OR
        - all active AND published courses (fallback)
        """
        try:
            selected = self.selected_courses.all()
            if selected.exists():
                published_selected = self.get_published_courses(selected)
                if published_selected.exists():
                    logger.info(
                        f"[{self.title}] Returning {published_selected.count()} manually selected published courses."
                    )
                    return published_selected
                else:
                    logger.warning(
                        f"[{self.title}] No published courses in selection. Falling back to all published active courses."
                    )

            # Fallback: get all active AND published courses
            published_courses = Course.objects.filter(
                is_active=True, is_published=True
            ).order_by("title")
            logger.info(
                f"[{self.title}] Returning {published_courses.count()} published active courses."
            )
            return published_courses

        except Exception as e:
            logger.error(
                f"[get_listed_items] Failed to load courses: {e}", exc_info=True
            )
            return Course.objects.none()

    def get_selected_courses_count(self):
        """
        Get count of selected courses (for admin info).
        """
        try:
            return self.selected_courses.count()
        except:
            return 0

    def get_published_selected_courses_count(self):
        """
        Get count of published selected courses (for admin info).
        """
        try:
            return self.get_published_courses(self.selected_courses.all()).count()
        except:
            return 0

    # === Context ===
    def get_context(self, request, *args, **kwargs):
        """
        Extend the context with:
          - Filtered & paginated courses based on user input
          - Filter options (difficulties, tags, price ranges)
          - Specializations
          - Pagination metadata
          - Publishing statistics for debugging
        """
        context = super().get_context(request, *args, **kwargs)

        try:
            # Build filter dict from GET parameters
            filters = {
                'difficulty': request.GET.get('difficulty', ''),
                'price_min': request.GET.get('price_min', ''),
                'price_max': request.GET.get('price_max', ''),
                'tags': request.GET.getlist('tags') or [],
                'search': request.GET.get('q', ''),
                'sort': request.GET.get('sort', '-created_at'),
            }

            # Get filtered courses
            filtered_courses = self.get_filtered_courses(request, **filters)

            # Get pagination info
            pagination_context = self.get_paginated_context(request, filtered_courses, per_page=12)

            # Get filter options for template
            filter_options = self.get_filter_options()

            # Get specializations
            specializations = Specialization.objects.filter(is_active=True)

            # Inject custom data
            context.update(
                {
                    "courses": pagination_context['courses'],
                    "page_obj": pagination_context['page_obj'],
                    "paginator": pagination_context['paginator'],
                    "total_count": pagination_context['total_count'],
                    "specializations": specializations,
                    "introduction": self.introduction,
                    "filter_options": filter_options,
                    "active_filters": {k: v for k, v in filters.items() if v},
                    "publishing_stats": {
                        "total_selected": self.get_selected_courses_count(),
                        "published_selected": self.get_published_selected_courses_count(),
                    },
                }
            )

            logger.info(
                f"[{self.title}] Context built: {len(context['courses'])} courses on page "
                f"{pagination_context['page_number']} of {pagination_context['paginator'].num_pages}. "
                f"Active filters: {context['active_filters']}"
            )

        except Exception as e:
            logger.error(f"[ContextError] CoursesPage.get_context: {str(e)}", exc_info=True)
            context.update(
                {
                    "courses": [],
                    "page_obj": None,
                    "paginator": None,
                    "specializations": [],
                    "introduction": "",
                    "filter_options": {
                        'difficulties': [],
                        'tags': [],
                        'price_range': {'min_price': 0, 'max_price': 0},
                    },
                    "active_filters": {},
                    "publishing_stats": {
                        "total_selected": 0,
                        "published_selected": 0,
                    },
                }
            )

        return context

    def get_admin_display_title(self):
        """
        Enhance admin display to show publishing status.
        """
        base_title = super().get_admin_display_title()
        try:
            published_count = self.get_published_selected_courses_count()
            total_count = self.get_selected_courses_count()
            return f"{base_title} ({published_count}/{total_count} published)"
        except:
            return base_title

    # === Catalog & Filter Methods ===
    def get_filtered_courses(self, request, **filters):
        """
        Get courses filtered by applied filters (search, difficulty, price, tags, sort).
        Used by catalog views for dynamic filtering.
        """
        courses = self.get_listed_items()

        # Apply difficulty filter
        if difficulty := filters.get('difficulty'):
            courses = courses.filter(difficulty_level=difficulty)

        # Apply price range filter
        if price_min := filters.get('price_min'):
            try:
                courses = courses.filter(price__gte=float(price_min))
            except (ValueError, TypeError):
                pass

        if price_max := filters.get('price_max'):
            try:
                courses = courses.filter(price__lte=float(price_max))
            except (ValueError, TypeError):
                pass

        # Apply tags filter
        if tags := filters.get('tags'):
            if isinstance(tags, str):
                tags = [tags]
            courses = courses.filter(tags__id__in=tags).distinct()

        # Apply search query
        if search_query := filters.get('search'):
            from django.db.models import Q
            courses = courses.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(short_description__icontains=search_query)
            ).distinct()

        # Apply sorting
        sort_by = filters.get('sort', '-created_at')
        courses = courses.order_by(sort_by)

        return courses

    def get_paginated_context(self, request, courses, per_page=12):
        """
        Return paginated courses with pagination metadata for templates.
        """
        from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

        page = request.GET.get('page', 1)
        paginator = Paginator(courses, per_page)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return {
            'page_obj': page_obj,
            'courses': page_obj.object_list,
            'paginator': paginator,
            'total_count': paginator.count,
            'page_number': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }

    def get_filter_options(self):
        """
        Get available filter options for template rendering.
        Returns all difficulty levels, tags, price ranges.
        """
        from django.db.models import Count, Max, Min

        courses = Course.objects.filter(is_active=True, is_published=True)

        # Get difficulty levels with counts
        difficulties = (
            courses.values('difficulty_level')
            .annotate(count=Count('id'))
            .order_by('difficulty_level')
        )

        # Get tags with counts
        tags = CourseTag.objects.annotate(
            course_count=Count('courses', filter=models.Q(courses__is_active=True, courses__is_published=True))
        ).filter(course_count__gt=0).order_by('name')

        # Get price range
        price_range = courses.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )

        return {
            'difficulties': [
                {'value': d['difficulty_level'], 'label': dict(Course.DifficultyChoices.choices).get(d['difficulty_level']), 'count': d['count']}
                for d in difficulties
            ],
            'tags': tags,
            'price_range': price_range,
        }
