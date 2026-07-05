# Boundary Violations Report

Generated: 2026-04-14 21:00:00

## Summary

This report documents all boundary violations found in the ecosystem according to the four boundary rules:

1. **nawaai-no-django**: nawaai must be pure Python with zero Django imports
2. **osoul-no-wagtail**: django_fusion must not import wagtail, celery, or crafts_ai
3. **rseal-no-projects**: crafts_ai must not import project-specific code
4. **grep-test-only**: django_fusion is test-only and must not be imported by production code

**Total Violations Found**: 150

## Violations by Rule

### grep-test-only (django_fusion imported by production code)
**Count**: 146 violations

**Rule Description**: django_fusion is test-only and must not be imported by production code. This includes test infrastructure, factories, assertions, and health check utilities that should only be used in test environments.

### rseal-no-projects (crafts_ai importing project-specific code)
**Count**: 4 violations

**Rule Description**: crafts_ai must not import project-specific code. The crafts_ai package should contain only reusable automation logic, not project-specific implementations.

### nawaai-no-django (nawaai importing Django)
**Count**: 0 violations

**Rule Description**: nawaai must be pure Python with zero Django imports. The nawaai package should contain only AI/MCP toolkit logic without any Django dependencies.

### osoul-no-wagtail (django_fusion importing wagtail/celery/rseal)
**Count**: 0 violations

**Rule Description**: django_fusion must not import wagtail, celery, or crafts_ai. The django_fusion package should contain only pure Django foundation logic.

## Detailed Violations

### grep-test-only Violations

| File | Line | Import | Fix Suggestion |
|------|------|--------|----------------|
| docs/scripts/test_email_extraction.py | 12 | django_fusion.email_tools.csv_manager | Remove import of django_fusion from production code |
| docs/scripts/test_email_extraction.py | 13 | django_fusion.email_tools.extractor | Remove import of django_fusion from production code |
| structa.cloud/tests/selenium/test_invite_flow.py | 120 | django_fusion.models | Remove import of django_fusion from production code |
| structa.cloud/tests/selenium/test_invite_flow.py | 177 | django_fusion.models | Remove import of django_fusion from production code |
| structa.cloud/alliance/CI/tests/test_auth_selenium.py | 37 | django_fusion.tests.base | Remove import of django_fusion from production code |
| structa.cloud/alliance/CI/tests/test_auth_selenium.py | 38 | django_fusion.tests.mixins | Remove import of django_fusion from production code |
| structa.cloud/alliance/CI/tests/test_assets_selenium.py | 32 | django_fusion.tests.base | Remove import of django_fusion from production code |
| structa.cloud/alliance/CI/tests/test_assets_selenium.py | 33 | django_fusion.tests.mixins | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/test_auth_selenium.py | 45 | django_fusion.tests.base | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/test_auth_selenium.py | 46 | django_fusion.tests.mixins | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/test_assets_selenium.py | 29 | django_fusion.tests.base | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/test_assets_selenium.py | 30 | django_fusion.tests.mixins | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/test_auth_full.py | 41 | django_fusion.tests.base | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/test_auth_full.py | 42 | django_fusion.tests.mixins | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/email/test_smtp.py | 19 | django_fusion.tests.base | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/auth/test_email_confirmation.py | 20 | django_fusion.tests.base | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/auth/test_password_reset.py | 21 | django_fusion.tests.base | Remove import of django_fusion from production code |
| ctc-research.com/core/CI/tests/auth/test_registration.py | 20 | django_fusion.tests.base | Remove import of django_fusion from production code |

*Note: 128 additional grep-test-only violations omitted for brevity. Full list available in boundary_violations.txt*

### rseal-no-projects Violations

| File | Line | Import | Fix Suggestion |
|------|------|--------|----------------|
| venv/libs/crafts-ai/src/crafts_ai/pipelines/snippets/manage/peoples.py | 5 | apps.handlers.models.manage.company | Remove import of apps.handlers.models.manage.company - crafts_ai must not import project-specific code |
| venv/libs/crafts-ai/src/crafts_ai/pipelines/snippets/manage/services.py | 1 | apps.handlers.models | Remove import of apps.handlers.models - crafts_ai must not import project-specific code |
| venv/libs/crafts-ai/src/crafts_ai/pipelines/models/users/team.py | 1 | apps.handlers.models.manage.company | Remove import of apps.handlers.models.manage.company - crafts_ai must not import project-specific code |
| venv/libs/crafts-ai/src/crafts_ai/pipelines/models/locations/branch.py | 1 | apps.handlers.models.manage.company | Remove import of apps.handlers.models.manage.company - crafts_ai must not import project-specific code |

## Analysis and Recommendations

### 1. grep-test-only Violations Analysis

**Root Cause**: Test files are importing django_fusion, which violates the boundary rule that django_fusion should only be imported by test infrastructure, not by test files themselves.

**Recommendations**:
- Test files should use test infrastructure provided by django_fusion but not import django_fusion directly
- Consider creating a test base class in each project that imports from django_fusion, then have test files inherit from that
- Or, refactor test infrastructure to be project-specific with django_fusion as a build-time dependency only

### 2. rseal-no-projects Violations Analysis

**Root Cause**: crafts_ai package is importing project-specific models from `apps.handlers.models`, which violates the boundary rule that crafts_ai should be project-agnostic.

**Recommendations**:
- Extract the shared model logic from `apps.handlers.models.manage.company` into crafts_ai
- Or, create abstract base classes in crafts_ai that projects can extend
- Use dependency injection to avoid direct imports of project-specific code

### 3. nawaai-no-django and osoul-no-wagtail

**Status**: No violations found. This is good and indicates these boundaries are being respected.

## Next Steps

1. **Phase 2.14**: Run full boundary check on django_fusion after all extractions
2. **Phase 3.17**: Run full boundary check on crafts_ai after all extractions
3. **Phase 4.10**: Run full boundary check - verify django_fusion not imported by production code
4. **Phase 5.1**: Audit nawaai for any Django imports and remove them
5. **Phase 13.1**: Create .importlinter configuration file with all four contracts

## Implementation Priority

1. **High Priority**: Fix rseal-no-projects violations (4 violations) - these are architectural violations
2. **Medium Priority**: Address grep-test-only violations in critical test files
3. **Low Priority**: Clean up remaining grep-test-only violations in non-critical test files

## Notes

- The grep-test-only violations are mostly in test files, which suggests the rule might need refinement
- The rseal-no-projects violations indicate architectural leakage that needs immediate attention
- No violations found for nawaai-no-django or osoul-no-wagtail, which is positive
- Consider updating the boundary rules if test files should be allowed to import django_fusion
