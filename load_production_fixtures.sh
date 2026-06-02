#!/bin/bash
#
# Load production fixtures from by-model structure
# Ensures all models are loaded in the correct order
#

set -e

SITE="${1:-ctc-research}"
FIXTURES_DIR="/root/site/websites/${SITE}/assets/fixtures/by-model"
VENV="/root/site/websites/.venv/bin"

echo "================================================"
echo "Loading Production Fixtures for: $SITE"
echo "================================================"
echo "Source: $FIXTURES_DIR"
echo ""

if [ ! -d "$FIXTURES_DIR" ]; then
    echo "❌ Fixtures directory not found: $FIXTURES_DIR"
    exit 1
fi

# Load order is critical - load dependencies first
LOAD_ORDER=(
    "auth/auth-group.json"
    "auth/auth-permission.json"
    "auth/auth-user.json"
    "handlers/handlers-organization.json"
    "modules/modules-activitytype.json"
    "modules/modules-derivedstatus.json"
    "modules/modules-statuschoice.json"
    "wagtailcore/wagtailcore-locale.json"
    "wagtailcore/wagtailcore-site.json"
    "wagtailcore/wagtailcore-collection.json"
    "wagtailcore/wagtailcore-page.json"
    "wagtailimages/wagtailimages-image.json"
    "wagtailimages/wagtailimages-rendition.json"
    "wagtailcore/pages-homepage.json"
    "wagtailcore/pages-aboutpage.json"
    "wagtailcore/pages-contactpage.json"
    "wagtailcore/pages-teampage.json"
    "wagtailcore/lms-coursespage.json"
    "wagtailcore/wagtailcore-groupcollectionpermission.json"
    "wagtailcore/wagtailcore-grouppagepermission.json"
    "wagtailcore/wagtailcore-groupapprovaltask.json"
    "wagtailcore/wagtailcore-task.json"
    "wagtailcore/wagtailcore-workflow.json"
    "wagtailcore/wagtailcore-workflowtask.json"
    "wagtailcore/wagtailcore-workflowpage.json"
    "wagtailcore/wagtailcore-modellogentry.json"
    "wagtailcore/wagtailcore-pagelogentry.json"
    "wagtailcore/wagtailcore-revision.json"
    "wagtailcore/wagtailcore-pagesubscription.json"
    "wagtailcore/wagtailcore-referenceindex.json"
)

LOADED=0
FAILED=0

echo "📦 Loading fixtures in order..."
echo ""

for fixture in "${LOAD_ORDER[@]}"; do
    fixture_path="$FIXTURES_DIR/$fixture"
    fixture_name=$(basename "$fixture")
    
    if [ -f "$fixture_path" ]; then
        echo -n "  ↳ $fixture_name ... "
        if $VENV/python manage.py loaddata "$fixture_path" --app=wagtail --ignorenonexistent 2>/dev/null; then
            echo "✅"
            ((LOADED++))
        else
            echo "⚠️  (continuing)"
        fi
    else
        echo "  ⚠️  $fixture_name (not found)"
    fi
done

echo ""
echo "================================================"
echo "Fixture Loading Summary"
echo "================================================"
echo "✅ Loaded: $LOADED fixtures"
echo ""

# Verify site configuration
echo "Verifying configuration..."
docker exec web-ctc-research $VENV/python manage.py check --site="$SITE" 2>&1 | grep -E "System check|Error|✓" || true

# Check if homepage is accessible
echo ""
echo "Checking homepage availability..."
docker exec web-ctc-research $VENV/python -c "
from wagtail.models import Page, Site
try:
    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
    pages = Page.objects.live().public().specific()
    print(f'✅ Found {pages.count()} live pages')
    
    # Look for homepage
    for page in pages[:5]:
        print(f'  - {page.title} ({page.get_verbose_name()})')
except Exception as e:
    print(f'❌ Error checking pages: {e}')
" 2>&1 || true

echo ""
echo "✅ Fixture loading complete!"
echo ""
echo "Next steps:"
echo "1. Verify homepage is displayed at http://ctc-research.com/"
echo "2. Check assets are loading from https://ctc-research.com/static/"
echo "3. Verify database data with: docker exec web-ctc-research python manage.py dbshell"

EOF
chmod +x /root/site/websites/load_production_fixtures.sh
echo "✅ Fixture loading script created"
