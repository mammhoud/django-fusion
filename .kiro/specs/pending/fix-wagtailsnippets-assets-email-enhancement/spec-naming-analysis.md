# Spec Naming Analysis Report

**Generated**: 2026-04-06
**Task**: 6.1 - Analyze current spec naming conventions

## Executive Summary

Analyzed 13 specs across 6 categories in `.kiro/specs-organized/`. Found significant naming inconsistencies that impact discoverability and organization.

## 1. Current Spec Inventory

### Category: auth (3 specs)
- `auth-allauth-enhancement` - feature
- `ctc-research-server-and-auth-fix` - feature
- `ctc-structa-admin-auth-integration` - feature

### Category: docs (3 specs)
- `comprehensive-project-documentation` - feature
- `ctc-docs-and-core-containers` - feature
- `docs-plugin-enhancement` - feature

### Category: features (1 spec)
- `spec-task-orchestrator` - feature

### Category: fixes (3 specs)
- `alliance-website-docker-fix` - bugfix
- `fix-get-translation-template-tag` - bugfix
- `fix-wagtailsnippets-assets-email-enhancement` - bugfix

### Category: integration (1 spec)
- `blog-lms-wagtail-integration` - feature

### Category: modernization (2 specs)
- `project-modernization` - feature
- `structa-color-update` - bugfix

**Total**: 13 specs (10 features, 3 bugfixes)

## 2. Naming Inconsistencies Identified

### Issue 1: Inconsistent Prefix Usage
**Problem**: Only some bugfix specs use the `fix-` prefix
- ✅ Has prefix: `fix-get-translation-template-tag`, `fix-wagtailsnippets-assets-email-enhancement`
- ❌ Missing prefix: `alliance-website-docker-fix`, `structa-color-update`

**Impact**: Difficult to identify bugfixes at a glance

### Issue 2: Category vs. Spec Type Mismatch
**Problem**: Specs are categorized by topic, not by type
- `fixes/` category contains bugfixes (correct)
- `modernization/structa-color-update` is a bugfix but not in `fixes/`
- `auth/` contains features, not a spec type category

**Impact**: Confusing organization - mixing topical and type-based categorization

### Issue 3: Verbose and Inconsistent Naming
**Problem**: Spec names vary widely in length and format
- Short: `spec-task-orchestrator` (23 chars)
- Medium: `auth-allauth-enhancement` (23 chars)
- Long: `fix-wagtailsnippets-assets-email-enhancement` (45 chars)
- Very long: `ctc-research-server-and-auth-fix` (32 chars)

**Impact**: Harder to scan and reference

### Issue 4: Project-Specific Prefixes
**Problem**: Some specs include project prefixes (ctc-, structa-), others don't
- With prefix: `ctc-research-server-and-auth-fix`, `ctc-docs-and-core-containers`, `ctc-structa-admin-auth-integration`, `structa-color-update`
- Without prefix: `auth-allauth-enhancement`, `docs-plugin-enhancement`

**Impact**: Inconsistent naming convention

### Issue 5: Ambiguous Categorization
**Problem**: Some categories overlap or are unclear
- `auth/` - topical category
- `docs/` - topical category
- `features/` - type-based category
- `fixes/` - type-based category
- `integration/` - topical category
- `modernization/` - topical category

**Impact**: No clear organizational principle

## 3. Recommended Naming Convention

### Principle: Consistent, Scannable, Hierarchical

### Format
```
{category}/{type}-{scope}-{description}
```

### Components

**Category** (topical grouping):
- `auth` - Authentication & authorization
- `docs` - Documentation
- `infra` - Infrastructure & deployment
- `integration` - System integrations
- `ui` - User interface
- `api` - API development
- `data` - Data models & migrations
- `core` - Core functionality

**Type** (spec type prefix):
- `feat-` - New features
- `fix-` - Bug fixes
- `refactor-` - Code refactoring
- `enhance-` - Enhancements to existing features
- `migrate-` - Migrations or modernization

**Scope** (component/area):
- Short identifier (1-2 words)
- Examples: `allauth`, `docker`, `wagtail`, `email`

**Description** (what it does):
- Brief, hyphenated description
- Max 3-4 words
- Examples: `snippet-namespace`, `asset-urls`, `csv-invitations`

### Examples of Renamed Specs

#### Current → Proposed

**auth category:**
- `auth-allauth-enhancement` → `auth/enhance-allauth-integration`
- `ctc-research-server-and-auth-fix` → `auth/fix-server-configuration`
- `ctc-structa-admin-auth-integration` → `auth/feat-admin-integration`

**docs category:**
- `comprehensive-project-documentation` → `docs/feat-comprehensive-docs`
- `ctc-docs-and-core-containers` → `docs/feat-container-docs`
- `docs-plugin-enhancement` → `docs/enhance-plugin-system`

**infra category (new):**
- `alliance-website-docker-fix` → `infra/fix-docker-build`

**integration category:**
- `blog-lms-wagtail-integration` → `integration/feat-blog-lms-wagtail`

**core category (new):**
- `spec-task-orchestrator` → `core/feat-task-orchestrator`
- `project-modernization` → `core/migrate-project-structure`

**ui category (new):**
- `structa-color-update` → `ui/fix-color-scheme`

**data category (new):**
- `fix-get-translation-template-tag` → `data/fix-translation-tag`
- `fix-wagtailsnippets-assets-email-enhancement` → `data/fix-wagtail-snippets` (split into multiple specs)

## 4. Proposed Category Structure

```
.kiro/specs-organized/
├── api/          # API development
├── auth/         # Authentication & authorization
├── core/         # Core functionality & orchestration
├── data/         # Data models, migrations, templates
├── docs/         # Documentation
├── infra/        # Infrastructure & deployment
├── integration/  # System integrations
└── ui/           # User interface & styling
```

## 5. Migration Strategy

### Phase 1: Standardize Naming (Low Risk)
1. Add consistent type prefixes to all specs
2. Remove project-specific prefixes (ctc-, structa-)
3. Shorten verbose names

### Phase 2: Reorganize Categories (Medium Risk)
1. Create new topical categories (infra, ui, data, core, api)
2. Move specs to appropriate categories
3. Remove old categories (features, fixes, modernization)

### Phase 3: Update References (High Risk)
1. Update all documentation references
2. Update any scripts or tools that reference spec paths
3. Update .config.kiro files if they contain path references

## 6. Benefits of New Convention

1. **Consistency**: All specs follow the same pattern
2. **Scannability**: Type prefix makes it easy to identify spec purpose
3. **Discoverability**: Topical categories group related work
4. **Clarity**: No ambiguity between type and topic
5. **Scalability**: Easy to add new specs following the pattern
6. **Maintainability**: Clear organizational principle

## 7. Next Steps

1. Review and approve naming convention
2. Create automated renaming script (Task 6.2)
3. Test script on a subset of specs
4. Execute full migration
5. Update documentation and references
6. Archive old spec paths for reference

---

**Analysis Complete**: Ready for Task 6.2 (Create renaming script)
