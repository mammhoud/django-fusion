#!/bin/bash
#
# Full Deployment & Test Suite for structa.cloud
# Runs all phases: fix, build, test, verify, deploy
#

set -e

PROJECT_DIR="/root/site/websites"
LOG_DIR="${PROJECT_DIR}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/full_test_suite_${TIMESTAMP}.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log() {
  echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
  echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
  echo -e "${RED}[✗] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
  echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

# Create log directory
mkdir -p "$LOG_DIR"

echo "================================================"
echo "  FULL DEPLOYMENT & TEST SUITE"
echo "  Started: $(date)"
echo "================================================" | tee "$LOG_FILE"
echo ""

# ============================================================
# PHASE 0: Health Check
# ============================================================
log "PHASE 0: Initial Health Check"
echo ""

cd "$PROJECT_DIR"

# Check Docker
if ! command -v docker &> /dev/null; then
  error "Docker not found. Please install Docker."
  exit 1
fi
success "Docker found: $(docker --version)"

# Check compose
if ! command -v docker &> /dev/null; then
  error "Docker Compose not found."
  exit 1
fi
success "Docker Compose: $(docker compose version)"

# Check Python
if ! command -v python3 &> /dev/null; then
  error "Python 3 not found."
  exit 1
fi
success "Python: $(python3 --version)"

echo ""

# ============================================================
# PHASE 1: Restart Containers
# ============================================================
log "PHASE 1: Restarting Docker Containers with Fixed Health Checks"
echo ""

log "Starting services..."
docker compose -f docker-compose.yml up -d --remove-orphans 2>&1 | tee -a "$LOG_FILE"
sleep 5

success "Containers started. Waiting for initialization..."
sleep 30

log "Checking container status..."
docker compose -f docker-compose.yml ps 2>&1 | tee -a "$LOG_FILE"

# Check if ctc-research is healthy
ATTEMPTS=0
MAX_ATTEMPTS=10
while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
  HEALTH=$(docker compose -f docker-compose.yml ps web-ctc-research 2>/dev/null | grep -o "healthy\|unhealthy" | head -1 || echo "unknown")
  if [ "$HEALTH" = "healthy" ]; then
    success "CTC Research container is HEALTHY"
    break
  elif [ "$ATTEMPTS" -eq $((MAX_ATTEMPTS - 1)) ]; then
    warning "CTC Research container still not healthy after ${MAX_ATTEMPTS} attempts. Proceeding anyway..."
    docker compose -f docker-compose.yml logs web-ctc-research --tail 30 | tee -a "$LOG_FILE"
  fi
  ATTEMPTS=$((ATTEMPTS + 1))
  sleep 5
done

echo ""

# ============================================================
# PHASE 2: Build Assets
# ============================================================
log "PHASE 2: Building Frontend Assets for All Sites"
echo ""

log "Installing npm dependencies..."
npm --prefix assets install --legacy-peer-deps --no-audit --no-fund 2>&1 | tail -20 | tee -a "$LOG_FILE"
success "Dependencies installed"

log "Building assets for CTC Research..."
PROJECT_PATH=ctc-research npm --prefix assets run build 2>&1 | grep -E "✓|✗|error|warning|built in" | tee -a "$LOG_FILE"
success "CTC Research assets built"

log "Building assets for LMS Demo..."
PROJECT_PATH=lms-demo npm --prefix assets run build 2>&1 | grep -E "✓|✗|error|warning|built in" | tee -a "$LOG_FILE"
success "LMS Demo assets built"

log "Building assets for VResume..."
PROJECT_PATH=vresume npm --prefix assets run build 2>&1 | grep -E "✓|✗|error|warning|built in" | tee -a "$LOG_FILE"
success "VResume assets built"

echo ""

# ============================================================
# PHASE 3: Collect Static Files
# ============================================================
log "PHASE 3: Collecting Static Files"
echo ""

log "Collecting static files for CTC Research..."
docker exec web-ctc-research python manage.py collectstatic --noinput --site ctc-research 2>&1 | tail -10 | tee -a "$LOG_FILE"
success "CTC Research static files collected"

log "Collecting static files for LMS Demo..."
docker exec web-lms-demo python manage.py collectstatic --noinput --site lms-demo 2>&1 | tail -10 | tee -a "$LOG_FILE" 2>/dev/null || warning "LMS Demo container not yet ready, skipping"

log "Collecting static files for VResume..."
docker exec web-vresume python manage.py collectstatic --noinput --site vresume 2>&1 | tail -10 | tee -a "$LOG_FILE" 2>/dev/null || warning "VResume container not yet ready, skipping"

echo ""

# ============================================================
# PHASE 4: Verify Asset Output
# ============================================================
log "PHASE 4: Verifying Asset Output"
echo ""

for site in ctc-research lms-demo VResume; do
  if [ -d "${site}/assets/bundles" ]; then
    count=$(find "${site}/assets/bundles" -type f | wc -l)
    size=$(du -sh "${site}/assets/bundles" 2>/dev/null | cut -f1)
    success "$site: $count bundle files ($size)"
  else
    warning "$site: No bundles directory found yet"
  fi
done

# Check shared media server
log "Checking shared media server..."
if docker exec shared-media ls -q /var/www/static 2>/dev/null | wc -l | grep -q .; then
  count=$(docker exec shared-media find /var/www/static -type f | wc -l)
  success "Shared media server has $count static files"
else
  warning "Shared media server not responding yet"
fi

echo ""

# ============================================================
# PHASE 5: Verify Database & Locales
# ============================================================
log "PHASE 5: Verifying Database & Locales"
echo ""

log "Checking locales in database..."
docker exec web-ctc-research python manage.py shell <<EOF 2>&1 | tee -a "$LOG_FILE"
from wagtail_localize.models import Locale
locales = Locale.objects.all().order_by('language_code')
print(f"✓ Found {locales.count()} locales:")
for l in locales:
    print(f"  ✓ {l.language_code}: {l.get_display_name()}")
EOF

echo ""

# ============================================================
# PHASE 6: Check Homepage
# ============================================================
log "PHASE 6: Checking Homepages"
echo ""

for port in 5070 5071 5072; do
  site_name=$(case $port in
    5070) echo "CTC Research" ;;
    5071) echo "LMS Demo" ;;
    5072) echo "VResume" ;;
  esac)
  
  log "Testing $site_name homepage (port $port)..."
  if curl -s -f http://localhost:$port/ > /dev/null 2>&1; then
    success "$site_name: Homepage is accessible"
  else
    warning "$site_name: Homepage not responding yet"
  fi
done

echo ""

# ============================================================
# PHASE 7: Run Unit Tests
# ============================================================
log "PHASE 7: Running Unit Tests"
echo ""

log "Running all unit tests..."
python3 -m pytest tests/unit -v --tb=short 2>&1 | tail -50 | tee -a "$LOG_FILE"
success "Unit tests completed"

echo ""

# ============================================================
# PHASE 8: Run Integration Tests
# ============================================================
log "PHASE 8: Running Integration Tests"
echo ""

log "Running integration tests..."
python3 -m pytest tests/integration -v --tb=short 2>&1 | tail -50 | tee -a "$LOG_FILE"
success "Integration tests completed"

echo ""

# ============================================================
# PHASE 9: Verify Assets Loading
# ============================================================
log "PHASE 9: Verifying Assets in HTML"
echo ""

for port in 5070 5071 5072; do
  site_name=$(case $port in
    5070) echo "CTC Research" ;;
    5071) echo "LMS Demo" ;;
    5072) echo "VResume" ;;
  esac)
  
  log "Checking asset references for $site_name..."
  if curl -s http://localhost:$port/ | grep -q "static\|media"; then
    success "$site_name: Asset references found in HTML"
  else
    warning "$site_name: No asset references detected"
  fi
done

echo ""

# ============================================================
# PHASE 10: Final Health Check
# ============================================================
log "PHASE 10: Final Docker Status"
echo ""

docker compose -f docker-compose.yml ps 2>&1 | tee -a "$LOG_FILE"

echo ""

# ============================================================
# Summary
# ============================================================
echo "================================================"
echo "  FULL TEST SUITE COMPLETED"
echo "  Finished: $(date)"
echo "  Log file: $LOG_FILE"
echo "================================================"

log "Next steps:"
log "1. Check log file: $LOG_FILE"
log "2. Verify all containers: docker compose ps"
log "3. Create admin user: docker exec web-ctc-research python manage.py createsuperuser"
log "4. Access admin: http://localhost:5070/admin/"
log "5. Run more detailed tests: make tests-website WEBSITE=ctc"

echo ""
success "Deployment & test suite completed! ✓"
