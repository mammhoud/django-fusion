"""
Blog Post Like View
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.blog.models import BlogPost


@method_decorator(login_required, name="dispatch")
class BlogPostLikeView(View):
    """
    HTMX POST endpoint to toggle a like on a blog post.
    Increments likes_count and returns an updated like-button fragment.
    """

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status="published")

        # Simple increment — no per-user deduplication for now
        BlogPost.objects.filter(pk=post.pk).update(likes_count=post.likes_count + 1)
        post.refresh_from_db(fields=["likes_count"])

        html = (
            f'<button class="btn btn-sm btn-outline-danger" '
            f'hx-post="{request.path}" '
            f'hx-swap="outerHTML" '
            f'hx-headers=\'{{"X-CSRFToken": "{request.META.get("CSRF_COOKIE", "")}"}}\' '
            f'aria-label="Like this post">'
            f'<i class="bi bi-heart-fill me-1" aria-hidden="true"></i>'
            f'{post.likes_count}'
            f"</button>"
        )
        return HttpResponse(html)
