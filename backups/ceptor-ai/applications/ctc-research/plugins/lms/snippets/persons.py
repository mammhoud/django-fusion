
# class StudentViewSet(SnippetViewSet):
#     """
#     Admin interface for managing Student records.
#     LMS-specific student management with academic information.
#     """
#     model = Student
#     menu_label = _("Students")
#     icon = "user"
#     menu_order = 220
#     list_display = ("first_name", "last_name", "job_title", "live")
#     search_fields = ("first_name", "last_name", "job_title")
#     list_filter = ("live",)
#     list_export = ("first_name", "last_name", "job_title")
