# Template Structure & Component Tracking

Complete guide to template organization, layout hierarchy, and component tracking for the analyzer.

## Template Organization Hierarchy

```
templates/
├── base.html                        # Root layout template
├── layout/
│   ├── base_layout.html            # Layout wrapper
│   ├── app_layout.html             # App-specific layout
│   ├── page_layout.html            # Page-specific layout
│   └── sections/
│       ├── header.html
│       ├── sidebar.html
│       ├── footer.html
│       └── breadcrumbs.html
├── components/
│   ├── form/
│   │   ├── form.html               # Generic form
│   │   ├── user.html               # User form
│   │   └── search.html             # Search form
│   ├── table/
│   │   ├── table.html              # Generic table
│   │   ├── users.html              # Users table
│   │   └── pagination.html
│   └── blocks/
│       ├── card.html
│       ├── modal.html
│       └── alert.html
└── pages/
    ├── home.html
    ├── 404.html
    └── error.html
```

## Template Layers

### Layer 1: Base Template

The root template providing site structure.

```django
{# base.html #}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Site Title{% endblock %}</title>
    {% block extra_head %}{% endblock %}
</head>
<body data-site="{% block data_site %}default{% endblock %}">
    {# Navigation tracked #}
    {% include "layout/sections/header.html" %}
    
    {# Main content area #}
    <main class="main-content" data-section="main">
        {% block content %}{% endblock %}
    </main>
    
    {# Footer tracked #}
    {% include "layout/sections/footer.html" %}
    
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**Tracking Attributes:**
- `data-site` - Site identifier
- `data-section` - Content section name

### Layer 2: Layout Template

App-specific layout extending base.

```django
{# layout/app_layout.html #}
{% extends "base.html" %}

{% block title %}{{ app_title }} - Site{% endblock %}

{% block content %}
<div class="app-container" data-app="{% block data_app %}app{% endblock %}">
    
    {# App header section #}
    <header class="app-header" data-section="app-header" data-tracked="true">
        <h1 data-component="app-title">{{ app_title }}</h1>
        {% block app_header %}{% endblock %}
    </header>
    
    {# App sidebar #}
    <aside class="app-sidebar" data-section="sidebar" data-tracked="true">
        {% include "layout/sections/sidebar.html" %}
    </aside>
    
    {# App main content #}
    <section class="app-main" data-section="app-main" data-tracked="true">
        {% block app_main %}{% endblock %}
    </section>
</div>
{% endblock %}
```

**Tracking Attributes:**
- `data-app` - Application name
- `data-section` - Section identifier
- `data-tracked` - Analyzer tracking flag
- `data-component` - Component type

### Layer 3: Page Template

Component-specific page template.

```django
{# pages/component_page.html #}
{% extends "layout/app_layout.html" %}

{% block data_app %}{{ app_name }}{% endblock %}

{% block app_main %}
<div class="page-container" data-page-type="component">
    
    {# Page title section #}
    <section class="page-header" data-section="page-header" data-tracked="true" data-page="{{ page_name }}">
        <h2 data-component="page-title">{{ title }}</h2>
        {% if breadcrumbs %}
            {% include "layout/sections/breadcrumbs.html" with breadcrumbs=breadcrumbs %}
        {% endif %}
    </section>
    
    {# Page content sections #}
    {% block page_sections %}
    
        {# Search/Filter section #}
        {% if form %}
        <section class="page-filters" data-section="filters" data-tracked="true" data-component-id="{{ component.route_name }}">
            {% include "components/form/form.html" with form=form %}
        </section>
        {% endif %}
        
        {# Data/Results section #}
        {% if table_data %}
        <section class="page-results" data-section="results" data-tracked="true" data-component-id="{{ component.route_name }}">
            {% include "components/table/table.html" with table_headers=table_headers table_data=table_data %}
        </section>
        {% endif %}
        
        {# Pagination section #}
        {% if is_paginated %}
        <section class="page-pagination" data-section="pagination" data-tracked="true">
            {% include "components/table/pagination.html" with page_obj=page_obj %}
        </section>
        {% endif %}
        
    {% endblock %}
</div>
{% endblock %}
```

**Tracking Attributes:**
- `data-page-type` - Type of page
- `data-section` - Section identifier
- `data-component-id` - Component identifier
- `data-page` - Page identifier

## Component Template Structure

### Form Component

```django
{# components/form/form.html #}
<form method="POST" class="form-component" 
      data-component="form" 
      data-form-name="{{ form_name }}"
      data-tracked="true">
    
    {% csrf_token %}
    
    {# Form header #}
    <div class="form-header" data-section="form-header">
        <h3 data-component="form-title">{{ form_name|title }}</h3>
    </div>
    
    {# Form fields #}
    <fieldset class="form-fields" data-section="form-fields">
        {% for field in form %}
            <div class="form-group" data-field="{{ field.name }}">
                {{ field.label_tag }}
                {{ field }}
                {% if field.errors %}
                    <div class="field-errors" data-component="error-message">
                        {{ field.errors }}
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    </fieldset>
    
    {# Form actions #}
    <div class="form-actions" data-section="form-actions">
        <button type="submit" class="btn-primary" data-action="submit">Submit</button>
        <a href="/" class="btn-secondary" data-action="cancel">Cancel</a>
    </div>
</form>
```

**Sections Tracked:**
- `form-header` - Form title section
- `form-fields` - Input fields section
- `form-actions` - Action buttons section

### Table Component

```django
{# components/table/table.html #}
<div class="table-component" 
     data-component="table" 
     data-table-name="{{ table_name }}"
     data-tracked="true">
    
    {# Table header #}
    <div class="table-header" data-section="table-header">
        <h3 data-component="table-title">{{ table_name|title }}</h3>
    </div>
    
    {# Table #}
    <table class="table" data-section="table-data">
        <thead>
            <tr data-section="table-headers">
                {% for header in table_headers %}
                    <th data-column="{{ header.key }}" 
                        data-sortable="{{ header.sortable }}">
                        {{ header.label }}
                    </th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in table_data %}
                <tr class="table-row" data-row-id="{{ row.pk }}" data-section="table-row">
                    {% for header in table_headers %}
                        <td data-column="{{ header.key }}">
                            {% with value=row|get_item:header.key %}
                                {{ value|default:"-" }}
                            {% endwith %}
                        </td>
                    {% endfor %}
                </tr>
            {% empty %}
                <tr class="table-empty" data-section="table-empty">
                    <td colspan="{{ table_headers|length }}">No data</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
    
    {# Table footer #}
    <div class="table-footer" data-section="table-footer">
        <span data-component="row-count">{{ table_data|length }} rows</span>
    </div>
</div>
```

**Sections Tracked:**
- `table-header` - Table title section
- `table-headers` - Column headers
- `table-data` - Table body
- `table-row` - Individual rows
- `table-footer` - Row count section

## Section Definition Reference

Sections are marked with `data-section` attribute for component analyzer tracking.

### Common Sections

| Section | Purpose | Tracked | Example |
|---------|---------|---------|---------|
| `header` | Page/component header | ✓ | Title, subtitle |
| `sidebar` | Navigation sidebar | ✓ | Menu, filters |
| `main` | Main content area | ✓ | Page content |
| `footer` | Page footer | ✓ | Footer links |
| `breadcrumbs` | Navigation breadcrumbs | ✓ | Path navigation |
| `form-header` | Form title section | ✓ | Form heading |
| `form-fields` | Input fields | ✓ | Form inputs |
| `form-actions` | Submit/cancel buttons | ✓ | Form actions |
| `table-header` | Table title | ✓ | Table heading |
| `table-headers` | Column headers | ✓ | Column names |
| `table-data` | Table body | ✓ | Data rows |
| `table-row` | Individual row | ✓ | Single data row |
| `pagination` | Pagination controls | ✓ | Page navigation |
| `filters` | Filter section | ✓ | Search/filter |
| `results` | Results section | ✓ | Data display |

## Analyzer Tracking Attributes

Components use these attributes for analyzer tracking:

### Core Attributes

```django
{# Basic tracking #}
<div data-component="component-type" 
     data-section="section-name"
     data-tracked="true">
```

### Identifier Attributes

```django
{# Unique identification #}
<div data-component-id="user_list"           {# Component route name #}
     data-form-name="user"                   {# Form name #}
     data-table-name="users"                 {# Table name #}
     data-page="{{ page_name }}">            {# Page identifier #}
```

### Context Attributes

```django
{# Context information #}
<div data-site="vresume"                     {# Site name #}
     data-app="admin"                        {# Application name #}
     data-page-type="component"              {# Page type #}
     data-template-path="users/list.html">   {# Template path #}
```

### Action Attributes

```django
{# Action tracking #}
<button data-action="submit"                 {# Action name #}
        data-target="form"                   {# Target element #}
        data-component="button">
```

## Component Structure Example

### Full Page Component with Tracking

```django
{# pages/user_management.html #}
{% extends "layout/app_layout.html" %}

{% block data_app %}admin{% endblock %}

{% block app_main %}
<div class="page-container" 
     data-page-type="component"
     data-component-id="user_management"
     data-site="{{ site_name }}"
     data-app="admin"
     data-tracked="true">
    
    {# === HEADER SECTION === #}
    <section class="page-header" 
             data-section="page-header"
             data-tracked="true">
        <h1 data-component="page-title">{{ title }}</h1>
        <p data-component="page-subtitle">Manage system users</p>
    </section>
    
    {# === FILTERS SECTION === #}
    <section class="page-filters" 
             data-section="filters"
             data-tracked="true"
             data-component="search-form">
        {% include "components/form/search.html" with form=search_form %}
    </section>
    
    {# === RESULTS SECTION === #}
    <section class="page-results" 
             data-section="results"
             data-tracked="true"
             data-component="data-table">
        
        {# Table header #}
        <div data-section="table-header">
            <h2 data-component="table-title">Results</h2>
        </div>
        
        {# Table data #}
        <table data-section="table-data" data-tracked="true">
            <thead data-section="table-headers">
                <tr>
                    {% for header in table_headers %}
                        <th data-column="{{ header.key }}">
                            {{ header.label }}
                        </th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for user in table_data %}
                    <tr class="table-row" 
                        data-row-id="{{ user.pk }}"
                        data-section="table-row">
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>
                            <a href="{% url 'admin:user-edit' user.id %}"
                               data-action="edit">Edit</a>
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
    
    {# === PAGINATION SECTION === #}
    {% if is_paginated %}
    <section class="page-pagination" 
             data-section="pagination"
             data-tracked="true">
        {% include "components/table/pagination.html" %}
    </section>
    {% endif %}
    
</div>
{% endblock %}
```

## Analyzer Integration

The component analyzer scans templates for tracking attributes:

### Scan Pattern

```python
# Looks for templates with data-section attributes
pattern = r'data-section="([^"]+)"'

# Identifies sections in templates
sections = {
    'page-header': {...},
    'filters': {...},
    'results': {...},
    'pagination': {...},
}
```

### Tracked Data

```json
{
  "template": "pages/user_management.html",
  "site": "admin",
  "app": "admin",
  "component": "user_management",
  "sections": [
    {
      "name": "page-header",
      "type": "header",
      "tracked": true,
      "components": ["page-title", "page-subtitle"]
    },
    {
      "name": "filters",
      "type": "form",
      "tracked": true,
      "component": "search-form"
    },
    {
      "name": "results",
      "type": "table",
      "tracked": true,
      "rows": 10,
      "columns": ["username", "email", "actions"]
    },
    {
      "name": "pagination",
      "type": "pagination",
      "tracked": true,
      "pages": 5
    }
  ]
}
```

## Template Best Practices

### 1. Use Consistent Section Names

```django
{# ✓ Good #}
<section data-section="page-header">

{# ✗ Bad #}
<section data-section="header">
```

### 2. Mark All Trackable Sections

```django
{# ✓ Good #}
<section data-section="filters" data-tracked="true">

{# ✗ Bad #}
<section class="filters">
```

### 3. Use Component Identifiers

```django
{# ✓ Good #}
<div data-component-id="user_list" data-table-name="users">

{# ✗ Bad #}
<div class="user-list">
```

### 4. Provide Context Information

```django
{# ✓ Good #}
<div data-site="admin" data-app="users" data-page="{{ page_name }}">

{# ✗ Bad #}
<div class="page">
```

## Template Layers Reference

| Layer | File | Purpose | Extension |
|-------|------|---------|-----------|
| Base | `base.html` | Root structure | N/A |
| Layout | `layout/app_layout.html` | App wrapper | `extends "base.html"` |
| Page | `pages/component_page.html` | Component view | `extends "layout/..."` |
| Component | `components/*.html` | Reusable piece | `{% include "..." %}` |

## Navigation Example

```
base.html
    ↑ extended by
layout/app_layout.html
    ↑ extended by
pages/user_management.html
    ├─ includes
    │  ├─ layout/sections/header.html
    │  ├─ components/form/search.html
    │  ├─ components/table/table.html
    │  └─ components/table/pagination.html
    └─ includes
       └─ layout/sections/footer.html
```

## Tracking Summary

- **Base template** provides overall structure
- **Layout template** organizes app sections
- **Page template** defines component layout
- **Component templates** render specific functionality
- **All tracked** via `data-section` and `data-component` attributes

## See Also

- [Component System](./COMPONENT_SYSTEM.md)
- [Forms & Tables Integration](./FORMS_TABLES_INTEGRATION.md)
- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md)

