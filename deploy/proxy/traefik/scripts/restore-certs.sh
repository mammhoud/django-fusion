#!/bin/bash
# Traefik SSL Certificate Restore Script
# Runs on container startup to restore SSL certificates if needed

set -e

ACME_FILE="/etc/traefik/acme/acme.json"
BACKUP_DIR="/etc/traefik/acme/backups"

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

# Run backup script to ensure current certificates are backed up
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Running backup after initialization..."
/backup-certs.sh

# Launch Traefik
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting Traefik..."
exec traefik --configFile=/etc/traefik/traefik.yml
#!/bin/bash
# Traefik SSL Certificate Restore Script
# Runs on container startup to restore SSL certificates if needed

set -e

ACME_FILE="/etc/traefik/acme/acme.json"
BACKUP_DIR="/etc/traefik/acme/backups"

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

# Run backup script to ensure current certificates are backed up
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Running backup after initialization..."
/backup-certs.sh

# Launch Traefik
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting Traefik..."
exec traefik --configFile=/etc/traefik/traefik.yml
