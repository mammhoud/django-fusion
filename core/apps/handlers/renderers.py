from django.template import Context, Template
from django.utils.safestring import mark_safe

from core import logger


class DynamicComponentRenderer:
    """
    🎨 Renderer for dynamic HTML components.
    This handles the loading and rendering of uploaded HTML templates
    using the Django template engine, ensuring they can be used
    within the `django-grep` component ecosystem.
    """

    def render(self, html_file, context: Context) -> str:
        if not html_file:
            return ""

        try:
            if hasattr(html_file, 'open'):
                with html_file.open('r') as f:
                    template_content = f.read()
            else:
                with open(html_file.path, 'r') as f:
                    template_content = f.read()

            # Compile and render
            template = Template(template_content)
            return template.render(context)
        except Exception as e:
            logger.error(f"[DynamicComponentRenderer] Error: {e}")
            return mark_safe(f"<!-- Renderer Error: {e} -->")

# Singleton instance for easy access
dynamic_renderer = DynamicComponentRenderer()
