#!/usr/bin/env python
"""
Script to help remove AuthEmailTemplate model and update references.

This script provides guidance on removing the AuthEmailTemplate model
and updating code to use ceptor-ai EmailTemplate instead.
"""

import os
import sys


def check_for_references():
    """Check for references to AuthEmailTemplate in the codebase."""

    print("="*60)
    print("CHECKING FOR AUTH EMAIL TEMPLATE REFERENCES")
    print("="*60)

    # Common patterns to search for
    patterns = [
        "AuthEmailTemplate",
        "apps.accounts.registration.models",
        "registration_confirmation",
        "signin_success",
    ]

    print("\nSearching for references...")

    # This would typically use grep, but we'll provide manual instructions
    print("\nTo find references, run these commands in the ctc-research.com directory:")
    print("\n1. Find imports:")
    print("   grep -r 'AuthEmailTemplate' --include='*.py' .")

    print("\n2. Find model usage:")
    print("   grep -r 'AuthEmailTemplate.objects' --include='*.py' .")

    print("\n3. Find template type references:")
    print("   grep -r 'registration_confirmation\\|signin_success' --include='*.py' .")

    print("\n4. Check admin registrations:")
    print("   grep -r 'AuthEmailTemplateAdmin' --include='*.py' .")

    print("\n5. Check wagtail hooks:")
    print("   grep -r 'AuthEmailTemplate' --include='*.py' apps/accounts/registration/")


def generate_removal_steps():
    """Generate step-by-step removal instructions."""

    print("\n" + "="*60)
    print("STEP-BY-STEP REMOVAL INSTRUCTIONS")
    print("="*60)

    print("\nStep 1: Backup existing data")
    print("   - Run the migration script first:")
    print("     python scripts/migrate_auth_email_templates.py")

    print("\nStep 2: Update models.py")
    print("   - Remove AuthEmailTemplate class from:")
    print("     ctc-research.com/apps/accounts/registration/models.py")
    print("   - Keep CSVEmailTest and CSVEmailTestBatch if still needed")

    print("\nStep 3: Update admin.py")
    print("   - Remove AuthEmailTemplateAdmin class from:")
    print("     ctc-research.com/apps/accounts/registration/admin.py")
    print("   - Remove admin.site.register(AuthEmailTemplate, AuthEmailTemplateAdmin)")

    print("\nStep 4: Update wagtail_hooks.py")
    print("   - Remove AuthEmailTemplate from wagtail hooks if present")
    print("   - File: ctc-research.com/apps/accounts/registration/wagtail_hooks.py")

    print("\nStep 5: Update all code references")
    print("   - Use the search patterns above to find all references")
    print("   - Update imports to use ceptor_ai.pipelines.models.settings.templates")
    print("   - Update template type references (see mapping guide)")

    print("\nStep 6: Create Django migrations")
    print("   - Run: python manage.py makemigrations accounts")
    print("   - This will generate a migration to remove AuthEmailTemplate table")

    print("\nStep 7: Run migrations")
    print("   - Run: python manage.py migrate accounts")

    print("\nStep 8: Test thoroughly")
    print("   - Test registration emails work with new EmailTemplate")
    print("   - Test sign-in notification emails")
    print("   - Verify no broken imports or references")


def update_code_examples():
    """Show code examples for updating references."""

    print("\n" + "="*60)
    print("CODE UPDATE EXAMPLES")
    print("="*60)

    print("\n1. Import update:")
    print("   BEFORE:")
    print("   from www.apps.accounts.registration.models import AuthEmailTemplate")
    print("")
    print("   AFTER:")
    print("   from ceptor_ai.workflows.pipelines.models.settings.templates import EmailTemplate")
    print("   from ceptor_ai.communication.email.services import EmailService")

    print("\n2. Getting a template:")
    print("   BEFORE:")
    print("   template = AuthEmailTemplate.objects.filter(")
    print("       template_type='registration_confirmation',")
    print("       is_active=True")
    print("   ).first()")
    print("")
    print("   AFTER:")
    print("   template = EmailTemplate.get_default_for_type('welcome', language='en')")
    print("   # or for specific template:")
    print("   template = EmailTemplate.objects.filter(")
    print("       template_type='welcome',")
    print("       language='en',")
    print("       is_active=True")
    print("   ).first()")

    print("\n3. Sending an email:")
    print("   BEFORE:")
    print("   from django.core.mail import send_mail")
    print("   send_mail(")
    print("       template.subject,")
    print("       template.body_text,")
    print("       'noreply@example.com',")
    print("       [user.email],")
    print("       html_message=template.body_html")
    print("   )")
    print("")
    print("   AFTER:")
    print("   from ceptor_ai.communication.email.services import EmailService")
    print("   service = EmailService()")
    print("   service.send_email(")
    print("       recipient=user.email,")
    print("       subject=template.subject_template,")
    print("       template_name='components/email/transactional/welcome.html',")
    print("       context={'user': user, 'site_name': 'CTC Research'},")
    print("       queue=True  # or False for immediate sending")
    print("   )")

    print("\n4. Template rendering with variables:")
    print("   BEFORE:")
    print("   html_content = template.body_html")
    print("   # No variable support")
    print("")
    print("   AFTER:")
    print("   rendered = template.get_rendered_content(")
    print("       context={")
    print("           'user_name': user.get_full_name(),")
    print("           'site_name': 'CTC Research',")
    print("           'current_year': datetime.now().year")
    print("       }")
    print("   )")
    print("   html_content = rendered['html']")
    print("   text_content = rendered['text']")


if __name__ == "__main__":
    print("AUTH EMAIL TEMPLATE REMOVAL GUIDE")
    print("="*60)

    check_for_references()
    generate_removal_steps()
    update_code_examples()

    print("\n" + "="*60)
    print("IMPORTANT NOTES:")
    print("="*60)
    print("\n1. Always test in a development environment first")
    print("2. Make sure ceptor-ai is properly installed and configured")
    print("3. Check that EmailTemplate migrations are applied")
    print("4. Verify email sending works before deploying to production")
    print("5. Consider keeping AuthEmailTemplate model commented out")
    print("   for reference during transition period")

    print("\n" + "="*60)
    print("Ready to proceed with consolidation!")
    print("="*60)
