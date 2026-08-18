"""Forms for persisted Loop-CRM workflow interactions."""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import WorkflowDefinition
from .workflows import WORKFLOW_ACTION_CATALOG


class WorkflowDefinitionForm(forms.ModelForm):
    """Create or edit a workflow without allowing unsafe executable input."""

    actions = forms.JSONField(
        help_text=_('Use a JSON array, for example ["assign_owner", "notify_sales"].'),
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "spellcheck": "false",
                "placeholder": '["assign_owner", "notify_sales"]',
            }
        ),
    )

    class Meta:
        model = WorkflowDefinition
        fields = [
            "name",
            "slug",
            "description",
            "module",
            "trigger",
            "actions",
            "status",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "A clear workflow name"}),
            "slug": forms.TextInput(attrs={"placeholder": "workflow-slug"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "What should this automation accomplish?"}),
            "module": forms.Select(choices=[
                ("crm", _("CRM")),
                ("marketing", _("Marketing")),
                ("attribution", _("Attribution")),
                ("workspace", _("Workspace")),
            ]),
            "trigger": forms.TextInput(attrs={"placeholder": "deal.stage_changed:closed_won"}),
            "status": forms.Select(),
        }

    def clean_actions(self):
        actions = self.cleaned_data["actions"]
        if not isinstance(actions, list) or not all(isinstance(action, str) and action.strip() for action in actions):
            raise forms.ValidationError(_("Actions must be a JSON array of non-empty strings."))
        allowed = {item["id"] for item in WORKFLOW_ACTION_CATALOG}
        unknown = sorted({action.strip() for action in actions} - allowed)
        if unknown:
            raise forms.ValidationError(
                _("Unknown workflow action(s): %(actions)s.") % {"actions": ", ".join(unknown)}
            )
        return [action.strip() for action in actions]

    def clean_slug(self):
        return self.cleaned_data["slug"].strip().lower()
