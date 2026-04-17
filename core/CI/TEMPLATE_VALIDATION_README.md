# Template Validation System

## Overview

The Template Validation System provides comprehensive validation for Django templates, ensuring template correctness, detecting syntax errors, and identifying potential issues before runtime.

## Features

- **Syntax Validation**: Detects template syntax errors and malformed tags
- **Structure Validation**: Ensures balanced block, if, and for tags
- **Variable Detection**: Identifies variables used in templates
- **Missing Variable Warnings**: Warns about variables used but not provided in context
- **Filter Validation**: Validates template filters
- **Detailed Error Messages**: Provides clear, actionable error and warning messages

## Installation

The template validation system is located in `core/CI/utils.py` and is ready to use.

## Usage

### Basic Usage

```python
from core.CI.utils import validate_template_string

# Validate a template string
template = "Hello {{ name }}!"
context = {'name': 'World'}

is_valid, errors, warnings = validate_template_string(template, context)

if is_valid:
    print("Template is valid!")
else:
    print(f"Errors: {errors}")

if warnings:
    print(f"Warnings: {warnings}")
```

### Validating Template Files

```python
from core.CI.utils import validate_template

# Validate a template file by name
is_valid, errors, warnings = validate_template('email/welcome.html', context)
```

### Using the TemplateValidator Class

```python
from core.CI.utils import TemplateValidator

validator = TemplateValidator()
is_valid, errors, warnings = validator.validate_template('my_template.html', context)

# Access extracted information
print(f"Variables found: {validator.variables_found}")
print(f"Filters found: {validator.filters_found}")
```

## API Reference

### `validate_template_string(template_string, context=None)`

Validates a template from a string.

**Parameters:**
- `template_string` (str): Template content as string
- `context` (dict, optional): Context dictionary to check for missing variables

**Returns:**
- Tuple of `(is_valid, errors, warnings)`
  - `is_valid` (bool): True if template is valid
  - `errors` (list): List of error messages
  - `warnings` (list): List of warning messages

### `validate_template(template_name, context=None)`

Validates a template by name/path.

**Parameters:**
- `template_name` (str): Name or path of the template
- `context` (dict, optional): Context dictionary to check for missing variables

**Returns:**
- Tuple of `(is_valid, errors, warnings)`

### `TemplateValidator`

Main validation class with comprehensive validation methods.

**Methods:**
- `validate_template(template_name, context=None)`: Validate a template by name
- `_validate_syntax(template_name)`: Validate template syntax
- `_validate_structure(template)`: Validate template structure
- `_extract_variables_and_filters(template)`: Extract variables and filters
- `_check_missing_variables(context)`: Check for missing variables
- `_validate_filters()`: Validate filters

**Attributes:**
- `errors`: List of error messages
- `warnings`: List of warning messages
- `variables_found`: Set of variables found in template
- `filters_found`: Set of filters found in template

## Examples

### Example 1: Validating Email Templates

```python
from core.CI.utils import validate_template

# Validate welcome email template
context = {
    'user': {
        'first_name': 'John',
        'email': 'john@example.com'
    },
    'site_name': 'My Site'
}

is_valid, errors, warnings = validate_template('email/welcome.html', context)

if not is_valid:
    print("Template validation failed:")
    for error in errors:
        print(f"  - {error}")
```

### Example 2: Detecting Syntax Errors

```python
from core.CI.utils import validate_template_string

# Template with syntax error (missing closing brace)
template = "Hello {{ name }!"

is_valid, errors, warnings = validate_template_string(template)

# Output: is_valid=False, errors=['Template syntax error: ...']
```

### Example 3: Detecting Unbalanced Tags

```python
from core.CI.utils import validate_template_string

# Template with unbalanced if tag
template = "{% if condition %}Hello"  # Missing {% endif %}

is_valid, errors, warnings = validate_template_string(template)

# Output: is_valid=False, errors=['Unbalanced if tags: ...']
```

### Example 4: Detecting Missing Variables

```python
from core.CI.utils import validate_template_string

template = "Hello {{ name }} and {{ age }}!"
context = {'name': 'World'}  # age is missing

is_valid, errors, warnings = validate_template_string(template, context)

# Output: is_valid=True, warnings=['Variables used in template but not in context: age']
```

## Validation Rules

### Syntax Validation

- Checks for valid Django template syntax
- Detects malformed variable tags `{{ }}`
- Detects malformed template tags `{% %}`
- Validates template can be parsed

### Structure Validation

- Ensures balanced `{% block %}` and `{% endblock %}` tags
- Ensures balanced `{% if %}` and `{% endif %}` tags
- Ensures balanced `{% for %}` and `{% endfor %}` tags
- Detects unclosed tags

### Variable Validation

- Extracts all variables used in template
- Compares against provided context
- Excludes Django builtin variables (user, request, etc.)
- Warns about missing variables

### Filter Validation

- Extracts all filters used in template
- Validates against Django's registered filters
- Warns about potentially invalid filters

## Testing

The template validation system includes comprehensive unit tests.

### Running Tests

```bash
# Run all template validation tests
python manage.py test core.CI.tests.test_template_validation

# Run specific test class
python manage.py test core.CI.tests.test_template_validation.TemplateValidatorUnitTests

# Run specific test method
python manage.py test core.CI.tests.test_template_validation.TemplateValidatorUnitTests.test_valid_simple_template
```

### Test Coverage

The test suite includes 26 test methods covering:

- Valid template validation
- Syntax error detection
- Unbalanced tag detection
- Missing variable detection
- Filter validation
- Complex template validation
- Edge cases and error handling

## Integration with Django

The template validation system integrates seamlessly with Django's template system:

```python
from django.template.loader import get_template
from core.CI.utils import TemplateValidator

# Validate a Django template
validator = TemplateValidator()
is_valid, errors, warnings = validator.validate_template('my_app/my_template.html')
```

## Error Messages

The system provides clear, actionable error messages:

- **Syntax Errors**: `"Template syntax error in 'template.html': Unclosed variable tag"`
- **Structure Errors**: `"Unbalanced block tags: 3 block(s) but 2 endblock(s)"`
- **Missing Template**: `"Template 'template.html' does not exist"`
- **Missing Variables**: `"Variables used in template but not in context: name, age"`

## Best Practices

1. **Validate Early**: Validate templates during development, not in production
2. **Provide Context**: Always provide expected context for accurate validation
3. **Handle Warnings**: Review warnings about missing variables
4. **Test Templates**: Include template validation in your test suite
5. **Use in CI/CD**: Integrate template validation in your CI/CD pipeline

## Limitations

- Cannot validate templates that use custom template tags not loaded at validation time
- Cannot validate dynamic template includes
- Filter validation may produce false positives for custom filters
- Context validation is based on top-level keys only

## Future Enhancements

Potential future improvements:

- Support for custom template tag validation
- Integration with template linters
- Performance optimization for large template sets
- HTML validation for rendered output
- Accessibility checks for templates

## Support

For issues or questions about the template validation system:

1. Check the test suite for usage examples
2. Review the source code in `core/CI/utils.py`
3. Consult Django's template documentation

## License

This template validation system is part of the ctc-research.com project and follows the same license.
