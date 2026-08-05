"""POS Cloud — Django-Fusion modal fragments.

Modal components for creating, editing, and viewing entities.

Usage:
    {% comp "core.modals.lead_modal" lead=lead / %}
    {% comp "core.modals.branch_modal" branch=branch organizations=orgs / %}
    {% comp "core.modals.report_modal" report=report branch=branch / %}
"""

from django_fusion.routes.components.fragments import FragmentComponent


class LeadModal(FragmentComponent):
    """Create / edit lead modal with form fields."""

    fragment_name = "core.modals.lead_modal"

    def get_context(self, **kwargs):
        lead = kwargs.get("lead")
        organizations = kwargs.get("organizations", [])
        branches = kwargs.get("branches", [])
        users = kwargs.get("users", [])
        return {
            "lead": lead,
            "is_edit": lead is not None,
            "organizations": organizations,
            "branches": branches,
            "users": users,
            "status_choices": [
                ("new", "New"), ("contacted", "Contacted"), ("qualified", "Qualified"),
                ("proposal", "Proposal Sent"), ("negotiation", "Negotiation"),
                ("won", "Won"), ("lost", "Lost"), ("archived", "Archived"),
            ],
            "source_choices": [
                ("website", "Website"), ("referral", "Referral"),
                ("social_media", "Social Media"), ("email_campaign", "Email Campaign"),
                ("phone", "Phone"), ("event", "Event"), ("other", "Other"),
            ],
        }


class BranchModal(FragmentComponent):
    """Create / edit branch modal with organization selector."""

    fragment_name = "core.modals.branch_modal"

    def get_context(self, **kwargs):
        branch = kwargs.get("branch")
        organizations = kwargs.get("organizations", [])
        return {
            "branch": branch,
            "is_edit": branch is not None,
            "organizations": organizations,
            "pos_types": [
                ("formint-pos", "Formint POS"), ("pos-solo", "POS Solo"), ("pos-full", "POS Full"), ("pos-mini", "POS Mini"),
            ],
        }


class ReportViewModal(FragmentComponent):
    """View inventory/branch report details modal."""

    fragment_name = "core.modals.report_view_modal"

    def get_context(self, **kwargs):
        report = kwargs.get("report")
        report_type = kwargs.get("report_type", "inventory")
        return {
            "report": report,
            "report_type": report_type,
        }
