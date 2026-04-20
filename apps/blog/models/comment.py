"""
Blog Comment Model
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BlogComment(models.Model):
    """
    Comment on a blog post. Requires approval before being publicly visible.
    """

    post = models.ForeignKey(
        "blog.BlogPost",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Post"),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_comments",
        verbose_name=_("Author"),
    )

    content = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Comment text"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Approved"),
        help_text=_("Only approved comments are shown publicly"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("Blog Comment")
        verbose_name_plural = _("Blog Comments")
        ordering = ["created_at"]
        app_label = 'blog'

    def __str__(self):
        return f"Comment by {self.author} on '{self.post}'"
