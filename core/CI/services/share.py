from __future__ import annotations

import logging
import secrets
import string
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


# =============================================================================
# SHARING & INVITATION SERVICE
# =============================================================================

class SharingInvitationService:
    """
    Service for handling sharing and invitation operations.
    Separated from manager for better separation of concerns.
    """
    
    @staticmethod
    def generate_share_token(person_id: str, expires_hours: int = 24) -> str | None:
        """
        Generate a secure token for sharing profile.
        Returns token if successful, None otherwise.
        """
        try:
            # Generate secure token
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            
            # Store token in cache with expiration
            cache_key = f"share_token:{token}"
            cache_data = {
                'person_id': person_id,
                'created_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timezone.timedelta(hours=expires_hours)).isoformat()
            }
            cache.set(cache_key, cache_data, expires_hours * 3600)
            
            return token
        except Exception as e:
            logger.error(f"Failed to generate share token: {e}")
            return None
    
    @staticmethod
    def get_person_by_share_token(token: str):
        """
        Get person by share token if valid.
        Returns person if token is valid and not expired, None otherwise.
        """
        cache_key = f"share_token:{token}"
        token_data = cache.get(cache_key)
        
        if not token_data:
            return None
        
        # Check expiration
        expires_at = timezone.datetime.fromisoformat(token_data['expires_at'])
        if timezone.now() > expires_at:
            cache.delete(cache_key)
            return None
        
        try:
            from .models import Person
            person = Person.objects.get(id=token_data['person_id'])
            return person
        except Person.DoesNotExist:
            cache.delete(cache_key)
            return None
    
    @staticmethod
    def generate_shareable_link(person_id: str, **kwargs) -> dict[str, Any]:
        """
        Generate a shareable link for a person's profile.
        Returns dict with link and metadata.
        """
        try:
            from .models import Person
            person = Person.objects.get(id=person_id)
            
            # Generate token
            token = SharingInvitationService.generate_share_token(person_id, **kwargs)
            if not token:
                return {}
            
            # Create shareable link
            base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            share_url = f"{base_url}/share/profile/{token}/"
            
            return {
                'token': token,
                'share_url': share_url,
                'expires_hours': kwargs.get('expires_hours', 24),
                'created_at': timezone.now(),
                'person_id': person_id,
                'person_name': person.full_name,
            }
        except Person.DoesNotExist:
            return {}

