#!/bin/bash

# Initialize all website databases with migrations and initial data

set -e

echo "🗄️  Initializing all website databases..."

# Function to initialize a website
initialize_website() {
    local site_name=$1
    local container_name=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Initializing $site_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    CONTAINER=$(docker ps -q -f "name=$container_name" | head -1)
    if [ -z "$CONTAINER" ]; then
        echo "❌ $container_name not found"
        return 1
    fi
    
    echo "Running migrations..."
    docker exec $CONTAINER python manage.py migrate --noinput
    
    echo "Creating superuser if needed..."
    docker exec $CONTAINER python manage.py shell << 'PYTHON'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'mk_pAssWord123')
    print("✅ Superuser created")
else:
    print("ℹ️  Superuser already exists")
PYTHON
    
    echo "✅ $site_name database initialized"
}

# Initialize each website
initialize_website "CTC Research" "ctc-web"
initialize_website "LMS Demo" "lms-web"
initialize_website "VResume" "vresume-web"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All databases initialized!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Next steps:"
echo "  1. Log in to admin panels"
echo "  2. Configure Wagtail sites"
echo "  3. Create home pages"
echo ""
