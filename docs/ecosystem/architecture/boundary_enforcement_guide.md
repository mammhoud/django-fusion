# Boundary Enforcement Guide

## Overview

This guide provides comprehensive procedures for enforcing architectural boundaries in the Django ecosystem. It covers the four core boundary rules, enforcement mechanisms, violation detection, resolution procedures, and best practices for maintaining clean separation between packages.

## Core Boundary Rules

### 1. nawaai-no-django
**Rule**: nawaai must be pure Python with zero Django imports
**Purpose**: Keep AI/MCP toolkit framework-agnostic and reusable across any Python project
**Allowed Imports**: Python standard library only
**Forbidden Imports**: Django, Wagtail, Celery, django_fusion, crafts_ai, django_fusion

### 2. osoul-no-wagtail
**Rule**: django_fusion must not import wagtail, celery, or crafts_ai
**Purpose**: Keep foundation layer pure Django for maximum reusability across Django projects
**Allowed Imports**: Python standard library, Django framework
**Forbidden Imports**: Wagtail, Celery, crafts_ai, django_fusion

### 3. rseal-no-projects
**Rule**: crafts_ai must not import project-specific code
**Purpose**: Keep automation layer reusable across all Django+Wagtail projects
**Allowed Imports**: django_fusion, Wagtail, Celery, nawaai
**Forbidden Imports**: `apps.*`, `ctc_research.*`, `structa.*`

### 4. grep-test-only
**Rule**: django_fusion must not be imported by production code
**Purpose**: Keep testing infrastructure separate from production code
**Allowed Imports**: Test files only, health URLs in project configuration
**Forbidden Imports**: Production code importing django_fusion modules

## Enforcement Mechanisms

### 1. Import-Linter Configuration
The primary enforcement mechanism is import-linter with configuration in `.importlinter`:

```ini
[importlinter]
root_packages =
    crafts_ai
    django_fusion
    crafts_ai
    django_fusion
include_external_packages = True
contracts = nawaai-no-django,osoul-no-wagtail,rseal-no-projects,grep-test-only,dependency-direction

[importlinter:contract:nawaai-no-django]
name = nawaai must not import Django, Wagtail, or Celery
type = forbidden
source_modules =
    crafts_ai
forbidden_modules =
    django
    wagtail
    celery

[importlinter:contract:osoul-no-wagtail]
name = django_fusion must not import Wagtail, Celery, or crafts_ai
type = forbidden
source_modules =
    django_fusion
forbidden_modules =
    wagtail
    celery
    crafts_ai

[importlinter:contract:rseal-no-projects]
name = crafts_ai must not import project-specific code
type = forbidden
source_modules =
    crafts_ai
forbidden_modules =
    apps
    ctc_research
    structa

[importlinter:contract:grep-test-only]
name = django_fusion must not be imported by production code
type = forbidden
source_modules =
    django_fusion
    crafts_ai
forbidden_modules =
    django_fusion

[importlinter:contract:dependency-direction]
name = Dependency direction: crafts_ai -> django_fusion -> crafts_ai
type = layers
layers =
    crafts_ai
    django_fusion
    crafts_ai
```

### 2. CI/CD Integration
Boundary checks are integrated into CI/CD pipeline:

```yaml
# .github/workflows/architecture-validation.yml
name: Architecture Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  boundary-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install import-linter

    - name: Run boundary checks
      run: |
        import-linter --config .importlinter

    - name: Run custom boundary checker
      run: |
        python scripts/check_boundaries.py
```

### 3. Pre-commit Hook
Local development enforcement via pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: boundary-check
        name: Boundary Check
        entry: python scripts/check_boundaries.py
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]
```

## Violation Detection Procedures

### 1. Automated Detection Script
```python
# scripts/check_boundaries.py
import subprocess
import sys
import os

def run_import_linter():
    """Run import-linter boundary checks."""
    print("Running import-linter boundary checks...")

    result = subprocess.run(
        ["import-linter", "--config", ".importlinter"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Boundary violations detected:")
        print(result.stdout)
        print(result.stderr)
        return False

    print("✅ All boundary checks passed")
    return True

def check_grep_test_only():
    """Check grep-test-only violations."""
    print("Checking grep-test-only violations...")

    # Find django_fusion imports in production code
    cmd = [
        "grep", "-r",
        "from django_fusion\\|import django_fusion",
        "--include=*.py",
        ".",
        "|", "grep", "-v", "test",
        "|", "grep", "-v", ".pyc",
        "|", "wc", "-l"
    ]

    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
    violation_count = int(result.stdout.strip())

    if violation_count > 0:
        print(f"❌ Found {violation_count} grep-test-only violations")
        return False

    print("✅ No grep-test-only violations")
    return True

def check_rseal_no_projects():
    """Check rseal-no-projects violations."""
    print("Checking rseal-no-projects violations...")

    # Find project imports in crafts_ai
    cmd = [
        "grep", "-r",
        "from apps\\|import apps",
        "venv/libs/crafts-ai/src/crafts_ai/",
        "|", "grep", "-v", ".pyc",
        "|", "wc", "-l"
    ]

    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
    violation_count = int(result.stdout.strip())

    if violation_count > 0:
        print(f"❌ Found {violation_count} rseal-no-projects violations")
        return False

    print("✅ No rseal-no-projects violations")
    return True

def main():
    """Run all boundary checks."""
    print("=" * 60)
    print("Running Comprehensive Boundary Checks")
    print("=" * 60)

    checks = [
        ("import-linter", run_import_linter),
        ("grep-test-only", check_grep_test_only),
        ("rseal-no-projects", check_rseal_no_projects),
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        if not check_func():
            all_passed = False

    if not all_passed:
        print("\n❌ Boundary violations detected. Please fix before committing.")
        sys.exit(1)

    print("\n✅ All boundary checks passed!")

if __name__ == "__main__":
    main()
```

### 2. Manual Detection Procedures
```bash
# Manual boundary check commands

# Check nawaai-no-django violations
grep -r "from django\|import django" venv/libs/nawaai/src/crafts_ai/

# Check osoul-no-wagtail violations
grep -r "from wagtail\|import wagtail" venv/libs/django-fusion/src/django_fusion/
grep -r "from crafts_ai\|import crafts_ai" venv/libs/django-fusion/src/django_fusion/

# Check rseal-no-projects violations
grep -r "from apps\.\|import apps\." venv/libs/crafts-ai/src/crafts_ai/

# Check grep-test-only violations
grep -r "from django_fusion\|import django_fusion" --include="*.py" . \
    | grep -v "/tests/" \
    | grep -v "test_" \
    | grep -v ".pyc"
```

### 3. Boundary Violation Report Generation
```python
# scripts/generate_boundary_report.py
import json
from datetime import datetime

def generate_boundary_report():
    """Generate comprehensive boundary violation report."""

    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_violations": 0,
            "by_rule": {}
        },
        "violations": {
            "nawaai_no_django": [],
            "osoul_no_wagtail": [],
            "rseal_no_projects": [],
            "grep_test_only": []
        },
        "recommendations": []
    }

    # Run detection and populate report
    # ... detection logic ...

    # Write report
    with open("boundary_violations_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report generated: boundary_violations_report.json")

    return report
```

## Violation Resolution Procedures

### 1. nawaai-no-django Violation Resolution

**Common Violation**: nawaai importing Django models
**Root Cause**: AI logic needs Django model data
**Resolution Strategies**:

#### Strategy 1: Extract Pure Python Logic
```python
# BEFORE (Violation)
# crafts_ai/ai/integrations.py
from django.contrib.auth.models import User

class OpenAIIntegration:
    def get_user_context(self, user_id):
        user = User.objects.get(id=user_id)  # VIOLATION: Django import
        return {"username": user.username}

# AFTER (Resolution)
# crafts_ai/ai/integrations.py (Pure Python)
class OpenAIIntegration:
    def get_user_context(self, user_data):  # Accept dict, not Django model
        return {"username": user_data.get("username")}

# django_fusion/adapters/ai.py (Django adapter)
from crafts_ai.ai.integrations import OpenAIIntegration
from django.contrib.auth.models import User

class DjangoOpenAIIntegration(OpenAIIntegration):
    def get_user_context(self, user_id):
        user = User.objects.get(id=user_id)
        return super().get_user_context({
            "username": user.username,
            "email": user.email
        })
```

#### Strategy 2: Use Dependency Injection
```python
# BEFORE (Violation)
# crafts_ai/orchestrator/models.py
from django.db import models  # VIOLATION

class Task(models.Model):
    name = models.CharField(max_length=255)

# AFTER (Resolution)
# crafts_ai/orchestrator/models.py (Pure Python dataclass)
from dataclasses import dataclass

@dataclass
class Task:
    name: str
    status: str

# django_fusion/orchestrator/adapters.py (Django adapter)
from crafts_ai.orchestrator.models import Task as PureTask
from django.db import models

class DjangoTask(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)

    def to_pure(self):
        return PureTask(name=self.name, status=self.status)

    @classmethod
    def from_pure(cls, pure_task):
        return cls(name=pure_task.name, status=pure_task.status)
```

### 2. osoul-no-wagtail Violation Resolution

**Common Violation**: django_fusion importing Wagtail components
**Root Cause**: Foundation logic needs Wagtail functionality
**Resolution Strategies**:

#### Strategy 1: Move Wagtail Logic to crafts_ai
```python
# BEFORE (Violation)
# django_fusion/handlers/mixins/wagtail_page.py
from wagtail.models import Page  # VIOLATION

class WagtailPageMixin:
    def get_page_tree(self):
        return Page.objects.all()

# AFTER (Resolution)
# crafts_ai/handlers/mixins/wagtail_page.py (Correct location)
from wagtail.models import Page  # ALLOWED in crafts_ai

class WagtailPageMixin:
    def get_page_tree(self):
        return Page.objects.all()

# django_fusion/handlers/mixins/page.py (Pure Django version)
class PageMixin:
    def get_page_data(self):
        # Pure Django logic
        return {"title": "Page"}
```

#### Strategy 2: Create Abstract Base Classes
```python
# BEFORE (Violation)
# django_fusion/comp/blocks.py
from wagtail.blocks import StructBlock  # VIOLATION

class ContentBlock(StructBlock):
    pass

# AFTER (Resolution)
# django_fusion/comp/blocks.py (Abstract base)
class BaseContentBlock:
    """Abstract base class for content blocks."""
    def render(self, context):
        raise NotImplementedError

# crafts_ai/comp/blocks.py (Wagtail implementation)
from wagtail.blocks import StructBlock
from django_fusion.comp.blocks import BaseContentBlock

class ContentBlock(BaseContentBlock, StructBlock):
    """Wagtail implementation of content block."""
    def render(self, context):
        return super().render(context)
```

### 3. rseal-no-projects Violation Resolution

**Common Violation**: crafts_ai importing project-specific models
**Root Cause**: Reusable logic needs project model data
**Resolution Strategies**:

#### Strategy 1: Extract Reusable Logic
```python
# BEFORE (Violation)
# crafts_ai/pipelines/services/cart.py
from apps.lms.models import Cart  # VIOLATION

class CartService:
    def add_to_cart(self, user, item):
        cart = Cart.objects.get_or_create(user=user)  # Project-specific model
        cart.items.add(item)
        return cart

# AFTER (Resolution)
# crafts_ai/pipelines/services/cart.py (Abstract base)
class CartServiceBase:
    cart_model = None  # Abstract attribute

    @classmethod
    def add_to_cart(cls, user, item):
        cart = cls.cart_model.objects.get_or_create(user=user)
        cart.items.add(item)
        return cart

# apps/lms/services/cart.py (Project-specific subclass)
from crafts_ai.pipelines.services.cart import CartServiceBase
from apps.lms.models import Cart

class CartService(CartServiceBase):
    cart_model = Cart  # Model injection
```

#### Strategy 2: Use Generic Types
```python
# BEFORE (Violation)
# crafts_ai/pipelines/models/users/team.py
from apps.handlers.models.manage.company import Organization  # VIOLATION

class Team:
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

# AFTER (Resolution)
# crafts_ai/pipelines/models/users/team.py (Generic)
class Team:
    organization_model = None  # Generic foreign key

    def set_organization(self, org_instance):
        self.organization = org_instance

# apps/accounts/models/manage/company.py (Project model)
from crafts_ai.pipelines.models.users.team import Team as BaseTeam

class Organization(models.Model):
    name = models.CharField(max_length=255)

class Team(BaseTeam):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization_model = Organization
```

### 4. grep-test-only Violation Resolution

**Common Violation**: Production code importing django_fusion
**Root Cause**: Test utilities used in production
**Resolution Strategies**:

#### Strategy 1: Move Test Utilities to Test Files Only
```python
# BEFORE (Violation)
# apps/accounts/views.py (Production code)
from django_fusion.tests.factories import UserFactory  # VIOLATION

class UserView:
    def create_test_user(self):
        return UserFactory.create()  # Test factory in production

# AFTER (Resolution)
# apps/accounts/views.py (Production code - fixed)
from django.contrib.auth.models import User

class UserView:
    def create_user(self, username, email):
        return User.objects.create(username=username, email=email)

# tests/test_accounts.py (Test file - allowed)
from django_fusion.tests.factories import UserFactory

class TestUserView:
    def test_user_creation(self):
        user = UserFactory.create()  # ALLOWED in test file
```

#### Strategy 2: Create Production Equivalents
```python
# BEFORE (Violation)
# apps/content/services.py
from django_fusion.tests.assertions import assert_json_response  # VIOLATION

class ContentService:
    def validate_response(self, response):
        assert_json_response(response)  # Test assertion in production

# AFTER (Resolution)
# django_fusion/contrib/responses.py (Production equivalent)
def validate_json_response(response):
    """Production version of JSON response validation."""
    if response.status_code != 200:
        raise ValueError(f"Invalid status code: {response.status_code}")
    if response["Content-Type"] != "application/json":
        raise ValueError("Not a JSON response")
    return True

# apps/content/services.py (Production code)
from django_fusion.contrib.responses import validate_json_response

class ContentService:
    def validate_response(self, response):
        validate_json_response(response)  # Production version
```

## Prevention Procedures

### 1. Code Review Checklist
**Before merging any PR, verify:**

#### nawaai-no-django Prevention
- [ ] No `import django` statements in crafts_ai
- [ ] No `from django.` imports in crafts_ai
- [ ] No `wagtail` or `celery` imports in crafts_ai
- [ ] All AI logic is framework-agnostic

#### osoul-no-wagtail Prevention
- [ ] No `import wagtail` statements in django_fusion
- [ ] No `from wagtail.` imports in django_fusion
- [ ] No `import celery` statements in django_fusion
- [ ] No `import crafts_ai` statements in django_fusion
- [ ] All foundation logic is pure Django

#### rseal-no-projects Prevention
- [ ] No `from apps.` imports in crafts_ai
- [ ] No `import apps` statements in crafts_ai
- [ ] No `ctc_research` or `structa` imports in crafts_ai
- [ ] All automation logic is project-agnostic
- [ ] Model injection pattern used for project-specific models

#### grep-test-only Prevention
- [ ] No `import django_fusion` in production code
- [ ] No `from django_fusion.` imports outside test files
- [ ] Test utilities only used in test files
- [ ] Health check imports only in URL configuration

### 2. Development Workflow Enforcement
```bash
#!/bin/bash
# development_workflow.sh

# Step 1: Run boundary checks before committing
python scripts/check_boundaries.py

# Step 2: Run import-linter
import-linter --config .importlinter

# Step 3: Run tests (which should not import django_fusion in production)
python manage.py test --exclude-tag=slow

# Step 4: If all checks pass, allow commit
if [ $? -eq 0 ]; then
    echo "✅ All boundary checks passed"
    exit 0
else
    echo "❌ Boundary violations detected"
    exit 1
fi
```

### 3. IDE Configuration
Configure IDE to warn about boundary violations:

```json
// .vscode/settings.json
{
  "python.analysis.extraPaths": [
    "./venv/libs/django-fusion/src",
    "./venv/libs/crafts-ai/src",
    "./venv/libs/django-fusion/src",
    "./venv/libs/nawaai/src"
  ],
  "python.analysis.exclude": [
    "**/tests/**",
    "**/migrations/**"
  ],
  "python.linting.pylintEnabled": true,
  "python.linting.pylintArgs": [
    "--disable=all",
    "--enable=import-error"
  ]
}
```

## Monitoring and Reporting

### 1. Boundary Violation Dashboard
```python
# monitoring/boundary_dashboard.py
from datetime import datetime, timedelta
import json

class BoundaryDashboard:
    def __init__(self):
        self.violations = []
        self.metrics = {}

    def record_violation(self, rule, file, line, import_statement):
        """Record a boundary violation."""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "rule": rule,
            "file": file,
            "line": line,
            "import": import_statement,
            "resolved": False
        }

        self.violations.append(violation)
        self._update_metrics()

    def _update_metrics(self):
        """Update violation metrics."""
        self.metrics = {
            "total_violations": len(self.violations),
            "unresolved_violations": len([v for v in self.violations if not v["resolved"]]),
            "violations_by_rule": {},
            "violations_today": len([
                v for v in self.violations
                if datetime.fromisoformat(v["timestamp"]).date() == datetime.now().date()
            ])
        }

        for violation in self.violations:
            rule = violation["rule"]
            self.metrics["violations_by_rule"][rule] = \
                self.metrics["violations_by_rule"].get(rule, 0) + 1

    def generate_report(self):
        """Generate boundary violation report."""
        report = {
            "generated": datetime.now().isoformat(),
            "metrics": self.metrics,
            "recent_violations": [
                v for v in self.violations
                if datetime.fromisoformat(v["timestamp"]) > datetime.now() - timedelta(days=7)
            ],
            "top_offending_files": self._get_top_offending_files(),
            "recommendations": self._generate_recommendations()
        }

        return report

    def _get_top_offending_files(self):
        """Get files with most violations."""
        file_counts = {}
        for violation in self.violations:
            file = violation["file"]
            file_counts[file] = file_counts.get(file, 0) + 1

        return sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    def _generate_recommendations(self):
        """Generate recommendations based on violations."""
        recommendations = []

        if self.metrics["violations_by_rule"].get("grep-test-only", 0) > 10:
            recommendations.append(
                "High grep-test-only violations: Consider moving test utilities to project-specific test base classes"
            )

        if self.metrics["violations_by_rule"].get("rseal-no-projects", 0) > 5:
            recommendations.append(
                "High rseal-no-projects violations: Review crafts_ai imports and extract reusable logic"
            )

        return recommendations
```

### 2. Automated Alerting
```python
# monitoring/boundary_alerts.py
import smtplib
from email.mime.text import MIMEText

class BoundaryAlertSystem:
    def __init__(self, threshold=5):
        self.threshold = threshold
        self.violation_counts = {}

    def check_and_alert(self, dashboard):
        """Check metrics and send alerts if needed."""
        report = dashboard.generate_report()

        # Check for threshold violations
        for rule, count in report["metrics"]["violations_by_rule"].items():
            if count > self.threshold:
                self._send_alert(rule, count, report)

    def _send_alert(self, rule, count, report):
        """Send email alert for boundary violations."""
        subject = f"🚨 Boundary Violation Alert: {rule}"
        body = f"""
        Boundary violation threshold exceeded!

        Rule: {rule}
        Violations: {count} (threshold: {self.threshold})

        Recent violations:
        {self._format_violations(report['recent_violations'])}

        Top offending files:
        {self._format_top_files(report['top_offending_files'])}

        Recommendations:
        {chr(10).join(report['recommendations'])}

        Please review and fix boundary violations.
        """

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "boundary-alerts@example.com"
        msg["To"] = "architecture-team@example.com"

        # Send email (configure SMTP server)
        # with smtplib.SMTP("smtp.example.com") as server:
        #     server.send_message(msg)

        print(f"Alert sent for {rule}: {count} violations")

    def _format_violations(self, violations):
        """Format violations for alert message."""
        if not violations:
            return "No recent violations"

        lines = []
        for v in violations[:5]:  # Show top 5
            lines.append(f"  - {v['file']}:{v['line']}: {v['import']}")

        return "\n".join(lines)

    def _format_top_files(self, top_files):
        """Format top files for alert message."""
        if not top_files:
            return "No offending files"

        lines = []
        for file, count in top_files:
            lines.append(f"  - {file}: {count} violations")

        return "\n".join(lines)
```

## Training and Documentation

### 1. Developer Onboarding
**Boundary Rules Training Checklist:**
- [ ] Understand nawaai-no-django rule and rationale
- [ ] Understand osoul-no-wagtail rule and rationale
- [ ] Understand rseal-no-projects rule and rationale
- [ ] Understand grep-test-only rule and rationale
- [ ] Know how to run boundary checks
- [ ] Know how to fix common violations
- [ ] Know who to contact for boundary issues

### 2. Documentation Resources
- [ARCHITECTURE.md](./ARCHITECTURE.md): System architecture and boundaries
- [MIGRATION_GUIDE.md](../deployment/MIGRATION_GUIDE.md): Import path changes
- [MIGRATION_SAFETY_GUIDE.md](./MIGRATION_SAFETY_GUIDE.md): Migration safety procedures
- [.importlinter](../../.importlinter): Boundary configuration
- [BOUNDARY_VIOLATIONS.md](./BOUNDARY_VIOLATIONS.md): Historical violations

### 3. FAQ and Troubleshooting

#### Q: Why can't nawaai import Django?
**A**: nawaai is designed to be a framework-agnostic AI/MCP toolkit that can be used in any Python project, not just Django projects. Keeping it pure Python ensures maximum reusability.

#### Q: Why can't django_fusion import Wagtail?
**A**: django_fusion is the pure Django foundation layer that should work with or without Wagtail. Keeping it Wagtail-free allows it to be used in Django projects that don't use Wagtail.

#### Q: Why can't crafts_ai import project code?
**A**: crafts_ai is the reusable automation layer that should work across all Django+Wagtail projects. Keeping it project-agnostic ensures it can be reused in new projects.

#### Q: Why can't production code import django_fusion?
**A**: django_fusion is the testing framework and should only be used in test environments. Keeping it separate from production code ensures clean separation of concerns.

#### Q: How do I know if my code violates boundaries?
**A**: Run `python scripts/check_boundaries.py` or `import-linter --config .importlinter`. The CI pipeline will also catch violations.

#### Q: What's the quickest way to fix a boundary violation?
**A**: Follow the resolution strategies in this guide. Most violations can be fixed by moving code to the correct package or using abstraction patterns.

## Continuous Improvement

### 1. Boundary Rule Evolution
Boundary rules should evolve with the ecosystem:

1. **Quarterly Review**: Review boundary rules every quarter
2. **Violation Analysis**: Analyze common violations for pattern improvements
3. **Rule Refinement**: Refine rules based on practical experience
4. **Documentation Updates**: Update guides based on lessons learned

### 2. Metrics-Driven Improvement
Track and improve based on metrics:

1. **Violation Trends**: Monitor violation trends over time
2. **Resolution Time**: Track average time to resolve violations
3. **Prevention Rate**: Measure effectiveness of prevention measures
4. **Developer Feedback**: Collect feedback from developers

### 3. Tooling Improvements
Continuously improve boundary enforcement tooling:

1. **Better Detection**: Improve violation detection accuracy
2. **Faster Feedback**: Reduce time to detect violations
3. **Better Guidance**: Provide clearer fix suggestions
4. **Integration**: Better IDE and CI/CD integration

## Appendices

### Appendix A: Boundary Rule Quick Reference

| Rule | Source Modules | Forbidden Modules | Purpose |
|------|---------------|-------------------|---------|
| nawaai-no-django | crafts_ai | django, wagtail, celery | Keep AI toolkit framework-agnostic |
| osoul-no-wagtail | django_fusion | wagtail, celery, crafts_ai | Keep foundation layer pure Django |
| rseal-no-projects | crafts_ai | apps, ctc_research, structa | Keep automation layer project-agnostic |
| grep-test-only | django_fusion, crafts_ai | django_fusion | Keep testing infrastructure separate |

### Appendix B: Common Fix Patterns

| Violation Pattern | Fix Pattern | Example |
|-------------------|------------|---------|
| nawaai importing Django | Extract pure logic, create adapter | See Strategy 1 |
| osoul importing Wagtail | Move to crafts_ai, create abstract base | See Strategy 1 |
| rseal importing apps | Use model injection, extract reusable logic | See Strategy 1 |
| Production importing django_fusion | Move to test files, create production equivalent | See Strategy 1 |

### Appendix C: Command Reference

```bash
# Boundary checking commands
import-linter --config .importlinter
python scripts/check_boundaries.py

# Manual checking commands
grep -r "from django" venv/libs/nawaai/src/crafts_ai/
grep -r "from wagtail" venv/libs/django-fusion/src/django_fusion/
grep -r "from apps" venv/libs/crafts-ai/src/crafts_ai/
grep -r "from django_fusion" --include="*.py" . | grep -v test

# Fix commands
python scripts/fix_boundary_violations.py --rule grep-test-only
python scripts/fix_boundary_violations.py --rule rseal-no-projects
```

### Appendix D: Contact Information

- **Architecture Team**: architecture@example.com
- **Emergency Contact**: oncall-architecture@example.com
- **Slack Channel**: #architecture-boundaries
- **Documentation**: https://docs.example.com/architecture/boundaries

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md): System architecture overview
- [MIGRATION_SAFETY_GUIDE.md](./MIGRATION_SAFETY_GUIDE.md): Migration safety procedures
- [MIGRATION_GUIDE.md](../deployment/MIGRATION_GUIDE.md): Import path changes
- [BOUNDARY_VIOLATIONS.md](./BOUNDARY_VIOLATIONS.md): Historical violation reports

## Version History

- **v1.0.0**: Initial boundary enforcement guide
- **v1.1.0**: Added violation resolution procedures
- **v1.2.0**: Added monitoring and alerting
- **v1.3.0**: Added training and FAQ sections

## Feedback and Improvements

Please report issues, suggestions, or improvements to the architecture team. This guide should be continuously updated based on boundary enforcement experiences and lessons learned.
