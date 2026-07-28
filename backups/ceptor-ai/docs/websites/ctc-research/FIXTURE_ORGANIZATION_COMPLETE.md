# Fixture Organization Complete

**Date**: June 2, 2026  
**Status**: ✅ FULLY ORGANIZED  
**Total Files**: 30+ (organized by model)  
**Total Items**: 1,513+  
**Total Size**: 1.1MB

---

## 🎉 What Was Done

### 1. ✅ Directory Structure Reorganized
```
fixtures/
├── original/              # Archive fixtures
├── cleaned/               # Filtered versions
├── production/            # Production-ready
├── test/                  # Test data
└── by-model/              # NEW: Organized by model
    ├── auth/
    ├── wagtailprojects/
    ├── wagtailimages/
    ├── modules/
    ├── handlers/
    ├── INDEX.json
    └── README.md
```

### 2. ✅ Helper Scripts Moved to Tests
```
tests/
├── __init__.py
├── README.md
├── fixtures/
│   ├── __init__.py
│   └── [test fixtures]
└── scripts/
    ├── __init__.py
    ├── manage_fixtures.py           # Fixture manager CLI
    ├── organize_fixtures_by_model.py # Organizer script
    ├── load_fixtures.py             # Moved from root
    ├── setup_initial_data.py        # Moved from root
    └── create_initial_homepage.sh   # Moved from root
```

### 3. ✅ Fixtures Separated by Model Type
- **1,513 items** separated across **5 categories**
- Created individual JSON files for each model
- Generated INDEX.json with metadata
- Organized hierarchically by app

### 4. ✅ New Management Command
Created `load_initial_fixtures.py` Django management command
- Load all fixtures in sequence
- Load specific steps
- Dry-run mode
- Validation

### 5. ✅ Comprehensive Documentation
- `tests/README.md` - Testing infrastructure guide
- `assets/fixtures/README.md` - Main fixtures guide
- `assets/fixtures/by-model/README.md` - Organized fixtures guide
- This file - Organization summary

---

## 📁 New Structure Details

### by-model/ Organization

#### auth/ (505 items, 90KB)
```
auth-group.json           (3 items)      - User groups
auth-permission.json      (499 items)    - Permissions
auth-user.json            (3 items)      - User accounts
```

#### wagtailprojects/ (900 items, 1MB)
```
wagtailcore-collection.json       (3 items)    - File collections
wagtailcore-groupapprovaltask.json (1 item)    - Approval tasks
wagtailcore-groupcollectionpermission.json     - Group permissions
wagtailcore-grouppagepermission.json           - Page permissions
wagtailcore-locale.json           (6 items)    - Languages
wagtailcore-modellogentry.json    (211 items)  - Model logs
wagtailcore-page.json             (43 items)   - Pages
wagtailcore-pagelogentry.json     (289 items)  - Page logs
wagtailcore-pagesubscription.json (10 items)   - Page subscriptions
wagtailcore-referenceindex.json   (132 items)  - References
wagtailcore-revision.json         (152 items)  - Revisions
wagtailcore-site.json             (1 item)     - Site config
wagtailcore-task.json             (1 item)     - Task
wagtailcore-workflow.json         (1 item)     - Workflow
wagtailcore-workflowpage.json     (1 item)     - Workflow page
wagtailcore-workflowtask.json     (1 item)     - Workflow task

# Old app models (archive):
lms-coursespage.json              (5 items)    - Old courses
pages-aboutpage.json              (6 items)    - Old about pages
pages-contactpage.json            (6 items)    - Old contact pages
pages-homepage.json               (6 items)    - Old home pages
pages-teampage.json               (6 items)    - Old team pages
```

#### wagtailimages/ (76 items, 25KB)
```
wagtailimages-image.json          (22 items)   - Images
wagtailimages-rendition.json      (54 items)   - Image variations
```

#### modules/ (31 items, 7KB)
```
modules-activitytype.json         (15 items)   - Activity types
modules-derivedstatus.json        (9 items)    - Derived status
modules-statuschoice.json         (7 items)    - Status choices
```

#### handlers/ (1 item, 1KB)
```
handlers-organization.json        (1 item)     - Organization
```

---

## 🔧 New Management Commands

### Fixture Manager CLI
```bash
# Show directory structure
python tests/scripts/manage_fixtures.py

# List all fixtures
python tests/scripts/manage_fixtures.py --list

# Show by-model organization
python tests/scripts/manage_fixtures.py --by-model

# Show fixtures for specific model
python tests/scripts/manage_fixtures.py --model wagtailcore

# Show recommended loading order
python tests/scripts/manage_fixtures.py --recommended

# Reorganize fixtures (run organizer)
python tests/scripts/manage_fixtures.py --organize
```

### Django Management Command
```bash
# Load all fixtures in sequence
docker exec web-ctc-research python manage.py load_initial_fixtures

# Load specific step
docker exec web-ctc-research python manage.py load_initial_fixtures --step 1

# Load single fixture
docker exec web-ctc-research python manage.py load_initial_fixtures --fixture wagtailcore-locale.json

# Dry run (preview)
docker exec web-ctc-research python manage.py load_initial_fixtures --dry-run

# List available fixtures
docker exec web-ctc-research python manage.py load_initial_fixtures --list
```

---

## 📊 Statistics

### Before Organization
- 12 fixture files at root/subdirectories
- Mixed models in single files
- Unclear relationships
- Hard to find specific data

### After Organization
- 30+ organized fixture files
- One model per file
- Clear hierarchy by app
- INDEX.json for metadata
- Easy discovery and loading

### Size Breakdown
| Category | Files | Items | Size | % |
|----------|-------|-------|------|---|
| wagtailcore | 21 | 900 | 1MB | 90% |
| auth | 3 | 505 | 90KB | 8% |
| wagtailimages | 2 | 76 | 25KB | 2% |
| modules | 3 | 31 | 7KB | 1% |
| handlers | 1 | 1 | 1KB | <1% |
| **TOTAL** | **30** | **1,513** | **1.1MB** | **100%** |

---

## 🎯 Loading Recommendations

### Quickest Setup
```bash
# Just locales (minimal)
docker exec web-ctc-research python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-locale.json
```

### Standard Setup
```bash
# Use the management command
docker exec web-ctc-research python manage.py load_initial_fixtures
```

### Complete Setup (All Data)
```bash
# All wagtailcore
docker exec web-ctc-research python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/*.json

# All auth
docker exec web-ctc-research python manage.py loaddata \
  assets/fixtures/by-model/auth/*.json

# All images
docker exec web-ctc-research python manage.py loaddata \
  assets/fixtures/by-model/wagtailimages/*.json
```

---

## 🔄 How to Reorganize (If Needed)

The `by-model/` directory is auto-generated. To regenerate after adding new fixtures:

```bash
# Method 1: Using fixture manager
python tests/scripts/manage_fixtures.py --organize

# Method 2: Direct script
python3 tests/scripts/organize_fixtures_by_model.py

# Clear first if needed
rm -rf assets/fixtures/by-model/
python3 tests/scripts/organize_fixtures_by_model.py
```

---

## 📚 Documentation Files

### For Users
- `assets/fixtures/README.md` - Main fixtures guide
- `assets/fixtures/by-model/README.md` - Organized fixtures guide
- `tests/README.md` - Testing infrastructure guide

### For Developers
- `tests/scripts/manage_fixtures.py` - Fixture manager source
- `tests/scripts/organize_fixtures_by_model.py` - Organizer source
- `www/apps/management/commands/load_initial_fixtures.py` - Django command

---

## ✅ Checklist

### Organization
- [x] Created by-model/ directory structure
- [x] Separated mixed fixtures by model
- [x] Generated INDEX.json
- [x] Created model README.md
- [x] Updated main fixtures README.md
- [x] Moved helper scripts to tests/

### Management
- [x] Created fixture manager CLI
- [x] Created Django management command
- [x] Added --organize flag
- [x] Added model-specific viewing
- [x] Added dry-run capability

### Documentation
- [x] by-model/README.md
- [x] tests/README.md
- [x] Updated assets/fixtures/README.md
- [x] This file (organization summary)

### Testing
- [x] Verified by-model structure
- [x] Tested load sequence
- [x] Verified INDEX.json
- [x] Tested management commands
- [x] Verified statistics

---

## 🚀 Next Steps

### Immediate
1. Use new organized fixtures for loading
2. Test loading by-model fixtures
3. Use INDEX.json for discovery

### Short-term
1. Delete old fixture files (after confirming by-model works)
2. Add new fixtures to by-model structure
3. Automate regeneration in CI/CD

### Long-term
1. Create migration scripts using by-model structure
2. Build fixture composition system
3. Implement fixture versioning

---

## 📝 Key Files Locations

```
/root/site/websites/ctc-research/

# Tests directory (organized)
tests/
├── __init__.py
├── README.md ......................... Testing infrastructure guide
├── fixtures/
│   ├── __init__.py
│   └── [test fixtures]
└── scripts/
    ├── __init__.py
    ├── manage_fixtures.py ............ Fixture manager CLI
    ├── organize_fixtures_by_model.py  Auto-organizer
    ├── load_fixtures.py (moved)
    ├── setup_initial_data.py (moved)
    └── create_initial_homepage.sh (moved)

# Fixtures directory (reorganized)
assets/fixtures/
├── README.md ......................... Main guide
├── by-model/ ......................... NEW: Organized by model
│   ├── README.md ..................... by-model guide
│   ├── INDEX.json .................... Auto-generated index
│   ├── auth/ ......................... Django auth models
│   ├── wagtailprojects/ .................. Wagtail core models
│   ├── wagtailimages/ ................ Image models
│   ├── modules/ ...................... Custom modules
│   └── handlers/ ..................... Custom handlers
├── original/ ......................... Archive
├── cleaned/ .......................... Filtered versions
├── production/ ....................... Production-ready
└── test/ ............................. Test data

# Management commands
www/apps/management/commands/
└── load_initial_fixtures.py .......... Django command

# Documentation
FIXTURE_ORGANIZATION_COMPLETE.md ...... This file
```

---

## 💡 Pro Tips

### Find Fixtures by Model
```bash
python tests/scripts/manage_fixtures.py --model wagtailcore
python tests/scripts/manage_fixtures.py --model auth
```

### Check What Would Load
```bash
docker exec web-ctc-research python manage.py load_initial_fixtures --dry-run
```

### Load Specific Model Only
```bash
docker exec web-ctc-research python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-locale.json
```

### See Organization Structure
```bash
python tests/scripts/manage_fixtures.py --by-model
```

---

## 🎓 Understanding the Organization

### Why by-model/?
- **Clarity**: Each file contains one model type
- **Reusability**: Load what you need
- **Scalability**: Easy to add new fixtures
- **Maintenance**: Update one model without affecting others
- **Dependencies**: Clear what needs to load first

### Model vs Fixture
- **Model**: The data type (e.g., `wagtailcore.page`)
- **Fixture**: The JSON file with data for that model
- **by-model/**: Directory organizing fixtures by their models

### INDEX.json
Metadata file that lists:
- All organized models
- File names
- Item counts
- File sizes
- Used for discovery and validation

---

## ✨ Benefits

✅ **Organized**: Clear directory structure by model type  
✅ **Discoverable**: Find what you need easily  
✅ **Manageable**: Update individual models independently  
✅ **Automated**: Auto-organizer for new fixtures  
✅ **Documented**: Comprehensive guides  
✅ **Tools**: CLI and Django commands  
✅ **Scalable**: Grows with your fixtures  
✅ **Reusable**: Load only what you need  

---

**Status**: ✅ COMPLETE AND READY TO USE  
**Last Updated**: June 2, 2026  
**Maintainer**: Kiro Deployment System  
**Next Review**: When new fixtures are added
