#!/bin/bash
# Start the POS Full sidecar server (Django ASGI — replaces the Robyn server).
# Serves the full Django surface + Channels WebSocket (/ws/nodes, /ws/entities, /ws/config).
cd "$(dirname "$0")"
PORT="${1:-8766}"
echo "Starting POS Full Server (Django ASGI) on port ${PORT}..."
exec .venv/bin/daphne -b 0.0.0.0 -p "${PORT}" asgi:application
