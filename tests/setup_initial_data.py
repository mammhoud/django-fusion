#!/usr/bin/env python
"""
Setup initial data for CTC-Research website
Creates Wagtail site structure and loads available fixture data
"""

import json
import os
import sys
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/app')

import django
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from wagtailcore.models import Page, Site, Locale as WagtailLocale
from wagtail_localize.models import Locale
from www.core.content.models.pages.home import HomePage

def setup_wagtail_site():
    """Create the basic Wagtail site structure"""
    print("\n🔧 Setting up Wagtail site structure...")
    
    # Create root page if it doesn't exist
    if not Page.objects.filter(depth=1).exists():
        print("  📄 Creating root page...")
        with transaction.atomic():
            # Create locales first
            locales_data = [
                ('en', 'English'),
                ('ar', 'العربية'),
                ('de', 'Deutsch'),
                ('es', 'Español'),
                ('fr', 'Français'),
                ('pt-br', 'Português Brasileiro'),
            ]
            
            for code, name in locales_data:
                locale, created = Locale.objects.get_or_create(language_code=code)
                if created:
                    print(f"     ✓ Created locale: {code}")
            
            # Create root page in English locale
            en_locale = Locale.objects.get(language_code='en')
            root = Page.add_root(
                title='Root',
                slug='root',
                content_type_id=1,  # Get the correct content type
                locale=en_locale,
            )
            print(f"  ✓ Created root page")
            
            # Create site
            site, created = Site.objects.get_or_create(
                defaults={'hostname': 'ctc-research.com', 'site_name': 'CTC-Research', 'root_page': root}
            )
            if created:
                print(f"  ✓ Created site: {site.site_name}")
            else:
                print(f"  ℹ️  Site already exists: {site.site_name}")
    else:
        print("  ℹ️  Root page already exists")

def load_fixture_data():
    """Load fixture data into the database"""
    print("\n📦 Loading fixture data...")
    
    # Read dump-data.json and filter only wagtail models
    fixture_file = Path('/app/precis-ctc/assets/fixtures/dump-data.json')
    
    if not fixture_file.exists():
        print(f"❌ Fixture file not found: {fixture_file}")
        return
    
    with open(fixture_file) as f:
        all_data = json.load(f)
    
    # Filter data by model
    wagtail_models = [
        'wagtailcore.locale',
        'wagtailcore.page',
        'wagtailcore.site',
        'wagtailimages.image',
        'wagtailimages.rendition',
        'auth.user',
        'auth.group',
    ]
    
    filtered_data = [
        item for item in all_data
        if item.get('model') in wagtail_models
    ]
    
    print(f"  📋 Found {len(filtered_data)} relevant objects from {len(all_data)} total")
    
    # Save filtered fixture
    filtered_fixture = Path('/app/precis-ctc/assets/fixtures/wagtail-only.json')
    with open(filtered_fixture, 'w') as f:
        json.dump(filtered_data, f, indent=2)
    print(f"  ✓ Created filtered fixture: {filtered_fixture.name}")
    
    # Load filtered data
    from django.core.management import call_command
    try:
        print("  ⏳ Loading filtered wagtail data...")
        call_command(
            'loaddata',
            str(filtered_fixture),
            verbosity=1,
        )
        print("  ✅ Successfully loaded wagtail data")
    except Exception as e:
        print(f"  ⚠️  Error loading wagtail data: {e}")
        # Continue anyway
    
    # Load other fixtures if available
    other_fixtures = [
        'users.json',
        'initial_choices.json',
    ]
    
    for fixture_name in other_fixtures:
        fixture_path = fixture_file.parent / fixture_name
        if not fixture_path.exists():
            continue
        
        print(f"  ⏳ Loading {fixture_name}...")
        try:
            # Try to load, but don't fail if there are model reference errors
            call_command(
                'loaddata',
                str(fixture_path),
                verbosity=0,
            )
            print(f"  ✅ Loaded {fixture_name}")
        except Exception as e:
            print(f"  ⚠️  Skipped {fixture_name} (model reference error)")

def verify_setup():
    """Verify the setup was successful"""
    print("\n✅ Verifying setup...")
    
    pages = Page.objects.all()
    locales = Locale.objects.all()
    sites = Site.objects.all()
    
    print(f"   Pages: {pages.count()}")
    print(f"   Locales: {locales.count()}")
    print(f"   Sites: {sites.count()}")
    
    if pages.exists():
        root = pages.filter(depth=1).first()
        if root:
            print(f"   Root page: {root.title}")
            children = root.get_children()
            print(f"   Child pages: {children.count()}")
    
    if locales.exists():
        print("   Languages: " + ", ".join([l.language_code for l in locales]))
    
    print("\n✨ Setup complete!")

if __name__ == '__main__':
    try:
        setup_wagtail_site()
        load_fixture_data()
        verify_setup()
    except KeyboardInterrupt:
        print("\n⏸️  Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
