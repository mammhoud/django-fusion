# CTC-Research Fixtures Data Summary

## Overview

The CTC-Research website uses fixture data from the `assets/fixtures/dump-data.json` file to populate initial content into the Wagtail CMS database.

## Fixture Files

### Main Fixture File
- **Path**: `/ctc-research/assets/fixtures/dump-data.json`
- **Total Objects**: 1,015
- **File Size**: 23,221 lines
- **Format**: JSON (Django fixture format)

### Generated Fixture Files (Separated by Model)

1. **core-data.json** - Essential core data
   - Objects: 266
   - Models: wagtailcore.page, wagtailcore.locale, wagtailcore.site, auth.user, auth.group, wagtailimages.image, wagtailcore.collection, wagtailcore.revision

2. **locales.json** - Localization data
   - Objects: 7 (Locale records)
   - Includes: en, ar, de, fr, es, pt-br, fr-ca

3. **pages.json** - Page structure data
   - Objects: 73 (Wagtail Page records)
   - Organizes pages in multilingual hierarchy

## Data Content Breakdown

### Models in dump-data.json

| Model | Count | Purpose |
|-------|-------|---------|
| wagtailcore.page | 73 | Page hierarchy structure |
| wagtailcore.locale | 6 | Available languages |
| wagtailcore.revision | 152 | Page revision history |
| wagtailcore.modellogentry | 211 | Model change logs |
| wagtailcore.pagelogentry | 289 | Page activity logs |
| wagtailcore.site | 1 | Site configuration |
| wagtailcore.pageviewrestriction | - | Page access control |
| auth.user | 6 | User accounts |
| auth.group | 3 | Permission groups |
| wagtailimages.image | 22 | Image assets |
| wagtailimages.rendition | 54 | Image variations |
| pages.homepage | 6 | Home page (multilingual) |
| pages.aboutpage | 6 | About page (multilingual) |
| pages.contactpage | 6 | Contact page (multilingual) |
| pages.teampage | 6 | Team page (multilingual) |
| lms.coursespage | 5 | Courses page |

### Page Hierarchy Structure

```
Root (id=1, depth=1)
├─ Home Page (id=3, depth=2, EN)
│  ├─ About CTC Research (id=4, depth=3, EN)
│  ├─ Contact Us (id=5, depth=3, EN)
│  ├─ Our Team (id=6, depth=3, EN)
│  └─ AI Courses (id=7, depth=3, EN)
├─ Home Page AR (id=8, depth=2, AR)
│  ├─ About (id=9, depth=3, AR)
│  ├─ Contact (id=10, depth=3, AR)
│  └─ Team (id=11, depth=3, AR)
├─ Home Page DE (id=13, depth=2, DE)
│  └─ [Similar sub-pages]
├─ Home Page ES (id=18, depth=2, ES)
│  └─ [Similar sub-pages]
└─ Home Page FR (id=23, depth=2, FR)
   └─ [Similar sub-pages]
```

## Language Support

### Supported Languages
- **en** - English (default)
- **ar** - Arabic
- **de** - Deutsch (German)
- **es** - Español (Spanish)
- **fr** - Français (French)
- **pt-br** - Português Brasileiro (Brazilian Portuguese)

### Homepage Configuration

**Default Language**: English (en)
- **Title**: "Home Page"
- **Slug**: "home-page"
- **URL Path**: "/home-page/"
- **Published**: Yes (live=true)
- **SEO Title**: "CTC Research | AI-Powered Medical Writing & Research"

## Loading Instructions

### Prerequisites
```bash
# Ensure database is migrated
python manage.py migrate

# Create Wagtail site structure
python manage.py setup_wagtail_home
```

### Load Core Data
```bash
# Load locales and site configuration
python manage.py loaddata assets/fixtures/locales.json

# Load page structure
python manage.py loaddata assets/fixtures/pages.json

# Or load everything at once (after fixing model references)
python manage.py loaddata assets/fixtures/dump-data.json
```

### Python-based Loading (Recommended)
```python
import json
from pathlib import Path
from wagtail_localize.models import Locale
from wagtailcore.models import Page

fixture_file = Path("ctc-research/assets/fixtures/dump-data.json")
with open(fixture_file) as f:
    data = json.load(f)

# Create locales
locales_data = [item for item in data if item.get("model") == "wagtailcore.locale"]
for item in locales_data:
    code = item["fields"]["language_code"]
    Locale.objects.get_or_create(language_code=code)
```

## Data Verification

### Check Loaded Data
```bash
# List all pages
python manage.py shell <<< "from wagtailcore.models import Page; [print(f'{p.depth}: {p.title}') for p in Page.objects.all()]"

# Verify locales
python manage.py shell <<< "from wagtail_localize.models import Locale; [print(l.language_code) for l in Locale.objects.all()]"

# Check homepage
python manage.py shell <<< "from www.core.content.models.pages.home import HomePage; print(HomePage.objects.first())"
```

### HTTP Verification
```bash
# Test homepage (English, default)
curl -H "Accept-Language: en" https://ctc-research.com/

# Test English translation
curl https://ctc-research.com/en/

# Test Arabic translation
curl https://ctc-research.com/ar/

# Test German translation
curl https://ctc-research.com/de/

# Test Spanish translation
curl https://ctc-research.com/es/

# Test French translation
curl https://ctc-research.com/fr/
```

## Admin Panel Access

### Homepage Configuration in Admin
1. Navigate to: `/admin/`
2. Go to **Pages** section
3. Select **"Home Page"** (English)
4. Verify:
   - ✓ Title: "Home Page"
   - ✓ Slug: "home-page"
   - ✓ Language: English (en)
   - ✓ Status: Published (Live)
   - ✓ SEO Title set
   - ✓ Search description configured

### Set as Root Page
In the **Pages** admin:
1. Right-click on "Home Page"
2. Select "Set as homepage"
3. Or use the page properties to set as root

## Content Separation

### Current Models in Fixture
The fixture contains references to these page models (from old app structure):
- `pages.homepage` → Maps to current HomePage
- `pages.aboutpage` → Maps to current AboutPage  
- `pages.contactpage` → Maps to current ContactPage
- `pages.teampage` → Maps to current TeamPage
- `lms.coursespage` → Maps to current CoursesPage

### To Properly Load All Data
Create separate fixture files by model:

```bash
# Extract by model
python3 << 'EOF'
import json
from pathlib import Path
from collections import defaultdict

dump_file = Path("ctc-research/assets/fixtures/dump-data.json")
with open(dump_file) as f:
    data = json.load(f)

# Group by model
by_model = defaultdict(list)
for item in data:
    model = item.get("model")
    by_model[model].append(item)

# Create individual fixture files
for model, items in by_model.items():
    filename = model.replace(".", "-") + ".json"
    filepath = Path(f"ctc-research/assets/fixtures/{filename}")
    with open(filepath, "w") as f:
        json.dump(items, f, indent=2)
    print(f"Created {filename}: {len(items)} objects")
EOF
```

## Status

### ✅ Working
- [x] Website accessible at ctc-research.com
- [x] HTTPS certificates active (Let's Encrypt)
- [x] Homepage loads in English (default)
- [x] Traefik routing configured
- [x] Static assets served from media server
- [x] Multiple language support configured

### 🚀 Next Steps
- [ ] Load all fixture data into database
- [ ] Verify all page translations display correctly
- [ ] Configure admin panel root page
- [ ] Test all language variations
- [ ] Set up email functionality
- [ ] Configure user permissions
- [ ] Deploy to production

## References
- Wagtail Localization: https://wagtail-localize.org/
- Django Fixtures: https://docs.djangoproject.com/en/stable/howto/initial-data/
- Wagtail Page Trees: https://docs.wagtail.org/en/stable/reference/pages/model_ref.html
