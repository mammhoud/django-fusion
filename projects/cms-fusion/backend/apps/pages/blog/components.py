"""
Blog Fragment Components for fusion-cms.com
==============================================

Template convention: ``fragment_name`` uses dotted notation.
  "blog.fragments.post_list"        → blog/fragments/post_list.html
  "blog.fragments.post_create_form" → blog/fragments/post_create_form.html
"""

from __future__ import annotations

import logging

from django import forms
from django.db.models import Q
from django.http import HttpResponse
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.components.dual_mode import FusionDualModeMixin

logger = logging.getLogger(__name__)


class BlogPostListFragment(FusionDualModeMixin, FragmentComponent):
    """
    Blog post list as HTMX fragment with pagination and search.

    URL: /blog/posts/list-fragment/

    Dual-mode: ``fusion_render_first=True`` renders the HTML fragment;
    ``False`` returns codec-encoded JSON with Site navigation.
    """

    route_name = "post-list-fragment"
    route_path = "posts/list-fragment/"
    fragment_name = "blog.fragments.post_list"
    htmx_only = True
    paginate_by = 10

    # OOB: post-count badge refreshed on every list render
    oob_fragments = {
        "post-count": "blog.fragments.post_count",
    }

    def has_permission(self, user):
        return True  # Public

    def get_queryset(self):
        from apps.pages.blog.models import BlogPost

        # ``BlogPost.categories`` is a M2M — there is no ``category`` FK to
        # select_related (previously raised FieldError -> HTTP 500).
        qs = BlogPost.objects.filter(status="published").select_related("author")

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(categories__slug=category)

        return qs.order_by("-published_date")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        from apps.pages.blog.models import BlogCategory, BlogPost

        context["categories"] = BlogCategory.objects.all()
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["show_success"] = self.request.session.pop("post_created", False)
        context["post_count"] = BlogPost.objects.filter(status="published").count()
        return context

    def get_fragment_data(self) -> dict:
        """Serialise the post list for data mode (fusion_render_first=False)."""
        from apps.pages.blog.models import BlogCategory, BlogPost

        qs = self.get_queryset()
        page = max(1, int(self.request.GET.get("page", 1)))
        per_page = self.paginate_by or 10
        total = qs.count()
        posts = qs[(page - 1) * per_page : page * per_page]

        return {
            "posts": [
                {
                    "id": p.pk, "title": p.title, "slug": getattr(p, "slug", ""),
                    "excerpt": getattr(p, "excerpt", ""),
                    "author": p.author.get_full_name() if p.author else "",
                    "published_date": p.published_date.isoformat() if p.published_date else None,
                    "categories": [
                        {"slug": c.slug, "name": c.name} for c in p.categories.all()
                    ],
                }
                for p in posts
            ],
            "categories": [
                {"slug": c.slug, "name": c.name} for c in BlogCategory.objects.all()
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
            "search_query": self.request.GET.get("q", ""),
            "selected_category": self.request.GET.get("category", ""),
            "post_count": BlogPost.objects.filter(status="published").count(),
        }


class BlogPostCreateFragment(FragmentComponent):
    """
    Blog post creation form as HTMX fragment.

    URL: /blog/posts/create-fragment/
    """

    route_name = "post-create-fragment"
    route_path = "posts/create-fragment/"
    fragment_name = "blog.fragments.post_create_form"
    htmx_only = True

    oob_fragments: dict = {}

    def has_permission(self, user):
        return user.is_staff

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["form"] = _get_blog_post_form_class()()
        return context

    def post(self, request, *args, **kwargs):
        form = _get_blog_post_form_class()(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return self._render_success_response(post)

        context = self.get_fragment_context()
        context["form"] = form
        return self.render_to_response(context)

    def _render_success_response(self, post):
        from django.template.loader import render_to_string

        success_html = render_to_string(
            "blog/fragments/post_create_success.html",
            {"post": post},
            request=self.request,
        )
        response = HttpResponse(f'<div id="post-create-success">{success_html}</div>')
        response["HX-Reswap"] = "innerHTML"
        response["HX-Retarget"] = "#post-list"
        oob_html = f'<div id="post-create-success" hx-swap-oob="true">{success_html}</div>'
        response.content = response.content.decode() + oob_html
        return response


def _get_blog_post_form_class():
    """Return BlogPostForm lazily to avoid import-time model conflicts."""
    from apps.blog.models import BlogPost

    class BlogPostForm(forms.ModelForm):
        class Meta:
            model = BlogPost
            fields = ["title", "slug", "excerpt", "content", "category", "status"]
            widgets = {
                "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Post title"}),
                "slug": forms.TextInput(attrs={"class": "form-control", "placeholder": "url-slug"}),
                "excerpt": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Brief summary..."}),
                "content": forms.Textarea(attrs={"class": "form-control", "rows": 10, "placeholder": "Post content..."}),
                "category": forms.Select(attrs={"class": "form-control"}),
                "status": forms.Select(attrs={"class": "form-control"}),
            }

        def clean_slug(self):
            slug = self.cleaned_data.get("slug")
            if not slug:
                from django.utils.text import slugify
                slug = slugify(self.cleaned_data.get("title", ""))
            qs = BlogPost.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError("A post with this slug already exists.")
            return slug

    return BlogPostForm


# ─── Blog post list (HTMX action fragment) ─────────────────────────


class ActionBlogPostListFragment(FusionDualModeMixin, FragmentComponent):
    """GET /blog/posts/ — Paginated blog post list with search/filter.

    Registered in ``BlogApp.viewsets`` (app_name="blog"), so the
    ``route_path`` is relative to the ``blog/`` app prefix.
    This is the richer dual-mode version; the Site-routed version
    ``BlogPostListFragment`` (``posts/list-fragment/``) lives in the same module.
    """

    route_name = "blog-posts"
    route_path = "posts/"
    fragment_name = "htmx.blog_post_list"
    htmx_only = True

    def get_queryset(self):
        from apps.pages.blog.models import BlogPost

        qs = BlogPost.objects.filter(status="published").order_by("-published_date")

        q = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(title__icontains=q)

        category = self.request.GET.get("category", "")
        if category:
            qs = qs.filter(categories__slug=category)

        tag = self.request.GET.get("tag", "")
        if tag:
            qs = qs.filter(tags__slug=tag)

        return qs

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context

    def get_fragment_data(self) -> dict:
        """Serialise the blog post list for data mode (fusion_render_first=False)."""
        qs = self.get_queryset()
        page = max(1, int(self.request.GET.get("page", 1)))
        per_page = 12
        total = qs.count()
        posts = qs[(page - 1) * per_page : page * per_page]

        return {
            "posts": [
                {
                    "id": p.pk, "title": p.title, "slug": p.slug,
                    "excerpt": p.excerpt,
                    "author": p.author.get_full_name() if p.author else "",
                    "published_date": p.published_date.isoformat() if p.published_date else None,
                    "featured_image_url": (
                        p.featured_image.get_rendition("fill-800x400").url
                        if p.featured_image else None
                    ),
                    "categories": [{"slug": c.slug, "name": c.name} for c in p.categories.all()],
                    "tags": [{"slug": t.slug, "name": t.name} for t in p.tags.all()],
                    "reading_time": p.get_reading_time() if hasattr(p, "get_reading_time") else 5,
                }
                for p in posts
            ],
            "pagination": {
                "page": page, "per_page": per_page, "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
            "q": self.request.GET.get("q", ""),
        }
