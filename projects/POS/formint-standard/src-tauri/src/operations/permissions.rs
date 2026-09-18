/// Permission resolution for the Standard tier (custom roles & permissions).
///
/// Consumes the existing ``roles`` table (JSON ``permissions`` column) and
/// returns the effective permission set for a user.  Superusers get all keys;
/// otherwise the union of every assigned role's truthy JSON flags is returned.
///
/// Canonical permission keys (source of truth — keep in sync with frontend):
///   can_manage_products, can_issue_refunds, can_manage_inventory,
///   can_manage_settings, can_manage_employees, can_manage_roles,
///   can_view_reports, can_view_analytics
use std::collections::HashSet;
use std::path::PathBuf;

use diesel::prelude::*;

use crate::db::models::Role;
use crate::db::schema::{roles, user_roles};

/// Return every permission key the user is entitled to.
///
/// * ``user_id == 1`` → **superuser** (implicit — all keys granted).
/// * Otherwise the union of every assigned active role's JSON permission flags
///   whose value is ``true`` is returned.
pub fn resolve_permissions(db_path: &PathBuf, user_id: i32) -> Result<HashSet<String>, String> {
    // ── Superuser gate ──────────────────────────────────────────
    if user_id == 1 {
        return Ok(crate::operations::roles::get_permission_catalog()
            .into_iter()
            .map(|p| p.key)
            .collect());
    }

    let mut conn = crate::db::open_conn(db_path)?;

    let assigned: Vec<Role> = user_roles::table
        .inner_join(roles::table)
        .filter(user_roles::user_id.eq(user_id))
        .filter(roles::is_active.eq(true))
        .select(Role::as_select())
        .load(&mut conn)
        .map_err(|e| format!("resolve permissions: {e}"))?;

    let mut keys: HashSet<String> = HashSet::new();
    for role in assigned {
        let perms: serde_json::Value =
            serde_json::from_str(&role.permissions).unwrap_or_default();
        if let Some(obj) = perms.as_object() {
            for (key, value) in obj {
                if value.as_bool() == Some(true) {
                    keys.insert(key.clone());
                }
            }
        }
    }
    Ok(keys)
}

/// Check whether a user holds a specific permission key.
pub fn has_permission(db_path: &PathBuf, user_id: i32, key: &str) -> Result<bool, String> {
    resolve_permissions(db_path, user_id).map(|keys| keys.contains(key))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::db::models::NewRole;
    use crate::db::run_migrations;

    fn temp_db(tag: &str) -> PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "formint-standard-perms-{}-{}.db",
            std::process::id(),
            tag
        ));
        let _ = std::fs::remove_file(&path);
        run_migrations(&path).expect("migrations ok");
        path
    }

    #[test]
    fn superuser_gets_all_keys() {
        let db = temp_db("super");
        let keys = resolve_permissions(&db, 1).expect("resolve");
        assert!(keys.contains("manage:products"));
        assert!(keys.contains("manage:settings"));
        assert!(!keys.is_empty());
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn user_with_no_roles_gets_nothing() {
        let db = temp_db("none");
        let keys = resolve_permissions(&db, 99).expect("resolve");
        assert!(keys.is_empty());
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn assigned_role_keys_are_resolved() {
        let db = temp_db("assign");
        let mut conn = crate::db::open_conn(&db).unwrap();
        // Insert a role with two permissions
        diesel::insert_into(roles::table)
            .values(&NewRole {
                name: "B3-Manager".into(),
                permissions: r#"{"manage:products":true,"view:reports":true,"manage:settings":false}"#.into(),
            })
            .execute(&mut conn)
            .unwrap();
        let role_id: i32 = roles::table
            .select(roles::id)
            .order(roles::id.desc())
            .first(&mut conn)
            .unwrap();
        // Assign the role to user 42
        diesel::insert_into(user_roles::table)
            .values(&crate::db::models::NewUserRole {
                user_id: 42,
                role_id,
            })
            .execute(&mut conn)
            .unwrap();

        let keys = resolve_permissions(&db, 42).expect("resolve");
        assert!(keys.contains("manage:products"));
        assert!(keys.contains("view:reports"));
        assert!(!keys.contains("manage:settings")); // false → excluded
        assert_eq!(keys.len(), 2);
        let _ = std::fs::remove_file(&db);
    }

    #[test]
    fn union_across_multiple_roles() {
        let db = temp_db("union");
        let mut conn = crate::db::open_conn(&db).unwrap();

        diesel::insert_into(roles::table)
            .values(&NewRole {
                name: "B3-Cashier".into(),
                permissions: r#"{"process:sales":true}"#.into(),
            })
            .execute(&mut conn)
            .unwrap();
        let r1: i32 = roles::table
            .select(roles::id)
            .order(roles::id.desc())
            .first(&mut conn)
            .unwrap();

        diesel::insert_into(roles::table)
            .values(&NewRole {
                name: "B3-Stock".into(),
                permissions: r#"{"manage:inventory":true,"view:reports":true}"#.into(),
            })
            .execute(&mut conn)
            .unwrap();
        let r2: i32 = roles::table
            .select(roles::id)
            .order(roles::id.desc())
            .first(&mut conn)
            .unwrap();

        for rid in [r1, r2] {
            diesel::insert_into(user_roles::table)
                .values(&crate::db::models::NewUserRole {
                    user_id: 99,
                    role_id: rid,
                })
                .execute(&mut conn)
                .unwrap();
        }

        let keys = resolve_permissions(&db, 99).expect("resolve");
        assert!(keys.contains("process:sales"));
        assert!(keys.contains("manage:inventory"));
        assert!(keys.contains("view:reports"));
        assert_eq!(keys.len(), 3);
        let _ = std::fs::remove_file(&db);
    }
}
