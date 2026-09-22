#!/bin/bash
# Traefik SSL Certificate Restore Script
# Runs on container startup to restore SSL certificates if needed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACME_ROOT="${TRAEFIK_ACME_DIR:-/etc/traefik/acme}"

if [ ! -d "$ACME_ROOT" ]; then
    if [ -d "${SCRIPT_DIR}/../configs" ]; then
        ACME_ROOT="${SCRIPT_DIR}/../configs"
    fi
fi

ACME_FILE="${ACME_ROOT}/acme.json"
BACKUP_DIR="${ACME_ROOT}/backups"

echo "=========================================="
echo "Traefik SSL Certificate Restore/Init"
echo "=========================================="
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting certificate initialization..."

# Check if certificates already exist
if [ -f "$ACME_FILE" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Existing certificates found: $ACME_FILE"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Using existing SSL certificates"
    ls -lh "$ACME_FILE"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⓘ No certificates found, attempting restore from backup..."

    # Look for most recent backup
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/acme_*.json 2>/dev/null | head -n1)

        if [ -n "$LATEST_BACKUP" ]; then
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Found backup: $LATEST_BACKUP"
            cp "$LATEST_BACKUP" "$ACME_FILE"
            chmod 600 "$ACME_FILE"
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Restored certificates from backup"
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Restored: $ACME_FILE"
            ls -lh "$ACME_FILE"
        else
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⓘ No backup files found"
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⓘ Traefik will generate new certificates"
        fi
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⓘ Backup directory empty or doesn't exist"
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⓘ Traefik will generate new certificates"
    fi
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Certificate initialization complete"
echo "=========================================="

backup_current_certificates() {
    mkdir -p "$BACKUP_DIR"

    if [ -f "$ACME_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/acme_$(date +%Y%m%d_%H%M%S).json"
        cp "$ACME_FILE" "$BACKUP_FILE"
        chmod 600 "$BACKUP_FILE"
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✓ Backed up current certificates: $BACKUP_FILE"
    fi
}

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Running backup after initialization..."
backup_current_certificates

# Launch Traefik
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting Traefik..."
exec traefik --configFile=/etc/traefik/dynamic.yml
