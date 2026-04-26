import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sync essential files from structa to xellent-site'

    def handle(self, *args, **options):
        # Base directories
        research_dir = "/root/site/structa"
        xellent_dir = "/root/site/xellent-site"

        # List of files to sync (relative to project root)
        files_to_sync = [
            "apps/handlers/snippets/manage/peoples.py",
            "apps/pages/wagtail_hooks.py",
            "components/content/media/gallery.html",
            "assets/templates/layout/landing/footer.html",
        ]

        self.stdout.write(self.style.NOTICE(f"🔄 Starting sync from {research_dir} to {xellent_dir}..."))

        synced_count = 0
        for file_path in files_to_sync:
            src = os.path.join(research_dir, file_path)
            dst = os.path.join(xellent_dir, file_path)

            if os.path.exists(src):
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dst), exist_ok=True)

                # Copy the file
                shutil.copy2(src, dst)
                self.stdout.write(self.style.SUCCESS(f'  ✅ Synced: {file_path}'))
                synced_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Source not found: {file_path}'))

        self.stdout.write(self.style.SUCCESS(f"\n✨ Sync completed! Total files synced: {synced_count}"))
