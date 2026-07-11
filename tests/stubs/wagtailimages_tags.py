"""Stub tag library for wagtailimages_tags in the django-fusion test environment.

The canonical django_fusion/comp/templates/components/form/form_block.html
template loads wagtailimages_tags for production use (Wagtail richtext/image rendering).
The test environment doesn't have Wagtail installed, so this stub provides
an empty Library so get_template() can still parse the template.
"""
from django.template import Library

register = Library()
