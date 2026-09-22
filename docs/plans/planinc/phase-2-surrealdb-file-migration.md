# Phase 2 — SurrealDB Embedded File Migration

**Status:** Planned — immediate priority  
**Scope:** `application/tools/PlanInc/runtime/`, `docker-compose.yml`, `verify-surrealdb.sh`  
**Owner:** Backend / Infrastructure  
**Depends on:** Phase 0 complete  
**Blocks:** Phase 3, Phase 4 (can proceed in parallel)

---

## Objective

Replace the SurrealDB **network server container** with SurrealDB in
**embedded file mode** (`file://path/planinc.db`) via the JS SDK — the same
query API, zero containers, zero network port, database stored as a local file
like SQLite.

---

## Current State

`docker-compose.yml` runs two containers:

```yaml
services:
  surrealdb:           # ← TO REMOVE
    image: surrealdb/surrealdb:v1.5.6
    command: start --auth --user root --pass ${SURREALDB_PASS} file:/data/planinc.db
    ports: ["8000:8000"]
    volumes: [planing-surreal-data:/data]

  planing:
    depends_on: surrealdb
    environment:
      SURREALDB_URL: http://surrealdb:8000/rpc   # ← TO REMOVE
      SURREALDB_USER: root                        # ← TO REMOVE
      SURREALDB_PASS: ${SURREALDB_PASS:-planing}  # ← TO REMOVE
```

`runtime/server.mjs` connection:

```js
import { Surreal, RecordId, StringRecordId } from 'surrealdb';  // v1.x
const surrealUrl = process.env.SURREALDB_URL || 'http://surrealdb:8000/rpc';

async function connectSurreal() {
  db = new Surreal();
  for (let attempt = 1; attempt <= 30; attempt++) {   // ← retry loop for container start
    await db.connect(surrealUrl);
    await db.signin({ username: surrealUser, password: surrealPass });
  }
  await db.use({ namespace: surrealNs, database: surrealDb });
}
```

---

## Target State

`runtime/server.mjs` connection (file mode):

```js
import { Surreal } from 'surrealdb';                // v2.x
import { NodeEngine } from '@surrealdb/node';

const dbPath = process.env.SURREALDB_FILE
  || path.join(__dirname, 'data', 'planinc.db');

async function connectSurreal() {
  db = new Surreal({ engines: { file: new NodeEngine() } });
  await db.connect(`file://${dbPath}`);
  await db.use({ namespace: surrealNs, database: surrealDb });
  // No signin() — embedded mode has no auth layer
}
```

`docker-compose.yml` after:

```yaml
services:
  planing:
    volumes:
      - ./runtime/data:/app/data      # ← db file persisted here
    environment:
      SURREALDB_FILE: /app/data/planinc.db
      # SURREALDB_URL / USER / PASS removed entirely
```

---

## Step-by-Step Implementation

### Step 2.1 — Upgrade SurrealDB JS SDK

In `runtime/package.json`:

```json
{
  "dependencies": {
    "surrealdb": "^2.0.0",
    "@surrealdb/node": "^2.0.0"
  }
}
```

Remove old `surrealdb@^1.3.2`.  
Run `npm install` / `bun install` in `runtime/`.

**Breaking changes between v1 → v2:**
- `db.connect()` no longer needs `signin()` for embedded
- `RecordId` constructor unchanged
- `StringRecordId` renamed to `RecordId` with string argument in v2 — update
  all `new StringRecordId(x)` calls to `new RecordId(x)` or use
  `db.query(sql, { id: new RecordId('table', id) })`

---

### Step 2.2 — Rewrite `connectSurreal()`

Replace the entire `connectSurreal()` function and remove:
- `reauthenticate()` function (no auth session in embedded mode)
- `reauthInFlight` variable
- `surrealUrl`, `surrealUser`, `surrealPass` env var reads
- The 30-attempt retry loop

Add:
```js
const dbPath = process.env.SURREALDB_FILE
  || path.join(__dirname, 'data', 'planinc.db');
fs.mkdirSync(path.dirname(dbPath), { recursive: true });
```

Update `q()` helper — remove the `reauthenticate()` catch branch, simplify to:
```js
async function q(sql, vars = {}) {
  return unwrapResult(await db.query(sql, vars));
}
```

---

### Step 2.3 — Remove SurrealDB container from `docker-compose.yml`

- Delete the `surrealdb` service block entirely.
- Delete the `planing-surreal-data` named volume.
- Remove `depends_on: surrealdb` from the `planing` service.
- Add `./runtime/data:/app/data` volume mount.
- Replace all `SURREALDB_*` env vars with `SURREALDB_FILE: /app/data/planinc.db`.

---

### Step 2.4 — Update `.env.example`

Remove:
```
SURREALDB_URL=
SURREALDB_PASS=
SURREALDB_PORT=
```

Add:
```
# Path to the SurrealDB embedded database file (default: runtime/data/planinc.db)
SURREALDB_FILE=
```

---

### Step 2.5 — Update `verify-surrealdb.sh`

Replace the URL check:
```bash
# OLD
if ! grep -Eq 'SURREALDB_URL|surrealUrl|surrealdb' "$SOURCE_DIR/server.mjs" "$COMPOSE_FILE"; then
  echo "❌ SurrealDB configuration was not found."
  exit 1
fi
```

With file mode check:
```bash
# NEW
if ! grep -Eq 'file://|SURREALDB_FILE|NodeEngine|@surrealdb/node' "$SOURCE_DIR/server.mjs"; then
  echo "❌ SurrealDB file-mode configuration not found in runtime." >&2
  exit 1
fi

if grep -Eq 'SURREALDB_URL|surrealdb/surrealdb' "$COMPOSE_FILE"; then
  echo "❌ Compose still references a SurrealDB network server." >&2
  exit 1
fi

echo "✅ Planing is SurrealDB file-mode only."
```

---

### Step 2.6 — Add `data/` to `.gitignore`

In `runtime/.gitignore`:
```
data/*.db
data/*.db-lock
data/*.db-wal
```

---

## Schema Compatibility

The SurrealDB schema bootstrap DDL in `server.mjs` (`DEFINE TABLE ... SCHEMAFULL`)
is **100% compatible** with file mode — it is pure SurrealQL, not tied to the
transport layer. No schema changes required.

The `connectSurreal()` call that runs the DDL at boot will still run identically;
`DEFINE TABLE IF NOT EXISTS` / `DEFINE FIELD ... DEFAULT` statements are all
idempotent.

---

## Verification

```bash
# Start without docker
node runtime/server.mjs

# Confirm DB file created
ls -lh runtime/data/planinc.db

# Health check
curl http://localhost:1111/health
# → { "status": "ok", "database": "surrealdb", "storage": { "connected": true } }

# Confirm no postgres guard triggered
grep -E 'POSTGRES|DATABASE_URL' runtime/server.mjs  # must return 0 lines in q()

# Run validator
bash verify-surrealdb.sh
# → ✅ Planing is SurrealDB file-mode only.
```

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| SurrealDB v2 SDK breaking changes in RecordId API | Audit all `new StringRecordId(x)` → `new RecordId(x)` before shipping |
| Embedded engine not available for all Node versions | Pin Node ≥ 20; `@surrealdb/node` requires native bindings |
| File locking — only one process can open the file | Acceptable for single-instance desktop; document in README |
| Data migration from existing volume | Provide a one-time export/import script using `EXPORT` SurrealQL command |

---

## Environment Variables After Migration

| Variable | Required | Default | Notes |
|---|---|---|---|
| `SURREALDB_FILE` | No | `runtime/data/planinc.db` | Override db file path |
| `SURREALDB_NS` | No | `planinc` | Namespace |
| `SURREALDB_DB` | No | `planinc` | Database name |
| `NEXTAUTH_SECRET` | Yes | — | JWT signing secret |
| `PLANING_PORT` | No | `1111` | HTTP port |
| `SMTP_HOST` | No | — | For email sharing (Phase 4) |
