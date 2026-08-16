"""
POS Full — Unfold Admin Dashboard.

Real-time POS KPI cards, charts, and recent activity feeds injected into the
admin index page.

Two integration paths are supported so the dashboard works across unfold
versions:

1. unfold >= 0.80 — ``UNFOLD["DASHBOARD_CALLBACK"]`` points at
   ``configs.dashboard.pos_dashboard_callback``; the custom
   ``admin/index.html`` override (server/django_templates) renders
   KPI cards, Chart.js charts, and tables.
2. older unfold — ``UNFOLD["DASHBOARD"]`` points at ``POSDashboardView``
   (defined only when ``unfold.views.DashboardView`` is available).

The heavy lifting lives in plain functions (``compute_kpi_cards``,
``compute_charts``, ``compute_tables``) so the callback never depends on a
specific unfold version.
"""

from datetime import timedelta

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

from models.pos import Category, Product, Customer, Sale, SaleItem
from models.node import Node
from models.ops import SupportTicket, KitchenTicket
from models.inventory import PurchaseOrder
from models.loyalty import ClientCategory, LoyaltyTransaction


def compute_kpi_cards(request) -> list:
    """KPI cards showing key business metrics.

    Returns a list of dicts:
    { title, metric, footer, trend (optional) }
    """
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    this_year = today.replace(month=1, day=1)
    last_year = this_year.replace(year=this_year.year - 1)

    # Same-day-range boundaries for period comparisons
    # MTD comparison: same number of days in previous month
    mtd_end = today
    prev_mtd_end = last_month + timedelta(days=today.day - 1)
    # YTD comparison: same number of days in previous year
    ytd_end = today
    prev_ytd_end = last_year + timedelta(days=today.timetuple().tm_yday - 1)

    # Today's sales
    today_sales = Sale.objects.filter(sale_date__date=today).aggregate(
        count=Count("id"), revenue=Sum("total")
    )

    # Monthly revenue
    month_sales = Sale.objects.filter(sale_date__date__gte=this_month).aggregate(
        count=Count("id"), revenue=Sum("total")
    )
    last_month_sales = Sale.objects.filter(
        sale_date__date__gte=last_month,
        sale_date__date__lt=this_month,
    ).aggregate(revenue=Sum("total"), count=Count("id"))

    current_revenue = month_sales["revenue"] or 0
    prev_revenue = last_month_sales["revenue"] or 0
    revenue_trend = (
        round(((current_revenue - prev_revenue) / prev_revenue) * 100, 1)
        if prev_revenue > 0
        else 0
    )

    # Average Order Value (AOV) = total revenue / total orders this month
    month_count = month_sales["count"] or 0
    aov = (current_revenue / month_count) if month_count > 0 else 0

    # Last month AOV for trend comparison
    prev_month_count = last_month_sales.get("count") or 0
    prev_aov = (prev_revenue / prev_month_count) if prev_month_count > 0 else 0
    aov_trend = (
        round(((aov - prev_aov) / prev_aov) * 100, 1)
        if prev_aov > 0
        else 0
    )

    # ── Month-to-Date (MTD) Revenue ──
    mtd_sales = Sale.objects.filter(
        sale_date__date__gte=this_month, sale_date__date__lte=mtd_end
    ).aggregate(revenue=Sum("total"), count=Count("id"))
    mtd_revenue = mtd_sales["revenue"] or 0

    prev_mtd_sales = Sale.objects.filter(
        sale_date__date__gte=last_month, sale_date__date__lte=prev_mtd_end
    ).aggregate(revenue=Sum("total"), count=Count("id"))
    prev_mtd_revenue = prev_mtd_sales["revenue"] or 0

    mtd_trend = (
        round(((mtd_revenue - prev_mtd_revenue) / prev_mtd_revenue) * 100, 1)
        if prev_mtd_revenue > 0
        else 0
    )

    # ── Year-to-Date (YTD) Revenue ──
    ytd_sales = Sale.objects.filter(
        sale_date__date__gte=this_year, sale_date__date__lte=ytd_end
    ).aggregate(revenue=Sum("total"), count=Count("id"))
    ytd_revenue = ytd_sales["revenue"] or 0

    prev_ytd_sales = Sale.objects.filter(
        sale_date__date__gte=last_year, sale_date__date__lte=prev_ytd_end
    ).aggregate(revenue=Sum("total"), count=Count("id"))
    prev_ytd_revenue = prev_ytd_sales["revenue"] or 0

    ytd_trend = (
        round(((ytd_revenue - prev_ytd_revenue) / prev_ytd_revenue) * 100, 1)
        if prev_ytd_revenue > 0
        else 0
    )

    # Node health
    total_nodes = Node.objects.count()
    online_nodes = Node.objects.filter(status="online").count()

    # Alerts
    open_support = SupportTicket.objects.filter(
        status__in=["open", "in_progress"]
    ).count()
    pending_kitchen = KitchenTicket.objects.filter(status="pending").count()
    pending_pos = PurchaseOrder.objects.filter(status="draft").count()
    alert_count = open_support + pending_kitchen + pending_pos

    # ── Loyalty / client category metrics ──
    loyalty_members = Customer.objects.filter(
        client_category__isnull=False
    ).count()
    loyalty_transactions = LoyaltyTransaction.objects.all()
    points_issued = loyalty_transactions.filter(
        transaction_type="earn", points_change__gt=0
    ).aggregate(total=Sum("points_change"))["total"] or 0
    points_redeemed = loyalty_transactions.filter(
        points_change__lt=0
    ).aggregate(total=Sum("points_change"))["total"] or 0
    client_categories = ClientCategory.objects.filter(is_active=True).count()

    return [
        {
            "title": "Today's Sales",
            "metric": f"${today_sales['revenue'] or 0:,.2f}",
            "footer": f"{today_sales['count'] or 0} transactions today",
        },
        {
            "title": "Monthly Revenue",
            "metric": f"${current_revenue:,.2f}",
            "footer": (
                f"{month_count} transactions"
                + (f" · {revenue_trend:+.1f}% vs last month" if revenue_trend != 0 else "")
            ),
        },
        {
            "title": "Avg Order Value",
            "metric": f"${aov:,.2f}",
            "footer": (
                f"{month_count} orders this month"
                + (f" · {aov_trend:+.1f}% vs last month" if aov_trend != 0 else "")
            ),
        },
        {
            "title": "MTD Revenue",
            "metric": f"${mtd_revenue:,.2f}",
            "footer": (
                f"{mtd_sales['count'] or 0} transactions"
                + (f" · {mtd_trend:+.1f}% vs last month" if mtd_trend != 0 else "")
            ),
        },
        {
            "title": "YTD Revenue",
            "metric": f"${ytd_revenue:,.2f}",
            "footer": (
                f"{ytd_sales['count'] or 0} transactions"
                + (f" · {ytd_trend:+.1f}% vs last year" if ytd_trend != 0 else "")
            ),
        },
        {
            "title": "Active Products",
            "metric": str(Product.objects.filter(is_active=True).count()),
            "footer": f"{Category.objects.count()} categories",
        },
        {
            "title": "Customers",
            "metric": str(Customer.objects.filter(is_active=True).count()),
            "footer": f"Total: {Customer.objects.count()} registered",
        },
        {
            "title": "Branch Nodes",
            "metric": f"{online_nodes}/{total_nodes}",
            "footer": (
                f"{online_nodes} online · {total_nodes - online_nodes} offline"
                if total_nodes > 0
                else "No nodes registered"
            ),
        },
        {
            "title": "Open Alerts",
            "metric": str(alert_count),
            "footer": (
                f"{open_support} support · {pending_kitchen} kitchen"
                f" · {pending_pos} POs"
            ),
        },
        {
            "title": "Loyalty Members",
            "metric": str(loyalty_members),
            "footer": f"{client_categories} client categories active",
        },
        {
            "title": "Points Issued",
            "metric": f"{points_issued:,.0f}",
            "footer": (
                f"{points_redeemed:,.0f} points redeemed"
                if points_redeemed
                else "No redemptions yet"
            ),
        },
    ]


def compute_charts(request) -> list:
    """Dashboard charts.

    Returns a list of Chart.js-compatible dicts:
    { title, type, labels, datasets: [{ label, data, ... }] }

    Charts:
    1. Revenue — Last 7 Days (bar)
    2. Top Products by Revenue (pie) — top 10
    3. Sales by Payment Method (doughnut)
    4. Hourly Sales Activity (bar — revenue by hour)
    5. Client Category Distribution (pie)
    """
    today = timezone.now().date()
    days_ago = today - timedelta(days=7)

    # ── 1. Daily Revenue (Last 7 Days) — bar ──
    daily_sales = (
        Sale.objects.filter(sale_date__date__gte=days_ago)
        .annotate(day=TruncDate("sale_date"))
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )

    # ── 2. Top Products by Revenue (Last 7 Days) — pie ──
    top_products = (
        SaleItem.objects.filter(sale__sale_date__date__gte=days_ago)
        .values("product_name")
        .annotate(total=Sum("line_total"))
        .order_by("-total")[:10]
    )

    # ── 3. Sales by Payment Method (Last 7 Days) — doughnut ──
    payment_methods = (
        Sale.objects.filter(sale_date__date__gte=days_ago)
        .values("payment_method")
        .annotate(count=Count("id"), total=Sum("total"))
        .order_by("-total")
    )

    # Payment method display labels
    PAYMENT_LABELS = {
        "cash": "Cash",
        "card": "Card",
        "mobile": "Mobile",
        "mixed": "Mixed",
        "credit": "Store Credit",
    }

    # ── 4. Hourly Sales Activity (Last 7 Days) — bar ──
    hourly_sales = (
        Sale.objects.filter(sale_date__date__gte=days_ago)
        .annotate(hour=TruncHour("sale_date"))
        .values("hour")
        .annotate(
            count=Count("id"),
            total=Sum("total"),
        )
        .order_by("hour")
    )

    # Aggregate hourly by extracting hour of day (0-23)
    hourly_agg = {h: {"count": 0, "total": 0.0} for h in range(24)}
    for h in hourly_sales:
        hour = h["hour"].hour  # extract hour from truncated datetime
        hourly_agg[hour] = {
            "count": h["count"],
            "total": float(h["total"] or 0),
        }

    # ── 5. Client Category Distribution — pie ──
    active_categories = list(ClientCategory.objects.filter(is_active=True))
    category_labels = [c.name for c in active_categories] or ["Uncategorized"]
    category_data = [c.customer_count for c in active_categories] or [
        Customer.objects.filter(client_category__isnull=True).count()
    ]

    return [
        {
            "title": "Revenue — Last 7 Days",
            "type": "bar",
            "labels": [d["day"].strftime("%a %m/%d") for d in daily_sales],
            "datasets": [
                {
                    "label": "Revenue ($)",
                    "data": [float(d["total"] or 0) for d in daily_sales],
                }
            ],
        },
        {
            "title": "Top Products by Revenue — Last 7 Days",
            "type": "pie",
            "labels": [p["product_name"] for p in top_products],
            "datasets": [
                {
                    "label": "Revenue ($)",
                    "data": [float(p["total"] or 0) for p in top_products],
                }
            ],
        },
        {
            "title": "Sales by Payment Method — Last 7 Days",
            "type": "doughnut",
            "labels": [
                PAYMENT_LABELS.get(p["payment_method"], p["payment_method"])
                for p in payment_methods
            ],
            "datasets": [
                {
                    "label": "Revenue ($)",
                    "data": [float(p["total"] or 0) for p in payment_methods],
                }
            ],
        },
        {
            "title": "Hourly Revenue — Last 7 Days",
            "type": "bar",
            "labels": [f"{h:02d}:00" for h in range(24)],
            "datasets": [
                {
                    "label": "Revenue ($)",
                    "data": [hourly_agg[h]["total"] for h in range(24)],
                },
            ],
        },
        {
            "title": "Hourly Transactions — Last 7 Days",
            "type": "bar",
            "labels": [f"{h:02d}:00" for h in range(24)],
            "datasets": [
                {
                    "label": "Transactions",
                    "data": [hourly_agg[h]["count"] for h in range(24)],
                },
            ],
        },
        {
            "title": "Client Category Distribution",
            "type": "pie",
            "labels": category_labels,
            "datasets": [
                {
                    "label": "Customers",
                    "data": category_data,
                }
            ],
        },
    ]


def compute_tables(request) -> list:
    """Recent activity tables.

    Returns a list of dicts:
    { title, headers: [...], rows: [[...], ...] }
    """
    # Recent sales
    recent_sales = (
        Sale.objects.select_related("customer")
        .order_by("-sale_date")[:5]
    )

    # Recent nodes
    recent_nodes = Node.objects.order_by("-last_seen")[:5]

    return [
        {
            "title": "Recent Sales",
            "headers": ["ID", "Customer", "Amount", "Status", "Date"],
            "rows": [
                [
                    str(s.id),
                    str(s.customer) if s.customer else "Walk-in",
                    f"${s.total:,.2f}",
                    s.get_status_display(),
                    s.sale_date.strftime("%Y-%m-%d %H:%M"),
                ]
                for s in recent_sales
            ],
        },
        {
            "title": "Node Status",
            "headers": ["Node ID", "Type", "Status", "Last Seen"],
            "rows": [
                [
                    n.node_id,
                    n.get_node_type_display(),
                    n.get_status_display(),
                    (
                        n.last_seen.strftime("%Y-%m-%d %H:%M")
                        if n.last_seen
                        else "—"
                    ),
                ]
                for n in recent_nodes
            ],
        },
    ]


# ---------------------------------------------------------------------------
# Legacy unfold.views.DashboardView adapter (only defined when available)
# ---------------------------------------------------------------------------

DASHBOARD_TITLE = "POS Full — Master Manager Dashboard"
DASHBOARD_SUBTITLE = "Real-time overview of all branch devices, sales, and operations"


def _get_unfold_dashboard_base():
    """Return unfold's DashboardView base class or None (unfold >= 0.80)."""
    from importlib import import_module

    views_module = import_module("unfold.views")
    return getattr(views_module, "DashboardView", None)


_dashboard_base = _get_unfold_dashboard_base()

if _dashboard_base is not None:

    class POSDashboardView(_dashboard_base):
        """Legacy unfold DashboardView subclass (unfold < 0.80)."""

        title = DASHBOARD_TITLE
        subtitle = DASHBOARD_SUBTITLE

        def get_kpi_cards(self, request):
            return compute_kpi_cards(request)

        def get_charts(self, request):
            return compute_charts(request)

        def get_tables(self, request):
            return compute_tables(request)


def pos_dashboard_callback(request, context):
    """Unfold ``DASHBOARD_CALLBACK`` (unfold >= 0.80 style).

    Injects KPI cards, charts, and tables into the admin index context.
    The custom ``admin/index.html`` override (server/django_templates)
    renders them.
    """
    context["kpi_cards"] = compute_kpi_cards(request)
    context["charts"] = compute_charts(request)
    context["dashboard_tables"] = compute_tables(request)
    context["dashboard_title"] = DASHBOARD_TITLE
    context["dashboard_subtitle"] = DASHBOARD_SUBTITLE
    return context
