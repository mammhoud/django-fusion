/// `register_crud!` — Collapse the 4-command CRUD pattern into one call.
///
/// Generates `get_{module}`, `add_{singular}`, `update_{singular}`, and
/// `delete_{singular}` / `soft_delete_{singular}` `#[tauri::command]` functions
/// that delegate to `operations::{module}::{fn}`.
///
/// Uses `$module => $singular` syntax where `$module` is the operations
/// module name (plural, used for `get_{module}`) and `$singular` is the
/// singular form (used for `add_{singular}`, `update_{singular}`).
///
/// # Syntax
/// ```ignore
/// // Simple (no events, hard delete)
/// register_crud!(categories => category, Category, NewCategory, UpdateCategory);
///
/// // With event emission
/// register_crud!(products => product, Product, NewProduct, UpdateProduct, emit "product-updated");
///
/// // With filter param + soft delete
/// register_crud!(employees => employee, Employee, NewEmployee, UpdateEmployee,
///                filter include_inactive: bool, soft);
///
/// // With event + filter + soft delete
/// register_crud!(ingredients => ingredient, Ingredient, NewIngredient, UpdateIngredient,
///                emit "inventory-changed", filter include_inactive: bool, soft);
/// ```
#[macro_export]
macro_rules! register_crud {
    // ── 1. Simple CRUD ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [], filter: [], delete: delete);
    };
    // ── 2. With events ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty, emit $event:expr) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [$event], filter: [], delete: delete);
    };
    // ── 3. With events + filter ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty, emit $event:expr,
     filter $param:ident: $ty:ty) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [$event], filter: [$param: $ty], delete: delete);
    };
    // ── 4. With filter + soft delete ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty,
     filter $param:ident: $ty:ty, soft) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [], filter: [$param: $ty], delete: soft_delete);
    };
    // ── 5. Soft delete only ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty, soft) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [], filter: [], delete: soft_delete);
    };
    // ── 6. Events + soft delete ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty, emit $event:expr, soft) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [$event], filter: [], delete: soft_delete);
    };
    // ── 7. Events + filter + soft delete ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty, emit $event:expr,
     filter $param:ident: $ty:ty, soft) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [$event], filter: [$param: $ty], delete: soft_delete);
    };
    // ── 8. Filter only (no events, hard delete) ──
    ($module:ident => $singular:ident, $model:ty, $new:ty, $update:ty,
     filter $param:ident: $ty:ty) => {
        $crate::register_crud!(@gen $module, $singular, $model, $new, $update,
            events: [], filter: [$param: $ty], delete: delete);
    };

    // ── Generator ──
    (@gen $module:ident, $singular:ident, $model:ty, $new:ty, $update:ty,
     events: [$($event:expr)?],
     filter: [$($filter_param:ident: $filter_ty:ty)?],
     delete: $delete:ident) => {
        paste::paste! {
            // ── get_{module} (returns a list — uses plural module name) ──
            #[tauri::command]
            fn [<get_ $module>](app: tauri::AppHandle $(, $filter_param: $filter_ty)?)
                -> Result<Vec<$model>, String>
            {
                let db_path = $crate::db::get_db_path(&app)?;
                $crate::operations::$module::[<get_ $module>](&db_path $(, $filter_param)?)
            }

            // ── add_{singular} ──
            #[allow(dead_code)]
            #[tauri::command]
            fn [<add_ $singular>](app: tauri::AppHandle, data: $new)
                -> Result<$model, String>
            {
                let db_path = $crate::db::get_db_path(&app)?;
                let result = $crate::operations::$module::[<add_ $singular>](&db_path, data)?;
                $(
                    if let Err(e) = app.emit($event, serde_json::json!({"type": "created"})) {
                        eprintln!("[events] failed to emit {}: {e}", $event);
                    }
                )?
                Ok(result)
            }

            // ── update_{singular} ──
            #[tauri::command]
            fn [<update_ $singular>](app: tauri::AppHandle, id: i32, update: $update)
                -> Result<$model, String>
            {
                let db_path = $crate::db::get_db_path(&app)?;
                let result = $crate::operations::$module::[<update_ $singular>](&db_path, id, update)?;
                $(
                    if let Err(e) = app.emit($event, serde_json::json!({"type": "updated", "id": id})) {
                        eprintln!("[events] failed to emit {}: {e}", $event);
                    }
                )?
                Ok(result)
            }

            // ── delete_{singular} or soft_delete_{singular} ──
            #[tauri::command]
            fn [<$delete _ $singular>](app: tauri::AppHandle, id: i32)
                -> Result<(), String>
            {
                let db_path = $crate::db::get_db_path(&app)?;
                $crate::operations::$module::[<$delete _ $singular>](&db_path, id)?;
                $(
                    if let Err(e) = app.emit($event, serde_json::json!({"type": "deleted", "id": id})) {
                        eprintln!("[events] failed to emit {}: {e}", $event);
                    }
                )?
                Ok(())
            }
        }
    };
}
