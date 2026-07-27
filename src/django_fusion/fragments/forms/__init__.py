"""
django_fusion.fragments.forms — Form integration with tag generation.

Provides:
  - FormMixin: Enhanced mixin for form rendering with ModelForm auto-creation
  - FormTableMixin: Combined form + table mixin
  - FormTagGenerator: Generates form HTML from Django form field definitions

Usage::

    from django_fusion.fragments.forms import FormMixin, FormTagGenerator

    class ProductCreate(RoutableComponent, FormMixin):
        form_name = "product"
        model = Product
        form_layout = [["name", "price"], ["description"]]
"""

from django_fusion.fragments.forms.mixins import FormMixin, FormTableMixin
from django_fusion.fragments.forms.tag_generator import FormTagGenerator

__all__ = ["FormMixin", "FormTableMixin", "FormTagGenerator"]
