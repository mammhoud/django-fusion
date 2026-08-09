//! Sidecar lifecycle management for the POS Django backend.
//!
//! The sidecar is a PyInstaller-bundled executable located at
//!   `<app resources>/binaries/pos-sidecar-<target-triple>`
//! Tauri's ExternalBin mechanism appends the target triple automatically.
//!
//! The sidecar is started once on app launch (via `setup`) and
//! kept alive in a global `OnceCell`. The frontend can also call
//! `start_sidecar` / `stop_sidecar` / `sidecar_status` via `invoke()`.
//!
//! Communication between the React frontend and the sidecar happens
//! over `http://127.0.0.1:8765` (HTTP REST + WebSocket). The Rust
//! side only manages the process lifecycle.
//!
//! In development the bundled binary is a placeholder (see
//! `binaries/pos-sidecar-*`) that satisfies `externalBin` validation and
//! exits immediately, so the desktop app runs without a backend until the
//! real sidecar is built via `pnpm build:sidecar`.

use once_cell::sync::OnceCell;
use std::sync::Mutex;
use tauri::{AppHandle, Manager};
use tauri_plugin_shell::{process::CommandChild, ShellExt};

// ---- Global process handle -------------------------------------------------

/// Holds the running sidecar process. `None` when not started.
static SIDECAR_PROCESS: OnceCell<Mutex<Option<CommandChild>>> = OnceCell::new();

fn process_cell() -> &'static Mutex<Option<CommandChild>> {
    SIDECAR_PROCESS.get_or_init(|| Mutex::new(None))
}

// ---- Public commands -------------------------------------------------------

/// Start the Python sidecar. Idempotent — calling it while it is already
/// running returns `Ok` without spawning a second process.
#[tauri::command]
pub fn start_sidecar(app: AppHandle) -> Result<String, String> {
    let mut guard = process_cell()
        .lock()
        .map_err(|e| format!("lock poisoned: {e}"))?;

    if guard.is_some() {
        return Ok("already running".to_string());
    }

    // Django development server road (replaces the removed Robyn `server.py`).
    let args = vec!["runserver", "127.0.0.1:8765", "--noreload"];

    // Try the bundled sidecar first; fall back to python in development.
    let (mut rx, child) = if let Ok(cmd) = app.shell().sidecar("pos-sidecar") {
        cmd.args(args.clone()).spawn()
            .map_err(|e| format!("sidecar spawn error: {e}"))?
    } else {
        eprintln!("[sidecar] bundled binary not found, falling back to python");
        let project_dir = std::env::current_dir()
            .map_err(|e| format!("current dir: {e}"))?;
        // Prefer the virtual environment Python so that dependencies
        // (django, django-bolt, channels, etc.) installed in .venv are available.
        let python_cmd = if cfg!(windows) {
            let venv_python = project_dir.join(".venv").join("Scripts").join("python.exe");
            if venv_python.exists() { venv_python.to_string_lossy().into_owned() } else { "python".to_string() }
        } else {
            let venv_python = project_dir.join(".venv").join("bin").join("python");
            if venv_python.exists() { venv_python.to_string_lossy().into_owned() } else { "python3".to_string() }
        };
        app.shell()
            .command(&python_cmd)
            .current_dir(project_dir)
            .args([&["sidecar/sidecar.py"], &args[..]].concat())
            .spawn()
            .map_err(|e| format!("{python_cmd} sidecar spawn error: {e}"))?
    };

    // Pipe stdout/stderr to the Tauri dev console in debug builds and
    // clear the global handle when the process terminates so it can be restarted.
    #[cfg(debug_assertions)]
    {
        use tauri_plugin_shell::process::CommandEvent;
        tauri::async_runtime::spawn(async move {
            while let Some(event) = rx.recv().await {
                match event {
                    CommandEvent::Stdout(line) => {
                        let _ = String::from_utf8(line)
                            .map(|s| eprintln!("[sidecar stdout] {s}"));
                    }
                    CommandEvent::Stderr(line) => {
                        let _ = String::from_utf8(line)
                            .map(|s| eprintln!("[sidecar stderr] {s}"));
                    }
                    CommandEvent::Terminated(status) => {
                        eprintln!("[sidecar] terminated: {:?}", status);
                        let _ = process_cell().lock().map(|mut g| g.take());
                        break;
                    }
                    _ => {}
                }
            }
        });
    }

    // In release builds we still need to consume the receiver or the
    // channel will fill and block the sidecar process.
    #[cfg(not(debug_assertions))]
    {
        use tauri_plugin_shell::process::CommandEvent;
        tauri::async_runtime::spawn(async move {
            while let Some(event) = rx.recv().await {
                if let CommandEvent::Terminated(_) = event {
                    let _ = process_cell().lock().map(|mut g| g.take());
                    break;
                }
            }
        });
    }

    *guard = Some(child);
    Ok("started".to_string())
}

/// Stop the running sidecar process.
#[tauri::command]
pub fn stop_sidecar() -> Result<String, String> {
    let mut guard = process_cell()
        .lock()
        .map_err(|e| format!("lock poisoned: {e}"))?;

    if let Some(child) = guard.take() {
        child
            .kill()
            .map_err(|e| format!("failed to kill sidecar: {e}"))?;
        return Ok("stopped".to_string());
    }
    Ok("not running".to_string())
}

/// Return whether the sidecar process is currently running.
#[tauri::command]
pub fn sidecar_status() -> Result<String, String> {
    let guard = process_cell()
        .lock()
        .map_err(|e| format!("lock poisoned: {e}"))?;
    if guard.is_some() {
        Ok("running".to_string())
    } else {
        Ok("stopped".to_string())
    }
}
