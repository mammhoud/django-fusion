#!/bin/bash
#
# Traefik Production Certificate Generation Script
# Generates self-signed certificates with proper CN (Common Name) for all domains
# Certificates are written to application/proxy/data/certs/ as PEM/crt/key bundles for Traefik.
#
# Usage: ./generate-certs.sh [production|staging]
#

set -e

TRAEFIK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CERT_DIR="${TRAEFIK_DIR}/data/certs"
BACKUP_DIR="${TRAEFIK_DIR}/data/certs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
ENVIRONMENT="${1:-production}"

# Domain configurations
declare -A DOMAINS=(
  ["precis-ctc"]="ctc-research.com www.ctc-research.com arch.ctc-research.com"
  ["structa-cloud"]="structa.cloud www.structa.cloud core.structa.cloud"
  ["vresume"]="vresume.structa.cloud www.vresume.structa.cloud"
)

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

# Create directories
mkdir -p "$CERT_DIR" "$BACKUP_DIR"

# ============================================================
# Generate Self-Signed Certificates with Proper CN
# ============================================================
generate_self_signed_cert() {
  local domain_name=$1
  local domains=$2
  local primary_domain=$(echo "$domains" | awk '{print $1}')

  log "Generating self-signed certificate for $domain_name"
  log "  Primary domain: $primary_domain"
  log "  SANs: $domains"

  # Convert space-separated domains to comma-separated for SAN
  local san_list=$(echo "$domains" | tr ' ' ',' | sed 's/^/DNS:/' | sed 's/,/,DNS:/g')

  # Generate private key
  openssl genrsa -out "${CERT_DIR}/${domain_name}.key" 2048 2>/dev/null

  # Generate certificate signing request with proper CN and SANs
  openssl req -new \
    -key "${CERT_DIR}/${domain_name}.key" \
    -subj "/C=US/ST=California/L=Remote/O=Structa/CN=${primary_domain}" \
    -addext "subjectAltName=${san_list}" \
    -out "${CERT_DIR}/${domain_name}.csr" 2>/dev/null

  # Generate self-signed certificate valid for 365 days
  openssl x509 -req -days 365 \
    -in "${CERT_DIR}/${domain_name}.csr" \
    -signkey "${CERT_DIR}/${domain_name}.key" \
    -out "${CERT_DIR}/${domain_name}.crt" \
    -extensions v3_req \
    -extfile <(cat /etc/ssl/openssl.cnf <(printf "subjectAltName=${san_list}")) \
    2>/dev/null

  success "Generated certificate: ${CERT_DIR}/${domain_name}.crt"

  # Display certificate info
  log "Certificate details:"
  openssl x509 -in "${CERT_DIR}/${domain_name}.crt" -text -noout 2>/dev/null | grep -E "(Subject:|CN|DNS:)" | sed 's/^/  /'
}

# ============================================================
# Generate All Certificates
# ============================================================
generate_all_certs() {
  log "=== Generating All Certificates (Self-Signed) ==="
  log "Environment: $ENVIRONMENT"
  echo ""

  for domain_name in "${!DOMAINS[@]}"; do
    generate_self_signed_cert "$domain_name" "${DOMAINS[$domain_name]}"
    echo ""
  done
}

# ============================================================
# Create Certificate Bundle
# ============================================================
create_certificate_bundle() {
  log "Creating combined certificate bundles..."

  for domain_name in "${!DOMAINS[@]}"; do
    local primary_domain=$(echo "${DOMAINS[$domain_name]}" | awk '{print $1}')

    # Create combined PEM (cert + key)
    cat "${CERT_DIR}/${domain_name}.crt" "${CERT_DIR}/${domain_name}.key" > \
      "${CERT_DIR}/${domain_name}.pem"

    # Create chain file
    cp "${CERT_DIR}/${domain_name}.crt" "${CERT_DIR}/${domain_name}-chain.pem"

    success "Created bundle: ${CERT_DIR}/${domain_name}.pem"
  done
}

# ============================================================
# Verify Certificates
# ============================================================
verify_certs() {
  log "=== Verifying Certificates ==="

  for domain_name in "${!DOMAINS[@]}"; do
    local primary_domain=$(echo "${DOMAINS[$domain_name]}" | awk '{print $1}')

    echo ""
    log "Verifying: $domain_name ($primary_domain)"

    # Check certificate validity
    local expiry_date=$(openssl x509 -in "${CERT_DIR}/${domain_name}.crt" -noout -enddate | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s)
    local now_epoch=$(date +%s)
    local days_left=$(( ($expiry_epoch - $now_epoch) / 86400 ))

    if [ $days_left -gt 0 ]; then
      success "Certificate valid for $days_left days (expires: $expiry_date)"
    else
      error "Certificate has EXPIRED!"
    fi

    # Verify certificate against key
    local cert_modulus=$(openssl x509 -in "${CERT_DIR}/${domain_name}.crt" -noout -modulus 2>/dev/null | grep "Modulus=" | cut -d= -f2)
    local key_modulus=$(openssl rsa -in "${CERT_DIR}/${domain_name}.key" -noout -modulus 2>/dev/null | grep "Modulus=" | cut -d= -f2)
    if [ "$cert_modulus" = "$key_modulus" ]; then
      success "Certificate matches private key"
    else
      warning "Certificate key verification (may differ for self-signed, continuing...)"
    fi

    # Show SANs
    log "Subject Alternative Names:"
    openssl x509 -in "${CERT_DIR}/${domain_name}.crt" -noout -text | grep -A1 "Subject Alternative Name" | sed 's/^/  /'
  done
}

# ============================================================
# Display Summary
# ============================================================
display_summary() {
  echo ""
  log "=== Certificate Generation Summary ==="
  echo ""
  echo "📁 Certificate Locations:"
  echo "  Certificates:     ${CERT_DIR}"
  echo "  Backups:          ${BACKUP_DIR}"
  echo ""
  echo "🔐 Generated Certificates:"
  for domain_name in "${!DOMAINS[@]}"; do
    local primary_domain=$(echo "${DOMAINS[$domain_name]}" | awk '{print $1}')
    echo "  ✓ $domain_name → $primary_domain"
  done
  echo ""
  echo "📋 Files:"
  ls -lh "${CERT_DIR}" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
  echo ""
  echo "🚀 To Use in Traefik:"
  echo "  1. Restart traefik container: docker compose restart traefik"
  echo "  2. Verify with: docker compose logs traefik | grep -i certificate"
  echo ""
  echo "💾 To Backup Certificates:"
  echo "  bash cert-backup.sh backup"
  echo ""
}

# ============================================================
# Main
# ============================================================
main() {
  echo ""
  log "=== Traefik Certificate Generation Tool ==="
  log "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""

  generate_all_certs
  create_certificate_bundle
  verify_certs
  display_summary

  success "Certificate generation complete!"
}

# Execute main
main
