use crate::db::models::*;
use crate::db::schema::kitchen_tickets;
use diesel::prelude::*;
use std::collections::HashMap;
use std::path::PathBuf;

pub fn get_kitchen_tickets(db_path: &PathBuf, status: Option<String>) -> Result<Vec<KitchenTicket>, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    let mut query = kitchen_tickets::table.into_boxed();
    if let Some(s) = status {
        query = query.filter(kitchen_tickets::status.eq(s));
    }
    query.select(KitchenTicket::as_select()).load(&mut conn).map_err(|e| e.to_string())
}

/// Resolve the product categories present on each kitchen ticket (matching the
/// given status filter, if any). sale_items only store the product name, so we
/// bridge to `products.name` first and then to `categories` via `category_id`.
/// Returns one row per (ticket, category) so the frontend can render colored
/// category filter pills with per-ticket membership.
pub fn get_kitchen_ticket_categories(db_path: &PathBuf, status: Option<String>) -> Result<Vec<KitchenTicketCategory>, String> {
    use crate::db::schema::{categories, products, sale_items};

    let mut conn = crate::db::open_conn(db_path)?;

    // 1. Tickets matching the status filter
    let mut tickets_query = kitchen_tickets::table.into_boxed();
    if let Some(s) = status {
        tickets_query = tickets_query.filter(kitchen_tickets::status.eq(s));
    }
    let tickets: Vec<KitchenTicket> = tickets_query
        .select(KitchenTicket::as_select())
        .load(&mut conn)
        .map_err(|e| e.to_string())?;

    if tickets.is_empty() {
        return Ok(vec![]);
    }

    // 2. Sale items for those tickets
    let sale_ids: Vec<i32> = tickets.iter().map(|t| t.sale_id).collect();
    let items: Vec<SaleItem> = sale_items::table
        .filter(sale_items::sale_id.eq_any(&sale_ids))
        .load(&mut conn)
        .map_err(|e| e.to_string())?;

    // 3. Products by name → category_id
    let product_names: Vec<String> = items.iter().map(|i| i.product_name.clone()).collect();
    let products: Vec<Product> = products::table
        .filter(products::name.eq_any(&product_names))
        .load(&mut conn)
        .map_err(|e| e.to_string())?;
    let mut name_to_category: HashMap<String, i32> = HashMap::new();
    for product in &products {
        if let Some(category_id) = product.category_id {
            name_to_category.insert(product.name.clone(), category_id);
        }
    }

    // 4. Categories by id → (name, color)
    let category_ids: Vec<i32> = name_to_category.values().copied().collect();
    let category_rows: Vec<Category> = categories::table
        .filter(categories::id.eq_any(&category_ids))
        .load(&mut conn)
        .map_err(|e| e.to_string())?;
    let category_map: HashMap<i32, Category> = category_rows.into_iter().map(|c| (c.id, c)).collect();

    // 5. sale_id → ticket_id
    let sale_to_ticket: HashMap<i32, i32> = tickets.iter().map(|t| (t.sale_id, t.id)).collect();

    let mut result: Vec<KitchenTicketCategory> = Vec::new();
    for item in items {
        let Some(&ticket_id) = sale_to_ticket.get(&item.sale_id) else { continue };
        let Some(&category_id) = name_to_category.get(&item.product_name) else { continue };
        let Some(category) = category_map.get(&category_id) else { continue };
        result.push(KitchenTicketCategory {
            ticket_id,
            category_id,
            name: category.name.clone(),
            color: category.color.clone(),
        });
    }
    Ok(result)
}

pub fn add_kitchen_ticket(db_path: &PathBuf, ticket: NewKitchenTicket) -> Result<KitchenTicket, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::insert_into(kitchen_tickets::table).values(&ticket).execute(conn)?;
        kitchen_tickets::table.order(kitchen_tickets::id.desc()).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn update_kitchen_ticket(db_path: &PathBuf, id: i32, update: UpdateKitchenTicket) -> Result<KitchenTicket, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        diesel::update(kitchen_tickets::table.find(id)).set(&update).execute(conn)?;
        kitchen_tickets::table.find(id).first(conn)
    })
    .map_err(|e| e.to_string())
}

pub fn delete_kitchen_ticket(db_path: &PathBuf, id: i32) -> Result<(), String> {
    let mut conn = crate::db::open_conn(db_path)?;
    diesel::delete(kitchen_tickets::table.find(id))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(())
}

/// Count all kitchen tickets with status = 'pending'
pub fn count_pending_tickets(db_path: &PathBuf) -> Result<i64, String> {
    let mut conn = crate::db::open_conn(db_path)?;
    use diesel::dsl::count;
    kitchen_tickets::table
        .filter(kitchen_tickets::status.eq("pending"))
        .select(count(kitchen_tickets::id))
        .first::<i64>(&mut conn)
        .map_err(|e| e.to_string())
}
