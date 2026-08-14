#!/bin/bash
# Start the POS Full server server
cd "$(dirname "$0")"
echo "Starting POS Full Server on port ${1:-8766}..."
python3 server.py --port "${1:-8766}" --migrate
