"""
Blog post management view for user profiles.
"""
import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django_fusion.site.interface.notifications import NotificationMixin
from django_fusion.site.interface.page_handler import PageHandler
from apps.pages.blog.forms import BlogPostFilterForm, BlogPostForm
from apps.pages.blog.models import BlogCategory, BlogPost, BlogTag
from apps.pages.blog.services import PostFilterService

logger = logging.getLogger(__name__)


class BlogPostsView(PageHandler, NotificationMixin):
    """
    Blog post management view in user profile.
    Lists the user's own posts and allows create/edit/delete via HTMX.
    """

    page_title = _("My Blog Posts")
    template_name = "base_profile.html"
    fragment_name = "profile.blog"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        self.request = request
        context = super().get_context_data(**kwargs)

        if not request.user.is_authenticated:
            return context

        try:
            posts = BlogPost.objects.filter(author=request.user).order_by("-created_at")

            # Apply search/filter from query params
            filter_form = BlogPostFilterForm(request.GET or None)
            q = request.GET.get("q", "").strip()
            if q:
                posts = PostFilterService.search_posts(posts, q)
            posts = filter_form.filter_queryset(posts)

            context.update({
                "blog_posts": posts,
                "filter_form": filter_form,
                "search_query": q,
                "post_counts": {
                    "total": BlogPost.objects.filter(author=request.user).count(),
                    "published": BlogPost.objects.filter(author=request.user, status="published").count(),
                    "draft": BlogPost.objects.filter(author=request.user, status="draft").count(),
                },
                "categories": BlogCategory.objects.all(),
                "tags": BlogTag.objects.all(),
            })
        except Exception as e:
            logger.error(f"Error loading blog posts context: {e}")

        return context


class BlogPostCreateView(PageHandler, NotificationMixin):
    """
    HTMX-powered blog post creation form in the profile panel.
    GET  → render the create form
    POST → save the post and return updated list fragment
    """

    page_title = _("New Blog Post")
    template_name = "base_profile.html"
    fragment_name = "profile.blog.create"
    layout_path = "profile/skeleton.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": _("Login required.")}, status=401)

        form = BlogPostForm()
        return render(request, "blog/profile/post_form.html", {
            "form": form,
            "form_title": _("Create New Post"),
            "submit_label": _("Save Post"),
            "cancel_url": request.META.get("HTTP_REFERER", "/profile/blog/"),
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": _("Login required.")}, status=401)

        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Handle featured image upload
            featured_image_file = request.FILES.get('featured_image_upload')
            if featured_image_file:
                try:
                    from wagtail.images import get_image_model
                    WagtailImage = get_image_model()
                    wagtail_image = WagtailImage(
                        title=featured_image_file.name,
                        uploaded_by_user=request.user,
                    )
                    wagtail_image.file = featured_image_file
                    wagtail_image.save()
                    post.featured_image = wagtail_image
                except Exception as e:
                    logger.warning(f"Could not save featured image: {e}")

            # Handle published_date
            published_date = form.cleaned_data.get('published_date')
            if published_date:
                post.published_date = published_date

            post.save()
            form.save_m2m()

            self.show_notification(
                message=_("Blog post saved successfully."),
                level="success",
                title=_("Saved"),
                duration=3000,
                request=request,
            )

            # Return the updated post list fragment for HTMX swap
            posts = BlogPost.objects.filter(author=request.user).order_by("-created_at")
            return render(request, "blog/profile/post_list_fragment.html", {
                "blog_posts": posts,
                "post_counts": {
                    "total": posts.count(),
                    "published": posts.filter(status="published").count(),
                    "draft": posts.filter(status="draft").count(),
                },
            })

        return render(request, "blog/profile/post_form.html", {
            "form": form,
            "form_title": _("Create New Post"),
            "submit_label": _("Save Post"),
            "cancel_url": request.META.get("HTTP_REFERER", "/profile/blog/"),
        }, status=422)


class BlogPostEditView(PageHandler, NotificationMixin):
    """
    HTMX-powered blog post edit form in the profile panel.
    GET  → render the edit form pre-filled
    POST → save changes and return updated list fragment
    """

    page_title = _("Edit Blog Post")
    template_name = "base_profile.html"
    fragment_name = "profile.blog.edit"
    layout_path = "profile/skeleton.html"

    def get(self, request: HttpRequest, post_id: int, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": _("Login required.")}, status=401)

        post = get_object_or_404(BlogPost, id=post_id, author=request.user)
        form = BlogPostForm(instance=post)
        return render(request, "blog/profile/post_form.html", {
            "form": form,
            "post": post,
            "form_title": _("Edit Post"),
            "submit_label": _("Update Post"),
            "cancel_url": request.META.get("HTTP_REFERER", "/profile/blog/"),
        })

    def post(self, request: HttpRequest, post_id: int, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": _("Login required.")}, status=401)

        post = get_object_or_404(BlogPost, id=post_id, author=request.user)
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

            # Handle featured image upload
            featured_image_file = request.FILES.get('featured_image_upload')
            if featured_image_file:
                try:
                    from wagtail.images import get_image_model
                    WagtailImage = get_image_model()
                    wagtail_image = WagtailImage(
                        title=featured_image_file.name,
                        uploaded_by_user=request.user,
                    )
                    wagtail_image.file = featured_image_file
                    wagtail_image.save()
                    updated_post.featured_image = wagtail_image
                except Exception as e:
                    logger.warning(f"Could not save featured image: {e}")

            # Handle published_date
            published_date = form.cleaned_data.get('published_date')
            if published_date:
                updated_post.published_date = published_date

            updated_post.save()
            form.save_m2m()

            self.show_notification(
                message=_("Blog post updated successfully."),
                level="success",
                title=_("Updated"),
                duration=3000,
                request=request,
            )

            posts = BlogPost.objects.filter(author=request.user).order_by("-created_at")
            return render(request, "blog/profile/post_list_fragment.html", {
                "blog_posts": posts,
                "post_counts": {
                    "total": posts.count(),
                    "published": posts.filter(status="published").count(),
                    "draft": posts.filter(status="draft").count(),
                },
            })

        return render(request, "blog/profile/post_form.html", {
            "form": form,
            "post": post,
            "form_title": _("Edit Post"),
            "submit_label": _("Update Post"),
            "cancel_url": request.META.get("HTTP_REFERER", "/profile/blog/"),
        }, status=422)


class BlogPostDeleteView(PageHandler, NotificationMixin):
    """
    HTMX-powered blog post deletion.
    POST → delete the post and return updated list fragment
    """

    def post(self, request: HttpRequest, post_id: int, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": _("Login required.")}, status=401)

        post = get_object_or_404(BlogPost, id=post_id, author=request.user)
        post.delete()

        self.show_notification(
            message=_("Blog post deleted."),
            level="info",
            title=_("Deleted"),
            duration=3000,
            request=request,
        )

        posts = BlogPost.objects.filter(author=request.user).order_by("-created_at")
        return render(request, "blog/profile/post_list_fragment.html", {
            "blog_posts": posts,
            "post_counts": {
                "total": posts.count(),
                "published": posts.filter(status="published").count(),
                "draft": posts.filter(status="draft").count(),
            },
        })