// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Welcome to Formint Client, {}! The register is ready.", name)
}

/// Opens the OS native print dialog for the focused window.
///
/// Used by the receipt view: the webview's print pipeline renders the
/// receipt through the same `@media print` stylesheet, but the dialog
/// itself is the platform's native one (unlike `window.print()`).
#[tauri::command]
fn print_receipt(window: tauri::WebviewWindow) -> Result<(), String> {
    window.print().map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::new().build())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, print_receipt])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
