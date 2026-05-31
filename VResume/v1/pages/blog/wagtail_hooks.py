from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .viewsets import BlogTagViewSet, BlogAuthorViewSet, BlogPostViewSet


class BlogAdminGroup(SnippetViewSetGroup):
    menu_label = "Blog"
    menu_icon = "doc-full"
    menu_order = 210
    items = (
        BlogTagViewSet,
        BlogAuthorViewSet,
        BlogPostViewSet,
    )


register_snippet(BlogAdminGroup)
