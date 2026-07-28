# Fixtures Organized by Model

**Location**: `/assets/fixtures/by-model/`  
**Purpose**: Fixture files separated and organized by model type  
**Status**: ✅ Automatically organized  
**Structure**: Hierarchical by app/model

---

## 📁 Directory Structure

```
by-model/
├── README.md                              # This file
├── INDEX.json                             # Auto-generated index
├── auth/                                  # Django auth models
│   ├── auth-group.json
│   ├── auth-permission.json
│   └── auth-user.json
├── handlers/                              # Custom handlers
│   └── handlers-organization.json
├── modules/                               # Custom modules
│   ├── modules-activitytype.json
│   ├── modules-derivedstatus.json
│   └── modules-statuschoice.json
├── wagtailprojects/                           # Wagtail core models
│   ├── wagtailcore-collection.json
│   ├── wagtailcore-locale.json
│   ├── wagtailcore-page.json
│   ├── wagtailcore-revision.json
│   ├── wagtailcore-site.json
│   ├── wagtailcore-workflow.json
│   ├── pages-homepage.json                # Old app models (archive)
│   ├── pages-aboutpage.json
│   ├── pages-contactpage.json
│   ├── pages-teampage.json
│   ├── lms-coursespage.json
│   └── [other models...]
└── wagtailimages/                         # Image models
    ├── wagtailimages-image.json
    └── wagtailimages-rendition.json
```

---

## 🎯 Model Categories

### 📌 auth/
**Purpose**: Django authentication models  
**Models**:
- `auth-group.json` - User groups (3 items)
- `auth-permission.json` - Permissions (499 items)
- `auth-user.json` - User accounts (3 items)

**Use Case**: Load user and permission data  
**Load Order**: Before other data that references users

```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/auth/auth-group.json \
  assets/fixtures/by-model/auth/auth-user.json
```

---

### 🌍 wagtailprojects/
**Purpose**: Core Wagtail CMS models  
**Models**:
- `wagtailcore-locale.json` - Languages/locales (6 items)
- `wagtailcore-page.json` - Page structure (43+ items)
- `wagtailcore-site.json` - Site configuration (1 item)
- `wagtailcore-collection.json` - File collections (3 items)
- `wagtailcore-revision.json` - Page revisions (152 items)
- `wagtailcore-modellogentry.json` - Model logs (211 items)
- `wagtailcore-pagelogentry.json` - Page logs (289 items)
- `wagtailcore-workflow.json` - Workflow (1 item)
- `wagtailcore-task.json` - Tasks (1 item)
- `wagtailcore-*.json` - Other models

**Use Case**: Load page structure and content  
**Load Order**: After auth, before images

```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-locale.json \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-site.json \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-page.json
```

---

### 🖼️ wagtailimages/
**Purpose**: Image and media models  
**Models**:
- `wagtailimages-image.json` - Image assets (22 items)
- `wagtailimages-rendition.json` - Image variations (54 items)

**Use Case**: Load media library  
**Load Order**: After wagtailcore collections

```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailimages/wagtailimages-image.json \
  assets/fixtures/by-model/wagtailimages/wagtailimages-rendition.json
```

---

### 📦 modules/
**Purpose**: Custom module choices and enums  
**Models**:
- `modules-activitytype.json` - Activity types (15 items)
- `modules-derivedstatus.json` - Status choices (9 items)
- `modules-statuschoice.json` - Status options (7 items)

**Use Case**: Load custom choices  
**Load Order**: Any time (independent)

```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/modules/modules-*.json
```

---

### 👤 handlers/
**Purpose**: Custom handler models  
**Models**:
- `handlers-organization.json` - Organizations (1 item)

**Use Case**: Load organization data  
**Load Order**: Any time

---

## 📊 Recommended Loading Sequence

### Step 1: Locales (Required)
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-locale.json
```

### Step 2: Sites (Required)
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-site.json
```

### Step 3: Collections (Optional)
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-collection.json
```

### Step 4: Auth (Optional)
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/auth/auth-group.json \
  assets/fixtures/by-model/auth/auth-user.json
```

### Step 5: Pages (Optional)
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-page.json
```

### Step 6: Images (Optional)
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailimages/wagtailimages-image.json \
  assets/fixtures/by-model/wagtailimages/wagtailimages-rendition.json
```

---

## 🔧 Using INDEX.json

The `INDEX.json` file contains metadata about all organized fixtures:

```bash
# View index
cat by-model/INDEX.json | grep -A 5 '"auth"'

# Parse with jq
jq '.models | keys' by-model/INDEX.json
jq '.models.wagtailcore | .[].file' by-model/INDEX.json
```

### Index Structure
```json
{
  "organized": true,
  "structure": "by-model",
  "description": "Fixtures separated by model type",
  "models": {
    "auth": [
      {
        "file": "auth-group.json",
        "items": 3,
        "size": 770
      }
    ]
  }
}
```

---

## 📈 Statistics

### Total Data Organized
- **Categories**: 5 (auth, wagtailcore, wagtailimages, modules, handlers)
- **Files**: 30+
- **Items**: 1,513+
- **Total Size**: 1.1MB

### By Category
| Category | Files | Items | Size |
|----------|-------|-------|------|
| auth | 3 | 505 | 90KB |
| wagtailcore | 21 | 900 | 1MB |
| wagtailimages | 2 | 76 | 25KB |
| modules | 3 | 31 | 7KB |
| handlers | 1 | 1 | 1KB |
| **TOTAL** | **30** | **1,513** | **1.1MB** |

---

## 🔄 Auto-Generation

The `by-model/` directory is automatically generated from mixed fixtures using:

```bash
python tests/scripts/organize_fixtures_by_model.py
```

### What It Does
1. Analyzes all fixture files
2. Identifies model types
3. Creates directories by app
4. Separates mixed files by model
5. Generates INDEX.json
6. Reports statistics

### Regenerating
```bash
# Remove old organized files
rm -rf assets/fixtures/by-model/

# Regenerate
python tests/scripts/organize_fixtures_by_model.py
```

---

## 🎯 Use Cases

### Case 1: Load Only Locales
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/wagtailcore-locale.json
```
✅ Safe for initial setup

### Case 2: Load All Auth Data
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/auth/*.json
```
✅ Loads users, groups, permissions

### Case 3: Load All Wagtail Core
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/wagtailprojects/*.json
```
⚠️ May have FK constraints - use in order

### Case 4: Load Everything
```bash
docker exec web-fusion-cms python manage.py loaddata \
  assets/fixtures/by-model/auth/*.json \
  assets/fixtures/by-model/wagtailprojects/*.json \
  assets/fixtures/by-model/wagtailimages/*.json \
  assets/fixtures/by-model/modules/*.json
```
⚠️ Requires correct order and FK handling

---

## ❌ Troubleshooting

### Issue: "Foreign key violation"
**Solution**: Load in recommended order above

### Issue: "ContentType does not exist"
**Solution**: Ensure you're loading from `by-model/` not old dumps

### Issue: "Duplicate key"
**Solution**: Clear database or use `--no-input` flag

### Issue: Files not found
**Solution**: Run organizer: `python tests/scripts/organize_fixtures_by_model.py`

---

## 📚 References

- [Main Fixtures README](../README.md)
- [Fixture Manager](../../tests/scripts/manage_fixtures.py)
- [Load Command](../../www/apps/management/commands/load_initial_fixtures.py)
- [Django Fixtures](https://docs.djangoproject.com/en/stable/howto/initial-data/)

---

## ✅ Best Practices

### Do's ✅
- Use fixtures from `by-model/` for specific needs
- Load in recommended order
- Use INDEX.json to find what you need
- Regenerate after adding new fixtures

### Don'ts ❌
- Don't manually edit organized files
- Don't skip dependencies (locales → site → pages)
- Don't load old app models (pages.*, lms.*)
- Don't ignore FK constraints

---

**Last Updated**: June 2, 2026  
**Auto-Generated**: Yes  
**Regenerate Command**: `python tests/scripts/organize_fixtures_by_model.py`  
**Status**: ✅ Ready for use
