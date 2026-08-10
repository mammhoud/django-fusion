use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

fn normalize_code(code: &str) -> Result<String, String> {
    let normalized = code.trim().to_ascii_uppercase();
    if normalized.len() != 3 || !normalized.chars().all(|character| character.is_ascii_alphabetic()) {
        return Err("currency code must be exactly three ASCII letters".to_string());
    }
    Ok(normalized)
}

fn validate_exchange_rate(exchange_rate: f64) -> Result<(), String> {
    if !exchange_rate.is_finite() || exchange_rate <= 0.0 {
        return Err("exchange rate must be a finite positive number".to_string());
    }
    Ok(())
}

/// List currencies with active/default entries first, then ISO code.
pub fn list_currencies(
    db_path: &PathBuf,
    active_only: bool,
    search: Option<&str>,
) -> Result<Vec<Currency>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::currencies::dsl::*;

    let mut query = currencies.into_boxed();
    if active_only {
        query = query.filter(is_active.eq(true));
    }
    if let Some(search) = search.map(str::trim).filter(|value| !value.is_empty()) {
        let pattern = format!("%{search}%");
        query = query.filter(code.like(pattern.clone()).or(name.like(pattern)));
    }

    query
        .order((is_active.desc(), is_default.desc(), code.asc()))
        .select(Currency::as_select())
        .load(&mut conn)
        .map_err(|error| format!("list currencies: {error}"))
}

pub fn get_currency(db_path: &PathBuf, currency_id: i32) -> Result<Currency, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::currencies::dsl::*;
    currencies
        .find(currency_id)
        .select(Currency::as_select())
        .first(&mut conn)
        .map_err(|error| format!("get currency {currency_id}: {error}"))
}

pub fn create_currency(
    db_path: &PathBuf,
    code_value: &str,
    name_value: &str,
    symbol_value: &str,
    exchange_rate_value: f64,
    default_value: bool,
) -> Result<Currency, String> {
    let code_value = normalize_code(code_value)?;
    let name_value = name_value.trim();
    if name_value.is_empty() {
        return Err("currency name cannot be empty".to_string());
    }
    validate_exchange_rate(exchange_rate_value)?;

    let mut conn = open_conn(db_path)?;
    conn.transaction::<Currency, diesel::result::Error, _>(|connection| {
        use crate::db::schema::currencies::dsl::*;
        let has_default: bool = currencies
            .filter(is_default.eq(true))
            .filter(is_active.eq(true))
            .select(id)
            .first::<i32>(connection)
            .optional()?
            .is_some();
        let should_be_default = default_value || !has_default;
        if should_be_default {
            diesel::update(currencies.filter(is_default.eq(true)))
                .set(is_default.eq(false))
                .execute(connection)?;
        }

        diesel::insert_into(currencies)
            .values(NewCurrency {
                code: code_value,
                name: name_value.to_string(),
                symbol: symbol_value.trim().to_string(),
                exchange_rate: exchange_rate_value,
                is_default: should_be_default,
                is_active: true,
            })
            .returning(Currency::as_returning())
            .get_result(connection)
    })
    .map_err(|error| format!("create currency: {error}"))
}

pub fn update_currency(
    db_path: &PathBuf,
    currency_id: i32,
    code_value: Option<&str>,
    name_value: Option<&str>,
    symbol_value: Option<&str>,
    exchange_rate_value: Option<f64>,
    default_value: Option<bool>,
    active_value: Option<bool>,
) -> Result<Currency, String> {
    let code_value = code_value.map(normalize_code).transpose()?;
    let name_value = match name_value {
        Some(value) if value.trim().is_empty() => {
            return Err("currency name cannot be empty".to_string());
        }
        Some(value) => Some(value.trim().to_string()),
        None => None,
    };
    if let Some(rate) = exchange_rate_value {
        validate_exchange_rate(rate)?;
    }
    if active_value == Some(false) && default_value == Some(true) {
        return Err("an inactive currency cannot be the default".to_string());
    }
    let effective_default = if active_value == Some(false) {
        Some(false)
    } else {
        default_value
    };

    let mut conn = open_conn(db_path)?;
    conn.transaction::<Currency, diesel::result::Error, _>(|connection| {
        use crate::db::schema::currencies::dsl::*;
        let current: Currency = currencies
            .find(currency_id)
            .select(Currency::as_select())
            .first(connection)?;
        let has_active_default: bool = currencies
            .filter(is_default.eq(true))
            .filter(is_active.eq(true))
            .select(id)
            .first::<i32>(connection)
            .optional()?
            .is_some();
        let effective_default = if !has_active_default {
            if effective_default == Some(false) {
                return Err(diesel::result::Error::RollbackTransaction);
            }
            if !current.is_active && active_value != Some(true) {
                return Err(diesel::result::Error::RollbackTransaction);
            }
            Some(true)
        } else {
            effective_default
        };
        let would_remove_default = current.is_default && effective_default == Some(false);
        if would_remove_default {
            let replacement_exists: bool = currencies
                .filter(is_default.eq(true))
                .filter(is_active.eq(true))
                .filter(id.ne(currency_id))
                .select(id)
                .first::<i32>(connection)
                .optional()?
                .is_some();
            if !replacement_exists {
                return Err(diesel::result::Error::RollbackTransaction);
            }
        }
        if effective_default == Some(true) {
            diesel::update(currencies.filter(is_default.eq(true)))
                .set(is_default.eq(false))
                .execute(connection)?;
        }

        let update = UpdateCurrency {
            code: code_value,
            name: name_value,
            symbol: symbol_value.map(|value| value.trim().to_string()),
            exchange_rate: exchange_rate_value,
            is_default: effective_default,
            is_active: active_value,
        };
        diesel::update(currencies.find(currency_id))
            .set(update)
            .returning(Currency::as_returning())
            .get_result(connection)
    })
    .map_err(|error| {
        if matches!(error, diesel::result::Error::RollbackTransaction) {
            "cannot remove the only active default currency".to_string()
        } else {
            format!("update currency {currency_id}: {error}")
        }
    })
}

/// Soft-delete a currency. The active default cannot be removed while it is
/// the only default currency left in the catalogue.
pub fn delete_currency(db_path: &PathBuf, currency_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    conn.transaction::<(), diesel::result::Error, _>(|connection| {
        use crate::db::schema::currencies::dsl::*;
        let currency: Currency = currencies
            .find(currency_id)
            .select(Currency::as_select())
            .first(connection)?;

        if currency.is_default {
            let other_default_exists: bool = currencies
                .filter(is_default.eq(true))
                .filter(is_active.eq(true))
                .filter(id.ne(currency_id))
                .select(id)
                .first::<i32>(connection)
                .optional()?
                .is_some();
            if !other_default_exists {
                return Err(diesel::result::Error::RollbackTransaction);
            }
        }

        diesel::update(currencies.find(currency_id))
            .set((is_active.eq(false), is_default.eq(false)))
            .execute(connection)?;
        Ok(())
    })
    .map_err(|error| {
        if matches!(error, diesel::result::Error::RollbackTransaction) {
            "cannot delete the only default currency".to_string()
        } else {
            format!("delete currency {currency_id}: {error}")
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::sync::atomic::{AtomicU32, Ordering};

    static TEST_COUNTER: AtomicU32 = AtomicU32::new(0);

    fn temp_db(tag: &str) -> PathBuf {
        let counter = TEST_COUNTER.fetch_add(1, Ordering::SeqCst);
        let directory = std::env::temp_dir().join(format!(
            "formint-standard-currency-{}-{}-{}",
            std::process::id(), tag, counter
        ));
        let _ = std::fs::create_dir_all(&directory);
        let path = directory.join("test.db");
        let _ = std::fs::remove_file(&path);
        run_migrations(&path).expect("migrations should succeed");
        path
    }

    #[test]
    fn list_currencies_returns_empty_initially() {
        let db = temp_db("list");
        assert!(list_currencies(&db, true, None).expect("list should succeed").is_empty());
    }

    #[test]
    fn create_normalizes_code_and_enforces_single_default() {
        let db = temp_db("default");
        let usd = create_currency(&db, " usd ", "US Dollar", "$", 1.0, false).expect("create USD");
        assert_eq!(usd.code, "USD");
        assert!(usd.is_default);

        let eur = create_currency(&db, "EUR", "Euro", "€", 0.92, true).expect("create EUR");
        assert!(eur.is_default);
        assert!(!get_currency(&db, usd.id).expect("get USD").is_default);
    }

    #[test]
    fn search_orders_active_default_and_matches_code_or_name() {
        let db = temp_db("search");
        create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create USD");
        create_currency(&db, "EUR", "Euro", "€", 0.92, false).expect("create EUR");
        let results = list_currencies(&db, true, Some("euro")).expect("search should succeed");
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].code, "EUR");
    }

    #[test]
    fn delete_rejects_only_default_and_soft_deletes_when_replaced() {
        let db = temp_db("delete");
        let usd = create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create USD");
        assert_eq!(delete_currency(&db, usd.id).expect_err("must protect default"), "cannot delete the only default currency");

        let eur = create_currency(&db, "EUR", "Euro", "€", 0.92, true).expect("create EUR");
        delete_currency(&db, usd.id).expect("old default should soft-delete");
        assert!(!get_currency(&db, usd.id).expect("get USD").is_active);
        assert!(get_currency(&db, eur.id).expect("get EUR").is_default);
    }

    #[test]
    fn update_rejects_removing_only_active_default() {
        let db = temp_db("update-default");
        let usd = create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create USD");
        let err = update_currency(&db, usd.id, None, None, None, None, Some(false), None)
            .expect_err("must protect the only default");
        assert_eq!(err, "cannot remove the only active default currency");
        let unchanged = get_currency(&db, usd.id).expect("get USD");
        assert!(unchanged.is_active);
        assert!(unchanged.is_default);
    }

    #[test]
    fn reactivating_non_default_currency_preserves_existing_default() {
        let db = temp_db("reactivate-existing-default");
        let usd = create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create USD");
        let eur = create_currency(&db, "EUR", "Euro", "€", 0.92, false).expect("create EUR");
        update_currency(&db, eur.id, None, None, None, None, None, Some(false))
            .expect("deactivate EUR");
        let restored = update_currency(&db, eur.id, None, None, None, None, None, Some(true))
            .expect("reactivate EUR");
        assert_ne!(usd.id, restored.id);
        assert!(!restored.is_default);
        assert!(get_currency(&db, usd.id).expect("get USD").is_default);
    }

    #[test]
    fn reactivating_currency_restores_missing_default() {
        let db = temp_db("reactivate-default");
        let usd = create_currency(&db, "USD", "US Dollar", "$", 1.0, true).expect("create USD");
        let eur = create_currency(&db, "EUR", "Euro", "€", 0.92, true).expect("create EUR");

        // Simulate a legacy database with no active default. Normal writes
        // cannot create this state because the operation layer protects it.
        let mut conn = open_conn(&db).expect("open database");
        diesel::sql_query("UPDATE currencies SET is_default = 0 WHERE id = ?")
            .bind::<diesel::sql_types::Integer, _>(eur.id)
            .execute(&mut conn)
            .expect("clear default");
        drop(conn);

        let restored = update_currency(&db, usd.id, None, None, None, None, None, Some(true))
            .expect("reactivation should restore a default");
        assert!(restored.is_default);
    }
}
