#!/bin/bash
# Start the POS Solo sidecar server
cd "$(dirname "$0")"
echo "Starting POS Solo Server on port ${1:-8765}..."
python3 server.py --port "${1:-8765}" --migrate
