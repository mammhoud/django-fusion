import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.conf import app_settings

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# BASE INVITATION MANAGER WITH ENHANCED FUNCTIONALITY
# ------------------------------------------------------------------
class BaseInvitationManager(models.Manager):
    """
    Enhanced manager for invitation models with query methods,
    bulk operations, and template integration.
    """

    def all_expired(self):
        """Get all expired invitations."""
        return self.filter(self.expired_q())

    def all_valid(self):
        """Get all valid (non-expired) invitations."""
        return self.exclude(self.expired_q())

    def expired_q(self):
        """Create Q object for expired invitations."""
        sent_threshold = timezone.now() - timedelta(
            days=app_settings.INVITATION_EXPIRY
        )
        q = Q(accepted=True) | Q(sent__lt=sent_threshold)
        return q

    def delete_expired_confirmations(self):
        """Delete all expired invitations."""
        return self.all_expired().delete()

    def pending(self):
        """Get all pending (not accepted and not expired) invitations."""
        return self.filter(accepted=False, sent__gte=timezone.now() - timedelta(
            days=app_settings.INVITATION_EXPIRY
        ))

    def accepted(self):
        """Get all accepted invitations."""
        return self.filter(accepted=True)

    def by_inviter(self, inviter):
        """Get all invitations sent by a specific inviter."""
        return self.filter(inviter=inviter)

    def by_email(self, email):
        """Get all invitations for a specific email."""
        return self.filter(email=email)

    def resend_expiring(self, days_before=1):
        """
        Resend invitations that will expire soon.
        Returns list of resent invitations.
        """
        expiring_threshold = timezone.now() + timedelta(days=days_before)
        expiring_q = Q(
            accepted=False,
            expires_at__lte=expiring_threshold,
            expires_at__gt=timezone.now()
        )
        
        expiring_invitations = self.filter(expiring_q)
        resent = []
        
        for invitation in expiring_invitations:
            try:
                # Check if we can resend (not too frequent)
                if invitation.can_resend():
                    invitation.resend_invitation()
                    resent.append(invitation)
            except Exception as e:
                logger.error(f"Failed to resend invitation {invitation.pk}: {str(e)}")
        
        return resent

    def bulk_create_invitations(self, emails, inviter=None, **kwargs):
        """
        Create multiple invitations in bulk.
        Returns list of created invitations.
        """
        invitations = []
        for email in emails:
            # Check if invitation already exists for this email
            existing = self.filter(
                email=email,
                accepted=False,
                is_active=True
            ).exists()
            
            if not existing:
                invitation = self.model.create(
                    email=email,
                    inviter=inviter,
                    **kwargs
                )
                invitations.append(invitation)
        
        return invitations

    def get_or_create_invitation(self, email, inviter=None, **kwargs):
        """
        Get existing valid invitation or create a new one.
        """
        # Look for existing valid invitation
        valid_invitation = self.filter(
            email=email,
            accepted=False,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        
        if valid_invitation:
            return valid_invitation, False
        
        # Create new invitation
        invitation = self.model.create(
            email=email,
            inviter=inviter,
            **kwargs
        )
        return invitation, True

    def send_bulk_invitations(self, invitation_ids, request=None):
        """
        Send invitations in bulk.
        Returns success count and failures.
        """
        invitations = self.filter(id__in=invitation_ids, accepted=False, is_active=True)
        success = 0
        failures = []
        
        for invitation in invitations:
            try:
                if invitation.send_invitation(request):
                    success += 1
                else:
                    failures.append(invitation.id)
            except Exception as e:
                logger.error(f"Failed to send invitation {invitation.id}: {str(e)}")
                failures.append(invitation.id)
        
        return success, failures

    def statistics(self):
        """
        Get invitation statistics.
        Returns dict with counts and metrics.
        """
        total = self.count()
        accepted = self.accepted().count()
        pending = self.pending().count()
        expired = self.all_expired().count()
        
        # Calculate acceptance rate
        acceptance_rate = (accepted / total * 100) if total > 0 else 0
        
        # Get recent activity
        recent_days = 30
        recent_threshold = timezone.now() - timedelta(days=recent_days)
        recent_sent = self.filter(sent__gte=recent_threshold).count()
        recent_accepted = self.filter(accepted_at__gte=recent_threshold).count()
        
        return {
            'total': total,
            'accepted': accepted,
            'pending': pending,
            'expired': expired,
            'acceptance_rate': round(acceptance_rate, 2),
            'recent_sent': recent_sent,
            'recent_accepted': recent_accepted,
        }

    def cleanup_old(self, days_old=90):
        """
        Clean up old invitations (soft delete).
        Returns count of cleaned invitations.
        """
        old_threshold = timezone.now() - timedelta(days=days_old)
        old_invitations = self.filter(
            Q(created__lt=old_threshold) & Q(accepted=True) | Q(is_active=False)
        )
        
        count = old_invitations.count()
        old_invitations.delete()  # Hard delete for old records
        
        return count

