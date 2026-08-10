use diesel::prelude::*;
use serde::Serialize;
use std::path::PathBuf;
use crate::db::{models::*, schema::*, open_conn};

#[derive(Serialize)]
pub struct DumpData {
    pub products: Vec<Product>,
    pub sales: Vec<Sale>,
    pub categories: Vec<Category>,
    pub ingredients: Vec<Ingredient>,
    pub recipes: Vec<Recipe>,
    pub recipe_ingredients: Vec<RecipeIngredient>,
}

pub fn dump_all(db_path: &PathBuf) -> Result<DumpData, String> {
    let mut conn = open_conn(db_path)?;
    Ok(DumpData {
        products: products::table.load::<Product>(&mut conn).map_err(|e| e.to_string())?,
        sales: sales::table.load::<Sale>(&mut conn).map_err(|e| e.to_string())?,
        categories: categories::table.load::<Category>(&mut conn).map_err(|e| e.to_string())?,
        ingredients: ingredients::table.load::<Ingredient>(&mut conn).map_err(|e| e.to_string())?,
        recipes: recipes::table.load::<Recipe>(&mut conn).map_err(|e| e.to_string())?,
        recipe_ingredients: recipe_ingredients::table.load::<RecipeIngredient>(&mut conn).map_err(|e| e.to_string())?,
    })
}

pub fn dump_unuploaded(db_path: &PathBuf) -> Result<DumpData, String> {
    let mut conn = open_conn(db_path)?;
    Ok(DumpData {
        products: products::table.filter(products::uploaded.eq(false))
            .load::<Product>(&mut conn).map_err(|e| e.to_string())?,
        sales: sales::table.filter(sales::uploaded.eq(false))
            .load::<Sale>(&mut conn).map_err(|e| e.to_string())?,
        categories: categories::table.load::<Category>(&mut conn).map_err(|e| e.to_string())?,
        ingredients: ingredients::table.filter(ingredients::uploaded.eq(false))
            .load::<Ingredient>(&mut conn).map_err(|e| e.to_string())?,
        recipes: recipes::table.filter(recipes::uploaded.eq(false))
            .load::<Recipe>(&mut conn).map_err(|e| e.to_string())?,
        recipe_ingredients: recipe_ingredients::table
            .load::<RecipeIngredient>(&mut conn).map_err(|e| e.to_string())?,
    })
}

pub fn dump_to_json(db_path: &PathBuf, only_unuploaded: bool) -> Result<String, serde_json::Error> {
    let data = if only_unuploaded {
        dump_unuploaded(db_path).unwrap_or_else(|_| DumpData {
            products: vec![],
            sales: vec![],
            categories: vec![],
            ingredients: vec![],
            recipes: vec![],
            recipe_ingredients: vec![],
        })
    } else {
        dump_all(db_path).unwrap_or_else(|_| DumpData {
            products: vec![],
            sales: vec![],
            categories: vec![],
            ingredients: vec![],
            recipes: vec![],
            recipe_ingredients: vec![],
        })
    };
    serde_json::to_string_pretty(&data)
}
