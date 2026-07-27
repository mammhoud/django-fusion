"""
Views for tag management and filtering.
"""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView

from ..models.example_tagged_model import Article, Product
from ..models.tags import Tag, TaggedItem


class TagListView(ListView):
    """Display all available tags."""

    model = Tag
    template_name = 'tags/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 20

    def get_queryset(self):
        """Get tags with item counts."""
        return Tag.objects.annotate(
            item_count=Count('tagged_items')
        ).order_by('-item_count')

    def get_context_data(self, **kwargs):
        """Add search functionality to context."""
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')

        if search_query:
            context['tags'] = context['tags'].filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            context['search_query'] = search_query

        return context


class TagDetailView(DetailView):
    """Display articles and products tagged with a specific tag."""

    model = Tag
    template_name = 'tags/tag_detail.html'
    context_object_name = 'tag'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        """Get all items tagged with this tag."""
        context = super().get_context_data(**kwargs)
        tag = self.get_object()

        # Get all tagged items for this tag
        tagged_items = TaggedItem.objects.filter(tag=tag)

        # Separate by content type
        article_ct = ContentType.objects.get_for_model(Article)
        product_ct = ContentType.objects.get_for_model(Product)

        article_ids = tagged_items.filter(
            content_type=article_ct
        ).values_list('object_id', flat=True)

        product_ids = tagged_items.filter(
            content_type=product_ct
        ).values_list('object_id', flat=True)

        context['articles'] = Article.objects.filter(id__in=article_ids)
        context['products'] = Product.objects.filter(id__in=product_ids)

        return context


class ArticlesByTagView(ListView):
    """Display articles filtered by tag."""

    model = Article
    template_name = 'tags/articles_by_tag.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        """Filter articles by tag."""
        tag_slug = self.kwargs.get('tag_slug')
        tag = get_object_or_404(Tag, slug=tag_slug)

        content_type = ContentType.objects.get_for_model(Article)
        article_ids = TaggedItem.objects.filter(
            tag=tag,
            content_type=content_type
        ).values_list('object_id', flat=True)

        return Article.objects.filter(id__in=article_ids).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add tag to context."""
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('tag_slug')
        context['tag'] = get_object_or_404(Tag, slug=tag_slug)
        return context


class ProductsByTagView(ListView):
    """Display products filtered by tag."""

    model = Product
    template_name = 'tags/products_by_tag.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        """Filter products by tag."""
        tag_slug = self.kwargs.get('tag_slug')
        tag = get_object_or_404(Tag, slug=tag_slug)

        content_type = ContentType.objects.get_for_model(Product)
        product_ids = TaggedItem.objects.filter(
            tag=tag,
            content_type=content_type
        ).values_list('object_id', flat=True)

        return Product.objects.filter(id__in=product_ids).order_by('name')

    def get_context_data(self, **kwargs):
        """Add tag to context."""
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('tag_slug')
        context['tag'] = get_object_or_404(Tag, slug=tag_slug)
        return context


@require_http_methods(["GET"])
def search_tags(request):
    """API endpoint for tag search."""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'tags': []})

    tags = Tag.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    ).values('id', 'name', 'slug')[:10]

    return JsonResponse({
        'tags': list(tags)
    })


@require_http_methods(["GET"])
def filter_by_tags(request):
    """API endpoint for filtering items by tags."""
    tag_names = request.GET.getlist('tags')
    content_type_name = request.GET.get('content_type', 'article')
    match_all = request.GET.get('match_all', 'false').lower() == 'true'

    if not tag_names:
        return JsonResponse({'error': 'No tags provided'}, status=400)

    # Get content type
    if content_type_name == 'product':
        model = Product
    else:
        model = Article

    content_type = ContentType.objects.get_for_model(model)

    # Get tagged items
    if match_all:
        # Items must have all tags
        queryset = model.objects.all()
        for tag_name in tag_names:
            tagged_ids = TaggedItem.objects.filter(
                tag__name=tag_name,
                content_type=content_type
            ).values_list('object_id', flat=True)
            queryset = queryset.filter(id__in=tagged_ids)
    else:
        # Items can have any tag
        tagged_ids = TaggedItem.objects.filter(
            tag__name__in=tag_names,
            content_type=content_type
        ).values_list('object_id', flat=True).distinct()
        queryset = model.objects.filter(id__in=tagged_ids)

    # Serialize results
    results = []
    for item in queryset:
        results.append({
            'id': item.id,
            'name': str(item),
            'url': item.get_absolute_url() if hasattr(item, 'get_absolute_url') else '#'
        })

    return JsonResponse({
        'count': len(results),
        'results': results
    })
