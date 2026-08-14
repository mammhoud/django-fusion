use once_cell::sync::OnceCell;
use std::sync::Mutex;
use tauri::AppHandle;
use tauri_plugin_shell::{process::CommandChild, ShellExt};

static PROCESS: OnceCell<Mutex<Option<CommandChild>>> = OnceCell::new();

fn process() -> &'static Mutex<Option<CommandChild>> {
    PROCESS.get_or_init(|| Mutex::new(None))
}

pub fn start(app: &AppHandle) -> Result<String, String> {
    let mut guard = process().lock().map_err(|error| error.to_string())?;
    if guard.is_some() {
        return Ok("already-running".to_string());
    }

    let command = app
        .shell()
        .sidecar("formint-backend")
        .map_err(|error| format!("formint-backend server is not bundled: {error}"))?;
    let (events, child) = command
        .args(["runserver", "127.0.0.1:8767", "--noreload"])
        .spawn()
        .map_err(|error| format!("formint-backend failed to start: {error}"))?;

    // Drain stdout/stderr events in background to prevent pipe buffer deadlock
    tauri::async_runtime::spawn(async move {
        let mut rx = events;
        loop {
            match rx.recv().await {
                Some(_event) => { /* log in production */ }
                None => break,
            }
        }
    });

    *guard = Some(child);
    Ok("started".to_string())
}

pub fn stop() -> Result<String, String> {
    let mut guard = process().lock().map_err(|error| error.to_string())?;
    match guard.take() {
        Some(child) => {
            child.kill().map_err(|error| error.to_string())?;
            Ok("stopped".to_string())
        }
        None => Ok("not-running".to_string()),
    }
}

pub fn status() -> Result<String, String> {
    let guard = process().lock().map_err(|error| error.to_string())?;
    Ok(if guard.is_some() { "running" } else { "stopped" }.to_string())
}
