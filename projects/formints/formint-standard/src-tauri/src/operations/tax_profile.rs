use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

fn validate_name(value: &str) -> Result<(), String> {
    if value.trim().is_empty() {
        return Err("tax profile name cannot be empty".to_string());
    }
    Ok(())
}

fn validate_rate(rate: f64) -> Result<(), String> {
    if !rate.is_finite() || rate < 0.0 {
        return Err("tax rate must be a non-negative finite number".to_string());
    }
    Ok(())
}

/// List tax profiles with active/default entries first, then name.
pub fn list_tax_profiles(
    db_path: &PathBuf,
    active_only: bool,
    search: Option<&str>,
) -> Result<Vec<TaxProfile>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::tax_profiles::dsl::*;

    let mut query = tax_profiles.into_boxed();
    if active_only {
        query = query.filter(is_active.eq(true));
    }
    if let Some(search) = search.map(str::trim).filter(|value| !value.is_empty()) {
        let pattern = format!("%{search}%");
        query = query.filter(name.like(pattern));
    }

    query
        .order((is_active.desc(), is_default.desc(), name.asc()))
        .select(TaxProfile::as_select())
        .load(&mut conn)
        .map_err(|error| format!("list tax profiles: {error}"))
}

pub fn get_tax_profile(db_path: &PathBuf, profile_id: i32) -> Result<TaxProfile, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::tax_profiles::dsl::*;
    tax_profiles
        .find(profile_id)
        .select(TaxProfile::as_select())
        .first(&mut conn)
        .map_err(|error| format!("get tax profile {profile_id}: {error}"))
}

pub fn create_tax_profile(
    db_path: &PathBuf,
    name_value: &str,
    rate_value: f64,
    default_value: bool,
) -> Result<TaxProfile, String> {
    let name_value = name_value.trim();
    validate_name(name_value)?;
    validate_rate(rate_value)?;

    let mut conn = open_conn(db_path)?;
    conn.transaction::<TaxProfile, diesel::result::Error, _>(|connection| {
        use crate::db::schema::tax_profiles::dsl::*;
        let has_default: bool = tax_profiles
            .filter(is_default.eq(true))
            .filter(is_active.eq(true))
            .select(id)
            .first::<i32>(connection)
            .optional()?
            .is_some();
        let should_be_default = default_value || !has_default;
        if should_be_default {
            diesel::update(tax_profiles.filter(is_default.eq(true)))
                .set(is_default.eq(false))
                .execute(connection)?;
        }

        diesel::insert_into(tax_profiles)
            .values(NewTaxProfile {
                name: name_value.to_string(),
                rate: rate_value,
                is_default: should_be_default,
                is_active: true,
            })
            .returning(TaxProfile::as_returning())
            .get_result(connection)
    })
    .map_err(|error| format!("create tax profile: {error}"))
}

pub fn update_tax_profile(
    db_path: &PathBuf,
    profile_id: i32,
    name_value: Option<&str>,
    rate_value: Option<f64>,
    default_value: Option<bool>,
    active_value: Option<bool>,
) -> Result<TaxProfile, String> {
    let name_value = match name_value {
        Some(value) if value.trim().is_empty() => {
            return Err("tax profile name cannot be empty".to_string());
        }
        Some(value) => Some(value.trim().to_string()),
        None => None,
    };
    if let Some(rate) = rate_value {
        validate_rate(rate)?;
    }
    if active_value == Some(false) && default_value == Some(true) {
        return Err("an inactive tax profile cannot be the default".to_string());
    }
    let effective_default = if active_value == Some(false) {
        Some(false)
    } else {
        default_value
    };

    let mut conn = open_conn(db_path)?;
    conn.transaction::<TaxProfile, diesel::result::Error, _>(|connection| {
        use crate::db::schema::tax_profiles::dsl::*;
        let current: TaxProfile = tax_profiles
            .find(profile_id)
            .select(TaxProfile::as_select())
            .first(connection)?;
        let has_active_default: bool = tax_profiles
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
            let replacement_exists: bool = tax_profiles
                .filter(is_default.eq(true))
                .filter(is_active.eq(true))
                .filter(id.ne(profile_id))
                .select(id)
                .first::<i32>(connection)
                .optional()?
                .is_some();
            if !replacement_exists {
                return Err(diesel::result::Error::RollbackTransaction);
            }
        }
        if effective_default == Some(true) {
            diesel::update(tax_profiles.filter(is_default.eq(true)))
                .set(is_default.eq(false))
                .execute(connection)?;
        }

        let update = UpdateTaxProfile {
            name: name_value,
            rate: rate_value,
            is_default: effective_default,
            is_active: active_value,
        };
        diesel::update(tax_profiles.find(profile_id))
            .set(update)
            .returning(TaxProfile::as_returning())
            .get_result(connection)
    })
    .map_err(|error| {
        if matches!(error, diesel::result::Error::RollbackTransaction) {
            "cannot remove the only active default tax profile".to_string()
        } else {
            format!("update tax profile {profile_id}: {error}")
        }
    })
}

/// Soft-delete a tax profile. The active default cannot be removed while it is
/// the only default profile left in the catalogue.
pub fn delete_tax_profile(db_path: &PathBuf, profile_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    conn.transaction::<(), diesel::result::Error, _>(|connection| {
        use crate::db::schema::tax_profiles::dsl::*;
        let current: TaxProfile = tax_profiles
            .find(profile_id)
            .select(TaxProfile::as_select())
            .first(connection)?;
        if current.is_default {
            let others: bool = tax_profiles
                .filter(is_default.eq(true))
                .filter(is_active.eq(true))
                .filter(id.ne(profile_id))
                .select(id)
                .first::<i32>(connection)
                .optional()?
                .is_some();
            if !others {
                return Err(diesel::result::Error::RollbackTransaction);
            }
        }
        diesel::update(tax_profiles.find(profile_id))
            .set((is_active.eq(false), is_default.eq(false)))
            .execute(connection)?;
        Ok(())
    })
    .map_err(|error| {
        if matches!(error, diesel::result::Error::RollbackTransaction) {
            "cannot delete the only default tax profile".to_string()
        } else {
            format!("delete tax profile {profile_id}: {error}")
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::path::PathBuf;

    fn temp_db(tag: &str) -> PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "formint-standard-tax-profile-{}-{}.db",
            std::process::id(),
            tag
        ));
        let _ = std::fs::remove_file(&path);
        run_migrations(&path).expect("migrations ok");
        path
    }

    #[test]
    fn list_tax_profiles_returns_empty_initially() {
        let db = temp_db("list");
        let result = list_tax_profiles(&db, true, None).expect("list ok");
        assert!(result.is_empty());
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn create_and_set_default() {
        let db = temp_db("default");
        let standard = create_tax_profile(&db, "Standard", 0.15, true).expect("create");
        assert!(standard.is_default);
        assert_eq!(standard.rate, 0.15);
        let reduced = create_tax_profile(&db, "Reduced", 0.07, true).expect("create");
        // Single-default enforcement: Standard should no longer be default
        let refreshed = get_tax_profile(&db, standard.id).expect("get");
        assert!(!refreshed.is_default);
        assert!(reduced.is_default);
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn delete_rejects_last_default() {
        let db = temp_db("delete_def");
        let std = create_tax_profile(&db, "Standard", 0.15, true).expect("create");
        let err = delete_tax_profile(&db, std.id).expect_err("should reject");
        assert!(err.contains("cannot delete the only default tax profile"));
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn search_by_name() {
        let db = temp_db("search");
        create_tax_profile(&db, "Standard", 0.15, true).expect("create");
        create_tax_profile(&db, "Zero-rated", 0.0, false).expect("create");
        let results = list_tax_profiles(&db, false, Some("zero")).expect("search");
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].name, "Zero-rated");
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn update_cannot_make_inactive_default() {
        let db = temp_db("inactive_def");
        let standard = create_tax_profile(&db, "Standard", 0.15, true).expect("create");
        let reduced = create_tax_profile(&db, "Reduced", 0.07, false).expect("create");
        // Make reduced the default first, then deactivate standard.
        let _ = update_tax_profile(&db, reduced.id, None, None, Some(true), None).expect("set default");
        let updated = update_tax_profile(&db, standard.id, None, None, None, Some(false)).expect("deactivate");
        assert!(!updated.is_active);
        let _ = std::fs::remove_file(&db);
    }
}
