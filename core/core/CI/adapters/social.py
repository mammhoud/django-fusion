
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

from core.conf import app_settings

# ------------------------------------------------------------------
# SOCIAL ACCOUNT ADAPTER
# ------------------------------------------------------------------

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Social account adapter with invitation system integration.
    """
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Allow social signup based on invitation and global settings.
        """
        # Check invitation-only mode
        if app_settings.INVITATION_ONLY is True:
            # Check if social login email matches an invitation
            email = sociallogin.user.email
            if email:
                from .utils import get_invitation_model
                InvitationModel = get_invitation_model()
                
                try:
                    invitation = InvitationModel.objects.get(
                        email=email,
                        accepted=False,
                        is_active=True
                    )
                    return not invitation.key_expired()
                except InvitationModel.DoesNotExist:
                    return False
        
        # Fall back to social account settings
        return getattr(settings, "SOCIALACCOUNT_ALLOW_REGISTRATION", True)
    
    def pre_social_login(self, request, sociallogin):
        """
        Process invitations before social login.
        """
        super().pre_social_login(request, sociallogin)
        
        # Check if social login email matches an invitation
        email = sociallogin.user.email
        if email:
            from .signals import invitations
            from .utils import get_invitation_model
            
            InvitationModel = get_invitation_model()
            
            try:
                invitation = InvitationModel.objects.get(
                    email=email,
                    accepted=False,
                    is_active=True
                )
                
                # Store invitation in session for processing after login
                request.session['invitation_key'] = invitation.key
                
            except InvitationModel.DoesNotExist:
                pass

