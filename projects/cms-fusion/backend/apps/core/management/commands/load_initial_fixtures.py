"""
Django management command to load initial fixture data
Handles fixture loading with proper ordering and validation
"""

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django_fusion.site.management.commands.base import BaseCommand


class Command(BaseCommand):
    help = "Load initial fixture data in the correct order"
    
    # Define fixture loading order and dependencies
    FIXTURE_SEQUENCE = [
        {
            "name": "locales",
            "description": "Load language locales",
            "paths": [
                "assets/fixtures/production/just-locales.json",
                "assets/fixtures/test/locales.json",
            ],
            "required": True,
        },
        {
            "name": "users",
            "description": "Load user accounts",
            "paths": [
                "assets/fixtures/test/users.json",
            ],
            "required": False,
        },
        {
            "name": "pages",
            "description": "Load page data",
            "paths": [
                "assets/fixtures/test/pages.json",
                "assets/fixtures/production/cleaned-dump-data.json",
            ],
            "required": False,
        },
        {
            "name": "homepage_content",
            "description": "Load HomePage demo content (slider, features, about, CTA)",
            "paths": [
                "assets/fixtures/seed/homepage_content.json",
            ],
            "required": False,
        },
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--step",
            type=int,
            help="Load only a specific step (1, 2, 3, etc.)",
        )
        parser.add_argument(
            "--fixture",
            help="Load a specific fixture file",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available fixtures",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be loaded without loading",
        )
        parser.add_argument(
            "--skip-validation",
            action="store_true",
            help="Skip fixture validation",
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n🔧 Fixture Loading Manager\n"))
        
        if options["list"]:
            self.list_fixtures()
            return
        
        if options["fixture"]:
            self.load_specific_fixture(options["fixture"], options)
            return
        
        if options["step"]:
            self.load_step(options["step"], options)
            return
        
        # Default: load all
        self.load_all(options)
    
    def list_fixtures(self):
        """List all available fixtures"""
        self.stdout.write(self.style.HTTP_INFO("\n📋 Available Fixture Sequences:\n"))
        
        for i, step in enumerate(self.FIXTURE_SEQUENCE, 1):
            marker = "✅" if step["required"] else "ℹ️ "
            self.stdout.write(f"{marker} Step {i}: {step['description']}")
            self.stdout.write(f"   Paths: {', '.join(step['paths'])}\n")
    
    def load_specific_fixture(self, fixture_name, options):
        """Load a specific fixture file"""
        self.stdout.write(f"\n📥 Loading specific fixture: {fixture_name}\n")
        
        from tests.scripts.manage_fixtures import FixtureManager
        
        fpath = FixtureManager.get_fixture_path(fixture_name)
        if not fpath:
            raise CommandError(f"Fixture not found: {fixture_name}")
        
        self.stdout.write(f"Path: {fpath}")
        
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("DRY RUN - Not actually loading"))
            return
        
        try:
            call_command(
                "loaddata",
                str(fpath),
                verbosity=2 if options["verbosity"] > 1 else 1,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded {fixture_name}"))
        except Exception as e:
            raise CommandError(f"Failed to load fixture: {e}")
    
    def load_step(self, step_num, options):
        """Load a specific step"""
        if step_num < 1 or step_num > len(self.FIXTURE_SEQUENCE):
            raise CommandError(f"Invalid step: {step_num}. Available: 1-{len(self.FIXTURE_SEQUENCE)}")
        
        step = self.FIXTURE_SEQUENCE[step_num - 1]
        self.stdout.write(f"\n📥 Loading Step {step_num}: {step['description']}\n")
        
        self.load_fixture_step(step, options)
    
    def load_all(self, options):
        """Load all fixtures in order"""
        self.stdout.write(self.style.HTTP_INFO("📥 Loading all fixtures in sequence\n"))
        
        loaded = 0
        skipped = 0
        
        for i, step in enumerate(self.FIXTURE_SEQUENCE, 1):
            try:
                result = self.load_fixture_step(step, options, step_num=i)
                if result:
                    loaded += 1
                else:
                    skipped += 1
            except Exception as e:
                if step["required"]:
                    raise CommandError(f"Failed to load required step {i}: {e}")
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️  Skipped step {i}: {e}"))
                    skipped += 1
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Loaded: {loaded}, Skipped: {skipped}\n"))
    
    def load_fixture_step(self, step, options, step_num=None):
        """Load fixtures for a step"""
        step_label = f"Step {step_num}: " if step_num else ""
        
        self.stdout.write(f"\n{step_label}{step['description']}")
        
        for fpath_str in step["paths"]:
            fpath = Path(fpath_str)
            
            # Handle relative paths from project root
            if not fpath.is_absolute():
                import django
                from django.conf import settings
                
                # Try relative to settings module
                project_root = Path(settings.BASE_DIR).parent.parent
                fpath = project_root / fpath_str
            
            if not fpath.exists():
                self.stdout.write(f"  ⏭️  Not found: {fpath}")
                continue
            
            if options["dry_run"]:
                size = fpath.stat().st_size / 1024
                self.stdout.write(f"  📄 Would load: {fpath.name} ({size:.1f}KB)")
                return False
            
            try:
                self.stdout.write(f"  📥 Loading: {fpath.name}...", ending="")
                call_command(
                    "loaddata",
                    str(fpath),
                    verbosity=0,
                )
                self.stdout.write(self.style.SUCCESS(" ✅"))
                return True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f" ❌ {str(e)[:50]}"))
                continue
        
        return False
    
    @staticmethod
    def _format_size(size_bytes):
        """Format bytes as human readable"""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}GB"
