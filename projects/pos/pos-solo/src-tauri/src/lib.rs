pub mod operations;
pub mod email;

use operations::sidecar::{start_sidecar, stop_sidecar, sidecar_status};
use tauri::{AppHandle, Manager};

// Load environment variables at startup
fn load_env() {
    if let Err(e) = dotenvy::dotenv() {
        eprintln!("Warning: Could not load .env file: {}", e);
    }
}

// ---- Sidecar lifecycle commands ----
#[tauri::command]
fn start_support_sidecar(app: AppHandle) -> Result<String, String> {
    operations::sidecar::start_sidecar(app)
}

// ---- Support email ----
#[tauri::command]
fn send_support_email(
    name: String,
    email: String,
    subject: String,
    message: String,
) -> Result<(), String> {
    email::send_support_email(name, email, subject, message)
}

// Helper function to get window state file path (desktop only)
fn get_window_state_path(app: &AppHandle) -> Result<std::path::PathBuf, String> {
    let app_dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&app_dir).map_err(|e| e.to_string())?;
    Ok(app_dir.join("window_state.json"))
}

fn save_window_state(app: &AppHandle, is_maximized: bool) -> Result<(), String> {
    let path = get_window_state_path(app)?;
    let state = serde_json::json!({ "is_maximized": is_maximized });
    std::fs::write(path, serde_json::to_string_pretty(&state).unwrap())
        .map_err(|e| e.to_string())
}

fn load_window_state(app: &AppHandle) -> Result<bool, String> {
    let path = get_window_state_path(app)?;
    if path.exists() {
        let content = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        let state: serde_json::Value = serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(state.get("is_maximized").and_then(|v| v.as_bool()).unwrap_or(false))
    } else {
        Ok(false)
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    load_env();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Auto-start the Python/Robyn sidecar
            #[cfg(not(any(target_os = "android", target_os = "ios")))]
            {
                if let Err(e) = start_sidecar(app.handle().clone()) {
                    eprintln!("[setup] sidecar start failed (non-fatal): {e}");
                }
            }

            // Setup window state management (desktop only)
            #[cfg(not(any(target_os = "android", target_os = "ios")))]
            {
                let window = app.get_webview_window("main").unwrap();
                let is_maximized = load_window_state(&app.handle()).unwrap_or(false);
                if is_maximized {
                    let _ = window.maximize();
                }
                let window_clone = window.clone();
                let app_handle = app.handle().clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::Resized(_) = event {
                        if let Ok(is_maximized) = window_clone.is_maximized() {
                            let _ = save_window_state(&app_handle, is_maximized);
                        }
                    }
                });
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            start_sidecar,
            stop_sidecar,
            sidecar_status,
            start_support_sidecar,
            send_support_email,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
