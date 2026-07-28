"""
API views for blog tagging system.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import BlogTag
from .services import TagService


@require_http_methods(["GET"])
def search_tags(request):
    """API endpoint for tag search."""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'tags': []})

    tags = TagService.search_tags(query).values('id', 'name', 'slug')[:10]

    return JsonResponse({
        'tags': list(tags)
    })


@require_http_methods(["GET"])
def tag_autocomplete(request):
    """API endpoint for tag autocomplete."""
    query = request.GET.get('q', '').strip()

    if not query:
        tags = BlogTag.objects.all().values('id', 'name', 'slug')[:10]
    else:
        tags = TagService.search_tags(query).values('id', 'name', 'slug')[:10]

    return JsonResponse({
        'results': [
            {
                'id': tag['id'],
                'text': tag['name'],
                'slug': tag['slug']
            }
            for tag in tags
        ]
    })


@require_http_methods(["GET"])
def tag_cloud(request):
    """API endpoint for tag cloud."""
    limit = int(request.GET.get('limit', 30))
    tags = TagService.get_tag_cloud(limit=limit)

    return JsonResponse({
        'tags': [
            {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug,
                'count': tag.post_count,
                'size': tag.size
            }
            for tag in tags
        ]
    })


@require_http_methods(["GET"])
def related_tags(request, tag_slug):
    """API endpoint for related tags."""
    try:
        tag = BlogTag.objects.get(slug=tag_slug)
        related = TagService.get_related_tags(tag, limit=10)

        return JsonResponse({
            'tag': {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug
            },
            'related_tags': [
                {
                    'id': t.id,
                    'name': t.name,
                    'slug': t.slug,
                    'count': t.post_count
                }
                for t in related
            ]
        })
    except BlogTag.DoesNotExist:
        return JsonResponse({'error': 'Tag not found'}, status=404)
