use crate::db::models::*;
use crate::db::schema::user_actions;
use diesel::prelude::*;
use std::path::PathBuf;

pub fn add_user_action(db_path: &PathBuf, action: NewUserAction) -> Result<UserAction, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::insert_into(user_actions::table)
        .values(&action)
        .returning(UserAction::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_user_actions(db_path: &PathBuf, limit: Option<i64>) -> Result<Vec<UserAction>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = user_actions::table
        .order(user_actions::id.desc())
        .into_boxed();
    if let Some(n) = limit {
        query = query.limit(n);
    }
    query
        .select(UserAction::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}
