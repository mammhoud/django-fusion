#!/usr/bin/env python
"""
Organize fixture files by model type
Separates mixed fixtures into model-specific subdirectories
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


class FixtureOrganizer:
    """Organize fixtures by model type"""
    
    FIXTURES_ROOT = Path(__file__).parent.parent.parent / "assets" / "fixtures"
    
    # Main model categories
    MODEL_CATEGORIES = {
        # Wagtail Core
        "wagtailcore": ["page", "locale", "site", "revision", "pagelogentry", "modellogentry", "groupapprovaltask"],
        
        # Wagtail Images
        "wagtailimages": ["image", "rendition"],
        
        # Wagtail Forms
        "wagtailforms": ["form", "formsubmission"],
        
        # Wagtail Docs
        "wagtaildocs": ["document"],
        
        # Auth
        "auth": ["user", "group", "permission"],
        
        # Django Core
        "django_contrib_contenttypes": ["contenttype"],
        "django_contrib_sessions": ["session"],
        "django_contrib_sites": ["site"],
        
        # Tagging
        "taggit": ["tag", "taggeditem"],
        
        # App Models
        "pages": ["homepage", "aboutpage", "contactpage", "teampage", "eventpage", "servicespage"],
        "lms": ["coursespage", "course", "enrollment"],
        "modules": ["activitytype", "statuschoice"],
    }
    
    def __init__(self):
        self.fixtures_by_model = defaultdict(list)
        self.models_seen = set()
    
    def analyze_fixture(self, filepath):
        """Analyze a fixture file and extract models"""
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return []
            
            models = set()
            for item in data:
                if isinstance(item, dict) and "model" in item:
                    models.add(item["model"])
            
            return sorted(models)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            return []
    
    def get_model_category(self, model_name):
        """Get category for a model"""
        if not model_name or "." not in model_name:
            return "other"
        
        app, name = model_name.split(".", 1)
        
        for category, models in self.MODEL_CATEGORIES.items():
            if category == app or any(m in model_name for m in models):
                return category
        
        return app
    
    def create_model_directories(self):
        """Create directories for each model category"""
        print("\n📁 Creating model-based directories...\n")
        
        model_dirs = set()
        
        # Scan all fixtures to find all models
        for fixture_file in self.FIXTURES_ROOT.rglob("*.json"):
            if fixture_file.name == "README.md":
                continue
            
            models = self.analyze_fixture(fixture_file)
            for model in models:
                category = self.get_model_category(model)
                model_dirs.add(category)
        
        # Create directories
        for model_dir in sorted(model_dirs):
            dirpath = self.FIXTURES_ROOT / "by-model" / model_dir
            dirpath.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: by-model/{model_dir}/")
        
        return sorted(model_dirs)
    
    def separate_fixture_files(self, model_dirs):
        """Separate mixed fixture files by model"""
        print("\n📊 Separating fixtures by model...\n")
        
        total_separated = 0
        
        # Process each fixture file
        fixture_files = list(self.FIXTURES_ROOT.glob("production/*.json")) + \
                       list(self.FIXTURES_ROOT.glob("test/*.json")) + \
                       list(self.FIXTURES_ROOT.glob("cleaned/*.json")) + \
                       list(self.FIXTURES_ROOT.glob("original/*.json"))
        
        for fixture_file in fixture_files:
            try:
                with open(fixture_file) as f:
                    all_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue
            
            if not isinstance(all_data, list):
                continue
            
            # Group by model
            data_by_model = defaultdict(list)
            for item in all_data:
                if isinstance(item, dict) and "model" in item:
                    model = item["model"]
                    data_by_model[model].append(item)
            
            # If multiple models, separate them
            if len(data_by_model) > 1:
                print(f"📄 {fixture_file.name}: {len(data_by_model)} model types")
                
                for model, items in sorted(data_by_model.items()):
                    category = self.get_model_category(model)
                    
                    # Create filename based on model
                    model_file = model.replace(".", "-") + ".json"
                    output_path = self.FIXTURES_ROOT / "by-model" / category / model_file
                    
                    # Write separated fixture
                    with open(output_path, "w") as f:
                        json.dump(items, f, indent=2)
                    
                    print(f"   → {category}/{model_file} ({len(items)} items)")
                    total_separated += len(items)
                    self.models_seen.add(model)
        
        print(f"\n✅ Separated {total_separated} items across models")
    
    def create_index_file(self):
        """Create index of organized fixtures"""
        print("\n📋 Creating index file...\n")
        
        index = {
            "organized": True,
            "structure": "by-model",
            "description": "Fixtures separated by model type",
            "models": {}
        }
        
        # Scan organized directories
        for model_dir in (self.FIXTURES_ROOT / "by-model").iterdir():
            if not model_dir.is_dir():
                continue
            
            category = model_dir.name
            index["models"][category] = []
            
            for fixture_file in sorted(model_dir.glob("*.json")):
                try:
                    with open(fixture_file) as f:
                        data = json.load(f)
                    
                    item_count = len(data) if isinstance(data, list) else 1
                    
                    index["models"][category].append({
                        "file": fixture_file.name,
                        "items": item_count,
                        "size": fixture_file.stat().st_size,
                    })
                except Exception as e:
                    print(f"Error processing {fixture_file}: {e}", file=sys.stderr)
        
        # Write index
        index_path = self.FIXTURES_ROOT / "by-model" / "INDEX.json"
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
        
        print(f"✅ Created: by-model/INDEX.json")
        
        return index
    
    def print_summary(self, index):
        """Print organization summary"""
        print("\n" + "=" * 80)
        print("📊 FIXTURE ORGANIZATION SUMMARY")
        print("=" * 80 + "\n")
        
        for category in sorted(index["models"].keys()):
            files = index["models"][category]
            total_items = sum(f["items"] for f in files)
            total_size = sum(f["size"] for f in files)
            
            print(f"📁 {category}/")
            print(f"   Files: {len(files)}")
            print(f"   Items: {total_items}")
            print(f"   Size: {self._format_size(total_size)}")
            
            for f in files:
                print(f"   • {f['file']:40} ({f['items']:4} items, {self._format_size(f['size']):>10})")
            print()
        
        total_items = sum(sum(f["items"] for f in index["models"][c]) 
                         for c in index["models"])
        print(f"✅ Total: {total_items} items organized across {len(index['models'])} categories\n")
    
    @staticmethod
    def _format_size(size_bytes):
        """Format bytes as human readable"""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024:
                return f"{size_bytes:.0f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}GB"
    
    def organize(self):
        """Run full organization"""
        print("\n🔧 FIXTURE ORGANIZATION BY MODEL\n")
        print("=" * 80)
        
        # Step 1: Create directories
        model_dirs = self.create_model_directories()
        
        # Step 2: Separate fixtures
        self.separate_fixture_files(model_dirs)
        
        # Step 3: Create index
        index = self.create_index_file()
        
        # Step 4: Print summary
        self.print_summary(index)
        
        print("=" * 80)
        print("✅ ORGANIZATION COMPLETE\n")


def main():
    """Main entry point"""
    organizer = FixtureOrganizer()
    organizer.organize()


if __name__ == "__main__":
    main()
