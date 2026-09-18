pub mod native;
pub mod server;

use std::fs;
use tauri::{AppHandle, Manager};

fn window_state_path(app: &AppHandle) -> Result<std::path::PathBuf, String> {
    let directory = app.path().app_data_dir().map_err(|error| error.to_string())?;
    fs::create_dir_all(&directory).map_err(|error| error.to_string())?;
    Ok(directory.join("window-state.json"))
}

fn restore_window_state(app: &AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or_else(|| "main window is not available".to_string())?;
    let path = window_state_path(app)?;
    if !path.exists() {
        return Ok(());
    }

    let content = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let state: serde_json::Value = serde_json::from_str(&content).map_err(|error| error.to_string())?;
    if state
        .get("maximized")
        .and_then(serde_json::Value::as_bool)
        .unwrap_or(false)
    {
        window.maximize().map_err(|error| error.to_string())?;
    }
    Ok(())
}

fn persist_window_state(app: &AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or_else(|| "main window is not available".to_string())?;
    let state = serde_json::json!({ "maximized": window.is_maximized().unwrap_or(false) });
    fs::write(window_state_path(app)?, serde_json::to_vec_pretty(&state).map_err(|e| e.to_string())?)
        .map_err(|error| error.to_string())
}

#[tauri::command]
fn start_formint_server(app: AppHandle) -> Result<String, String> {
    server::start(&app)
}

#[tauri::command]
fn stop_formint_server() -> Result<String, String> {
    server::stop()
}

#[tauri::command]
fn formint_server_status() -> Result<String, String> {
    server::status()
}

#[tauri::command]
fn native_capabilities() -> native::NativeCapabilities {
    native::NativeCapabilities::default()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            if let Err(error) = restore_window_state(app.handle()) {
                eprintln!("[formint] window restore skipped: {error}");
            }
            if let Err(error) = server::start(app.handle()) {
                eprintln!("[formint] server auto-start skipped: {error}");
            }
            Ok(())
        })
        .on_window_event(|window, event| {
            if matches!(event, tauri::WindowEvent::Resized(_)) {
                if let Err(error) = persist_window_state(&window.app_handle()) {
                    eprintln!("[formint] window state save skipped: {error}");
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            start_formint_server,
            stop_formint_server,
            formint_server_status,
            native_capabilities,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Formint POS");
}
