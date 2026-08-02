# managers/user_manager.py
"""
UserManager
===========
Enhanced UserManager with profile and person creation.

Canonical import: from django_fusion.management.managers.user import UserManager

Pure Django — no Wagtail, no Celery.
"""

import logging
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth import authenticate
from django.contrib.auth.models import BaseUserManager
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from .base import CachedManager

logger = logging.getLogger(__name__)


class UserManager(CachedManager, BaseUserManager):
    """
    Enhanced user manager with authentication, caching, and automatic
    profile/person creation.
    """

    def __init__(self):
        super().__init__(
        )
        self.cache_key_prefix = "user_manager"

    def create_user(self, email, password=None, **extra_fields):
        """
        Create regular user with automatic person and profile creation.
        """
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        # Create user
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Create person and profile records
        self._create_user_records(user, extra_fields)

        # Cache the new user
        self._cache_user(user)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create superuser with person and profile creation.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def _create_user_records(self, user: models.Model, extra_fields: Dict[str, Any]) -> None:
        """
        Create person and profile records for a new user.
        """
        try:
            # Hook: projects can override _create_user_records to add person/profile creation
            # by subclassing UserManager and implementing this method.
            pass
        except Exception as e:
            logger.error(f"Failed to create user records: {e}")
            # Don't raise - user creation should succeed even if person/profile fails

    def _cache_user(self, user: models.Model) -> None:
        """Cache user data."""
        if not self.enable_cache:
            return

        cache_keys = {
            f"{self.cache_key_prefix}:id:{user.id}": user,
            f"{self.cache_key_prefix}:email:{user.email.lower()}": user,
        }

        for key, value in cache_keys.items():
            cache.set(key, value, self.cache_timeout)

    def get_by_email_cached(self, email: str) -> Optional[models.Model]:
        """Get user by email with caching."""
        return self.get_cached(
            identifier=email,
            field='email__iexact'
        )

    def get_by_id_cached(self, user_id: str) -> Optional[models.Model]:
        """Get user by ID with caching."""
        return self.get_cached(
            identifier=user_id,
            field='id'
        )

    def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Tuple[bool, Optional[models.Model], str]:
        """
        Authenticate user with security checks.
        """
        try:
            # Get user by email
            user = self.get_by_email_cached(email)
            if not user:
                return False, None, "Invalid credentials"

            # Check if user is active
            if not user.is_active:
                return False, user, "Account is deactivated"

            # Check login attempts
            if not self._check_login_attempts(user):
                return False, user, "Account is temporarily locked"

            # Authenticate
            authenticated_user = authenticate(
                username=user.email,
                password=password,
            )

            if authenticated_user:
                # Record successful login
                self._record_successful_login(user)
                return True, user, "Authentication successful"
            else:
                # Record failed login
                self._record_failed_login(user)
                return False, user, "Invalid credentials"

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, f"Authentication error: {str(e)}"

    def _check_login_attempts(self, user: models.Model) -> bool:
        """Check if user can attempt login."""
        # Check if account is locked
        if hasattr(user, 'account_locked_until') and user.account_locked_until:
            if user.account_locked_until > timezone.now():
                return False

        # Reset failed attempts if lock period passed
        if hasattr(user, 'account_locked_until') and user.account_locked_until:
            if user.account_locked_until <= timezone.now():
                user.failed_login_attempts = 0
                user.account_locked_until = None
                user.save(update_fields=["failed_login_attempts", "account_locked_until"])

        return True

    def _record_failed_login(self, user: models.Model) -> None:
        """Record failed login attempt."""
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.account_locked_until = timezone.now() + timedelta(minutes=15)

            user.save(update_fields=["failed_login_attempts", "account_locked_until"])

            # Invalidate cache
            self.invalidate_object_cache(user)

    def _record_successful_login(self, user: models.Model) -> None:
        """Record successful login."""
        # Reset security counters
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts = 0

        if hasattr(user, 'account_locked_until'):
            user.account_locked_until = None

        # Update login tracking
        user.last_login = timezone.now()

        # Update fields
        update_fields = ["last_login"]
        if hasattr(user, 'failed_login_attempts'):
            update_fields.append("failed_login_attempts")
        if hasattr(user, 'account_locked_until'):
            update_fields.append("account_locked_until")

        user.save(update_fields=update_fields)

        # Also update person's last_active if exists
        # Hook: projects can override _on_successful_login to add person tracking

        # Invalidate cache
        self.invalidate_object_cache(user)

    def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any],
    ) -> Tuple[bool, Optional[models.Model], str]:
        """
        Update user profile with validation and sync with person.
        """
        try:
            user = self.get_by_id_cached(user_id)
            if not user:
                return False, None, "User not found"

            old_email = user.email if "email" in updates else None

            # Validate email uniqueness
            if "email" in updates:
                new_email = updates["email"].lower().strip()
                if self.filter(email=new_email).exclude(id=user_id).exists():
                    return False, None, "Email already in use"
                updates["email"] = new_email

            # Update user fields
            for field, value in updates.items():
                setattr(user, field, value)

            user.save()

            # Sync with person record
            # Hook: projects can override _sync_person_on_profile_update for person sync
            try:
                pass  # No-op: person sync is project-specific
            except:
                pass  # Don't fail if person sync fails

            # Invalidate cache
            self.invalidate_object_cache(user)

            # Invalidate old email cache
            if old_email and old_email.lower() != user.email.lower():
                old_cache_key = f"{self.cache_key_prefix}:email:{old_email.lower()}"
                cache.delete(old_cache_key)

            return True, user, "Profile updated successfully"

        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False, None, str(e)

    def get_user_profile_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user information for profile context.
        Includes user, person, and profile data.
        """
        try:
            user = self.get_by_id_cached(user_id)
            if not user:
                return {}

            context = {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                }
            }

            # Add person data if exists
            # Hook: projects can override get_user_profile_context to add person data
            try:
                pass  # No-op: person data is project-specific
            except:
                pass  # Don't fail if person/profile data unavailable

            # Add permissions and groups
            if hasattr(user, 'get_all_permissions'):
                context['permissions'] = list(user.get_all_permissions())

            if hasattr(user, 'groups'):
                context['groups'] = list(user.groups.values_list('name', flat=True))

            return context

        except Exception as e:
            logger.error(f"Failed to get user profile context: {e}")
            return {}

    def _get_profile_preferences(self, profile) -> Dict[str, Any]:
        """Extract preferences from profile."""
        preferences = {}

        # Add notification preferences
        for field in ['email_notifications', 'sms_notifications', 'newsletter_notifications']:
            if hasattr(profile, field):
                preferences[field] = getattr(profile, field)

        return preferences

    def invalidate_object_cache(self, user: models.Model) -> bool:
        """Invalidate cache for a specific user object."""
        try:
            # Invalidate by ID
            self.cache_delete("get", str(user.id))

            # Invalidate by email
            self.cache_delete("get", user.email)

            # Pattern deletion for Redis
            if self.is_redis_available():
                patterns = [
                    f"{self.cache_key_prefix}:*:{user.id}",
                    f"{self.cache_key_prefix}:*:{user.email.lower()}",
                ]
                for pattern in patterns:
                    self.delete_cache_pattern(pattern)

            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False
