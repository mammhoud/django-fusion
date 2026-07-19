//! Standalone binary to seed the SQLite database with a chosen demo preset.
//!
//! Reads `DATABASE_URL` from the environment or `.env` (resolved via
//! `pos_lib::db::get_db_path_from_env`), then selects which demo-data
//! preset to land via the `PRESET` environment variable.
//!
//! | `PRESET` env   | Effect                                                                                            | Branding                       |
//! |----------------|---------------------------------------------------------------------------------------------------|--------------------------------|
//! | all (default)  | Layered: base + gaming + coffee. Branding = gaming (last-write-wins on `settings.restaurant_name`).| "Level Up Gaming Center"       |
//! | base           | Layered then strips gaming + coffee. Gaming's `down.sql` restores food defaults + rebrand.         | "POS KO"                       |
//! | gaming         | Layered then strips coffee.                                                                       | "Level Up Gaming Center"       |
//! | coffee         | Layered then strips gaming.                                                                       | "The Daily Grind"              |
//!
//! # Usage
//!
//! ```bash
//! # Layered (default) — equivalent to `pnpm db:seed`:
//! cargo run --manifest-path src-tauri/Cargo.toml --bin seed
//!
//! # Pick a preset via the env var:
//! PRESET=coffee cargo run --manifest-path src-tauri/Cargo.toml --bin seed
//!
//! # Or via the new `make seed` target (recommended for first-time users):
//! make seed                          # preset=all (default)
//! make seed PRESET=coffee            # coffee-only
//! make seed PRESET=gaming            # gaming-only
//! make seed PRESET=base              # restaurant-only
//! ```

use std::env;
use std::path::{Path, PathBuf};

use diesel::prelude::*;
use diesel::sql_query;

fn main() {
    // Load .env if present — dotenvy silently ignores missing files.
    dotenvy::dotenv().ok();

    let preset = env::var("PRESET").unwrap_or_else(|_| "all".to_string());
    if !is_valid_preset(&preset) {
        print_preset_help(&preset);
        std::process::exit(1);
    }

    let db_path = pos_lib::db::get_db_path_from_env().unwrap_or_else(|msg| {
        eprintln!("❌ {msg}\n");
        eprintln!("Create a .env file in the project root with:\n");
        eprintln!("  DATABASE_URL=restaurant.db");
        std::process::exit(1);
    });

    println!("🔧 Seeding database (preset={preset}): {}", db_path.display());

    if let Err(err) = seed_with_preset(&db_path, &preset) {
        eprintln!("❌ Seed failed: {err}");
        std::process::exit(1);
    }

    println!("✅ Database seeded with preset '{preset}'.");
    println!("   Location: {}", db_path.display());
}

fn is_valid_preset(p: &str) -> bool {
    matches!(p, "all" | "base" | "gaming" | "coffee")
}

fn print_preset_help(bad: &str) {
    eprintln!("❌ Invalid PRESET '{bad}'.");
    eprintln!("\nValid PRESET values:");
    eprintln!("  all     — layered (base + gaming + coffee); brand = 'Level Up Gaming Center'");
    eprintln!("  base    — layered then strips gaming + coffee; brand = 'POS KO'");
    eprintln!("  gaming  — layered then strips coffee; brand = 'Level Up Gaming Center'");
    eprintln!("  coffee  — layered then strips gaming; brand = 'The Daily Grind'");
    eprintln!("\nNotes:");
    eprintln!("  • Strip is a no-op when a referenced preset's `down.sql` is absent from");
    eprintln!("    this branch's `src-tauri/migrations/` folder (e.g. forks shipping only");
    eprintln!("    one preset). Useful warnings are printed, not errors.");
    eprintln!("  • Bare `make seed` defaults to all. Set PRESET explicitly to a valid value;");
    eprintln!("    bare `make seed PRESET=` (empty) is treated as invalid to catch typos.");
    eprintln!("\nUsage:");
    eprintln!("  make seed                          # preset=all (default)");
    eprintln!("  make seed PRESET=coffee            # coffee-only");
    eprintln!("  PRESET=coffee pnpm db:reset        # equivalent via pnpm script");
    eprintln!("  PRESET=coffee cargo run --manifest-path src-tauri/Cargo.toml --bin seed");
}

fn seed_with_preset(db_path: &Path, preset: &str) -> Result<(), String> {
    // 1. Make sure parent dir exists; drop any existing DB so we layer predictably.
    if let Some(parent) = db_path.parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent)
                .map_err(|e| format!("create parent of {}: {}", db_path.display(), e))?;
        }
    }
    if db_path.exists() {
        std::fs::remove_file(db_path)
            .map_err(|e| format!("remove {}: {}", db_path.display(), e))?;
        println!("✓ removed existing {}", db_path.display());
    }

    // 2. Apply ALL migrations. `embed_migrations!` includes base + gaming + coffee
    //    in `MIGRATIONS`; the two presets layer additively on top of base. Diesel
    //    tracks applied versions in `__diesel_schema_migrations` so subsequent
    //    prod-app launches won't try to re-apply them.
    pos_lib::db::run_migrations(db_path)?;

    let mut conn = pos_lib::db::open_conn(db_path)?;

    // 3. Strip the unwanted presets' rows via their `down.sql`. The preset-specific
    //    downs are narrow (`IN (..)` lists) — see the SQL collision-fixes commit
    //    for the audit that confirms no gaming/coffee data is collateral-deleted.
    //
    //    Each entry in `to_strip` is *referenced by its absolute folder name*. If
    //    a preset's `down.sql` is not present in this build's `migrations/` dir
    //    (e.g. a community fork that only ships one preset, or a branch where the
    //    coffee/gaming migration hasn't landed yet), we *skip* its strip with a
    //    friendly warning rather than hard-failing. Strip semantics are no-ops in
    //    that case, since the data wasn't seeded in the first place.
    let migrations_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("migrations");
    let to_strip: &[&str] = match preset {
        "all" => &[],
        "base" => &[
            "2026-07-17-000000_gaming_center_seed",
            "2026-08-01-000000_coffee_shop_seed",
        ],
        "gaming" => &["2026-08-01-000000_coffee_shop_seed"],
        "coffee" => &["2026-07-17-000000_gaming_center_seed"],
        _ => unreachable!(),
    };
    for label in to_strip {
        let down = migrations_dir.join(label).join("down.sql");
        if !down.exists() {
            println!(
                "⚠️  preset '{label}' is not present in migrations/ — skipping strip"
            );
            continue;
        }
        let sql = std::fs::read_to_string(&down)
            .map_err(|e| format!("read {}: {}", down.display(), e))?;
        sql_query(&sql)
            .execute(&mut conn)
            .map_err(|e| format!("apply {} down.sql: {}", label, e))?;
        println!("✓ stripped {label}");
    }

    // 4. Force `settings.restaurant_name` to the chosen preset's brand. Without
    //    this, gaming's UP injects 'Level Up Gaming Center' last-write-wins,
    //    so a coffee preset would otherwise display the gaming brand.
    let brand = match preset {
        "all" => "Level Up Gaming Center", // gaming's UP wins last-write-wins
        "base" => "POS KO",                 // gaming's down restores this
        "gaming" => "Level Up Gaming Center",
        "coffee" => "The Daily Grind",
        _ => unreachable!(),
    };
    let safe = brand.replace('\'', "''");
    let sql = format!("UPDATE settings SET restaurant_name='{safe}' WHERE id=1;");
    sql_query(sql.as_str())
        .execute(&mut conn)
        .map_err(|e| format!("settings update: {}", e))?;
    println!("✓ settings.restaurant_name = '{brand}'");

    Ok(())
}
