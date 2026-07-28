# services/person_service.py
"""
Service for complex person operations.

Delegates to apps.core.domain.services.PersonServiceBase
Canonical import: from django_fusion.services.infrastructure import BaseService
"""

import logging
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.core.domain.models.users.users import Person

logger = logging.getLogger(__name__)
User = get_user_model()


class PersonService:
    """
    Service for handling complex person operations.
    Separates business logic from manager methods.
    """


    @staticmethod
    def _create_or_link_profile(person: Person, user: User) -> None:
        """
        Create or link a profile for the person.

        Note: This handles Wagtail profiles or any other profile model
        configured in settings.
        """
        try:
            # Try to get Wagtail profile
            from wagtail.users.models import UserProfile as WagtailUserProfile

            wagtail_profile, created = WagtailUserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'approved_notifications': True,
                    'preferred_language': settings.LANGUAGE_CODE,
                }
            )

            # Link Wagtail profile to person
            person.profile = wagtail_profile
            person.save(update_fields=['profile'])

            logger.debug(f"{'Created' if created else 'Linked'} Wagtail profile for {person.email}")

        except ImportError:
            # Wagtail not available, try other profile models
            PersonService._link_alternative_profile(person, user)
        except Exception as e:
            logger.error(f"Failed to create/link Wagtail profile: {e}")
            PersonService._link_alternative_profile(person, user)

    @staticmethod
    def _link_alternative_profile(person: Person, user: User) -> None:
        """
        Try to link alternative profile models.
        """
        # Try common profile model names
        profile_model_names = [
            'userprofile',
            'profile',
            'account',
            'user_profile',
        ]

        for model_name in profile_model_names:
            if hasattr(user, model_name):
                try:
                    profile = getattr(user, model_name)
                    if profile:
                        person.profile = profile
                        person.save(update_fields=['profile'])
                        logger.info(f"Linked {model_name} profile for {person.email}")
                        return
                except Exception as e:
                    logger.debug(f"Failed to link {model_name} profile: {e}")

        logger.warning(f"No profile model found for {person.email}")

    @staticmethod
    def get_user_profile_information(user: User) -> Dict[str, Any]:
        """
        Get comprehensive profile information for a user.

        Args:
            user: User instance

        Returns:
            Dict with profile information
        """
        try:
            person = Person.objects.filter(user=user).first()
            if not person:
                return {}

            # Get basic person info
            info = {
                'person': {
                    'id': str(person.id),
                    'full_name': person.full_name,
                    'email': person.email,
                    'phone': person.phone,
                    'profile_type': person.profile_type,
                    'status': person.status,
                    'is_active': person.is_active,
                    'completion_percentage': person.completion_percentage,
                    'profile_image_url': person.profile_image.url if person.profile_image else None,
                },
                'preferences': {
                    'email_notifications': person.email_notifications,
                    'sms_notifications': person.sms_notifications,
                    'newsletter_notifications': person.newsletter_notifications,
                },
                'verification': {
                    'email_verified': person.email_verified,
                    'phone_verified': person.phone_verified,
                },
                'activity': {
                    'last_active': person.last_active,
                    'days_since_active': PersonService._days_since(person.last_active),
                },
            }

            # Add professional info if available
            if person.job_title or person.organization:
                info['professional'] = {
                    'job_title': person.job_title,
                    'department': person.department,
                    'organization': str(person.organization) if person.organization else None,
                    'position': person.position,
                    'company': person.company if person.company else None,
                    'industry': person.industry,
                    'years_of_experience': person.years_of_experience,
                }

            # Add profile stats
            info['stats'] = PersonService._calculate_profile_stats(person)

            return info

        except Exception as e:
            logger.error(f"Failed to get user profile information: {e}")
            return {}

    @staticmethod
    def _days_since(dt) -> Optional[int]:
        """Calculate days since a datetime."""
        if not dt:
            return None
        return (timezone.now().date() - dt.date()).days

    @staticmethod
    def _calculate_profile_stats(person: Person) -> Dict[str, Any]:
        """Calculate profile statistics."""
        stats = {
            'social_links_count': len(person.social_links),
            'certifications_count': len(person.certifications),
            'projects_count': len(person.projects),
            'has_profile_image': bool(person.profile_image),
            'has_cover_image': bool(person.cover_image),
            'has_resume': bool(person.resume),
            'has_website': bool(person.website),
            'has_linkedin': bool(person.linkedin_url),
            'has_github': bool(person.github_url),
            'has_twitter': bool(person.twitter_url),
        }

        # Calculate completion score
        required_fields = [
            person.first_name,
            person.last_name,
            person.email,
            person.professional_summary,
        ]

        optional_fields = [
            person.phone,
            person.profile_image,
            person.position,
            person.company,
            person.linkedin_url,
            person.website,
        ]

        required_completion = sum(1 for field in required_fields if field) / len(required_fields)
        optional_completion = sum(1 for field in optional_fields if field) / len(optional_fields)

        # Weighted completion (70% required, 30% optional)
        stats['completion_score'] = int((required_completion * 0.7 + optional_completion * 0.3) * 100)

        return stats


    @staticmethod
    def update_notification_preferences(
        person_id: str,
        preferences: Dict[str, bool]
    ) -> Tuple[bool, str]:
        """
        Update notification preferences for a person.

        Args:
            person_id: Person ID
            preferences: Dict of preference values

        Returns:
            Tuple of (success, message)
        """
        try:
            person = Person.objects.get(id=person_id)

            valid_fields = {
                'email_notifications',
                'sms_notifications',
                'newsletter_notifications',
            }

            updated = False
            for field, value in preferences.items():
                if field in valid_fields and hasattr(person, field):
                    if getattr(person, field) != value:
                        setattr(person, field, value)
                        updated = True

            if updated:
                person.save()

                # Invalidate cache
                from apps.pages.accounts.managers import PersonManager
                PersonManager().invalidate_object_cache(person)

                return True, "Notification preferences updated"

            return False, "No valid preferences to update"

        except Person.DoesNotExist:
            return False, "Person not found"
        except Exception as e:
            logger.error(f"Failed to update notification preferences: {e}")
            return False, str(e)

