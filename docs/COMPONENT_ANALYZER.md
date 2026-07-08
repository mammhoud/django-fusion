# Component Analyzer Documentation

Guide to analyzing and tracking template components across the application.

## Overview

The Component Analyzer scans templates and Python components to:

1. **Identify** all components and their sections
2. **Track** component usage across templates
3. **Analyze** component relationships
4. **Generate** component maps
5. **Report** on component coverage

## Template Scanning

### Detection Pattern

The analyzer looks for `data-section` attributes in templates:

```django
<section data-section="section-name" data-tracked="true">
    <!-- This section is tracked -->
</section>
```

### Scanning Process

```
1. Find all .html templates
2. Parse for data-section attributes
3. Extract section metadata
4. Map to components
5. Build relationships graph
6. Generate report
```

## Section Hierarchy

Sections are organized hierarchically:

```
Page Template
├── Section 1 (data-section="header")
│   ├── Component: page-title
│   └── Component: page-subtitle
├── Section 2 (data-section="filters")
│   └── Component: search-form
├── Section 3 (data-section="results")
│   ├── Section 3.1 (data-section="table-header")
│   ├── Section 3.2 (data-section="table-data")
│   └── Section 3.3 (data-section="table-footer")
└── Section 4 (data-section="pagination")
```

## Tracking Attributes Reference

### Component Identification

```django
{# Identify the component #}
<div data-component="component-type"
     data-component-id="unique-id"
     data-template-path="path/to/template.html">
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-component` | Component type | `form`, `table`, `button` |
| `data-component-id` | Unique identifier | `user_list`, `blog_create` |
| `data-template-path` | Template location | `users/list.html` |

### Section Identification

```django
{# Identify the section #}
<section data-section="section-name"
         data-section-type="type"
         data-tracked="true">
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-section` | Section identifier | `header`, `filters`, `results` |
| `data-section-type` | Section type | `header`, `form`, `table`, `list` |
| `data-tracked` | Enable tracking | `true` |

### Context Information

```django
{# Provide context #}
<div data-site="site-name"
     data-app="app-name"
     data-page="{{ page_name }}"
     data-page-type="component">
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-site` | Site name | `vresume`, `admin`, `lms` |
| `data-app` | Application name | `blog`, `portfolio`, `users` |
| `data-page` | Page identifier | `user_list`, `blog_detail` |
| `data-page-type` | Page type | `component`, `page`, `modal` |

## Component Map Generation

### Structure

```json
{
  "site": "admin",
  "app": "users",
  "component": "user_list",
  "template": "pages/user_management.html",
  "sections": [
    {
      "name": "page-header",
      "type": "header",
      "tracked": true,
      "components": [
        {
          "name": "page-title",
          "type": "text",
          "element": "h1"
        }
      ]
    },
    {
      "name": "filters",
      "type": "form",
      "tracked": true,
      "included_template": "components/form/search.html",
      "form_name": "search"
    },
    {
      "name": "results",
      "type": "table",
      "tracked": true,
      "included_template": "components/table/table.html",
      "table_name": "users",
      "columns": [
        {"key": "username", "label": "Username", "sortable": true},
        {"key": "email", "label": "Email", "sortable": true},
        {"key": "actions", "label": "Actions", "sortable": false}
      ]
    },
    {
      "name": "pagination",
      "type": "pagination",
      "tracked": true,
      "included_template": "components/table/pagination.html"
    }
  ]
}
```

## Usage in Python

### Scanning Templates

```python
from django_fusion.comp.analyzer import TemplateScanner

scanner = TemplateScanner()

# Scan single template
component_map = scanner.scan_template("pages/user_management.html")

# Scan all templates
all_maps = scanner.scan_all_templates()

# Scan by site
site_maps = scanner.scan_by_site("admin")
```

### Analyzing Components

```python
from django_fusion.comp.analyzer import ComponentAnalyzer

analyzer = ComponentAnalyzer()

# Analyze component
analysis = analyzer.analyze_component("user_list")

# Get section information
sections = analyzer.get_sections("user_list")

# Get relationships
dependencies = analyzer.get_dependencies("user_list")
```

### Generating Reports

```python
from django_fusion.comp.analyzer import AnalysisReporter

reporter = AnalysisReporter()

# Generate full report
report = reporter.generate_full_report()

# Generate site-specific report
site_report = reporter.generate_site_report("admin")

# Generate component coverage
coverage = reporter.generate_coverage_report()
```

## Analysis Examples

### Example 1: Component Structure

```json
{
  "name": "user_management",
  "path": "pages/user_management.html",
  "sections": 4,
  "components": 8,
  "tracked": true,
  "included_templates": [
    "components/form/search.html",
    "components/table/table.html",
    "components/table/pagination.html"
  ]
}
```

### Example 2: Section Dependencies

```json
{
  "section": "results",
  "type": "table",
  "depends_on": [
    "filters/form",
    "table-headers",
    "table-data"
  ],
  "used_by": [
    "user_management.html",
    "admin_list.html"
  ]
}
```

### Example 3: Component Coverage

```json
{
  "total_templates": 50,
  "tracked_templates": 48,
  "coverage": "96%",
  "sections_tracked": 180,
  "components_identified": 250,
  "by_site": {
    "admin": {"coverage": "100%", "templates": 15},
    "blog": {"coverage": "90%", "templates": 20},
    "portfolio": {"coverage": "85%", "templates": 15}
  }
}
```

## Analyzer Output

### Console Report

```
╔═══════════════════════════════════════════╗
║     Component Analysis Report             ║
╚═══════════════════════════════════════════╝

Site: admin
  Application: users
    Component: user_list
    Template: pages/user_management.html
    Status: ✓ Tracked
    Sections: 4
      ✓ page-header (header)
      ✓ filters (form)
      ✓ results (table)
      ✓ pagination (pagination)
    Components: 8
    Dependencies: 3 templates
```

### JSON Export

```json
{
  "report_date": "2024-07-06",
  "total_templates": 50,
  "tracked": 48,
  "analysis": {
    "admin": {
      "users": {
        "user_list": {
          "template": "pages/user_management.html",
          "sections": 4,
          "status": "tracked"
        }
      }
    }
  }
}
```

## Tracking Best Practices

### 1. Mark All Sections

```django
{# ✓ Recommended #}
<section data-section="header" data-tracked="true">

{# ✗ Not Recommended #}
<section class="header">
```

### 2. Use Consistent Names

```django
{# ✓ Use consistent naming #}
data-section="page-header"
data-section="form-fields"
data-section="table-data"

{# ✗ Inconsistent #}
data-section="header"
data-section="fields"
data-section="data"
```

### 3. Provide Context

```django
{# ✓ Full context #}
<div data-site="admin"
     data-app="users"
     data-component-id="user_list"
     data-section="results">

{# ✗ Minimal context #}
<div data-section="results">
```

### 4. Document Components

```django
{# Add comments for clarity #}
{# === USER MANAGEMENT PAGE === #}
{# List all users with search and pagination #}
<div data-component-id="user_management" data-tracked="true">
    {# === SEARCH SECTION === #}
    <section data-section="filters">
```

## Integration with Django-Fusion

### Component Analyzer Integration

The analyzer integrates with django-fusion components:

```python
from django_fusion.comp.routes import RoutableComponent
from django_fusion.comp.analyzer import track_component

@track_component
class UserListComponent(RoutableComponent):
    template_name = "pages/user_management.html"
    
    def get_template_names(self):
        # Templates auto-tracked
        return super().get_template_names()
```

### Template Registry

```python
from django_fusion.comp.analyzer import TemplateRegistry

registry = TemplateRegistry()

# Auto-register templates
registry.register_template(
    path="pages/user_management.html",
    component="user_list",
    site="admin",
    app="users"
)
```

## Analyzer Configuration

### Settings

```python
# settings.py

COMPONENT_ANALYZER = {
    'ENABLED': True,
    'SCAN_ON_STARTUP': True,
    'EXPORT_PATH': 'component_analysis/',
    'FORMATS': ['json', 'html', 'csv'],
    'TRACK_SECTIONS': True,
    'TRACK_COMPONENTS': True,
    'MIN_COVERAGE': 0.90,  # 90% coverage requirement
}
```

### Template Configuration

```django
{# Opt-in to tracking in templates #}
{% comment %}
Component-Analyzer-Config:
  site: admin
  app: users
  tracked: true
{% endcomment %}
```

## Reports and Exports

### Available Reports

1. **Full Report** - All components and sections
2. **Coverage Report** - Tracked vs. untracked ratio
3. **Site Report** - Components by site
4. **App Report** - Components by application
5. **Dependency Report** - Component relationships
6. **Timeline Report** - Changes over time

### Export Formats

- **JSON** - Structured data
- **HTML** - Visual report
- **CSV** - Spreadsheet format
- **YAML** - Configuration format

## Troubleshooting

### Sections Not Tracked

Check:
1. `data-section` attribute present? ✓
2. `data-tracked="true"`? ✓
3. Analyzer running? ✓

### Missing Components

Check:
1. Component has `data-component` attribute? ✓
2. Template is in scan path? ✓
3. Template syntax valid? ✓

### Coverage Low

Steps:
1. Identify untracked sections
2. Add `data-section` attributes
3. Re-run analyzer
4. Verify coverage improved

## See Also

- [Template Structure](./TEMPLATE_STRUCTURE.md)
- [Component System](./COMPONENT_SYSTEM.md)
- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md)

