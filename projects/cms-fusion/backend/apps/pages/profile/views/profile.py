"""
Profile views for fusion-cms.

All heavy imports (django_fusion.site) are deferred to
dispatch-time to avoid the `RuntimeError: Conflicting 'role' models` that
occurs when these libraries are imported during URL-pattern loading
(before django.setup() has fully registered all app models).
"""
import logging

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.pages.accounts.management.services import PersonService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lazy base-class resolver
# ---------------------------------------------------------------------------

_BASES_CACHE: dict = {}


def _profile_bases():
    """Return (PageHandler, ProfileContextMixin, ProfileOperationsMixin) lazily."""
    if not _BASES_CACHE:
        from django_fusion.site.interface.page_handler import PageHandler

        from apps.core.domain.site.mixins import ProfileContextMixin, ProfileOperationsMixin
        _BASES_CACHE["PageHandler"] = PageHandler
        _BASES_CACHE["ProfileContextMixin"] = ProfileContextMixin
        _BASES_CACHE["ProfileOperationsMixin"] = ProfileOperationsMixin
    return (
        _BASES_CACHE["PageHandler"],
        _BASES_CACHE["ProfileContextMixin"],
        _BASES_CACHE["ProfileOperationsMixin"],
    )


def _person_model():
    from apps.core.domain.models.users.users import Person
    return Person


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class ProfileView(View):
    """
    Profile view — resolves PageHandler base lazily at first request.
    """

    page_title = _("Profile")
    template_name = "base_profile.html"
    fragment_name = "profile.profile"
    layout_path = "profile/skeleton.html"

    def dispatch(self, request, *args, **kwargs):
        # Rebuild with real bases on first call
        PageHandler, ProfileContextMixin, ProfileOperationsMixin = _profile_bases()
        if not isinstance(self, PageHandler):
            self.__class__ = type(
                self.__class__.__name__,
                (PageHandler, ProfileContextMixin, ProfileOperationsMixin, View),
                dict(self.__class__.__dict__),
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, request: HttpRequest, **kwargs):
        self.request = request
        try:
            context = super().get_context_data(**kwargs)
        except AttributeError:
            context = {}

        try:
            if request.user.is_authenticated:
                Person = _person_model()
                person = Person.objects.filter(user=request.user).first()
                if person:
                    profile_info = PersonService.get_user_profile_information(request.user)
                    context.update({
                        "person": person,
                        "profile_info": profile_info,
                        "completion_percentage": person.completion_percentage,
                        "is_complete": person.is_complete,
                        "social_links": person.social_links,
                        "certifications": person.certifications,
                        "projects": person.projects,
                        "activity_stats": {
                            "last_active": person.last_active,
                            "member_since": person.created_at.date(),
                            "profile_views": 0,
                            "completion_score": person.completion_percentage,
                        },
                        "verification": {
                            "email": person.email_verified,
                            "phone": person.phone_verified,
                        },
                    })
                else:
                    context.update({"person": None, "profile_info": {}, "completion_percentage": 0, "is_complete": False})
        except Exception as e:
            logger.error("Error getting profile context: %s", e)

        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        return JsonResponse({"status": "error", "message": _("Invalid endpoint.")}, status=400)


class ProfileEditView(ProfileView):
    template_name = "base_modal.html"
    fragment_name = "profile.forms.edit_profile"

    def get_context_data(self, request: HttpRequest, **kwargs):
        context = super().get_context_data(request, **kwargs)
        context["form_sections"] = [
            {"id": "basic", "title": _("Basic Information"), "fields": ["first_name", "last_name", "email", "phone"], "icon": "user"},
            {"id": "personal", "title": _("Personal Details"), "fields": ["birth_date", "gender", "address", "city", "country"], "icon": "info"},
            {"id": "professional", "title": _("Professional Information"), "fields": ["job_title", "company", "industry", "bio"], "icon": "briefcase"},
            {"id": "social", "title": _("Social Links"), "fields": ["website", "linkedin_url", "github_url"], "icon": "link"},
        ]
        return context


class ProfileImageUploadView(ProfileView):
    def post(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": _("Authentication required.")}, status=401)
        try:
            Person = _person_model()
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse({"status": "error", "message": _("Profile not found.")}, status=404)
            image = request.FILES.get("profile_image")
            if not image:
                return JsonResponse({"status": "error", "message": _("No image provided.")}, status=400)
            if image.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
                return JsonResponse({"status": "error", "message": _("Invalid file type.")}, status=400)
            if image.size > 5 * 1024 * 1024:
                return JsonResponse({"status": "error", "message": _("File too large (max 5 MB).")}, status=400)
            person.profile_image = image
            person.save()
            return render(request, "profile/partials/avatar_image.html", {"user_profile": person, "user": request.user})
        except Exception as e:
            logger.error("Error uploading profile image: %s", e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class ProfileImageRemoveView(ProfileView):
    def post(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": _("Authentication required.")}, status=401)
        try:
            Person = _person_model()
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse({"status": "error", "message": _("Profile not found.")}, status=404)
            if person.profile_image:
                person.profile_image.delete()
                person.profile_image = None
                person.save()
            return render(request, "profile/partials/avatar_image.html", {"user_profile": person, "user": request.user})
        except Exception as e:
            logger.error("Error removing profile image: %s", e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)