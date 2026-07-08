# Template & Components Documentation Index

Complete index for template structure, component tracking, and analyzer documentation.

## Documentation Map

```
docs/
├── TEMPLATE_COMPONENTS_INDEX.md       (This file - Index)
├── ARCHITECTURE_OVERVIEW.md           (Architecture & routing)
├── TEMPLATE_STRUCTURE.md              (Template organization)
├── COMPONENT_ANALYZER.md              (Component tracking)
├── COMPONENT_SYSTEM.md                (Component system)
├── FORMS_TABLES_INTEGRATION.md        (Forms & tables)
├── ROUTABLE_COMPONENTS.md             (Routable components)
└── INTEGRATION_EXAMPLES.md            (Real examples)
```

## Quick Start

### For Template Developers

1. Read: [Template Structure](./TEMPLATE_STRUCTURE.md)
2. Learn: Template layers (base → layout → page → component)
3. Practice: Add tracking attributes to templates
4. Verify: Use Component Analyzer to check tracking

### For Component Builders

1. Read: [Architecture Overview](./ARCHITECTURE_OVERVIEW.md)
2. Learn: Site → Application → Component hierarchy
3. Create: Define components in Python
4. Register: Add to Site and Application

### For Analyzers

1. Read: [Component Analyzer](./COMPONENT_ANALYZER.md)
2. Learn: Scanning and tracking patterns
3. Configure: Set up analyzer settings
4. Generate: Run reports and exports

## Document Relationships

```
ARCHITECTURE_OVERVIEW
├─ Explains dual routing (Page vs Component)
├─ Site → Application → Component hierarchy
└─ References: TEMPLATE_STRUCTURE, COMPONENT_SYSTEM

TEMPLATE_STRUCTURE
├─ Template layers and organization
├─ Section tracking with data-* attributes
├─ References: COMPONENT_ANALYZER, INTEGRATION_EXAMPLES
└─ Referenced by: COMPONENT_ANALYZER

COMPONENT_ANALYZER
├─ Scanning templates for data-section attributes
├─ Building component maps
├─ Generating reports
└─ References: TEMPLATE_STRUCTURE, ARCHITECTURE_OVERVIEW

COMPONENT_SYSTEM
├─ Component classes and types
├─ Component lifecycle
└─ References: ARCHITECTURE_OVERVIEW, ROUTABLE_COMPONENTS

FORMS_TABLES_INTEGRATION
├─ Form and table rendering
├─ Template cascade
└─ References: TEMPLATE_STRUCTURE, INTEGRATION_EXAMPLES

ROUTABLE_COMPONENTS
├─ Component routing
├─ Fragment detection
└─ References: ARCHITECTURE_OVERVIEW, INTEGRATION_EXAMPLES

INTEGRATION_EXAMPLES
├─ Real-world examples
├─ Multi-site customization
└─ References: All documentation
```

## Key Concepts

### Template Layers

**Level 1: Base Template**
- Root HTML structure
- Global styles and scripts
- Main navigation
- Footer

**Level 2: Layout Template**
- App-specific wrapper
- Sidebar/navigation
- Header structure
- Main content area

**Level 3: Page Template**
- Component-specific view
- Sections (header, filters, results, pagination)
- Form and table containers
- Action buttons

**Level 4: Component Template**
- Reusable pieces (form, table, card, etc.)
- Included in page templates
- Isolated styling and logic

### Component Hierarchy

```
Site (VResumeSite)
├── Application (BlogApp)
│   ├── RoutableComponent (BlogListComponent)
│   │   route_path: "list/"
│   │   template_name: "blog/list.html"
│   │   URL: /blog/list/
│   │
│   └── FragmentComponent (BlogDetailComponent)
│       route_path: "<slug>/"
│       fragment_name: "blog.fragments.post_detail"
│       URL: /blog/<slug>/
│
└── Application (PortfolioApp)
    ├── RoutableComponent (ProjectListComponent)
    └── RoutableComponent (ProjectDetailComponent)
```

### Tracking Attributes

**Component Identification**
- `data-component` - Component type (form, table, etc.)
- `data-component-id` - Unique identifier (user_list, blog_create, etc.)
- `data-tracked` - Tracking enabled (true/false)

**Section Identification**
- `data-section` - Section name (header, filters, results, pagination, etc.)
- `data-section-type` - Section type (header, form, table, etc.)

**Context Information**
- `data-site` - Site name (admin, blog, portfolio, etc.)
- `data-app` - Application name (users, blog, portfolio, etc.)
- `data-page` - Page identifier (user_list, blog_detail, etc.)
- `data-page-type` - Page type (component, page, modal, etc.)

## Section Types Reference

### Page Sections

| Section | Type | Purpose |
|---------|------|---------|
| page-header | header | Page title and subtitle |
| page-breadcrumbs | nav | Navigation breadcrumbs |
| page-filters | form | Search/filter form |
| page-results | list | Data results |
| page-pagination | nav | Page pagination |

### Form Sections

| Section | Type | Purpose |
|---------|------|---------|
| form-header | header | Form title |
| form-fields | form | Input fields |
| form-actions | nav | Submit/cancel buttons |
| form-errors | alert | Error messages |

### Table Sections

| Section | Type | Purpose |
|---------|------|---------|
| table-header | header | Table title |
| table-headers | nav | Column headers |
| table-data | list | Data rows |
| table-row | item | Individual row |
| table-footer | footer | Row count/info |
| table-empty | alert | No data message |

## Usage Patterns

### Pattern 1: Full Page with Form and Table

```django
{# pages/user_management.html #}
<div data-component-id="user_management" data-tracked="true">
    
    {# Header #}
    <section data-section="page-header">...</section>
    
    {# Search form #}
    <section data-section="filters">
        {% include "components/form/search.html" %}
    </section>
    
    {# Results table #}
    <section data-section="results">
        {% include "components/table/table.html" %}
    </section>
    
    {# Pagination #}
    <section data-section="pagination">
        {% include "components/table/pagination.html" %}
    </section>
</div>
```

### Pattern 2: Component with Dynamic Content

```django
{# components/blog_list.html #}
<div data-component="blog-list" 
     data-component-id="blog_list"
     data-tracked="true">
    
    {% for post in posts %}
        <article data-section="blog-post"
                 data-row-id="{{ post.id }}">
            <h3>{{ post.title }}</h3>
            <p>{{ post.excerpt }}</p>
        </article>
    {% endfor %}
</div>
```

### Pattern 3: Modal with Form

```django
{# Modal component #}
<div data-component="modal"
     data-component-id="user_create_modal"
     data-tracked="true">
    
    <div data-section="modal-header">
        <h2>Create User</h2>
    </div>
    
    <div data-section="modal-body">
        {% include "components/form/user.html" %}
    </div>
    
    <div data-section="modal-footer">
        <button>Save</button>
        <button>Cancel</button>
    </div>
</div>
```

## Analyzer Workflow

```
1. Define Components
   ├─ Create Python component classes
   ├─ Set template_name or fragment_name
   └─ Define route_path

2. Create Templates
   ├─ Extend layout template
   ├─ Add data-section attributes
   └─ Include component templates

3. Mark Sections
   ├─ Add data-section to major sections
   ├─ Add data-component to elements
   └─ Add context data-* attributes

4. Scan Templates
   ├─ Run component analyzer
   ├─ Parse data-section attributes
   └─ Build component map

5. Generate Reports
   ├─ Analyze coverage
   ├─ Export data
   └─ Review relationships
```

## Common Tasks

### Task 1: Add a New Component

```
1. Create component class (routable_components.py)
2. Create template (pages/my_component.html)
3. Add data-section attributes
4. Register with Application
5. Run analyzer to verify tracking
```

### Task 2: Track a Section

```
1. Find section in template
2. Add data-section="section-name"
3. Add data-tracked="true"
4. Add context data-* attributes
5. Verify in analyzer report
```

### Task 3: Generate Analysis Report

```
from django_fusion.comp.analyzer import AnalysisReporter

reporter = AnalysisReporter()
report = reporter.generate_full_report()
print(report)
```

## Best Practices Checklist

- [ ] Use semantic section names (page-header, filters, results, etc.)
- [ ] Mark all trackable sections with data-section
- [ ] Provide context via data-site, data-app, data-page
- [ ] Use data-component-id for unique identification
- [ ] Document section purposes in comments
- [ ] Test tracking with component analyzer
- [ ] Keep template hierarchy consistent
- [ ] Use template inclusion for reusable components
- [ ] Maintain consistent naming across sites
- [ ] Generate and review analyzer reports regularly

## Troubleshooting Guide

### Issue: Sections Not Tracked

**Check:**
1. Is `data-section` attribute present?
2. Is `data-tracked="true"`?
3. Has analyzer been run?

**Fix:**
```django
{# Add missing attributes #}
<section data-section="section-name" data-tracked="true">
```

### Issue: Component Not Identified

**Check:**
1. Is `data-component-id` present?
2. Is component registered with Application?
3. Is template path correct?

**Fix:**
```django
{# Add component identification #}
<div data-component-id="my_component" data-tracked="true">
```

### Issue: Low Coverage

**Check:**
1. How many templates are untracked?
2. Which sections are missing tracking?
3. Are new components added?

**Fix:**
1. Add data-section to all major sections
2. Update analyzer configuration
3. Re-run analysis

## Integration Points

### With Django-Fusion

- **Components**: Use RoutableComponent, FragmentComponent
- **Templates**: Extend provided layouts
- **Tracking**: Use data-* attributes
- **Analyzer**: Built-in component scanning

### With Forms & Tables

- **FormMixin**: Provides form context
- **TableMixin**: Provides table context
- **Tracking**: Sections auto-tracked
- **Templates**: Use shared form/table templates

### With Sites & Applications

- **Site**: Top-level container
- **Application**: Groups components
- **Component**: Individual view
- **Tracking**: Hierarchy preserved

## Next Steps

1. **Read Architecture** - Understand component structure
2. **Review Templates** - Study template organization
3. **Learn Tracking** - Add tracking attributes
4. **Run Analyzer** - Generate component maps
5. **Generate Reports** - Analyze coverage

## Document Quick Links

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) | System architecture and routing |
| [TEMPLATE_STRUCTURE.md](./TEMPLATE_STRUCTURE.md) | Template organization and layout |
| [COMPONENT_ANALYZER.md](./COMPONENT_ANALYZER.md) | Component tracking and analysis |
| [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) | Component system fundamentals |
| [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md) | Form and table components |
| [ROUTABLE_COMPONENTS.md](./ROUTABLE_COMPONENTS.md) | Component routing |
| [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) | Real-world examples |

## Support

For questions or issues:

1. Check [Troubleshooting Guide](#troubleshooting-guide)
2. Review [Best Practices Checklist](#best-practices-checklist)
3. See [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md)
4. Review source code comments
5. Run component analyzer for diagnostics

