import logging

from django.conf import settings

logger = logging.getLogger(__name__)

__all__ = ["StyledBlockMixin", "ResponsiveBlockMixin"]

# =============================================================================
# MIXINS FOR ENHANCED FUNCTIONALITY
# =============================================================================


class StyledBlockMixin:
    """
    Mixin providing styling configuration for both Bootstrap and Tailwind CSS.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_framework = getattr(settings, "STYLES_FRAMEWORK", "bootstrap")
        self.css_prefix = getattr(settings, "STYLES_PREFIX", "")

    def get_styling_config(self):
        """Get styling configuration based on selected framework."""
        if self.style_framework == "tailwind":
            return {
                "container": f"{self.css_prefix}relative",
                "section": f"{self.css_prefix}py-12 {self.css_prefix}px-4",
                "grid": {
                    "row": f"{self.css_prefix}grid {self.css_prefix}grid-cols-1 {self.css_prefix}gap-6",
                    "col_2": f"{self.css_prefix}grid {self.css_prefix}grid-cols-1 {self.css_prefix}md:grid-cols-2 {self.css_prefix}gap-6",
                    "col_3": f"{self.css_prefix}grid {self.css_prefix}grid-cols-1 {self.css_prefix}md:grid-cols-3 {self.css_prefix}gap-6",
                    "col_4": f"{self.css_prefix}grid {self.css_prefix}grid-cols-1 {self.css_prefix}md:grid-cols-2 {self.css_prefix}lg:grid-cols-4 {self.css_prefix}gap-6",
                },
                "card": f"{self.css_prefix}bg-white {self.css_prefix}rounded-lg {self.css_prefix}shadow-md {self.css_prefix}p-6",
                "image": f"{self.css_prefix}rounded-lg {self.css_prefix}shadow-md",
                "button": f"{self.css_prefix}inline-flex {self.css_prefix}items-center {self.css_prefix}justify-center {self.css_prefix}px-4 {self.css_prefix}py-2 {self.css_prefix}rounded-md {self.css_prefix}shadow-sm",
                "title": f"{self.css_prefix}text-2xl {self.css_prefix}font-bold {self.css_prefix}mb-4",
                "subtitle": f"{self.css_prefix}text-sm {self.css_prefix}font-semibold {self.css_prefix}uppercase {self.css_prefix}tracking-wide {self.css_prefix}text-gray-500 {self.css_prefix}mb-2",
            }
        else:  # Bootstrap
            return {
                "container": "container",
                "section": "py-5",
                "grid": {
                    "row": "row g-4",
                    "col_2": "row row-cols-1 row-cols-md-2 g-4",
                    "col_3": "row row-cols-1 row-cols-md-3 g-4",
                    "col_4": "row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4",
                },
                "card": "card shadow-sm",
                "image": "img-fluid rounded shadow",
                "button": "btn",
                "title": "h2 mb-4",
                "subtitle": "text-uppercase text-muted mb-3 small fw-bold",
            }


class ResponsiveBlockMixin:
    """
    Mixin for responsive block configuration.
    """

    def get_responsive_classes(self, value):
        """Generate responsive CSS classes based on block configuration."""
        responsive_config = value.get("responsive_config", {})

        if hasattr(self, "style_framework") and self.style_framework == "tailwind":
            classes = []

            width = responsive_config.get("width", "full")
            if width == "container":
                classes.append(f"{self.css_prefix}max-w-7xl {self.css_prefix}mx-auto")
            elif width == "narrow":
                classes.append(f"{self.css_prefix}max-w-3xl {self.css_prefix}mx-auto")

            padding = responsive_config.get("padding", "default")
            padding_map = {
                "none": "",
                "small": f"{self.css_prefix}py-4 {self.css_prefix}px-2",
                "default": f"{self.css_prefix}py-8 {self.css_prefix}px-4",
                "large": f"{self.css_prefix}py-12 {self.css_prefix}px-6",
            }
            if padding in padding_map:
                classes.append(padding_map[padding])

            return " ".join(classes)
        else:  # Bootstrap
            classes = []

            width = responsive_config.get("width", "container")
            if width == "full":
                classes.append("container-fluid")
            elif width == "container":
                classes.append("container")
            elif width == "narrow":
                classes.append("container container-narrow")

            padding = responsive_config.get("padding", "default")
            padding_map = {
                "none": "p-0",
                "small": "py-3",
                "default": "py-5",
                "large": "py-6",
            }
            if padding in padding_map:
                classes.append(padding_map[padding])

            return " ".join(classes)
