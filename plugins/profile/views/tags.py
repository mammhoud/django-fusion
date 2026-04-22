"""
Tags view for user profiles.
Moved from www/core/handlers/site/tags.py
"""
import json

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django_osoul.comp.site import NotificationMixin, PageHandler
from plugins.accounts.models import PersonTag, PersonTagCategory

from apps import logger


class EnhancedTagsView(PageHandler, NotificationMixin):
    """
    Enhanced tags view using the new manager system.
    """
    page_title = "Tags"
    template_name = "base_profile.html"
    fragment_name = "profile.tags"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                tags_with_stats = PersonTag.objects.get_tags_with_stats(user=request.user)
                popular_tags = PersonTag.objects.get_popular_tags(limit=20, days=30)
                categories_with_stats = PersonTagCategory.objects.get_categories_with_stats(user=request.user)
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
        from django.db.models import Count
        user_tags = PersonTag.objects.filter(
            tagged_persons__content_object__user=user,
            tagged_persons__content_object__is_active=True
        ).distinct()

        tag_categories = user_tags.values('category__name', 'category__slug').annotate(
            count=Count('id')
        ).order_by('-count')

        return {
            'total_tags': user_tags.count(),
            'tag_categories': list(tag_categories),
            'recent_tags': user_tags.order_by('-last_used')[:10],
            'tag_cloud': self._generate_tag_cloud(user_tags),
        }

    def _generate_tag_cloud(self, tags, max_font_size=24, min_font_size=12):
        if not tags.exists():
            return []
        tags_with_counts = tags.annotate(usage_count=models.Count('tagged_persons')).order_by('-usage_count')
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
