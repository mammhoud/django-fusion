# from django.utils.translation import gettext_lazy as _

# from apps.handlers.models import Company  # Uses your detailed model

# from ..base import BaseSnippetViewSet


# class CompanyViewSet(BaseSnippetViewSet):
#     """Admin interface for managing Company snippets."""

#     model = Company
#     menu_label = _("Companies")
#     icon = "suitcase"
#     menu_order = 130
#     search_fields = ["name", "legal_name", "industry"]
#     ordering = ["name"]

#     # Columns shown in the list view
#     list_display = ["name", "industry", "company_type", "website", "is_active", "is_verified"]
#     list_export = [
#         "name",
#         "company_type",
#         "industry",
#         "company_size",
#         "website",
#         "email",
#         "phone",
#         "country",
#         "is_displayed",
#         "is_partner",
#         "is_educational",
#         "is_active",
#         "is_verified",
#         "tax_id",
#     ]
#     csv_filename = "companies.csv"

#     # ------------------------------------------------------------------
#     # CUSTOM DISPLAY METHODS
#     # ------------------------------------------------------------------
#     @staticmethod
#     def type_display(obj):
#         """Show the company type in readable form."""
#         return obj.get_company_type_display()

#     type_display.short_description = _("Type")

#     @staticmethod
#     def website(obj):
#         """Clickable company website link."""
#         if obj.website:
#             return BaseSnippetViewSet.link_display(obj.website)
#         return "—"

#     website.short_description = _("Website")

#     # ------------------------------------------------------------------
#     # CUSTOM FILTERS / FEATURES (OPTIONAL EXTENSIONS)
#     # ------------------------------------------------------------------
#     list_filter = ["company_type", "industry", "is_active", "is_verified", "is_displayed"]

#     # def get_queryset(self, request):
#     #     """Optimized queryset with prefetches for faster admin loading."""
#     #     qs = super().get_queryset(request)
#     #     return qs.select_related("parent_company", "relationship_manager").prefetch_related("tags")


# # ------------------------------------------------------------------
# # OPTIONAL: REGISTER DEPARTMENT AS SNIPPET
# # Uncomment if you want departments manageable as standalone snippets
# # ------------------------------------------------------------------
# # from apps.handlers.models import Department
# #
# # @register_snippet
# # class DepartmentViewSet(BaseSnippetViewSet):
# #     """Admin interface for managing Department snippets."""
# #
# #     model = Department
# #     menu_label = _("Departments")
# #     icon = "group"
# #     menu_order = 131
# #     search_fields = ["name", "company__name", "function"]
# #     ordering = ["company__name", "name"]
# #
# #     list_display = ["name", "company", "function", "manager_display"]
# #     list_export = ["name", "company", "function", "budget", "budget_year"]
# #     csv_filename = "departments.csv"
# #
# #     @staticmethod
# #     def manager_display(obj):
# #         """Display department manager name."""
# #         return getattr(obj.manager, "get_full_name", lambda: _("—"))()
# #     manager_display.short_description = _("Manager")
# #
# #     def get_queryset(self, request):
# #         qs = super().get_queryset(request)
# #         return qs.select_related("company", "manager").prefetch_related("teams", "services")
