# profiles/views.py (updated with translations)
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django_osoul.comp.site import PageHandler
from django_rseal.pipelines.models import Person
from django_rseal.pipelines.site.mixins import ProfileContextMixin, ProfileOperationsMixin

from apps.accounts.services import PersonService


class ProfileView(PageHandler, ProfileContextMixin, ProfileOperationsMixin):
    """
    Profile view using PageComponent infrastructure with notification support.
    Handles profile display, updates, and image uploads.
    """

    page_title = _("Profile")
    template_name = "base_profile.html"
    fragment_name = "profile.profile"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for profile page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        try:
            # Get comprehensive profile information
            if request.user.is_authenticated:
                # Get person record
                person = Person.objects.filter(user=request.user).first()

                if person:
                    # Get profile information via service
                    profile_info = PersonService.get_user_profile_information(request.user)

                    context.update(
                        {
                            "person": person,
                            "profile_info": profile_info,
                            "completion_percentage": person.completion_percentage,
                            "is_complete": person.is_complete,
                            "social_links": person.social_links,
                            "certifications": person.certifications,
                            "projects": person.projects,
                        }
                    )

                    # Add activity stats
                    context["activity_stats"] = self._get_activity_stats(person)

                    # Add verification status
                    context["verification"] = {
                        "email": person.email_verified,
                        "phone": person.phone_verified,
                    }

                else:
                    # No person record - show empty profile
                    context["person"] = None
                    context["profile_info"] = {}
                    context["completion_percentage"] = 0
                    context["is_complete"] = False

        except Exception as e:
            # Log error but don't crash the page
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error getting profile context: {e}")

        return context

    def _get_activity_stats(self, person: Person):
        """
        Get activity statistics for the profile.
        """
        return {
            "last_active": person.last_active,
            "member_since": person.created_at.date(),
            "profile_views": 0,  # Placeholder - implement tracking if needed
            "completion_score": person.completion_percentage,
        }

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Handle POST requests - dispatch to appropriate method based on URL name.
        """
        # This method should handle general POST requests if needed
        return JsonResponse({"status": "error", "message": _("Invalid endpoint.")}, status=400)


class ProfileEditView(ProfileView):
    """
    Profile edit view with form handling.
    """

    template_name = "base_modal.html"
    fragment_name = "profile.forms.edit_profile"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for profile edit page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        # Add form sections with translations
        context["form_sections"] = [
            {
                "id": "basic",
                "title": _("Basic Information"),
                "fields": ["first_name", "last_name", "email", "phone"],
                "icon": "user",
            },
            {
                "id": "personal",
                "title": _("Personal Details"),
                "fields": ["birth_date", "gender", "address", "city", "country"],
                "icon": "info",
            },
            {
                "id": "professional",
                "title": _("Professional Information"),
                "fields": ["job_title", "company", "industry", "bio"],
                "icon": "briefcase",
            },
            {
                "id": "social",
                "title": _("Social Links"),
                "fields": ["website", "linkedin_url", "github_url"],
                "icon": "link",
            },
        ]

        return context


class ProfileImageUploadView(ProfileView):
    """
    Handle profile image upload via HTMX.
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Handle profile image upload.
        """
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": _("Authentication required.")}, status=401)

        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse({"status": "error", "message": _("Profile not found.")}, status=404)

            # Get uploaded file
            image = request.FILES.get('profile_image')
            if not image:
                return JsonResponse({"status": "error", "message": _("No image provided.")}, status=400)

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                return JsonResponse({"status": "error", "message": _("Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.")}, status=400)

            # Validate file size (5MB max)
            if image.size > 5 * 1024 * 1024:
                return JsonResponse({"status": "error", "message": _("File size must be less than 5MB.")}, status=400)

            # Save the image
            person.profile_image = image
            person.save()

            # Return updated avatar HTML for HTMX swap
            from django.template.loader import render_to_string
            from django.templatetags.static import static

            avatar_html = f'''<img id="avatarImage"
                 class="profile__avatar-img avatar-img rounded-circle border border-3 border-white shadow"
                 src="{person.profile_image.url}"
                 alt="{_('Avatar')}">'''

            return render(request, 'profile/partials/avatar_image.html', {
                'user_profile': person,
                'user': request.user,
            })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error uploading profile image: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class ProfileImageRemoveView(ProfileView):
    """
    Handle profile image removal via HTMX.
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Handle profile image removal.
        """
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": _("Authentication required.")}, status=401)

        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse({"status": "error", "message": _("Profile not found.")}, status=404)

            # Remove the image
            if person.profile_image:
                person.profile_image.delete()
                person.profile_image = None
                person.save()

            # Return default avatar HTML for HTMX swap
            return render(request, 'profile/partials/avatar_image.html', {
                'user_profile': person,
                'user': request.user,
            })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error removing profile image: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

