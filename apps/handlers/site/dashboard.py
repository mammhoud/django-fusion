
import json

from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models.aggregates import Count
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from django_grep.comp.site import NotificationMixin, PageHandler
from django_grep.pipelines.models import (
    Person,
    PersonTag,
    PersonTagCategory,
)

from .mixins import ProfileDashboardMixin, ProfileOperationsMixin


class DashboardView(PageHandler):
    """
    Generic profile dashboard view.
    """
    page_title = "Dashboard"
    template_name = "base_profile.html"
    fragment_name = "profile.dashboard"
    layout_path = "profile/skeleton.html"
    
    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get profile dashboard data.
        """
        self.request = request
        context = super().get_context_data(**kwargs)
        
        if request.user.is_authenticated:
            try:
                # Get tag analytics
                tag_analytics = self._get_tag_analytics(request.user)
                
                # Get recent activity
                recent_activity = self._get_recent_activity(request.user)
                
                context.update({
                    'tag_analytics': tag_analytics,
                    'recent_activity': recent_activity,
                    'quick_actions': self._get_quick_actions(request.user),
                })
                
            except Exception as e:
                logger.error(f"Error getting dashboard context: {e}")
        
        return context
    
    def _get_tag_analytics(self, user):
        """Get tag analytics for dashboard."""
        user_tags = PersonTag.objects.filter(
            tagged_persons__content_object__user=user,
            tagged_persons__content_object__is_active=True
        ).annotate(
            usage_count=Count('tagged_persons')
        ).order_by('-usage_count')[:10]
        
        return {
            'total_tags': user_tags.count(),
            'top_tags': user_tags,
        }
    
    def _get_recent_activity(self, user):
        """Get recent activity."""
        # Generic activity placeholder
        return []
    
    def _get_quick_actions(self, user):
        """Get quick actions for dashboard."""
        actions = []
        
        # Manage tags
        from apps.handlers.models import Person
        person = Person.objects.filter(user=user).first()
        if person and person.tagged_items.count() < 5:
            actions.append({
                'title': 'Add Tags',
                'description': 'Tag your profile for better visibility',
                'icon': 'tag',
                'url': '/profile/tags/',
                'color': 'warning',
                'priority': 3,
            })
        
        # Sort by priority
        actions.sort(key=lambda x: x['priority'])
        return actions
