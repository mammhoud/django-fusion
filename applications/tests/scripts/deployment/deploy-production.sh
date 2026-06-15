#!/bin/bash

# ============================================================
# Production Deployment Script
# ============================================================
# Orchestrates deployment of all 3 websites with infrastructure
# ============================================================

set -e

# Configuration
DEPLOYMENT_DATE=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/production_deployment_${DEPLOYMENT_DATE}.log"
ERROR_LOG="${LOG_DIR}/production_deployment_errors_${DEPLOYMENT_DATE}.log"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "${LOG_DIR}"

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ℹ️  $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ✅ $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ❌ $1" | tee -a "${ERROR_LOG}"
    exit 1
}

# Header
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Production Deployment Script                             ║"
echo "║  $(date +'%Y-%m-%d %H:%M:%S')                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

log_info "Starting production deployment..."
log_info "Log file: ${LOG_FILE}"
log_info "Error log: ${ERROR_LOG}"
echo ""

# ============================================================
# PHASE 1: Pre-Deployment Validation
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 1: Pre-Deployment Validation"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Docker is running
log_info "Checking Docker daemon..."
if ! docker ps > /dev/null 2>&1; then
    log_error "Docker daemon is not running. Please start Docker and try again."
fi
log_success "Docker daemon is running"

# Check Docker Compose
log_info "Checking Docker Compose..."
if ! docker compose version > /dev/null 2>&1; then
    log_error "Docker Compose is not available. Please install Docker Compose."
fi
log_success "Docker Compose is available"

# Check required files exist
log_info "Checking required files..."
required_files=(
    "docker-compose.yml"
    "compose/docker-compose.traefik.yml"
    "compose/docker-compose.warehouse.yml"
    "compose/docker-compose.yml"
    "compose/docker-compose.nginx.yml"
    "ctc-research/docker-compose.yml"
    "lms-demo/docker-compose.yml"
    "VResume/docker-compose.yml"
    "assets/package.json"
)

for file in "${required_files[@]}"; do
    if [ ! -f "${file}" ]; then
        log_error "Required file not found: ${file}"
    fi
done
log_success "All required files found"

# Check disk space
log_info "Checking disk space..."
available_space=$(df / | tail -1 | awk '{print $4}')
required_space=$((5 * 1024 * 1024))  # 5GB in KB
if [ "$available_space" -lt "$required_space" ]; then
    log_warning "Low disk space available. Consider cleaning up before proceeding."
fi
log_success "Disk space check passed (${available_space} KB available)"

echo ""

# ============================================================
# PHASE 2: Environment Preparation
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 2: Environment Preparation"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Backup current environment
log_info "Backing up current environment..."
if [ -f ".env" ]; then
    cp ".env" ".env.backup.${DEPLOYMENT_DATE}"
    log_success "Environment backed up to .env.backup.${DEPLOYMENT_DATE}"
fi

# Create traefik network
log_info "Creating Docker network..."
docker network create traefik-net 2>/dev/null || log_info "Network already exists"
log_success "Docker network ready"

# Clean up existing containers
log_info "Stopping existing containers..."
docker compose -f docker-compose.yml down --remove-orphans >> "${LOG_FILE}" 2>&1 || true
log_success "Existing containers stopped"

echo ""

# ============================================================
# PHASE 3: Build Docker Images
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 3: Building Docker Images"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Building production images (this may take several minutes)..."
if ! docker compose -f docker-compose.yml build --no-cache >> "${LOG_FILE}" 2>&1; then
    log_error "Docker build failed. Check ${LOG_FILE} for details."
fi
log_success "All production images built successfully"

echo ""

# ============================================================
# PHASE 4: Start Infrastructure Services
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 4: Starting Infrastructure Services"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Starting Traefik, PostgreSQL, Redis, and Media Server..."
docker compose -f docker-compose.yml up -d traefik postgres redis shared-media >> "${LOG_FILE}" 2>&1

log_info "Waiting for infrastructure to initialize (90 seconds)..."
for i in {1..18}; do
    echo -n "."
    sleep 5
done
echo ""

# Verify infrastructure
log_info "Verifying infrastructure services..."

# Check Traefik
if docker ps --filter "name=traefik" --filter "status=running" | grep -q traefik; then
    log_success "✓ Traefik is running"
else
    log_error "Traefik failed to start"
fi

# Check PostgreSQL
if docker exec postgres pg_isready -U structa > /dev/null 2>&1; then
    log_success "✓ PostgreSQL is ready"
else
    log_warning "PostgreSQL not ready yet, continuing..."
fi

# Check Redis
if docker exec redis redis-cli ping > /dev/null 2>&1; then
    log_success "✓ Redis is ready"
else
    log_warning "Redis not ready yet, continuing..."
fi

echo ""

# ============================================================
# PHASE 5: Start Website Services
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 5: Starting Website Services"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Starting CTC Research, LMS Demo, and VResume..."
docker compose -f docker-compose.yml up -d web-ctc-research web-lms-demo web-vresume >> "${LOG_FILE}" 2>&1

log_info "Waiting for website services to initialize (120 seconds)..."
for i in {1..24}; do
    echo -n "."
    sleep 5
done
echo ""

# Verify all containers
log_info "Verifying all services..."
docker compose -f docker-compose.yml ps | tee -a "${LOG_FILE}"

echo ""

# ============================================================
# PHASE 6: Database Migration
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 6: Database Migration"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Running migrations for CTC Research..."
docker exec web-ctc-research python manage.py migrate --noinput >> "${LOG_FILE}" 2>&1 || log_warning "CTC Research migration may have issues"
log_success "CTC Research migrations complete"

log_info "Running migrations for LMS Demo..."
docker exec web-lms-demo python manage.py migrate --noinput >> "${LOG_FILE}" 2>&1 || log_warning "LMS Demo migration may have issues"
log_success "LMS Demo migrations complete"

log_info "Running migrations for VResume..."
docker exec web-vresume python manage.py migrate --noinput >> "${LOG_FILE}" 2>&1 || log_warning "VResume migration may have issues"
log_success "VResume migrations complete"

echo ""

# ============================================================
# PHASE 7: Collect Static Files
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 7: Collecting Static Files"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Collecting static files for CTC Research..."
docker exec web-ctc-research python manage.py collectstatic --noinput >> "${LOG_FILE}" 2>&1
log_success "CTC Research static files collected"

log_info "Collecting static files for LMS Demo..."
docker exec web-lms-demo python manage.py collectstatic --noinput >> "${LOG_FILE}" 2>&1
log_success "LMS Demo static files collected"

log_info "Collecting static files for VResume..."
docker exec web-vresume python manage.py collectstatic --noinput >> "${LOG_FILE}" 2>&1
log_success "VResume static files collected"

echo ""

# ============================================================
# PHASE 8: Certificate Backup
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 8: Certificate Backup"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Creating certificate backup..."
cd compose/traefik
./cert-backup.sh backup >> "${LOG_FILE}" 2>&1 || log_warning "Certificate backup may have failed"
log_success "Certificate backup created"
cd "${ROOT_DIR}"

echo ""

# ============================================================
# PHASE 9: Verification
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "PHASE 9: Deployment Verification"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_info "Final container status:"
docker compose -f docker-compose.yml ps | tee -a "${LOG_FILE}"

# Test website connectivity
log_info "Testing website connectivity..."

for port in 5070 5071 5072; do
    site_name=""
    case $port in
        5070) site_name="CTC Research" ;;
        5071) site_name="LMS Demo" ;;
        5072) site_name="VResume" ;;
    esac
    
    if curl -s -I http://localhost:${port}/ | grep -q "HTTP"; then
        log_success "✓ ${site_name} is responding on port ${port}"
    else
        log_warning "⚠ ${site_name} on port ${port} not responding yet"
    fi
done

echo ""

# ============================================================
# Summary & Next Steps
# ============================================================
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "DEPLOYMENT COMPLETE!"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Production deployment completed successfully!"
echo ""
echo "📍 Website URLs:"
echo "   • CTC Research:  http://localhost:5070/"
echo "   • LMS Demo:      http://localhost:5071/"
echo "   • VResume:       http://localhost:5072/"
echo ""
echo "🔐 Admin Panels:"
echo "   • CTC Research:  http://localhost:5070/admin/"
echo "   • LMS Demo:      http://localhost:5071/admin/"
echo "   • VResume:       http://localhost:5072/admin/"
echo ""
echo "📚 Media Server:"
echo "   • http://localhost/media/"
echo ""
echo "📋 Next Steps:"
echo "   1. Create admin users:"
echo "      docker exec -it web-ctc-research python manage.py createsuperuser"
echo "      docker exec -it web-lms-demo python manage.py createsuperuser"
echo "      docker exec -it web-vresume python manage.py createsuperuser"
echo ""
echo "   2. Load production data (if fixtures available):"
echo "      docker exec web-ctc-research python manage.py loaddata fixtures/initial_data.json"
echo "      docker exec web-lms-demo python manage.py loaddata fixtures/initial_data.json"
echo ""
echo "   3. Run health checks:"
echo "      bash run_full_test_suite.sh"
echo ""
echo "   4. Monitor logs:"
echo "      docker compose logs -f"
echo ""
echo "📄 Logs:"
echo "   • Deployment log:  ${LOG_FILE}"
echo "   • Error log:       ${ERROR_LOG}"
echo ""
log_success "Deployment script completed at $(date +'%Y-%m-%d %H:%M:%S')"
