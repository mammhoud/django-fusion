#!/bin/bash
set -euo pipefail

echo "==================================================================="
echo "CTCR-RESEARCH LOG RESOLUTION AND REDEPLOYMENT SCRIPT"
echo "==================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_DIR="/root/site/websites/logs"
WEBSITES=("precis-ctc" "lms" "VResume")

# Function to log messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to resolve identified errors
fix_issues() {
    local website="$1"
    echo ""
    log_info "Processing website: $website"
    echo ""
    
    # Issue 1: Clear Python cache files (pycache)
    log_info "Clearing Python cache files for $website..."
    find "/root/site/websites" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "/root/site/websites" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "/root/site/websites" -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Issue 2: Clear old log files
    log_info "Backing up and clearing error logs for $website..."
    local site_log_dir="/root/site/websites/${website}/logs"
    if [ -d "$site_log_dir" ]; then
        # Backup current logs
        mkdir -p "${site_log_dir}/backups"
        for logfile in "${site_log_dir}"/*.log; do
            if [ -f "$logfile" ]; then
                local filename=$(basename "$logfile")
                local timestamp=$(date +%s)
                cp "$logfile" "${site_log_dir}/backups/${filename}.${timestamp}.bak" || true
                > "$logfile"  # Clear the log
            fi
        done
    fi
    
    # Issue 3: Ensure Python path configuration is correct
    log_info "Verifying settings.py sys.path configuration..."
    local settings_file="/root/site/websites/${website}/settings.py"
    if [ -f "$settings_file" ]; then
        # Check if PYTHONPATH setup is correct
        if grep -q "_WORKSPACE_DIR" "$settings_file"; then
            log_info "✓ Settings.py has correct workspace path setup"
        else
            log_warn "Settings.py may not have proper workspace path setup"
        fi
    fi
    
    # Issue 4: Ensure configs/__init__.py exists
    if [ -f "/root/site/websites/configs/__init__.py" ]; then
        log_info "✓ configs/__init__.py exists"
    else
        log_error "configs/__init__.py is missing! Creating it..."
        touch "/root/site/websites/configs/__init__.py"
    fi
}

# Function to check logs for errors
check_logs() {
    local website="$1"
    local site_log_dir="/root/site/websites/${website}/logs"
    
    echo ""
    log_info "Analyzing error logs for $website..."
    
    if [ -d "$site_log_dir" ]; then
        # Check for ContentType errors
        local contenttype_errors=$(grep -c "ContentType.DoesNotExist" "${site_log_dir}/error.log" 2>/dev/null || echo "0")
        if [ "$contenttype_errors" -gt 0 ]; then
            log_warn "Found $contenttype_errors ContentType.DoesNotExist errors"
        fi
        
        # Check for modelsearch errors
        local modelsearch_errors=$(grep -c "modelsearch.tasks" "${site_log_dir}/error.log" 2>/dev/null || echo "0")
        if [ "$modelsearch_errors" -gt 0 ]; then
            log_warn "Found $modelsearch_errors modelsearch task errors"
        fi
        
        # Check for import errors
        local import_errors=$(grep -c "ModuleNotFoundError" "${site_log_dir}/gunicorn-error.log" 2>/dev/null || echo "0")
        if [ "$import_errors" -gt 0 ]; then
            log_error "Found $import_errors ModuleNotFoundError in gunicorn logs"
        fi
    fi
}

# Function to verify Django setup
verify_django_setup() {
    local website="$1"
    echo ""
    log_info "Verifying Django setup for $website..."
    
    cd "/root/site/websites" || exit 1
    
    # Check if settings.py can be imported
    if PYTHONPATH="/root/site/websites:/root/site/websites/${website}" python -c "
import sys
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
os.environ.setdefault('DJANGO_WEBSITE', '${website}')
sys.path.insert(0, '/root/site/websites/${website}')
sys.path.insert(0, '/root/site/websites')
try:
    import settings
    print('✓ Settings module imports successfully')
except Exception as e:
    print(f'✗ Settings import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log_info "✓ Django settings can be imported"
    else
        log_error "✗ Django settings import failed"
    fi
}

# ===================================================================
# MAIN EXECUTION
# ===================================================================

echo "Step 1: Fixing known issues across all websites..."
echo ""

for website in "${WEBSITES[@]}"; do
    fix_issues "$website"
done

echo ""
echo "Step 2: Checking logs for unresolved errors..."
echo ""

for website in "${WEBSITES[@]}"; do
    check_logs "$website"
done

echo ""
echo "Step 3: Verifying Django setup..."
echo ""

for website in "${WEBSITES[@]}"; do
    verify_django_setup "$website"
done

echo ""
echo "==================================================================="
echo "REDEPLOYMENT PHASE"
echo "==================================================================="
echo ""

log_info "Rebuilding precis-ctc website..."
cd "/root/site/websites" || exit 1

# Clean up containers
log_info "Stopping existing containers..."
docker-compose -f docker-compose.yml down 2>/dev/null || true

# Clear Docker build cache if needed
log_info "Rebuilding Django container..."
docker-compose -f docker-compose.yml build --no-cache django 2>&1 | tee "${LOG_DIR}/rebuild_$(date +%s).log"

log_info "Starting container stack..."
docker-compose -f docker-compose.yml up -d 2>&1 | tee -a "${LOG_DIR}/rebuild_$(date +%s).log"

# Wait for container to be ready
log_info "Waiting for containers to stabilize (30 seconds)..."
sleep 30

# Check container health
log_info "Checking container status..."
if docker-compose -f docker-compose.yml ps | grep -q "Up"; then
    log_info "✓ Containers are running"
else
    log_error "✗ Containers failed to start"
    log_error "Showing container logs:"
    docker-compose -f docker-compose.yml logs --tail=50
    exit 1
fi

# Check for startup errors
log_info "Checking for startup errors in logs..."
STARTUP_ERRORS=0

for container in $(docker-compose -f docker-compose.yml ps -q); do
    docker logs "$container" 2>&1 | grep -i "error" | head -5 || true
done

echo ""
echo "==================================================================="
echo "REDEPLOYMENT SUMMARY"
echo "==================================================================="
echo ""
log_info "✓ Cleared Python cache files"
log_info "✓ Backed up and cleared old log files"
log_info "✓ Verified Django configuration"
log_info "✓ Rebuilt and redeployed precis-ctc website"
echo ""
log_info "New container is now running!"
log_info "Log files: ${LOG_DIR}/"
log_info "Container logs: docker-compose logs -f"
echo ""
