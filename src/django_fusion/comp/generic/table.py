import django_tables2 as tables
from django.db.models import Model
from django.views.generic import ListView


class BaseTable(tables.Table):
    check_box = tables.columns.CheckBoxColumn()
    model: Model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.model, "category"):
            self.base_columns["category"] = tables.Column(
                accessor="category", verbose_name="Category", orderable=True
            )


class TableView(ListView):
    """Generic list view backed by django-tables2."""
    table_class = None
    template_name = None

    def get_table(self):
        qs = self.get_queryset()
        if self.table_class:
            return self.table_class(qs)
        return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["table"] = self.get_table()
        return ctx
