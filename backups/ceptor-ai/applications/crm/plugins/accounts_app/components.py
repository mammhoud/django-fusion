"""Accounts fragment components."""
from __future__ import annotations

from django.db.models import Q

from django_fusion.comp.routes import FragmentComponent


class CustomerListFragment(FragmentComponent):
    """
    HTMX customer list fragment with search.

    URL: /crm/accounts_app/accounts_app/customers/list-fragment/
    Template: crm/fragments/customer_list.html
    """

    route_name = "customer-list-fragment"
    route_path = "customers/list-fragment/"
    fragment_name = "crm.fragments.customer_list"
    htmx_only = True
    paginate_by = 20
    show_in_menu = False

    def has_permission(self, user):
        return user.is_authenticated

    def get_queryset(self):
        from plugins.accounts_app.models import Customer

        qs = Customer.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(email__icontains=q)
            )
        return qs

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context
