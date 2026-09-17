#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
ENV_FILE="${ENV_FILE:-${1:-.env}}"
SOURCE_DIR="${SOURCE_DIR:-runtime}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ Missing Planing env file: $ENV_FILE" >&2
  exit 1
fi

rendered="$(mktemp)"
trap 'rm -f "$rendered"' EXIT

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config >"$rendered"

if grep -Eiq 'postgres|postgresql|DATABASE_URL' "$rendered"; then
  echo "❌ Rendered Planing Compose contains a forbidden relational database configuration." >&2
  grep -Ein 'postgres|postgresql|DATABASE_URL' "$rendered" >&2 || true
  exit 1
fi

runtime_paths=(
  "$SOURCE_DIR/package.json"
  "$SOURCE_DIR/Dockerfile"
  "$SOURCE_DIR/server.mjs"
)
for path in "${runtime_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "❌ Deployed Planing runtime is missing: $path" >&2
    exit 1
  fi
done

if grep -Eiq 'postgres|postgresql|DATABASE_URL|@prisma/client|pg-boss|pgBoss' "$SOURCE_DIR/package.json" "$SOURCE_DIR/Dockerfile"; then
  echo "❌ Deployed Planing package or image definition contains a forbidden legacy datastore dependency." >&2
  grep -Ein 'postgres|postgresql|DATABASE_URL|@prisma/client|pg-boss|pgBoss' "$SOURCE_DIR/package.json" "$SOURCE_DIR/Dockerfile" >&2 || true
  exit 1
fi

# server.mjs may mention forbidden environment names only in its fail-fast
# safety guard; it must still prove that SurrealDB is the active datastore.
if grep -Eq 'from .*(prisma|pg-boss)|require\(. *(prisma|pg-boss)' "$SOURCE_DIR/server.mjs"; then
  echo "❌ Deployed Planing runtime imports a legacy datastore module." >&2
  exit 1
fi

if ! grep -Eq 'SURREALDB_URL|surrealUrl|surrealdb' "$SOURCE_DIR/server.mjs" "$COMPOSE_FILE"; then
  echo "❌ SurrealDB configuration was not found in the deployed runtime." >&2
  exit 1
fi

echo "✅ Planing Compose and runtime are SurrealDB-only."
