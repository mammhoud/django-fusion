#!/usr/bin/env python
"""
Fix Homepage Content Type
This script updates the homepage to use the correct HomePage model
"""
import os
import sys

import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, Site


def fix_homepage():
    """Fix the homepage content type"""

    # Get the default site
    site = Site.objects.get(is_default_site=True)
    current_root = site.root_page

    print(f"Current root page: {current_root.title} (ID: {current_root.id})")
    print(f"Current content type: {current_root.content_type}")

    # Get the HomePage content type
    try:
        from www.core.content.models.pages.home import HomePage
        homepage_ct = ContentType.objects.get_for_model(HomePage)
        print(f"Target content type: {homepage_ct}")
    except Exception as e:
        print(f"Error getting HomePage model: {e}")
        return False

    # Check if there's already a HomePage
    homepages = Page.objects.filter(content_type=homepage_ct, depth=2)

    if homepages.exists():
        print(f"\nFound {homepages.count()} existing HomePage(s):")
        for hp in homepages:
            print(f"  - {hp.title} (ID: {hp.id}, URL: {hp.url_path})")

        # Use the first one
        new_root = homepages.first()
        print(f"\nSetting {new_root.title} (ID: {new_root.id}) as site root...")

        site.root_page = new_root
        site.save()

        print(f"✓ Site root updated successfully!")
        print(f"  New root: {new_root.title}")
        print(f"  Content type: {new_root.content_type}")
        return True
    else:
        print("\n⚠ No HomePage instances found in database")
        print("You need to create a HomePage through the Wagtail admin")
        return False

if __name__ == '__main__':
    fix_homepage()
