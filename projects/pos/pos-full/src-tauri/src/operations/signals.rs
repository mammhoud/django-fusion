//! Change signal/event system for POS.
//!
//! Uses a global `tokio::sync::broadcast` channel to notify subscribers
//! when entities are created, updated, or deleted. Currently wired for:
//!
//! - **Settings** — emitted on `save_settings()`
//! - **Products** — emitted on `add_product()`, `update_product()`, `delete_product()`
//!
//! The cloud CRM server (pos-full/cloud/) and the sidecar can listen
//! for these events to trigger re-syncs or cache invalidations.
//!
//! ## Usage (subscriber)
//!
//! ```ignore
//! use crate::operations::signals::{ChangeEvent, subscribe};
//! let mut rx = subscribe();
//! tokio::spawn(async move {
//!     while let Ok(event) = rx.recv().await {
//!         match event {
//!             ChangeEvent::SettingsChanged => { /* re-sync settings */ }
//!             ChangeEvent::ProductUpdated(id) => { /* re-sync product */ }
//!             _ => {}
//!         }
//!     }
//! });
//! ```
//!
//! Related Names: signals, events, change, notification, broadcast
//! Tags: #signals #events #change #notification

use std::sync::LazyLock;
use tokio::sync::broadcast;

/// Capacity of the broadcast channel — after this many unconsumed
/// events the oldest ones are dropped (lagging subscribers catch up
/// by re-reading the source data).
const CHANNEL_CAPACITY: usize = 256;

/// Global broadcast sender.
static SENDER: LazyLock<broadcast::Sender<ChangeEvent>> = LazyLock::new(|| {
    let (tx, _) = broadcast::channel(CHANNEL_CAPACITY);
    tx
});

// ---------------------------------------------------------------------------
// Event type
// ---------------------------------------------------------------------------

/// A change event emitted when an entity is modified.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum ChangeEvent {
    // ── Settings ──────────────────────────────────────────────────────
    /// Restaurant settings were saved/updated.
    SettingsChanged,

    // ── Products ──────────────────────────────────────────────────────
    /// A new product was created.
    ProductCreated(i32),
    /// An existing product was updated.
    ProductUpdated(i32),
    /// A product was deleted.
    ProductDeleted(i32),

    // ── Catch-all ─────────────────────────────────────────────────────
    /// Generic entity change (entity_type, entity_id)
    EntityChanged(String, i32),
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/// Subscribe to change events.
///
/// Returns a `broadcast::Receiver` that can be `await`ed in a spawned task.
pub fn subscribe() -> broadcast::Receiver<ChangeEvent> {
    SENDER.subscribe()
}

/// Emit a change event to all subscribers.
///
/// If all receivers are lagging, the event is silently dropped.
pub fn emit(event: ChangeEvent) {
    let _ = SENDER.send(event);
}

/// Number of active subscribers.
pub fn subscriber_count() -> usize {
    SENDER.receiver_count()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_subscribe_and_emit() {
        let mut rx = subscribe();
        emit(ChangeEvent::SettingsChanged);
        let received = rx.try_recv().ok();
        assert_eq!(received, Some(ChangeEvent::SettingsChanged));
    }

    #[test]
    fn test_product_events() {
        let mut rx = subscribe();
        emit(ChangeEvent::ProductCreated(42));
        emit(ChangeEvent::ProductUpdated(7));
        emit(ChangeEvent::ProductDeleted(99));

        assert_eq!(rx.try_recv().ok(), Some(ChangeEvent::ProductCreated(42)));
        assert_eq!(rx.try_recv().ok(), Some(ChangeEvent::ProductUpdated(7)));
        assert_eq!(rx.try_recv().ok(), Some(ChangeEvent::ProductDeleted(99)));
    }

    #[test]
    fn test_entity_changed() {
        let mut rx = subscribe();
        emit(ChangeEvent::EntityChanged("sale".into(), 1));
        assert_eq!(
            rx.try_recv().ok(),
            Some(ChangeEvent::EntityChanged("sale".into(), 1))
        );
    }

    #[test]
    fn test_subscriber_count() {
        let _rx1 = subscribe();
        let _rx2 = subscribe();
        assert!(subscriber_count() >= 2);
    }
}
