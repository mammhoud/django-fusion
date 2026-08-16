# CTC-Research Fixtures Organization

**Location**: `/precis-ctc/assets/fixtures/`  
**Purpose**: Manage fixture data for database initialization and testing  
**Status**: ✅ Organized and categorized

---

## 📁 Directory Structure

```
fixtures/
├── README.md                      # This file
├── dump-data.json                 # Main fixture dump (source)
├── original/                      # Archive/original fixtures
│   ├── wagtail_pages_dump.json
│   └── precis-ctc-data.json
├── cleaned/                       # Cleaned/filtered versions
│   ├── filtered-dump-data.json
│   └── essential-data.json
├── production/                    # Production-ready fixtures
│   ├── just-locales.json         # ✅ RECOMMENDED
│   └── cleaned-dump-data.json
├── test/                          # Test/staging fixtures
│   ├── locales.json
│   ├── pages.json
│   ├── users.json
│   ├── core-data.json
│   └── initial_choices.json
├── auth/                          # Authentication fixtures
├── sites/                         # Site configuration fixtures
└── [other]/                       # Legacy directories
```

---

## 📋 Fixture Categories

### 🟢 Production (Ready to Load)

**Location**: `production/`  
**Status**: ✅ Tested and safe to load

| Fixture | Size | Models | Objects | Notes |
|---------|------|--------|---------|-------|
| `just-locales.json` | 647B | `wagtailcore.locale` | 6 | **RECOMMENDED** - Load first |
| `cleaned-dump-data.json` | 251KB | Pages, locales, images | 594 | Valid content types only |

**Loading**:
```bash
# Recommended: Load just locales first
docker exec web-precis-ctc python manage.py loaddata production/just-locales.json

# Or use the management command
docker exec web-precis-ctc python manage.py load_initial_fixtures
```

### 🟡 Cleaned (Processed)

**Location**: `cleaned/`  
**Status**: ⚠️ Processed but may have FK issues

| Fixture | Size | Models | Objects | Notes |
|---------|------|--------|---------|-------|
| `filtered-dump-data.json` | 339KB | Wagtail-only models | 665 | Wagtail core data |
| `essential-data.json` | 31KB | Locales, images, users | 91 | Subset of data |

**Use When**: Testing data migration, developing load scripts

### 🟠 Test/Staging (For Development)

**Location**: `test/`  
**Status**: ⚠️ Test data with potential issues

| Fixture | Size | Models | Objects | Notes |
|---------|------|--------|---------|-------|
| `locales.json` | 848B | `wagtailcore.locale` | 7 | Test locales |
| `pages.json` | 90KB | `wagtailcore.page` | 73 | Test pages |
| `users.json` | 508B | `auth.user` | 6 | Test users |
| `core-data.json` | 818KB | Core models | 266 | Test core data |
| `initial_choices.json` | 7.2KB | Choices | 7 | Test choices |

**Use When**: Development, testing, staging environments

### 🔵 Original/Archive (Reference)

**Location**: `original/`  
**Status**: 📦 Archive/backup

| Fixture | Size | Models | Notes |
|---------|------|--------|-------|
| `wagtail_pages_dump.json` | 1.3MB | Page records | Original Wagtail dump |
| `precis-ctc-data.json` | 63KB | Mixed | Original CTC data |

**Use When**: Reference, recovery, historical analysis

### ⚪ Active (Root Level)

**Location**: `/fixtures/`  
**Status**: 📌 Current working file

| Fixture | Size | Models | Notes |
|---------|------|--------|-------|
| `dump-data.json` | 1.3MB | All | Main fixture source (1,015 objects) |

**Notes**: This is the original dump from database export

---

## 🔄 Recommended Fixture Loading Flow

### Step 1: Locales Only ✅
```bash
# Load 6 language records
docker exec web-precis-ctc python manage.py loaddata assets/fixtures/production/just-locales.json
```

**Why First**: Other fixtures may reference locales

### Step 2: Users (Optional)
```bash
# Load test/demo users
docker exec web-precis-ctc python manage.py loaddata assets/fixtures/test/users.json
```

**Why Optional**: Create admin user separately with `createsuperuser`

### Step 3: Pages (Optional)
```bash
# Load page structure
docker exec web-precis-ctc python manage.py loaddata assets/fixtures/test/pages.json
```

**Why Optional**: Create pages via `populate_content` command instead

---

## 🛠️ Management Commands

### List Fixtures
```bash
python manage.py load_initial_fixtures --list
```

### Load Recommended Sequence
```bash
# Load all fixtures in order
docker exec web-precis-ctc python manage.py load_initial_fixtures

# Dry run - show what would load
docker exec web-precis-ctc python manage.py load_initial_fixtures --dry-run
```

### Load Specific Step
```bash
# Load step 1 (locales)
docker exec web-precis-ctc python manage.py load_initial_fixtures --step 1

# Load step 2 (users)
docker exec web-precis-ctc python manage.py load_initial_fixtures --step 2
```

### Load Single Fixture
```bash
docker exec web-precis-ctc python manage.py load_initial_fixtures --fixture just-locales.json
```

---

## 🐍 Python Fixture Manager

Use the fixture manager script to inspect and manage fixtures:

```bash
# Show directory structure
python tests/scripts/manage_fixtures.py

# List all fixtures
python tests/scripts/manage_fixtures.py --list

# List fixtures by type
python tests/scripts/manage_fixtures.py --list --type production

# Verbose listing
python tests/scripts/manage_fixtures.py --list --verbose

# Get path for a fixture
python tests/scripts/manage_fixtures.py --path just-locales.json

# Show recommended loading order
python tests/scripts/manage_fixtures.py --recommended
```

---

## 📊 Fixture Data Summary

### Total Files: 12 JSON + 2 Directories

### By Type
- **Production Ready**: 2 fixtures (647B, 251KB)
- **Cleaned/Processed**: 2 fixtures (339KB, 31KB)
- **Test/Staging**: 5 fixtures (90KB, 818KB, 7.2KB, 848B, 508B)
- **Archive**: 2 fixtures (1.3MB, 63KB)
- **Active**: 1 fixture (1.3MB)

### Total Data Size
- **Production**: ~251KB (used)
- **Cleaned**: ~370KB (available)
- **Test**: ~935KB (available)
- **Archive**: ~1.4MB (reference)
- **Active**: ~1.3MB (source)
- **Total**: ~4.1MB

### Models Covered
- wagtailcore (pages, locales, sites)
- wagtailimages (images, renditions)
- auth (users, groups)
- taggit (tags)
- django_contrib_contenttypes (content types)
- Various app models

---

## ❌ Issues & Limitations

### Known Problems

1. **Fixture Model Incompatibility**
   - ❌ `dump-data.json` contains old app models (pages.homepage, etc.)
   - ✅ Solution: Use `just-locales.json` instead

2. **Foreign Key Violations**
   - ❌ Page fixtures reference non-existent content types
   - ✅ Solution: Use cleaned versions or populate_content command

3. **Large File Sizes**
   - ⚠️ Main dump is 1.3MB
   - ✅ Clean fixtures are much smaller (~250KB)

---

## ✅ Best Practices

### Do's ✅
- Use `just-locales.json` for initial load
- Use `populate_content` command for page content
- Keep original dumps as reference/archive
- Organize by purpose (production, test, etc.)
- Document fixture contents and dependencies

### Don'ts ❌
- Don't load `dump-data.json` directly (has FK issues)
- Don't mix old and new model formats
- Don't forget to load locales before pages
- Don't overwrite production fixtures without backup

---

## 🔍 Fixture Analysis

### dump-data.json (1.3MB, 1,015 objects)
**Source**: Original database export  
**Status**: Contains incompatible models  
**Content**:
- 73 wagtailcore.page records
- 6 wagtailcore.locale records
- 6 pages.homepage (OLD - doesn't exist)
- 6 pages.aboutpage (OLD - doesn't exist)
- 6 pages.contactpage (OLD - doesn't exist)
- 6 pages.teampage (OLD - doesn't exist)
- 5 lms.coursespage (OLD - doesn't exist)
- 289 page activity logs
- 211 model change logs
- 22 images and 54 renditions

**Why Not Use**: References old app structure with non-existent models

### just-locales.json (647B, 6 objects)
**Source**: Extracted from dump-data.json  
**Status**: ✅ Safe to load  
**Content**:
- en (English)
- ar (العربية)
- de (Deutsch)
- es (Español)
- fr (Français)
- pt-br (Português Brasileiro)

**Why Use**: Minimal, no dependencies, safe for production

---

## 📝 Creating New Fixtures

### Export All Data
```bash
docker exec web-precis-ctc python manage.py dumpdata > fixtures/backup.json
```

### Export Specific Models
```bash
docker exec web-precis-ctc python manage.py dumpdata wagtailcore.page > fixtures/pages.json
docker exec web-precis-ctc python manage.py dumpdata wagtail_localize.locale > fixtures/locales.json
```

### Export with Pretty Printing
```bash
docker exec web-precis-ctc python manage.py dumpdata --indent 2 > fixtures/backup.json
```

---

## 🔐 Security Notes

- ✅ Fixtures are data only - no executable code
- ✅ Always backup before loading
- ❌ Don't include passwords in fixtures (use dumpdata with exclude)
- ⚠️ Test in development before production

---

## 📚 References

- [Django Fixtures Documentation](https://docs.djangoproject.com/en/stable/howto/initial-data/)
- [Wagtail Data Migrations](https://docs.wagtail.org/en/stable/reference/pages/model_ref.html)
- [Fixture Management Script](./README.md)

---

## 📞 Support

**Questions**: See `/root/site/websites/precis-ctc/www/apps/management/commands/load_initial_fixtures.py`  
**Issues**: Check fixture model compatibility (see Fixture Analysis section)  
**Management**: Use `manage_fixtures.py` script in `tests/scripts/`

---

**Last Updated**: June 2, 2026  
**Maintainer**: Kiro Deployment System  
**Status**: ✅ Organized and Ready
