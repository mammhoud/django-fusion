"""
Blog Comment Views
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View

from plugins.blog.models import BlogComment, BlogPost


@method_decorator(login_required, name="dispatch")
class AddCommentView(View):
    """
    HTMX POST endpoint to submit a comment on a blog post.
    Returns the updated comments partial on success, or an error fragment.
    """

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status="published")
        content = request.POST.get("content", "").strip()

        if not content:
            return HttpResponse(
                '<p class="text-danger small mt-1">'
                + str(_("Comment cannot be empty."))
                + "</p>",
                status=422,
            )

        BlogComment.objects.create(
            post=post,
            author=request.user,
            content=content,
            is_approved=False,
        )

        # Return the refreshed comments partial
        from django.template.loader import render_to_string

        approved_comments = post.comments.filter(is_approved=True).select_related("author")
        html = render_to_string(
            "blog/components/comments.html",
            {
                "post": post,
                "comments": approved_comments,
                "comment_submitted": True,
                "request": request,
            },
            request=request,
        )
        return HttpResponse(html)
