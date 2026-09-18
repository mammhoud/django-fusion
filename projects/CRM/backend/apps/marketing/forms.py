"""Forms for real content-calendar interactions."""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.models import Workspace
from apps.core.tenancy import current_workspace_id

from .connector_adapters import MANUAL_CONNECT
from .models import Campaign, Post, SocialChannel


class PostComposerForm(forms.ModelForm):
    """Create a draft post tied to the caller's workspace and a scoped channel."""

    class Meta:
        model = Post
        fields = ["workspace", "campaign", "channel", "content", "scheduled_at"]
        widgets = {
            "workspace": forms.Select(),
            "campaign": forms.Select(),
            "channel": forms.Select(),
            "content": forms.Textarea(attrs={"rows": 5, "placeholder": "Write the post that should enter review."}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        workspace_id = current_workspace_id(request) if request is not None else None
        if workspace_id is not None:
            self.fields["workspace"].queryset = Workspace.objects.filter(pk=workspace_id)
            self.fields["workspace"].initial = workspace_id
            self.fields["campaign"].queryset = Campaign.objects.filter(workspace_id=workspace_id).order_by("-created_at")
            self.fields["channel"].queryset = SocialChannel.objects.filter(workspace_id=workspace_id).order_by("platform", "account_name")
        else:
            self.fields["campaign"].queryset = Campaign.objects.order_by("-created_at")
            self.fields["channel"].queryset = SocialChannel.objects.order_by("platform", "account_name")

    def clean(self):
        cleaned = super().clean()
        workspace = cleaned.get("workspace")
        campaign = cleaned.get("campaign")
        channel = cleaned.get("channel")
        if workspace:
            if campaign and campaign.workspace_id != workspace.pk:
                self.add_error("campaign", _("The campaign must belong to the selected workspace."))
            if channel and channel.workspace_id != workspace.pk:
                self.add_error("channel", _("The channel must belong to the selected workspace."))
        return cleaned

    def save(self, commit=True):
        post = super().save(commit=False)
        post.status = "draft"
        user = getattr(self.request, "user", None)
        if getattr(user, "is_authenticated", False):
            post.created_by = user
        if commit:
            post.save()
        return post


class PostLifecycleForm(forms.Form):
    """Explicit lifecycle action; no endpoint can silently skip approval."""

    ACTIONS = [
        ("submit", _("Submit for approval")),
        ("approve", _("Approve")),
        ("schedule", _("Schedule")),
        ("publish", _("Publish now")),
        ("reset", _("Return to draft")),
    ]

    action = forms.ChoiceField(choices=ACTIONS)


class ChannelConnectForm(forms.Form):
    """Store a catalog-platform credential without a redirect OAuth flow.

    The credential (token or webhook URL) lands on ``oauth_token``; the
    optional refresh token lands on ``oauth_refresh_token``. Nothing is ever
    rendered back to the browser.
    """

    platform = forms.ChoiceField(choices=[(p["platform"], p["label"]) for p in MANUAL_CONNECT])
    account_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "e.g. @handle, #channel, page name"}),
    )
    credential = forms.CharField(
        widget=forms.TextInput(
            attrs={"autocomplete": "off", "spellcheck": "false", "placeholder": "Access token or webhook URL"}
        )
    )
    refresh_token = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off", "spellcheck": "false", "placeholder": "Optional refresh token"}),
    )
