{{SPEC_NAME}}
=============================================================================

## Overview
{{SPEC_DESCRIPTION}}

## Category
{{SPEC_CATEGORY}}

## Status
**Completion**: {{COMPLETION_PERCENTAGE}}
**Tasks**: {{COMPLETED_TASKS}}/{{TOTAL_TASKS}} completed

## Files
- requirements.md: {{REQUIREMENTS_STATUS}}
- design.md: {{DESIGN_STATUS}}
- tasks.md: {{TASKS_STATUS}}

## Task Summary
- **Total tasks**: {{TOTAL_TASKS}}
- **Completed**: {{COMPLETED_TASKS}}
- **In progress**: {{IN_PROGRESS_TASKS}}
- **Partial**: {{PARTIAL_TASKS}}
- **Not started**: {{NOT_STARTED_TASKS}}

## Use Cases
{{USE_CASES}}

## Methods (Key Tasks)

### Phase 1: [Phase Name]
**Purpose**: Brief description of phase purpose

**Methods**:
- **1.1 [Task Name]**: {{TASK_DESCRIPTION}}
  - **Parameters**: {{PARAMETERS}}
  - **Returns**: {{RETURNS}}
  - **Raises**: {{EXCEPTIONS}}
  - **Example**:
    ```python
    # Example code
    result = method_name(param1, param2)
    ```

- **1.2 [Task Name]**: {{TASK_DESCRIPTION}}
  - **Parameters**: {{PARAMETERS}}
  - **Returns**: {{RETURNS}}
  - **Example**:
    ```bash
    # Example command
    command --option value
    ```

### Phase 2: [Phase Name]
**Purpose**: Brief description of phase purpose

**Methods**:
- **2.1 [Task Name]**: {{TASK_DESCRIPTION}}
  - **Parameters**: {{PARAMETERS}}
  - **Returns**: {{RETURNS}}
  - **Notes**: {{NOTES}}

## Usage Examples

### Example 1: Basic Usage
**Scenario**: {{SCENARIO_DESCRIPTION}}

**Code**:
```python
# Python example
from module import ClassName

instance = ClassName()
result = instance.method(param)
print(result)
```

**Output**:
```
Expected output
```

### Example 2: Advanced Usage
**Scenario**: {{SCENARIO_DESCRIPTION}}

**Code**:
```bash
# Command line example
./script.sh --input file.txt --output result.json
```

**Expected Result**:
- Result 1
- Result 2
- Result 3

### Example 3: Error Handling
**Scenario**: {{ERROR_SCENARIO}}

**Code**:
```python
try:
    result = risky_operation()
except Exception as e:
    handle_error(e)
```

**Error Messages**:
- `ErrorType: Error message`
- `AnotherError: Another message`

## Configuration

### Environment Variables
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VAR_NAME` | Description | `default_value` | Yes/No |
| `ANOTHER_VAR` | Description | `another_default` | Yes/No |

### Configuration Files
**File**: `config.json`
```json
{
  "setting1": "value1",
  "setting2": "value2"
}
```

**File**: `.env`
```
KEY=VALUE
ANOTHER_KEY=ANOTHER_VALUE
```

## Dependencies

### Internal Dependencies
- [Dependency 1](../dependency1/): {{DESCRIPTION}}
- [Dependency 2](../dependency2/): {{DESCRIPTION}}

### External Dependencies
- **Library 1**: {{VERSION}} - {{DESCRIPTION}}
- **Library 2**: {{VERSION}} - {{DESCRIPTION}}

## Testing

### Unit Tests
**File**: `tests/test_module.py`
```python
def test_method():
    # Test code
    assert result == expected
```

**Run Tests**:
```bash
pytest tests/test_module.py
```

### Integration Tests
**File**: `tests/integration/test_integration.py`
```python
def test_integration():
    # Integration test code
```

**Run Integration Tests**:
```bash
pytest tests/integration/ -v
```

## Performance

### Benchmarks
| Operation | Time | Memory | Notes |
|-----------|------|--------|-------|
| Operation 1 | 100ms | 10MB | Description |
| Operation 2 | 200ms | 20MB | Description |

### Optimization Tips
- Tip 1: Description
- Tip 2: Description
- Tip 3: Description

## Troubleshooting

### Common Issues

#### Issue 1: [Error Message]
**Symptoms**: {{SYMPTOMS}}
**Cause**: {{CAUSE}}
**Solution**: {{SOLUTION}}

#### Issue 2: [Error Message]
**Symptoms**: {{SYMPTOMS}}
**Cause**: {{CAUSE}}
**Solution**: {{SOLUTION}}

### Debugging
**Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Debug Commands**:
```bash
# Debug command 1
command --debug

# Debug command 2
another-command -v
```

## Related Documentation

### API Reference
- [API Documentation](api.md) - Complete API reference
- [Data Models](models.md) - Data structure definitions

### Guides
- [Getting Started](getting-started.md) - Quick start guide
- [Best Practices](best-practices.md) - Recommended practices
- [Migration Guide](migration.md) - Upgrade instructions

## Changelog

### Version 1.0.0
- Initial implementation
- Basic functionality
- Documentation

### Version 1.1.0
- Added feature X
- Improved performance
- Fixed bugs

## See Also
- [Related Spec 1](../related-spec1/) - {{DESCRIPTION}}
- [Related Spec 2](../related-spec2/) - {{DESCRIPTION}}
- [Project Documentation](../../README.md) - Main project documentation

---

**Last Updated**: {{LAST_UPDATED}}
**Version**: {{VERSION}}
**Status**: {{STATUS}}
