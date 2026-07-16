#!/usr/bin/env python3
"""
Script to update imports from apps.accounts to apps.accounts
"""

import os
import re
from pathlib import Path

#!/usr/bin/env python3
"""
Script to update imports from apps.accounts to apps.accounts
"""

import os
import re
from pathlib import Path


def update_file_imports(filepath):
    """Update imports in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update imports from apps.accounts to apps.accounts
    updated_content = content.replace('apps.accounts', 'apps.accounts')

    # Update imports from accounts. to accounts. (relative imports within the app)
    updated_content = updated_content.replace('from accounts.', 'from accounts.')
    updated_content = updated_content.replace('import accounts.', 'import accounts.')

    # Update app_label references
    updated_content = updated_content.replace("app_label = 'accounts'", "app_label = 'accounts'")
    updated_content = updated_content.replace('app_label="accounts"', 'app_label="accounts"')

    if content != updated_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    return False

def main():
    """Update all imports in the structa.cloud project."""
    project_dir = Path('structa.cloud')

    updated_files = []

    # First update accounts directory itself
    accounts_dir = project_dir / 'apps' / 'accounts'
    if accounts_dir.exists():
        for root, dirs, files in os.walk(accounts_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    if update_file_imports(filepath):
                        updated_files.append(str(filepath.relative_to(project_dir)))

    # Update all other files in the project
    for root, dirs, files in os.walk(project_dir):
        # Skip accounts directory (already handled)
        if 'apps/accounts' in root:
            continue

        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                if update_file_imports(filepath):
                    updated_files.append(str(filepath.relative_to(project_dir)))

    print(f"Updated {len(updated_files)} files:")
    for f in updated_files[:50]:  # Show first 50 files
        print(f"  - {f}")

    if len(updated_files) > 50:
        print(f"  ... and {len(updated_files) - 50} more files")

if __name__ == '__main__':
    main()

def update_file_imports(filepath):
    """Update imports in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update imports
    updated_content = content.replace('apps.accounts', 'apps.accounts')

    # Update class names if needed
    updated_content = updated_content.replace('AccountsConfig', 'AccountsConfig')

    if content != updated_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    return False

def main():
    """Update all imports in the accounts directory."""
    accounts_dir = Path('ctc-research.com/apps/accounts')

    updated_files = []

    for root, dirs, files in os.walk(accounts_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                if update_file_imports(filepath):
                    updated_files.append(str(filepath))

    # Also update imports in the main project
    project_dir = Path('ctc-research.com')
    for root, dirs, files in os.walk(project_dir):
        # Skip accounts directory (already handled)
        if 'apps/accounts' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                if update_file_imports(filepath):
                    updated_files.append(str(filepath))

    print(f"Updated {len(updated_files)} files:")
    for f in updated_files:
        print(f"  - {f}")

if __name__ == '__main__':
    main()
