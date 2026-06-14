#!/bin/bash
# Traefik SSL Certificate Backup Script
# Runs on container startup to backup SSL certificates

set -e

ACME_FILE="/etc/traefik/acme/acme.json"
BACKUP_DIR="/etc/traefik/acme/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup certificates
backup_certificates() {
    if [ -f "$ACME_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/acme_$TIMESTAMP.json"
        cp "$ACME_FILE" "$BACKUP_FILE"
        chmod 600 "$BACKUP_FILE"
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Certificate backup created: $BACKUP_FILE"

        # Keep only last 10 backups
        cd "$BACKUP_DIR"
        ls -t acme_*.json | tail -n +11 | xargs rm -f 2>/dev/null || true
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Old backups cleaned (kept 10 most recent)"
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ℹ No certificates to backup yet"
    fi
}

# Function to show backup info
show_backup_info() {
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Certificate backups available:"
        ls -lh "$BACKUP_DIR"/acme_*.json | awk '{print "  - " $9 " (" $5 ")"}'
    fi
}

# Run backup
echo "=========================================="
echo "Traefik SSL Certificate Backup"
echo "=========================================="
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting backup process..."

backup_certificates
show_backup_info

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backup process complete"
echo "=========================================="
