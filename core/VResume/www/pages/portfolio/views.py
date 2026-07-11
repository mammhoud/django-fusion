"""
Consolidated views for the portfolio app.
Handles project searching and filtering.
"""
import json
import logging
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from pages.portfolio.models import PortfolioTag, Project

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def portfolio_search(request):
    """
    Search and filter portfolio projects via HTMX.
    """
    q = request.GET.get('q', '').strip()
    tags_param = request.GET.get('tags', '').strip()
    tags_list = [t.strip() for t in tags_param.split(',') if t.strip()]
    
    # Query projects directly from the Project snippet model
    projects = Project.objects.filter(is_active=True).order_by('-date_completed', '-created_at')
    
    if q:
        # Split search terms to support multiple entries (AND logic)
        terms = q.split()
        for term in terms:
            projects = projects.filter(
                Q(title__icontains=term) |
                Q(description__icontains=term) |
                Q(body__icontains=term)
            )
    
    if tags_list:
        projects = projects.filter(tags__slug__in=tags_list).distinct()
    
    paginator = Paginator(projects, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    tags_qs = PortfolioTag.objects.filter(is_active=True).order_by('name')
    context = {
        'featured_projects': page_obj.object_list,
        'page_obj': page_obj,
        'current_tags': tags_param,
        'current_q': q,
        'tags': tags_qs,
        'tags_json': json.dumps([
            {'slug': tag.slug, 'name': tag.name}
            for tag in tags_qs
        ]),
    }
    
    if request.headers.get('HX-Request') == 'true':
        if request.GET.get("append") == "1":
            return render(request, 'portfolio/sections/projects_items.html', context)
        return render(request, 'portfolio/sections/projects.html', context)
    
    query_string = f"?tags={tags_param}&q={q}"
    return redirect(f"{reverse('pages:tab', args=['portfolio'])}{query_string}")
