use serde::Serialize;

/// Native operations exposed by Tauri plugins. Business rules stay in Django.
#[derive(Debug, Clone, Serialize)]
pub struct NativeCapabilities {
    pub printing: bool,
    pub scanning: bool,
    pub filesystem: bool,
    pub device_events: bool,
}

impl Default for NativeCapabilities {
    fn default() -> Self {
        Self {
            printing: false,
            scanning: false,
            filesystem: true,
            device_events: false,
        }
    }
}

// Future native plugins should implement one capability at a time and expose
// typed commands here. Do not duplicate catalog, order, payment, or sync logic.
