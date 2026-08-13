use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_categories(db_path: &PathBuf) -> Result<Vec<Category>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::categories::dsl::*;
    categories.load::<Category>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_category(db_path: &PathBuf, new: NewCategory) -> Result<Category, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::categories::dsl::*;
    diesel::insert_into(categories)
        .values(&new)
        .returning(Category::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_category(db_path: &PathBuf, category_id: i32, update: UpdateCategory) -> Result<Category, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::categories::dsl::*;
    diesel::update(categories.filter(id.eq(category_id)))
        .set(&update)
        .returning(Category::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn delete_category(db_path: &PathBuf, category_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::categories::dsl::*;
    diesel::delete(categories.filter(id.eq(category_id)))
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
        let dir = std::env::temp_dir().join(format!("pos_test_categories_{}_{}", std::process::id(), counter));
        let _ = std::fs::create_dir_all(&dir);
        let db_path = dir.join("test.db");
        let _ = std::fs::remove_file(&db_path);
        let _ = std::fs::remove_file(db_path.with_extension("db-wal"));
        let _ = std::fs::remove_file(db_path.with_extension("db-shm"));

        run_migrations(&db_path).expect("migrations should succeed");
        db_path
    }

    #[test]
    fn test_category_color_round_trip() {
        let db_path = setup_test_db();

        // Create with a color
        let created = add_category(
            &db_path,
            NewCategory {
                name: "Signature Burgers".into(),
                color: Some("#f97316".into()),
            },
        )
        .expect("add_category should succeed");
        assert_eq!(created.name, "Signature Burgers");
        assert_eq!(created.color.as_deref(), Some("#f97316"));

        // Backend returns it in the list with the color intact
        let all = get_categories(&db_path).expect("get_categories should succeed");
        assert!(all.iter().any(|c| c.id == created.id && c.color.as_deref() == Some("#f97316")));

        // Update the color
        let updated = update_category(
            &db_path,
            created.id,
            UpdateCategory {
                name: Some("Burgers".into()),
                color: Some(Some("#06b6d4".into())),
            },
        )
        .expect("update_category should succeed");
        assert_eq!(updated.name, "Burgers");
        assert_eq!(updated.color.as_deref(), Some("#06b6d4"));

        // Clear the color to NULL
        let cleared = update_category(
            &db_path,
            created.id,
            UpdateCategory {
                name: None,
                color: Some(None),
            },
        )
        .expect("clearing color should succeed");
        assert_eq!(cleared.color, None);

        // Delete
        delete_category(&db_path, created.id).expect("delete_category should succeed");
        let remaining = get_categories(&db_path).expect("get_categories should succeed");
        assert!(!remaining.iter().any(|c| c.id == created.id));
    }
}
