"""
Management command to create initial privacy policies and terms of service.

Usage:
    python manage.py create_privacy_policies
"""

from django.core.management.base import BaseCommand
from django_fusion.management.commands.base import BaseCommand

from apps.core.models.profiles.privacy import (
    PrivacyPolicy,
    TermsOfService,
)


class Command(BaseCommand):
    help = "Create initial privacy policies and terms of service"

    def handle(self, *args, **options):
        # Create default privacy policy
        privacy_policy, created = PrivacyPolicy.objects.get_or_create(
            version="1.0",
            defaults={
                "title": "Privacy Policy",
                "content": """
                <h2>Privacy Policy</h2>
                <p>This is our privacy policy. We are committed to protecting your privacy.</p>

                <h3>Information We Collect</h3>
                <p>We collect information you provide directly to us, such as when you create an account or contact us.</p>

                <h3>How We Use Your Information</h3>
                <p>We use the information we collect to provide, maintain, and improve our services.</p>

                <h3>Data Security</h3>
                <p>We implement appropriate technical and organizational measures to protect your personal data.</p>

                <h3>Your Rights</h3>
                <p>You have the right to access, correct, or delete your personal data at any time.</p>

                <h3>Contact Us</h3>
                <p>If you have any questions about this privacy policy, please contact us at privacy@example.com</p>
                """,
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created default privacy policy v1.0")
            )
        else:
            self.stdout.write(
                self.style.WARNING("✓ Privacy policy v1.0 already exists")
            )

        # Create default terms of service
        terms, created = TermsOfService.objects.get_or_create(
            version="1.0",
            defaults={
                "title": "Terms of Service",
                "content": """
                <h2>Terms of Service</h2>
                <p>These terms of service govern your use of our platform.</p>

                <h3>Acceptance of Terms</h3>
                <p>By accessing and using this platform, you accept and agree to be bound by the terms and provision of this agreement.</p>

                <h3>Use License</h3>
                <p>Permission is granted to temporarily download one copy of the materials (information or software) on our platform for personal, non-commercial transitory viewing only.</p>

                <h3>Disclaimer</h3>
                <p>The materials on our platform are provided on an 'as is' basis. We make no warranties, expressed or implied, and hereby disclaim and negate all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.</p>

                <h3>Limitations</h3>
                <p>In no event shall our company or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on our platform.</p>

                <h3>Accuracy of Materials</h3>
                <p>The materials appearing on our platform could include technical, typographical, or photographic errors. We do not warrant that any of the materials on our platform are accurate, complete, or current.</p>

                <h3>Links</h3>
                <p>We have not reviewed all of the sites linked to our platform and are not responsible for the contents of any such linked site. The inclusion of any link does not imply endorsement by us of the site. Use of any such linked website is at the user's own risk.</p>

                <h3>Modifications</h3>
                <p>We may revise these terms of service for our platform at any time without notice. By using this platform, you are agreeing to be bound by the then current version of these terms of service.</p>

                <h3>Governing Law</h3>
                <p>These terms and conditions are governed by and construed in accordance with the laws of the jurisdiction in which we operate, and you irrevocably submit to the exclusive jurisdiction of the courts in that location.</p>
                """,
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created default terms of service v1.0")
            )
        else:
            self.stdout.write(
                self.style.WARNING("✓ Terms of service v1.0 already exists")
            )

        self.stdout.write(
            self.style.SUCCESS("\n✓ Privacy policies and terms created successfully")
        )
