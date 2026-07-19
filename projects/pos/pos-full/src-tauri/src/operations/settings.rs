use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use crate::operations::signals::{self, ChangeEvent};
use std::path::PathBuf;

pub fn get_settings(db_path: &PathBuf) -> Result<Settings, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::settings::dsl::*;
    settings.find(1)
        .first::<Settings>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn save_settings(db_path: &PathBuf, update: UpdateSettings) -> Result<Settings, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::settings::dsl::*;
    let result = diesel::update(settings.filter(id.eq(1)))
        .set(&update)
        .returning(Settings::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::SettingsChanged);
    Ok(result)
}
