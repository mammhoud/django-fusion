from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.handlers.models import Team, TeamMembership

from ..base import BaseSnippetViewSet


# =============================================================================
# TEAM ADMIN SNIPPET VIEWSET
# =============================================================================
class TeamViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Teams within departments.
    Provides powerful filtering, search, and bulk management actions.
    """

    model = Team
    menu_label = _("Teams")
    icon = "group"
    menu_order = 160
    search_fields = [
        "name",
        "slug",
        "short_name",
        "department__name",
        "leader__first_name",
        "leader__last_name",
    ]
    ordering = ["department", "name"]

    # -------------------------------------------------------------------------
    # List Configuration
    # -------------------------------------------------------------------------
    list_display = [
        "name",
        "department",
        "leader_display",
        "team_type_display",
        "status_display",
        "member_count_display",
        "active_since_display",
    ]
    list_filter = [
        "department",
        "team_type",
        "status",
        "is_active",
        "requires_approval",
    ]
    list_export = [
        "name",
        "department",
        "leader",
        "team_type",
        "status",
        "member_count",
        "purpose",
        "objectives",
    ]

    # -------------------------------------------------------------------------
    # Display Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def leader_display(obj):
        """Display leader name with emoji."""
        if obj.leader:
            return format_html("👤 <strong>{}</strong>", obj.leader)
        return format_html("<span style='color:#999;'>—</span>")
    leader_display.short_description = _("Leader")

    @staticmethod
    def team_type_display(obj):
        """Show team type."""
        color = "#4CAF50" if obj.team_type == "departmental" else "#007BFF"
        return format_html(
            "<span style='color:{}; font-weight:600;'>{}</span>",
            color,
            obj.get_team_type_display(),
        )
    team_type_display.short_description = _("Type")

    @staticmethod
    def status_display(obj):
        """Show status with colored badge."""
        colors = {
            "active": "#22C55E",
            "planning": "#EAB308",
            "on_hold": "#F97316",
            "completed": "#3B82F6",
            "archived": "#6B7280",
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            "<span style='color:{}; font-weight:600;'>{}</span>",
            color,
            obj.get_status_display(),
        )
    status_display.short_description = _("Status")

    @staticmethod
    def member_count_display(obj):
        """Display member count."""
        count = obj.member_count or obj.memberships.count()
        return format_html("<strong>{}</strong>", count)
    member_count_display.short_description = _("Members")

    @staticmethod
    def active_since_display(obj):
        """Display formatted activation date."""
        return obj.active_since.strftime("%Y-%m-%d") if obj.active_since else "—"
    active_since_display.short_description = _("Active Since")

    # -------------------------------------------------------------------------
    # Custom Bulk Actions
    # -------------------------------------------------------------------------
    list_actions = ["activate_teams", "deactivate_teams", "refresh_member_counts"]

    def activate_teams(self, request, queryset):
        """Activate selected teams."""
        updated = queryset.update(is_active=True, status=Team.TeamStatus.ACTIVE)
        messages.success(request, f"✅ Activated {updated} team(s).")
    activate_teams.label = _("Activate Selected Teams")
    activate_teams.icon = "tick"

    def deactivate_teams(self, request, queryset):
        """Deactivate selected teams."""
        updated = queryset.update(is_active=False, status=Team.TeamStatus.ON_HOLD)
        messages.warning(request, f"🚫 Deactivated {updated} team(s).")
    deactivate_teams.label = _("Deactivate Selected Teams")
    deactivate_teams.icon = "cross"

    def refresh_member_counts(self, request, queryset):
        """Recalculate and update member counts for selected teams."""
        total = 0
        for team in queryset:
            team.member_count = team.active_member_count
            team.save(update_fields=["member_count"])
            total += 1
        messages.info(request, f"🔄 Refreshed member counts for {total} team(s).")
    refresh_member_counts.label = _("Recalculate Member Counts")
    refresh_member_counts.icon = "refresh"


# =============================================================================
# TEAM MEMBERSHIP ADMIN SNIPPET VIEWSET
# =============================================================================
class TeamMembershipViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Team Memberships.
    Provides search, filtering, and role-based actions.
    """

    model = TeamMembership
    menu_label = _("Team Memberships")
    icon = "user"
    menu_order = 161
    search_fields = [
        "person__first_name",
        "person__last_name",
        "team__name",
        "role",
    ]
    ordering = ["team", "person"]

    # -------------------------------------------------------------------------
    # List Configuration
    # -------------------------------------------------------------------------
    list_display = [
        "person_display",
        "team_display",
        "role_display",
        "status_display",
        "is_primary_display",
        "allocation_display",
        "date_joined",
        "date_left",
    ]
    list_filter = [
        "team",
        "role",
        "status",
        "is_primary_team",
    ]
    list_export = [
        "person",
        "team",
        "role",
        "status",
        "date_joined",
        "date_left",
        "is_primary_team",
        "allocation_percentage",
    ]

    # -------------------------------------------------------------------------
    # Display Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def person_display(obj):
        return format_html("<strong>{}</strong>", obj.person)
    person_display.short_description = _("Member")

    @staticmethod
    def team_display(obj):
        return format_html("🏷️ {}", obj.team)
    team_display.short_description = _("Team")

    @staticmethod
    def role_display(obj):
        return format_html("<span style='color:#2563EB;'>{}</span>", obj.get_role_display())
    role_display.short_description = _("Role")

    @staticmethod
    def status_display(obj):
        colors = {
            "active": "#16A34A",
            "pending": "#FACC15",
            "inactive": "#DC2626",
            "on_leave": "#F97316",
            "alumni": "#6B7280",
        }
        color = colors.get(obj.status, "#999")
        return format_html("<strong style='color:{};'>{}</strong>", color, obj.get_status_display())
    status_display.short_description = _("Status")

    @staticmethod
    def is_primary_display(obj):
        icon = "✅" if obj.is_primary_team else "—"
        return format_html("<center>{}</center>", icon)
    is_primary_display.short_description = _("Primary")

    @staticmethod
    def allocation_display(obj):
        return f"{obj.allocation_percentage}%"
    allocation_display.short_description = _("Allocation")

    # -------------------------------------------------------------------------
    # Bulk Actions
    # -------------------------------------------------------------------------
    list_actions = ["activate_members", "deactivate_members", "mark_primary"]

    def activate_members(self, request, queryset):
        """Activate selected team memberships."""
        updated = queryset.update(status=TeamMembership.MembershipStatus.ACTIVE)
        messages.success(request, f"✅ Activated {updated} team membership(s).")
    activate_members.label = _("Activate Memberships")
    activate_members.icon = "tick"

    def deactivate_members(self, request, queryset):
        """Deactivate selected team memberships."""
        updated = queryset.update(status=TeamMembership.MembershipStatus.INACTIVE)
        messages.warning(request, f"🚫 Deactivated {updated} team membership(s).")
    deactivate_members.label = _("Deactivate Memberships")
    deactivate_members.icon = "cross"

    def mark_primary(self, request, queryset):
        """Mark selected memberships as primary (per person)."""
        count = 0
        for membership in queryset:
            TeamMembership.objects.filter(person=membership.person).update(is_primary_team=False)
            membership.is_primary_team = True
            membership.save()
            count += 1
        messages.info(request, f"⭐ Set {count} membership(s) as primary.")
    mark_primary.label = _("Mark as Primary")
    mark_primary.icon = "star"
