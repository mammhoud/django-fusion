# Component Analyzer Module

Complete guide to the django-fusion component analyzer for scanning, parsing, and analyzing templates and components.

## Overview

The analyzer module (`django_fusion.analyzer`) provides tools for:
- Scanning template files and extracting component usage
- Parsing component data attributes
- Building component maps
- Analyzing component coverage
- Generating analysis reports

## Module Structure

```python
from django_fusion.analyzer import (
    scanner,      # Template scanning utilities
    parser,       # Component data parsing
)
```

### Submodules

| Module | Purpose |
|--------|---------|
| `scanner` | Scans template files and finds component markers |
| `parser` | Parses component attributes and metadata |
| `views` | Analysis view endpoints and reports |
| `schemas` | Data models for analysis results |
| `apps` | Django app configuration |

## Scanner

The scanner module scans template directories for component usage.

```python
from django_fusion.analyzer.scanner import scan

# Scan templates for component usage
result = scan(
    root_paths=['/path/to/templates'],
    filters={
        'include_patterns': ['**/*.html'],
        'exclude_patterns': ['**/legacy/**'],
    },
    depth=10,  # Maximum recursion depth
)

# Access results
for scanned_file in result.files:
    print(f"File: {scanned_file.path}")
    for component in scanned_file.components:
        print(f"  Component: {component.name}")
```

### ScannedFile

Represents a template file with found components.

```python
from django_fusion.analyzer.scanner import ScannedFile

scanned = ScannedFile(
    path='templates/pages/blog_list.html',
    components=[...],  # Found components
    depth=2,  # Directory depth
)

print(scanned.path)
print(len(scanned.components))
```

## Parser

The parser extracts component data from templates.

```python
from django_fusion.analyzer.parser import ParsedTemplate, parse_kwargs

# Parse component template
template_content = """
<div data-component-id="blog_list" data-tracked="true">
    ...
</div>
"""

parsed = ParsedTemplate.from_html(template_content)

# Get component usage
for usage in parsed.usages:
    print(f"Component: {usage.name}")
    print(f"Location: {usage.line}:{usage.column}")
```

### CompUsage

Represents a component usage in a template.

```python
from django_fusion.analyzer.parser import CompUsage

usage = CompUsage(
    name='blog_list',
    line=5,
    column=10,
    attributes={'data-tracked': 'true'},
)

print(usage.name)
print(f"{usage.line}:{usage.column}")
```

### SectionMarker

Represents a template section marker.

```python
from django_fusion.analyzer.parser import SectionMarker

section = SectionMarker(
    name='page-header',
    line=6,
    attributes={'data-section': 'page-header'},
)

print(section.name)
```

## Analysis Views

The module provides Django views for analysis reports.

```python
# In your Django app
from django_fusion.analyzer.views import AnalysisView

# Access analysis endpoints:
# /admin/analyzer/components/  - Component list
# /admin/analyzer/coverage/     - Coverage report
# /admin/analyzer/templates/    - Template analysis
```

## Component Data Attributes

Templates use data attributes for tracking:

### Component Identification

```html
<div data-component-id="blog_list" data-tracked="true">
    <!-- Component content -->
</div>
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-component-id` | Unique component identifier | `blog_list` |
| `data-tracked` | Whether component is tracked | `true` / `false` |
| `data-component` | Component type | `form`, `table`, `card` |

### Section Tracking

```html
<section data-section="page-header" data-section-type="header">
    <h1>Page Title</h1>
</section>

<section data-section="filters" data-section-type="form">
    {% include "components/form/search.html" %}
</section>

<section data-section="results" data-section-type="table">
    {% include "components/table/table.html" %}
</section>
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-section` | Section identifier | `page-header`, `filters`, `results` |
| `data-section-type` | Section type | `header`, `form`, `table`, `nav` |
| `data-tracked` | Whether section is tracked | `true` / `false` |

### Context Information

```html
<div data-site="vresume" 
     data-app="blog" 
     data-page="blog_list"
     data-page-type="component">
    <!-- Content -->
</div>
```

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-site` | Site name | `vresume`, `ctc-research` |
| `data-app` | Application name | `blog`, `portfolio` |
| `data-page` | Page identifier | `blog_list`, `blog_detail` |
| `data-page-type` | Page type | `component`, `page`, `modal` |

## Parsing Component Attributes

Extract component data from templates programmatically.

```python
from django_fusion.analyzer.parser import parse_kwargs

# Parse component attributes
html = '''<div data-component-id="blog_list" 
               data-tracked="true"
               data-section="results">'''

kwargs = parse_kwargs(html)
print(kwargs)
# Output: {
#     'data-component-id': 'blog_list',
#     'data-tracked': 'true',
#     'data-section': 'results'
# }
```

## Complete Example

### Template with Full Tracking

```html
{# pages/blog_list.html #}
{% extends "layout/default.html" %}
{% load i18n %}

{% block main %}
<div data-component-id="blog_list" 
     data-tracked="true"
     data-site="vresume"
     data-app="blog"
     data-page="blog_list"
     data-page-type="component">
    
    {# Page header #}
    <section data-section="page-header" data-section-type="header">
        <h1>{% trans "Blog Posts" %}</h1>
        <p>Latest articles and updates</p>
    </section>
    
    {# Search form #}
    <section data-section="filters" data-section-type="form">
        {% include "components/form/search.html" %}
    </section>
    
    {# Results table #}
    <section data-section="results" data-section-type="table">
        {% include "components/table/blog_list.html" %}
    </section>
    
    {# Pagination #}
    <section data-section="pagination" data-section-type="nav">
        {% include "components/pagination/pagination.html" %}
    </section>
</div>
{% endblock %}
```

### Scanning for Analysis

```python
from django_fusion.analyzer.scanner import scan
from django_fusion.analyzer.parser import ParsedTemplate

# Scan templates
result = scan(root_paths=['templates/'])

# Analyze each file
for scanned_file in result.files:
    print(f"\nAnalyzing: {scanned_file.path}")
    
    # Parse content
    with open(scanned_file.path) as f:
        parsed = ParsedTemplate.from_html(f.read())
    
    # Report components
    print(f"  Components found: {len(parsed.usages)}")
    for usage in parsed.usages:
        print(f"    - {usage.name} at line {usage.line}")
    
    # Report sections
    print(f"  Sections found: {len(parsed.sections)}")
    for section in parsed.sections:
        print(f"    - {section.name} at line {section.line}")
```

## Analysis Schemas

Data models for analysis results.

```python
from django_fusion.analyzer.schemas import Prop, Slot

# Component property
prop = Prop(
    name='title',
    type='string',
    default='Blog',
)

# Template slot
slot = Slot(
    name='content',
    type='html',
    description='Main content area',
)

# Convert to dict
print(prop.to_dict())
# {
#     'name': 'title',
#     'type': 'string',
#     'default': 'Blog',
# }
```

## Common Tasks

### Task 1: Find All Components

```python
from django_fusion.analyzer.scanner import scan

result = scan(root_paths=['templates/'])
all_components = set()

for file in result.files:
    for component in file.components:
        all_components.add(component.name)

print(f"Total unique components: {len(all_components)}")
for name in sorted(all_components):
    print(f"  - {name}")
```

### Task 2: Generate Coverage Report

```python
from django_fusion.analyzer.scanner import scan

result = scan(root_paths=['templates/'])

total_files = len(result.files)
tracked_files = sum(1 for f in result.files if any(c.data_tracked for c in f.components))

coverage = (tracked_files / total_files * 100) if total_files > 0 else 0
print(f"Coverage: {coverage:.1f}% ({tracked_files}/{total_files} files tracked)")
```

### Task 3: Find Untracked Components

```python
from django_fusion.analyzer.scanner import scan

result = scan(root_paths=['templates/'])
untracked = []

for file in result.files:
    for component in file.components:
        if not component.data_tracked:
            untracked.append({
                'file': file.path,
                'component': component.name,
                'line': component.line,
            })

for item in untracked:
    print(f"{item['file']}:{item['line']} - {item['component']}")
```

## Best Practices

### 1. Always Track Components

```html
{# ✅ Good: Tracked #}
<div data-component-id="my_component" data-tracked="true">
    ...
</div>

{# ❌ Avoid: Untracked #}
<div>
    ...
</div>
```

### 2. Use Semantic Section Names

```html
{# ✅ Good: Clear semantic names #}
<section data-section="page-header">...</section>
<section data-section="filters">...</section>
<section data-section="results">...</section>

{# ❌ Avoid: Generic names #}
<section data-section="section1">...</section>
<section data-section="div2">...</section>
```

### 3. Include Context Information

```html
{# ✅ Good: Full context #}
<div data-site="vresume"
     data-app="blog"
     data-page="blog_list"
     data-component-id="blog_list"
     data-tracked="true">
    ...
</div>

{# ❌ Avoid: Missing context #}
<div data-component-id="blog_list">
    ...
</div>
```

### 4. Document Sections

```html
{# ✅ Good: Clear section purposes #}
<!-- Page header with title and description -->
<section data-section="page-header">
    <h1>Blog</h1>
</section>

<!-- Search and filter form -->
<section data-section="filters">
    {% include "components/form/search.html" %}
</section>

{# ❌ Avoid: No documentation #}
<section data-section="header">...</section>
<section data-section="filters">...</section>
```

## Integration with Components

The analyzer integrates with component tracking:

```python
# In your component
class BlogListComponent(RoutableComponent):
    """Tracked component with sections."""
    route_path = "blog/"
    template_name = "pages/blog_list.html"  # Should have tracking attributes
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Component data available for tracking
        context['site'] = 'vresume'
        context['app'] = 'blog'
        context['page'] = 'blog_list'
        return context
```

## Related Documentation

- [COMPONENT_ANALYZER.md](./COMPONENT_ANALYZER.md) - Analysis tools and reporting
- [TEMPLATE_STRUCTURE.md](./TEMPLATE_STRUCTURE.md) - Template organization
- [TEMPLATE_TRACKING.md](./TEMPLATE_TRACKING.md) - Tracking system
- [TEMPLATE_COMPONENTS_INDEX.md](./TEMPLATE_COMPONENTS_INDEX.md) - Component index

---

**Next**: Read [COMPONENT_ANALYZER.md](./COMPONENT_ANALYZER.md) for analysis and reporting.

