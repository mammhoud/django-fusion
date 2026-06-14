#!/bin/bash

################################################################################
# SSL Certificate Management Script for Traefik
# ─────────────────────────────────────────────────────────────────────────────
# Manage self-signed and Let's Encrypt certificates for the multi-site setup.
# 
# Usage:
#   ./manage-certs.sh [command] [options]
#
# Commands:
#   generate-self-signed   Generate self-signed certificates for all domains
#   list                   List all certificates with expiration dates
#   check-expiry           Check if any certificates are expiring soon
#   backup                 Backup all certificates to a dated archive
#   restore [file]         Restore certificates from backup
#   renew-letsencrypt      Attempt to renew using Let's Encrypt ACME
#   validate               Validate certificate and key pairs
#   help                   Show this help message
#
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="${SCRIPT_DIR}/certs"
BACKUP_DIR="${SCRIPT_DIR}/certs-backups"
COMPOSE_FILE="${SCRIPT_DIR}/../../docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Certificate domains
DOMAINS=(
  "ctc-research:ctc-research.com"
  "structa-cloud:structa.cloud"
  "vresume:vresume.structa.cloud"
)

################################################################################
# Helper Functions
################################################################################

log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

################################################################################
# Generate Self-Signed Certificates
################################################################################

generate_self_signed() {
  local cert_name=$1
  local domain=$2
  local days=${3:-365}
  
  log_info "Generating self-signed certificate for $domain ($cert_name)..."
  
  # Generate private key
  openssl genrsa -out "${CERTS_DIR}/${cert_name}.key" 2048 2>/dev/null
  
  # Generate certificate signing request
  openssl req -new \
    -key "${CERTS_DIR}/${cert_name}.key" \
    -out "${CERTS_DIR}/${cert_name}.csr" \
    -subj "/C=US/ST=California/L=Remote/O=Structa/CN=${domain}" \
    2>/dev/null
  
  # Generate self-signed certificate (valid for 365 days)
  openssl x509 -req -days "${days}" \
    -in "${CERTS_DIR}/${cert_name}.csr" \
    -signkey "${CERTS_DIR}/${cert_name}.key" \
    -out "${CERTS_DIR}/${cert_name}.crt" \
    2>/dev/null
  
  # Generate certificate chain (for compatibility)
  cp "${CERTS_DIR}/${cert_name}.crt" "${CERTS_DIR}/${cert_name}-chain.pem"
  
  # Generate combined PEM (for some applications)
  cat "${CERTS_DIR}/${cert_name}.crt" "${CERTS_DIR}/${cert_name}.key" \
    > "${CERTS_DIR}/${cert_name}.pem"
  
  # Set proper permissions
  chmod 600 "${CERTS_DIR}/${cert_name}.key"
  chmod 644 "${CERTS_DIR}/${cert_name}.crt"
  chmod 644 "${CERTS_DIR}/${cert_name}.pem"
  
  log_success "Certificate generated: $cert_name (valid for $days days)"
}

################################################################################
# List Certificates
################################################################################

list_certificates() {
  echo ""
  log_info "SSL Certificates Summary"
  echo "────────────────────────────────────────────────────────────"
  
  for domain_config in "${DOMAINS[@]}"; do
    IFS=':' read -r cert_name domain <<< "$domain_config"
    cert_file="${CERTS_DIR}/${cert_name}.crt"
    
    if [ ! -f "$cert_file" ]; then
      log_warning "Certificate not found: $cert_name"
      continue
    fi
    
    echo ""
    echo "Certificate: $cert_name"
    echo "Domain: $domain"
    echo "File: $cert_file"
    
    # Get expiration date
    expiry=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || echo 0)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    
    if [ $days_left -lt 0 ]; then
      log_error "EXPIRED $((-days_left)) days ago"
    elif [ $days_left -lt 30 ]; then
      log_warning "Expires in $days_left days: $expiry"
    else
      log_success "Valid for $days_left days (expires: $expiry)"
    fi
  done
  echo ""
}

################################################################################
# Check Certificate Expiry
################################################################################

check_expiry() {
  log_info "Checking certificate expiry dates..."
  echo ""
  
  local expired=0
  local expiring_soon=0
  
  for domain_config in "${DOMAINS[@]}"; do
    IFS=':' read -r cert_name domain <<< "$domain_config"
    cert_file="${CERTS_DIR}/${cert_name}.crt"
    
    if [ ! -f "$cert_file" ]; then
      log_warning "Certificate not found: $cert_name"
      continue
    fi
    
    expiry=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || echo 0)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    
    if [ $days_left -lt 0 ]; then
      log_error "$cert_name: EXPIRED"
      expired=$((expired + 1))
    elif [ $days_left -lt 30 ]; then
      log_warning "$cert_name: Expires in $days_left days"
      expiring_soon=$((expiring_soon + 1))
    else
      log_success "$cert_name: Valid for $days_left days"
    fi
  done
  
  echo ""
  if [ $expired -gt 0 ]; then
    log_error "Found $expired expired certificate(s)"
    return 1
  elif [ $expiring_soon -gt 0 ]; then
    log_warning "Found $expiring_soon certificate(s) expiring soon"
    return 0
  else
    log_success "All certificates are valid"
    return 0
  fi
}

################################################################################
# Backup Certificates
################################################################################

backup_certificates() {
  mkdir -p "$BACKUP_DIR"
  
  local backup_file="${BACKUP_DIR}/certs-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
  
  log_info "Backing up certificates to: $backup_file"
  
  tar -czf "$backup_file" -C "${SCRIPT_DIR}" certs/
  
  log_success "Certificates backed up successfully"
  echo "Location: $backup_file"
  
  # List recent backups
  echo ""
  log_info "Recent backups:"
  ls -lh "$BACKUP_DIR" | tail -5 | awk '{print "  " $9 " (" $5 ")"}'
}

################################################################################
# Restore Certificates
################################################################################

restore_certificates() {
  local backup_file=$1
  
  if [ -z "$backup_file" ]; then
    log_error "Backup file path required"
    echo "Usage: $0 restore /path/to/backup.tar.gz"
    return 1
  fi
  
  if [ ! -f "$backup_file" ]; then
    log_error "Backup file not found: $backup_file"
    return 1
  fi
  
  log_warning "Restoring certificates from: $backup_file"
  echo "This will overwrite existing certificates."
  read -p "Continue? (y/N) " -n 1 -r
  echo
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    tar -xzf "$backup_file" -C "${SCRIPT_DIR}"
    log_success "Certificates restored successfully"
    log_info "Restarting Traefik to apply changes..."
    docker compose -f "$COMPOSE_FILE" restart structa-proxy || true
  else
    log_warning "Restore cancelled"
  fi
}

################################################################################
# Validate Certificates
################################################################################

validate_certificates() {
  log_info "Validating certificates and key pairs..."
  echo ""
  
  local valid=0
  local invalid=0
  
  for domain_config in "${DOMAINS[@]}"; do
    IFS=':' read -r cert_name domain <<< "$domain_config"
    cert_file="${CERTS_DIR}/${cert_name}.crt"
    key_file="${CERTS_DIR}/${cert_name}.key"
    
    if [ ! -f "$cert_file" ] || [ ! -f "$key_file" ]; then
      log_error "$cert_name: Certificate or key file missing"
      invalid=$((invalid + 1))
      continue
    fi
    
    # Validate certificate and key match
    cert_md5=$(openssl x509 -noout -modulus -in "$cert_file" | openssl md5)
    key_md5=$(openssl rsa -noout -modulus -in "$key_file" | openssl md5)
    
    if [ "$cert_md5" = "$key_md5" ]; then
      log_success "$cert_name: Certificate and key match"
      valid=$((valid + 1))
    else
      log_error "$cert_name: Certificate and key do NOT match"
      invalid=$((invalid + 1))
    fi
  done
  
  echo ""
  echo "Results: $valid valid, $invalid invalid"
  return $([ $invalid -eq 0 ] && echo 0 || echo 1)
}

################################################################################
# Main
################################################################################

main() {
  local command=${1:-help}
  
  mkdir -p "$CERTS_DIR"
  
  case "$command" in
    generate-self-signed)
      log_info "Generating self-signed certificates for all domains..."
      for domain_config in "${DOMAINS[@]}"; do
        IFS=':' read -r cert_name domain <<< "$domain_config"
        generate_self_signed "$cert_name" "$domain" 365
      done
      log_success "All certificates generated"
      ;;
    
    list)
      list_certificates
      ;;
    
    check-expiry)
      check_expiry
      ;;
    
    backup)
      backup_certificates
      ;;
    
    restore)
      restore_certificates "$2"
      ;;
    
    validate)
      validate_certificates
      ;;
    
    help|--help|-h)
      cat << 'HELP'

SSL Certificate Management Script for Traefik
══════════════════════════════════════════════════════════════════════════════

Usage:  ./manage-certs.sh [command] [options]

Commands:
  generate-self-signed     Generate self-signed certificates for all domains
  list                     List all certificates with expiration dates
  check-expiry             Check if any certificates are expiring soon
  backup                   Backup all certificates to a dated archive
  restore [file]           Restore certificates from a backup archive
  validate                 Validate certificate and key pairs
  help                     Show this help message

Examples:
  # Generate new self-signed certificates
  ./manage-certs.sh generate-self-signed

  # List all certificates
  ./manage-certs.sh list

  # Check expiration status
  ./manage-certs.sh check-expiry

  # Backup certificates
  ./manage-certs.sh backup

  # Restore from backup
  ./manage-certs.sh restore certs-backups/certs-backup-20260611-120000.tar.gz

  # Validate certificates match keys
  ./manage-certs.sh validate

Supported Domains:
  • ctc-research.com
  • structa.cloud
  • vresume.structa.cloud

Certificate Information:
  • Type: Self-signed (currently in use)
  • Validity: 365 days from generation
  • Storage: ./certs/ directory
  • Backups: ./certs-backups/ directory

ACME / Let's Encrypt Configuration:
  To enable automatic ACME certificate renewal:
  1. Set valid email in TRAEFIK_ACME_EMAIL environment variable (.env)
  2. Configure DNS or HTTP challenge in traefik.yml
  3. Restart Traefik: docker compose restart structa-proxy

HELP
      ;;
    
    *)
      log_error "Unknown command: $command"
      echo "Use '$0 help' for usage information"
      exit 1
      ;;
  esac
}

# Run main function with all arguments
main "$@"
