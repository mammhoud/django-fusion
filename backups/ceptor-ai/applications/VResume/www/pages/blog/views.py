"""
Consolidated views for the blog app.
Handles listing, detail, search, tracking, and newsletter integration for BlogPost snippets.
"""
import json
import logging
from django.db.models import Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.contrib import messages
from django.core.paginator import Paginator

from pages.blog.models import BlogPage, BlogTag, ArticleRead
from pages.blog.models.snippets.post import BlogPost
from pages.connect.models import Campaign

logger = logging.getLogger(__name__)

# ── Listing & Detail Views ───────────────────────────────────────────

class BlogPostListView(ListView):
    model = BlogPost
    # The legacy path `blog/standalone/blog_index.html` was orphaned when
    # the standalone blog tree was consolidated into the shared asset
    # template. Point to the shared `blog/blog_index.html` (the same one
    # used by CTC and LMS-Demo) so /blog/list/ renders instead of 500'ing.
    template_name = "blog/blog_index.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        qs = BlogPost.objects.filter(is_published=True).order_by("-published_date", "-created_at")
        tag = self.request.GET.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = BlogTag.objects.filter(is_active=True).order_by("display_order", "name")
        context["current_tag"] = self.request.GET.get("tag")
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = "blog/standalone/blog_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        if self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_posts"] = BlogPost.objects.filter(is_published=True).exclude(pk=self.object.pk)[:3]
        return context


# ── Search & Filtering (HTMX) ─────────────────────────────────────────

@require_http_methods(["GET"])
def blog_search(request):
    """
    Search and filter blog posts via HTMX.
    """
    q = request.GET.get('q', '').strip()
    tags_param = request.GET.get('tags', '').strip()
    tags_list = [t.strip() for t in tags_param.split(',') if t.strip()]
    
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_date', '-created_at')
    
    if q:
        # Split search terms to support multiple entries (AND logic)
        terms = q.split()
        for term in terms:
            posts = posts.filter(
                Q(title__icontains=term) |
                Q(introduction__icontains=term) |
                Q(excerpt__icontains=term) |
                Q(body__icontains=term)
            )
    
    if tags_list:
        posts = posts.filter(tags__slug__in=tags_list).distinct()
    
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    tags_qs = BlogTag.objects.filter(is_active=True).order_by('display_order', 'name')
    context = {
        'posts': page_obj.object_list,
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
            return render(request, 'blog/sections/posts_items.html', context)
        return render(request, 'blog/sections/posts.html', context)
    
    query_string = f"?tags={tags_param}&q={q}"
    return redirect(f'/blog/{query_string}')


# ── Tracking & Analytics ───────────────────────────────────────────────

class TrackReadView(View):
    """Track article read — record read duration and scroll depth"""
    
    def post(self, request, post_id):
        try:
            post = get_object_or_404(BlogPost, id=post_id)
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            
            duration_seconds = data.get("duration_seconds", 0)
            scroll_depth = data.get("scroll_depth", 0)
            session_key = data.get("session_key") or request.session.session_key or ""
            ip_address = self.get_client_ip(request)
            
            scroll_depth = max(0, min(100, scroll_depth))
            
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            recent_read = ArticleRead.objects.filter(
                post=post,
                session_key=session_key,
                ip_address=ip_address,
                read_at__gte=one_hour_ago,
            ).first()
            
            is_unique = recent_read is None
            
            if recent_read:
                recent_read.read_duration_seconds = max(recent_read.read_duration_seconds, duration_seconds)
                recent_read.scroll_depth = max(recent_read.scroll_depth, scroll_depth)
                recent_read.save(update_fields=["read_duration_seconds", "scroll_depth"])
                read = recent_read
            else:
                read = ArticleRead.objects.create(
                    post=post,
                    session_key=session_key,
                    ip_address=ip_address,
                    read_duration_seconds=duration_seconds,
                    scroll_depth=scroll_depth,
                    is_unique=is_unique,
                )
            
            # Increment page views count on snippet
            if is_unique:
                BlogPost.objects.filter(pk=post.pk).update(page_views=F('page_views') + 1)
            
            return JsonResponse({"success": True, "read_id": read.id, "is_unique": is_unique})
        except Exception as e:
            logger.error(f"TrackReadView error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


@require_http_methods(["GET"])
def track_read_simple(request, post_id):
    """Fallback tracking endpoint for non-JS clients"""
    try:
        post = get_object_or_404(BlogPost, id=post_id)
        duration_seconds = int(request.GET.get("duration", 0))
        scroll_depth = int(request.GET.get("scroll", 0))
        session_key = request.session.session_key or ""
        ip_address = TrackReadView.get_client_ip(request)
        
        scroll_depth = max(0, min(100, scroll_depth))
        
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        recent_read = ArticleRead.objects.filter(
            post=post, session_key=session_key, ip_address=ip_address, read_at__gte=one_hour_ago
        ).first()
        
        is_unique = recent_read is None
        
        if recent_read:
            recent_read.read_duration_seconds = max(recent_read.read_duration_seconds, duration_seconds)
            recent_read.scroll_depth = max(recent_read.scroll_depth, scroll_depth)
            recent_read.save(update_fields=["read_duration_seconds", "scroll_depth"])
        else:
            ArticleRead.objects.create(
                post=post, session_key=session_key, ip_address=ip_address,
                read_duration_seconds=duration_seconds, scroll_depth=scroll_depth, is_unique=is_unique
            )
            if is_unique:
                BlogPost.objects.filter(pk=post.pk).update(page_views=F('page_views') + 1)
        
        return JsonResponse({"success": True, "is_unique": is_unique})
    except Exception as e:
        logger.error(f"track_read_simple error: {e}")
        return JsonResponse({"error": str(e)}, status=500)


# ── Newsletter Integration ────────────────────────────────────────────

@require_http_methods(["GET"])
def post_preview(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, "blog/modals/blog_preview.html", {"post": post})


@require_http_methods(["GET", "POST"])
def send_newsletter(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    campaign = Campaign.objects.create(
        name=f"Newsletter: {post.title}",
        subject=post.title,
        preview_text=post.introduction[:100] if post.introduction else "",
        body=str(post.body),
        status="draft",
    )
    messages.success(request, f"Created draft campaign: {campaign.name}")
    return redirect(reverse("admin:connect_campaign_change", args=[campaign.pk]))
