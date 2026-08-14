"""Forms for real content-calendar interactions."""
from __future__ import annotations

from django import forms

from .models import Post


class PostComposerForm(forms.ModelForm):
    """Create a draft post tied to a real workspace and channel."""

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

    def save(self, commit=True):
        post = super().save(commit=False)
        post.status = "draft"
        if commit:
            post.save()
        return post


class PostLifecycleForm(forms.Form):
    """Explicit lifecycle action; no endpoint can silently skip approval."""

    ACTIONS = [
        ("submit", "Submit for approval"),
        ("approve", "Approve"),
        ("schedule", "Schedule"),
        ("publish", "Publish now"),
        ("reset", "Return to draft"),
    ]

    action = forms.ChoiceField(choices=ACTIONS)
