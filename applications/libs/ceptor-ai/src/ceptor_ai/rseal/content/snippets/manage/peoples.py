# Import models
# Project-specific imports removed
# Project-specific imports removed - use dependency injection
# Project-specific imports removed
# Project-specific imports removed
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter, ChoiceFilter
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.snippets.views.snippets import SnippetViewSet

from ceptor_ai.content.models.locations.branch import Branch
from ceptor_ai.content.models.users.team import Team
from ceptor_ai.content.models.users.users import Person
from ceptor_ai.content.models.workspace import Workspace

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
    is_registered = BooleanFilter(
        field_name='is_registered',
        label=_('Is Registered'),
    )
    has_company = BooleanFilter(
        field_name='company',
        lookup_expr='isnull',
        exclude=True,
        label=_('Has Company Association')
    )

    class Meta:
        model = Person
        fields = {
            "profile_type": ["exact"],
            "status": ["exact"],
            "company": ["exact"],
            "is_registered": ["exact"],
        }


# =============================================================================
# PERSON VIEWSET — FULL TABBED INTERFACE
# =============================================================================

class PersonViewSet(SnippetViewSet):
    """
    Comprehensive admin interface for Person records.
    Displays all profile data in a 7-tab interface.
    Linked to Wagtail/Django User — auto-created on registration via signal.
    """
    model = Person
    menu_label = _("People")
    icon = "user"
    menu_order = 100
    list_display = (
        "full_name", "email", "profile_type", "status",
        "is_registered", "profile_completion", "company", "created_at"
    )
    list_filter = ("profile_type", "status", "is_registered", "gender")
    search_fields = ("first_name", "last_name", "email", "job_title", "company", "phone_number")
    filterset_class = PersonFilterSet
    list_export = (
        "full_name", "email", "phone_number", "profile_type",
        "company", "job_title", "status", "is_registered", "registration_date"
    )

    # ── TAB 1: Identity & User Account ──────────────────────────────────────
    identity_panels = [
        MultiFieldPanel(
            [
                HelpPanel(
                    content=_(
                        "<strong>🔗 Linked Wagtail/Django User</strong><br>"
                        "This profile is auto-created when a user registers. "
                        "User account details (username, is_staff, date_joined) "
                        "are managed in the Django auth admin. "
                        "Use <em>Status</em> and <em>Profile Type</em> to "
                        "control access and role."
                    ),
                    heading=_("ℹ️ About This Profile"),
                ),
                FieldPanel("user"),
            ],
            heading=_("Linked User Account"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("first_name"),
                    FieldPanel("last_name"),
                ]),
                FieldPanel("full_name"),
                FieldPanel("display_name"),
                FieldPanel("slug"),
                FieldRowPanel([
                    FieldPanel("profile_type"),
                    FieldPanel("status"),
                ]),
                FieldRowPanel([
                    FieldPanel("gender"),
                    FieldPanel("birth_date"),
                ]),
            ],
            heading=_("Personal Identity"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("is_registered"),
                    FieldPanel("registration_date"),
                ]),
                FieldRowPanel([
                    FieldPanel("is_email_verified"),
                    FieldPanel("email_verified_at"),
                ]),
                FieldRowPanel([
                    FieldPanel("is_phone_verified"),
                    FieldPanel("phone_verified_at"),
                ]),
                FieldPanel("profile_completion"),
            ],
            heading=_("Registration & Verification"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("profile_image"),
                FieldPanel("cover_image"),
            ],
            heading=_("Profile Media"),
        ),
    ]

    # ── TAB 2: Contact Information ───────────────────────────────────────────
    contact_panels = [
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("alternate_email"),
                FieldPanel("phone_number"),
                FieldPanel("alternate_phone"),
            ],
            heading=_("Contact Details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldRowPanel([
                    FieldPanel("city"),
                    FieldPanel("postal_code"),
                ]),
                FieldRowPanel([
                    FieldPanel("country"),
                    FieldPanel("location"),
                ]),
            ],
            heading=_("Address"),
        ),
    ]

    # ── TAB 3: Professional ──────────────────────────────────────────────────
    professional_panels = [
        MultiFieldPanel(
            [
                FieldPanel("job_title"),
                FieldPanel("position"),
                FieldRowPanel([
                    FieldPanel("company"),
                    FieldPanel("department"),
                ]),
                FieldPanel("industry"),
                FieldPanel("bio"),
            ],
            heading=_("Professional Details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("profile_content"),
            ],
            heading=_("Extended Content (Certifications, Projects, Social Links)"),
        ),
    ]

    # ── TAB 4: Social & Digital Presence ────────────────────────────────────
    social_panels = [
        MultiFieldPanel(
            [
                FieldPanel("website"),
                FieldPanel("linkedin_url"),
                FieldPanel("github_url"),
                FieldPanel("twitter_url"),
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
            ],
            heading=_("Social & Web Presence"),
        ),
    ]

    # ── TAB 5: Preferences & Notifications ──────────────────────────────────
    preferences_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("language"),
                    FieldPanel("timezone"),
                ]),
                FieldRowPanel([
                    FieldPanel("dark_mode"),
                    FieldPanel("high_contrast"),
                    FieldPanel("reduce_animations"),
                ]),
                FieldRowPanel([
                    FieldPanel("ui_density"),
                    FieldPanel("date_format"),
                    FieldPanel("time_format"),
                ]),
            ],
            heading=_("UI Preferences"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("email_notifications"),
                    FieldPanel("newsletter_notifications"),
                    FieldPanel("marketing_emails"),
                ]),
                FieldPanel("notification_frequency"),
                FieldRowPanel([
                    FieldPanel("course_updates_notifications"),
                    FieldPanel("instructor_messages_notifications"),
                ]),
                FieldRowPanel([
                    FieldPanel("weekly_reports_notifications"),
                    FieldPanel("assignment_notifications"),
                ]),
                FieldRowPanel([
                    FieldPanel("forum_activity_notifications"),
                    FieldPanel("deadline_reminders_notifications"),
                ]),
            ],
            heading=_("Notification Preferences"),
        ),
    ]

    # ── TAB 6: Privacy & Visibility ──────────────────────────────────────────
    privacy_panels = [
        MultiFieldPanel(
            [
                FieldPanel("public_profile"),
                FieldPanel("profile_visibility"),
                FieldRowPanel([
                    FieldPanel("show_email"),
                    FieldPanel("show_online_status"),
                    FieldPanel("allow_contact"),
                ]),
                FieldRowPanel([
                    FieldPanel("share_usage_data"),
                    FieldPanel("allow_search_indexing"),
                ]),
            ],
            heading=_("Privacy Settings"),
        ),
    ]

    # ── TAB 7: Billing & Subscription ────────────────────────────────────────
    billing_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("subscription_plan"),
                    FieldPanel("billing_cycle"),
                ]),
                FieldRowPanel([
                    FieldPanel("payment_method"),
                    FieldPanel("auto_renew"),
                ]),
                FieldPanel("billing_name"),
                FieldPanel("billing_address"),
                FieldRowPanel([
                    FieldPanel("tax_id"),
                    FieldPanel("send_invoices"),
                    FieldPanel("paperless_billing"),
                ]),
            ],
            heading=_("Billing & Subscription"),
        ),
    ]

    # ── TAB 8: Activity & Metadata ─────────────────────────────────────────
    activity_panels = [
        MultiFieldPanel(
            [
                FieldPanel("last_active"),
                FieldPanel("last_profile_update"),
                FieldPanel("login_count"),
                FieldPanel("metadata"),
            ],
            heading=_("Activity & Metadata"),
        ),
    ]

    # Assemble TabbedInterface
    edit_handler = TabbedInterface(
        [
            ObjectList(identity_panels, heading=_("Identity & Account")),
            ObjectList(contact_panels, heading=_("Contact")),
            ObjectList(professional_panels, heading=_("Professional")),
            ObjectList(social_panels, heading=_("Social & Web")),
            ObjectList(preferences_panels, heading=_("Preferences")),
            ObjectList(privacy_panels, heading=_("Privacy")),
            ObjectList(billing_panels, heading=_("Billing")),
            ObjectList(activity_panels, heading=_("Activity")),
        ]
    )




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


class CorporateFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Corporate model with company_size and industry filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Corporate Name')
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


class DepartmentFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Department model with function and company filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Department Name')
    )

    class Meta:
        model = Department
        fields = {
            "function": ["exact"],
            "company": ["exact"],
        }


class TeamFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Team model with department and status filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Team Name')
    )

    class Meta:
        model = Team
        fields = {
            "department": ["exact"],
            "status": ["exact"],
            "team_type": ["exact"],
        }


class ServiceFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Service model with category and active status filters.
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
            "is_active": ["exact"],
        }


class BranchFilterSet(RevisionFilterSetMixin, WagtailFilterSet):
    """
    Filtering for Branch model with location and corporate filters.
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Branch Name')
    )
    location = CharFilter(
        field_name='location',
        lookup_expr='icontains',
        label=_('Location contains')
    )

    class Meta:
        model = Branch
        fields = {
            "corporate": ["exact"],
            "is_headquarters": ["exact"],
        }


# =============================================================================
# VIEWSETS
# =============================================================================


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


class CorporateViewSet(SnippetViewSet):
    """
    Admin interface for managing Corporate entities.
    Handles company information, legal names, and corporate hierarchy.
    """
    model = Corporate
    menu_label = _("Corporates")
    icon = "suitcase"
    menu_order = 120
    list_display = ("name", "legal_name", "website", "company_size", "industry")
    list_filter = ("company_size", "industry")
    search_fields = ("name", "legal_name", "website", "industry")
    filterset_class = CorporateFilterSet
    list_export = ("name", "legal_name", "website", "company_size", "industry")


class DepartmentViewSet(SnippetViewSet):
    """
    Admin interface for managing Departments.
    Organizes corporate structure with department types and sizes.
    """
    model = Department
    menu_label = _("Departments")
    icon = "group"
    menu_order = 130
    list_display = ("name", "function", "company")
    list_filter = ("function", "company")
    max_search_results = 20
    search_fields = ("name", "company__name")
    filterset_class = DepartmentFilterSet
    list_export = ("name", "function", "company")


class TeamViewSet(SnippetViewSet):
    """
    Admin interface for managing Teams.
    Groups users by function, industry, or project.
    """
    model = Team
    menu_label = _("Teams")
    icon = "users"
    menu_order = 150
    list_display = ("name", "department", "team_type", "status")
    list_filter = ("department", "team_type", "status")
    search_fields = ("name", "department__name")
    filterset_class = TeamFilterSet
    list_export = ("name", "department", "team_type", "status")


class ServiceViewSet(SnippetViewSet):
    """
    Admin interface for managing Services.
    Defines services offered by teams with industry categorization.
    """
    model = Service
    menu_label = _("Services")
    icon = "cog"
    menu_order = 160
    list_display = ("name", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "category")
    filterset_class = ServiceFilterSet
    list_export = ("name", "category", "price", "is_active")


class BranchViewSet(SnippetViewSet):
    """
    Admin interface for managing Branches.
    Manages company locations with headquarters designation.
    """
    model = Branch
    menu_label = _("Branches")
    icon = "home"
    menu_order = 200
    list_display = ("name", "location", "corporate", "is_headquarters")
    list_filter = ("corporate", "is_headquarters")
    search_fields = ("name", "location", "corporate__name")
    filterset_class = BranchFilterSet
    list_export = ("name", "location", "corporate", "is_headquarters")
