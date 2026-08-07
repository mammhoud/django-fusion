use crate::db::models::*;
use crate::db::schema::support_messages;
use diesel::prelude::*;
use std::path::PathBuf;

/// List all support messages, newest first.
pub fn get_support_messages(db_path: &PathBuf) -> Result<Vec<SupportMessage>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    support_messages::table
        .select(SupportMessage::as_select())
        .order(support_messages::created_at.desc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

/// Insert a new support message (contact/ticket submission).
pub fn add_support_message(
    db_path: &PathBuf,
    message: NewSupportMessage,
) -> Result<SupportMessage, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(support_messages::table)
            .values(&message)
            .execute(conn)?;
        support_messages::table
            .order(support_messages::id.desc())
            .first(conn)
    })
    .map_err(|e| e.to_string())
}

/// Update a support message's status/priority (workflow state).
pub fn update_support_message(
    db_path: &PathBuf,
    id: i32,
    update: UpdateSupportMessage,
) -> Result<SupportMessage, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(support_messages::table.find(id))
            .set(&update)
            .execute(conn)?;
        support_messages::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

/// Delete a support message.
pub fn delete_support_message(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(support_messages::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::sync::atomic::{AtomicU32, Ordering};

    static TEST_COUNTER: AtomicU32 = AtomicU32::new(0);

    fn setup_test_db() -> PathBuf {
        let counter = TEST_COUNTER.fetch_add(1, Ordering::SeqCst);
        let dir = std::env::temp_dir().join(format!(
            "pos_test_support_{}_{}",
            std::process::id(),
            counter
        ));
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));
        run_migrations(&db_path).expect("migrations should succeed");
        db_path
    }

    #[test]
    fn test_support_message_round_trip() {
        let db_path = setup_test_db();

        let created = add_support_message(
            &db_path,
            NewSupportMessage {
                name: "Sara".into(),
                email: "sara@example.com".into(),
                phone: Some("+20 100 000 0000".into()),
                subject: Some("Billing question".into()),
                category: Some("billing".into()),
                priority: "high".into(),
                message: "My invoice total looks wrong.".into(),
                status: "new".into(),
            },
        )
        .expect("add should succeed");

        assert_eq!(created.name, "Sara");
        assert_eq!(created.status, "new");
        assert_eq!(created.priority, "high");

        // Update workflow state
        let updated = update_support_message(
            &db_path,
            created.id,
            UpdateSupportMessage {
                status: Some("resolved".into()),
                priority: None,
            },
        )
        .expect("update should succeed");
        assert_eq!(updated.status, "resolved");

        // List — newest first
        let all = get_support_messages(&db_path).expect("list should succeed");
        assert_eq!(all.len(), 1);
        assert_eq!(all[0].status, "resolved");

        // Delete
        delete_support_message(&db_path, created.id).expect("delete should succeed");
        assert!(get_support_messages(&db_path).unwrap().is_empty());
    }
}
