"""Public template discovery URLs."""

from django.urls import path

from .discovery import render_component_json, sections_json

urlpatterns = [
    path("sections.json", sections_json, name="fusion_template_sections"),
    path("render.json", render_component_json, name="fusion_template_render"),
]
