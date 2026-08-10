use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_ingredients(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<Ingredient>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::ingredients::dsl::*;
    let mut query = ingredients.into_boxed();
    if !include_inactive {
        query = query.filter(is_active.eq(true));
    }
    query.order(id.asc())
        .load::<Ingredient>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_ingredient(db_path: &PathBuf, new: NewIngredient) -> Result<Ingredient, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::ingredients::dsl::*;
    diesel::insert_into(ingredients)
        .values(&new)
        .returning(Ingredient::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_ingredient(db_path: &PathBuf, ingredient_id: i32, update: UpdateIngredient) -> Result<Ingredient, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::ingredients::dsl::*;
    diesel::update(ingredients.filter(id.eq(ingredient_id)))
        .set(&update)
        .returning(Ingredient::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn soft_delete_ingredient(db_path: &PathBuf, ingredient_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::ingredients::dsl::*;
    diesel::update(ingredients.filter(id.eq(ingredient_id)))
        .set(is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn mark_ingredient_uploaded(db_path: &PathBuf, ingredient_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::ingredients::dsl::*;
    diesel::update(ingredients.filter(id.eq(ingredient_id)))
        .set(uploaded.eq(true))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
