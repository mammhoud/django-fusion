"""
Role group forms with dual-framework styling.
Includes Wagtail group forms with additional fields.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import GroupForm as WagtailGroupForm

from django.contrib.auth.models import Group
from django_osoul.core.forms import BaseStyledForm, LayoutMixin, SecurityMixin, ValidationMixin


class GroupRolesForm(BaseStyledForm, SecurityMixin, LayoutMixin, ValidationMixin, WagtailGroupForm):
    """
    Role Wagtail group form with dual-framework styling and additional fields.
    """

    roles = forms.ModelMultipleChoiceField(
        label=_("Active Directory Groups"),
        required=False,
        queryset=Group.objects.order_by("name"),
        help_text=_("Select Active Directory groups to associate with this Wagtail group."),
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "size": "5",
            }
        ),
    )

    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": _("Enter a description for this group")}
        ),
        help_text=_("Optional description of the group's purpose or permissions."),
    )

    is_active = forms.BooleanField(
        label=_("Active"),
        required=False,
        initial=True,
        help_text=_("Designates whether this group is active and can be assigned to users."),
    )

    def __init__(self, initial=None, instance=None, **kwargs):
        if instance is not None:
            if initial is None:
                initial = {}
            initial["roles"] = instance.roles.all()
            initial["description"] = getattr(instance, "description", "")
            initial["is_active"] = getattr(instance, "is_active", True)

        super().__init__(initial=initial, instance=instance, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["name", "description", "permissions", "roles", "is_active"],
            submit_text=_("Save Group"),
            show_links=False,
        )

        # Apply styling
        self.apply_field_styling(
            self.fields["name"], field_type="text", placeholder=_("Enter group name")
        )

        self.apply_field_styling(
            self.fields["description"], field_type="textarea", placeholder=_("Group description")
        )

        self.apply_field_styling(self.fields["permissions"], field_type="select", size="lg")

        self.apply_field_styling(self.fields["roles"], field_type="select", size="lg")

        self.apply_field_styling(self.fields["is_active"], field_type="checkbox")

    class Meta(WagtailGroupForm.Meta):
        fields = WagtailGroupForm.Meta.fields + ("description", "roles", "is_active")

    def clean_name(self):
        """Validate group name."""
        name = self.cleaned_data.get("name")
        if name:
            # Check for duplicate names (excluding current instance)
            qs = Group.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(_("A group with this name already exists."))

        return name

    def save(self, commit=True):
        """Save group with additional fields."""
        instance = super().save(commit=False)

        # Set additional fields
        instance.description = self.cleaned_data.get("description", "")
        instance.is_active = self.cleaned_data.get("is_active", True)

        if commit:
            instance.save()
            self.save_m2m()

        # Save AD groups
        instance.roles.set(self.cleaned_data["roles"])

        return instance


class SearchForm(BaseStyledForm, SecurityMixin, LayoutMixin, ValidationMixin, forms.Form):
    """
    Role group search form for admin interface.
    """

    name = forms.CharField(
        label=_("Group Name"),
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by group name..."),
            }
        ),
        help_text=_("Enter part of the group name to search."),
    )

    is_active = forms.ChoiceField(
        label=_("Status"),
        required=False,
        choices=[
            ("", _("All Status")),
            ("active", _("Active Only")),
            ("inactive", _("Inactive Only")),
        ],
        widget=forms.Select(),
        help_text=_("Filter by group activity status."),
    )

    sort_by = forms.ChoiceField(
        label=_("Sort By"),
        required=False,
        choices=[
            ("name", _("Name (A-Z)")),
            ("-name", _("Name (Z-A)")),
            ("created_at", _("Date Created (Oldest)")),
            ("-created_at", _("Date Created (Newest)")),
        ],
        initial="name",
        widget=forms.Select(),
        help_text=_("Select how to sort the results."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setup form layout
        self.setup_layout(
            fields=["name", "is_active", "sort_by"],
            submit_text=_("Search Groups"),
            show_links=False,
        )

        # Apply styling
        self.apply_field_styling(
            self.fields["name"], field_type="text", placeholder=_("Search groups...")
        )

        self.apply_field_styling(self.fields["is_active"], field_type="select")

        self.apply_field_styling(self.fields["sort_by"], field_type="select")

    def search(self, queryset):
        """Apply search filters to queryset."""
        data = self.cleaned_data

        # Filter by name
        if data.get("name"):
            queryset = queryset.filter(name__icontains=data["name"])

        # Filter by active status
        if data.get("is_active") == "active":
            queryset = queryset.filter(is_active=True)
        elif data.get("is_active") == "inactive":
            queryset = queryset.filter(is_active=False)

        # Apply sorting
        if data.get("sort_by"):
            queryset = queryset.order_by(data["sort_by"])

        return queryset
