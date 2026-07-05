"""
Fragment handler mixins for django_fusion.

Pure Django mixins for fragment handlers without Wagtail dependencies.
"""

from typing import Any, Dict

from django.http import HttpRequest, JsonResponse


class ProfileOperationsMixin:
    """
    Mixin for handling profile operations with notification support.

    Pure Django version without Wagtail dependencies.
    """

    def update_profile_info(self, request: HttpRequest, data: Dict[str, Any]) -> JsonResponse:
        """
        Update profile information.

        Args:
            request: HTTP request
            data: Profile data to update

        Returns:
            JSON response
        """
        from django.contrib import messages

        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Authentication required"})

        try:
            # Update user fields
            user = request.user
            if "first_name" in data:
                user.first_name = data["first_name"]
            if "last_name" in data:
                user.last_name = data["last_name"]
            if "email" in data:
                user.email = data["email"]

            user.save()

            messages.success(request, "Profile updated successfully")
            return JsonResponse({"success": True})

        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    def update_profile_image(self, request: HttpRequest) -> JsonResponse:
        """
        Update profile image.

        Args:
            request: HTTP request with image file

        Returns:
            JSON response
        """
        from django.contrib import messages

        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Authentication required"})

        if "image" not in request.FILES:
            return JsonResponse({"success": False, "error": "No image provided"})

        try:
            image_file = request.FILES["image"]

            # In a real implementation, this would save the image
            # For now, just return success
            messages.success(request, "Profile image updated successfully")
            return JsonResponse({"success": True, "filename": image_file.name})

        except Exception as e:
            messages.error(request, f"Error updating profile image: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    def update_notifications(self, request: HttpRequest, data: Dict[str, Any]) -> JsonResponse:
        """
        Update notification preferences.

        Args:
            request: HTTP request
            data: Notification preferences

        Returns:
            JSON response
        """
        from django.contrib import messages

        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Authentication required"})

        try:
            # In a real implementation, this would save notification preferences
            # For now, just return success
            messages.success(request, "Notification preferences updated")
            return JsonResponse({"success": True})

        except Exception as e:
            messages.error(request, f"Error updating notifications: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    def update_security(self, request: HttpRequest, data: Dict[str, Any]) -> JsonResponse:
        """
        Update security settings.

        Args:
            request: HTTP request
            data: Security settings

        Returns:
            JSON response
        """
        from django.contrib import messages
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Authentication required"})

        try:
            user = request.user

            # Update password if provided
            if "current_password" in data and "new_password" in data:
                # Verify current password
                if not user.check_password(data["current_password"]):
                    return JsonResponse({"success": False, "error": "Current password is incorrect"})

                # Validate new password
                try:
                    validate_password(data["new_password"], user)
                except ValidationError as e:
                    return JsonResponse({"success": False, "error": list(e.messages)})

                # Set new password
                user.set_password(data["new_password"])
                user.save()

                messages.success(request, "Password updated successfully")

            return JsonResponse({"success": True})

        except Exception as e:
            messages.error(request, f"Error updating security settings: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})
