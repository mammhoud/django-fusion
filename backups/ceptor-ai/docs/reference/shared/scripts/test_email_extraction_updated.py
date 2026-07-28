#!/usr/bin/env python3
"""
Test script for updated email extraction with source_spec field.
"""
import csv
import re
from datetime import datetime, timezone
from pathlib import Path

# Email regex pattern
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def extract_emails_from_file(filepath):
    """Extract emails from a single file."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        emails = EMAIL_RE.findall(text)
        return list(dict.fromkeys(emails))  # Deduplicate
    except OSError:
        return []


def extract_emails_from_directory(directory, extensions=(".md", ".txt", ".rst")):
    """Extract emails from all matching files in directory with source_spec."""
    results = []
    for ext in extensions:
        for filepath in sorted(directory.rglob(f"*{ext}")):
            # Extract spec name from path
            parts = filepath.parts
            source_spec = ""
            try:
                if len(parts) >= 2:
                    source_spec = parts[-2]  # Parent directory name
            except (IndexError, AttributeError):
                source_spec = ""

            for email in extract_emails_from_file(filepath):
                results.append({
                    "email": email.lower(),
                    "source_file": str(filepath),
                    "source_spec": source_spec
                })
    return results


def write_csv(csv_path, rows):
    """Write emails to CSV file with source_spec."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    # Deduplicate by email
    unique = {}
    ts = datetime.now(timezone.utc).isoformat()

    for row in rows:
        email = row["email"]
        if email not in unique:
            unique[email] = {
                "email": email,
                "source_spec": row["source_spec"],
                "source_file": row["source_file"],
                "extracted_at": ts
            }

    # Write to CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["email", "source_spec", "source_file", "extracted_at"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique.values())

    return len(unique)


def test_email_extraction():
    """Test email extraction with source_spec field."""
    print("=" * 70)
    print("Testing Email Extraction System (Updated with source_spec)")
    print("=" * 70)

    # Test 1: Extract from .kiro/specs-organized
    print("\n1. Testing extraction from .kiro/specs-organized...")
    spec_dir = Path(".kiro/specs-organized")

    if not spec_dir.exists():
        print(f"   ❌ Directory not found: {spec_dir}")
        return False

    print(f"   ✓ Directory found: {spec_dir}")

    # Extract emails
    print("\n2. Extracting emails with source_spec...")
    emails_found = extract_emails_from_directory(spec_dir)
    print(f"   ✓ Found {len(emails_found)} email occurrences")

    # Show sample emails with source_spec
    if emails_found:
        print("\n3. Sample extracted emails with source_spec:")
        unique_emails = {}
        for item in emails_found:
            email = item['email']
            if email not in unique_emails:
                unique_emails[email] = item

        print(f"   ✓ Total unique emails: {len(unique_emails)}")

        for i, (email, data) in enumerate(list(unique_emails.items())[:10], 1):
            print(f"   {i}. {email}")
            print(f"      Spec: {data['source_spec']}")
            source_short = data['source_file'].replace(str(spec_dir), "...")
            print(f"      File: {source_short}")

    # Test 2: Write to CSV
    print("\n4. Writing to CSV with source_spec field...")
    csv_path = Path(".kiro/specs/email-list.csv")
    count = write_csv(csv_path, emails_found)
    print(f"   ✓ Wrote {count} unique emails to CSV")

    # Verify CSV was created with correct fields
    if csv_path.exists():
        print(f"\n5. CSV file created successfully:")
        print(f"   ✓ Path: {csv_path}")
        print(f"   ✓ Size: {csv_path.stat().st_size} bytes")

        # Read and verify fields
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Check fieldnames
            if reader.fieldnames:
                print(f"   ✓ Fields: {', '.join(reader.fieldnames)}")
                expected = ["email", "source_spec", "source_file", "extracted_at"]
                if list(reader.fieldnames) == expected:
                    print(f"   ✓ All required fields present")
                else:
                    print(f"   ⚠ Field mismatch. Expected: {expected}")

        print(f"   ✓ Total rows in CSV: {len(rows)}")

        if rows:
            print("\n   First 5 entries:")
            for i, row in enumerate(rows[:5], 1):
                print(f"   {i}. {row.get('email', 'N/A')}")
                print(f"      Spec: {row.get('source_spec', 'N/A')}")
                source_short = row.get('source_file', '').replace('.kiro/specs-organized/', '...')
                print(f"      File: {source_short}")
    else:
        print(f"\n   ❌ CSV file not created: {csv_path}")
        return False

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print(f"\n📧 Email list saved to: {csv_path.absolute()}")
    return True


if __name__ == "__main__":
    try:
        success = test_email_extraction()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
