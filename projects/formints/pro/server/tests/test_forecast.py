"""
AI Forecasting (P2) — advisory demand / stock / waste / insights tests.

Covers ``services.forecast``:
  * ``demand_forecast`` — per-product projection, moving-average math, trend
    factor clamp, skips products without sales history.
  * ``stock_advisory`` — reorder recommendation when projected demand exceeds
    stock over lead time; healthy products omitted.
  * ``waste_analysis`` — waste transaction aggregation with cost estimate.
  * ``sales_insights`` — top products, growth vs previous period, rising
    products, recommendation strings.

The service is read-only advisory: it never writes POS records. Models are
imported lazily (the conftest ``django_bootstrap`` fixture configures Django
first).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from django.utils import timezone


def _svc():
    import services.forecast as f

    return f


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.pos import InventoryTransaction, Sale, SaleItem
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    InventoryTransaction.objects.all().delete()
    yield


def _product(name="Espresso", price=3.5, stock=100, threshold=10, sku=None, **kw):
    from models.pos import Product

    return Product.objects.create(
        name=name, price=price, stock_quantity=stock,
        low_stock_threshold=threshold, sku=sku, **kw,
    )


def _sale(days_ago=1, total=20.0):
    from models.pos import Sale, Customer

    return Sale.objects.create(
        customer=Customer.objects.create(
            first_name="FC", last_name="Test", email=f"fc{days_ago}@t.com",
        ),
        subtotal=total, total=total, tax_amount=0,
        status="completed",
        sale_date=timezone.now() - timedelta(days=days_ago),
    )


def _sale_item(sale, product, qty=2, line_total=None):
    from models.pos import SaleItem

    return SaleItem.objects.create(
        sale=sale, product=product, product_name=product.name,
        quantity=qty, unit_price=float(product.price),
        line_total=line_total if line_total is not None else float(product.price) * qty,
    )


def _seed_history(name="Espresso", days_back=5, daily_qty=10, price=3.5, stock=100):
    """Create a product + ``daily_qty`` units sold per day for the last N days."""
    p = _product(name=name, price=price, stock=stock)
    for d in range(1, days_back + 1):
        sale = _sale(days_ago=d, total=price * daily_qty)
        _sale_item(sale, p, qty=daily_qty, line_total=price * daily_qty)
    return p


class TestDemandForecast:
    def test_forecast_projects_daily_units(self):
        f = _svc()
        _seed_history(name="Espresso", days_back=5, daily_qty=10)
        result = f.demand_forecast(days=14, lookback=28)
        assert result["advisory"] is True
        rows = {r["product_name"]: r for r in result["products"]}
        assert "Espresso" in rows
        # 50 units over the 28-day lookback → avg daily ≈ 1.79
        assert 1.5 <= rows["Espresso"]["avg_daily_units"] <= 2.1
        assert rows["Espresso"]["projected_days_total"] > 0

    def test_forecast_skips_products_without_history(self):
        f = _svc()
        _product(name="NoHistory", price=5)
        result = f.demand_forecast()
        assert all(r["product_name"] != "NoHistory" for r in result["products"])

    def test_trend_factor_clamped(self):
        f = _svc()
        p = _product(name="Trending", price=2)
        # Old history: low. Recent history: high → trend > 1, clamped to 2.
        for d in range(20, 7, -1):
            sale = _sale(days_ago=d, total=4)
            _sale_item(sale, p, qty=1, line_total=2)
        for d in range(7, 0, -1):
            sale = _sale(days_ago=d, total=40)
            _sale_item(sale, p, qty=20, line_total=40)
        result = f.demand_forecast(lookback=28)
        row = next(r for r in result["products"] if r["product_name"] == "Trending")
        assert row["trend_factor"] <= 2.0


class TestStockAdvisory:
    def test_reorder_when_demand_exceeds_stock(self):
        f = _svc()
        _seed_history(name="Popular", days_back=5, daily_qty=10, stock=5)
        result = f.stock_advisory(days=14, lead_time_days=3)
        rows = {r["product_name"]: r for r in result["reorders"]}
        assert "Popular" in rows
        assert rows["Popular"]["current_stock"] == 5
        assert rows["Popular"]["suggested_reorder_quantity"] > 0
        assert rows["Popular"]["reason"]

    def test_healthy_product_omitted(self):
        f = _svc()
        _seed_history(name="Healthy", days_back=5, daily_qty=2, stock=500)
        result = f.stock_advisory()
        assert all(r["product_name"] != "Healthy" for r in result["reorders"])

    def test_zero_stock_flagged(self):
        f = _svc()
        _seed_history(name="Empty", days_back=5, daily_qty=5, stock=0)
        result = f.stock_advisory()
        rows = {r["product_name"]: r for r in result["reorders"]}
        assert "Empty" in rows
        assert rows["Empty"]["days_of_cover"] == 0.0


class TestWasteAnalysis:
    def test_waste_aggregation(self):
        f = _svc()
        from models.pos import InventoryTransaction
        p = _product(name="Milk", price=2, stock=50)
        InventoryTransaction.objects.create(
            product=p, transaction_type="waste", quantity=3,
        )
        InventoryTransaction.objects.create(
            product=p, transaction_type="waste", quantity=2,
        )
        result = f.waste_analysis(days=30)
        assert result["total_wasted_units"] == 5
        entry = result["by_product"][0]
        assert entry["product_name"] == "Milk"
        assert entry["units"] == 5

    def test_waste_excludes_non_waste_txns(self):
        f = _svc()
        from models.pos import InventoryTransaction
        p = _product(name="Stock", price=1)
        InventoryTransaction.objects.create(
            product=p, transaction_type="in", quantity=50,
        )
        result = f.waste_analysis()
        assert result["total_wasted_units"] == 0


class TestSalesInsights:
    def test_insights_growth(self):
        f = _svc()
        _seed_history(name="Old", days_back=20, daily_qty=2, price=3)
        _seed_history(name="New", days_back=3, daily_qty=10, price=3)
        result = f.sales_insights(days=30)
        assert result["current_revenue"] > 0
        assert result["advisory"] is True
        # Top products list populated.
        assert any(t["product_name"] == "New" for t in result["top_products"])

    def test_insights_flat_history(self):
        f = _svc()
        _seed_history(name="Steady", days_back=5, daily_qty=4)
        result = f.sales_insights(days=30)
        assert result["growth_pct"] is not None or result["current_revenue"] > 0
        assert isinstance(result["recommendations"], list)

    def test_insights_empty(self):
        f = _svc()
        result = f.sales_insights(days=30)
        assert result["current_revenue"] == 0
        assert result["top_products"] == []


class TestFullReport:
    def test_full_report_envelope(self):
        f = _svc()
        _seed_history(name="Coffee", days_back=5, daily_qty=6)
        report = f.full_report(days=14)
        assert report["advisory"] is True
        for key in ("demand", "stock", "waste", "insights"):
            assert key in report
            assert report[key]["advisory"] is True
