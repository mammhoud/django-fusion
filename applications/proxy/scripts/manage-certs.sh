#!/bin/bash

################################################################################
# SSL Certificate Management Script for Traefik
# ─────────────────────────────────────────────────────────────────────────────
# Production certificates are now obtained via Let's Encrypt DNS-01 (Cloudflare),
# managed natively by Traefik. This script is retained for:
#   • Bootstrapping the local ACME storage (bootstrap-acme)
#   • Inspecting what Traefik has stored (status)
#   • Legacy self-signed cert generation (generate-self-signed) — kept as a
#     fallback for environments without DNS provider access.
#
# Usage:
#   ./manage-certs.sh [command] [options]
#
# Commands:
#   bootstrap-acme         Create applications/proxy/acme/ with a 0600 acme.json placeholder
#   status                 Show Traefik ACME storage + certs on disk
#   check-expiry           Check expiry of any LE certs in acme.json
#   generate-self-signed   Generate self-signed certificates for all domains (legacy)
#   list                   List all certificates with expiration dates (legacy)
#   backup                 Backup all certificates to a dated archive (legacy)
#   restore [file]         Restore certificates from backup (legacy)
#   validate               Validate certificate and key pairs (legacy)
#   help                   Show this help message
#
# See applications/proxy/LETSENCRYPT.md for the full DNS-01 deployment runbook.
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="${SCRIPT_DIR}/../certs"
BACKUP_DIR="${SCRIPT_DIR}/../certs"
COMPOSE_FILE="${SCRIPT_DIR}/../../../docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Certificate domains. First domain is the CN; the rest become SubjectAltName (SAN) entries.
# Keep these in sync with the per-site ALLOWED_HOSTS in core/<site>/docker-compose.yml.
DOMAINS=(
  "ctc-research:ctc-research.com www.ctc-research.com arch.ctc-research.com"
  "structa-cloud:structa.cloud www.structa.cloud core.structa.cloud"
  "vresume:vresume.structa.cloud www.vresume.structa.cloud resume.structa.cloud"
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
  shift
  local domains=("$@")
  local primary_domain="${domains[0]}"
  local days=365

  log_info "Generating self-signed certificate for $primary_domain ($cert_name)..."
  log_info "  SANs: ${domains[*]}"

  # Build the SubjectAltName value: "DNS:dom1,DNS:dom2,..."
  local san_csv=""
  local d
  for d in "${domains[@]}"; do
    if [ -z "$san_csv" ]; then
      san_csv="DNS:${d}"
    else
      san_csv="${san_csv},DNS:${d}"
    fi
  done

  # Generate private key
  openssl genrsa -out "${CERTS_DIR}/${cert_name}.key" 2048 2>/dev/null

  # Generate certificate signing request with proper CN and SANs
  # (-addext requires OpenSSL ≥ 1.1.0; the -extfile on x509 is a belt-and-braces fallback.)
  openssl req -new \
    -key "${CERTS_DIR}/${cert_name}.key" \
    -out "${CERTS_DIR}/${cert_name}.csr" \
    -subj "/C=US/ST=California/L=Remote/O=Structa/CN=${primary_domain}" \
    -addext "subjectAltName=${san_csv}" \
    2>/dev/null

  # Generate self-signed certificate (valid for $days days) with SANs
  openssl x509 -req -days "${days}" \
    -in "${CERTS_DIR}/${cert_name}.csr" \
    -signkey "${CERTS_DIR}/${cert_name}.key" \
    -out "${CERTS_DIR}/${cert_name}.crt" \
    -extfile <(printf "subjectAltName=%s\n" "$san_csv") \
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
    echo "Domains:"
    for d in $domain; do
      echo "  - $d"
    done
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
# Bootstrap ACME storage (applications/proxy/acme/acme.json, mode 0600)
################################################################################

bootstrap_acme() {
  local acme_dir="${SCRIPT_DIR}/../acme"
  local acme_file="${acme_dir}/acme.json"

  log_info "Bootstrapping ACME storage at ${acme_file}..."

  mkdir -p "$acme_dir"
  if [ ! -f "$acme_file" ]; then
    : > "$acme_file"
  fi
  chmod 600 "$acme_file"

  log_success "ACME storage ready: ${acme_file} (mode 0600)"
  log_info "You can now start the proxy: docker compose -f applications/proxy/docker-compose.traefik.yml up -d"
}

################################################################################
# Status — show Traefik ACME storage + per-site certs on disk
################################################################################

status_certificates() {
  local acme_file="${SCRIPT_DIR}/../acme/acme.json"
  echo ""
  log_info "ACME / Let's Encrypt status"
  echo "────────────────────────────────────────────────────────────"

  if [ -f "$acme_file" ]; then
    local size
    size=$(du -sh "$acme_file" | cut -f1)
    local perms
    perms=$(stat -c %a "$acme_file")
    log_success "acme.json present  (${size}, mode ${perms})"
    if command -v jq >/dev/null 2>&1; then
      local cert_count
      cert_count=$(jq -r '.. | .Certificates? // empty | length' "$acme_file" 2>/dev/null \
        | awk '{s+=$1} END {print s+0}')
      if [ "${cert_count:-0}" -gt 0 ]; then
        log_success "LE certs in store: ${cert_count}"
        jq -r '.. | .Certificates? // empty | .[] | "  - " + .domain + "  (expires " + (.certificate.expiry // "unknown") + ")"' \
          "$acme_file" 2>/dev/null || true
      else
        log_warning "acme.json exists but no LE certs yet — trigger by hitting an https endpoint"
      fi
    else
      log_warning "Install 'jq' to inspect cert domains/expiries"
    fi
  else
    log_warning "acme.json not found at ${acme_file}"
    log_info "Run: $0 bootstrap-acme"
  fi

  echo ""
  log_info "Legacy self-signed certs in ${CERTS_DIR}:"
  for cert in "${CERTS_DIR}"/*.crt; do
    [ -f "$cert" ] || continue
    local notAfter
    notAfter=$(openssl x509 -in "$cert" -noout -enddate 2>/dev/null | cut -d= -f2)
    printf "  %-32s expires: %s\n" "$(basename "$cert" .crt)" "$notAfter"
  done
  echo ""
}

################################################################################
# Main
################################################################################

main() {
  local command=${1:-help}

  mkdir -p "$CERTS_DIR"

  case "$command" in
    bootstrap-acme)
      bootstrap_acme
      ;;

    status)
      status_certificates
      ;;

    check-expiry)
      check_expiry
      ;;

    generate-self-signed)
      log_info "Generating self-signed certificates for all domains..."
      for domain_config in "${DOMAINS[@]}"; do
        IFS=':' read -r cert_name domain_str <<< "$domain_config"
        # Split the space-separated domain list into positional args (first is CN, rest are SANs).
        # Filter out empty entries to avoid `subjectAltName=DNS:,DNS:...` if anyone leaves a trailing space.
        set --
        # shellcheck disable=SC2086
        for d in $domain_str; do
          [ -n "$d" ] && set -- "$@" "$d"
        done
        generate_self_signed "$cert_name" "$@"
      done
      log_success "All certificates generated"
      ;;

    list)
      list_certificates
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

Primary (Let's Encrypt / ACME) commands:
  bootstrap-acme         Create applications/proxy/acme/acme.json (mode 0600) before first start
  status                 Show ACME storage contents + per-site cert status
  check-expiry           Check expiry of LE certs in acme.json (uses jq if available)

Legacy (self-signed) commands — kept as a fallback for environments
without DNS provider access:
  generate-self-signed   Generate self-signed certificates for all domains
  list                   List self-signed certificates with expiration dates
  backup                 Backup self-signed certs to a dated archive
  restore [file]         Restore self-signed certs from a backup archive
  validate               Validate self-signed cert/key pairs

Other:
  help                   Show this help message

Examples:
  # First-time LE setup
  cp applications/proxy/.env.example applications/proxy/.env  # fill in CF_DNS_API_TOKEN
  ./manage-certs.sh bootstrap-acme
  docker compose -f applications/proxy/docker-compose.traefik.yml up -d
  ./manage-certs.sh status

  # Inspect an existing LE store
  ./manage-certs.sh status
  ./manage-certs.sh check-expiry

  # Legacy self-signed flow (fallback)
  ./manage-certs.sh generate-self-signed
  ./manage-certs.sh validate

DNS-01 / Let's Encrypt Configuration:
  See applications/proxy/LETSENCRYPT.md for the full runbook (provider credentials,
  staged rollout, acme.json bootstrapping, rollback).

Supported Domains (CN + SANs):
  • ctc-research.com       (www.ctc-research.com, arch.ctc-research.com)
  • structa.cloud          (www.structa.cloud, core.structa.cloud)
  • vresume.structa.cloud  (www.vresume.structa.cloud, resume.structa.cloud)

Certificate Information:
  • Primary:  Let's Encrypt (DNS-01, Cloudflare) — auto-renewed by Traefik
  • Fallback: Self-signed (365 days) — managed by this script
  • Storage:  ./acme/acme.json (LE)  and  ./certs/ (self-signed)

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
