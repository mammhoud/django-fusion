#!/usr/bin/env python
"""
Fixture Management Script
Handles loading, organizing, and managing fixture data for CTC-Research
"""

import os
import sys
import json
from pathlib import Path
from enum import Enum

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class FixtureType(Enum):
    """Fixture categories"""
    ORIGINAL = "original"      # Original/archive dumps
    CLEANED = "cleaned"         # Cleaned/filtered versions
    PRODUCTION = "production"   # Production-ready fixtures
    TEST = "test"               # Test fixtures
    ACTIVE = "."                # Currently active (root)


class FixtureManager:
    """Manage fixture files and operations"""
    
    FIXTURES_ROOT = Path(__file__).parent.parent.parent / "assets" / "fixtures"
    
    FIXTURE_PATHS = {
        FixtureType.ORIGINAL: FIXTURES_ROOT / "original",
        FixtureType.CLEANED: FIXTURES_ROOT / "cleaned",
        FixtureType.PRODUCTION: FIXTURES_ROOT / "production",
        FixtureType.TEST: FIXTURES_ROOT / "test",
        FixtureType.ACTIVE: FIXTURES_ROOT,
    }
    
    FIXTURE_DESCRIPTIONS = {
        # Production ready
        "just-locales.json": {
            "type": FixtureType.PRODUCTION,
            "description": "6 language locale records (RECOMMENDED FOR LOADING)",
            "models": ["wagtailcore.locale"],
            "objects": 6,
        },
        "cleaned-dump-data.json": {
            "type": FixtureType.PRODUCTION,
            "description": "Cleaned dump with valid content types only",
            "models": ["wagtailcore.page", "wagtailcore.locale", "wagtailimages.image"],
            "objects": 594,
        },
        
        # Cleaned/processed
        "filtered-dump-data.json": {
            "type": FixtureType.CLEANED,
            "description": "Filtered to wagtail-only models",
            "models": ["wagtailcore.*"],
            "objects": 665,
        },
        "essential-data.json": {
            "type": FixtureType.CLEANED,
            "description": "Essential data (locales, users, images)",
            "models": ["wagtailcore.locale", "auth.*", "wagtailimages.*"],
            "objects": 91,
        },
        
        # Test/staging
        "locales.json": {
            "type": FixtureType.TEST,
            "description": "Test locale records",
            "models": ["wagtailcore.locale"],
            "objects": 7,
        },
        "pages.json": {
            "type": FixtureType.TEST,
            "description": "Test page records",
            "models": ["wagtailcore.page"],
            "objects": 73,
        },
        "users.json": {
            "type": FixtureType.TEST,
            "description": "Test user records",
            "models": ["auth.user"],
            "objects": 6,
        },
        "core-data.json": {
            "type": FixtureType.TEST,
            "description": "Core data (pages, locales, users)",
            "models": ["wagtailcore.*", "auth.*"],
            "objects": 266,
        },
        "initial_choices.json": {
            "type": FixtureType.TEST,
            "description": "Initial choices/options",
            "models": ["*"],
            "objects": 7,
        },
        
        # Original/Archive
        "wagtail_pages_dump.json": {
            "type": FixtureType.ORIGINAL,
            "description": "Original Wagtail pages dump",
            "models": ["wagtailcore.page"],
            "objects": "unknown",
        },
        "ctc-research-data.json": {
            "type": FixtureType.ORIGINAL,
            "description": "Original CTC-Research data dump",
            "models": ["*"],
            "objects": "unknown",
        },
        
        # Active/Root
        "dump-data.json": {
            "type": FixtureType.ACTIVE,
            "description": "Main fixture dump (original source)",
            "models": ["*"],
            "objects": 1015,
        },
    }
    
    @classmethod
    def list_fixtures(cls, fixture_type=None, verbose=False):
        """List available fixtures"""
        print("\n📋 Available Fixtures\n")
        print("=" * 80)
        
        for fname, info in cls.FIXTURE_DESCRIPTIONS.items():
            ftype = info["type"]
            
            # Filter by type if specified
            if fixture_type and ftype != fixture_type:
                continue
            
            # Find actual file
            fpath = cls.FIXTURE_PATHS[ftype] / fname
            if not fpath.exists():
                fpath = cls.FIXTURES_ROOT / fname
            
            if not fpath.exists():
                continue
            
            # Get file size
            size = fpath.stat().st_size
            size_str = cls._format_size(size)
            
            print(f"\n📁 {ftype.value.upper()}")
            print(f"   📄 {fname}")
            print(f"      Size: {size_str}")
            print(f"      Models: {', '.join(info['models'])}")
            print(f"      Objects: {info['objects']}")
            print(f"      Description: {info['description']}")
            
            if verbose:
                print(f"      Path: {fpath}")
        
        print("\n" + "=" * 80)
    
    @classmethod
    def show_structure(cls):
        """Show directory structure"""
        print("\n📁 Fixtures Directory Structure\n")
        print("=" * 80)
        
        for ftype in FixtureType:
            fdir = cls.FIXTURE_PATHS[ftype]
            if not fdir.exists():
                continue
            
            files = list(fdir.glob("*.json"))
            if not files:
                continue
            
            print(f"\n📂 {ftype.value}/")
            for fpath in sorted(files):
                size = cls._format_size(fpath.stat().st_size)
                print(f"   • {fpath.name:40} ({size:>10})")
        
        print("\n" + "=" * 80)
    
    @classmethod
    def get_fixture_path(cls, fixture_name):
        """Get full path for a fixture file"""
        # Check all locations
        for ftype in FixtureType:
            fpath = cls.FIXTURE_PATHS[ftype] / fixture_name
            if fpath.exists():
                return fpath
        
        # Try root
        fpath = cls.FIXTURES_ROOT / fixture_name
        if fpath.exists():
            return fpath
        
        return None
    
    @classmethod
    def get_recommended_load_order(cls):
        """Get recommended fixture loading order"""
        return [
            "production/just-locales.json",          # Step 1: Locales
            "test/users.json",                       # Step 2: Users
            # "production/cleaned-dump-data.json",  # Step 3: Other data
        ]
    
    @classmethod
    def show_by_model_organization(cls):
        """Show by-model fixture organization"""
        by_model_dir = cls.FIXTURES_ROOT / "by-model"
        
        if not by_model_dir.exists():
            print("\n⚠️  by-model/ directory not found. Run with --organize to create it.\n")
            return
        
        print("\n📁 Fixtures Organized by Model\n")
        print("=" * 80)
        
        # Try to load INDEX.json
        index_file = by_model_dir / "INDEX.json"
        if index_file.exists():
            try:
                with open(index_file) as f:
                    index = json.load(f)
                
                for model_type in sorted(index.get("models", {}).keys()):
                    files = index["models"][model_type]
                    total_items = sum(f["items"] for f in files)
                    total_size = sum(f["size"] for f in files)
                    
                    print(f"\n📂 {model_type}/")
                    print(f"   Files: {len(files)}")
                    print(f"   Items: {total_items}")
                    print(f"   Size: {cls._format_size(total_size)}")
                    
                    for f in sorted(files, key=lambda x: x["file"]):
                        print(f"   • {f['file']:45} ({f['items']:4} items, {cls._format_size(f['size']):>10})")
            except Exception as e:
                print(f"Error reading INDEX.json: {e}")
        
        print("\n" + "=" * 80)
    
    @classmethod
    def show_model_fixtures(cls, model_name):
        """Show fixtures for a specific model"""
        by_model_dir = cls.FIXTURES_ROOT / "by-model"
        model_dir = by_model_dir / model_name
        
        if not model_dir.exists():
            print(f"\n❌ Model '{model_name}' not found in by-model/\n")
            print("Available models:")
            for d in sorted(by_model_dir.iterdir()):
                if d.is_dir() and d.name != ".":
                    print(f"  • {d.name}")
            print()
            return
        
        print(f"\n📂 Fixtures for model: {model_name}\n")
        print("=" * 80)
        
        for fixture_file in sorted(model_dir.glob("*.json")):
            try:
                with open(fixture_file) as f:
                    data = json.load(f)
                
                item_count = len(data) if isinstance(data, list) else 1
                size = fixture_file.stat().st_size
                
                print(f"\n📄 {fixture_file.name}")
                print(f"   Items: {item_count}")
                print(f"   Size: {cls._format_size(size)}")
                
                # Show first item as example
                if isinstance(data, list) and data:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        print(f"   Model: {first_item.get('model', 'N/A')}")
                        print(f"   PK: {first_item.get('pk', 'N/A')}")
            except Exception as e:
                print(f"   Error: {e}")
        
        print("\n" + "=" * 80)
    
    @staticmethod
    def _format_size(size_bytes):
        """Format bytes as human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage CTC-Research fixture data")
    parser.add_argument("--list", action="store_true", help="List all available fixtures")
    parser.add_argument("--structure", action="store_true", help="Show directory structure")
    parser.add_argument("--by-model", action="store_true", help="Show by-model organization")
    parser.add_argument("--type", choices=[t.value for t in FixtureType], help="Filter by type")
    parser.add_argument("--model", help="Show fixtures for a specific model (e.g., wagtailcore)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--path", help="Get path for a fixture")
    parser.add_argument("--recommended", action="store_true", help="Show recommended load order")
    parser.add_argument("--organize", action="store_true", help="Organize fixtures by model (runs script)")
    
    args = parser.parse_args()
    
    # Default: show structure
    if not any([args.list, args.structure, args.path, args.recommended, args.by_model, args.organize, args.model]):
        args.structure = True
    
    if args.structure:
        FixtureManager.show_structure()
    
    if args.by_model:
        FixtureManager.show_by_model_organization()
    
    if args.model:
        FixtureManager.show_model_fixtures(args.model)
    
    if args.list:
        fixture_type = FixtureType(args.type) if args.type else None
        FixtureManager.list_fixtures(fixture_type, args.verbose)
    
    if args.path:
        fpath = FixtureManager.get_fixture_path(args.path)
        if fpath:
            print(fpath)
        else:
            print(f"Fixture not found: {args.path}", file=sys.stderr)
            sys.exit(1)
    
    if args.recommended:
        print("\n📋 Recommended Fixture Loading Order\n")
        for i, fixture in enumerate(FixtureManager.get_recommended_load_order(), 1):
            print(f"{i}. {fixture}")
        print()
    
    if args.organize:
        print("\n🔧 Running fixture organizer...\n")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "organize_fixtures_by_model.py")],
            cwd=str(Path(__file__).parent.parent.parent)
        )
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
