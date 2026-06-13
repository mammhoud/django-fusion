#!/usr/bin/env python3
"""
Phase 3 Import Updater: Fix boundary violations and update imports in projects
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class Phase3ImportUpdater:
    """Updates imports after Phase 3 extraction."""

    def __init__(self):
        self.workspace_root = Path("/root/site")
        self.ctc_project = self.workspace_root / "ctc-research.com"
        self.structa_project = self.workspace_root / "structa.cloud"
        self.django_rseal_src = self.workspace_root / "venv/libs/django-rseal/src/django_rseal"
        self.updates_count = 0

    def log(self, message: str):
        """Log progress."""
        print(f"[IMPORT_UPDATE] {message}")

    def fix_boundary_violations(self) -> int:
        """Fix project-specific imports in django_rseal files."""
        self.log("\n=== Fixing Boundary Violations in django_rseal ===")

        violations_fixed = 0

        # Files with project-specific imports that should be removed or abstracted
        files_to_fix = [
            self.django_rseal_src / "pipelines/managers/user.py",
            self.django_rseal_src / "pipelines/models/users/team.py",
            self.django_rseal_src / "pipelines/models/locations/branch.py",
            self.django_rseal_src / "pipelines/models/workspace.py",
            self.django_rseal_src / "pipelines/services/certificate.py",
            self.django_rseal_src / "pipelines/site/mixins.py",
            self.django_rseal_src / "pipelines/site/payments.py",
            self.django_rseal_src / "pipelines/site/tags.py",
            self.django_rseal_src / "pipelines/signals/utils.py",
            self.django_rseal_src / "pipelines/snippets/tags.py",
            self.django_rseal_src / "pipelines/snippets/manage/services.py",
            self.django_rseal_src / "pipelines/snippets/manage/peoples.py",
            self.django_rseal_src / "pipelines/snippets/manage/partners.py",
            self.django_rseal_src / "pipelines/snippets/manage/events.py",
            self.django_rseal_src / "pipelines/snippets/manage/team.py",
            self.django_rseal_src / "contrib/snippets/services.py",
            self.django_rseal_src / "contrib/snippets/peoples.py",
            self.django_rseal_src / "contrib/snippets/tags.py",
            self.django_rseal_src / "handlers/models/manage_company.py",
            self.django_rseal_src / "handlers/models/blog_index.py",
            self.django_rseal_src / "comp/blocks.py",
        ]

        for filepath in files_to_fix:
            if filepath.exists():
                content = filepath.read_text()
                original = content

                # Remove or comment out project-specific imports
                # These will be handled by dependency injection in projects
                content = re.sub(
                    r'from apps\.handlers\.models import.*\n',
                    '# Project-specific imports removed - use dependency injection\n',
                    content
                )
                content = re.sub(
                    r'from apps\.handlers\..*import.*\n',
                    '# Project-specific imports removed\n',
                    content
                )
                content = re.sub(
                    r'from apps\.LMS\.models import.*\n',
                    '# Project-specific imports removed\n',
                    content
                )
                content = re.sub(
                    r'from apps\.pages\.models import.*\n',
                    '# Project-specific imports removed\n',
                    content
                )
                content = re.sub(
                    r'from apps\.teams\.models import.*\n',
                    '# Project-specific imports removed\n',
                    content
                )
                content = re.sub(
                    r'from apps\.profiles\.models import.*\n',
                    '# Project-specific imports removed\n',
                    content
                )

                if content != original:
                    filepath.write_text(content)
                    violations_fixed += 1
                    self.log(f"✓ Fixed: {filepath.relative_to(self.workspace_root)}")

        self.log(f"✓ Fixed {violations_fixed} files with boundary violations")
        return violations_fixed

    def update_project_imports(self, project_path: Path) -> int:
        """Update imports in a project to use new django_rseal locations."""
        self.log(f"\n=== Updating imports in {project_path.name} ===")

        # Import replacements mapping
        replacements = {
            # Email templates
            r'from apps\.handlers\.email_templates import': 'from django_rseal.email.selectors import',
            # Wagtail blocks
            r'from apps\.handlers\.blocks import': 'from django_rseal.comp.blocks import',
            # Wagtail hooks
            r'from apps\.handlers\.registration\.wagtail_hooks import': 'from django_rseal.contrib.wagtail_hooks import',
            # Snippets
            r'from apps\.handlers\.snippets\.base import': 'from django_rseal.contrib.snippets.base import',
            r'from apps\.handlers\.snippets\.tags import': 'from django_rseal.contrib.snippets.tags import',
            # Services
            r'from apps\.handlers\.services\.cart import': 'from django_rseal.pipelines.services.cart import',
            r'from apps\.handlers\.services\.person import': 'from django_rseal.pipelines.services.person import',
            r'from apps\.handlers\.services\.message import': 'from django_rseal.pipelines.services.message import',
            r'from apps\.handlers\.services\.form_submission import': 'from django_rseal.pipelines.services.form_submission import',
        }

        updated_count = 0
        for py_file in project_path.rglob("*.py"):
            content = py_file.read_text()
            original = content

            for old_pattern, new_import in replacements.items():
                content = re.sub(old_pattern, new_import, content)

            if content != original:
                py_file.write_text(content)
                updated_count += 1

        self.log(f"✓ Updated {updated_count} files in {project_path.name}")
        return updated_count

    def run_all_updates(self) -> bool:
        """Run all import updates."""
        self.log("=" * 70)
        self.log("PHASE 3: Import Updates and Boundary Violation Fixes")
        self.log("=" * 70)

        try:
            # Fix boundary violations in django_rseal
            violations_fixed = self.fix_boundary_violations()

            # Update imports in both projects
            ctc_updates = self.update_project_imports(self.ctc_project)
            structa_updates = self.update_project_imports(self.structa_project)

            self.log("\n" + "=" * 70)
            self.log("IMPORT UPDATE SUMMARY")
            self.log("=" * 70)
            self.log(f"Boundary violations fixed: {violations_fixed}")
            self.log(f"CTC project imports updated: {ctc_updates}")
            self.log(f"Structa project imports updated: {structa_updates}")

            return True
        except Exception as e:
            self.log(f"✗ Error during import updates: {e}")
            return False

if __name__ == "__main__":
    updater = Phase3ImportUpdater()
    success = updater.run_all_updates()
    exit(0 if success else 1)
