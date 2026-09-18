use crate::db::models::*;
use crate::db::schema::{budgets, finance_transactions};
use diesel::prelude::*;
use std::path::PathBuf;

// ---- Finance transactions ----

pub fn get_finance_transactions(db_path: &PathBuf) -> Result<Vec<FinanceTransaction>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    finance_transactions::table
        .order((finance_transactions::date.desc(), finance_transactions::id.desc()))
        .select(FinanceTransaction::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_finance_transaction(
    db_path: &PathBuf,
    tx: NewFinanceTransaction,
) -> Result<FinanceTransaction, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(finance_transactions::table)
            .values(&tx)
            .execute(conn)?;
        finance_transactions::table.order(finance_transactions::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_finance_transaction(
    db_path: &PathBuf,
    id: i32,
    update: UpdateFinanceTransaction,
) -> Result<FinanceTransaction, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(finance_transactions::table.find(id))
            .set(&update)
            .execute(conn)?;
        finance_transactions::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_finance_transaction(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(finance_transactions::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

// ---- Budgets ----

pub fn get_budgets(db_path: &PathBuf) -> Result<Vec<Budget>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    budgets::table
        .order((budgets::period_start.desc(), budgets::id.desc()))
        .select(Budget::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_budget(db_path: &PathBuf, budget: NewBudget) -> Result<Budget, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(budgets::table).values(&budget).execute(conn)?;
        budgets::table.order(budgets::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_budget(db_path: &PathBuf, id: i32, update: UpdateBudget) -> Result<Budget, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(budgets::table.find(id)).set(&update).execute(conn)?;
        budgets::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_budget(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(budgets::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

// ---- Summary ----

/// Aggregates the finance summary: income/expense totals (overall and per
/// category) plus budget tracking (budget vs. actual expense in the period).
pub fn get_finance_summary(db_path: &PathBuf) -> Result<FinanceSummary, String> {
    let mut conn = crate::db::open_conn(db_path)?;

    let all = finance_transactions::table
        .select(FinanceTransaction::as_select())
        .load::<FinanceTransaction>(&mut conn)
        .map_err(|e| e.to_string())?;

    let mut total_income = 0.0;
    let mut total_expense = 0.0;
    let mut income_by_category: Vec<FinanceCategorySummary> = Vec::new();
    let mut expense_by_category: Vec<FinanceCategorySummary> = Vec::new();

    for tx in &all {
        let target = if tx.direction == "payment" {
            total_expense += tx.amount;
            &mut expense_by_category
        } else {
            total_income += tx.amount;
            &mut income_by_category
        };
        let bucket = target
            .iter_mut()
            .find(|b| b.category_id == tx.category_id);
        match bucket {
            Some(b) => b.total += tx.amount,
            None => target.push(FinanceCategorySummary {
                category_id: tx.category_id.clone(),
                direction: tx.direction.clone(),
                total: tx.amount,
            }),
        }
    }

    // Sort per-category buckets by total (descending).
    income_by_category.sort_by(|a, b| b.total.partial_cmp(&a.total).unwrap_or(std::cmp::Ordering::Equal));
    expense_by_category.sort_by(|a, b| b.total.partial_cmp(&a.total).unwrap_or(std::cmp::Ordering::Equal));

    // Budget tracking — spent = payments in the budget's period whose category
    // matches (or all payments for a global budget with category_id = NULL).
    let budget_rows = budgets::table
        .select(Budget::as_select())
        .load::<Budget>(&mut conn)
        .map_err(|e| e.to_string())?;

    let mut tracking = Vec::new();
    for b in budget_rows {
        let spent: f64 = all
            .iter()
            .filter(|tx| tx.direction == "payment")
            .filter(|tx| tx.date >= b.period_start && tx.date <= b.period_end)
            .filter(|tx| b.category_id.is_none() || tx.category_id == b.category_id.as_deref().unwrap_or(""))
            .map(|tx| tx.amount)
            .sum();
        tracking.push(BudgetTracking {
            budget_id: b.id,
            category_id: b.category_id.clone(),
            period_start: b.period_start.clone(),
            period_end: b.period_end.clone(),
            budget_amount: b.amount,
            spent,
            remaining: b.amount - spent,
            over: spent > b.amount,
        });
    }

    Ok(FinanceSummary {
        total_income,
        total_expense,
        net: total_income - total_expense,
        income_by_category,
        expense_by_category,
        budgets: tracking,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;

    fn setup_test_db() -> std::path::PathBuf {
        let dir = std::env::temp_dir().join("formint_finance_test");
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
        run_migrations(&db_path).expect("migrations should succeed");
        db_path
    }

    fn insert_tx(db_path: &PathBuf, date: &str, category_id: &str, direction: &str, amount: f64) {
        add_finance_transaction(
            db_path,
            NewFinanceTransaction {
                date: date.to_string(),
                category_id: category_id.to_string(),
                direction: direction.to_string(),
                amount,
                description: None,
                reference: None,
            },
        )
        .expect("insert should succeed");
    }

    #[test]
    fn test_finance_summary_totals_and_budget_tracking() {
        let db_path = setup_test_db();

        insert_tx(&db_path, "2026-11-01", "products", "collection", 1000.0);
        insert_tx(&db_path, "2026-11-05", "products", "collection", 500.0);
        insert_tx(&db_path, "2026-11-10", "pay_supplier", "payment", 300.0);
        insert_tx(&db_path, "2026-11-12", "employee_meal", "payment", 50.0);

        // Global budget for November + category budget for pay_supplier.
        add_budget(
            &db_path,
            NewBudget {
                category_id: None,
                period_start: "2026-11-01".into(),
                period_end: "2026-11-30".into(),
                amount: 400.0,
            },
        )
        .expect("add global budget");
        add_budget(
            &db_path,
            NewBudget {
                category_id: Some("pay_supplier".into()),
                period_start: "2026-11-01".into(),
                period_end: "2026-11-30".into(),
                amount: 200.0,
            },
        )
        .expect("add category budget");

        let summary = get_finance_summary(&db_path).expect("summary should succeed");

        assert_eq!(summary.total_income, 1500.0);
        assert_eq!(summary.total_expense, 350.0);
        assert_eq!(summary.net, 1150.0);

        // Per-category income bucket.
        assert_eq!(summary.income_by_category.len(), 1);
        assert_eq!(summary.income_by_category[0].category_id, "products");
        assert_eq!(summary.income_by_category[0].total, 1500.0);

        // Per-category expense buckets (sorted by total desc).
        assert_eq!(summary.expense_by_category.len(), 2);
        assert_eq!(summary.expense_by_category[0].category_id, "pay_supplier");

        // Global budget: spent 350 of 400 → remaining 50, not over.
        let global = summary.budgets.iter().find(|b| b.category_id.is_none()).expect("global budget");
        assert_eq!(global.spent, 350.0);
        assert_eq!(global.remaining, 50.0);
        assert!(!global.over);

        // Category budget: spent 300 of 200 → over budget.
        let cat = summary.budgets.iter().find(|b| b.category_id.as_deref() == Some("pay_supplier")).expect("cat budget");
        assert_eq!(cat.spent, 300.0);
        assert_eq!(cat.remaining, -100.0);
        assert!(cat.over);

        // Update + delete round-trips.
        let rows = get_finance_transactions(&db_path).expect("list");
        assert_eq!(rows.len(), 4);
        update_finance_transaction(
            &db_path,
            rows[0].id,
            UpdateFinanceTransaction {
                amount: Some(1200.0),
                ..Default::default()
            },
        )
        .expect("update");
        let updated = get_finance_transactions(&db_path).expect("list");
        assert!(updated.iter().any(|t| t.amount == 1200.0));

        delete_finance_transaction(&db_path, rows[1].id).expect("delete");
        assert_eq!(get_finance_transactions(&db_path).expect("list").len(), 3);
    }
}
