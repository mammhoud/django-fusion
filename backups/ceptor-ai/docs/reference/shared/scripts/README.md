# Scripts Documentation

This directory contains documentation for all scripts available in the workspace.

## Available Scripts

### Test Execution Scripts

| Script | Purpose | Usage | Parameters |
|--------|---------|-------|------------|
| `run_all_tests.py` | Run all tests for both websites and packages | `python3 scripts/run_all_tests.py` | `--project`, `--package`, `--format`, `--coverage` |
| `verify_test_parity.py` | Verify test parity between structa.cloud and ctc-research.com | `python3 scripts/verify_test_parity.py` | `--threshold`, `--output-format` |
| `test_script_demo.py` | Demonstration of test script usage | `python3 scripts/test_script_demo.py` | None |
| `test_bulk_email.py` | Test bulk email functionality | `python3 scripts/test_bulk_email.py` | `--dry-run`, `--limit` |
| `test_migration_reversal.py` | Test migration reversal functionality | `python3 scripts/test_migration_reversal.py` | `--app`, `--migration` |
| `create_rollback_tags.sh` | Create git tags for rollback points | `./scripts/create_rollback_tags.sh` | None |

### Analysis and Validation Scripts

| Script | Purpose | Usage | Parameters |
|--------|---------|-------|------------|
| `analyze_duplication.py` | Analyze code duplication across the ecosystem | `python3 scripts/analyze_duplication.py` | `--threshold`, `--min-lines`, `--output-format` |
| `analyze_duplication_simple.py` | Simplified duplication analysis | `python3 scripts/analyze_duplication_simple.py` | `--threshold` |
| `analyze_package_duplication.py` | Analyze duplication between packages | `python3 scripts/analyze_package_duplication.py` | `--packages`, `--threshold` |
| `check_boundaries.py` | Check import boundary violations | `python3 scripts/check_boundaries.py` | `--rule`, `--fix`, `--report-only` |
| `check_consistency.py` | Check code consistency across projects | `python3 scripts/check_consistency.py` | `--rules`, `--fix` |
| `check_thin_layer.py` | Check thin layer pattern compliance | `python3 scripts/check_thin_layer.py` | `--verbose`, `--output` |
| `detect_cycles.py` | Detect circular dependencies | `python3 scripts/detect_cycles.py` | `--visualize`, `--output` |
| `detect_parsers.py` | Detect parsers and serializers | `python3 scripts/detect_parsers.py` | `--type`, `--output` |
| `enforce_naming.py` | Enforce naming conventions | `python3 scripts/enforce_naming.py` | `check_module_names`, `check_class_names` |
| `identify_domains.py` | Identify cross-domain leakage | `python3 scripts/identify_domains.py` | `--output`, `--fix` |
| `validate_templates.py` | Validate template organization | `python3 scripts/validate_templates.py` | `check_no_package_templates` |
| `validate_migrations.py` | Validate migration safety | `python3 scripts/validate_migrations.py` | `check_all_migrations` |
| `validate_system.py` | Validate system configuration | `python3 scripts/validate_system.py` | `--check`, `--fix` |
| `validate_and_commit.py` | Validate changes and commit | `python3 scripts/validate_and_commit.py` | `--message`, `--dry-run` |

### Documentation and Organization Scripts

| Script | Purpose | Usage | Parameters |
|--------|---------|-------|------------|
| `organize_docs.py` | Organize documentation files | `python3 scripts/organize_docs.py` | `--run`, `--dry-run` |
| `track_spec_status.py` | Track spec completion status | `python3 scripts/track_spec_status.py` | `--spec`, `--output` |
| `generate_completion_reports.py` | Generate completion reports | `python3 scripts/generate_completion_reports.py` | `--phase`, `--format` |
| `add_translation_tags.py` | Add translation tags to templates | `python3 scripts/add_translation_tags.py` | `--dry-run`, `--verbose` |

### Phase and Migration Scripts

| Script | Purpose | Usage | Parameters |
|--------|---------|-------|------------|
| `phase3_extractor.py` | Phase 3 extraction utilities | `python3 scripts/phase3_extractor.py` | `--module`, `--output` |
| `phase3_extractor_complete.py` | Complete phase 3 extraction | `python3 scripts/phase3_extractor_complete.py` | `--dry-run`, `--verbose` |
| `phase3_import_updater.py` | Update imports for phase 3 | `python3 scripts/phase3_import_updater.py` | `--fix`, `--dry-run` |
| `sync_phases_2_4_to_2_8.py` | Sync phases 2.4 to 2.8 | `python3 scripts/sync_phases_2_4_to_2_8.py` | `--dry-run`, `--verbose` |

### Recovery and Merge Scripts

| Script | Purpose | Usage | Parameters |
|--------|---------|-------|------------|
| `recover_code.py` | Recover deleted code from git history | `python3 scripts/recover_code.py` | `--file`, `--commit` |
| `analyze_branches.py` | Analyze feature branches for improvements | `python3 scripts/analyze_branches.py` | `--branch`, `--output` |
| `intelligent_merge.py` | Merge improvements preserving quality | `python3 scripts/intelligent_merge.py` | `--source`, `--target` |
| `analyze_dependencies.py` | Analyze dependency conflicts | `python3 scripts/analyze_dependencies.py` | `--package`, `--output` |

### Planning and Implementation Scripts

| Script | Purpose | Usage | Parameters |
|--------|---------|-------|------------|
| `plan_implementation.py` | Build complete execution plan | `python3 scripts/plan_implementation.py` | `--phase`, `--output` |

## Script Usage Examples

### Running All Tests

```bash
# Run all tests for both websites
python3 scripts/run_all_tests.py

# Run tests for specific project
python3 scripts/run_all_tests.py --project ctc
python3 scripts/run_all_tests.py --project structa

# Run tests for specific package
python3 scripts/run_all_tests.py --package osoul
python3 scripts/run_all_tests.py --package rseal

# Generate coverage report
python3 scripts/run_all_tests.py --coverage

# Output includes:
# - Test counts for each project
# - Pass/fail status
# - Test parity verification
# - Summary report
# - JSON report saved to TEST_REPORT.json
```

### Verifying Test Parity

```bash
# Verify test parity between websites
python3 scripts/verify_test_parity.py

# With custom threshold (default: 1.5)
python3 scripts/verify_test_parity.py --threshold 1.3

# Output includes:
# - Test count comparison
# - Test category comparison
# - Parity status (pass/fail)
# - Recommendations for improving parity
```

### Analyzing Duplication

```bash
# Analyze duplication with 70% similarity threshold
python3 scripts/analyze_duplication.py --threshold 0.70

# Analyze with minimum lines filter
python3 scripts/analyze_duplication.py --threshold 0.70 --min-lines 10

# Output in different formats
python3 scripts/analyze_duplication.py --threshold 0.70 --output-format json
python3 scripts/analyze_duplication.py --threshold 0.70 --output-format markdown

# Output includes:
# - Duplication report
# - Similarity percentages
# - File locations
# - Categorization (extract-to-osoul, extract-to-rseal, etc.)
# - Report saved to DUPLICATION_REPORT.md
```

### Checking Boundaries

```bash
# Check all boundary rules
python3 scripts/check_boundaries.py

# Check specific boundary rule
python3 scripts/check_boundaries.py --rule crafts-ai-no-django
python3 scripts/check_boundaries.py --rule osoul-no-wagtail
python3 scripts/check_boundaries.py --rule rseal-no-projects
python3 scripts/check_boundaries.py --rule grep-test-only

# Attempt to fix violations automatically
python3 scripts/check_boundaries.py --fix

# Generate report without failing
python3 scripts/check_boundaries.py --report-only

# Output includes:
# - Boundary violation report
# - File, line, import statement
# - Fix suggestions
# - Report saved to BOUNDARY_VIOLATIONS.md
```

### Detecting Circular Dependencies

```bash
# Detect circular dependencies
python3 scripts/detect_cycles.py

# Visualize dependency graph
python3 scripts/detect_cycles.py --visualize

# Output includes:
# - Cycle detection report
# - Cycle details with import paths
# - Break strategy suggestions
# - Graph visualization (if --visualize)
```

### Organizing Documentation

```bash
# Dry run (show what would be moved)
python3 scripts/organize_docs.py --dry-run

# Actually organize files
python3 scripts/organize_docs.py --run

# Output includes:
# - Files to be moved
# - Destination directories
# - Organization summary
```

### Tracking Spec Status

```bash
# Track all spec completion status
python3 scripts/track_spec_status.py

# Track specific spec
python3 scripts/track_spec_status.py --spec ecosystem-architectural-refactoring

# Output includes:
# - Spec completion percentages
# - Task status breakdown
# - Priority recommendations
# - Report saved to MASTER_TASK_LIST.md
```

### Validating Migrations

```bash
# Validate all migrations
python3 scripts/validate_migrations.py check_all_migrations

# Validate specific app migrations
python3 scripts/validate_migrations.py check_app_migrations --app accounts

# Output includes:
# - Migration safety checks
# - Reversibility verification
# - Data integrity validation
```

### Phase 3 Extraction

```bash
# Extract specific module
python3 scripts/phase3_extractor.py --module handlers

# Complete phase 3 extraction (dry run)
python3 scripts/phase3_extractor_complete.py --dry-run

# Update imports after extraction
python3 scripts/phase3_import_updater.py --fix
```

## Script Parameters

### Common Parameters

Most scripts support these common parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--help` | Show help message | `python3 script.py --help` |
| `--verbose` | Enable verbose output | `python3 script.py --verbose` |
| `--dry-run` | Show what would be done without making changes | `python3 script.py --dry-run` |
| `--output` | Specify output file | `python3 script.py --output report.json` |
| `--format` | Output format (text, json, markdown, junit) | `python3 script.py --format json` |

### Script-Specific Parameters

#### `run_all_tests.py`
- `--project`: Specific project to test (ctc, structa, all)
- `--package`: Specific package to test (osoul, rseal, grep, nawaai)
- `--format`: Output format (text, json, junit)
- `--coverage`: Generate coverage report

#### `analyze_duplication.py`
- `--threshold`: Similarity threshold (0.0 to 1.0, default: 0.70)
- `--min-lines`: Minimum lines to consider for duplication (default: 5)
- `--output-format`: Output format (json, markdown, text)

#### `check_boundaries.py`
- `--rule`: Specific boundary rule to check (crafts-ai-no-django, osoul-no-wagtail, rseal-no-projects, grep-test-only)
- `--fix`: Attempt to fix violations automatically
- `--report-only`: Generate report without failing

#### `detect_cycles.py`
- `--visualize`: Generate visualization of dependency graph
- `--output`: Output file for visualization

#### `organize_docs.py`
- `--run`: Actually organize files (required for changes)
- `--dry-run`: Show what would be moved without making changes

#### `track_spec_status.py`
- `--spec`: Specific spec to track
- `--output`: Output file for report

#### `validate_migrations.py`
- `check_all_migrations`: Check all migrations
- `check_app_migrations`: Check specific app migrations
- `--app`: App name for migration checking

## Script Output

Scripts generate various output files:

### Reports Directory
Scripts save reports to appropriate directories:

- `docs/reports/` - Completion reports, validation reports
- `TEST_REPORT.json` - Test execution results
- `TEST_PARITY_REPORT.json` - Test parity verification
- `DUPLICATION_REPORT.md` - Duplication analysis results
- `BOUNDARY_VIOLATIONS.md` - Boundary violation reports
- `MASTER_TASK_LIST.md` - Spec task tracking
- `CIRCULAR_DEPENDENCIES.md` - Cycle detection report
- `THIN_LAYER_VIOLATIONS.md` - Thin layer pattern violations

### Output Formats

Scripts support multiple output formats:

1. **Text**: Human-readable text output to console
2. **JSON**: Structured JSON for programmatic consumption
3. **Markdown**: Formatted markdown for documentation
4. **JUnit**: JUnit XML for CI/CD integration

## Integration with CI/CD

Scripts are integrated into GitHub Actions workflows:

- `.github/workflows/architecture-validation.yml` - Runs boundary checks, duplication checks, tests
- `.github/workflows/test-parity.yml` - Runs test parity verification
- `.github/workflows/documentation.yml` - Runs documentation organization
- `.github/workflows/migration-validation.yml` - Runs migration validation
- `.github/workflows/spec-tracking.yml` - Runs spec status tracking

## Creating New Scripts

When creating new scripts:

1. Follow the existing pattern and structure
2. Include comprehensive help (`--help`)
3. Support common parameters (`--verbose`, `--dry-run`)
4. Generate appropriate output formats
5. Document in this README
6. Add to CI/CD workflows if appropriate

### Script Template

```python
#!/usr/bin/env python3
"""
Brief description of script purpose.

Detailed description including:
- What the script does
- Why it's needed
- How to use it
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Description of script")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Script logic here

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure scripts are executable (`chmod +x script.py`)
2. **Module not found**: Check Python path and dependencies
3. **Output file not created**: Check write permissions
4. **Script hangs**: Check for infinite loops or waiting for input
5. **Import errors**: Ensure virtual environment is activated

### Debugging

```bash
# Enable debug output
python3 -m pdb script.py

# Run with verbose logging
python3 script.py --verbose

# Check script dependencies
python3 -c "import script_module"

# Run with strace for system calls
strace -f python3 script.py
```

### Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Check Python version
python3 --version

# Check script permissions
ls -la scripts/
```

## Related Documentation

- [Testing Documentation](../tests/README.md) - Test structure and execution
- [Architecture Documentation](../architecture/README.md) - Boundary rules and dependencies
- [Development Documentation](../development/README.md) - Development workflow
- [Deployment Documentation](../deployment/README.md) - CI/CD integration
- [Migration Documentation](../migrations/README.md) - Migration strategies and validation

## Maintenance

### Updating Documentation
When adding new scripts or modifying existing ones:

1. Update this README.md with script details
2. Add examples for new parameters
3. Update the script categories if needed
4. Verify all links and references

### Testing Scripts
Regularly test scripts to ensure they work correctly:

```bash
# Run script validation
python3 scripts/validate_system.py

# Test all scripts (dry run)
for script in scripts/*.py; do
    echo "Testing $script..."
    python3 "$script" --help > /dev/null && echo "✓ $script" || echo "✗ $script"
done
```

### Version Compatibility
Scripts are tested with:
- Python 3.11+
- Django 4.2+
- pytest 7.4+
- NetworkX 3.1+

</content>
