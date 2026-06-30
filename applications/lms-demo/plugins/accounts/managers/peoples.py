import logging
from datetime import date
from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Q, QuerySet
from django.utils import timezone
from django_osoul.managers import CachedManager
from www.core.CI.services import *

# from ceptor_ai.workflows.pipelines.models.manage.tags import PersonTag, TaggedPerson

if TYPE_CHECKING:
    from ..models import Person

logger = logging.getLogger(__name__)
User = get_user_model()



# =============================================================================
# PERSON MANAGER WITH ALL PROFILE OPERATIONS
# =============================================================================

class PersonManager(CachedManager):
    """
    Comprehensive manager for Person model that includes all profile operations.
    Inherits from CachedManager for intelligent caching.
    """

    def __init__(self):
        super().__init__(
            # cache_timeout=1800,  # 30 minutes
            # enable_cache=True
        )
        self.cache_key_prefix = "person_manager"

    # ---------------------------------------------------------------
    # CORE QUERYSETS (Combined from both Person and Profile)
    # ---------------------------------------------------------------
    def active(self) -> QuerySet:
        """Return active persons."""
        return self.filter_cached(
            filters={'is_active': True},
            include_related=True
        ).select_related('organization', 'user')

    def with_user_profile(self) -> QuerySet:
        """Return persons with linked user profiles."""
        return self.active().filter(
            user__isnull=False
        ).select_related('user')

    def with_full_profile(self) -> QuerySet:
        """Return persons with all related data prefetched."""
        return self.filter_cached(
            filters={'is_active': True},
            include_related=True
        ).prefetch_related(
            'contact_methods',
        ).select_related(
            'organization',
            'user'
        )

    def get_complete_profiles(self) -> QuerySet:
        """Return persons with complete profile information."""
        return self.filter_cached(
            filters={
                'is_active': True,
                'first_name__isnull': False,
                'last_name__isnull': False,
                'email__isnull': False,
                'email_verified': True,
            }
        ).exclude(
            Q(first_name='') | Q(last_name='') | Q(email='')
        )

    def by_profile_type(self, profile_type: str) -> QuerySet:
        """Return persons by profile type."""
        return self.filter_cached(
            filters={'profile_type': profile_type},
            include_related=True
        )

    # ---------------------------------------------------------------
    # GETTERS & FINDERS (Combined)
    # ---------------------------------------------------------------
    def get_by_email(self, email: str):
        """Get person by email (case-insensitive)."""
        return self.get_cached(
            identifier=email,
            field='email__iexact'
        )

    def get_by_user(self, user: User):
        """Get person by user instance."""
        return self.get_cached(
            identifier=user.id,
            field='user_id'
        )

    def get_by_user_id(self, user_id: int):
        """Get person by user ID."""
        return self.get_cached(
            identifier=user_id,
            field='user_id'
        )

    def get_by_uuid(self, uuid: str):
        """Get person by UUID string."""
        return self.get_cached(
            identifier=uuid,
            field='id'
        )

    def get_by_full_name(self, full_name: str) -> QuerySet:
        """Get persons by full name."""
        return self.filter_cached(
            filters={'full_name__iexact': full_name},
            include_related=True
        )

    def get_or_create_for_user(self, user: User, **defaults) -> tuple['Person', bool]:
        """
        Get or create person for a user.
        """
        try:
            person = self.get_by_user(user)
            return person, False
        except self.model.DoesNotExist:
            # Create person
            person = self.create(
                user=user,
                first_name=user.first_name or '',
                last_name=user.last_name or '',
                email=user.email,
                profile_type=self.model.ProfileType.CONTACT,
                status=self.model.Status.ACTIVE,
                is_active=True,
                created_by=user,
                updated_by=user,
                **defaults
            )

            # Invalidate cache
            self.invalidate_object_cache(person)
            return person, True

    # ---------------------------------------------------------------
    # SEARCH & FILTER (Combined)
    # ---------------------------------------------------------------
    def search(self, query: str, limit: int = 20) -> QuerySet:
        """Search persons by multiple criteria."""
        return self.filter_cached(
            filters={
                'is_active': True,
            },
            include_related=True
        ).filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(job_title__icontains=query) |
            Q(organization__name__icontains=query) |
            Q(address__icontains=query) |
            Q(professional_summary__icontains=query)
        ).distinct()[:limit]

    def filter_by_demographics(
        self,
        gender: str = None,
        min_age: int = None,
        max_age: int = None,
        country: str = None,
        marital_status: str = None
    ) -> QuerySet:
        """Filter persons by demographic criteria."""
        filters = {'is_active': True}

        if gender:
            filters['gender'] = gender

        if country:
            filters['country__iexact'] = country

        if marital_status:
            filters['marital_status'] = marital_status

        qs = self.filter_cached(
            filters=filters,
            include_related=True
        )

        # Age filtering
        if min_age or max_age:
            today = date.today()
            qs = qs.filter(birth_date__isnull=False)

            if max_age:
                min_birth_date = date(today.year - max_age - 1, today.month, today.day)
                qs = qs.filter(birth_date__gte=min_birth_date)

            if min_age:
                max_birth_date = date(today.year - min_age, today.month, today.day)
                qs = qs.filter(birth_date__lte=max_birth_date)

        return qs

    def filter_by_notification_preferences(
        self,
        email_notifications: bool = None,
        sms_notifications: bool = None,
        newsletter_notifications: bool = None
    ) -> QuerySet:
        """Filter persons by notification preferences."""
        filters = {'is_active': True}

        if email_notifications is not None:
            filters['email_notifications'] = email_notifications

        if sms_notifications is not None:
            filters['sms_notifications'] = sms_notifications

        if newsletter_notifications is not None:
            filters['newsletter_notifications'] = newsletter_notifications

        return self.filter_cached(
            filters=filters,
            include_related=True
        )

    # ---------------------------------------------------------------
    # PROFILE OPERATIONS (From old Profile model)
    # ---------------------------------------------------------------
    def update_last_active(self, person_id: str) -> bool:
        """Update last active timestamp."""
        try:
            person = self.get_by_uuid(person_id)
            person.last_active = timezone.now()
            person.save(update_fields=['last_active'])

            # Invalidate cache
            self.invalidate_object_cache(person)
            return True
        except self.model.DoesNotExist:
            return False

    def verify_email(self, person_id: str) -> bool:
        """Mark email as verified."""
        try:
            person = self.get_by_uuid(person_id)
            person.email_verified = True
            person.save(update_fields=['email_verified'])

            # Also update user's email if needed
            if person.user and person.user.email != person.email:
                person.user.email = person.email
                person.user.save()

            self.invalidate_object_cache(person)
            return True
        except self.model.DoesNotExist:
            return False

    def verify_phone(self, person_id: str) -> bool:
        """Mark phone as verified."""
        try:
            person = self.get_by_uuid(person_id)
            person.phone_verified = True
            person.save(update_fields=['phone_verified'])
            self.invalidate_object_cache(person)
            return True
        except self.model.DoesNotExist:
            return False

    def activate_person(self, person_id: str) -> bool:
        """Activate the person."""
        try:
            person = self.get_by_uuid(person_id)
            person.status = self.model.Status.ACTIVE
            person.is_active = True

            # Also activate user if exists
            if person.user:
                person.user.is_active = True
                person.user.save()

            person.save(update_fields=['status', 'is_active'])
            self.invalidate_object_cache(person)
            return True
        except self.model.DoesNotExist:
            return False

    def deactivate_person(self, person_id: str) -> bool:
        """Deactivate the person."""
        try:
            person = self.get_by_uuid(person_id)
            person.status = self.model.Status.INACTIVE
            person.is_active = False

            # Also deactivate user if exists
            if person.user:
                person.user.is_active = False
                person.user.save()

            person.save(update_fields=['status', 'is_active'])
            self.invalidate_object_cache(person)
            return True
        except self.model.DoesNotExist:
            return False

    def get_profile_statistics(self, person_id: str) -> dict[str, Any]:
        """Get detailed statistics for a person."""
        cache_key = f"{self.cache_key_prefix}:stats:{person_id}"

        if self.enable_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            person = self.with_full_profile().get(id=person_id)

            # Calculate completion percentage
            fields_to_check = [
                person.first_name,
                person.last_name,
                person.email,
                person.professional_summary,
                person.job_title,
                person.profile_image,
                person.linkedin_url,
            ]
            completed = sum(1 for field in fields_to_check if field)
            completion_percentage = int((completed / len(fields_to_check)) * 100)

            stats = {
                'person_id': person.id,
                'completion_percentage': completion_percentage,
                'age': person.age,
                'days_since_created': (timezone.now().date() - person.created_at.date()).days if person.created_at else None,
                'days_since_last_active': (timezone.now().date() - person.last_active.date()).days if person.last_active else None,
                'has_profile_image': bool(person.profile_image),
                'has_cover_image': bool(person.cover_image),
                'has_resume': bool(person.resume),
                'social_links_count': len(person.social_links),
                'certifications_count': len(person.certifications),
                'projects_count': len(person.projects),
                'is_complete': person.is_complete,
                'notification_channels': person.notification_channels,
            }

            if self.enable_cache:
                cache.set(cache_key, stats, self.cache_timeout)

            return stats

        except self.model.DoesNotExist:
            return {}

    # ---------------------------------------------------------------
    # SHARING & INVITATION OPERATIONS (Using Services)
    # ---------------------------------------------------------------
    def generate_share_token(self, person_id: str, expires_hours: int = 24) -> str | None:
        """Generate a share token for a person."""
        return SharingInvitationService.generate_share_token(person_id, expires_hours)

    def get_person_by_share_token(self, token: str):
        """Get person by share token if valid."""
        return SharingInvitationService.get_person_by_share_token(token)

    def generate_shareable_link(self, person_id: str, **kwargs) -> dict[str, Any]:
        """Generate a shareable link for a person's profile."""
        return SharingInvitationService.generate_shareable_link(person_id, **kwargs)

    def send_invitation(
        self,
        person_id: str,
        inviter: User,
        invitation_type: str = 'join',
        message: str = ''
    ) -> dict[str, Any]:
        """Send an invitation to a person."""
        return InvitationService.send_invitation(person_id, inviter, invitation_type, message)

    def accept_invitation(self, token: str) -> dict[str, Any]:
        """Accept an invitation using token."""
        return InvitationService.accept_invitation(token)

    # ---------------------------------------------------------------
    # BULK OPERATIONS
    # ---------------------------------------------------------------
    def bulk_update_last_active(self, person_ids: list[str]) -> int:
        """Bulk update last_active timestamp."""
        updated = self.filter(id__in=person_ids).update(
            last_active=timezone.now()
        )

        # Invalidate cache
        for person_id in person_ids:
            self.cache_delete("get", person_id)
            cache.delete(f"{self.cache_key_prefix}:stats:{person_id}")

        return updated

    def bulk_verify_emails(self, person_ids: list[str]) -> int:
        """Bulk verify emails."""
        updated = self.filter(id__in=person_ids).update(email_verified=True)

        # Also update user emails if linked
        persons = self.filter(id__in=person_ids, user__isnull=False)
        for person in persons:
            if person.user and person.user.email != person.email:
                person.user.email = person.email
                person.user.save()

        # Invalidate cache
        for person_id in person_ids:
            self.cache_delete("get", person_id)
            cache.delete(f"{self.cache_key_prefix}:stats:{person_id}")

        return updated

    def bulk_activate(self, person_ids: list[str]) -> int:
        """Bulk activate persons."""
        updated = self.filter(id__in=person_ids).update(
            status=self.model.Status.ACTIVE,
            is_active=True
        )

        # Also activate users
        persons = self.filter(id__in=person_ids, user__isnull=False)
        for person in persons:
            if person.user:
                person.user.is_active = True
                person.user.save()

        # Invalidate cache
        for person_id in person_ids:
            self.cache_delete("get", person_id)
            cache.delete(f"{self.cache_key_prefix}:stats:{person_id}")

        return updated

    def bulk_update_notification_preferences(
        self,
        person_ids: list[str],
        **preferences
    ) -> int:
        """Bulk update notification preferences."""
        valid_fields = {'email_notifications', 'sms_notifications', 'newsletter_notifications'}
        update_fields = {k: v for k, v in preferences.items() if k in valid_fields}

        if not update_fields:
            return 0

        updated = self.filter(id__in=person_ids).update(**update_fields)

        # Invalidate cache
        for person_id in person_ids:
            self.cache_delete("get", person_id)
            cache.delete(f"{self.cache_key_prefix}:stats:{person_id}")

        return updated

    # ---------------------------------------------------------------
    # STATISTICS & ANALYTICS (Combined)
    # ---------------------------------------------------------------
    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics."""
        cache_key = f"{self.cache_key_prefix}:global_stats"

        if self.enable_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        stats = self.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            with_user=Count('id', filter=Q(user__isnull=False)),
            email_verified=Count('id', filter=Q(email_verified=True)),
            phone_verified=Count('id', filter=Q(phone_verified=True)),
            has_organization=Count('id', filter=Q(organization__isnull=False)),
            email_notifications_enabled=Count('id', filter=Q(email_notifications=True)),
            sms_notifications_enabled=Count('id', filter=Q(sms_notifications=True)),
            newsletter_subscribed=Count('id', filter=Q(newsletter_notifications=True)),
        )

        # Profile type distribution
        type_stats = {}
        for choice in self.model.ProfileType.choices:
            type_code, type_name = choice
            count = self.filter(profile_type=type_code).count()
            type_stats[type_code] = {
                'name': type_name,
                'count': count,
                'percentage': (count / stats['total'] * 100) if stats['total'] > 0 else 0
            }

        stats['type_distribution'] = type_stats

        if self.enable_cache:
            cache.set(cache_key, stats, self.cache_timeout)

        return stats

    # ---------------------------------------------------------------
    # USER PROFILE METHODS
    # ---------------------------------------------------------------
    def get_or_create_user_profile(self, user: User) -> Any:
        """
        Get or create a user profile for the person.
        If Wagtail profile not found, find a profile with related field to user model.
        """
        try:
            # First, try to get the person for this user
            person = self.get_by_user(user)

            # If person has no profile, try to find one through related fields
            if not hasattr(person, 'user_profile'):
                # Look for any profile model related to user
                # This is a generic approach that can be customized
                profile_models = [
                    'userprofile', 'profile', 'account', 'user_profile'
                ]

                for model_name in profile_models:
                    if hasattr(user, model_name):
                        profile = getattr(user, model_name)
                        setattr(person, 'user_profile', profile)
                        return profile

            return getattr(person, 'user_profile', None)

        except self.model.DoesNotExist:
            # Create a new person for the user
            person, created = self.get_or_create_for_user(user)
            return getattr(person, 'user_profile', None)

    # ---------------------------------------------------------------
    # CACHE MANAGEMENT
    # ---------------------------------------------------------------
    def invalidate_object_cache(self, person: 'Person') -> bool:
        """Invalidate cache for a specific person object."""
        try:
            # Invalidate by UUID
            self.cache_delete("get", str(person.id))

            # Invalidate by other identifiers
            self.cache_delete("get", person.email)

            # Invalidate statistics cache
            cache.delete(f"{self.cache_key_prefix}:stats:{person.id}")

            # Invalidate global stats
            cache.delete(f"{self.cache_key_prefix}:global_stats")

            # Pattern deletion for Redis
            if self.is_redis_available():
                patterns = [
                    f"{self.cache_key_prefix}:filter:*",
                    f"{self.cache_key_prefix}:stats:*",
                ]
                for pattern in patterns:
                    self.delete_cache_pattern(pattern)

            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False
