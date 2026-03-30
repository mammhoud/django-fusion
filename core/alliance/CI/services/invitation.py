from __future__ import annotations

import logging
import secrets
import string
from datetime import date
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()

class InvitationService:
    """
    Service for handling invitation operations.
    """
    
    @staticmethod
    def send_invitation(
        person_id: str, 
        inviter: User,
        invitation_type: str = 'join',
        message: str = ''
    ) -> dict[str, Any]:
        """
        Send an invitation to a person.
        Returns dict with invitation details and status.
        """
        try:
            from .models import Person
            person = Person.objects.get(id=person_id)
            
            # Check if person already has a user account
            if person.user:
                return {
                    'success': False,
                    'error': 'Person already has a user account',
                    'person_id': person_id,
                }
            
            # Generate invitation token
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            
            # Store invitation data
            invitation_key = f"invitation:{token}"
            invitation_data = {
                'person_id': person_id,
                'inviter_id': inviter.id,
                'invitation_type': invitation_type,
                'message': message,
                'created_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timezone.timedelta(days=7)).isoformat()
            }
            cache.set(invitation_key, invitation_data, 7 * 24 * 3600)  # 7 days
            
            # Send invitation email
            if person.email:
                context = {
                    'person': person,
                    'inviter': inviter,
                    'invitation_type': invitation_type,
                    'message': message,
                    'token': token,
                    'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                }
                
                # Email subject and content based on invitation type
                if invitation_type == 'join':
                    subject = f"Join our platform - Invitation from {inviter.get_full_name()}"
                    template = 'emails/invitation_join.html'
                elif invitation_type == 'connect':
                    subject = f"Connect with {inviter.get_full_name()}"
                    template = 'emails/invitation_connect.html'
                else:
                    subject = f"Invitation from {inviter.get_full_name()}"
                    template = 'emails/invitation_general.html'
                
                # Try to render template, fallback to plain text
                try:
                    html_message = render_to_string(template, context)
                    plain_message = f"""
                    Hello {person.first_name or person.full_name},
                    
                    {inviter.get_full_name()} has invited you to {invitation_type} on our platform.
                    
                    {message}
                    
                    To accept this invitation, click the link below:
                    {context['site_url']}/invitation/accept/{token}/
                    
                    This invitation will expire in 7 days.
                    """
                except:
                    plain_message = f"""
                    Invitation from {inviter.get_full_name()}
                    
                    To accept: {context['site_url']}/invitation/accept/{token}/
                    """
                    html_message = None
                
                # Send email
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                    recipient_list=[person.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Log the invitation
                logger.info(f"Invitation sent to {person.email} by {inviter.email}")
                
                return {
                    'success': True,
                    'person_id': person_id,
                    'inviter_id': inviter.id,
                    'invitation_type': invitation_type,
                    'token': token,
                    'email_sent': True,
                    'expires_at': invitation_data['expires_at'],
                }
            else:
                return {
                    'success': False,
                    'error': 'Person has no email address',
                    'person_id': person_id,
                }
                
        except Person.DoesNotExist:
            return {
                'success': False,
                'error': 'Person not found',
                'person_id': person_id,
            }
        except Exception as e:
            logger.error(f"Failed to send invitation: {e}")
            return {
                'success': False,
                'error': str(e),
                'person_id': person_id,
            }
    
    @staticmethod
    def accept_invitation(token: str) -> dict[str, Any]:
        """
        Accept an invitation using token.
        Returns dict with acceptance details.
        """
        invitation_key = f"invitation:{token}"
        invitation_data = cache.get(invitation_key)
        
        if not invitation_data:
            return {
                'success': False,
                'error': 'Invalid or expired invitation',
            }
        
        # Check expiration
        expires_at = timezone.datetime.fromisoformat(invitation_data['expires_at'])
        if timezone.now() > expires_at:
            cache.delete(invitation_key)
            return {
                'success': False,
                'error': 'Invitation has expired',
            }
        
        try:
            from .models import Person
            person = Person.objects.get(id=invitation_data['person_id'])
            
            # If person already has a user, return existing
            if person.user:
                cache.delete(invitation_key)
                return {
                    'success': True,
                    'existing_user': True,
                    'user_id': person.user.id,
                    'person_id': person.id,
                }
            
            # Create user account for person
            # Generate username from email
            username_base = person.email.split('@')[0]
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}_{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=person.email,
                password=None,  # Will need to set password via password reset
                first_name=person.first_name or '',
                last_name=person.last_name or '',
                is_active=True,
            )
            
            # Link person to user
            person.user = user
            person.save(update_fields=['user'])
            
            # Clean up invitation
            cache.delete(invitation_key)
            
            # Send welcome email with password reset link
            # (Implement password reset token generation and email here)
            
            return {
                'success': True,
                'user_created': True,
                'user_id': user.id,
                'person_id': person.id,
                'invitation_type': invitation_data['invitation_type'],
            }
            
        except Person.DoesNotExist:
            cache.delete(invitation_key)
            return {
                'success': False,
                'error': 'Person not found',
            }
        except Exception as e:
            logger.error(f"Failed to accept invitation: {e}")
            return {
                'success': False,
                'error': str(e),
            }
