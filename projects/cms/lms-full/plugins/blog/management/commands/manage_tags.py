"""
Management command for managing blog tags.
"""

from django.core.management.base import BaseCommand
from django_fusion.management.commands.base import BaseCommand

from plugins.blog.models import BlogTag
from plugins.blog.services import TagService


class Command(BaseCommand):
    """Management command for blog tag operations."""

    help = "Manage blog tags: list, create, delete, merge, and cleanup unused tags"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            nargs="?",
            choices=["list", "create", "delete", "merge", "cleanup"],
            default="list",
            help="Action to perform",
        )
        parser.add_argument("--name", help="Tag name")
        parser.add_argument("--slug", help="Tag slug")
        parser.add_argument("--from-tag", help="Source tag for merge")
        parser.add_argument("--to-tag", help="Target tag for merge")

    def handle(self, *args, **options):
        action = options.get("action", "list")
        if action == "list":
            self.list_tags()
        elif action == "create":
            self.create_tag(options.get("name"), options.get("slug"))
        elif action == "delete":
            self.delete_tag(options.get("name"))
        elif action == "merge":
            self.merge_tags(options.get("from-tag"), options.get("to-tag"))
        elif action == "cleanup":
            count = self.list_unused_tags()
            self.stdout.write(f"Found {count} unused tags")

    def list_tags(self):
        """List all blog tags."""
        tags = BlogTag.objects.all().order_by("name")
        for tag in tags:
            self.stdout.write(f"  {tag.name} ({tag.slug})")
        return tags

    def create_tag(self, name, slug=None):
        """Create a new blog tag."""
        if not name:
            self.stderr.write("Tag name is required")
            return None
        if not slug:
            slug = name.lower().replace(" ", "-")
        tag, created = BlogTag.objects.get_or_create(name=name, defaults={"slug": slug})
        if created:
            self.stdout.write(f"Created tag: {tag.name}")
        else:
            self.stdout.write(f"Tag already exists: {tag.name}")
        return tag

    def delete_tag(self, name):
        """Delete a blog tag by name."""
        if not name:
            self.stderr.write("Tag name is required")
            return
        try:
            tag = BlogTag.objects.get(name=name)
            tag.delete()
            self.stdout.write(f"Deleted tag: {name}")
        except BlogTag.DoesNotExist:
            self.stderr.write(f"Tag not found: {name}")

    def merge_tags(self, from_name, to_name):
        """Merge one tag into another."""
        if not from_name or not to_name:
            self.stderr.write("Both --from-tag and --to-tag are required")
            return
        try:
            old_tag = BlogTag.objects.get(name=from_name)
            new_tag = BlogTag.objects.get(name=to_name)
            TagService.merge_tags(old_tag, new_tag)
            self.stdout.write(f"Merged '{from_name}' into '{to_name}'")
        except BlogTag.DoesNotExist as e:
            self.stderr.write(f"Tag not found: {e}")

    def list_unused_tags(self):
        """List and return count of unused tags."""
        unused = BlogTag.objects.filter(posts__isnull=True)
        for tag in unused:
            self.stdout.write(f"  Unused: {tag.name}")
        return unused.count()
