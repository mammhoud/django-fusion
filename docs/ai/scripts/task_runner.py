#!/usr/bin/env python3
"""
Task Runner – List, run, and interactively resolve AI tasks.
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Add parent of scripts to path to import utils
sys.path.insert(0, str(Path(__file__).parent))
from utils import TASKS_DIR, call_ollama, log_change, ENV

def list_tasks() -> List[str]:
    """Return list of task names (without .md extension)."""
    return [p.stem for p in TASKS_DIR.glob("*.md")]

def run_task(task_name: str, interactive: bool = False):
    """Load a task prompt, optionally ask user how to resolve, then run."""
    task_file = TASKS_DIR / f"{task_name}.md"
    if not task_file.exists():
        print(f"❌ Task '{task_name}' not found. Available: {', '.join(list_tasks())}")
        return
    task_prompt = task_file.read_text(encoding='utf-8')
    print(f"\n📄 Loaded task: {task_name}\n{'-'*40}")
    print(task_prompt[:500] + ("…" if len(task_prompt) > 500 else ""))
    
    if interactive:
        print("\nHow would you like to resolve this task?")
        print("1. Analyze only (no changes) – uses @docs and @search")
        print("2. Propose code changes – includes priority files and docs")
        print("3. Update documentation only")
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == '2':
            # Would need to call ai-customizer with --priority --with-docs
            cmd = f"ai-customizer task {task_name} --priority --with-docs"
            print(f"Running: {cmd}")
            # In a real script you'd subprocess.run(cmd, shell=True)
        elif choice == '3':
            cmd = f"ai-customizer task {task_name} --with-docs"
            print(f"Running: {cmd}")
        else:
            cmd = f"ai-customizer task {task_name}"
            print(f"Running: {cmd}")
        # For demo, we just call the same function without interactive flag
        # Real implementation would call subprocess or use call_ollama directly.
        # Here we simulate:
        print("\n🤖 AI Response (simulated):")
        print(call_ollama(task_prompt, system=ENV.get('SYSTEM_PROMPT', '')))
    else:
        # Non-interactive: just run the task directly
        response = call_ollama(task_prompt, system=ENV.get('SYSTEM_PROMPT', ''))
        print("\n🤖 AI Response:\n", response)
    log_change(f"Ran task '{task_name}'" + (" (interactive)" if interactive else ""))

def sync_website(site: str):
    """Example sync: copy auth.py from ctc-research to target site."""
    source_site = "ctc-research"
    if site == source_site:
        print("Cannot sync with itself.")
        return
    source_file = Path(source_site) / "assets/js/modules/auth.py"
    target_file = Path(site) / "assets/js/modules/auth.py"
    if not source_file.exists():
        print(f"Source file {source_file} does not exist.")
        return
    if target_file.exists():
        diff = subprocess.run(f"diff -u {source_file} {target_file}", shell=True, capture_output=True)
        if diff.stdout:
            print("Differences found:")
            print(diff.stdout.decode()[:500])
            choice = input("Overwrite target? (y/n): ").strip().lower()
            if choice == 'y':
                target_file.write_text(source_file.read_text())
                log_change(f"Overwrote {target_file} from {source_site}", site)
                print("✅ Synced.")
            else:
                print("Skipped.")
        else:
            print("Files are identical.")
    else:
        print(f"Target file does not exist. Copying from {source_site}...")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(source_file.read_text())
        log_change(f"Created {target_file} from {source_site}", site)
        print("✅ Created.")

def find_file_across_websites(rel_path: str):
    """Check which websites contain a given relative file."""
    websites = ENV.get('WEBSITES', 'ctc-research lms-demo vresume').split()
    found = []
    for site in websites:
        p = Path(site) / rel_path
        if p.exists():
            found.append(site)
    print(f"File '{rel_path}' exists in: {', '.join(found) if found else 'none'}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List available tasks")
    parser.add_argument("--task", help="Run a specific task by name")
    parser.add_argument("--interactive", action="store_true", help="Interactive resolution (choose analysis/code/doc)")
    parser.add_argument("--sync", help="Sync a website (e.g., lms-demo)")
    parser.add_argument("--find-file", help="Check which websites contain a file")
    args = parser.parse_args()

    if args.list:
        tasks = list_tasks()
        print("Available tasks:")
        for t in tasks:
            print(f"  {t}")
    elif args.task:
        run_task(args.task, interactive=args.interactive)
    elif args.sync:
        sync_website(args.sync)
    elif args.find_file:
        find_file_across_websites(args.find_file)
    else:
        print("No action specified. Use --list, --task, --sync, or --find-file.")

if __name__ == "__main__":
    main()