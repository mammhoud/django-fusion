"""
Tag management views for the blog app.
"""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from www.apps.blog.forms import BlogTagForm
from www.apps.blog.models import BlogTag
from www.apps.blog.services import TagService


@method_decorator(staff_member_required, name="dispatch")
class TagListView(ListView):
    """List all tags with post counts."""

    model = BlogTag
    template_name = "blog/tags/tag_list.html"
    context_object_name = "tags"
    paginate_by = 20

    def get_queryset(self):
        queryset = BlogTag.objects.annotate(
            post_count=Count("posts")
        ).order_by("name")

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tag Management")
        context["search_query"] = self.request.GET.get("q", "")
        context["total_tags"] = BlogTag.objects.count()
        context["unused_count"] = BlogTag.objects.annotate(
            post_count=Count("posts")
        ).filter(post_count=0).count()
        return context


@method_decorator(staff_member_required, name="dispatch")
class TagCreateView(CreateView):
    """Create a new tag."""

    model = BlogTag
    form_class = BlogTagForm
    template_name = "blog/tags/tag_form.html"
    success_url = reverse_lazy("blog:tag_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Tag")
        context["action"] = "create"
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Tag created successfully."))
        return super().form_valid(form)


@method_decorator(staff_member_required, name="dispatch")
class TagUpdateView(UpdateView):
    """Edit an existing tag."""

    model = BlogTag
    form_class = BlogTagForm
    template_name = "blog/tags/tag_form.html"
    success_url = reverse_lazy("blog:tag_list")
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Tag")
        context["action"] = "edit"
        context["post_count"] = self.object.get_post_count()
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Tag updated successfully."))
        return super().form_valid(form)


@method_decorator(staff_member_required, name="dispatch")
class TagDeleteView(DeleteView):
    """Delete a tag."""

    model = BlogTag
    template_name = "blog/tags/tag_confirm_delete.html"
    success_url = reverse_lazy("blog:tag_list")
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Delete Tag")
        context["post_count"] = self.object.get_post_count()
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Tag deleted successfully."))
        return super().form_valid(form)


@method_decorator(staff_member_required, name="dispatch")
class TagCleanupView(ListView):
    """List and clean up unused tags."""

    model = BlogTag
    template_name = "blog/tags/tag_cleanup.html"
    context_object_name = "unused_tags"

    def get_queryset(self):
        return BlogTag.objects.annotate(
            post_count=Count("posts")
        ).filter(post_count=0).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Cleanup Unused Tags")
        return context

    def post(self, request, *args, **kwargs):
        count = TagService.cleanup_unused_tags()
        messages.success(
            request,
            _("%(count)d unused tag(s) removed.") % {"count": count},
        )
        return redirect("blog:tag_list")
