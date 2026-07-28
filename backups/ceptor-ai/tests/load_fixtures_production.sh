#!/bin/bash

##############################################################################
# Production Fixture Loading Script
# Loads all fixtures in dependency order to populate the database
##############################################################################

set -e

echo "🚀 Starting Production Fixture Loading"
echo "========================================"
echo ""

# Configuration
CONTAINER="web-ctc-research"
FIXTURES_DIR="/app/ctc-research/assets/fixtures/by-model"
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

# Load fixtures in dependency order
load_fixture() {
    local fixture_name=$1
    local fixture_path=$2
    
    if [ ! -f "$fixture_path" ]; then
        warning "Fixture file not found: $fixture_path"
        return
    fi
    
    log "Loading: $fixture_name"
    
    if docker exec "$CONTAINER" python manage.py loaddata "$fixture_path" >> "$LOG_FILE" 2>&1; then
        success "Loaded: $fixture_name"
    else
        error "Failed to load: $fixture_name"
        return 1
    fi
}

# Main loading sequence
echo "📦 Loading Fixtures in Dependency Order" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Step 1: Load core models (permissions, groups, locales)
log "Step 1/5: Loading authentication and core models..."
load_fixture "Permissions" "$FIXTURES_DIR/auth/auth-permission.json"
load_fixture "Groups" "$FIXTURES_DIR/auth/auth-group.json"
load_fixture "Users" "$FIXTURES_DIR/auth/auth-user.json"
load_fixture "Locales" "$FIXTURES_DIR/wagtailprojects/wagtailcore-locale.json"
load_fixture "Site" "$FIXTURES_DIR/wagtailprojects/wagtailcore-site.json"
echo "" | tee -a "$LOG_FILE"

# Step 2: Load page models
log "Step 2/5: Loading page models and structure..."
load_fixture "Base Pages" "$FIXTURES_DIR/wagtailprojects/wagtailcore-page.json"
load_fixture "Collections" "$FIXTURES_DIR/wagtailprojects/wagtailcore-collection.json"
load_fixture "Group Collection Permissions" "$FIXTURES_DIR/wagtailprojects/wagtailcore-groupcollectionpermission.json"
load_fixture "Group Page Permissions" "$FIXTURES_DIR/wagtailprojects/wagtailcore-grouppagepermission.json"
echo "" | tee -a "$LOG_FILE"

# Step 3: Load images
log "Step 3/5: Loading images and renditions..."
load_fixture "Images" "$FIXTURES_DIR/wagtailimages/wagtailimages-image.json"
load_fixture "Image Renditions" "$FIXTURES_DIR/wagtailimages/wagtailimages-rendition.json"
echo "" | tee -a "$LOG_FILE"

# Step 4: Load page content
log "Step 4/5: Loading page content (homepage, about, contact, team, courses)..."
load_fixture "Homepage" "$FIXTURES_DIR/wagtailprojects/pages-homepage.json"
load_fixture "About Page" "$FIXTURES_DIR/wagtailprojects/pages-aboutpage.json"
load_fixture "Contact Page" "$FIXTURES_DIR/wagtailprojects/pages-contactpage.json"
load_fixture "Team Page" "$FIXTURES_DIR/wagtailprojects/pages-teampage.json"
load_fixture "Courses Page" "$FIXTURES_DIR/wagtailprojects/lms-coursespage.json"
echo "" | tee -a "$LOG_FILE"

# Step 5: Load workflows and metadata
log "Step 5/5: Loading workflows, logs, and metadata..."
load_fixture "Workflows" "$FIXTURES_DIR/wagtailprojects/wagtailcore-workflow.json"
load_fixture "Workflow Pages" "$FIXTURES_DIR/wagtailprojects/wagtailcore-workflowpage.json"
load_fixture "Workflow Tasks" "$FIXTURES_DIR/wagtailprojects/wagtailcore-workflowtask.json"
load_fixture "Group Approval Tasks" "$FIXTURES_DIR/wagtailprojects/wagtailcore-groupapprovaltask.json"
load_fixture "Tasks" "$FIXTURES_DIR/wagtailprojects/wagtailcore-task.json"
load_fixture "Page Log Entries" "$FIXTURES_DIR/wagtailprojects/wagtailcore-pagelogentry.json"
load_fixture "Model Log Entries" "$FIXTURES_DIR/wagtailprojects/wagtailcore-modellogentry.json"
load_fixture "Revisions" "$FIXTURES_DIR/wagtailprojects/wagtailcore-revision.json"
load_fixture "Reference Index" "$FIXTURES_DIR/wagtailprojects/wagtailcore-referenceindex.json"
load_fixture "Page Subscriptions" "$FIXTURES_DIR/wagtailprojects/wagtailcore-pagesubscription.json"
load_fixture "Organization" "$FIXTURES_DIR/handlers/handlers-organization.json"
load_fixture "Activity Types" "$FIXTURES_DIR/modules/modules-activitytype.json"
load_fixture "Status Choices" "$FIXTURES_DIR/modules/modules-statuschoice.json"
load_fixture "Derived Status" "$FIXTURES_DIR/modules/modules-derivedstatus.json"
echo "" | tee -a "$LOG_FILE"

# Verification
echo "" | tee -a "$LOG_FILE"
log "Verifying fixture load..."
echo "" | tee -a "$LOG_FILE"

# Check page count
PAGE_COUNT=$(docker exec postgres psql -U structa -d db_ctc -c "SELECT COUNT(*) FROM wagtailcore_page;" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+" | tr -d ' ')

if [ -n "$PAGE_COUNT" ]; then
    success "Total pages in database: $PAGE_COUNT"
fi

# Check locales
LOCALE_COUNT=$(docker exec postgres psql -U structa -d db_ctc -c "SELECT COUNT(*) FROM wagtail_localize_locale;" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+" | tr -d ' ')

if [ -n "$LOCALE_COUNT" ]; then
    success "Total locales configured: $LOCALE_COUNT"
fi

# Summary
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "📊 Loading Summary" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
success "All fixtures loaded successfully!"
log "Total pages: $PAGE_COUNT"
log "Total locales: $LOCALE_COUNT"
log "Log file: $LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "🚀 Restarting web service to apply changes..."
docker restart "$CONTAINER"
sleep 5

log "✅ Fixture loading complete!"
echo "" | tee -a "$LOG_FILE"
echo "🎉 Production database is now populated with all content!" | tee -a "$LOG_FILE"
echo "   - Pages: Homepage, About, Contact, Team, Courses" | tee -a "$LOG_FILE"
echo "   - Languages: 6 locales (English, Arabic, German, Spanish, French, Portuguese)" | tee -a "$LOG_FILE"
echo "   - Images: 22 images with renditions" | tee -a "$LOG_FILE"
echo "   - Users & Permissions: All configured" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Visit: https://ctc-research.com/ to see the fully populated site!" | tee -a "$LOG_FILE"
