#!/usr/bin/env python3
"""
Validate synced files and create git commits for each phase.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List

TARGET_BASE = Path("structa.cloud")

PHASE_COMMITS = {
    "2.4": {
        "message": "sync: phase 2.4 - LMS enhancements",
        "files": [
            "apps/LMS/",
        ],
    },
    "2.5": {
        "message": "sync: phase 2.5 - CI/infrastructure",
        "files": [
            "docker-compose.yml",
            "docker-compose.override.yml",
            "docker-compose.test.yml",
            ".dockerignore",
        ],
    },
    "2.6": {
        "message": "sync: phase 2.6 - configuration",
        "files": [
            "configs/",
        ],
    },
    "2.7": {
        "message": "sync: phase 2.7 - testing infrastructure",
        "files": [
            "tests/",
        ],
    },
    "2.8": {
        "message": "sync: phase 2.8 - frontend & styling",
        "files": [
            "apps/templates/",
            "assets/",
        ],
    },
}


def validate_python_files(directory: Path) -> Dict:
    """Validate Python files in a directory."""
    results = {
        "total_files": 0,
        "valid_files": 0,
        "errors": [],
    }

    if not directory.exists():
        return results

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        results["total_files"] += 1

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(py_file), 'exec')
            results["valid_files"] += 1
        except SyntaxError as e:
            results["errors"].append(f"{py_file}: {e}")

    return results


def run_git_command(cmd: List[str], cwd: Path = None) -> bool:
    """Run a git command."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or TARGET_BASE,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running git command: {e}")
        return False


def create_commit(phase: str, config: Dict) -> bool:
    """Create a git commit for a phase."""
    print(f"\nCreating commit for Phase {phase}...")

    # Stage files
    for file_pattern in config["files"]:
        if not run_git_command(["git", "add", file_pattern]):
            print(f"  ⚠️  Failed to stage {file_pattern}")
            return False

    # Create commit
    if not run_git_command(["git", "commit", "-m", config["message"]]):
        print(f"  ⚠️  Failed to create commit (may be no changes)")
        return False

    print(f"  ✅ Commit created: {config['message']}")
    return True


def main():
    """Execute validation and commits."""
    print("=" * 70)
    print("VALIDATION AND COMMIT PHASE")
    print("=" * 70)

    # Validate Python files
    print("\nValidating Python files...")
    validation_results = {}

    for phase in ["2.4", "2.6", "2.7"]:  # Python phases
        if phase == "2.4":
            dir_to_validate = TARGET_BASE / "apps/LMS"
        elif phase == "2.6":
            dir_to_validate = TARGET_BASE / "configs"
        elif phase == "2.7":
            dir_to_validate = TARGET_BASE / "tests"

        result = validate_python_files(dir_to_validate)
        validation_results[phase] = result

        if result["total_files"] > 0:
            print(f"  Phase {phase}: {result['valid_files']}/{result['total_files']} files valid")
            if result["errors"]:
                print(f"    Errors: {len(result['errors'])}")
                for error in result["errors"][:3]:  # Show first 3 errors
                    print(f"      - {error}")

    # Create commits
    print("\n" + "=" * 70)
    print("CREATING GIT COMMITS")
    print("=" * 70)

    commits_created = 0
    for phase, config in PHASE_COMMITS.items():
        if create_commit(phase, config):
            commits_created += 1

    print(f"\n✅ Total commits created: {commits_created}/{len(PHASE_COMMITS)}")

    # Show git log
    print("\n" + "=" * 70)
    print("GIT COMMIT HISTORY")
    print("=" * 70)

    result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        cwd=TARGET_BASE,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)

    return commits_created == len(PHASE_COMMITS)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
