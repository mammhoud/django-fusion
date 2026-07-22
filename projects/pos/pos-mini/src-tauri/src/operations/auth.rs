use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use crate::email;
use std::collections::HashMap;
use std::env;
use std::path::PathBuf;
use std::sync::Mutex;
use std::time::{Duration, Instant};
use once_cell::sync::Lazy;

// In-memory store for confirmation codes with expiry
type CodeStore = HashMap<String, (String, Instant)>;

static CONFIRMATION_CODES: Lazy<Mutex<CodeStore>> = Lazy::new(|| Mutex::new(HashMap::new()));

const CODE_EXPIRY_SECS: u64 = 300; // 5 minutes

/// Check if authentication is required.
/// Auth is required when any of the following is true:
/// 1. SMTP_USERNAME env var is set AND settings has a manager email configured
/// 2. SUPERUSER_EMAIL + SUPERUSER_PASSWORD env vars are both set
pub fn check_auth_required(db_path: &PathBuf) -> Result<bool, String> {
    // First check: superuser env vars
    let superuser_configured = env::var("SUPERUSER_EMAIL").is_ok()
        && !env::var("SUPERUSER_EMAIL").unwrap_or_default().is_empty()
        && env::var("SUPERUSER_PASSWORD").is_ok()
        && !env::var("SUPERUSER_PASSWORD").unwrap_or_default().is_empty();

    if superuser_configured {
        return Ok(true);
    }

    // Check SMTP configuration
    let smtp_configured = env::var("SMTP_USERNAME").is_ok()
        && !env::var("SMTP_USERNAME").unwrap_or_default().is_empty();

    if !smtp_configured {
        return Ok(false);
    }

    // Check if manager email is set in settings
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::settings::dsl::*;
    let result = settings.find(1)
        .select(email)
        .first::<Option<String>>(&mut conn)
        .map_err(|e| e.to_string())?;

    let has_manager_email = result
        .as_ref()
        .map(|e| !e.trim().is_empty())
        .unwrap_or(false);

    Ok(has_manager_email)
}

/// Get the superuser email from environment variables, if configured
pub fn get_superuser_email() -> Option<String> {
    let email = env::var("SUPERUSER_EMAIL").ok()?;
    let password = env::var("SUPERUSER_PASSWORD").ok()?;
    if email.is_empty() || password.is_empty() {
        return None;
    }
    Some(email)
}

/// Ensure a superuser exists in the database.
/// If SUPERUSER_EMAIL + SUPERUSER_PASSWORD are set, creates or updates the superuser.
/// Called during app setup (after migrations run).
pub fn ensure_superuser_exists(db_path: &PathBuf) -> Result<(), String> {
    let super_email = match env::var("SUPERUSER_EMAIL") {
        Ok(e) if !e.is_empty() => e,
        _ => return Ok(()), // Not configured, nothing to do
    };
    let password = match env::var("SUPERUSER_PASSWORD") {
        Ok(p) if !p.is_empty() => p,
        _ => return Ok(()), // Not configured, nothing to do
    };

    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::{self, dsl::*};

    // Check if a user with this email already exists
    let existing = users::table
        .filter(users::email.eq(&super_email))
        .first::<User>(&mut conn)
        .ok();

    if let Some(user) = existing {
        // User exists — update password if it changed
        let pw_matches = bcrypt::verify(&password, &user.password_hash).unwrap_or(false);
        if !pw_matches {
            let pw_hash = bcrypt::hash(&password, bcrypt::DEFAULT_COST)
                .map_err(|e| format!("Failed to hash password: {}", e))?;
            diesel::update(users::table.filter(users::email.eq(&super_email)))
                .set(password_hash.eq(pw_hash))
                .execute(&mut conn)
                .map_err(|e| format!("Failed to update superuser password: {}", e))?;
            eprintln!("[superuser] Updated password for existing user: {}", super_email);
        }
        return Ok(());
    }

    // Create the superuser
    let pw_hash = bcrypt::hash(&password, bcrypt::DEFAULT_COST)
        .map_err(|e| format!("Failed to hash password: {}", e))?;

    let super_name = env::var("SUPERUSER_NAME").unwrap_or_else(|_| "Admin".to_string());

    let new_user = NewUser {
        email: super_email.clone(),
        password_hash: pw_hash,
        name: super_name,
    };

    diesel::insert_into(users::table)
        .values(&new_user)
        .execute(&mut conn)
        .map_err(|e| format!("Failed to create superuser: {}", e))?;

    eprintln!("[superuser] Created superuser: {}", super_email);
    Ok(())
}

/// Check if any user exists in the database
pub fn has_users(db_path: &PathBuf) -> Result<bool, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::dsl::*;
    let count = users.count().get_result::<i64>(&mut conn)
        .map_err(|e| e.to_string())?;
    Ok(count > 0)
}

/// Get user count (for frontend display)
pub fn get_user_count(db_path: &PathBuf) -> Result<i64, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::dsl::*;
    users.count().get_result::<i64>(&mut conn)
        .map_err(|e| e.to_string())
}

/// Verify a specific user still exists (for session validation on app restart)
pub fn verify_user(db_path: &PathBuf, user_email: String) -> Result<User, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::dsl::*;
    
    users
        .filter(email.eq(&user_email))
        .first::<User>(&mut conn)
        .map_err(|_| "User no longer exists.".to_string())
}

/// Send a confirmation code to the given email via SMTP
pub fn send_confirmation_code(email_address: String) -> Result<(), String> {
    // Generate a random 6-digit code
    use rand::Rng;
    let code: u32 = rand::thread_rng().gen_range(100000..999999);
    let code_str = format!("{:06}", code);

    // Store the code with expiry
    let mut store = CONFIRMATION_CODES.lock().map_err(|e| e.to_string())?;
    store.insert(email_address.clone(), (code_str.clone(), Instant::now()));

    // Send email via SMTP
    email::send_confirmation_email(&email_address, &code_str)?;

    Ok(())
}

/// Verify the confirmation code and optionally create the user account
pub fn verify_and_setup_account(
    db_path: &PathBuf,
    email_address: String,
    code: String,
    password: String,
    user_name: String,
) -> Result<User, String> {
    // Verify the code
    let mut store = CONFIRMATION_CODES.lock().map_err(|e| e.to_string())?;
    let entry = store.remove(&email_address)
        .ok_or_else(|| "No confirmation code found. Please request a new one.".to_string())?;

    let (stored_code, timestamp) = entry;
    if Instant::now().duration_since(timestamp) > Duration::from_secs(CODE_EXPIRY_SECS) {
        return Err("Confirmation code has expired. Please request a new one.".to_string());
    }

    if stored_code != code.trim() {
        return Err("Invalid confirmation code. Please try again.".to_string());
    }

    // Verify SMTP is configured (should be if we sent email)
    if env::var("SMTP_USERNAME").is_err() {
        return Err("SMTP is not configured. Cannot complete setup.".to_string());
    }

    // Hash the password
    let pw_hash = bcrypt::hash(&password, bcrypt::DEFAULT_COST)
        .map_err(|e| format!("Failed to hash password: {}", e))?;

    // Create the user
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::dsl::*;

    let new_user = NewUser {
        email: email_address,
        password_hash: pw_hash,
        name: user_name,
    };

    diesel::insert_into(users)
        .values(&new_user)
        .returning(User::as_returning())
        .get_result(&mut conn)
        .map_err(|e| format!("Failed to create user: {}", e))
}

/// Login with email and password
pub fn login(db_path: &PathBuf, email_address: String, password: String) -> Result<User, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::dsl::*;

    let user = users
        .filter(email.eq(&email_address))
        .first::<User>(&mut conn)
        .map_err(|_| "Invalid email or password.".to_string())?;

    let valid = bcrypt::verify(&password, &user.password_hash)
        .map_err(|e| format!("Password verification error: {}", e))?;

    if !valid {
        return Err("Invalid email or password.".to_string());
    }

    Ok(user)
}

/// Change password for a user
pub fn change_password(
    db_path: &PathBuf,
    email_address: String,
    old_password: String,
    new_password: String,
) -> Result<(), String> {
    // First verify the old password
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::users::dsl::*;

    let user = users
        .filter(email.eq(&email_address))
        .first::<User>(&mut conn)
        .map_err(|_| "User not found.".to_string())?;

    let valid = bcrypt::verify(&old_password, &user.password_hash)
        .map_err(|e| format!("Password verification error: {}", e))?;

    if !valid {
        return Err("Current password is incorrect.".to_string());
    }

    if new_password.len() < 6 {
        return Err("New password must be at least 6 characters long.".to_string());
    }

    // Hash the new password
    let new_hash = bcrypt::hash(&new_password, bcrypt::DEFAULT_COST)
        .map_err(|e| format!("Failed to hash password: {}", e))?;

    // Update
    diesel::update(users.filter(email.eq(&email_address)))
        .set(password_hash.eq(new_hash))
        .execute(&mut conn)
        .map_err(|e| format!("Failed to update password: {}", e))?;

    Ok(())
}

// ============================================================================
// Unit tests
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use std::path::PathBuf;
    use std::sync::Mutex as StdMutex;
    use once_cell::sync::Lazy;

    /// Global mutex to serialize tests that modify environment variables.
    /// `env::set_var` / `env::remove_var` are process-wide and NOT thread-safe.
    static ENV_MUTEX: Lazy<StdMutex<()>> = Lazy::new(|| StdMutex::new(()));

    // ---- Helpers ----------------------------------------------------------

    /// Create a temporary SQLite database with all migrations applied.
    fn setup_test_db(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join("pos_tests");
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join(format!("test_{}.db", name));
        let _ = std::fs::remove_file(&path);
        crate::db::run_migrations(&path).unwrap();
        path
    }

    /// Remove auth-related env vars that might leak between tests.
    fn clear_auth_env_vars() {
        env::remove_var("SUPERUSER_EMAIL");
        env::remove_var("SUPERUSER_PASSWORD");
        env::remove_var("SUPERUSER_NAME");
        env::remove_var("SMTP_USERNAME");
    }

    /// Set the manager email in the settings table (row id=1 from migrations).
    fn set_manager_email(db_path: &PathBuf, mgr_email: Option<&str>) {
        use crate::db::schema::settings::dsl::*;
        let mut conn = open_conn(db_path).unwrap();
        diesel::update(settings.find(1))
            .set(email.eq(mgr_email))
            .execute(&mut conn)
            .unwrap();
    }

    /// Count rows in the users table.
    fn count_users(db_path: &PathBuf) -> i64 {
        use crate::db::schema::users::dsl::*;
        let mut conn = open_conn(db_path).unwrap();
        users.count().get_result::<i64>(&mut conn).unwrap()
    }

    // ========================================================================
    // get_superuser_email
    // ========================================================================

    #[test]
    fn get_superuser_email_both_set() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");

        assert_eq!(get_superuser_email(), Some("admin@test.com".to_string()));
    }

    #[test]
    fn get_superuser_email_none_set() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        assert_eq!(get_superuser_email(), None);
    }

    #[test]
    fn get_superuser_email_only_email_set() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        assert_eq!(get_superuser_email(), None);
    }

    #[test]
    fn get_superuser_email_only_password_set() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_PASSWORD", "secret123");
        assert_eq!(get_superuser_email(), None);
    }

    #[test]
    fn get_superuser_email_both_empty() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "");
        env::set_var("SUPERUSER_PASSWORD", "");
        assert_eq!(get_superuser_email(), None);
    }

    #[test]
    fn get_superuser_email_password_empty() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "");
        assert_eq!(get_superuser_email(), None);
    }

    // ========================================================================
    // check_auth_required
    // ========================================================================

    #[test]
    fn check_auth_required_no_env_vars() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        let db = setup_test_db("car_none");

        let result = check_auth_required(&db).unwrap();
        assert!(!result, "auth should NOT be required when no env vars are set");
    }

    #[test]
    fn check_auth_required_superuser_set() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");
        let db = setup_test_db("car_su");

        let result = check_auth_required(&db).unwrap();
        assert!(result, "auth should be required when SUPERUSER vars are set");
    }

    #[test]
    fn check_auth_required_superuser_partial() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        // No SUPERUSER_PASSWORD — should fall through to SMTP check
        let db = setup_test_db("car_su_partial");

        let result = check_auth_required(&db).unwrap();
        assert!(!result, "only email set, no SMTP — auth NOT required");
    }

    #[test]
    fn check_auth_required_smtp_with_manager_email() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SMTP_USERNAME", "smtp@test.com");
        let db = setup_test_db("car_smtp_email");
        set_manager_email(&db, Some("manager@restaurant.com"));

        let result = check_auth_required(&db).unwrap();
        assert!(result, "auth should be required when SMTP+manager email are set");
    }

    #[test]
    fn check_auth_required_smtp_no_manager_email() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SMTP_USERNAME", "smtp@test.com");
        let db = setup_test_db("car_smtp_nomgr");
        set_manager_email(&db, None);

        let result = check_auth_required(&db).unwrap();
        assert!(!result, "SMTP set but no manager email — auth NOT required");
    }

    #[test]
    fn check_auth_required_smtp_empty_manager_email() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SMTP_USERNAME", "smtp@test.com");
        let db = setup_test_db("car_smtp_empty");
        set_manager_email(&db, Some(""));

        let result = check_auth_required(&db).unwrap();
        assert!(!result, "empty manager email — auth NOT required");
    }

    #[test]
    fn check_auth_required_superuser_priority_over_smtp() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");
        env::set_var("SMTP_USERNAME", "smtp@test.com");
        let db = setup_test_db("car_priority");
        // No manager email — but superuser short-circuits before SMTP check
        set_manager_email(&db, None);

        let result = check_auth_required(&db).unwrap();
        assert!(result, "superuser should short-circuit regardless of SMTP config");
    }

    #[test]
    fn check_auth_required_superuser_no_db_needed() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");

        // Superuser check doesn't touch DB — even nonexistent path returns true
        let result = check_auth_required(&PathBuf::from("/nonexistent/path.db")).unwrap();
        assert!(result);
    }

    // ========================================================================
    // ensure_superuser_exists
    // ========================================================================

    #[test]
    fn ensure_superuser_no_env_vars() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        let db = setup_test_db("ese_none");

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 0);
    }

    #[test]
    fn ensure_superuser_email_empty() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "");
        env::set_var("SUPERUSER_PASSWORD", "password123");
        let db = setup_test_db("ese_empty_email");

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 0);
    }

    #[test]
    fn ensure_superuser_password_empty() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "");
        let db = setup_test_db("ese_empty_pw");

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 0);
    }

    #[test]
    fn ensure_superuser_creates_user() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");
        let db = setup_test_db("ese_create");

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 1);

        let user = verify_user(&db, "admin@test.com".to_string()).unwrap();
        assert_eq!(user.email, "admin@test.com");
        assert_eq!(user.name, "Admin");
        assert!(bcrypt::verify("secret123", &user.password_hash).unwrap());
        assert!(!bcrypt::verify("wrong", &user.password_hash).unwrap());
    }

    #[test]
    fn ensure_superuser_respects_custom_name() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "boss@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secure123");
        env::set_var("SUPERUSER_NAME", "The Boss");
        let db = setup_test_db("ese_name");

        ensure_superuser_exists(&db).unwrap();
        let user = verify_user(&db, "boss@test.com".to_string()).unwrap();
        assert_eq!(user.name, "The Boss");
    }

    #[test]
    fn ensure_superuser_idempotent() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");
        let db = setup_test_db("ese_idem");

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 1);

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 1, "should still have exactly 1 user");

        let user = verify_user(&db, "admin@test.com".to_string()).unwrap();
        assert!(bcrypt::verify("secret123", &user.password_hash).unwrap());
    }

    #[test]
    fn ensure_superuser_updates_password() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "original");
        let db = setup_test_db("ese_update_pw");

        ensure_superuser_exists(&db).unwrap();
        let user1 = verify_user(&db, "admin@test.com".to_string()).unwrap();
        assert!(bcrypt::verify("original", &user1.password_hash).unwrap());

        env::set_var("SUPERUSER_PASSWORD", "updated");
        ensure_superuser_exists(&db).unwrap();

        assert_eq!(count_users(&db), 1);
        let user2 = verify_user(&db, "admin@test.com".to_string()).unwrap();
        assert!(!bcrypt::verify("original", &user2.password_hash).unwrap());
        assert!(bcrypt::verify("updated", &user2.password_hash).unwrap());
    }

    #[test]
    fn ensure_superuser_only_email_no_password() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        // No SUPERUSER_PASSWORD at all
        let db = setup_test_db("ese_only_email");

        ensure_superuser_exists(&db).unwrap();
        assert_eq!(count_users(&db), 0);
    }

    #[test]
    fn ensure_superuser_preserves_name_on_update() {
        let _lock = ENV_MUTEX.lock().unwrap();
        clear_auth_env_vars();
        env::set_var("SUPERUSER_EMAIL", "admin@test.com");
        env::set_var("SUPERUSER_PASSWORD", "secret123");
        env::set_var("SUPERUSER_NAME", "Original Admin");
        let db = setup_test_db("ese_name_preserve");

        ensure_superuser_exists(&db).unwrap();
        let user1 = verify_user(&db, "admin@test.com".to_string()).unwrap();
        assert_eq!(user1.name, "Original Admin");

        // Remove SUPERUSER_NAME, change password: name should survive
        env::remove_var("SUPERUSER_NAME");
        env::set_var("SUPERUSER_PASSWORD", "newpassword");
        ensure_superuser_exists(&db).unwrap();

        let user2 = verify_user(&db, "admin@test.com".to_string()).unwrap();
        assert_eq!(user2.name, "Original Admin", "name should not be overwritten on password update");
        assert!(bcrypt::verify("newpassword", &user2.password_hash).unwrap());
    }
}
