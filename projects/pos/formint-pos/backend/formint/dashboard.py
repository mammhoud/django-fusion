"""
Formint — Unfold Admin Dashboard.

Real-time POS KPI cards, charts, and recent activity feeds injected into the
admin index page via ``UNFOLD["DASHBOARD_CALLBACK"]`` (unfold >= 0.80).

Includes a dedicated **Loyalty & Settings** focus: client categories, loyalty
points issued/redeemed, and user settings coverage, alongside the classic
sales/products/customers/nodes KPIs.

The custom ``admin/index.html`` override (backend/templates) renders the
injected context (``kpi_cards``, ``charts``, ``dashboard_tables``).
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

from formint.models import (
    Category, ClientCategory, Customer, LoyaltyTransaction, Node, Product,
    Sale, SaleItem, SupportTicket, UserSettings,
)

DASHBOARD_TITLE = "Formint POS — Professional Dashboard"
DASHBOARD_SUBTITLE = "Merged master manager · real-time sales, loyalty & settings overview"


def compute_kpi_cards(request) -> list:
    """KPI cards showing key business + loyalty/settings metrics."""
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    # Today's sales
    today_sales = Sale.objects.filter(sale_date__date=today).aggregate(
        count=Count("id"), revenue=Sum("total")
    )

    # Monthly revenue + AOV
    month_sales = Sale.objects.filter(sale_date__date__gte=this_month).aggregate(
        count=Count("id"), revenue=Sum("total")
    )
    last_month_sales = Sale.objects.filter(
        sale_date__date__gte=last_month, sale_date__date__lt=this_month,
    ).aggregate(count=Count("id"), revenue=Sum("total"))

    current_revenue = month_sales["revenue"] or 0
    prev_revenue = last_month_sales["revenue"] or 0
    revenue_trend = (
        round(((current_revenue - prev_revenue) / prev_revenue) * 100, 1)
        if prev_revenue > 0 else 0
    )
    month_count = month_sales["count"] or 0
    aov = (current_revenue / month_count) if month_count > 0 else 0

    # ── Loyalty metrics ──
    loyalty_members = Customer.objects.filter(client_category__isnull=False).count()
    loyalty_transactions = LoyaltyTransaction.objects.all()
    points_issued = loyalty_transactions.filter(
        transaction_type="earn", points_change__gt=0
    ).aggregate(total=Sum("points_change"))["total"] or 0
    points_redeemed = abs(loyalty_transactions.filter(
        points_change__lt=0
    ).aggregate(total=Sum("points_change"))["total"] or 0)
    active_client_categories = ClientCategory.objects.filter(is_active=True).count()

    # ── Settings coverage ──
    settings_rows = UserSettings.objects.count()
    two_factor_enabled = UserSettings.objects.filter(two_factor_enabled=True).count()

    # ── Nodes & alerts ──
    total_nodes = Node.objects.count()
    online_nodes = Node.objects.filter(status="online").count()
    open_support = SupportTicket.objects.filter(
        status__in=["open", "in_progress"]
    ).count()

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
                + (f" · {revenue_trend:+.1f}% vs last month" if revenue_trend else "")
            ),
        },
        {
            "title": "Avg Order Value",
            "metric": f"${aov:,.2f}",
            "footer": f"{month_count} orders this month",
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
                if total_nodes else "No nodes registered"
            ),
        },
        {
            "title": "Loyalty Members",
            "metric": str(loyalty_members),
            "footer": f"{active_client_categories} client categories active",
        },
        {
            "title": "Points Issued",
            "metric": f"{points_issued:,.0f}",
            "footer": f"{points_redeemed:,.0f} points redeemed",
        },
        {
            "title": "Settings Rows",
            "metric": str(settings_rows),
            "footer": (
                f"{two_factor_enabled} users with 2FA enabled"
                if two_factor_enabled else "No 2FA enabled yet"
            ),
        },
        {
            "title": "Open Alerts",
            "metric": str(open_support),
            "footer": f"{open_support} open support tickets",
        },
    ]


def compute_charts(request) -> list:
    """Dashboard charts (Chart.js-compatible dicts)."""
    today = timezone.now().date()
    days_ago = today - timedelta(days=7)

    # 1. Daily revenue — last 7 days (bar)
    daily_sales = (
        Sale.objects.filter(sale_date__date__gte=days_ago)
        .annotate(day=TruncDate("sale_date"))
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )

    # 2. Top products by revenue (pie)
    top_products = (
        SaleItem.objects.filter(sale__sale_date__date__gte=days_ago)
        .values("product_name")
        .annotate(total=Sum("line_total"))
        .order_by("-total")[:10]
    )

    # 3. Sales by payment method (doughnut)
    payment_methods = (
        Sale.objects.filter(sale_date__date__gte=days_ago)
        .values("payment_method")
        .annotate(count=Count("id"), total=Sum("total"))
        .order_by("-total")
    )
    PAYMENT_LABELS = {
        "cash": "Cash", "card": "Card", "mobile": "Mobile",
        "mixed": "Mixed", "credit": "Store Credit",
    }

    # 4. Hourly sales activity (bar)
    hourly_sales = (
        Sale.objects.filter(sale_date__date__gte=days_ago)
        .annotate(hour=TruncHour("sale_date"))
        .values("hour")
        .annotate(count=Count("id"), total=Sum("total"))
        .order_by("hour")
    )
    hourly_agg = {h: {"count": 0, "total": 0.0} for h in range(24)}
    for h in hourly_sales:
        hour = h["hour"].hour
        hourly_agg[hour] = {"count": h["count"], "total": float(h["total"] or 0)}

    # 5. Loyalty transaction mix (doughnut)
    loyalty_mix = (
        LoyaltyTransaction.objects.values("transaction_type")
        .annotate(total=Sum("points_change"))
        .order_by("-total")
    )
    LOYALTY_LABELS = {
        "earn": "Earn", "redeem": "Redeem",
        "adjust": "Adjustment", "expire": "Expiry",
    }

    return [
        {
            "title": "Revenue — Last 7 Days",
            "type": "bar",
            "labels": [d["day"].strftime("%a %m/%d") for d in daily_sales],
            "datasets": [
                {"label": "Revenue ($)", "data": [float(d["total"] or 0) for d in daily_sales]}
            ],
        },
        {
            "title": "Top Products by Revenue — Last 7 Days",
            "type": "pie",
            "labels": [p["product_name"] for p in top_products],
            "datasets": [
                {"label": "Revenue ($)", "data": [float(p["total"] or 0) for p in top_products]}
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
                {"label": "Revenue ($)", "data": [float(p["total"] or 0) for p in payment_methods]}
            ],
        },
        {
            "title": "Hourly Revenue — Last 7 Days",
            "type": "bar",
            "labels": [f"{h:02d}:00" for h in range(24)],
            "datasets": [
                {"label": "Revenue ($)", "data": [hourly_agg[h]["total"] for h in range(24)]}
            ],
        },
        {
            "title": "Loyalty Points — Transaction Mix",
            "type": "doughnut",
            "labels": [
                LOYALTY_LABELS.get(t["transaction_type"], t["transaction_type"])
                for t in loyalty_mix
            ],
            "datasets": [
                {"label": "Points", "data": [float(t["total"] or 0) for t in loyalty_mix]}
            ],
        },
    ]


def compute_tables(request) -> list:
    """Recent activity tables."""
    recent_sales = Sale.objects.select_related("customer").order_by("-sale_date")[:5]
    recent_loyalty = (
        LoyaltyTransaction.objects.select_related("customer")
        .order_by("-created_at")[:5]
    )
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
            "title": "Recent Loyalty Transactions",
            "headers": ["ID", "Customer", "Type", "Points", "Date"],
            "rows": [
                [
                    str(t.id),
                    str(t.customer),
                    t.get_transaction_type_display(),
                    f"{t.points_change:+d}",
                    t.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
                for t in recent_loyalty
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
                    n.last_seen.strftime("%Y-%m-%d %H:%M") if n.last_seen else "—",
                ]
                for n in recent_nodes
            ],
        },
    ]


def formint_dashboard_callback(request, context):
    """Unfold ``DASHBOARD_CALLBACK`` (>= 0.80) — inject KPI/charts/tables."""
    context["kpi_cards"] = compute_kpi_cards(request)
    context["charts"] = compute_charts(request)
    context["dashboard_tables"] = compute_tables(request)
    context["dashboard_title"] = DASHBOARD_TITLE
    context["dashboard_subtitle"] = DASHBOARD_SUBTITLE
    return context
