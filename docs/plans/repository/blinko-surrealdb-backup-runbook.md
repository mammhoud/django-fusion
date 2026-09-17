# Blinko on SurrealDB — backup and restore runbook

> **Scope:** `application/tools/blinko/` — the SurrealDB-only Blinko runtime.
> **Engine:** `surrealdb/surrealdb:v1.5.6`, data volume `blinko_blinko-surreal-data` mounted at `/data` as `file:/data/blinko.db`.

<!-- AI-generated: review needed -->

## What exists where

| Asset | Location |
|---|---|
| Workspace JSON (notes, lanes, tags, attachments metadata) | `GET /api/export` from the running app (auth required) |
| Full SurrealQL export (schema + data) | `surreal export` inside the engine container |
| Raw datastore files | Docker volume `blinko_blinko-surreal-data` → `/data/blinko.db` (rocksdb) |
| Uploaded attachment binaries | app container path from `UPLOAD_DIR` (default `/app/data/uploads`) |

Use both layers: the JSON export is portable and human-readable; the SurrealQL
export preserves schema definitions and is the engine-level snapshot.

## Before you start

```bash
cd application/tools/blinko
# Password used by the engine (matches the stored root credential).
pass=$(grep '^SURREALDB_PASS=' ../.env.example | cut -d= -f2-)
ns=blinko; db=blinko
```

`SURREALDB_NS`/`SURREALDB_DB` default to `blinko`/`blinko` in the compose file.
Never print or echo the password in logs or terminal output.

## 1. Workspace JSON export (application level)

```bash
token=$(curl -s -X POST http://127.0.0.1:1111/api/auth/login \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"<admin>\",\"password\":\"<password>\"}" \
  | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>console.log(JSON.parse(d).token))")
curl -s -H "Authorization: Bearer $token" http://127.0.0.1:1111/api/export -o "blinko-export-$(date +%F).json"
```

- The file is versioned (`schemaVersion`, `exportedAt`) and restores through
  `POST /api/import` (Settings → Data → Import JSON, `settings:write` role).
- Import is **idempotent**: existing notes/lanes are never duplicated, only
  missing records are re-created. Re-running the same file is always safe.
- Attachment binaries are **not** in the JSON — copy them separately (step 3).

## 2. Engine-level SurrealDB export

```bash
mkdir -p /tmp/blinko-backup-$(date +%F)
docker exec blinko-surreal /surreal export \
  --endpoint http://127.0.0.1:8000 \
  --namespace $ns --database $db \
  -u root -p "$pass" - \
  > /tmp/blinko-backup-$(date +%F)/blinko.surql
```

Verify before trusting it:

```bash
test -s /tmp/blinko-backup-$(date +%F)/blinko.surql && echo NONEMPTY_OK
grep -c "DEFINE TABLE" /tmp/blinko-backup-$(date +%F)/blinko.surql
```

## 3. Attachment binaries

```bash
docker cp blinko:/app/data/uploads /tmp/blinko-backup-$(date +%F)/uploads
```

## 4. Restore from SurrealQL

```bash
# 4a. Stop the app so nothing writes while restoring.
docker compose --env-file ../.env stop blinko

# 4b. Wipe only the blinko namespace/db (destructive — confirm first).
docker exec blinko-surreal /surreal sql \
  --endpoint http://127.0.0.1:8000 --namespace $ns --database $db \
  -u root -p "$pass" - <<< "REMOVE DATABASE IF EXISTS $db;" || true

# 4c. Recreate and import.
docker exec -i blinko-surreal /surreal import \
  --endpoint http://127.0.0.1:8000 \
  --namespace $ns --database $db \
  -u root -p "$pass" - \
  < /tmp/blinko-backup-$(date +%F)/blinko.surql

# 4d. Bring the app back and check health.
docker compose --env-file ../.env up -d blinko
curl -s http://127.0.0.1:1111/health | head -c 200
```

## 5. Restore from JSON (partial, data only)

If the engine is healthy and only records were lost, prefer JSON import — it
skips schema concerns and never overwrites existing records:

```bash
curl -s -X POST -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/blinko-backup-$(date +%F)/blinko-export.json \
  http://127.0.0.1:1111/api/import
# → {"imported":{"categories":N,"tags":N,"notes":N,"skipped":N}, ...}
```

Then restore attachment binaries into the app container's upload dir and
re-attach them via `PATCH /api/attachments/:id` if needed.

## 6. Point-in-time safety net

v1.5.6 has no incremental backup; for PITR-style protection schedule frequent
`/api/export` calls (cheap, idempotent to replay) plus a nightly step-2 dump:

```bash
# crontab example (host), 03:15 nightly
# 15 3 * * * cd /path/to/repo/application/tools/blinko && ./backup-nightly.sh
```

Keep at least two restore paths rehearsed: full SurrealQL (4) and JSON (5).
Test restores in a scratch namespace **before** you ever need them in anger.

## Remarks & Notes

- The engine container is stateless — all durable state is in the volume, the
  upload dir, and your exports.
- Compose's `SURREALDB_PASS` must match the stored root credential; a mismatch
  crash-loops the app with `There was a problem with authentication` at boot.
- After any restore, watch the server boot logs once: schema defines are
  idempotent, but restore + restart is the only supported way to change the
  schema version (`workspace-v4` today).
