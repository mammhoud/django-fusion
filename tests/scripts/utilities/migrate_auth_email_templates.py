#!/usr/bin/env python
"""
Migration script to move data from AuthEmailTemplate to django-rseal EmailTemplate.

This script migrates existing authentication email templates from the
website-specific AuthEmailTemplate model to the shared django-rseal
EmailTemplate model.

Usage:
    python migrate_auth_email_templates.py
"""

import os
import sys

import django

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.apps import apps
from django.db import transaction
from django.utils import timezone


def migrate_auth_email_templates():
    """Migrate AuthEmailTemplate data to EmailTemplate."""

    print("Starting migration of AuthEmailTemplate to EmailTemplate...")

    # Check if AuthEmailTemplate model exists
    try:
        AuthEmailTemplate = apps.get_model("accounts", "AuthEmailTemplate")
    except LookupError:
        print("❌ AuthEmailTemplate model not found. Skipping migration.")
        return

    # Check if EmailTemplate model exists
    try:
        EmailTemplate = apps.get_model("pipelines", "EmailTemplate")
    except LookupError:
        print("❌ django-rseal EmailTemplate model not found.")
        print("   Make sure 'django_rseal.pipelines' is in INSTALLED_APPS.")
        return

    # Get all AuthEmailTemplate instances
    auth_templates = AuthEmailTemplate.objects.all()
    total = auth_templates.count()

    if total == 0:
        print("✅ No AuthEmailTemplate instances to migrate.")
        return

    print(f"Found {total} AuthEmailTemplate instance(s) to migrate.")

    migrated_count = 0
    skipped_count = 0

    with transaction.atomic():
        for auth_template in auth_templates:
            try:
                # Map AuthEmailTemplate type to EmailTemplate type
                template_type_map = {
                    "registration_confirmation": "welcome",
                    "signin_success": "notification",
                }

                email_template_type = template_type_map.get(
                    auth_template.template_type, "notification"
                )

                # Create EmailTemplate instance
                email_template = EmailTemplate(
                    name=f"Migrated: {auth_template.get_template_type_display()}",
                    description=f"Migrated from AuthEmailTemplate on {timezone.now().date()}",
                    template_type=email_template_type,
                    template_source="inline",
                    subject_template=auth_template.subject,
                    html_content=auth_template.body_html,
                    text_content=auth_template.body_text,
                    language="en",
                    is_active=auth_template.is_active,
                    is_default=auth_template.is_active,  # Active templates become default
                    version=1,
                )

                # Save the template
                email_template.save()

                print(f"  ✅ Migrated: {auth_template.get_template_type_display()} "
                      f"(id: {auth_template.id}) -> EmailTemplate (id: {email_template.id})")
                migrated_count += 1

            except Exception as e:
                print(f"  ❌ Failed to migrate AuthEmailTemplate id {auth_template.id}: {e}")
                skipped_count += 1

    print("\n" + "="*60)
    print("Migration Summary:")
    print(f"  Total AuthEmailTemplate instances: {total}")
    print(f"  Successfully migrated: {migrated_count}")
    print(f"  Skipped/Failed: {skipped_count}")

    if migrated_count > 0:
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update code to use django-rseal EmailTemplate instead of AuthEmailTemplate")
        print("2. Remove AuthEmailTemplate model from models.py")
        print("3. Create and run Django migrations to remove AuthEmailTable table")
        print("4. Test email functionality with new templates")
    else:
        print("\n⚠️ No templates were migrated. Check for errors above.")


def update_references_guide():
    """Print guide for updating code references."""

    print("\n" + "="*60)
    print("CODE REFERENCE UPDATE GUIDE")
    print("="*60)

    print("\n1. Import statements to change:")
    print("   FROM: from www.apps.accounts.registration.models import AuthEmailTemplate")
    print("   TO:   from django_rseal.workflows.pipelines.models.settings.templates import EmailTemplate")

    print("\n2. Template type mapping:")
    print("   AuthEmailTemplate.REGISTRATION_CONFIRMATION -> EmailTemplate 'welcome'")
    print("   AuthEmailTemplate.SIGNIN_SUCCESS -> EmailTemplate 'notification'")

    print("\n3. Query examples:")
    print("   FROM: AuthEmailTemplate.objects.filter(template_type='registration_confirmation', is_active=True).first()")
    print("   TO:   EmailTemplate.get_default_for_type('welcome', language='en')")

    print("\n4. Using EmailService instead of direct email sending:")
    print("   FROM: send_mail(subject, message, from_email, [recipient])")
    print("   TO:   from django_rseal.communication.email.services import EmailService")
    print("         service = EmailService()")
    print("         service.send_email(recipient, subject, template_name, context)")

    print("\n5. Template rendering:")
    print("   FROM: render_to_string('email/registration.html', context)")
    print("   TO:   template = EmailTemplate.get_default_for_type('welcome')")
    print("         rendered = template.get_rendered_content(context)")


if __name__ == "__main__":
    print("="*60)
    print("AUTH EMAIL TEMPLATE MIGRATION TOOL")
    print("="*60)

    # Run migration
    migrate_auth_email_templates()

    # Show reference update guide
    update_references_guide()

    print("\n" + "="*60)
    print("Migration tool completed.")
    print("="*60)
