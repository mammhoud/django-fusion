use diesel::prelude::*;
use diesel::dsl::{count, sum};
use diesel::sql_types::{Text, BigInt, Double};
use crate::db::{schema::sales, open_conn};
use std::path::PathBuf;
use chrono::{Duration, Local};
use serde::Serialize;

#[derive(Serialize)]
pub struct DailyRevenue { pub date: String, pub revenue: f64, pub orders: i64 }
#[derive(Serialize)]
pub struct TopProduct { pub name: String, pub sales: i64, pub revenue: f64 }
#[derive(Serialize)]
pub struct ProductDistribution { pub name: String, pub value: i64 }
#[derive(Serialize)]
pub struct AnalyticsSummary { pub total_orders: i64, pub total_revenue: f64, pub average_order_value: f64 }
#[derive(Serialize)]
pub struct AnalyticsData {
    pub daily_revenue: Vec<DailyRevenue>,
    pub top_products: Vec<TopProduct>,
    pub product_distribution: Vec<ProductDistribution>,
    pub summary: AnalyticsSummary,
}

// QueryableByName structs for raw SQL deserialization
#[derive(QueryableByName)]
struct TopProductRow {
    #[diesel(sql_type = Text)]
    name: String,
    #[diesel(sql_type = BigInt)]
    sales: i64,
    #[diesel(sql_type = Double)]
    revenue: f64,
}

#[derive(QueryableByName)]
struct DistRow {
    #[diesel(sql_type = Text)]
    name: String,
    #[diesel(sql_type = BigInt)]
    value: i64,
}

#[derive(QueryableByName)]
struct SummaryRow {
    #[diesel(sql_type = BigInt)]
    total_orders: i64,
    #[diesel(sql_type = Double)]
    total_revenue: f64,
}

pub fn get_analytics(db_path: &PathBuf) -> Result<AnalyticsData, String> {
    let mut conn = open_conn(db_path)?;
    let cutoff = (Local::now().naive_local().date() - Duration::days(30))
        .format("%Y-%m-%d")
        .to_string();

    // Daily revenue (last 30 days, oldest first, then reversed for chart display)
    let daily_rows: Vec<(String, Option<f64>, i64)> = sales::table
        .filter(sales::date.ge(&cutoff))
        .group_by(sales::date)
        .select((sales::date, sum(sales::total_amount), count(sales::id)))
        .order(sales::date.asc())
        .load(&mut conn)
        .map_err(|e| e.to_string())?;

    let mut daily_revenue = daily_rows.into_iter()
        .map(|(date, rev, orders)| DailyRevenue {
            date,
            revenue: rev.unwrap_or(0.0),
            orders,
        })
        .collect::<Vec<_>>();
    daily_revenue.reverse();

    // Top products (raw SQL with QueryableByName)
    let top_rows: Vec<TopProductRow> = diesel::sql_query(
        "SELECT product_name as name, CAST(SUM(quantity) AS INTEGER) as sales, \
         COALESCE(SUM(price * quantity), 0.0) as revenue \
         FROM sale_items \
         GROUP BY product_name \
         ORDER BY sales DESC \
         LIMIT 10"
    )
    .load(&mut conn)
    .map_err(|e| e.to_string())?;

    let top_products = top_rows.into_iter()
        .map(|r| TopProduct { name: r.name, sales: r.sales, revenue: r.revenue })
        .collect();

    // Product distribution (raw SQL with QueryableByName)
    let dist_rows: Vec<DistRow> = diesel::sql_query(
        "SELECT product_name as name, CAST(SUM(quantity) AS INTEGER) as value \
         FROM sale_items \
         GROUP BY product_name \
         ORDER BY value DESC \
         LIMIT 5"
    )
    .load(&mut conn)
    .map_err(|e| e.to_string())?;

    let product_distribution = dist_rows.into_iter()
        .map(|r| ProductDistribution { name: r.name, value: r.value })
        .collect();

    // Summary (raw SQL with QueryableByName)
    let summary_rows: Vec<SummaryRow> = diesel::sql_query(
        "SELECT COUNT(*) as total_orders, COALESCE(SUM(total_amount), 0.0) as total_revenue FROM sales"
    )
    .load(&mut conn)
    .map_err(|e| e.to_string())?;

    let (total_orders, total_revenue) = summary_rows.into_iter()
        .next()
        .map(|r| (r.total_orders, r.total_revenue))
        .unwrap_or((0, 0.0));

    let average_order_value = if total_orders > 0 {
        total_revenue / total_orders as f64
    } else {
        0.0
    };

    Ok(AnalyticsData {
        daily_revenue,
        top_products,
        product_distribution,
        summary: AnalyticsSummary {
            total_orders,
            total_revenue,
            average_order_value,
        },
    })
}
