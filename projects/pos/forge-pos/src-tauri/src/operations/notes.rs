use crate::db::models::*;
use crate::db::schema::receipt_templates;// DB table: receipt_templates
use diesel::prelude::*;
use std::path::PathBuf;

pub fn get_notes(db_path: &PathBuf) -> Result<Vec<Note>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .select(Note::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_selectable_notes(db_path: &PathBuf) -> Result<Vec<Note>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .filter(receipt_templates::selectable.eq(true))
        .select(Note::as_select())
        .order(receipt_templates::name.asc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_default_note(db_path: &PathBuf) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .filter(receipt_templates::is_default.eq(true))
        .first(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_note(db_path: &PathBuf, template: NewNote) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(receipt_templates::table).values(&template).execute(conn)?;
        receipt_templates::table.order(receipt_templates::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_note(db_path: &PathBuf, id: i32, update: UpdateNote) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(receipt_templates::table.find(id)).set(&update).execute(conn)?;
        receipt_templates::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn get_recipe_notes(db_path: &PathBuf, recipe_id: i32) -> Result<Vec<Note>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    receipt_templates::table
        .filter(receipt_templates::recipe_id.eq(recipe_id))
        .select(Note::as_select())
        .order(receipt_templates::created_at.desc())
        .load(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_recipe_note(db_path: &PathBuf, template: NewNote) -> Result<Note, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(receipt_templates::table).values(&template).execute(conn)?;
        receipt_templates::table.order(receipt_templates::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_note(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(receipt_templates::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::run_migrations;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU32, Ordering};

    static TEST_COUNTER: AtomicU32 = AtomicU32::new(0);

    /// Create a temporary SQLite database, run migrations, return the path.
    fn setup_test_db() -> PathBuf {
        let counter = TEST_COUNTER.fetch_add(1, Ordering::SeqCst);
        let dir = std::env::temp_dir().join(format!("pos_test_notes_{}_{}", std::process::id(), counter));
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));

        run_migrations(&db_path).expect("migrations should succeed");
        db_path
    }

    #[test]
    fn test_selectable_notes_filter_and_steps_round_trip() {
        let db_path = setup_test_db();

        // Create two notes — one selectable with steps, one not selectable.
        let selectable = add_note(
            &db_path,
            NewNote {
                name: "Burger Prep".into(),
                template_body: "Prep checklist".into(),
                category: Some("preparation".into()),
                recipe_id: None,
                use_as_template: false,
                selectable: true,
                steps: Some(
                    r#"[{"title":"Toast the bun","details":"2 min"},{"title":"Grill the patty"}]"#.into(),
                ),
            },
        )
        .expect("add_note should succeed");
        assert!(selectable.selectable);
        assert!(selectable.steps.is_some());

        let _plain = add_note(
            &db_path,
            NewNote {
                name: "Thank you footer".into(),
                template_body: "Thanks!".into(),
                category: Some("receipt".into()),
                recipe_id: None,
                use_as_template: true,
                selectable: false,
                steps: None,
            },
        )
        .expect("add_note should succeed");

        // get_notes returns both; get_selectable_notes only the flagged one.
        let all = get_notes(&db_path).expect("get_notes should succeed");
        assert!(all.iter().any(|n| n.name == "Burger Prep"));
        assert!(all.iter().any(|n| n.name == "Thank you footer"));

        let selectable_list = get_selectable_notes(&db_path).expect("get_selectable_notes should succeed");
        assert_eq!(selectable_list.len(), 1);
        assert_eq!(selectable_list[0].name, "Burger Prep");
        assert_eq!(selectable_list[0].category.as_deref(), Some("preparation"));

        // Steps survive the round-trip as the exact JSON string.
        let steps = selectable_list[0].steps.as_deref().unwrap();
        assert!(steps.contains("Toast the bun"));
        assert!(steps.contains("Grill the patty"));

        // Flip selectable off → no longer returned by get_selectable_notes.
        let updated = update_note(
            &db_path,
            selectable.id,
            UpdateNote {
                name: None,
                template_body: None,
                category: None,
                recipe_id: None,
                is_default: None,
                use_as_template: None,
                selectable: Some(false),
                steps: None,
            },
        )
        .expect("update_note should succeed");
        assert!(!updated.selectable);
        assert!(get_selectable_notes(&db_path)
            .expect("get_selectable_notes should succeed")
            .is_empty());
    }
}
