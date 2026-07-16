#!/usr/bin/env python3
"""
Clean Migrations Script

This script removes all migration files except core migrations,
then regenerates clean migrations for both websites.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return result."""
    print(f"Running: {' '.join(cmd)} in {cwd or 'current directory'}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True


def clean_migrations(website_path):
    """Clean migrations for a website, keeping only core migrations."""
    website_path = Path(website_path)
    print(f"\n{'='*60}")
    print(f"Cleaning migrations for {website_path.name}")
    print(f"{'='*60}")

    # Find all app migration directories
    apps_dir = website_path / "apps"
    if apps_dir.exists():
        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir():
                migrations_dir = app_dir / "migrations"
                if migrations_dir.exists():
                    print(f"Cleaning migrations in {migrations_dir}")
                    # Keep __init__.py, remove everything else
                    for migration_file in migrations_dir.iterdir():
                        if migration_file.name != "__init__.py" and migration_file.name != "__pycache__":
                            if migration_file.is_file():
                                migration_file.unlink()
                                print(f"  Removed: {migration_file.name}")
                            elif migration_file.is_dir():
                                shutil.rmtree(migration_file)
                                print(f"  Removed directory: {migration_file.name}")

    # Also check for other app directories at root level
    for item in website_path.iterdir():
        if item.is_dir() and item.name not in ["core", "configs", "static", "media", "templates", ".venv", "__pycache__", ".git", "node_modules"]:
            migrations_dir = item / "migrations"
            if migrations_dir.exists():
                print(f"Cleaning migrations in {migrations_dir}")
                for migration_file in migrations_dir.iterdir():
                    if migration_file.name != "__init__.py" and migration_file.name != "__pycache__":
                        if migration_file.is_file():
                            migration_file.unlink()
                            print(f"  Removed: {migration_file.name}")
                        elif migration_file.is_dir():
                            shutil.rmtree(migration_file)
                            print(f"  Removed directory: {migration_file.name}")


def regenerate_migrations(website_path):
    """Regenerate migrations for a website."""
    website_path = Path(website_path)
    print(f"\n{'='*60}")
    print(f"Regenerating migrations for {website_path.name}")
    print(f"{'='*60}")

    # Make migrations
    if not run_command(["python", "manage.py", "makemigrations"], cwd=website_path):
        print(f"Failed to make migrations for {website_path.name}")
        return False

    # Apply migrations
    if not run_command(["python", "manage.py", "migrate"], cwd=website_path):
        print(f"Failed to apply migrations for {website_path.name}")
        return False

    return True


def main():
    """Main function."""
    websites = ["ctc-research.com", "structa.cloud"]

    print("🧹 Starting migration cleanup and regeneration...")

    for website in websites:
        website_path = Path(website)
        if not website_path.exists():
            print(f"Warning: {website} directory not found, skipping...")
            continue

        # Clean migrations
        clean_migrations(website_path)

        # Regenerate migrations
        if not regenerate_migrations(website_path):
            print(f"Failed to regenerate migrations for {website}")
            return 1

    print("\n✅ Migration cleanup and regeneration completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
