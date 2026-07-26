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
