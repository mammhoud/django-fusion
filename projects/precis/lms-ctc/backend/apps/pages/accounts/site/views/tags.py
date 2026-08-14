"""
Views for the custom tagging system.
"""

from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.generic import DetailView, ListView

from apps.pages.accounts.models.example_tagged_model import Article, Product
from apps.pages.accounts.models.tags import Tag, TaggedItem


class TagListView(ListView):
    """List all tags."""

    model = Tag
    template_name = "handlers/tags/tag_list.html"
    context_object_name = "tags"
    ordering = ["name"]


class TagDetailView(DetailView):
    """Detail view for a single tag."""

    model = Tag
    template_name = "handlers/tags/tag_detail.html"
    context_object_name = "tag"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class ArticlesByTagView(ListView):
    """List articles filtered by a tag."""

    template_name = "handlers/tags/articles_by_tag.html"
    context_object_name = "articles"

    def get_queryset(self):
        tag_slug = self.kwargs.get("slug")
        return Article.objects.filter_by_tag(tag_slug)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = Tag.objects.filter(slug=self.kwargs.get("slug")).first()
        return ctx


class ProductsByTagView(ListView):
    """List products filtered by a tag."""

    template_name = "handlers/tags/products_by_tag.html"
    context_object_name = "products"

    def get_queryset(self):
        tag_slug = self.kwargs.get("slug")
        return Product.objects.filter_by_tag(tag_slug)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = Tag.objects.filter(slug=self.kwargs.get("slug")).first()
        return ctx


def search_tags(request):
    """API view to search tags by name."""
    query = request.GET.get("q", "")
    tags = Tag.objects.filter(name__icontains=query).values("id", "name", "slug")
    return JsonResponse({"tags": list(tags)})


def filter_by_tags(request):
    """API view to filter content by tags."""
    tag_names = request.GET.getlist("tags")
    match_all = request.GET.get("match_all", "false").lower() == "true"
    articles = Article.objects.filter_by_tags(tag_names, match_all=match_all)
    data = list(articles.values("id", "title"))
    return JsonResponse({"articles": data})
