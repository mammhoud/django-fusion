from django import forms
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock

from apps import logger
from apps.content.models.pages.base import BaseIndexPage
from apps.lms.models.courses.detail import Specialization
from apps.lms.models.courses.info import Course


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
                                template="django_grep/comp/blocks/media/simple_image.html",
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
          - Paginated published courses
          - Specializations
          - Base context (services, fragment, etc.)
          - Publishing statistics for debugging
        """
        context = super().get_context(request, *args, **kwargs)

        try:
            # Reuse the pagination logic from PaginatedBaseView
            # front_view = PaginatedBaseView()
            # context = front_view.extend_context(request, context)

            # Get published selected courses for the context
            published_selected_courses = self.get_published_courses(
                self.selected_courses.all()
            )

            # Inject custom data
            context.update(
                {
                    "courses": context.get(
                        "page_items"
                    ),  # alias for frontend template (already filtered by get_listed_items)
                    "specializations": Specialization.objects.all(),
                    "introduction": self.introduction,
                    "selected_courses": published_selected_courses,  # Only published ones
                    "publishing_stats": {
                        "total_selected": self.get_selected_courses_count(),
                        "published_selected": self.get_published_selected_courses_count(),
                    },
                }
            )

            logger.info(
                f"[{self.title}] Context successfully built with {len(context['courses'])} published courses. "
                f"Selected: {context['publishing_stats']['published_selected']}/"
                f"{context['publishing_stats']['total_selected']} published"
            )

        except Exception as e:
            logger.error(f"[ContextError] CourseIndexPage: {str(e)}", exc_info=True)
            context.update(
                {
                    "courses": [],
                    "specializations": [],
                    "introduction": "",
                    "selected_courses": [],
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
