"""
Django management command to build static assets.

This command runs webpack bundling and Django collectstatic to prepare
static files for deployment.

Usage:
    python manage.py build_assets                    # Run full build (webpack + collectstatic)
    python manage.py build_assets --webpack-only     # Run only webpack
    python manage.py build_assets --collectstatic-only  # Run only collectstatic
    python manage.py build_assets --production       # Production build (default)
    python manage.py build_assets --watch            # Watch mode (development)
    python manage.py build_assets --no-input         # Non-interactive mode
"""

import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Build static assets using webpack and collectstatic."""

    help = "Build static assets: run webpack bundling and Django collectstatic"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--webpack-only",
            action="store_true",
            help="Run only webpack bundling, skip collectstatic",
        )
        parser.add_argument(
            "--collectstatic-only",
            action="store_true",
            help="Run only Django collectstatic, skip webpack",
        )
        parser.add_argument(
            "--production",
            action="store_true",
            default=True,
            help="Run production build (minified, optimized)",
        )
        parser.add_argument(
            "--development",
            action="store_true",
            help="Run development build (not minified)",
        )
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Run webpack in watch mode (development only)",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Run in non-interactive mode (skip confirmations)",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean bundles directory before building",
        )

    def handle(self, *args, **options):
        """Run the asset build process."""
        webpack_only = options["webpack_only"]
        collectstatic_only = options["collectstatic_only"]
        production = options["production"]
        development = options["development"]
        watch = options["watch"]
        no_input = options["no_input"]
        clean = options["clean"]

        # Determine build mode
        if development:
            production = False

        # Get project root (parent of www/)
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        webpack_config = project_root / "webpack"
        static_root = Path(settings.STATIC_ROOT)

        self.stdout.write(
            self.style.SUCCESS(f"Project root: {project_root}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Static root: {static_root}")
        )

        # Step 1: Clean if requested
        if clean and not collectstatic_only:
            self._clean_bundles(static_root)

        # Step 2: Run webpack
        if not collectstatic_only:
            self._run_webpack(
                project_root=project_root,
                production=production,
                watch=watch,
            )

        # Step 3: Run collectstatic
        if not webpack_only:
            self._run_collectstatic(no_input=no_input)

        self.stdout.write(
            self.style.SUCCESS("✓ Asset build completed successfully!")
        )

    def _clean_bundles(self, static_root: Path):
        """Clean the bundles directory."""
        bundles_dir = static_root.parent / "bundles"
        if bundles_dir.exists():
            self.stdout.write(f"Cleaning bundles directory: {bundles_dir}")
            import shutil

            try:
                shutil.rmtree(bundles_dir)
                self.stdout.write(self.style.SUCCESS("✓ Bundles directory cleaned"))
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Could not clean bundles: {e}")
                )
        else:
            self.stdout.write("Bundles directory does not exist, skipping clean")

    def _run_webpack(
        self,
        project_root: Path,
        production: bool = True,
        watch: bool = False,
    ):
        """Run webpack bundling."""
        self.stdout.write("")
        self.stdout.write(
            self.style.HTTP_INFO("=" * 50)
        )
        self.stdout.write(
            self.style.HTTP_INFO("Running webpack...")
        )

        # Determine npm script
        if watch:
            npm_script = "watch"
            self.stdout.write(self.style.WARNING("Running in watch mode (Ctrl+C to stop)"))
        elif production:
            npm_script = "build:prod"
        else:
            npm_script = "build:dev"

        self.stdout.write(f"Running npm script: {npm_script}")

        try:
            # Run npm script
            result = subprocess.run(
                ["npm", "run", npm_script],
                cwd=str(project_root),
                capture_output=False,
                text=True,
            )

            if result.returncode != 0:
                raise CommandError(f"Webpack failed with return code {result.returncode}")

            self.stdout.write(self.style.SUCCESS("✓ Webpack build completed"))

        except FileNotFoundError:
            raise CommandError(
                "npm not found. Please ensure Node.js and npm are installed."
            )
        except subprocess.CalledProcessError as e:
            raise CommandError(f"Webpack failed: {e}")

    def _run_collectstatic(self, no_input: bool = False):
        """Run Django collectstatic."""
        self.stdout.write("")
        self.stdout.write(
            self.style.HTTP_INFO("=" * 50)
        )
        self.stdout.write(
            self.style.HTTP_INFO("Running Django collectstatic...")
        )

        # Build collectstatic command
        cmd = [
            sys.executable,
            "manage.py",
            "collectstatic",
            "--no-progress",
        ]

        if no_input:
            cmd.append("--no-input")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(Path(__file__).resolve().parent.parent.parent.parent.parent),
                capture_output=False,
                text=True,
            )

            if result.returncode != 0:
                raise CommandError(
                    f"collectstatic failed with return code {result.returncode}"
                )

            self.stdout.write(self.style.SUCCESS("✓ Collectstatic completed"))

        except subprocess.CalledProcessError as e:
            raise CommandError(f"collectstatic failed: {e}")
