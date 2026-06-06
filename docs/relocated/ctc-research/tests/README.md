# CTC-Research Tests & Helper Scripts

**Location**: `/ctc-research/tests/`  
**Purpose**: Testing utilities, fixture management, and setup scripts  
**Status**: ✅ Organized

---

## 📁 Directory Structure

```
tests/
├── README.md                      # This file
├── __init__.py                    # Python package marker
├── fixtures/                      # Test fixtures
│   ├── __init__.py
│   ├── [fixture files]
│   └── [organized by type]
└── scripts/                       # Helper & management scripts
    ├── __init__.py
    ├── manage_fixtures.py         # Fixture manager CLI
    ├── load_fixtures.py           # Fixture loading utility
    ├── setup_initial_data.py      # Initial setup script
    └── create_initial_homepage.sh # Homepage creation script
```

---

## 🔧 Helper Scripts

### 1. manage_fixtures.py
**Purpose**: CLI tool for managing and inspecting fixtures  
**Type**: Python script  

**Usage**:
```bash
# Show directory structure
python tests/scripts/manage_fixtures.py

# List all fixtures
python tests/scripts/manage_fixtures.py --list

# List by type
python tests/scripts/manage_fixtures.py --list --type production

# Verbose listing with paths
python tests/scripts/manage_fixtures.py --list --verbose

# Get fixture path
python tests/scripts/manage_fixtures.py --path just-locales.json

# Show recommended loading order
python tests/scripts/manage_fixtures.py --recommended
```

**Features**:
- ✅ Lists all fixtures with descriptions
- ✅ Shows directory organization
- ✅ Provides recommended loading order
- ✅ Supports filtering by type
- ✅ Verbose output with paths and sizes

---

### 2. load_fixtures.py
**Purpose**: Loads fixture data with dependency management  
**Type**: Python script (Django standalone)  

**Usage**:
```bash
# From container
docker exec web-ctc-research python tests/scripts/load_fixtures.py

# Or in shell
cd ctc-research && python tests/scripts/load_fixtures.py
```

**Features**:
- ✅ Loads fixtures in proper order
- ✅ Handles FK constraints
- ✅ Transaction atomic operations
- ✅ Verification after loading

---

### 3. setup_initial_data.py
**Purpose**: Sets up initial Wagtail site structure  
**Type**: Python script (Django standalone)  

**Usage**:
```bash
# From container
docker exec web-ctc-research python tests/scripts/setup_initial_data.py

# Or locally
cd ctc-research && python tests/scripts/setup_initial_data.py
```

**Features**:
- ✅ Creates root page structure
- ✅ Initializes locales
- ✅ Loads fixture data
- ✅ Verifies setup completion

---

### 4. create_initial_homepage.sh
**Purpose**: Creates multilingual homepage structure  
**Type**: Bash script  

**Usage**:
```bash
# From container
docker exec web-ctc-research bash tests/scripts/create_initial_homepage.sh

# Or locally
bash tests/scripts/create_initial_homepage.sh
```

**Features**:
- ✅ Creates HomePage instances
- ✅ Sets up translations
- ✅ Publishes pages
- ✅ Lists final structure

---

## 🎯 Common Tasks

### Task 1: Inspect Fixtures
```bash
# See what fixtures are available
python tests/scripts/manage_fixtures.py --list --verbose

# Show directory organization
python tests/scripts/manage_fixtures.py --structure
```

### Task 2: Load Production Fixtures
```bash
# Load recommended fixtures in order
docker exec web-ctc-research python manage.py load_initial_fixtures

# Or specific step
docker exec web-ctc-research python manage.py load_initial_fixtures --step 1
```

### Task 3: Create Admin User
```bash
docker exec web-ctc-research python manage.py createsuperuser
```

### Task 4: Initialize Site
```bash
docker exec web-ctc-research python tests/scripts/setup_initial_data.py
```

### Task 5: Create Homepage
```bash
docker exec web-ctc-research bash tests/scripts/create_initial_homepage.sh
```

---

## 🧪 Testing Fixtures

### Manual Load Test
```bash
# Test loading just locales
docker exec web-ctc-research python manage.py loaddata assets/fixtures/production/just-locales.json

# Verify
docker exec web-ctc-research python manage.py shell <<EOF
from wagtail_localize.models import Locale
print(f"Locales loaded: {Locale.objects.count()}")
for l in Locale.objects.all():
    print(f"  {l.language_code}")
EOF
```

### Dry Run
```bash
# See what would be loaded without loading
docker exec web-ctc-research python manage.py load_initial_fixtures --dry-run
```

### Check Fixture Validity
```bash
# Validate fixture format
docker exec web-ctc-research python manage.py loaddata assets/fixtures/production/just-locales.json --verbosity 2
```

---

## 📊 Fixture Organization

### By Category
- **production/**: Ready for load (647B, 251KB)
- **cleaned/**: Filtered versions (339KB, 31KB)
- **test/**: Test data (935KB)
- **original/**: Archive (1.4MB)

### By Model Type
- **locales**: Language/locale records
- **pages**: Page structure
- **users**: User accounts
- **images**: Media assets
- **choices**: Choice fields
- **core**: Mixed core data

### By Status
- ✅ **Production Ready**: just-locales.json
- ⚠️ **Tested**: cleaned-dump-data.json
- 🧪 **Test**: test/*.json
- 📦 **Archive**: original/*.json

---

## 🚀 Quick Start

### 1. Initialize Site (One Time)
```bash
docker exec web-ctc-research python manage.py setup_wagtail_home
docker exec web-ctc-research python manage.py load_initial_fixtures
```

### 2. Verify Setup
```bash
docker exec web-ctc-research python manage.py shell <<EOF
from wagtailcore.models import Page
from wagtail_localize.models import Locale

print(f"Pages: {Page.objects.count()}")
print(f"Locales: {Locale.objects.count()}")
EOF
```

### 3. Create Admin User
```bash
docker exec web-ctc-research python manage.py createsuperuser
```

### 4. Add Content
```bash
docker exec web-ctc-research python manage.py populate_content \
  --content-file /app/ctc-research/docs/content.md
```

---

## 📋 Script Dependencies

### manage_fixtures.py
- Python 3.8+
- pathlib (std lib)
- enum (std lib)
- argparse (std lib)

### load_fixtures.py
- Django
- Python 3.8+
- settings.py configured

### setup_initial_data.py
- Django
- Wagtail
- wagtail_localize
- Python 3.8+

### create_initial_homepage.sh
- bash
- Python
- Docker (if running in container)
- Django manage.py

---

## 🔧 Extending Scripts

### Add New Fixture Type
Edit `manage_fixtures.py`:
```python
FIXTURE_PATHS = {
    FixtureType.CUSTOM: FIXTURES_ROOT / "custom",
    # ... existing types
}
```

### Add New Loading Step
Edit `load_initial_fixtures.py`:
```python
FIXTURE_SEQUENCE = [
    # ... existing steps
    {
        "name": "custom",
        "description": "Load custom data",
        "paths": ["assets/fixtures/custom/*.json"],
        "required": False,
    },
]
```

---

## 🐛 Troubleshooting

### Issue: "Fixture not found"
**Solution**: Use `manage_fixtures.py --list` to find correct path

### Issue: "Foreign key violation"
**Solution**: Load fixtures in correct order (see manage_fixtures.py --recommended)

### Issue: "Module not found"
**Solution**: Ensure you're in ctc-research directory and Django is configured

### Issue: "Permission denied"
**Solution**: Check file permissions or run with docker exec

---

## 📚 References

- [Fixtures README](../assets/fixtures/README.md)
- [Management Commands](../www/apps/management/commands/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Wagtail Documentation](https://docs.wagtail.org/)

---

## ✅ Checklist

### Initial Setup
- [ ] Run `setup_wagtail_home` command
- [ ] Load locales with `load_initial_fixtures --step 1`
- [ ] Create admin user
- [ ] Verify database loaded

### Content Creation
- [ ] Prepare content markdown
- [ ] Run `populate_content` command
- [ ] Test language routes
- [ ] Upload images/media

### Deployment
- [ ] Run all tests
- [ ] Verify fixtures load cleanly
- [ ] Create backup
- [ ] Document process

---

## 📞 Support

**Questions about fixtures?**
→ See `assets/fixtures/README.md`

**Questions about scripts?**
→ Check script docstrings or run with `--help`

**Issues with loading?**
→ Run with `--dry-run` first to diagnose

**Need to add new features?**
→ See "Extending Scripts" section

---

**Last Updated**: June 2, 2026  
**Status**: ✅ Organized and Ready  
**Maintainer**: Kiro Deployment System
