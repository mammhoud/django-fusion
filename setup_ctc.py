#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
django.setup()

from django.contrib.auth import get_user_model
from wagtail.models import Page, Site

User = get_user_model()

# Check superusers
print("=== SUPERUSERS ===")
superusers = User.objects.filter(is_superuser=True)
print(f"Total: {superusers.count()}")
for u in superusers:
    print(f"  - {u.username} ({u.email})")

# Check pages
print("\n=== PAGES ===")
pages = Page.objects.all()
print(f"Total pages: {pages.count()}")
for p in pages[:10]:
    print(f"  - {p.id}: {p.title} (slug: {p.slug}, depth: {p.depth})")

# Check sites
print("\n=== WAGTAIL SITES ===")
sites = Site.objects.all()
print(f"Total sites: {sites.count()}")
for s in sites:
    print(f"  - {s.hostname} (root_page_id: {s.root_page_id})")

# Create superuser if not exists
if not superusers.exists():
    print("\n=== CREATING SUPERUSER ===")
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@ctc-research.com',
            password='mk_pAssWord123'
        )
        print(f"✅ Created: {user.username} ({user.email})")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("\n✅ Superuser already exists")
