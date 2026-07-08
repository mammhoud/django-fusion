"""Component loaders — lazy and async-safe rendering helpers.

Modules
-------
htmx    ``component_loader`` decorator that renders a spinner placeholder when
        a component function exceeds its timeout. Integrates with HTMX's
        hx-swap pattern for progressive enhancement.

Usage::

    from django_fusion.comp.loaders import component_loader

    @component_loader(timeout=0.3)
    def expensive_widget(request):
        return render(request, "widgets/expensive.html", context)
"""

from .htmx import component_loader

__all__ = ["component_loader"]
