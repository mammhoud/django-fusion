from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import user_signed_up
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages
from django.urls import reverse

from .email import InvitationEmailHandler
from core.conf import app_settings


if TYPE_CHECKING:  # pragma: no cover
    from allauth.account.models import EmailAddress
    from allauth.socialaccount.models import SocialLogin
    from django.contrib.auth.models import AbstractBaseUser
    from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    """
    Enhanced account adapter with invitation system integration,
    email template support, and advanced registration controls.
    """
    
    # ------------------------------------------------------------------
    # REGISTRATION CONTROLS
    # ------------------------------------------------------------------
    
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """
        Determine if signup is open based on multiple factors:
        1. Session-based verified email (from invitations)
        2. Invitation-only mode
        3. Global registration settings
        4. Social authentication bypass
        """
        # Bypass for social authentication if configured
        if request.path.startswith('/accounts/social/'):
            if getattr(settings, 'SOCIALACCOUNT_ALLOW_REGISTRATION', True):
                return True
        
        # Check for session-based email verification (from invitations)
        if hasattr(request, "session") and request.session.get("account_verified_email"):
            return True
        
        # Check for valid invitation in session or GET parameters
        if self._has_valid_invitation(request):
            return True
        
        # Check invitation-only mode
        if app_settings.INVITATION_ONLY is True:
            return False
        
        # Fall back to global registration setting
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
    
    def _has_valid_invitation(self, request: HttpRequest) -> bool:
        """Check if request has a valid invitation."""
        from .utils import get_invitation_model
        
        InvitationModel = get_invitation_model()
        
        # Check session
        invitation_key = request.session.get('invitation_key')
        if invitation_key:
            try:
                invitation = InvitationModel.objects.get(
                    key=invitation_key,
                    accepted=False,
                    is_active=True
                )
                return not invitation.key_expired()
            except InvitationModel.DoesNotExist:
                return False
        
        # Check GET parameters
        invitation_key = request.GET.get('key')
        if invitation_key:
            try:
                invitation = InvitationModel.objects.get(
                    key=invitation_key,
                    accepted=False,
                    is_active=True
                )
                return not invitation.key_expired()
            except InvitationModel.DoesNotExist:
                return False
        
        return False
    
    # ------------------------------------------------------------------
    # USER SAVING & INVITATION PROCESSING
    # ------------------------------------------------------------------
    
    def save_user(self, request, user, form, commit=True):
        """
        Save the user and handle invitation acceptance.
        """
        user = super().save_user(request, user, form, commit)
        
        # Process invitation if exists
        self._process_invitation(request, user)
        
        # Set user properties based on invitation
        self._set_user_properties_from_invitation(request, user)
        
        return user
    
    def _process_invitation(self, request, user):
        """Process and accept invitation for the user."""
        from .signals import invitations
        from .utils import get_invitation_model
        
        InvitationModel = get_invitation_model()
        
        # Try to get invitation from various sources
        invitation = self._get_invitation_from_request(request)
        
        if invitation and invitation.accept(user):
            # Clear invitation from session
            if 'invitation_key' in request.session:
                del request.session['invitation_key']
            
            # Send acceptance signal
            invitations.invite_accepted.send(
                sender=InvitationModel,
                instance=invitation,
                accepted_by=user,
            )
            
            # Add success message
            messages.success(
                request,
                "Your invitation has been accepted! Welcome to the platform."
            )
    
    def _get_invitation_from_request(self, request) -> Optional:
        """Extract invitation from request."""
        from .utils import get_invitation_model
        
        InvitationModel = get_invitation_model()
        
        # Check sources in order
        sources = [
            request.session.get('invitation_key'),
            request.GET.get('key'),
            # Check if user email matches any pending invitation
            lambda: InvitationModel.objects.filter(
                email=request.POST.get('email'),
                accepted=False,
                is_active=True
            ).first() if request.method == 'POST' else None
        ]
        
        for source in sources:
            if callable(source):
                invitation = source()
            else:
                invitation_key = source
                if invitation_key:
                    try:
                        invitation = InvitationModel.objects.get(
                            key=invitation_key,
                            accepted=False,
                            is_active=True
                        )
                    except InvitationModel.DoesNotExist:
                        invitation = None
                else:
                    invitation = None
            
            if invitation and not invitation.key_expired():
                return invitation
        
        return None
    
    def _set_user_properties_from_invitation(self, request, user):
        """Set user properties based on invitation."""
        from .utils import get_invitation_model
        
        InvitationModel = get_invitation_model()
        
        # Check if user was invited
        try:
            invitation = InvitationModel.objects.get(
                email=user.email,
                accepted=True,
                accepted_by=user
            )
            
            # Set user properties from invitation
            if invitation.inviter:
                # Add inviter as a connection or set manager
                user.invited_by = invitation.inviter
                
                # Set user group based on invitation if configured
                if hasattr(settings, 'INVITATION_DEFAULT_GROUP'):
                    from django.contrib.auth.models import Group
                    group = Group.objects.get(name=settings.INVITATION_DEFAULT_GROUP)
                    user.groups.add(group)
            
            user.save(update_fields=['invited_by'] if hasattr(user, 'invited_by') else [])
            
        except InvitationModel.DoesNotExist:
            pass
    
    # ------------------------------------------------------------------
    # EMAIL HANDLING
    # ------------------------------------------------------------------
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send confirmation email with invitation context if applicable.
        """
        # Check if this is related to an invitation
        from .models import Invitation
        
        try:
            invitation = Invitation.objects.get(
                email=emailconfirmation.email_address.email,
                accepted=False,
                is_active=True
            )
            
            # Use invitation-specific email template
            ctx = self._get_invitation_email_context(request, emailconfirmation, invitation)
            
            # Determine email template
            if signup:
                email_template = getattr(
                    app_settings,
                    "INVITATION_SIGNUP_CONFIRMATION_TEMPLATE",
                    "account/email/email_confirmation_invitation_signup"
                )
            else:
                email_template = getattr(
                    app_settings,
                    "INVITATION_CONFIRMATION_TEMPLATE",
                    "account/email/email_confirmation_invitation"
                )
            
            # Send using email handler for better tracking
            email_handler = InvitationEmailHandler()
            success = email_handler.send_email(
                subject=ctx.get('subject', 'Confirm your email'),
                recipients=[emailconfirmation.email_address.email],
                html_content=self.render_mail(email_template, ctx),
                text_content=self.render_mail(email_template, ctx, text=True),
                priority='normal'
            )
            
            if not success:
                # Fallback to default method
                super().send_confirmation_mail(request, emailconfirmation, signup)
            
            return
        
        except Invitation.DoesNotExist:
            # Use default behavior for non-invitation emails
            super().send_confirmation_mail(request, emailconfirmation, signup)
    
    def _get_invitation_email_context(self, request, emailconfirmation, invitation):
        """Get context for invitation-related emails."""
        ctx = {
            "user": emailconfirmation.email_address.user,
            "key": emailconfirmation.key,
            "invitation": invitation,
            "invite_url": invitation.get_invite_url(request) if request else invitation.get_invite_url(),
            "inviter": invitation.inviter,
            "expiry_days": app_settings.INVITATION_EXPIRY,
            "site": getattr(request, 'site', None),
            "current_site": getattr(request, 'site', None),
            "protocol": 'https' if request.is_secure() else 'http',
        }
        
        # Add activation URL
        activate_url = reverse("account_confirm_email", args=[emailconfirmation.key])
        ctx["activate_url"] = request.build_absolute_uri(activate_url)
        
        return ctx
    
    def send_mail(self, template_prefix, email, context):
        """
        Override send_mail to use email handler system.
        """
        # Check if we should use the email handler
        use_email_handler = getattr(app_settings, 'USE_EMAIL_HANDLER_FOR_ALL', False)
        
        if use_email_handler:
            email_handler = InvitationEmailHandler()
            
            # Get subject from context or template
            subject = context.get('subject')
            if not subject:
                # Extract subject from template
                subject = self.render_mail(template_prefix, context, subject_only=True)
            
            # Send email
            success = email_handler.send_email(
                subject=subject,
                recipients=[email],
                html_content=self.render_mail(template_prefix, context),
                text_content=self.render_mail(template_prefix, context, text=True),
                priority='normal'
            )
            
            return success
        else:
            # Use default behavior
            return super().send_mail(template_prefix, email, context)
    
    # ------------------------------------------------------------------
    # REDIRECTS & URLS
    # ------------------------------------------------------------------
    
    def get_login_redirect_url(self, request):
        """
        Customize login redirect URL based on user status.
        """
        # Redirect invited users to welcome page
        if hasattr(request.user, 'accepted_invitations') and request.user.accepted_invitations.exists():
            return getattr(
                settings,
                'POST_INVITATION_REDIRECT_URL',
                reverse('welcome') if hasattr(self, 'reverse') else '/welcome/'
            )
        
        # Redirect new users to complete profile
        if request.user.date_joined > timezone.now() - timezone.timedelta(days=1):
            return getattr(
                settings,
                'NEW_USER_REDIRECT_URL',
                reverse('complete_profile') if hasattr(self, 'reverse') else '/profile/complete/'
            )
        
        return super().get_login_redirect_url(request)
    
    def get_signup_redirect_url(self, request):
        """
        Customize signup redirect URL.
        """
        # If user came from an invitation, redirect to post-signup page
        if request.session.get('invitation_key'):
            return getattr(
                settings,
                'INVITATION_SIGNUP_REDIRECT_URL',
                reverse('post_invitation_signup') if hasattr(self, 'reverse') else '/signup/invitation-complete/'
            )
        
        return super().get_signup_redirect_url(request)
    
    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------
    
    def clean_email(self, email):
        """
        Validate email against invitation rules.
        """
        cleaned_email = super().clean_email(email)
        
        # Check if email is on blacklist
        if cleaned_email in app_settings.EMAIL_BLACKLIST:
            from django.core.exceptions import ValidationError
            raise ValidationError("This email address is not allowed.")
        
        # Check whitelist if enabled
        if app_settings.EMAIL_WHITELIST and cleaned_email not in app_settings.EMAIL_WHITELIST:
            from django.core.exceptions import ValidationError
            raise ValidationError("This email address is not allowed.")
        
        return cleaned_email
    
    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------
    
    def get_user_signed_up_signal(self):
        """
        Return the user_signed_up signal for invitation tracking.
        """
        return user_signed_up
    
    def respond_user_signed_up(self, request, user):
        """
        Handle post-signup actions.
        """
        # Call parent method
        response = super().respond_user_signed_up(request, user)
        
        # Send welcome email for invited users
        if hasattr(user, 'accepted_invitations') and user.accepted_invitations.exists():
            self._send_welcome_email(request, user)
        
        return response
    
    def _send_welcome_email(self, request, user):
        """Send welcome email to newly invited users."""
        try:
            invitation = user.accepted_invitations.first()
            
            ctx = {
                'user': user,
                'invitation': invitation,
                'inviter': invitation.inviter,
                'site': getattr(request, 'site', None),
            }
            
            email_handler = InvitationEmailHandler()
            email_handler.send_email(
                subject=f"Welcome to {getattr(request.site, 'site_name', 'Our Platform')}!",
                recipients=[user.email],
                html_content=self.render_mail('account/email/welcome_invited', ctx),
                text_content=self.render_mail('account/email/welcome_invited', ctx, text=True),
                priority='background'
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")

