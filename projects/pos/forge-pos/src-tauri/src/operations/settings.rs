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
