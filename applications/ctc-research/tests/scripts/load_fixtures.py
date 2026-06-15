#!/usr/bin/env python
"""
Script to load fixture data into CTC-Research database
Handles model references and dependencies correctly
"""

import json
import os
import sys
from pathlib import Path

# Add the project to the path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.db import transaction
from django.core.management import call_command

def load_fixtures():
    """Load fixtures in the correct order"""
    
    print("🚀 Starting fixture data loading process...")
    
    fixture_dir = Path(__file__).parent / "assets" / "fixtures"
    
    # Files to load in order
    fixtures = [
        "initial_choices.json",
        "users.json",
        "core-data.json",
        "locales.json",
        "pages.json",
    ]
    
    for fixture_file in fixtures:
        fixture_path = fixture_dir / fixture_file
        if not fixture_path.exists():
            print(f"⚠️  Skipping {fixture_file} - file not found")
            continue
            
        print(f"\n📦 Loading {fixture_file}...")
        try:
            with transaction.atomic():
                call_command(
                    'loaddata',
                    str(fixture_path),
                    verbosity=2,
                )
            print(f"✅ Successfully loaded {fixture_file}")
        except Exception as e:
            print(f"❌ Error loading {fixture_file}: {e}")
            # Continue to try other fixtures
    
    print("\n✨ Fixture loading complete!")
    
    # Verify the data was loaded
    print("\n📊 Verification:")
    
    from wagtailcore.models import Page, Locale
    from wagtail_localize.models import Locale as LocalizeLocale
    
    page_count = Page.objects.count()
    locale_count = Locale.objects.count()
    
    print(f"   - Total pages: {page_count}")
    print(f"   - Total locales: {locale_count}")
    
    if page_count > 1:  # Should have at least Root page
        root = Page.objects.get(depth=1)
        print(f"   - Root page: {root.title}")
        
        # Get home pages
        homes = Page.objects.filter(depth=2)
        print(f"   - Home pages: {homes.count()}")
        for home in homes:
            print(f"      • {home.title} ({home.locale})")
    
    print("\n✅ Data verification complete!")

if __name__ == "__main__":
    load_fixtures()
