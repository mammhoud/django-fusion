# Documentation Templates

This directory contains templates for spec documentation and organization.

## Available Templates

### 1. Spec Directory Template
**File**: `spec-directory-template/`
**Purpose**: Template for creating new spec directories
**Contents**:
- `requirements.md` - Template for requirements documentation
- `design.md` - Template for design documentation
- `tasks.md` - Template for task lists
- `README.md` - Template for spec-specific README

### 2. Documentation Templates
**File**: `documentation-templates/`
**Purpose**: Templates for various documentation types
**Contents**:
- `pydoc-template.md` - Pydoc-style documentation template
- `api-documentation.md` - API documentation template
- `usage-examples.md` - Usage examples template
- `changelog-template.md` - Changelog template

### 3. Report Templates
**File**: `report-templates/`
**Purpose**: Templates for analysis and status reports
**Contents**:
- `status-report.md` - Status report template
- `analysis-report.md` - Analysis report template
- `completion-report.md` - Completion report template

## How to Use Templates

### Create New Spec
```bash
# Copy template to new spec directory
cp -r .kiro/specs-organized/templates/spec-directory-template .kiro/specs/new-spec-name

# Customize template files
cd .kiro/specs/new-spec-name
# Edit requirements.md, design.md, tasks.md
```

### Generate Documentation
```bash
# Use pydoc template
cat .kiro/specs-organized/templates/documentation-templates/pydoc-template.md > docs/pydoc.md

# Customize with spec-specific content
sed -i "s/{{SPEC_NAME}}/new-spec-name/g" docs/pydoc.md
```

### Generate Reports
```bash
# Use status report template
cat .kiro/specs-organized/templates/report-templates/status-report.md > reports/status.md

# Fill in template variables
# {{TOTAL_SPECS}}, {{COMPLETED_SPECS}}, etc.
```

## Template Variables

All templates support these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{SPEC_NAME}}` | Name of the spec | `ecosystem-architectural-refactoring` |
| `{{SPEC_CATEGORY}}` | Category of the spec | `refactoring`, `deployment`, `phases` |
| `{{CREATION_DATE}}` | Date spec was created | `2026-04-17` |
| `{{LAST_UPDATED}}` | Date spec was last updated | `2026-04-17` |
| `{{TOTAL_TASKS}}` | Total number of tasks | `136` |
| `{{COMPLETED_TASKS}}` | Number of completed tasks | `136` |
| `{{COMPLETION_PERCENTAGE}}` | Percentage of tasks completed | `100.0%` |

## Best Practices

### 1. Consistent Structure
- Use the same template for all specs
- Maintain consistent file naming
- Follow the same documentation format

### 2. Template Customization
- Customize templates for specific use cases
- Add project-specific sections as needed
- Update templates when standards change

### 3. Version Control
- Keep templates in version control
- Document template changes
- Maintain backward compatibility

## Related Resources

- [Spec Organization README](../README.md) - Main organization documentation
- [Analysis Script](../analyze_specs.py) - Automated analysis and reporting
- [Report Directory](../reports/) - Generated reports and documentation
