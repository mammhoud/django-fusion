# POS Editions

## Comparison

| Feature | pos-full | pos-solo | pos-mini |
|---------|----------|----------|----------|
| **Tauri shell** | ✅ | ✅ | ✅ |
| **React frontend** | ✅ | ✅ | ✅ |
| **Rust backend** | ✅ | ✅ | ✅ |
| **Python sidecar** | ✅ | ✅ | ❌ |
| **Cloud sync** | ✅ | ❌ | ❌ |
| **Multi-node** | ✅ | ❌ | ❌ |
| **Django ORM** | ✅ (sidecar) | ✅ (sidecar) | ❌ |
| **WebSocket** | ✅ | ✅ | ❌ |
| **POS preset** | all/base/gaming/coffee | retail | basic |
| **Port** | 1420 | 1420 | 1420 |

## Architecture Per Edition

### pos-full (Cloud Master)
```
React → Tauri Commands → Rust/Diesel → SQLite
React → HTTP/WS → Robyn Sidecar → Django ORM → SQLite
     → Sync Engine → Multi-node replication
     → Cloud Links → External CRM/ERP
```

### pos-solo (Standalone)
```
React → Tauri Commands → Rust/Diesel → SQLite
React → HTTP/WS → Robyn Sidecar → Django ORM → SQLite
```

### pos-mini (Minimal)
```
React → Tauri Commands → Rust/Diesel → SQLite
```

## Preset Configurations (pos-full)

| Preset | Brand | Products |
|--------|-------|----------|
| `all` | Level Up Gaming Center | base + gaming + coffee |
| `base` | POS KO | Core POS products |
| `gaming` | Level Up Gaming Center | Gaming station products |
| `coffee` | The Daily Grind | Coffee shop products |
