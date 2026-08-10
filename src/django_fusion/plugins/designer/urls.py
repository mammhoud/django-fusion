"""Optional URLs for the authenticated django-fusion designer.

Projects should include this module beneath a project-owned, protected URL
prefix rather than publishing it at the site root.
"""

from django.urls import path

from django_fusion.designer.views import designer_tools_call, designer_tools_list

urlpatterns = [
    path("tools/", designer_tools_list, name="fusion_designer_tools"),
    path("call/", designer_tools_call, name="fusion_designer_call"),
]
