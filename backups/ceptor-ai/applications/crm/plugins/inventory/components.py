"""
Inventory Components
====================
RoutableComponent and FragmentComponent implementations for the CRM inventory.
"""
from __future__ import annotations

from django.db.models import Count, Sum, Q

from django_fusion.comp.routes import FragmentComponent, RoutableComponent


class CRMDashboardComponent(RoutableComponent):
    """
    CRM main dashboard — full-page component.

    URL: /crm/dashboard/dashboard/
    Template: crm/dashboard.html
    """

    route_name = "dashboard"
    route_path = "dashboard/"
    title = "Dashboard"
    page_title = "Dashboard"
    icon = "dashboard"
    menu_order = 1
    template_name = "crm/dashboard.html"

    def has_permission(self, user):
        return user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self._build_stats())
        return context

    def _build_stats(self) -> dict:
        from plugins.inventory.models import Category, Delivery, Item
        from plugins.transactions_app.models import Sale
        from plugins.accounts_app.models import StaffProfile

        items = Item.objects.all()
        total_items = items.aggregate(total=Sum("quantity")).get("total") or 0
        category_qs = Category.objects.annotate(item_count=Count("items"))
        sale_dates_qs = (
            Sale.objects.values("date_added__date")
            .annotate(total_sales=Sum("grand_total"))
            .order_by("date_added__date")
        )
        return {
            "items_count": items.count(),
            "total_items": total_items,
            "profiles_count": StaffProfile.objects.count(),
            "delivery_count": Delivery.objects.filter(is_delivered=False).count(),
            "sales_count": Sale.objects.count(),
            "categories": [c.name for c in category_qs],
            "category_counts": [c.item_count for c in category_qs],
            "sale_dates_labels": [
                d["date_added__date"].strftime("%Y-%m-%d") for d in sale_dates_qs
            ],
            "sale_dates_values": [float(d["total_sales"]) for d in sale_dates_qs],
        }


class ItemListFragment(FragmentComponent):
    """
    HTMX item list fragment with search + category filter.

    URL: /crm/inventory/inventory/items/list-fragment/
    Fragment template: crm/fragments/item_list.html
    """

    route_name = "item-list-fragment"
    route_path = "items/list-fragment/"
    fragment_name = "crm.fragments.item_list"
    htmx_only = True
    paginate_by = 20
    show_in_menu = False

    def has_permission(self, user):
        return user.is_authenticated

    def get_queryset(self):
        from plugins.inventory.models import Item

        qs = Item.objects.select_related("category", "vendor")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs.order_by("name")

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        from plugins.inventory.models import Category
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["categories"] = Category.objects.all()
        return context
