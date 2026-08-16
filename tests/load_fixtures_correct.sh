#!/bin/bash

##############################################################################
# Production Fixture Loading Script - Corrected Version
# Loads all fixtures using Django's loaddata command
##############################################################################

set -e

echo "🚀 Starting Production Fixture Loading"
echo "========================================"
echo ""

# Configuration
CONTAINER="web-precis-ctc"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="fixture_loading_${TIMESTAMP}.log"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Load fixtures using Django command
load_fixture() {
    local fixture_name=$1
    local fixture_path=$2
    
    log "Loading: $fixture_name"
    
    if docker exec "$CONTAINER" python manage.py loaddata "$fixture_path" >> "$LOG_FILE" 2>&1; then
        success "Loaded: $fixture_name"
    else
        warning "Issue loading: $fixture_name (may already exist or have dependencies)"
    fi
}

# Main loading sequence
echo "📦 Loading Fixtures in Dependency Order" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Step 1: Load core models (permissions, groups, locales)
log "Step 1/5: Loading authentication and core models..."
load_fixture "Permissions" "precis-ctc/assets/fixtures/by-model/auth/auth-permission"
load_fixture "Groups" "precis-ctc/assets/fixtures/by-model/auth/auth-group"
load_fixture "Users" "precis-ctc/assets/fixtures/by-model/auth/auth-user"
load_fixture "Locales" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-locale"
load_fixture "Site" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-site"
echo "" | tee -a "$LOG_FILE"

# Step 2: Load page structure
log "Step 2/5: Loading page structure..."
load_fixture "Base Pages" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-page"
load_fixture "Collections" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-collection"
load_fixture "Group Collection Permissions" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-groupcollectionpermission"
load_fixture "Group Page Permissions" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-grouppagepermission"
echo "" | tee -a "$LOG_FILE"

# Step 3: Load images
log "Step 3/5: Loading images and renditions..."
load_fixture "Images" "precis-ctc/assets/fixtures/by-model/wagtailimages/wagtailimages-image"
load_fixture "Image Renditions" "precis-ctc/assets/fixtures/by-model/wagtailimages/wagtailimages-rendition"
echo "" | tee -a "$LOG_FILE"

# Step 4: Load page content
log "Step 4/5: Loading page content..."
load_fixture "Homepage" "precis-ctc/assets/fixtures/by-model/wagtailprojects/pages-homepage"
load_fixture "About Page" "precis-ctc/assets/fixtures/by-model/wagtailprojects/pages-aboutpage"
load_fixture "Contact Page" "precis-ctc/assets/fixtures/by-model/wagtailprojects/pages-contactpage"
load_fixture "Team Page" "precis-ctc/assets/fixtures/by-model/wagtailprojects/pages-teampage"
load_fixture "Courses Page" "precis-ctc/assets/fixtures/by-model/wagtailprojects/lms-coursespage"
echo "" | tee -a "$LOG_FILE"

# Step 5: Load workflows and metadata
log "Step 5/5: Loading workflows and metadata..."
load_fixture "Workflows" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-workflow"
load_fixture "Workflow Pages" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-workflowpage"
load_fixture "Workflow Tasks" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-workflowtask"
load_fixture "Group Approval Tasks" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-groupapprovaltask"
load_fixture "Tasks" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-task"
load_fixture "Page Log Entries" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-pagelogentry"
load_fixture "Model Log Entries" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-modellogentry"
load_fixture "Revisions" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-revision"
load_fixture "Reference Index" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-referenceindex"
load_fixture "Page Subscriptions" "precis-ctc/assets/fixtures/by-model/wagtailprojects/wagtailcore-pagesubscription"
load_fixture "Organization" "precis-ctc/assets/fixtures/by-model/handlers/handlers-organization"
load_fixture "Activity Types" "precis-ctc/assets/fixtures/by-model/modules/modules-activitytype"
load_fixture "Status Choices" "precis-ctc/assets/fixtures/by-model/modules/modules-statuschoice"
load_fixture "Derived Status" "precis-ctc/assets/fixtures/by-model/modules/modules-derivedstatus"
echo "" | tee -a "$LOG_FILE"

# Verification
echo "" | tee -a "$LOG_FILE"
log "Verifying fixture load..."
echo "" | tee -a "$LOG_FILE"

# Check page count
PAGE_COUNT=$(docker exec postgres psql -U structa -d db_ctc -c "SELECT COUNT(*) FROM wagtailcore_page;" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+" | tr -d ' ')

if [ -n "$PAGE_COUNT" ] && [ "$PAGE_COUNT" -gt "2" ]; then
    success "Total pages in database: $PAGE_COUNT"
else
    warning "Pages in database: $PAGE_COUNT (may need manual loading)"
fi

# Check locales
LOCALE_COUNT=$(docker exec postgres psql -U structa -d db_ctc -c "SELECT COUNT(*) FROM wagtail_localize_locale;" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+" | tr -d ' ')

if [ -n "$LOCALE_COUNT" ] && [ "$LOCALE_COUNT" -gt "0" ]; then
    success "Total locales configured: $LOCALE_COUNT"
fi

# Summary
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "📊 Loading Summary" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
log "Fixture loading process completed"
log "Total pages: $PAGE_COUNT"
log "Total locales: $LOCALE_COUNT"
log "Log file: $LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "🚀 Restarting web service..." | tee -a "$LOG_FILE"
docker restart "$CONTAINER"
sleep 5

log "✅ Production fixture loading complete!" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "🎉 Production database update complete!" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
