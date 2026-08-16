import logging
import uuid

from wagtail import blocks

from .mixins import ResponsiveBlockMixin, StyledBlockMixin

logger = logging.getLogger(__name__)

__all__ = ["BaseBlock"]


class BaseBlock(StyledBlockMixin, ResponsiveBlockMixin, blocks.StructBlock):
    """
    Enhanced base block class with built-in styling and responsive support.
    Provides common functionality for all blocks.
    """

    def get_block_classes(self, value):
        """Get CSS classes for the block container."""
        base_classes = self.get_styling_config().get("container", "")
        responsive_classes = self.get_responsive_classes(value)
        custom_classes = value.get("custom_css_class", "")

        classes = [base_classes, responsive_classes, custom_classes]
        return " ".join(filter(None, classes))

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        # Add framework info
        context["framework"] = self.style_framework
        context["css_prefix"] = self.css_prefix

        # Generate unique block ID
        block_id = f"block-{uuid.uuid4().hex[:8]}"
        context["block_id"] = block_id
        context["block_classes"] = self.get_block_classes(value)

        return context
