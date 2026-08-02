"""
django_fusion.contrib.views.tags
================================

Enhanced tags view with tag management capabilities.

Note: This view requires project-specific models to be injected:
- PersonTag: Tag model
- PersonTagCategory: Tag category model
"""
import json
import logging
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django_fusion.contrib import NotificationMixin, PageHandler

logger = logging.getLogger(__name__)

# Project-specific models must be injected by the project subclass.
PersonTag: Optional[models.Model] = None
PersonTagCategory: Optional[models.Model] = None


class EnhancedTagsView(PageHandler, NotificationMixin):
    """
    Enhanced tags view using the new manager system.

    Requires PersonTag and PersonTagCategory models to be set before use.
    """
    page_title = "Tags"
    template_name = "tags/enhanced_tags.html"
    fragment_name = "tags.enhanced"
    layout_path = "layout/tags/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data using enhanced tag managers.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                if PersonTag is None or PersonTagCategory is None:
                    raise ValueError("PersonTag and PersonTagCategory models must be set")

                # Get tags with statistics
                tags_with_stats = PersonTag.objects.get_tags_with_stats(
                    user=request.user
                )

                # Get popular tags
                popular_tags = PersonTag.objects.get_popular_tags(
                    limit=20,
                    days=30
                )

                # Get categories with stats
                categories_with_stats = PersonTagCategory.objects.get_categories_with_stats(
                    user=request.user
                )

                # Get tag analytics
                tag_analytics = self._get_tag_analytics(request.user)

                context.update({
                    'tags_with_stats': tags_with_stats,
                    'popular_tags': popular_tags,
                    'categories_with_stats': categories_with_stats,
                    'tag_analytics': tag_analytics,
                    'search_query': request.GET.get('q', ''),
                })

            except Exception as e:
                logger.error(f"Error getting enhanced tags context: {e}")
                self.show_notification(
                    message="Error loading tags",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request
                )

        return context

    def _get_tag_analytics(self, user):
        """Get tag analytics for the user."""
        if PersonTag is None:
            return {}

        # Get user's tags
        user_tags = PersonTag.objects.filter(
            tagged_persons__content_object__user=user,
            tagged_persons__content_object__is_active=True
        ).distinct()

        # Calculate analytics
        total_tags = user_tags.count()

        tag_categories = user_tags.values(
            'category__name',
            'category__slug'
        ).annotate(
            count=models.Count('id')
        ).order_by('-count')

        # Recent activity
        recent_tags = user_tags.order_by('-last_used')[:10]

        return {
            'total_tags': total_tags,
            'tag_categories': list(tag_categories),
            'recent_tags': recent_tags,
            'tag_cloud': self._generate_tag_cloud(user_tags),
        }

    def _generate_tag_cloud(self, tags, max_font_size=24, min_font_size=12):
        """Generate tag cloud data."""
        if not tags.exists():
            return []

        # Get usage counts
        tags_with_counts = tags.annotate(
            usage_count=models.Count('tagged_persons')
        ).order_by('-usage_count')

        # Calculate font sizes
        max_count = tags_with_counts.first().usage_count
        min_count = tags_with_counts.last().usage_count

        tag_cloud = []
        for tag in tags_with_counts:
            if max_count > min_count:
                font_size = min_font_size + (
                    (tag.usage_count - min_count) / (max_count - min_count)
                ) * (max_font_size - min_font_size)
            else:
                font_size = (max_font_size + min_font_size) / 2

            tag_cloud.append({
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug,
                'color': tag.color,
                'usage_count': tag.usage_count,
                'font_size': round(font_size, 1),
                'category': tag.category.name if tag.category else None,
            })

        return tag_cloud

    @require_GET
    @login_required
    def search_tags_api(self, request: HttpRequest) -> JsonResponse:
        """
        Search tags using enhanced manager.
        """
        try:
            if PersonTag is None or PersonTagCategory is None:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Tag models not configured'
                }, status=500)

            query = request.GET.get('q', '')
            category_id = request.GET.get('category')

            if category_id:
                try:
                    category = PersonTagCategory.objects.get(id=category_id)
                except PersonTagCategory.DoesNotExist:
                    category = None
            else:
                category = None

            tags = PersonTag.objects.search_tags(
                query=query,
                category=category,
                limit=50
            )

            return JsonResponse({
                'status': 'success',
                'tags': [
                    {
                        'id': str(tag.id),
                        'name': tag.name,
                        'slug': tag.slug,
                        'color': tag.color,
                        'category': {
                            'id': str(tag.category.id),
                            'name': tag.category.name,
                        } if tag.category else None,
                        'usage_count': tag.usage_count,
                    }
                    for tag in tags
                ],
                'count': tags.count(),
            })

        except Exception as e:
            logger.error(f"Error searching tags: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error',
            }, status=500)

    @require_POST
    @csrf_exempt
    @login_required
    def merge_tags_api(self, request: HttpRequest) -> JsonResponse:
        """
        Merge tags using enhanced manager.
        """
        try:
            if PersonTag is None:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Tag model not configured'
                }, status=500)

            data = json.loads(request.body) if request.body else {}

            source_tag_id = data.get('source_tag_id')
            target_tag_id = data.get('target_tag_id')

            if not source_tag_id or not target_tag_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Both source and target tag IDs are required'
                }, status=400)

            try:
                source_tag = PersonTag.objects.get(id=source_tag_id)
                target_tag = PersonTag.objects.get(id=target_tag_id)
            except PersonTag.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Tag not found'
                }, status=404)

            # Merge tags
            success, message, stats = PersonTag.objects.merge_tags(
                source_tag=source_tag,
                target_tag=target_tag,
                user=request.user
            )

            if success:
                self.show_notification(
                    message=message,
                    level="success",
                    title="Tags Merged",
                    duration=3000,
                    request=request
                )

                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'stats': stats,
                })
            else:
                self.show_notification(
                    message=message,
                    level="error",
                    title="Merge Failed",
                    duration=5000,
                    request=request
                )

                return JsonResponse({
                    'status': 'error',
                    'message': message
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error merging tags: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error merging tags: {str(e)}'
            }, status=500)
