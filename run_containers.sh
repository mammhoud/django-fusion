#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
SERVICE="ctc-research-website"
SERVICE="${SERVICE_OVERRIDE:-${SERVICE}}"

docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans "$SERVICE"
docker compose -f "$COMPOSE_FILE" ps "$SERVICE"
