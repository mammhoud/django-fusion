from django import forms
from django.utils.translation import gettext_lazy as _

from apps.learning.models import CourseEnrollmentLead


class CourseEnrollmentLeadForm(forms.ModelForm):
    """Capture an enrollment prospect for a course (Precis-style lead)."""

    full_name = forms.CharField(
        max_length=255,
        label=_("Full name"),
        widget=forms.TextInput(attrs={"placeholder": _("Your name"), "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"placeholder": _("you@example.com"), "autocomplete": "email"}
        ),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label=_("Phone (optional)"),
        widget=forms.TextInput(attrs={"placeholder": _("+20 …"), "autocomplete": "tel"}),
    )

    class Meta:
        model = CourseEnrollmentLead
        fields = ["full_name", "email", "phone"]
