#!/usr/bin/env python3
"""
Test script for email extraction functionality.
Tests the EmailExtractor and EmailCSVManager classes.
"""
import sys
from pathlib import Path

# Add libs to path
sys.path.insert(0, str(Path(__file__).parent / "libs" / "django-grep" / "src"))

from django_grep.email_tools.csv_manager import EmailCSVManager
from django_grep.email_tools.extractor import EmailExtractor


def test_email_extraction():
    """Test email extraction from spec directories."""
    print("=" * 70)
    print("Testing Email Extraction System")
    print("=" * 70)

    # Test 1: Extract from .kiro/specs-organized
    print("\n1. Testing extraction from .kiro/specs-organized...")
    spec_dir = Path(".kiro/specs-organized")

    if not spec_dir.exists():
        print(f"   ❌ Directory not found: {spec_dir}")
        return False

    print(f"   ✓ Directory found: {spec_dir}")

    # Initialize extractor
    extractor = EmailExtractor(extensions=(".md", ".txt", ".rst"))
    print(f"   ✓ EmailExtractor initialized with extensions: .md, .txt, .rst")

    # Extract emails
    print("\n2. Extracting emails...")
    emails_found = list(extractor.extract_from_directory(spec_dir))
    print(f"   ✓ Found {len(emails_found)} email occurrences")

    # Show sample emails
    if emails_found:
        print("\n3. Sample extracted emails:")
        unique_emails = {}
        for item in emails_found:
            email = item['email']
            if email not in unique_emails:
                unique_emails[email] = item['source_file']

        for i, (email, source) in enumerate(list(unique_emails.items())[:10], 1):
            print(f"   {i}. {email}")
            print(f"      Source: {source}")

    # Test 2: CSV Manager
    print("\n4. Testing CSV Manager...")
    csv_path = Path(".kiro/specs/email-list.csv")
    manager = EmailCSVManager(csv_path)
    print(f"   ✓ EmailCSVManager initialized with path: {csv_path}")

    # Merge emails
    print("\n5. Merging emails to CSV...")
    added = manager.merge(emails_found)
    print(f"   ✓ Added {added} new emails to CSV")
    print(f"   ✓ Total unique emails: {len(unique_emails)}")

    # Verify CSV was created
    if csv_path.exists():
        print(f"\n6. CSV file created successfully:")
        print(f"   ✓ Path: {csv_path}")
        print(f"   ✓ Size: {csv_path.stat().st_size} bytes")

        # Read and display first few lines
        rows = manager.read()
        print(f"   ✓ Total rows in CSV: {len(rows)}")

        if rows:
            print("\n   First 5 entries:")
            for i, row in enumerate(rows[:5], 1):
                print(f"   {i}. {row.get('email', 'N/A')}")
    else:
        print(f"\n   ❌ CSV file not created: {csv_path}")
        return False

    # Test 3: Check both project directories
    print("\n7. Checking project-specific spec directories...")

    ctc_specs = Path("ctc-research.com/.kiro/specs")
    structa_specs = Path("structa.cloud/.kiro/specs")

    for proj_dir in [ctc_specs, structa_specs]:
        if proj_dir.exists():
            print(f"   ✓ Found: {proj_dir}")
            proj_emails = list(extractor.extract_from_directory(proj_dir))
            print(f"     - Emails found: {len(proj_emails)}")
        else:
            print(f"   ℹ Not found: {proj_dir}")

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_email_extraction()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
