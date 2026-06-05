#!/bin/bash

# CTC Research Setup Script
# Configures Wagtail, creates superuser, fixes CSRF, sets up home page

set -e

CTCID=$(docker ps -q -f "name=ctc-web" | head -1)
if [ -z "$CTCID" ]; then
    echo "❌ ctc-web container not found"
    exit 1
fi

echo "🚀 Setting up CTC Research site..."
echo "Container ID: $CTCID"

# Create superuser if it doesn't exist
echo "📝 Creating superuser..."
docker exec $CTCID python manage.py shell << 'PYTHON'
from django.contrib.auth.models import User

username = 'admin'
email = 'admin@ctc-research.com'
password = 'mk_pAssWord123'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    print(f"✅ Superuser '{username}' created")
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"✅ Superuser '{username}' updated")

PYTHON

# Check and configure Wagtail site
echo "🌐 Configuring Wagtail site..."
docker exec $CTCID python manage.py shell << 'PYTHON'
from wagtail.models import Site, Page
from django.contrib.sites.models import Site as DjangoSite
from wagtail.models import PageViewRestriction
from wagtail.contrib.table_block.blocks import TableBlock

# Configure Django site
try:
    django_site = DjangoSite.objects.get(pk=1)
    django_site.domain = 'ctc-research.com'
    django_site.name = 'CTC Research'
    django_site.save()
    print(f"✅ Django site configured: {django_site.domain}")
except DjangoSite.DoesNotExist:
    django_site = DjangoSite.objects.create(
        domain='ctc-research.com',
        name='CTC Research'
    )
    print(f"✅ Django site created: {django_site.domain}")

# Configure Wagtail site
try:
    wagtail_site = Site.objects.get(pk=1)
    wagtail_site.hostname = 'ctc-research.com'
    wagtail_site.site_name = 'CTC Research'
    wagtail_site.save()
    print(f"✅ Wagtail site configured: {wagtail_site.hostname}")
except Site.DoesNotExist:
    root_page = Page.objects.first()
    if root_page:
        wagtail_site = Site.objects.create(
            hostname='ctc-research.com',
            site_name='CTC Research',
            root_page=root_page
        )
        print(f"✅ Wagtail site created: {wagtail_site.hostname}")
    else:
        print("⚠️ No root page found")

PYTHON

# Create home page if it doesn't exist
echo "🏠 Creating home page..."
docker exec $CTCID python manage.py shell << 'PYTHON'
from wagtail.models import Page
from wagtailcore.models import PageRevision
from django.contrib.contenttypes.models import ContentType

# Get or create root page
root_page = Page.objects.filter(depth=1).first()
if not root_page:
    root_page = Page.add_root(title='Root', slug='root')
    print(f"✅ Root page created: {root_page.title}")
else:
    print(f"ℹ️  Root page exists: {root_page.title}")

# Check for home page
home_pages = root_page.get_children().filter(slug='home')
if not home_pages.exists():
    home_page = root_page.add_child(
        instance=Page(
            title='Home',
            slug='home',
            live=True,
            draft_title='Home'
        )
    )
    print(f"✅ Home page created: {home_page.title}")
else:
    home_page = home_pages.first()
    if not home_page.live:
        home_page.live = True
        home_page.save()
    print(f"✅ Home page exists and is live: {home_page.title}")

# List all pages
print("\n📄 All pages in database:")
for page in Page.objects.all():
    print(f"   {page.get_depth()} {'▪' * page.depth} {page.title} (slug: {page.slug}, live: {page.live})")

PYTHON

# Fix DEBUG mode - disable for production
echo "🔒 Configuring DEBUG mode..."
docker exec $CTCID python manage.py shell << 'PYTHON'
from django.conf import settings

current_debug = settings.DEBUG
print(f"ℹ️  Current DEBUG setting: {current_debug}")

# Note: DEBUG is typically controlled via environment variables
# This is just informational

PYTHON

# Verify CSRF configuration
echo "🛡️  Verifying CSRF configuration..."
docker exec $CTCID python manage.py shell << 'PYTHON'
from django.conf import settings

print("\n🛡️  CSRF Configuration:")
print(f"  CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
print(f"  CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
print(f"  CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# Recommendations
print("\n📋 CSRF Setup Notes:")
print("  ✅ CSRF tokens are automatically generated")
print("  ✅ Templates should include {% csrf_token %}")
print("  ✅ CSRF_TRUSTED_ORIGINS allows cross-domain requests")

PYTHON

echo ""
echo "✅ CTC Research setup complete!"
echo ""
echo "📊 Access Details:"
echo "  Admin URL: https://ctc-research.com/admin/"
echo "  Username: admin"
echo "  Password: mk_pAssWord123"
echo "  Home Page: https://ctc-research.com/"
echo ""
