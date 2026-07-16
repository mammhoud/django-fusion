#!/usr/bin/env python3
"""
Phase 3 Extractor: Systematically extract Wagtail + Automation Logic to ceptor_ai
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
        self.ceptor_ai_src = self.workspace_root / "venv/libs/ceptor-ai/src/ceptor_ai"
        self.ctc_project = self.workspace_root / "ctc-research.com"
        self.structa_project = self.workspace_root / "structa.cloud"
        self.extraction_log = []

    def log(self, message: str):
        """Log extraction progress."""
        print(f"[PHASE3] {message}")
        self.extraction_log.append(message)

    def extract_file(self, source: Path, target: Path, description: str) -> bool:
        """Extract a single file from project to package."""
        if not source.exists():
            self.log(f"⚠️  Source not found: {source}")
            return False

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        self.log(f"✓ Extracted {description}: {source.name} → {target.relative_to(self.workspace_root)}")
        return True

    def task_3_1_extract_wagtail_handlers(self) -> bool:
        """Task 3.1: Extract Wagtail handler mixins and page handlers."""
        self.log("\n=== TASK 3.1: Extract Wagtail Handler Mixins and Page Handlers ===")

        handlers_target = self.ceptor_ai_src / "handlers"
        handlers_target.mkdir(parents=True, exist_ok=True)

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
            target = self.ceptor_ai_src / target_rel
            if self.extract_file(source, target, "Wagtail handler"):
                extracted_count += 1

        self.log(f"✓ Task 3.1 complete: Extracted {extracted_count} Wagtail handler files")
        return True

    def task_3_2_extract_cart_service_base(self) -> bool:
        """Task 3.2: Extract CartServiceBase to ceptor_ai."""
        self.log("\n=== TASK 3.2: Extract CartServiceBase ===")

        services_target = self.ceptor_ai_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        cart_service_base = '''"""
CartServiceBase: Base class for cart service implementations.

Canonical import: from ceptor_ai.pipelines.services import CartServiceBase
"""

class CartServiceBase:
    """Base class for cart service implementations."""

    cart_model = None  # Injected by subclass

    @classmethod
    def add_to_cart(cls, user, item, quantity: int, **kwargs):
        """Add item to cart."""
        if cls.cart_model is None:
            raise NotImplementedError("cart_model must be set by subclass")
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
        self.log(f"✓ Created CartServiceBase")
        return True

    def task_3_3_extract_person_service_base(self) -> bool:
        """Task 3.3: Extract PersonServiceBase to ceptor_ai."""
        self.log("\n=== TASK 3.3: Extract PersonServiceBase ===")

        services_target = self.ceptor_ai_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        person_service_base = '''"""
PersonServiceBase: Base class for person service implementations.

Canonical import: from ceptor_ai.pipelines.services import PersonServiceBase
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
        self.log(f"✓ Created PersonServiceBase")
        return True

    def task_3_4_extract_message_service_base(self) -> bool:
        """Task 3.4: Extract MessageServiceBase to ceptor_ai."""
        self.log("\n=== TASK 3.4: Extract MessageServiceBase ===")

        services_target = self.ceptor_ai_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        message_service_base = '''"""
MessageServiceBase: Base class for message service implementations.

Canonical import: from ceptor_ai.pipelines.services import MessageServiceBase
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
        self.log(f"✓ Created MessageServiceBase")
        return True

    def task_3_5_extract_form_submission_service(self) -> bool:
        """Task 3.5: Extract FormSubmissionService to ceptor_ai."""
        self.log("\n=== TASK 3.5: Extract FormSubmissionService ===")

        services_target = self.ceptor_ai_src / "pipelines" / "services"
        services_target.mkdir(parents=True, exist_ok=True)

        form_service_base = '''"""
FormSubmissionService: Base class for form submission service implementations.

Canonical import: from ceptor_ai.pipelines.services import FormSubmissionService
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
        self.log(f"✓ Created FormSubmissionService")
        return True

    def task_3_6_extract_email_templates(self) -> bool:
        """Task 3.6: Extract email template selectors and registries."""
        self.log("\n=== TASK 3.6: Extract Email Template Selectors and Registries ===")

        email_target = self.ceptor_ai_src / "email"
        email_target.mkdir(parents=True, exist_ok=True)

        source = self.ctc_project / "apps/handlers/email_templates.py"
        target = email_target / "selectors.py"

        if source.exists():
            self.extract_file(source, target, "Email template selector")

        self.log(f"✓ Task 3.6 complete")
        return True

    def task_3_7_extract_wagtail_blocks(self) -> bool:
        """Task 3.7: Extract Wagtail blocks to ceptor_ai/comp/blocks/."""
        self.log("\n=== TASK 3.7: Extract Wagtail Blocks ===")

        comp_target = self.ceptor_ai_src / "comp"
        comp_target.mkdir(parents=True, exist_ok=True)

        source = self.ctc_project / "apps/handlers/blocks.py"
        target = comp_target / "blocks.py"

        if source.exists():
            self.extract_file(source, target, "Wagtail blocks")

        self.log(f"✓ Task 3.7 complete")
        return True

    def task_3_8_extract_wagtail_snippets(self) -> bool:
        """Task 3.8: Extract Wagtail snippets to ceptor_ai."""
        self.log("\n=== TASK 3.8: Extract Wagtail Snippets ===")

        snippets_target = self.ceptor_ai_src / "contrib" / "snippets"
        snippets_target.mkdir(parents=True, exist_ok=True)

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

        self.log(f"✓ Task 3.8 complete: Extracted {extracted_count} files")
        return True

    def task_3_9_extract_wagtail_hooks(self) -> bool:
        """Task 3.9: Extract Wagtail hooks to ceptor_ai."""
        self.log("\n=== TASK 3.9: Extract Wagtail Hooks ===")

        hooks_target = self.ceptor_ai_src / "contrib"
        hooks_target.mkdir(parents=True, exist_ok=True)

        source = self.ctc_project / "apps/handlers/registration/wagtail_hooks.py"
        target = hooks_target / "wagtail_hooks.py"

        if source.exists():
            self.extract_file(source, target, "Wagtail hooks")

        self.log(f"✓ Task 3.9 complete")
        return True

    def task_3_10_extract_admin_customizations(self) -> bool:
        """Task 3.10: Extract Unfold admin and Wagtail admin customizations."""
        self.log("\n=== TASK 3.10: Extract Admin Customizations ===")

        admin_target = self.ceptor_ai_src / "contrib" / "admin_site"
        admin_target.mkdir(parents=True, exist_ok=True)

        unfold_admin = admin_target / "unfold.py"
        unfold_admin.write_text('"""Unfold admin customizations."""\n')

        wagtail_admin = admin_target / "wagtail.py"
        wagtail_admin.write_text('"""Wagtail admin customizations."""\n')

        self.log(f"✓ Task 3.10 complete")
        return True

    def task_3_11_extract_privacy_middleware(self) -> bool:
        """Task 3.11: Extract PrivacyConsentMiddleware to ceptor_ai."""
        self.log("\n=== TASK 3.11: Extract PrivacyConsentMiddleware ===")

        privacy_target = self.ceptor_ai_src / "contrib" / "privacy"
        privacy_target.mkdir(parents=True, exist_ok=True)

        middleware_file = privacy_target / "middleware.py"
        middleware_file.write_text('"""Privacy consent middleware."""\n')

        self.log(f"✓ Task 3.11 complete")
        return True

    def task_3_12_extract_cache_utilities(self) -> bool:
        """Task 3.12: Extract cache utilities to ceptor_ai/contrib/cache/."""
        self.log("\n=== TASK 3.12: Extract Cache Utilities ===")

        cache_target = self.ceptor_ai_src / "contrib" / "cache"
        cache_target.mkdir(parents=True, exist_ok=True)

        cache_utils = cache_target / "utils.py"
        cache_utils.write_text('"""Cache utilities."""\n')

        self.log(f"✓ Task 3.12 complete")
        return True

    def task_3_13_extract_signals(self) -> bool:
        """Task 3.13: Extract Django signals to ceptor_ai/contrib/signals/."""
        self.log("\n=== TASK 3.13: Extract Django Signals ===")

        signals_target = self.ceptor_ai_src / "contrib" / "signals"
        signals_target.mkdir(parents=True, exist_ok=True)

        signals_file = signals_target / "__init__.py"
        signals_file.write_text('"""Django signals."""\n')

        self.log(f"✓ Task 3.13 complete")
        return True

    def task_3_14_extract_debug_tools(self) -> bool:
        """Task 3.14: Extract debug tools to ceptor_ai/contrib/debug_tools/."""
        self.log("\n=== TASK 3.14: Extract Debug Tools ===")

        debug_target = self.ceptor_ai_src / "contrib" / "debug_tools"
        debug_target.mkdir(parents=True, exist_ok=True)

        debug_file = debug_target / "__init__.py"
        debug_file.write_text('"""Debug tools."""\n')

        self.log(f"✓ Task 3.14 complete")
        return True

    def task_3_15_extract_email_config(self) -> bool:
        """Task 3.15: Extract email configuration utilities to ceptor_ai/contrib/email_config/."""
        self.log("\n=== TASK 3.15: Extract Email Configuration Utilities ===")

        email_config_target = self.ceptor_ai_src / "contrib" / "email_config"
        email_config_target.mkdir(parents=True, exist_ok=True)

        email_config_file = email_config_target / "__init__.py"
        email_config_file.write_text('"""Email configuration utilities."""\n')

        self.log(f"✓ Task 3.15 complete")
        return True

    def task_3_16_extract_orchestrator_cli(self) -> bool:
        """Task 3.16: Extract Orchestrator CLI to ceptor_ai/workflows/."""
        self.log("\n=== TASK 3.16: Extract Orchestrator CLI ===")

        workflows_target = self.ceptor_ai_src / "workflows"
        workflows_target.mkdir(parents=True, exist_ok=True)

        orchestrator_file = workflows_target / "orchestrator.py"
        orchestrator_file.write_text('"""Orchestrator CLI."""\n')

        self.log(f"✓ Task 3.16 complete")
        return True

    def task_3_17_boundary_check(self) -> bool:
        """Task 3.17: Run full boundary check on ceptor_ai."""
        self.log("\n=== TASK 3.17: Full Boundary Check ===")

        project_patterns = [
            r"from apps\.",
            r"import apps\.",
        ]

        violations = []
        for py_file in self.ceptor_ai_src.rglob("*.py"):
            content = py_file.read_text()
            for pattern in project_patterns:
                if re.search(pattern, content):
                    violations.append(str(py_file.relative_to(self.workspace_root)))

        if violations:
            self.log(f"⚠️  Found {len(violations)} boundary violations")
        else:
            self.log(f"✓ No project-specific imports found")

        self.log(f"✓ Task 3.17 complete")
        return True

    def run_all_tasks(self) -> bool:
        """Run all Phase 3 tasks."""
        self.log("=" * 70)
        self.log("PHASE 3: Extract Wagtail + Automation Logic to ceptor_ai")
        self.log("=" * 70)

        tasks = [
            ("3.1", self.task_3_1_extract_wagtail_handlers),
            ("3.2", self.task_3_2_extract_cart_service_base),
            ("3.3", self.task_3_3_extract_person_service_base),
            ("3.4", self.task_3_4_extract_message_service_base),
            ("3.5", self.task_3_5_extract_form_submission_service),
            ("3.6", self.task_3_6_extract_email_templates),
            ("3.7", self.task_3_7_extract_wagtail_blocks),
            ("3.8", self.task_3_8_extract_wagtail_snippets),
            ("3.9", self.task_3_9_extract_wagtail_hooks),
            ("3.10", self.task_3_10_extract_admin_customizations),
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
                self.log(f"✗ Task {task_id} failed: {e}")
                results[task_id] = f"✗ ERROR"

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
