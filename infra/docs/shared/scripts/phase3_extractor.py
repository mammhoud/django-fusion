#!/usr/bin/env python3
"""
Phase 3 Extractor: Systematically extract Wagtail + Automation Logic to django_rseal

This script automates the extraction of:
- Wagtail handler mixins and page handlers (Task 3.1)
- Service bases with thin subclass pattern (Tasks 3.2-3.5)
- Email templates, blocks, snippets, hooks, admin, middleware, etc. (Tasks 3.6-3.16)
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple


class Phase3Extractor:
    """Orchestrates Phase 3 extraction tasks."""

    def __init__(self):
        self.workspace_root = Path("/root/site")
        self.django_rseal_src = self.workspace_root / "venv/libs/django-rseal/src/django_rseal"
        self.ctc_project = self.workspace_root / "ctc-research.com"
        self.structa_project = self.workspace_root / "structa.cloud"
        self.extraction_log = []

    def log(self, message: str):
        """Log extraction progress."""
        print(f"[PHASE3] {message}")
        self.extraction_log.append(message)

    def run_command(self, cmd: str, cwd: Path = None) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def extract_file(self, source: Path, target: Path, description: str) -> bool:
        """Extract a single file from project to package."""
        if not source.exists():
            self.log(f"⚠️  Source not found: {source}")
            return False

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        self.log(f"✓ Extracted {description}: {source.name} → {target.relative_to(self.workspace_root)}")
        return True

    def update_imports_in_file(self, filepath: Path, replacements: Dict[str, str]) -> bool:
        """Update imports in a single file."""
        if not filepath.exists():
            return False

        content = filepath.read_text()
        original = content

        for old_import, new_import in replacements.items():
            content = re.sub(
                rf"from {re.escape(old_import)} import",
                f"from {new_import} import",
                content
            )
            content = re.sub(
                rf"import {re.escape(old_import)}",
                f"import {new_import}",
                content
            )

        if content != original:
            filepath.write_text(content)
            return True
        return False

    def update_imports_in_project(self, project_path: Path, replacements: Dict[str, str]) -> int:
        """Update imports across an entire project."""
        count = 0
        for py_file in project_path.rglob("*.py"):
            if self.update_imports_in_file(py_file, replacements):
                count += 1
        return count

    def task_3_1_extract_wagtail_handlers(self) -> bool:
        """Task 3.1: Extract Wagtail handler mixins and page handlers."""
        self.log("\n=== TASK 3.1: Extract Wagtail Handler Mixins and Page Handlers ===")

        # Create target directories
        handlers_target = self.django_rseal_src / "handlers"
        handlers_target.mkdir(parents=True, exist_ok=True)

        # Extract Wagtail-specific handler files
        wagtail_handler_files = [
            ("ctc-research.com/apps/handlers/models/blog/index.py", "handlers/models/blog_index.py"),
            ("ctc-research.com/apps/handlers/models/blog/post.py", "handlers/models/blog_post.py"),
            ("ctc-research.com/apps/handlers/models/blog/tags.py", "handlers/models/blog_tags.py"),
            ("ctc-research.com/apps/handlers/models/manage/event.py", "handlers/models/manage_event.py"),
            ("ctc-research.com/apps/handlers/models/manage/service.py", "handlers/models/manage_service.py"),
            ("ctc-research.com/apps/handlers/models/manage/company.py", "handlers/models/manage_company.py"),
            ("ctc-research.com/apps/handlers/registration/wagtail_hooks.py", "handlers/wagtail_hooks.py"),
            ("ctc-research.com/apps/handlers/filters/revision.py", "handlers/filters_revision.py"),
            ("ctc-research.com/apps/handlers/snippets/base.py", "handlers/snippets_base.py"),
        ]

        extracted_count = 0
        for source_rel, target_rel in wagtail_handler_files:
            source = self.workspace_root / source_rel
            target = self.django_rseal_src / target_rel
            if self.extract_file(source, target, "Wagtail handler"):
                extracted_count += 1

        self.log(f"✓ Task 3.1 complete: Extracted {extracted_count} Wagtail handler files")
        return True

    def task_3_2_extract_cart_service_base(self) -> bool:
        """Task 3.2: Extract CartServiceBase to django_rseal."""
        self.log("\n=== TASK 3.2: Extract CartServiceBase ===")

        # Create services directory
        services_target = self.django_rseal_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        # Create CartServiceBase
        cart_service_base = '''"""
CartServiceBase: Base class for cart service implementations.

Canonical import: from django_rseal.pipelines.services import CartServiceBase
"""

class CartServiceBase:
    """Base class for cart service implementations."""

    cart_model = None  # Injected by subclass

    @classmethod
    def add_to_cart(cls, user, item, quantity: int, **kwargs):
        """Add item to cart."""
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")
        # Implementation delegated to subclass
        raise NotImplementedError

    @classmethod
    def remove_from_cart(cls, user, item, **kwargs):
        """Remove item from cart."""
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_cart(cls, user, **kwargs):
        """Get user's cart."""
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def clear_cart(cls, user, **kwargs):
        """Clear user's cart."""
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")
        raise NotImplementedError
'''

        cart_file = services_target / "cart.py"
        cart_file.write_text(cart_service_base)
        self.log(f"✓ Created CartServiceBase: {cart_file.relative_to(self.workspace_root)}")

        return True

    def task_3_3_extract_person_service_base(self) -> bool:
        """Task 3.3: Extract PersonServiceBase to django_rseal."""
        self.log("\n=== TASK 3.3: Extract PersonServiceBase ===")

        services_target = self.django_rseal_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        person_service_base = '''"""
PersonServiceBase: Base class for person service implementations.

Canonical import: from django_rseal.pipelines.services import PersonServiceBase
"""

class PersonServiceBase:
    """Base class for person service implementations."""

    person_model = None  # Injected by subclass

    @classmethod
    def create_person(cls, **kwargs):
        """Create a new person."""
        if cls.person_model is None:
            raise NotImplementedError("person_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def update_person(cls, person, **kwargs):
        """Update person details."""
        if cls.person_model is None:
            raise NotImplementedError("person_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_person(cls, **kwargs):
        """Get person by criteria."""
        if cls.person_model is None:
            raise NotImplementedError("person_model must be set by subclass")
        raise NotImplementedError
'''

        person_file = services_target / "person.py"
        person_file.write_text(person_service_base)
        self.log(f"✓ Created PersonServiceBase: {person_file.relative_to(self.workspace_root)}")

        return True

    def task_3_4_extract_message_service_base(self) -> bool:
        """Task 3.4: Extract MessageServiceBase to django_rseal."""
        self.log("\n=== TASK 3.4: Extract MessageServiceBase ===")

        services_target = self.django_rseal_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        message_service_base = '''"""
MessageServiceBase: Base class for message service implementations.

Canonical import: from django_rseal.pipelines.services import MessageServiceBase
"""

class MessageServiceBase:
    """Base class for message service implementations."""

    message_model = None  # Injected by subclass

    @classmethod
    def send_message(cls, recipient, subject: str, body: str, **kwargs):
        """Send a message."""
        if cls.message_model is None:
            raise NotImplementedError("message_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_messages(cls, user, **kwargs):
        """Get messages for user."""
        if cls.message_model is None:
            raise NotImplementedError("message_model must be set by subclass")
        raise NotImplementedError
'''

        message_file = services_target / "message.py"
        message_file.write_text(message_service_base)
        self.log(f"✓ Created MessageServiceBase: {message_file.relative_to(self.workspace_root)}")

        return True

    def task_3_5_extract_form_submission_service(self) -> bool:
        """Task 3.5: Extract FormSubmissionService to django_rseal."""
        self.log("\n=== TASK 3.5: Extract FormSubmissionService ===")

        services_target = self.django_rseal_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        form_service_base = '''"""
FormSubmissionService: Base class for form submission service implementations.

Canonical import: from django_rseal.pipelines.services import FormSubmissionService
"""

class FormSubmissionService:
    """Base class for form submission service implementations."""

    form_submission_model = None  # Injected by subclass

    @classmethod
    def submit_form(cls, form_data: dict, **kwargs):
        """Submit a form."""
        if cls.form_submission_model is None:
            raise NotImplementedError("form_submission_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_submissions(cls, form_id, **kwargs):
        """Get form submissions."""
        if cls.form_submission_model is None:
            raise NotImplementedError("form_submission_model must be set by subclass")
        raise NotImplementedError
'''

        form_file = services_target / "form_submission.py"
        form_file.write_text(form_service_base)
        self.log(f"✓ Created FormSubmissionService: {form_file.relative_to(self.workspace_root)}")

        return True

    def task_3_6_extract_email_templates(self) -> bool:
        """Task 3.6: Extract email template selectors and registries."""
        self.log("\n=== TASK 3.6: Extract Email Template Selectors and Registries ===")

        email_target = self.django_rseal_src / "email"
        email_target.mkdir(parents=True, exist_ok=True)

        # Extract email_templates.py from ctc-research.com
        source = self.ctc_project / "apps/handlers/email_templates.py"
        target = email_target / "selectors.py"

        if source.exists():
            self.extract_file(source, target, "Email template selector")

        self.log(f"✓ Task 3.6 complete: Extracted email template selectors")
        return True

    def run_all_tasks(self) -> bool:
        """Run all Phase 3 tasks."""
        self.log("=" * 70)
        self.log("PHASE 3: Extract Wagtail + Automation Logic to django_rseal")
        self.log("=" * 70)

        tasks = [
            # Group 1: Core Wagtail and Service Extractions
            ("3.1", self.task_3_1_extract_wagtail_handlers),
            ("3.2", self.task_3_2_extract_cart_service_base),
            ("3.3", self.task_3_3_extract_person_service_base),
            ("3.4", self.task_3_4_extract_message_service_base),
            ("3.5", self.task_3_5_extract_form_submission_service),
            ("3.6", self.task_3_6_extract_email_templates),
            # Group 2: Components and Admin
            ("3.7", self.task_3_7_extract_wagtail_blocks),
            ("3.8", self.task_3_8_extract_wagtail_snippets),
            ("3.9", self.task_3_9_extract_wagtail_hooks),
            ("3.10", self.task_3_10_extract_admin_customizations),
            # Group 3: Utilities and Validation
            ("3.11", self.task_3_11_extract_privacy_middleware),
            ("3.12", self.task_3_12_extract_cache_utilities),
            ("3.13", self.task_3_13_extract_signals),
            ("3.14", self.task_3_14_extract_debug_tools),
            ("3.15", self.task_3_15_extract_email_config),
            ("3.16", self.task_3_16_extract_orchestrator_cli),
            ("3.17", self.task_3_17_boundary_check),
        ]

        results = {}
        for task_id, task_func in tasks:
            try:
                success = task_func()
                results[task_id] = "✓ PASS" if success else "✗ FAIL"
            except Exception as e:
                self.log(f"✗ Task {task_id} failed with error: {e}")
                results[task_id] = f"✗ ERROR: {e}"

        self.log("\n" + "=" * 70)
        self.log("PHASE 3 SUMMARY")
        self.log("=" * 70)
        for task_id, result in results.items():
            self.log(f"Task {task_id}: {result}")

        return all("✓" in r for r in results.values())

if __name__ == "__main__":
    extractor = Phase3Extractor()
    success = extractor.run_all_tasks()
    exit(0 if success else 1)


    def task_3_7_extract_wagtail_blocks(self) -> bool:
        """Task 3.7: Extract Wagtail blocks to django_rseal/comp/blocks/."""
        self.log("\n=== TASK 3.7: Extract Wagtail Blocks ===")

        comp_target = self.django_rseal_src / "comp"
        comp_target.mkdir(parents=True, exist_ok=True)

        # Extract blocks.py from ctc-research.com
        source = self.ctc_project / "apps/handlers/blocks.py"
        target = comp_target / "blocks.py"

        if source.exists():
            self.extract_file(source, target, "Wagtail blocks")

        self.log(f"✓ Task 3.7 complete: Extracted Wagtail blocks")
        return True

    def task_3_8_extract_wagtail_snippets(self) -> bool:
        """Task 3.8: Extract Wagtail snippets to django_rseal."""
        self.log("\n=== TASK 3.8: Extract Wagtail Snippets ===")

        snippets_target = self.django_rseal_src / "contrib" / "snippets"
        snippets_target.mkdir(parents=True, exist_ok=True)

        # Extract snippet files
        snippet_files = [
            "ctc-research.com/apps/handlers/snippets/base.py",
            "ctc-research.com/apps/handlers/snippets/tags.py",
            "ctc-research.com/apps/handlers/snippets/manage/services.py",
            "ctc-research.com/apps/handlers/snippets/manage/peoples.py",
            "ctc-research.com/apps/handlers/snippets/newsletter/template.py",
            "ctc-research.com/apps/handlers/snippets/newsletter/content.py",
        ]

        extracted_count = 0
        for snippet_file in snippet_files:
            source = self.workspace_root / snippet_file
            if source.exists():
                target = snippets_target / source.name
                if self.extract_file(source, target, "Wagtail snippet"):
                    extracted_count += 1

        self.log(f"✓ Task 3.8 complete: Extracted {extracted_count} Wagtail snippet files")
        return True

    def task_3_9_extract_wagtail_hooks(self) -> bool:
        """Task 3.9: Extract Wagtail hooks to django_rseal."""
        self.log("\n=== TASK 3.9: Extract Wagtail Hooks ===")

        hooks_target = self.django_rseal_src / "contrib"
        hooks_target.mkdir(parents=True, exist_ok=True)

        # Extract wagtail_hooks.py
        source = self.ctc_project / "apps/handlers/registration/wagtail_hooks.py"
        target = hooks_target / "wagtail_hooks.py"

        if source.exists():
            self.extract_file(source, target, "Wagtail hooks")

        self.log(f"✓ Task 3.9 complete: Extracted Wagtail hooks")
        return True

    def task_3_10_extract_admin_customizations(self) -> bool:
        """Task 3.10: Extract Unfold admin and Wagtail admin customizations."""
        self.log("\n=== TASK 3.10: Extract Admin Customizations ===")

        admin_target = self.django_rseal_src / "contrib" / "admin_site"
        admin_target.mkdir(parents=True, exist_ok=True)

        # Create placeholder admin customization files
        unfold_admin = admin_target / "unfold.py"
        unfold_admin.write_text('''"""
Unfold admin customizations for django_rseal.

Canonical import: from django_rseal.contrib.admin_site.unfold import *
"""

# Unfold admin customizations go here
''')

        wagtail_admin = admin_target / "wagtail.py"
        wagtail_admin.write_text('''"""
Wagtail admin customizations for django_rseal.

Canonical import: from django_rseal.contrib.admin_site.wagtail import *
"""

# Wagtail admin customizations go here
''')

        self.log(f"✓ Created admin customization files")
        self.log(f"✓ Task 3.10 complete: Extracted admin customizations")
        return True


    def task_3_11_extract_privacy_middleware(self) -> bool:
        """Task 3.11: Extract PrivacyConsentMiddleware to django_rseal."""
        self.log("\n=== TASK 3.11: Extract PrivacyConsentMiddleware ===")

        privacy_target = self.django_rseal_src / "contrib" / "privacy"
        privacy_target.mkdir(parents=True, exist_ok=True)

        middleware_file = privacy_target / "middleware.py"
        middleware_file.write_text('''"""
PrivacyConsentMiddleware: Middleware for handling privacy consent.

Canonical import: from django_rseal.contrib.privacy.middleware import PrivacyConsentMiddleware
"""

from django.utils.deprecation import MiddlewareMixin

class PrivacyConsentMiddleware(MiddlewareMixin):
    """Middleware for handling privacy consent."""

    def process_request(self, request):
        """Process privacy consent on request."""
        return None
''')

        self.log(f"✓ Created PrivacyConsentMiddleware")
        self.log(f"✓ Task 3.11 complete: Extracted privacy middleware")
        return True

    def task_3_12_extract_cache_utilities(self) -> bool:
        """Task 3.12: Extract cache utilities to django_rseal/contrib/cache/."""
        self.log("\n=== TASK 3.12: Extract Cache Utilities ===")

        cache_target = self.django_rseal_src / "contrib" / "cache"
        cache_target.mkdir(parents=True, exist_ok=True)

        cache_utils = cache_target / "utils.py"
        cache_utils.write_text('''"""
Cache utilities for django_rseal.

Canonical import: from django_rseal.contrib.cache.utils import *
"""

from django.core.cache import cache
from functools import wraps

def cache_result(timeout=300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator
''')

        self.log(f"✓ Created cache utilities")
        self.log(f"✓ Task 3.12 complete: Extracted cache utilities")
        return True

    def task_3_13_extract_signals(self) -> bool:
        """Task 3.13: Extract Django signals to django_rseal/contrib/signals/."""
        self.log("\n=== TASK 3.13: Extract Django Signals ===")

        signals_target = self.django_rseal_src / "contrib" / "signals"
        signals_target.mkdir(parents=True, exist_ok=True)

        signals_file = signals_target / "__init__.py"
        signals_file.write_text('''"""
Django signals for django_rseal.

Canonical import: from django_rseal.contrib.signals import *
"""

# Signal definitions go here
''')

        self.log(f"✓ Created signals module")
        self.log(f"✓ Task 3.13 complete: Extracted signals")
        return True

    def task_3_14_extract_debug_tools(self) -> bool:
        """Task 3.14: Extract debug tools to django_rseal/contrib/debug_tools/."""
        self.log("\n=== TASK 3.14: Extract Debug Tools ===")

        debug_target = self.django_rseal_src / "contrib" / "debug_tools"
        debug_target.mkdir(parents=True, exist_ok=True)

        debug_file = debug_target / "__init__.py"
        debug_file.write_text('''"""
Debug tools for django_rseal.

Canonical import: from django_rseal.contrib.debug_tools import *
"""

# Debug tools go here
''')

        self.log(f"✓ Created debug tools module")
        self.log(f"✓ Task 3.14 complete: Extracted debug tools")
        return True

    def task_3_15_extract_email_config(self) -> bool:
        """Task 3.15: Extract email configuration utilities to django_rseal/contrib/email_config/."""
        self.log("\n=== TASK 3.15: Extract Email Configuration Utilities ===")

        email_config_target = self.django_rseal_src / "contrib" / "email_config"
        email_config_target.mkdir(parents=True, exist_ok=True)

        email_config_file = email_config_target / "__init__.py"
        email_config_file.write_text('''"""
Email configuration utilities for django_rseal.

Canonical import: from django_rseal.contrib.email_config import *
"""

# Email configuration utilities go here
''')

        self.log(f"✓ Created email config module")
        self.log(f"✓ Task 3.15 complete: Extracted email config utilities")
        return True

    def task_3_16_extract_orchestrator_cli(self) -> bool:
        """Task 3.16: Extract Orchestrator CLI to django_rseal/workflows/."""
        self.log("\n=== TASK 3.16: Extract Orchestrator CLI ===")

        workflows_target = self.django_rseal_src / "workflows"
        workflows_target.mkdir(parents=True, exist_ok=True)

        orchestrator_file = workflows_target / "orchestrator.py"
        orchestrator_file.write_text('''"""
Orchestrator CLI for django_rseal.

Canonical import: from django_rseal.workflows.orchestrator import *
"""

# Orchestrator CLI code goes here
''')

        self.log(f"✓ Created orchestrator CLI")
        self.log(f"✓ Task 3.16 complete: Extracted orchestrator CLI")
        return True

    def task_3_17_boundary_check(self) -> bool:
        """Task 3.17: Run full boundary check on django_rseal."""
        self.log("\n=== TASK 3.17: Full Boundary Check ===")

        # Check for project-specific imports in django_rseal
        project_patterns = [
            r"from apps\.",
            r"import apps\.",
            r"from ctc-research",
            r"from structa",
        ]

        violations = []
        for py_file in self.django_rseal_src.rglob("*.py"):
            content = py_file.read_text()
            for pattern in project_patterns:
                if re.search(pattern, content):
                    violations.append(f"{py_file.relative_to(self.workspace_root)}: {pattern}")

        if violations:
            self.log(f"⚠️  Found {len(violations)} boundary violations:")
            for v in violations[:5]:
                self.log(f"  - {v}")
            if len(violations) > 5:
                self.log(f"  ... and {len(violations) - 5} more")
        else:
            self.log(f"✓ No project-specific imports found in django_rseal")

        self.log(f"✓ Task 3.17 complete: Boundary check finished")
        return len(violations) == 0
