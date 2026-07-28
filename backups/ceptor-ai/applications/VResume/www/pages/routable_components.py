"""
Routable Components for VResume
================================

Defines a ``VResumeSite`` with ``BlogApp`` and ``PortfolioApp``
applications that use django-fusion ``RoutableComponent`` / ``FragmentComponent``
to display blog posts and projects.

This is the recommended pattern for new django-fusion views:

1. Define a **Site** (top-level) that groups applications.
2. Define **Applications** that group related routable components.
3. Define **RoutableComponent** subclasses for each view.
4. Use **FragmentComponent** for HTMX-only partial views.

Usage in ``urls.py``::

    from .routable_components import vresume_site
    urlpatterns += vresume_site.viewsets_urls()

The components are registered at the root path `/` alongside Wagtail pages.

Each component supports Unpoly (up-follow/up-target) and HTMX fallback
(hx-get/hx-target) via the ``{% nav_link %}`` and ``{% nav_panel %}`` tags.
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from django_fusion.comp.routes import (
    Application, AppMenuMixin, FragmentComponent,
    RoutableComponent, Site, route, menu_path, viewprop,
)


# =========================================================================
# Blog Components
# =========================================================================

class BlogListComponent(FragmentComponent):
    """HTMX fragment listing of blog posts.

    Note: ``route_path`` is RELATIVE to the parent Application (BlogApp).
    Since BlogApp prepends the ``blog/`` app_name prefix, the route path
    here is just ``list/``. This produces ``/fusion/blog/list/`` once
    mounted under the VResumeSite at ``/fusion/``.
    """
    route_name = "blog-list"
    route_path = "list/"
    fragment_name = "blog.fragments.post_list"
    paginate_by = 6
    title = "Blog Posts"
    icon = "article"

    def get_queryset(self):
        from pages.blog.models.snippets.post import BlogPost
        return BlogPost.objects.filter(is_published=True).order_by("-published_date", "-created_at")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        from pages.blog.models import BlogTag
        context["tags"] = BlogTag.objects.filter(is_active=True).order_by("display_order", "name")
        return context


class BlogDetailComponent(RoutableComponent):
    """CONTAINER for a single blog post.

    Renders the pure fragment (``blog/fragments/post_detail.html``) for
    HTMX requests (modal flow) and the full-page wrapper
    (``blog/fragments/post_detail_page.html``) for direct GETs.

    The ``fragment_name`` attribute is kept for the menu / ``{% comp
    'base_fragment' %}`` rendering pipeline (see
    ``applications/assets/templates/ui/base_page.html``), even though
    the view overrides ``get_template_names()`` for the actual render.
    """
    route_name = "blog-detail"
    route_path = "<slug:slug>/"
    fragment_name = "blog.fragments.post_detail"
    title = "Blog Post"
    icon = "article"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        from pages.blog.models.snippets.post import BlogPost
        self.post = get_object_or_404(BlogPost, slug=kwargs.get("slug"), is_published=True)
        return super().get(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        # CONTAINER: branch on request.htmx so HTMX gets the pure fragment
        # (no chrome) and direct GETs get the full page wrapper.
        request = getattr(self, "request", None)
        if request is not None and getattr(request, "htmx", False):
            return ["blog/fragments/post_detail.html"]
        return ["blog/fragments/post_detail_page.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = getattr(self, "post", None)
        if context["post"]:
            context["page_title"] = context["post"].title
            context["title"] = context["post"].title
        return context


# =========================================================================
# Portfolio / Project Components
# =========================================================================

class ProjectListComponent(FragmentComponent):
    """HTMX fragment listing of portfolio projects."""
    route_name = "project-list"
    route_path = "list/"
    fragment_name = "portfolio.fragments.project_list"
    paginate_by = 6
    title = "Projects"
    icon = "folder"

    def get_queryset(self):
        from pages.portfolio.models import Project
        return Project.objects.filter(is_active=True).order_by("-date_completed", "-created_at")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        from pages.portfolio.models import PortfolioTag
        context["tags"] = PortfolioTag.objects.filter(is_active=True).order_by("name")
        return context


class ProjectDetailComponent(RoutableComponent):
    """CONTAINER for a single project.

    Renders the pure fragment (``portfolio/fragments/project_detail.html``)
    for HTMX requests (modal flow) and the full-page wrapper
    (``portfolio/fragments/project_detail_page.html``) for direct GETs.

    The ``fragment_name`` attribute is kept for the menu / ``{% comp
    'base_fragment' %}`` rendering pipeline, even though the view
    overrides ``get_template_names()`` for the actual render.
    """
    route_name = "project-detail"
    route_path = "<slug:slug>/"
    fragment_name = "portfolio.fragments.project_detail"
    title = "Project"
    icon = "folder"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        from pages.portfolio.models import Project
        self.project = get_object_or_404(Project, slug=kwargs.get("slug"), is_active=True)
        return super().get(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        # CONTAINER: branch on request.htmx so HTMX gets the pure fragment
        # (no chrome) and direct GETs get the full page wrapper.
        request = getattr(self, "request", None)
        if request is not None and getattr(request, "htmx", False):
            return ["portfolio/fragments/project_detail.html"]
        return ["portfolio/fragments/project_detail_page.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = getattr(self, "project", None)
        if context["project"]:
            context["page_title"] = context["project"].title
            context["title"] = context["project"].title
        return context


# =========================================================================
# Applications
# =========================================================================

class BlogApp(Application):
    title = "Blog"
    icon = "article"
    menu_template_name = "components/menu/app_menu.html"

    class BlogList(AppMenuMixin, BlogListComponent):
        menu_order = 10
        show_in_menu = True

    class BlogDetail(BlogDetailComponent):
        show_in_menu = False

    @viewprop
    def viewsets(self):
        return [self.BlogList(), self.BlogDetail()]


class PortfolioApp(Application):
    title = "Portfolio"
    icon = "folder"
    menu_template_name = "components/menu/app_menu.html"

    class ProjectList(AppMenuMixin, ProjectListComponent):
        menu_order = 10
        show_in_menu = True

    class ProjectDetail(ProjectDetailComponent):
        show_in_menu = False

    @viewprop
    def viewsets(self):
        return [self.ProjectList(), self.ProjectDetail()]


# =========================================================================
# Site
# =========================================================================

class VResumeSite(Site):
    title = "VResume"
    icon = "view_comfy"
    menu_template_name = "components/menu/site_menu.html"

    class Blog(BlogApp):
        pass

    class Portfolio(PortfolioApp):
        pass


# =========================================================================
# Instance
# =========================================================================

vresume_site = VResumeSite()
vresume_site.register(VResumeSite.Blog)
vresume_site.register(VResumeSite.Portfolio)
