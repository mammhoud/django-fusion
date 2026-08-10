/// Hardware integration — thermal printer & cash drawer via serial/USB.
///
/// Uses raw ESC/POS commands sent over a serial port (typically a USB-to-serial
/// adapter for thermal printers).  Cash drawer is triggered through the printer's
/// RJ12 kick connector using standard ESC/POS drawer-kick commands.
///
/// Port configuration is stored in the `settings` table as `printer_port` and
/// `printer_enabled` columns.  When no port is configured, commands return
/// `Err` with a descriptive message rather than panicking.

use std::path::PathBuf;
use std::io::Write;

fn write_bytes(file: &mut std::fs::File, bytes: &[u8]) -> Result<(), String> {
    file.write_all(bytes).map_err(|e| e.to_string())
}

// ── ESC/POS Command constants ──────────────────────────────────────────────

/// Initialize printer (reset to default)
const ESC_INIT: &[u8] = b"\x1b\x40";

/// Cash drawer kick — pulse pin 2 for 250ms (standard RJ12 drawer trigger)
const ESC_DRAWER_KICK: &[u8] = b"\x1b\x70\x00\x19\xfa";

/// Cut paper (partial cut — leaves a small tab)
const ESC_CUT_PAPER: &[u8] = b"\x1d\x56\x42\x00";

/// Bold on / off
const ESC_BOLD_ON: &[u8] = b"\x1b\x45\x01";
const ESC_BOLD_OFF: &[u8] = b"\x1b\x45\x00";

/// Double width / height
const ESC_DOUBLE_ON: &[u8] = b"\x1b\x21\x30";
const ESC_DOUBLE_OFF: &[u8] = b"\x1b\x21\x00";

/// Center / left align
const ESC_ALIGN_CENTER: &[u8] = b"\x1b\x61\x01";
const ESC_ALIGN_LEFT: &[u8] = b"\x1b\x61\x00";

/// Line feed
const ESC_LF: &[u8] = b"\x0a";

/// Dashed separator line
const SEPARATOR: &str = "--------------------------------";

// ── Printer port helpers ────────────────────────────────────────────────────

/// Read the configured printer port from settings.
fn get_printer_port(db_path: &PathBuf) -> Result<Option<String>, String> {
    use diesel::prelude::*;
    use crate::db::open_conn;
    use crate::db::schema::settings::dsl::*;

    let mut conn = open_conn(db_path)?;
    let port: Option<String> = settings
        .select(printer_port)
        .first(&mut conn)
        .map_err(|e| e.to_string())?;

    match port {
        Some(p) if !p.is_empty() => Ok(Some(p)),
        _ => Ok(None),
    }
}

/// Open a serial port and return a write handle.
/// Uses simple std::fs::File on Unix (e.g., /dev/ttyUSB0) or Windows (COM3).
#[cfg(not(any(target_os = "android", target_os = "ios")))]
fn open_serial_port(port_path: &str) -> Result<std::fs::File, String> {
    use std::fs::OpenOptions;
    OpenOptions::new()
        .write(true)
        .open(port_path)
        .map_err(|e| format!("Cannot open printer port '{}': {}", port_path, e))
}

#[cfg(any(target_os = "android", target_os = "ios"))]
fn open_serial_port(_port_path: &str) -> Result<std::fs::File, String> {
    Err("Serial port not available on mobile platforms".into())
}

// ── Public API ──────────────────────────────────────────────────────────────

/// Trigger the cash drawer attached to the thermal printer.
///
/// Sends a drawer-kick pulse sequence over the configured serial port.
/// The drawer is typically connected to the printer via an RJ12 cable.
pub fn trigger_cash_drawer(db_path: &PathBuf) -> Result<(), String> {
    let active_shift = crate::operations::shifts::get_active_shift(db_path)?;
    if active_shift.is_none() {
        return Err("Open a cash shift before opening the drawer.".to_string());
    }

    let port = get_printer_port(db_path)?
        .ok_or_else(|| "Printer port not configured. Set it in Settings → Database → Printer Port.".to_string())?;

    let mut file = open_serial_port(&port)?;
    write_bytes(&mut file, ESC_INIT)?;
    std::thread::sleep(std::time::Duration::from_millis(100));
    write_bytes(&mut file, ESC_DRAWER_KICK)?;
    file.flush().map_err(|e| e.to_string())?;

    Ok(())
}

/// Format and send a receipt to the thermal printer.
///
/// `lines` contains pre-formatted receipt text lines.  The function wraps
/// them in ESC/POS formatting commands (center-align header, bold totals,
/// paper cut at end).
pub fn print_thermal_receipt(
    db_path: &PathBuf,
    header: &str,
    lines: &[String],
    footer: &str,
) -> Result<(), String> {
    let port = get_printer_port(db_path)?
        .ok_or_else(|| "Printer port not configured. Set it in Settings → Database → Printer Port.".to_string())?;

    let mut file = open_serial_port(&port)?;

    // Initialize
    write_bytes(&mut file, ESC_INIT)?;
    std::thread::sleep(std::time::Duration::from_millis(50));

    // Header — center aligned, bold, double-width
    write_bytes(&mut file, ESC_ALIGN_CENTER)?;
    write_bytes(&mut file, ESC_DOUBLE_ON)?;
    write_bytes(&mut file, ESC_BOLD_ON)?;
    write_bytes(&mut file, header.as_bytes())?;
    write_bytes(&mut file, ESC_LF)?;
    write_bytes(&mut file, ESC_BOLD_OFF)?;
    write_bytes(&mut file, ESC_DOUBLE_OFF)?;
    write_bytes(&mut file, ESC_LF)?;

    // Separator
    write_bytes(&mut file, ESC_ALIGN_CENTER)?;
    write_bytes(&mut file, SEPARATOR.as_bytes())?;
    write_bytes(&mut file, ESC_LF)?;

    // Body — left aligned
    write_bytes(&mut file, ESC_ALIGN_LEFT)?;
    for line in lines {
        write_bytes(&mut file, line.as_bytes())?;
        write_bytes(&mut file, ESC_LF)?;
    }

    // Separator
    write_bytes(&mut file, ESC_ALIGN_CENTER)?;
    write_bytes(&mut file, SEPARATOR.as_bytes())?;
    write_bytes(&mut file, ESC_LF)?;

    // Footer — center aligned
    write_bytes(&mut file, ESC_ALIGN_CENTER)?;
    write_bytes(&mut file, footer.as_bytes())?;
    write_bytes(&mut file, ESC_LF)?;
    write_bytes(&mut file, ESC_LF)?;

    // Cut paper
    write_bytes(&mut file, ESC_CUT_PAPER)?;
    file.flush().map_err(|e| e.to_string())?;

    Ok(())
}

/// Check if a printer port is configured and accessible.
pub fn check_printer_status(db_path: &PathBuf) -> Result<String, String> {
    match get_printer_port(db_path)? {
        Some(port) => {
            // Try opening the port briefly to verify it's accessible
            match open_serial_port(&port) {
                Ok(_) => Ok(format!("Printer ready on {}", port)),
                Err(e) => Ok(format!("Port configured ({}) but not accessible: {}", port, e)),
            }
        }
        None => Ok("No printer port configured".to_string()),
    }
}
