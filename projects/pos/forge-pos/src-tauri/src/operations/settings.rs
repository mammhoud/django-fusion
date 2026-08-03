use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_settings(db_path: &PathBuf) -> Result<Settings, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::settings::dsl::*;
    let s = settings.find(1)
        .first::<Settings>(&mut conn)
        .map_err(|e| e.to_string())?;

    // Trace: log logo presence + size (truncated to prevent log spam)
    match &s.logo {
        Some(data) => {
            let len = data.len();
            let preview = if len > 80 {
                format!("{}…", &data[..80])
            } else {
                data.clone()
            };
            eprintln!("[settings] get_settings: logo present ({} chars). preview={}", len, preview);
        }
        None => {
            eprintln!("[settings] get_settings: logo is NULL");
        }
    }

    Ok(s)
}

pub fn save_settings(db_path: &PathBuf, update: UpdateSettings) -> Result<Settings, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::settings::dsl::*;

    // Trace: log incoming logo state
    // update.logo is Option<Option<String>> for Diesel AsChangeset semantics:
    //   None             → skip field (no DB change)
    //   Some(None)       → SET column to NULL
    //   Some(Some(data)) → SET column to the given string
    match &update.logo {
        Some(Some(data)) => {
            eprintln!("[settings] save_settings: logo set to {} chars", data.len());
        }
        Some(None) => {
            eprintln!("[settings] save_settings: logo explicitly cleared (SET NULL)");
        }
        None => {
            eprintln!("[settings] save_settings: logo not in payload (skipped)");
        }
    }

    diesel::update(settings.filter(id.eq(1)))
        .set(&update)
        .returning(Settings::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::env;
    use std::path::PathBuf;

    use std::sync::atomic::{AtomicU32, Ordering};
    static TEST_COUNTER: AtomicU32 = AtomicU32::new(0);

    /// Create a temporary SQLite database, run migrations, return the path.
    fn setup_test_db() -> PathBuf {
        let counter = TEST_COUNTER.fetch_add(1, Ordering::SeqCst);
        let dir = std::env::temp_dir().join(format!("pos_test_settings_{}_{}", std::process::id(), counter));
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        // Remove if exists from a previous interrupted run
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));

        run_migrations(&db_path).expect("migrations should succeed");

        // Ensure settings row 1 exists, then reset logo to NULL for clean test state
        let mut conn = open_conn(&db_path).unwrap();
        use crate::db::schema::settings::dsl::*;
        let count: i64 = settings.count().get_result(&mut conn).unwrap();
        if count == 0 {
            diesel::insert_into(settings)
                .values((id.eq(1), restaurant_name.eq("Forge POS"), currency.eq("USD")))
                .execute(&mut conn)
                .unwrap();
        }
        // Migrations may seed a logo (e.g. coffee shop preset). Reset to NULL
        // so each test starts with a clean, predictable initial state.
        diesel::update(settings.find(1))
            .set(logo.eq(None::<String>))
            .execute(&mut conn)
            .unwrap();

        eprintln!("[test] test DB at: {}", db_path.display());
        db_path
    }

    fn get_logo(db_path: &PathBuf) -> Option<String> {
        let mut conn = open_conn(db_path).unwrap();
        use crate::db::schema::settings::dsl::*;
        settings.find(1)
            .select(logo)
            .first::<Option<String>>(&mut conn)
            .unwrap()
    }

    #[test]
    fn test_logo_set_and_retrieve() {
        let db_path = setup_test_db();

        // Initially logo should be NULL
        assert_eq!(get_logo(&db_path), None, "initial logo should be NULL");

        // Set a logo
        let test_logo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA=".to_string();
        let update = UpdateSettings {
            restaurant_name: None,
            address: None,
            phone: None,
            email: None,
            tax_rate: None,
            tax_id: None,
            currency: None,
            opening_time: None,
            closing_time: None,
            receipt_footer: None,
            logo: Some(Some(test_logo.clone())),
            invoice_logo: None,
            dine_in_tables: None,
            delivery_fee: None,
            delivery_fee_per_km: None,
            smtp_server: None,
            smtp_port: None,
            smtp_username: None,
            smtp_password: None,
            smtp_recipient: None,
            smtp_from_name: None,
            smtp_from_email: None,
        };

        let result = save_settings(&db_path, update).expect("save_settings should succeed");
        assert_eq!(result.logo, Some(test_logo.clone()), "logo should be stored");

        // Verify via direct query
        let stored = get_logo(&db_path);
        assert_eq!(stored, Some(test_logo), "direct query should confirm logo");
    }

    #[test]
    fn test_logo_clear_to_null() {
        let db_path = setup_test_db();

        // First set a logo
        let test_logo = "data:image/png;base64,logo_data_here".to_string();
        save_settings(&db_path, UpdateSettings {
            logo: Some(Some(test_logo)),
            ..Default::default()
        }).expect("set logo should succeed");
        assert!(get_logo(&db_path).is_some(), "logo should be present after set");

        // Now clear it — send Some(None)
        save_settings(&db_path, UpdateSettings {
            logo: Some(None),
            ..Default::default()
        }).expect("clear logo should succeed");

        let stored = get_logo(&db_path);
        assert_eq!(stored, None, "logo should be NULL after clear");
    }

    #[test]
    fn test_logo_skip_preserves_value() {
        let db_path = setup_test_db();

        // First set a logo
        let test_logo = "data:image/png;base64,preserve_me".to_string();
        save_settings(&db_path, UpdateSettings {
            logo: Some(Some(test_logo.clone())),
            ..Default::default()
        }).expect("set logo should succeed");

        // Now save without touching logo (logo: None = skip field)
        save_settings(&db_path, UpdateSettings {
            restaurant_name: Some("New Name".to_string()),
            logo: None,  // ← skip field
            ..Default::default()
        }).expect("save with skip should succeed");

        let stored = get_logo(&db_path);
        assert_eq!(stored, Some(test_logo), "logo should be preserved when skipped");

        // Also verify restaurant_name was updated
        let mut conn = open_conn(&db_path).unwrap();
        use crate::db::schema::settings::dsl::*;
        let name: Option<String> = settings.find(1)
            .select(restaurant_name)
            .first(&mut conn)
            .unwrap();
        assert_eq!(name, Some("New Name".to_string()));
    }

    #[test]
    fn test_logo_replace_with_new_value() {
        let db_path = setup_test_db();

        // Set first logo
        save_settings(&db_path, UpdateSettings {
            logo: Some(Some("logo_v1".to_string())),
            ..Default::default()
        }).expect("set logo v1");

        // Replace with new logo
        save_settings(&db_path, UpdateSettings {
            logo: Some(Some("logo_v2_replacement".to_string())),
            ..Default::default()
        }).expect("set logo v2");

        let stored = get_logo(&db_path);
        assert_eq!(stored, Some("logo_v2_replacement".to_string()), "logo should be replaced");
    }


    #[test]
    fn test_smtp_settings_round_trip() {
        let db_path = setup_test_db();

        // Save SMTP settings via UpdateSettings (the same path the UI uses)
        save_settings(&db_path, UpdateSettings {
            smtp_server: Some("smtp.example.com".to_string()),
            smtp_port: Some(2525),
            smtp_username: Some("user@example.com".to_string()),
            smtp_password: Some("hunter2".to_string()),
            smtp_recipient: Some("support@example.com".to_string()),
            smtp_from_name: Some("My Restaurant".to_string()),
            smtp_from_email: Some("no-reply@example.com".to_string()),
            ..Default::default()
        }).expect("save SMTP settings should succeed");

        // load_smtp_config must return the DB values (DB wins over env/defaults)
        let cfg = crate::email::load_smtp_config(&db_path);
        assert_eq!(cfg.server, "smtp.example.com");
        assert_eq!(cfg.port, 2525);
        assert_eq!(cfg.username, "user@example.com");
        assert_eq!(cfg.password, "hunter2");
        assert_eq!(cfg.recipient, "support@example.com");
        assert_eq!(cfg.from_name, "My Restaurant");
        assert_eq!(cfg.from_email, "no-reply@example.com");
        assert!(cfg.is_configured(), "credentials present → configured");
        assert!(cfg.has_recipient(), "recipient present → has_recipient");
    }

    #[test]
    fn test_smtp_empty_db_falls_back_to_env_defaults() {
        // Deterministic: set known env values for fields that no other test
        // module mutates (auth.rs tests touch only SMTP_USERNAME/SMTP_PASSWORD).
        // With an empty settings row, load_smtp_config must use these values.
        env::set_var("SMTP_SERVER", "smtp.test-env.com");
        env::set_var("SMTP_PORT", "2525");
        env::set_var("SMTP_FROM_NAME", "Env Sender");
        env::set_var("SMTP_FROM_EMAIL", "env@test-env.com");

        let db_path = setup_test_db();

        // Nothing saved → env values apply
        let cfg = crate::email::load_smtp_config(&db_path);
        assert_eq!(cfg.server, "smtp.test-env.com");
        assert_eq!(cfg.port, 2525);
        assert_eq!(cfg.from_name, "Env Sender");
        assert_eq!(cfg.from_email, "env@test-env.com");

        // Clean up so we don't leak env into other tests in this process
        env::remove_var("SMTP_SERVER");
        env::remove_var("SMTP_PORT");
        env::remove_var("SMTP_FROM_NAME");
        env::remove_var("SMTP_FROM_EMAIL");
    }

    #[test]
    fn test_logo_full_flow_set_clear_set() {
        // Full end-to-end: set -> verify -> clear -> verify -> set again -> verify
        let db_path = setup_test_db();

        // 1. Initial: NULL
        assert_eq!(get_logo(&db_path), None, "step 1: initially NULL");

        // 2. Set logo
        let logo_a = "data:image/png;base64,AAAA".to_string();
        let result = save_settings(&db_path, UpdateSettings {
            logo: Some(Some(logo_a.clone())),
            ..Default::default()
        }).expect("set logo A");
        assert_eq!(result.logo, Some(logo_a.clone()), "step 2: logo A stored");

        // 3. Clear logo
        let result = save_settings(&db_path, UpdateSettings {
            logo: Some(None),
            ..Default::default()
        }).expect("clear logo");
        assert_eq!(result.logo, None, "step 3: logo cleared to NULL");

        // 4. Set another logo
        let logo_b = "data:image/png;base64,BBBB".to_string();
        let result = save_settings(&db_path, UpdateSettings {
            logo: Some(Some(logo_b.clone())),
            ..Default::default()
        }).expect("set logo B");
        assert_eq!(result.logo, Some(logo_b.clone()), "step 4: logo B stored");

        // 5. Final direct verification
        assert_eq!(get_logo(&db_path), Some(logo_b), "step 5: direct query confirms logo B");
    }
} // mod tests
