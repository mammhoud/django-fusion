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

/// Returns user actions filtered by entity type + id (e.g. the audit trail
/// for one employee), newest first, with an optional row limit.
pub fn get_user_actions_for_entity(
    db_path: &PathBuf,
    entity_type: &str,
    entity_id: i32,
    limit: Option<i64>,
) -> Result<Vec<UserAction>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = user_actions::table
        .filter(user_actions::entity_type.eq(entity_type))
        .filter(user_actions::entity_id.eq(entity_id))
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;

    fn setup_test_db() -> std::path::PathBuf {
        let dir = std::env::temp_dir().join("formint_user_actions_test");
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
        run_migrations(&db_path).expect("migrations should succeed");
        db_path
    }

    fn insert_action(db_path: &PathBuf, action: &str, entity_type: &str, entity_id: i32) -> UserAction {
        add_user_action(
            db_path,
            NewUserAction {
                action: action.to_string(),
                entity_type: Some(entity_type.to_string()),
                entity_id: Some(entity_id),
                details: Some("{}".to_string()),
                user_id: None,
            },
        )
        .expect("add_user_action should succeed")
    }

    #[test]
    fn test_entity_filter_returns_only_matching_actions() {
        let db_path = setup_test_db();

        insert_action(&db_path, "add_employee", "employee", 1);
        insert_action(&db_path, "update_employee", "employee", 1);
        insert_action(&db_path, "deactivate_employee", "employee", 2);

        let emp1 = get_user_actions_for_entity(&db_path, "employee", 1, None).expect("query should succeed");
        assert_eq!(emp1.len(), 2, "employee 1 has exactly two actions");
        assert!(emp1.iter().all(|a| a.entity_id == Some(1)));

        let emp2 = get_user_actions_for_entity(&db_path, "employee", 2, None).expect("query should succeed");
        assert_eq!(emp2.len(), 1);
        assert_eq!(emp2[0].action, "deactivate_employee");

        // Newest first ordering.
        assert_eq!(emp1[0].action, "update_employee");
        assert_eq!(emp1[1].action, "add_employee");

        // Limit clamps the result set.
        let limited = get_user_actions_for_entity(&db_path, "employee", 1, Some(1)).expect("query should succeed");
        assert_eq!(limited.len(), 1);
        assert_eq!(limited[0].action, "update_employee");
    }
}
