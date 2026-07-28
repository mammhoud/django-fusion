"""Accounts plugin URL patterns (auth helpers, AJAX endpoints)."""
from django.http import JsonResponse, HttpResponse
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def is_ajax(request):
    return (
        request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
        or request.headers.get("HX-Request")
    )


@csrf_exempt
@require_POST
@login_required
def get_customers_ajax(request):
    """Return customers as Select2/HTMX-compatible JSON."""
    from plugins.accounts_app.models import Customer

    term = request.POST.get("term", "")
    customers = Customer.objects.filter(first_name__icontains=term)[:15]
    data = [c.to_select2() for c in customers]
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_POST
@login_required
def get_items_ajax(request):
    """Return inventory items as HTMX fragment HTML for the POS search box."""
    from plugins.inventory.models import Item
    from django.template.loader import render_to_string

    term = request.POST.get("term", "").strip()
    if not term:
        return HttpResponse("")

    items = Item.objects.filter(name__icontains=term).select_related("category")[:10]
    items_data = [i.to_json() for i in items]

    html = render_to_string(
        "crm/fragments/item_search_results.html",
        {"items": items_data},
        request=request,
    )
    return HttpResponse(html)


app_name = "crm_accounts"

urlpatterns = [
    path("get-customers/", get_customers_ajax, name="get_customers"),
    path("get-items/", get_items_ajax, name="get_items"),
]
