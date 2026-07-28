//! Standalone binary to seed the SQLite database with a chosen demo preset.
//!
//! Reads `DATABASE_URL` from the environment or `.env` (resolved via
//! `pos_lib::db::get_db_path_from_env`), then selects which demo-data
//! preset to land via the `PRESET` environment variable.
//!
//! | `PRESET` env   | Effect                                                                                            | Branding                       |
//! |----------------|---------------------------------------------------------------------------------------------------|--------------------------------|
//! | all (default)  | Layered: base + gaming + coffee. Branding = gaming (last-write-wins on `settings.restaurant_name`).| "Level Up Gaming Center"       |
//! | base           | Layered then strips gaming + coffee. Gaming's `down.sql` restores food defaults + rebrand.         | "Forge POS"                    |
//! | gaming         | Layered then strips coffee.                                                                       | "Level Up Gaming Center"       |
//! | coffee         | Layered then strips gaming.                                                                       | "Forge POS"                    |
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
    eprintln!("  base    — layered then strips gaming + coffee; brand = 'Forge POS'");
    eprintln!("  gaming  — layered then strips coffee; brand = 'Level Up Gaming Center'");
    eprintln!("  coffee  — layered then strips gaming; brand = 'Forge POS'");
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

/// Determine which sections to run for a given preset.
fn sections_for_preset(preset: &str) -> &[&str] {
    match preset {
        "all"    => &["shared", "gaming", "coffee"],
        "base"   => &["shared", "base"],
        "gaming" => &["shared", "gaming"],
        "coffee" => &["shared", "base", "coffee"],
        _        => unreachable!(),
    }
}

/// Brand name override for each preset (last-write-wins over section SETs).
fn brand_for_preset(preset: &str) -> &str {
    match preset {
        "all"    => "Level Up Gaming Center",
        "base"   => "Forge POS",
        "gaming" => "Level Up Gaming Center",
        "coffee" => "Forge POS",
        _        => unreachable!(),
    }
}

/// Parse seed SQL content into named sections.
/// Returns a list of `(section_name, lines)` tuples in document order.
/// Lines before any section marker are ignored.
pub fn parse_sections(seed_sql: &str) -> Vec<(String, Vec<String>)> {
    type Section = (String, Vec<String>);
    let mut sections: Vec<Section> = Vec::new();
    let mut current_section: Option<String> = None;
    let mut current_lines: Vec<String> = Vec::new();

    for line in seed_sql.lines() {
        let trimmed = line.trim();
        if let Some(cap) = trimmed.strip_prefix("-- [SECTION:") {
            if let Some(name) = cap.strip_suffix(']') {
                let name = name.to_lowercase();
                // Flush previous section
                if let Some(prev) = current_section.take() {
                    sections.push((prev, std::mem::take(&mut current_lines)));
                }
                current_section = Some(name);
                continue;
            }
        }
        if current_section.is_some() {
            current_lines.push(line.to_string());
        }
    }
    // Flush last section
    if let Some(prev) = current_section.take() {
        sections.push((prev, std::mem::take(&mut current_lines)));
    }

    sections
}

/// Collect lines from active sections (in order).
pub fn collect_active_lines(
    sections: &[(String, Vec<String>)],
    active_sections: &[&str],
) -> Vec<String> {
    let mut active_lines: Vec<String> = Vec::new();
    for (sec_name, sec_lines) in sections {
        if active_sections.contains(&sec_name.as_str()) {
            active_lines.extend(sec_lines.iter().cloned());
        }
    }
    active_lines
}

fn seed_with_preset(db_path: &Path, preset: &str) -> Result<(), String> {
    // 1. Ensure parent dir exists; start with a clean DB.
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

    // 2. Apply ALL schema migrations (creates tables, triggers, essential defaults).
    pos_lib::db::run_migrations(db_path)?;

    let mut conn = pos_lib::db::open_conn(db_path)?;

    // 3. Resolve the unified seed file path.
    let migrations_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("migrations");
    let seed_path = migrations_dir.join("2026-01-01-000000_create_all").join("seed.sql");

    if !seed_path.exists() {
        println!("⚠️  seed.sql not found at {} — skipping seed", seed_path.display());
        return Ok(());
    }

    let seed_sql = std::fs::read_to_string(&seed_path)
        .map_err(|e| format!("read seed.sql: {}", e))?;

    // 4. Determine which sections to run based on the preset.
    let active_sections = sections_for_preset(preset);
    println!("✓ sections to run: {:?}", active_sections);

    // 5. Parse the seed file — split into sections, then extract lines for each.
    //    Section markers look like: `-- [SECTION:<name>]`
    type Section = (String, Vec<String>);
    let mut sections: Vec<Section> = Vec::new();
    let mut current_section: Option<String> = None;
    let mut current_lines: Vec<String> = Vec::new();

    for line in seed_sql.lines() {
        let trimmed = line.trim();
        if let Some(cap) = trimmed.strip_prefix("-- [SECTION:") {
            if let Some(name) = cap.strip_suffix(']') {
                let name = name.to_lowercase();
                // Flush previous section
                if let Some(prev) = current_section.take() {
                    sections.push((prev, std::mem::take(&mut current_lines)));
                }
                current_section = Some(name);
                continue;
            }
        }
        if current_section.is_some() {
            current_lines.push(line.to_string());
        }
    }
    // Flush last section
    if let Some(prev) = current_section.take() {
        sections.push((prev, std::mem::take(&mut current_lines)));
    }

    // 6. Collect lines from active sections (in order).
    //    We also collect comment-headers so the overall sequence feels natural.
    let mut active_lines: Vec<String> = Vec::new();
    for (sec_name, sec_lines) in &sections {
        if active_sections.contains(&sec_name.as_str()) {
            active_lines.extend(sec_lines.iter().cloned());
            println!("  ✓ section [{sec_name}]: {} statements", sec_lines.len());
        } else {
            println!("  - section [{sec_name}]: skipped");
        }
    }

    // 7. Join and execute all statements from the active lines.
    let joined = active_lines.join("\n");
    for statement in joined.split(';') {
        let trimmed = statement.trim();
        if !trimmed.is_empty() {
            // Skip pure comment lines
            if trimmed.starts_with("--") {
                continue;
            }
            sql_query(trimmed)
                .execute(&mut conn)
                .map_err(|e| format!("execute seed statement: {}", e))?;
        }
    }

    // 8. Force the brand name (last-write-wins over section UPDATEs).
    let brand = brand_for_preset(preset);
    let safe = brand.replace('\'', "''");
    let sql = format!("UPDATE settings SET restaurant_name='{safe}' WHERE id=1;");
    sql_query(sql.as_str())
        .execute(&mut conn)
        .map_err(|e| format!("settings update: {}", e))?;
    println!("✓ settings.restaurant_name = '{brand}'");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // ── is_valid_preset ──────────────────────────────────────────────────────

    #[test]
    fn test_is_valid_preset_accepts_all_four() {
        assert!(is_valid_preset("all"));
        assert!(is_valid_preset("base"));
        assert!(is_valid_preset("gaming"));
        assert!(is_valid_preset("coffee"));
    }

    #[test]
    fn test_is_valid_preset_rejects_unknown() {
        assert!(!is_valid_preset(""));
        assert!(!is_valid_preset("foo"));
        assert!(!is_valid_preset("ALL"));      // case-sensitive
        assert!(!is_valid_preset("base "));     // trailing space
        assert!(!is_valid_preset(" all"));      // leading space
    }

    // ── sections_for_preset ──────────────────────────────────────────────────

    #[test]
    fn test_sections_for_all_preset() {
        assert_eq!(sections_for_preset("all"), &["shared", "gaming", "coffee"]);
    }

    #[test]
    fn test_sections_for_base_preset() {
        assert_eq!(sections_for_preset("base"), &["shared", "base"]);
    }

    #[test]
    fn test_sections_for_gaming_preset() {
        assert_eq!(sections_for_preset("gaming"), &["shared", "gaming"]);
    }

    #[test]
    fn test_sections_for_coffee_preset() {
        assert_eq!(sections_for_preset("coffee"), &["shared", "base", "coffee"]);
    }

    // ── brand_for_preset ────────────────────────────────────────────────────

    #[test]
    fn test_brand_for_all_preset() {
        assert_eq!(brand_for_preset("all"), "Level Up Gaming Center");
    }

    #[test]
    fn test_brand_for_base_preset() {
        assert_eq!(brand_for_preset("base"), "Forge POS");
    }

    #[test]
    fn test_brand_for_gaming_preset() {
        assert_eq!(brand_for_preset("gaming"), "Level Up Gaming Center");
    }

    #[test]
    fn test_brand_for_coffee_preset() {
        assert_eq!(brand_for_preset("coffee"), "Forge POS");
    }

    // ── parse_sections ───────────────────────────────────────────────────────

    const MOCK_SEED: &str = r#"-- some leading comment before any section
-- that should be ignored

-- [SECTION:shared]
INSERT INTO suppliers VALUES (1, 'Test');

-- [SECTION:base]
INSERT INTO categories VALUES (1, 'Food');

-- [SECTION:gaming]
INSERT INTO categories VALUES (11, 'PS5');

-- [SECTION:coffee]
INSERT INTO categories VALUES (17, 'Coffee');
"#;

    #[test]
    fn test_parse_sections_returns_four_sections() {
        let sections = parse_sections(MOCK_SEED);
        assert_eq!(sections.len(), 4);
    }

    #[test]
    fn test_parse_sections_names_are_lowercase() {
        let sections = parse_sections(MOCK_SEED);
        let names: Vec<&str> = sections.iter().map(|(n, _)| n.as_str()).collect();
        assert_eq!(names, &["shared", "base", "gaming", "coffee"]);
    }

    #[test]
    fn test_parse_sections_each_has_content() {
        let sections = parse_sections(MOCK_SEED);
        for (name, lines) in &sections {
            assert!(!lines.is_empty(), "section [{name}] should have content");
        }
    }

    #[test]
    fn test_parse_sections_shared_has_suppliers() {
        let sections = parse_sections(MOCK_SEED);
        let shared = sections.iter().find(|(n, _)| n == "shared").unwrap();
        let text = shared.1.join("\n");
        assert!(text.contains("suppliers"), "shared should contain suppliers INSERT");
    }

    #[test]
    fn test_parse_sections_leading_comments_excluded() {
        let sections = parse_sections(MOCK_SEED);
        // Leading comments before [SECTION:shared] should not appear in any section
        let all_lines: Vec<&str> = sections.iter().flat_map(|(_, l)| l.iter().map(|s| s.as_str())).collect();
        assert!(!all_lines.iter().any(|l| l.contains("leading comment")));
    }

    #[test]
    fn test_parse_empty_content_yields_no_sections() {
        let sections = parse_sections("");
        assert!(sections.is_empty());
    }

    #[test]
    fn test_parse_no_section_markers_yields_no_sections() {
        let sections = parse_sections("INSERT INTO foo VALUES (1);\nINSERT INTO bar VALUES (2);");
        assert!(sections.is_empty());
    }

    #[test]
    fn test_parse_malformed_marker_is_ignored() {
        // Missing closing bracket — should not be treated as a section marker
        let sql = "-- [SECTION:shared\nSELECT 1;";
        let sections = parse_sections(sql);
        assert!(sections.is_empty());
    }

    // ── collect_active_lines ─────────────────────────────────────────────────

    #[test]
    fn test_collect_active_lines_includes_matching_sections() {
        let sections = parse_sections(MOCK_SEED);
        let lines = collect_active_lines(&sections, &["shared", "base"]);
        let text = lines.join("\n");
        assert!(text.contains("suppliers"));
        assert!(text.contains("'Food'"));
        assert!(!text.contains("'PS5'"));       // gaming excluded
        assert!(!text.contains("'Coffee'"));     // coffee excluded
    }

    #[test]
    fn test_collect_active_lines_all_sections() {
        let sections = parse_sections(MOCK_SEED);
        let lines = collect_active_lines(&sections, &["shared", "base", "gaming", "coffee"]);
        let text = lines.join("\n");
        assert!(text.contains("suppliers"));
        assert!(text.contains("'Food'"));
        assert!(text.contains("'PS5'"));
        assert!(text.contains("'Coffee'"));
    }

    #[test]
    fn test_collect_active_lines_empty_sections_list() {
        let sections = parse_sections(MOCK_SEED);
        let lines = collect_active_lines(&sections, &[]);
        assert!(lines.is_empty());
    }

    #[test]
    fn test_collect_active_lines_preserves_order() {
        let sections = parse_sections(MOCK_SEED);
        // Request in reverse order — should still get document order
        let lines = collect_active_lines(&sections, &["coffee", "shared"]);
        let text = lines.join("\n");
        // shared content should come before coffee content
        let shared_pos = text.find("suppliers").unwrap();
        let coffee_pos = text.find("'Coffee'").unwrap();
        assert!(shared_pos < coffee_pos, "shared should come before coffee");
    }

    // ── End-to-end: sections_for_preset + collect_active_lines ───────────────

    #[test]
    fn test_end_to_end_base_preset_gets_only_shared_and_base() {
        let sections = parse_sections(MOCK_SEED);
        let active = sections_for_preset("base");
        let lines = collect_active_lines(&sections, active);
        let text = lines.join("\n");
        assert!(text.contains("suppliers"));
        assert!(text.contains("'Food'"));
        assert!(!text.contains("'PS5'"));
        assert!(!text.contains("'Coffee'"));
    }

    #[test]
    fn test_end_to_end_gaming_preset_gets_only_shared_and_gaming() {
        let sections = parse_sections(MOCK_SEED);
        let active = sections_for_preset("gaming");
        let lines = collect_active_lines(&sections, active);
        let text = lines.join("\n");
        assert!(text.contains("suppliers"));
        assert!(text.contains("'PS5'"));
        assert!(!text.contains("'Food'"));
        assert!(!text.contains("'Coffee'"));
    }

    #[test]
    fn test_end_to_end_coffee_preset_gets_shared_base_and_coffee() {
        let sections = parse_sections(MOCK_SEED);
        let active = sections_for_preset("coffee");
        let lines = collect_active_lines(&sections, active);
        let text = lines.join("\n");
        assert!(text.contains("suppliers"));
        assert!(text.contains("'Food'"));
        assert!(text.contains("'Coffee'"));
        assert!(!text.contains("'PS5'"));
    }

    #[test]
    fn test_end_to_end_all_preset_gets_all_except_base() {
        let sections = parse_sections(MOCK_SEED);
        let active = sections_for_preset("all");
        let lines = collect_active_lines(&sections, active);
        let text = lines.join("\n");
        assert!(text.contains("suppliers"));  // shared
        assert!(text.contains("'PS5'"));       // gaming
        assert!(text.contains("'Coffee'"));    // coffee
        assert!(!text.contains("'Food'"));     // base excluded
    }
}
