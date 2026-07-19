use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use crate::operations::signals::{self, ChangeEvent};
use std::path::PathBuf;

pub fn get_products(db_path: &PathBuf) -> Result<Vec<Product>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::products::dsl::*;
    products.order(id.desc()).load::<Product>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_product(db_path: &PathBuf, new: NewProduct) -> Result<Product, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::products::dsl::*;
    let product = diesel::insert_into(products)
        .values(&new)
        .returning(Product::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::ProductCreated(product.id));
    Ok(product)
}

pub fn update_product(db_path: &PathBuf, product_id: i32, update: UpdateProduct) -> Result<Product, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::products::dsl::*;
    let product = diesel::update(products.filter(id.eq(product_id)))
        .set(&update)
        .returning(Product::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::ProductUpdated(product.id));
    Ok(product)
}

pub fn delete_product(db_path: &PathBuf, product_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::products::dsl::*;
    diesel::delete(products.filter(id.eq(product_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::ProductDeleted(product_id));
    Ok(())
}

pub fn mark_product_uploaded(db_path: &PathBuf, product_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::products::dsl::*;
    diesel::update(products.filter(id.eq(product_id)))
        .set(uploaded.eq(true))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::ProductUpdated(product_id));
    Ok(())
}
