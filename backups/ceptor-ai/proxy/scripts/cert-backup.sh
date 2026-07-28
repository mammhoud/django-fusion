#!/bin/bash
#
# Traefik Certificate Backup & Restoration System
# Automatically backs up ACME certificates with timestamps
# Usage: ./cert-backup.sh [backup|restore|list|cleanup]
#

set -e

TRAEFIK_ACME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/acme"
BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/certs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATED_BACKUP_DIR="${BACKUP_DIR}/${TIMESTAMP}_certs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log() {
  echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

error() {
  echo -e "${RED}[✗]${NC} $1"
  exit 1
}

warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

# Create backups directory if needed
mkdir -p "$BACKUP_DIR"

# ============================================================
# BACKUP: Save current certs with timestamp
# ============================================================
backup_certs() {
  log "Backing up Traefik ACME certificates..."

  if [ ! -d "$TRAEFIK_ACME_DIR" ]; then
    error "Traefik ACME directory not found: $TRAEFIK_ACME_DIR"
  fi

  # Check if there are any certificates to backup
  if [ ! -f "$TRAEFIK_ACME_DIR/acme.json" ]; then
    warning "No acme.json found. Certificates may not have been generated yet."
    return 0
  fi

  # Create timestamped backup directory
  mkdir -p "$DATED_BACKUP_DIR"

  # Copy all ACME files
  cp "$TRAEFIK_ACME_DIR/acme.json" "$DATED_BACKUP_DIR/" 2>/dev/null || warning "acme.json not found"

  # Create metadata file
  cat > "$DATED_BACKUP_DIR/backup-metadata.txt" <<EOF
Traefik Certificate Backup
==========================
Backup Date: $(date '+%Y-%m-%d %H:%M:%S')
Timestamp: $TIMESTAMP
Source Directory: $TRAEFIK_ACME_DIR
Backup Directory: $DATED_BACKUP_DIR

Files Backed Up:
EOF

  # List backed up files
  ls -lah "$DATED_BACKUP_DIR" | tail -n +4 >> "$DATED_BACKUP_DIR/backup-metadata.txt"

  # Create readable info file
  if [ -f "$DATED_BACKUP_DIR/acme.json" ]; then
    cat >> "$DATED_BACKUP_DIR/backup-metadata.txt" <<EOF

Certificate Information:
EOF
    # Extract certificate info (if jq is available)
    if command -v jq &> /dev/null; then
      jq -r '.acme[] | select(.Certificates) | .Certificates[] | "Domain: \(.domain), Expiry: \(.certificate.expiry // "N/A")"' "$DATED_BACKUP_DIR/acme.json" >> "$DATED_BACKUP_DIR/backup-metadata.txt" 2>/dev/null || true
    fi
  fi

  # Calculate backup size
  BACKUP_SIZE=$(du -sh "$DATED_BACKUP_DIR" | cut -f1)

  success "Certificates backed up to: $DATED_BACKUP_DIR ($BACKUP_SIZE)"
  log "Backup metadata saved to: $DATED_BACKUP_DIR/backup-metadata.txt"

  # Display backup info
  cat "$DATED_BACKUP_DIR/backup-metadata.txt"
}

# ============================================================
# RESTORE: Restore certificates from a backup
# ============================================================
restore_certs() {
  local backup_dir="$1"

  if [ -z "$backup_dir" ]; then
    error "Usage: $0 restore <backup_directory_path>"
  fi

  if [ ! -d "$backup_dir" ]; then
    error "Backup directory not found: $backup_dir"
  fi

  if [ ! -f "$backup_dir/acme.json" ]; then
    error "No acme.json found in backup directory: $backup_dir"
  fi

  log "Restoring Traefik certificates from backup..."
  log "Source: $backup_dir"
  log "Destination: $TRAEFIK_ACME_DIR"

  # Create a safety backup of current certs before restoring
  if [ -f "$TRAEFIK_ACME_DIR/acme.json" ]; then
    log "Creating safety backup of current certificates..."
    SAFETY_BACKUP="${BACKUP_DIR}/pre-restore_$(date +%s)_certs"
    mkdir -p "$SAFETY_BACKUP"
    cp "$TRAEFIK_ACME_DIR/acme.json" "$SAFETY_BACKUP/"
    log "Safety backup created at: $SAFETY_BACKUP"
  fi

  # Restore certificates
  mkdir -p "$TRAEFIK_ACME_DIR"
  cp "$backup_dir/acme.json" "$TRAEFIK_ACME_DIR/"

  # Ensure correct permissions (Traefik needs to read this)
  chmod 600 "$TRAEFIK_ACME_DIR/acme.json"

  success "Certificates restored from: $backup_dir"
  log "To apply changes, restart Traefik container:"
  log "  docker compose restart traefik"
}

# ============================================================
# LIST: Show available backups
# ============================================================
list_backups() {
  if [ ! -d "$BACKUP_DIR" ]; then
    warning "No backups directory found. Create one with: $0 backup"
    return 0
  fi

  log "Available certificate backups:"
  echo ""

  local backup_count=0
  for backup in $(ls -dt "$BACKUP_DIR"/*/ 2>/dev/null); do
    backup_count=$((backup_count + 1))
    basename=$(basename "$backup")
    size=$(du -sh "$backup" | cut -f1)
    created=$(stat -c %y "$backup" 2>/dev/null | cut -d' ' -f1-2)

    echo -e "${BLUE}${backup_count}.${NC} $basename ($size)"
    if [ -f "$backup/backup-metadata.txt" ]; then
      echo "   Created: $created"
      grep -m 1 "^Domain:" "$backup/backup-metadata.txt" | sed 's/^/   /'
    fi
  done

  if [ $backup_count -eq 0 ]; then
    warning "No backups found in: $BACKUP_DIR"
  else
    echo ""
    success "Total backups: $backup_count"
  fi
}

# ============================================================
# CLEANUP: Remove old backups (keep last N)
# ============================================================
cleanup_old_backups() {
  local keep_count="${1:-10}"

  log "Cleaning up old certificate backups (keeping last $keep_count)..."

  if [ ! -d "$BACKUP_DIR" ]; then
    warning "No backups directory found"
    return 0
  fi

  local backup_count=$(ls -d "$BACKUP_DIR"/*/ 2>/dev/null | wc -l)

  if [ $backup_count -le $keep_count ]; then
    log "Only $backup_count backups found (threshold: $keep_count). No cleanup needed."
    return 0
  fi

  log "Found $backup_count backups. Removing oldest..."

  # Sort by date (oldest first) and remove all but the last $keep_count
  ls -dt "$BACKUP_DIR"/*/ | tail -n +$((keep_count + 1)) | while read -r old_backup; do
    size=$(du -sh "$old_backup" | cut -f1)
    log "Removing: $(basename "$old_backup") ($size)"
    rm -rf "$old_backup"
  done

  success "Cleanup complete. Kept last $keep_count backups."
}

# ============================================================
# CURRENT STATUS: Show current cert status
# ============================================================
show_status() {
  log "Traefik Certificate Status"
  echo ""

  if [ -f "$TRAEFIK_ACME_DIR/acme.json" ]; then
    success "ACME configuration file exists"
    size=$(du -sh "$TRAEFIK_ACME_DIR/acme.json" | cut -f1)
    modified=$(stat -c %y "$TRAEFIK_ACME_DIR/acme.json" | cut -d. -f1)
    echo "  File size: $size"
    echo "  Last modified: $modified"

    if command -v jq &> /dev/null; then
      cert_count=$(jq -r '.acme[].Certificates 2>/dev/null | length' "$TRAEFIK_ACME_DIR/acme.json" | paste -sd+ | bc 2>/dev/null || echo "unknown")
      echo "  Certificates: $cert_count"
    fi
  else
    warning "ACME configuration file not found"
    log "Expected location: $TRAEFIK_ACME_DIR/acme.json"
  fi

  echo ""
  log "Backup Information"
  if [ -d "$BACKUP_DIR" ]; then
    backup_count=$(ls -d "$BACKUP_DIR"/*/ 2>/dev/null | wc -l)
    total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    echo "  Backups available: $backup_count"
    echo "  Total backup size: $total_size"
    echo "  Backup directory: $BACKUP_DIR"
  else
    warning "No backups found yet"
  fi
}

# ============================================================
# HELP: Show usage
# ============================================================
show_help() {
  cat <<EOF
Traefik Certificate Backup & Restoration System
===============================================

Usage: $0 [command] [options]

Commands:
  backup                    Backup current certificates with timestamp
  restore <backup_dir>      Restore certificates from a backup directory
  list                      List all available backups
  cleanup [keep_count]      Remove old backups (default: keep 10)
  status                    Show current certificate and backup status
  help                      Show this help message

Examples:
  # Backup current certificates
  $0 backup

  # List available backups
  $0 list

  # Restore from a specific backup
  $0 restore /root/site/websites/compose/traefik/certs/20260602_121530_certs

  # Keep only the last 5 backups
  $0 cleanup 5

  # Show current status
  $0 status

Automated Backup Integration:
  Add to crontab for daily backups:
  0 2 * * * cd /root/site/websites/compose/traefik && ./cert-backup.sh backup >> /var/log/traefik-backup.log 2>&1

Location:
  Current certificates:  $TRAEFIK_ACME_DIR
  Backup directory:      $BACKUP_DIR
EOF
}

# ============================================================
# Main
# ============================================================
COMMAND="${1:-help}"

case "$COMMAND" in
  backup)
    backup_certs
    ;;
  restore)
    restore_certs "$2"
    ;;
  list)
    list_backups
    ;;
  cleanup)
    cleanup_old_backups "$2"
    ;;
  status)
    show_status
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    error "Unknown command: $COMMAND. Use 'help' for usage information."
    ;;
esac

