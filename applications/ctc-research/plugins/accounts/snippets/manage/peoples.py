from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter, ChoiceFilter, DateFilter
from crafts_ai.handlers.models.manage_company import Organization as Corporate
from crafts_ai.models.users.team import Team
from crafts_ai.models import Person
from crafts_ai.models.workspace import Workspace
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.snippets.views.snippets import SnippetViewSet

from plugins.accounts.filters.revision import RevisionFilterSetMixin
from plugins.accounts.models import Service

# from crafts_ai.workflows.pipelines.models.locations.branch import Branch

# =============================================================================
# FILTERSET CLASSES
# =============================================================================

class PersonFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Advanced filtering for Person model with search and status filters.
    """
    name = CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        label=_('Name contains')
    )
    profile_type = ChoiceFilter(
        field_name='profile_type',
        choices=Person.ProfileType.choices,
        label=_('Profile Type')
    )
    has_company = BooleanFilter(
        field_name='company',
        lookup_expr='isnull',
        exclude=True,
        label=_('Has company Association')
    )

    class Meta:
        model = Person
        fields = {
            "profile_type": ["exact"],
            "company": ["exact"],
        }


class PersonViewSet(SnippetViewSet):
    """
    Admin interface for managing Person records.
    Supports different person types: Customers, Suppliers, Employees, etc.
    """
    model = Person
    menu_label = _("Employees")
    icon = "user"
    menu_order = 100
    list_display = ("full_name", "profile_type", "company", "job_title")
    list_filter = ("profile_type", "company")
    search_fields = ("first_name", "last_name", "email", "job_title", "company")
    filterset_class = PersonFilterSet

    # Export fields for data export functionality
    list_export = ("full_name", "email", "phone_number", "profile_type", "company", "job_title")

    # Custom panels for the edit view
    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("email"),
        FieldPanel("phone_number"),
        FieldPanel("profile_type"),
        FieldPanel("company"),
        # FieldPanel("is_primary"),
        FieldPanel("job_title"),
        FieldPanel("address"),
        # FieldPanel("notes"),
    ]


class WorkspaceFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Workspace model with module and company filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Workspace Name')
    )
    module = CharFilter(
        field_name='module',
        lookup_expr='icontains',
        label=_('Module contains')
    )

    class Meta:
        model = Workspace
        fields = {
            "company": ["exact"],
            "module": ["exact"],
        }


class CompanyFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Company model with size and industry filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Company Name')
    )
    legal_name = CharFilter(
        field_name='legal_name',
        lookup_expr='icontains',
        label=_('Legal Name contains')
    )

    class Meta:
        model = Corporate
        fields = {
            "company_size": ["exact"],
            "industry": ["exact"],
        }


# class DepartmentFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Filtering for Department model with type and company filters.
#     """
#     name = CharFilter(
#         field_name='name',
#         lookup_expr='icontains',
#         label=_('Department Name')
#     )
#
#     class Meta:
#         model = Department
#         fields = {
#             "type": ["exact"],
#             "company": ["exact"],
#             "size": ["exact"],
#         }


# class ContactFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Advanced filtering for Contact model with company and date filters.
#     """
#     name = CharFilter(
#         field_name='name',
#         lookup_expr='icontains',
#         label=_('Contact Name')
#     )
#     company = CharFilter(
#         field_name='company',
#         lookup_expr='icontains',
#         label=_('Company contains')
#     )
#     created_after = DateFilter(
#         field_name='date_created',
#         lookup_expr='date__gte',
#         # widget=DateRangePickerWidget,
#         label=_('Created after')
#     )
#
#     class Meta:
#         model = Contact
#         fields = {
#             "company": ["exact"],
#             "job_title": ["icontains"],
#         }


class TeamFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Team model with industry and company filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Team Name')
    )

    class Meta:
        model = Team
        fields = {
            "team_type": ["exact"],
            "status": ["exact"],
            "department": ["exact"],
        }


class ServiceFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Service model with team and industry filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Service Name')
    )

    class Meta:
        model = Service
        fields = {
            "category": ["exact"],
            "is_visible": ["exact"],
        }


# class InvitationFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Filtering for Invitation model with status and date filters.
#     """
#     email = CharFilter(
#         field_name='email',
#         lookup_expr='icontains',
#         label=_('Email contains')
#     )
#     is_accepted = BooleanFilter(
#         field_name='accepted',
#         label=_('Is Accepted')
#     )
#
#     class Meta:
#         model = Invitation
#         fields = {
#             "accepted": ["exact"],
#             "created": ["date"],
#         }


# class ContactEmailFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Filtering for ContactEmail model with email and contact filters.
#     """
#     email = CharFilter(
#         field_name='email__email',
#         lookup_expr='icontains',
#         label=_('Email address contains')
#     )
#
#     class Meta:
#         model = ContactEmail
#         fields = {
#             "is_primary": ["exact"],
#             "contact": ["exact"],
#         }
#
#
# class ContactPhoneFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Filtering for ContactPhone model with phone type and contact filters.
#     """
#     phone_number = CharFilter(
#         field_name='phone_number',
#         lookup_expr='icontains',
#         label=_('Phone number contains')
#     )
#
#     class Meta:
#         model = ContactPhone
#         fields = {
#             "phone_type": ["exact"],
#             "is_primary": ["exact"],
#             "contact": ["exact"],
#         }


# class BranchFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Filtering for Branch model with location and company filters.
#     """
#     name = CharFilter(
#         field_name='name',
#         lookup_expr='icontains',
#         label=_('Branch Name')
#     )
#     location = CharFilter(
#         field_name='location',
#         lookup_expr='icontains',
#         label=_('Location contains')
#     )
#
#     class Meta:
#         model = Branch
#         fields = {
#             "company": ["exact"],
#             "is_headquarters": ["exact"],
#         }
#
#
# class FooterTextFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
#     """
#     Simple filtering for FooterText model.
#     """
#     class Meta:
#         model = FooterText
#         fields = {
#             "live": ["exact"],
#         }





class WorkspaceViewSet(SnippetViewSet):
    """
    Admin interface for managing Workspaces.
    Workspaces organize content and users by module and company.
    """
    model = Workspace
    menu_label = _("Workspaces")
    icon = "folder"
    menu_order = 110
    list_display = ("name", "module", "company", "created_at")
    list_filter = ("module", "company")
    search_fields = ("name", "module", "company__name")
    filterset_class = WorkspaceFilterSet
    list_export = ("name", "module", "company", "created_at")


class CompanyViewSet(SnippetViewSet):
    """
    Admin interface for managing Companies.
    Handles company information, legal names, and corporate hierarchy.
    """
    model = Corporate
    menu_label = _("Companies")
    icon = "suitcase"
    menu_order = 120
    list_display = ("name", "legal_name", "website", "company_size", "industry")
    list_filter = ("company_size", "industry")
    search_fields = ("name", "legal_name", "website", "industry")
    filterset_class = CompanyFilterSet
    list_export = ("name", "legal_name", "website", "company_size", "industry")


# class DepartmentViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Departments.
#     Organizes corporate structure with department types and sizes.
#     """
#     model = Department
#     menu_label = _("Departments")
#     icon = "group"
#     menu_order = 130
#     list_display = ("name", "size", "type", "company")
#     list_filter = ("type", "size", "company")
#     search_fields = ("name", "company__name")
#     filterset_class = DepartmentFilterSet
#     list_export = ("name", "size", "type", "company")


# class ContactViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Contacts.
#     Centralized contact management with company associations.
#     """
#     model = Contact
#     menu_label = _("Contacts")
#     icon = "user"
#     menu_order = 140
#     list_display = ("name", "company", "job_title", "date_created")
#     list_filter = ("company",)
#     search_fields = ("name", "company", "job_title", "email")
#     filterset_class = ContactFilterSet
#     list_export = ("name", "company", "job_title", "email", "date_created")
class TeamViewSet(SnippetViewSet):
    """
    Admin interface for managing Teams.
    Groups users by function, industry, or project.
    """
    model = Team
    menu_label = _("Teams")
    icon = "users"
    menu_order = 150
    list_display = ("name", "department", "team_type", "status", "leader")
    list_filter = ("team_type", "status", "department")
    search_fields = ("name", "short_name", "purpose")
    filterset_class = TeamFilterSet
    list_export = ("name", "department", "team_type", "status", "leader")
class ServiceViewSet(SnippetViewSet):
    """
    Admin interface for managing Services.
    Defines services offered by teams with industry categorization.
    """
    model = Service
    menu_label = _("Services")
    icon = "cog"
    menu_order = 160
    list_display = ("name", "category", "is_visible")
    list_filter = ("category", "is_visible")
    search_fields = ("name", "overview", "description")
    filterset_class = ServiceFilterSet
    list_export = ("name", "category", "is_visible")
#
#
# class InvitationViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Invitations.
#     Tracks user invitations with acceptance status.
#     """
#     model = Invitation
#     menu_label = _("Invitations")
#     icon = "mail"
#     menu_order = 170
#     list_display = ("email", "created", "accepted", "accepted_date")
#     list_filter = ("accepted", "created")
#     search_fields = ("email",)
#     filterset_class = InvitationFilterSet
#     list_export = ("email", "created", "accepted", "accepted_date")
#
#
# class ContactEmailViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Contact Email addresses.
#     Handles multiple email addresses per contact with primary designations.
#     """
#     model = ContactEmail
#     menu_label = _("Contact Emails")
#     icon = "mail"
#     menu_order = 180
#     list_display = ("contact", "email", "is_primary", "email_type")
#     list_filter = ("is_primary", "email_type")
#     search_fields = ("contact__name", "email")
#     filterset_class = ContactEmailFilterSet
#     list_export = ("contact", "email", "is_primary", "email_type")
#
#
# class ContactPhoneViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Contact Phone numbers.
#     Supports multiple phone types (mobile, work, home) per contact.
#     """
#     model = ContactPhone
#     menu_label = _("Contact Phones")
#     icon = "mobile-alt"
#     menu_order = 190
#     list_display = ("contact", "phone_number", "phone_type", "is_primary")
#     list_filter = ("phone_type", "is_primary")
#     search_fields = ("contact__name", "phone_number")
#     filterset_class = ContactPhoneFilterSet
#     list_export = ("contact", "phone_number", "phone_type", "is_primary")
#
#
# # class BranchViewSet(SnippetViewSet):
# #     """
# #     Admin interface for managing Branches.
# #     Manages company locations with headquarters designation.
# #     """
# #     model = Branch
# #     menu_label = _("Branches")
# #     icon = "home"
# #     menu_order = 200
# #     list_display = ("name", "location", "company", "is_headquarters")
# #     list_filter = ("company", "is_headquarters")
# #     search_fields = ("name", "location", "company__name")
# #     filterset_class = BranchFilterSet
# #     list_export = ("name", "location", "company", "is_headquarters")
#
#
# class FooterTextViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Footer Text content.
#     Editable footer text with publishing workflow.
#     """
#     model = FooterText
#     menu_label = _("Footer Text")
#     icon = "doc-full"
#     menu_order = 210
#     search_fields = ("body",)
#     filterset_class = FooterTextFilterSet
#     list_display = ("__str__", "live")
#     panels = [
#         FieldPanel("body"),
#     ]

