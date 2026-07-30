# Forge POS — Tauri Plugins & Features Enhancement Plan

> **Generated:** 2026-07-30 | **Scope:** Tauri v2 backend + React frontend
> **Status:** ⬜ Research Complete — No Changes Made Yet

---

## Current State Audit

### Plugins Already in Cargo.toml
| Plugin | Status | Current Use |
|--------|:------:|-------------|
| `tauri-plugin-dialog` | ✅ Active | File save dialogs for exports (PDF, CSV, Excel) |
| `tauri-plugin-fs` | ✅ Active | Filesystem access for media, logs, backups |
| `tauri-plugin-shell` | ✅ Active | Shell commands (sidecar, sendmail for support) |
| `tauri-plugin-opener` | ✅ Active | Open URLs/files in default OS handler |
| `tray-icon` (feature) | ✅ Enabled | Feature flag only — no tray implementation yet |

### Plugins NOT in Use (14 candidates)

| Plugin | Docs |
|--------|------|
| `tauri-plugin-autostart` | https://tauri.app/plugin/autostart/ |
| `tauri-plugin-global-shortcut` | https://tauri.app/plugin/global-shortcut/ |
| `tauri-plugin-localhost` | https://tauri.app/plugin/localhost/ |
| `tauri-plugin-logging` | https://tauri.app/plugin/logging/ |
| `tauri-plugin-notification` | https://tauri.app/plugin/notification/ |
| `tauri-plugin-os-info` | https://tauri.app/plugin/os-info/ |
| `tauri-plugin-persisted-scope` | https://tauri.app/plugin/persisted-scope/ |
| `tauri-plugin-positioner` | https://tauri.app/plugin/positioner/ |
| `tauri-plugin-single-instance` | https://tauri.app/plugin/single-instance/ |
| `tauri-plugin-store` | https://tauri.app/plugin/store/ |
| System Tray | https://tauri.app/learn/system-tray/ |
| Window Customization | https://tauri.app/learn/window-customization/ |
| Window Menu | https://tauri.app/learn/window-menu/ |

---

## Enhancement Roadmap

### 🔴 Tier 1 — Essential (High Impact, Low Effort)

#### 1. Single Instance (`tauri-plugin-single-instance`)
**Link:** https://tauri.app/plugin/single-instance/

**Use Case:** Prevent users from accidentally opening multiple POS instances, which could cause database conflicts, duplicate orders, and confusion.

**Implementation:**
```rust
// src-tauri/src/lib.rs
app.handle().plugin(tauri_plugin_single_instance::init(|app, argv, cwd| {
    // Focus the existing window when a second instance is launched
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.set_focus();
        let _ = window.show();
    }
}));
```
```toml
# Cargo.toml
tauri-plugin-single-instance = "2"
```

**UX:** Second launch → existing window focuses and comes to front.

---

#### 2. Native Notifications (`tauri-plugin-notification`)
**Link:** https://tauri.app/plugin/notification/

**Use Cases:**
- **KDS (Kitchen Display):** Notify when new orders arrive — even if KDS window is minimized
- **Low Stock Alerts:** Notify when ingredients fall below reorder level
- **Order Ready:** Notify waitstaff when kitchen marks an order "ready"
- **Shift Reminders:** Notify employees 15 min before shift starts
- **Backup Reminder:** Notify to perform daily database backup

**Implementation:**
```typescript
// src/hooks/useNativeNotification.ts
import { isPermissionGranted, requestPermission, sendNotification } from '@tauri-apps/plugin-notification';

export function useNativeNotification() {
  const notify = async (title: string, body: string) => {
    let granted = await isPermissionGranted();
    if (!granted) {
      const perm = await requestPermission();
      granted = perm === 'granted';
    }
    if (granted) {
      sendNotification({ title, body });
    }
  };
  return { notify };
}
```

**Integration Points:**
- `useKDSNotification.ts` — replace audio-only with native notifications
- `Inventory.tsx` — low stock threshold crossing
- `KitchenDisplay.tsx` — new ticket arrival
- `Settings.tsx` — notification preferences toggle

**Settings UI:**
- Toggle: "Enable desktop notifications"
- Per-category toggles: Orders, Inventory, Shifts, Backups

---

#### 3. Persistent Store (`tauri-plugin-store`)
**Link:** https://tauri.app/plugin/store/

**Use Cases:**
- **Settings Persistence:** Replace localStorage with a typed, synced key-value store
- **User Preferences:** Theme variant, language, KDS sort order, chime variant
- **Window State:** Remember last window position, size, and monitor
- **Recent Items:** Recently viewed products, recipes, customers
- **Draft Recovery:** Auto-save unsent orders, incomplete forms

**Implementation:**
```typescript
// src/lib/store.ts
import { Store } from '@tauri-apps/plugin-store';

const store = new Store('settings.json');

export async function getSetting<T>(key: string, fallback: T): Promise<T> {
  const val = await store.get<T>(key);
  return val ?? fallback;
}

export async function setSetting<T>(key: string, value: T): Promise<void> {
  await store.set(key, value);
  await store.save();
}
```

**Migration Path:**
1. Create `settings.json` store
2. Migrate localStorage keys → store keys on first launch
3. Update Settings.tsx, ThemeContext, LanguageContext, CurrencyContext to use store
4. Keep localStorage as fallback for backwards compat

---

### 🟡 Tier 2 — High Value (Moderate Effort)

#### 4. Global Shortcuts (`tauri-plugin-global-shortcut`)
**Link:** https://tauri.app/plugin/global-shortcut/

**Use Cases:**
- **Quick Sale:** `Ctrl+Shift+N` → open new sale from anywhere
- **KDS Toggle:** `Ctrl+Shift+K` → show/hide kitchen display
- **Quick Search:** `Ctrl+Shift+F` → global product/customer search
- **Lock Station:** `Ctrl+Shift+L` → lock POS (require PIN to unlock)
- **Emergency Print:** `Ctrl+Shift+P` → print last receipt

**Implementation:**
```typescript
// src/hooks/useGlobalShortcuts.ts
import { register } from '@tauri-apps/plugin-global-shortcut';

export function useGlobalShortcuts(shortcuts: Record<string, () => void>) {
  useEffect(() => {
    const unregisters: (() => void)[] = [];
    for (const [key, handler] of Object.entries(shortcuts)) {
      register(key, handler).then(unreg => unregisters.push(unreg));
    }
    return () => unregisters.forEach(fn => fn());
  }, []);
}
```

**Settings UI:**
- Shortcut configuration panel in Settings → Keyboard
- Show current shortcuts, allow custom rebinding
- Conflict detection (two actions can't share same shortcut)

---

#### 5. System Tray (`tray-icon` — already in Cargo.toml features)
**Link:** https://tauri.app/learn/system-tray/

**Use Cases:**
- **Minimize to Tray:** Close button minimizes to tray instead of quitting
- **Quick Actions:** Right-click tray icon → New Sale, Open KDS, Lock Station
- **Status Indicator:** Tray icon changes color based on state (green=idle, yellow=order pending, red=error)
- **Background Operation:** Keep POS running in background for notifications/updates

**Implementation:**
```rust
// src-tauri/src/lib.rs
use tauri::tray::{TrayIconBuilder, MenuBuilder, MenuItemBuilder};

let tray_menu = MenuBuilder::new(app)
    .item(&MenuItemBuilder::with_id("new_sale", "New Sale").build(app)?)
    .item(&MenuItemBuilder::with_id("kds", "Kitchen Display").build(app)?)
    .separator()
    .item(&MenuItemBuilder::with_id("lock", "Lock Station").build(app)?)
    .item(&MenuItemBuilder::with_id("quit", "Quit").build(app)?)
    .build()?;

TrayIconBuilder::new()
    .menu(&tray_menu)
    .tooltip("Forge POS")
    .on_menu_event(|app, event| { /* handle menu clicks */ })
    .build(app)?;
```

---

#### 6. Window Menu (`@tauri-apps/api/menu`)
**Link:** https://tauri.app/learn/window-menu/

**Use Cases:**
- **Native Menu Bar:** File (New Sale, Export, Print, Quit), Edit (Undo, Redo, Preferences), View (KDS, Reports, Fullscreen), Help (About, Support, Shortcuts)
- **Keyboard Shortcuts in Menu:** Show shortcut hints (e.g., "New Sale  ⌘N")
- **Platform Consistency:** macOS app menu, Windows/Linux window menu

---

### 🟢 Tier 3 — Nice to Have (Lower Priority)

#### 7. Auto-Start (`tauri-plugin-autostart`)
**Link:** https://tauri.app/plugin/autostart/

**Use Case:** Restaurant POS terminals auto-launch on boot — no need for staff to manually start the app.

**Settings UI:** Toggle "Launch at system startup" in Settings → General.

---

#### 8. OS Info (`tauri-plugin-os-info`)
**Link:** https://tauri.app/plugin/os-info/

**Use Case:** Detect OS for platform-specific behavior (e.g., macOS menu bar, Windows taskbar, Linux notifications). Show in About page: "Forge POS v0.1.0 on macOS 15.0 (arm64)".

---

#### 9. Logging (`tauri-plugin-logging`)
**Link:** https://tauri.app/plugin/logging/

**Use Case:** Structured backend logging for debugging. Write to `~/.forge-pos/logs/` with rotation. Essential for support/troubleshooting.

---

#### 10. Window Customization
**Link:** https://tauri.app/learn/window-customization/

**Use Cases:**
- **Frameless KDS Window:** Custom titlebar for kitchen display (immersive, minimal chrome)
- **Transparent Overlay:** Floating calculator or quick-sale widget
- **Always on Top:** KDS window stays visible above other apps
- **Shadow Control:** Consistent shadow appearance across platforms

---

#### 11. Positioner (`tauri-plugin-positioner`)
**Link:** https://tauri.app/plugin/positioner/

**Use Case:** Auto-position KDS window on a second monitor (kitchen display screen). "Move KDS to secondary display" button.

---

#### 12. Persisted Scope (`tauri-plugin-persisted-scope`)
**Link:** https://tauri.app/plugin/persisted-scope/

**Use Case:** Remember user-selected export folders across sessions. "Always save reports to Desktop/Reports/".

---

#### 13. Localhost (`tauri-plugin-localhost`)
**Link:** https://tauri.app/plugin/localhost/

**Use Case:** Expose a local API for third-party integrations (e.g., online ordering platform pushes orders to POS via localhost). **Note:** Only if sidecar is insufficient.

---

## Feature Mapping by Page

| Page/Feature | Plugins Needed |
|-------------|---------------|
| **Settings → General** | autostart, os-info (about), logging (debug toggle) |
| **Settings → Notifications** | notification (permissions, categories) |
| **Settings → Keyboard** | global-shortcut (shortcut config) |
| **Settings → Appearance** | store (theme/locale persistence) |
| **KitchenDisplay** | notification (new orders), positioner (second screen) |
| **Inventory** | notification (low stock alerts) |
| **Sale** | global-shortcut (quick sale) |
| **Auth / Login** | global-shortcut (lock station) |
| **App Shell** | single-instance, system-tray, window-menu, window-customization |
| **All Pages** | store (settings), logging (debug) |

---

## Implementation Order (Recommended)

### Phase 1 — Foundation (Tier 1)
1. **`single-instance`** — 30 min — prevent duplicate instances
2. **`store`** — 1 hour — typed settings persistence, migrate from localStorage
3. **`notification`** — 1 hour — KDS alerts, low stock, order ready

### Phase 2 — Power Features (Tier 2)
4. **`global-shortcut`** — 1.5 hours — quick actions from anywhere
5. **System Tray** — 2 hours — minimize to tray, quick actions
6. **Window Menu** — 1 hour — native menu bar with shortcuts

### Phase 3 — Polish (Tier 3)
7. **`autostart`** — 30 min — launch on boot for dedicated terminals
8. **`os-info`** — 15 min — About page platform info
9. **`logging`** — 30 min — structured backend logs
10. **Window Customization** — 1 hour — frameless KDS, always-on-top
11. **`positioner`** — 30 min — KDS on second monitor
12. **`persisted-scope`** — 15 min — remember export folders
13. **`localhost`** — evaluate if needed later

---

## Before Implementing: Pre-Flight Checklist

- [ ] Read each plugin's Tauri v2 migration guide (APIs changed from v1)
- [ ] Check plugin compatibility with current Tauri v2.x version in Cargo.toml
- [ ] Test each plugin in isolation before combining
- [ ] Add capability permissions in `src-tauri/capabilities/default.json`
- [ ] Update `tauri.conf.json` `plugins` section for each new plugin
- [ ] Verify frontend `@tauri-apps/plugin-*` npm packages match Cargo versions
- [ ] Run `cargo build` after each plugin addition to catch Rust compile errors early
- [ ] Test on all target platforms (Windows, macOS, Linux) — especially notifications and tray

---

## Files That Will Change

| File | Changes |
|------|---------|
| `src-tauri/Cargo.toml` | Add plugin dependencies |
| `src-tauri/src/lib.rs` | Initialize plugins, tray icon, menu |
| `src-tauri/tauri.conf.json` | Window customization, plugin config |
| `src-tauri/capabilities/default.json` | Permission scopes for each plugin |
| `src/hooks/useNativeNotification.ts` | New — notification helper hook |
| `src/hooks/useGlobalShortcuts.ts` | New — global shortcut hook |
| `src/lib/store.ts` | New — typed store wrapper |
| `src/pages/settings/Settings.tsx` | Notification prefs, shortcut config, autostart toggle |
| `src/pages/kitchen/KitchenDisplay.tsx` | Native notification integration |
| `src/pages/dashboard/Home.tsx` | Quick actions from tray/shortcuts |
| `src/App.tsx` | Single instance handler, tray setup |
| `package.json` | Add `@tauri-apps/plugin-*` npm packages |
