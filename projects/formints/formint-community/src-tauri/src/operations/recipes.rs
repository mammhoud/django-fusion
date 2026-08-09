use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use std::path::PathBuf;

pub fn get_recipes(db_path: &PathBuf, include_inactive: bool) -> Result<Vec<Recipe>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipes::dsl::*;
    let mut query = recipes.into_boxed();
    if !include_inactive {
        query = query.filter(is_active.eq(true));
    }
    query.load::<Recipe>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_recipe_with_ingredients(db_path: &PathBuf, recipe_id: i32) -> Result<(Recipe, Vec<RecipeIngredient>), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::{recipes, recipe_ingredients};
    let recipe: Recipe = recipes::table.find(recipe_id)
        .first::<Recipe>(&mut conn)
        .map_err(|e| e.to_string())?;
    let ingredients_list: Vec<RecipeIngredient> = recipe_ingredients::table
        .filter(recipe_ingredients::recipe_id.eq(recipe_id))
        .load::<RecipeIngredient>(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok((recipe, ingredients_list))
}

pub fn add_recipe(db_path: &PathBuf, new_recipe: NewRecipe) -> Result<Recipe, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipes::dsl::*;
    diesel::insert_into(recipes)
        .values(&new_recipe)
        .returning(Recipe::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_recipe(
    db_path: &PathBuf,
    new_recipe: NewRecipe,
    ingredients_list: Vec<NewRecipeIngredient>,
) -> Result<Recipe, String> {
    let mut conn = open_conn(db_path)?;
    conn.transaction(|conn| {
        use crate::db::schema::recipes::dsl::*;
        let recipe: Recipe = diesel::insert_into(recipes)
            .values(&new_recipe)
            .returning(Recipe::as_returning())
            .get_result(conn)?;
        for mut item in ingredients_list {
            item.recipe_id = recipe.id;
            diesel::insert_into(crate::db::schema::recipe_ingredients::table)
                .values(&item)
                .execute(conn)?;
        }
        Ok(recipe)
    }).map_err(|e: diesel::result::Error| e.to_string())
}

pub fn update_recipe(db_path: &PathBuf, recipe_id: i32, update: UpdateRecipe) -> Result<Recipe, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipes::dsl::*;
    diesel::update(recipes.filter(id.eq(recipe_id)))
        .set(&update)
        .returning(Recipe::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn soft_delete_recipe(db_path: &PathBuf, recipe_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipes::dsl::*;
    diesel::update(recipes.filter(id.eq(recipe_id)))
        .set(is_active.eq(false))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

pub fn mark_recipe_uploaded(db_path: &PathBuf, recipe_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipes::dsl::*;
    diesel::update(recipes.filter(id.eq(recipe_id)))
        .set(uploaded.eq(true))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

// Individual recipe ingredient CRUD
pub fn add_recipe_ingredient(db_path: &PathBuf, new: NewRecipeIngredient) -> Result<RecipeIngredient, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipe_ingredients::dsl::*;
    diesel::insert_into(recipe_ingredients)
        .values(&new)
        .returning(RecipeIngredient::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn update_recipe_ingredient(
    db_path: &PathBuf,
    ri_id: i32,
    update: UpdateRecipeIngredient,
) -> Result<RecipeIngredient, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipe_ingredients::dsl::*;
    diesel::update(recipe_ingredients.filter(id.eq(ri_id)))
        .set(&update)
        .returning(RecipeIngredient::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn delete_recipe_ingredient(db_path: &PathBuf, ri_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::recipe_ingredients::dsl::*;
    diesel::delete(recipe_ingredients.filter(id.eq(ri_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}
