"""
Blog post comments — managed as a Wagtail snippet.

The comment thread is logged-in-only on the render roads (anonymous visitors
see a sign-in prompt), while ``POST /apis/blog/<slug>/comments/`` persists
rows here and ``GET /apis/blog/<slug>/comments/`` serves the approved list to
the public Astro road. ``is_approved`` is the moderation switch — uncheck a
comment in the Wagtail admin to hide it from every road without deleting it.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.ui.tables import BooleanColumn, Column, DateColumn
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class PostComment(models.Model):
    """A single comment on a BlogPostPage, authored by a logged-in user."""

    post = models.ForeignKey(
        "pages.BlogPostPage",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("post"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="landing_blog_comments",
        verbose_name=_("author"),
    )
    body = models.TextField(
        verbose_name=_("comment"),
        help_text=_("The comment text — up to 2000 characters."),
    )
    is_approved = models.BooleanField(
        _("approved"),
        default=True,
        db_index=True,
        help_text=_(
            "Uncheck to hide this comment from the public thread without "
            "deleting it."
        ),
    )
    created_at = models.DateTimeField(_("created at"), default=timezone.now)

    panels = [
        MultiFieldPanel([
            FieldPanel("post"),
            FieldPanel("author", read_only=True),
        ], heading=_("Thread")),
        MultiFieldPanel([
            FieldPanel("body"),
            FieldPanel("is_approved"),
        ], heading=_("Comment")),
        MultiFieldPanel([
            FieldPanel("created_at", read_only=True),
        ], heading=_("Timing")),
    ]

    class Meta:
        app_label = "pages"
        verbose_name = _("blog comment")
        verbose_name_plural = _("blog comments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} on {self.post} ({'✓' if self.is_approved else 'hidden'})"

    @property
    def display_name(self) -> str:
        """The reader-facing author name — email local part, else username."""
        email = getattr(self.author, "email", "") or ""
        if email:
            return email.split("@")[0] or self.author.username
        return self.author.username


class PostCommentViewSet(SnippetViewSet):
    """Wagtail snippet viewset — the admin home for the comment moderation queue.

    Lists every comment with its post, author, approval state and date, with
    filtering + search, and the built-in CSV export for a moderation/archive
    record. Approval is an inline edit on the row.
    """

    model = PostComment
    menu_label = _("Blog comments")
    icon = "comment"
    add_to_admin_menu = True

    list_display = [
        Column("post", label=_("Post")),
        Column("author", label=_("Author")),
        Column("body", label=_("Comment")),
        BooleanColumn("is_approved", label=_("Approved")),
        DateColumn("created_at", label=_("Date"), sort_key="created_at"),
    ]
    list_filter = ["is_approved"]
    search_fields = ["body", "author__email", "author__username"]
    list_export = ["post", "author", "body", "is_approved", "created_at"]
    export_headings = {
        "post": _("Post"),
        "author": _("Author"),
        "body": _("Comment"),
        "is_approved": _("Approved"),
        "created_at": _("Date"),
    }


register_snippet(PostCommentViewSet)
