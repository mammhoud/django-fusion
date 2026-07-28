#!/bin/bash
# Create initial homepage structure for all locales

echo "🏠 Creating initial homepage structure for CTC-Research..."

docker exec web-ctc-research python manage.py shell << 'PYEOF'
import sys
from django.db import transaction
from wagtailcore.models import Page
from wagtail_localize.models import Locale
from www.core.content.models.pages.home import HomePage

print("\n📋 Creating HomePage for all locales...\n")

# Get locales
locales = list(Locale.objects.all())
print(f"Available locales: {', '.join([l.language_code for l in locales])}\n")

# Get root page
root = Page.objects.get(depth=1)
print(f"Root page: {root.title} (id={root.id})\n")

with transaction.atomic():
    # Remove the default welcome page if it exists
    welcome = Page.objects.filter(depth=2, title__icontains="welcome").first()
    if welcome:
        print(f"Removing old welcome page: {welcome.title}")
        welcome.delete()
    
    # Create English homepage first
    en_locale = Locale.objects.get(language_code='en')
    
    # Check if homepage already exists
    en_home = HomePage.objects.filter(locale=en_locale).first()
    
    if en_home:
        print(f"✓ English homepage already exists: {en_home.title}")
    else:
        print("Creating English homepage...")
        en_home = HomePage(
            title="Home Page",
            slug="home",
            locale=en_locale,
        )
        root.add_child(instance=en_home)
        en_home.save_revision().publish()
        print(f"✓ Created: {en_home.title} (id={en_home.id})")
    
    # Create translations for other locales
    for locale in locales:
        if locale.language_code == 'en':
            continue
        
        translation = HomePage.objects.filter(locale=locale).first()
        if translation:
            print(f"✓ {locale.language_code} translation exists: {translation.title}")
        else:
            print(f"Creating {locale.language_code} translation...")
            translation = en_home.copy_for_translation(locale)
            translation.title = f"Home Page ({locale.language_code.upper()})"
            translation.save_revision().publish()
            print(f"✓ Created: {translation.title}")

print("\n📊 Final structure:")
root = Page.objects.get(depth=1)
for page in Page.objects.all():
    indent = "  " * (page.depth - 1)
    print(f"{indent}└─ {page.title} (id={page.id}, locale={page.locale})")

print("\n✅ Homepage structure created successfully!")
PYEOF
