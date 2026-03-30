"""
Blog Post Views
"""
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from apps.blog.models import BlogCategory, BlogPost, BlogTag


class BlogPostListView(ListView):
    """
    List view for blog posts with filtering.
    """

    model = BlogPost
    template_name = "blog/blog_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status="published").order_by("-published_date")

        # Filter by category
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(categories__slug=category)

        # Filter by tag
        tag = self.request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Blog")
        context["categories"] = BlogCategory.objects.all()
        context["tags"] = BlogTag.objects.all()
        context["current_category"] = self.request.GET.get("category")
        context["current_tag"] = self.request.GET.get("tag")
        return context


class BlogPostDetailView(DetailView):
    """
    Detail view for a single blog post.
    """

    model = BlogPost
    template_name = "blog/blog_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # Only show published posts to non-staff users
        if self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.object.title
        context["related_posts"] = self.object.get_related_posts(limit=3)
        return context
