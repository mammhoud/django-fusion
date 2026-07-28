
#!/usr/bin/env python3
"""
AI Assistant Customizer – Full interactive control over Ollama for Django projects.
Creates an `ai/` directory, searches your codebase with priority, references docs,
and logs every change as a snake_case markdown changelog.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import fnmatch

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DEFAULT_MODEL = "gemma3:4b"          # or "qwen3:4b", "qwen2.5-coder:7b", etc.
DEFAULT_TEMPERATURE = 0.7
DEFAULT_CONTEXT_SIZE = 4096
AI_DIR = Path("ai")                  # root for all AI‑generated files
CONFIG_FILE = AI_DIR / "config.json"
CHANGELOG_DIR = AI_DIR / "changelogs"
PROMPTS_DIR = AI_DIR / "prompts"
CONTEXT_DIR = AI_DIR / "context"

# ----------------------------------------------------------------------
# Setup AI directory structure
# ----------------------------------------------------------------------
def setup_ai_directories():
    """Create the ai/ directory and its subfolders if missing."""
    AI_DIR.mkdir(exist_ok=True)
    CHANGELOG_DIR.mkdir(exist_ok=True)
    PROMPTS_DIR.mkdir(exist_ok=True)
    CONTEXT_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        default_config = {
            "model": DEFAULT_MODEL,
            "temperature": DEFAULT_TEMPERATURE,
            "num_ctx": DEFAULT_CONTEXT_SIZE,
            "system_prompt": "You are a senior Django developer. Be concise, use best practices, and explain only when asked.",
            "priority_patterns": ["*.py", "*/models.py", "*/views.py", "*/serializers.py"],
            "exclude_patterns": ["*/migrations/*", "*/__pycache__/*", ".git/*", "ai/*", "docs/50_reports/*"]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"Created default config at {CONFIG_FILE}")

def load_config() -> dict:
    """Load configuration from ai/config.json."""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# ----------------------------------------------------------------------
# Project search with priority
# ----------------------------------------------------------------------
def find_files_by_priority(patterns: List[str], exclude_patterns: List[str], root_dir: Path = Path(".")) -> List[Path]:
    """
    Return list of files matching any of the patterns (glob style), excluding those
    that match any exclude_patterns. Results are ordered by "priority" – here we
    simply give higher priority to files that appear earlier in the patterns list.
    """
    matches = []
    root = root_dir.resolve()
    for pat in patterns:
        for p in root.rglob(pat):
            rel = p.relative_to(root)
            # check exclusions
            excluded = False
            for excl in exclude_patterns:
                if fnmatch.fnmatch(str(rel), excl) or fnmatch.fnmatch(str(p), excl):
                    excluded = True
                    break
            if not excluded and p.is_file():
                matches.append(p)
    # remove duplicates (if a file matches multiple patterns) while preserving order
    seen = set()
    unique = []
    for p in matches:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique

def interactive_file_selection(files: List[Path]) -> List[Path]:
    """Let user choose which files to include as context."""
    if not files:
        print("No files found matching priority patterns.")
        return []
    print("\n📁 Found the following files (by priority):")
    for i, f in enumerate(files):
        print(f"  {i+1}. {f}")
    print("  a. Select all")
    print("  q. Cancel")
    choice = input("\nEnter numbers separated by commas (e.g., 1,3,5) or 'a' for all: ").strip()
    if choice.lower() == 'q':
        return []
    if choice.lower() == 'a':
        return files
    selected = []
    try:
        indices = [int(x.strip()) - 1 for x in choice.split(',') if x.strip().isdigit()]
        for idx in indices:
            if 0 <= idx < len(files):
                selected.append(files[idx])
    except:
        print("Invalid input. No files selected.")
    return selected

# ----------------------------------------------------------------------
# Documentation reference
# ----------------------------------------------------------------------
def load_docs_reference(docs_dir: Path = Path("docs")) -> str:
    """Load all markdown files from docs/ (or subdirs) as context."""
    if not docs_dir.exists():
        return "# No documentation folder found"
    docs_content = []
    for md_file in docs_dir.rglob("*.md"):
        # skip huge or temp files
        if md_file.stat().st_size > 100_000:
            continue
        try:
            rel = md_file.relative_to(docs_dir)
            docs_content.append(f"## {rel}\n{md_file.read_text(encoding='utf-8')[:3000]}")
        except:
            continue
    return "\n\n".join(docs_content)

# ----------------------------------------------------------------------
# Ollama interaction with full tweaks
# ----------------------------------------------------------------------
def call_ollama(prompt: str, model: str, system: str = None, temperature: float = None,
                num_ctx: int = None, stream: bool = False) -> str:
    """
    Send a chat request to Ollama using the `ollama run` command.
    """
    full_prompt = []
    if system:
        full_prompt.append(f"System: {system}")
    full_prompt.append(f"User: {prompt}")
    final_prompt = "\n\n".join(full_prompt)

    cmd = ["ollama", "run", model]
    try:
        result = subprocess.run(cmd, input=final_prompt.encode('utf-8'),
                                capture_output=True, check=True, timeout=120)
        return result.stdout.decode('utf-8').strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Model took too long to respond. Try a smaller model or reduce context."
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.decode()}"

def chat_loop(config: dict):
    """Interactive chat with user, logging each turn."""
    print("\n🤖 AI Assistant Chat (type 'exit' to stop, 'save' to log conversation)")
    print(f"Using model: {config['model']}")
    conversation = []
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'exit':
            break
        if user_input.lower() == 'save':
            if conversation:
                log_conversation(conversation, config)
                print("Conversation saved to changelogs.")
            else:
                print("No conversation to save.")
            continue
        if user_input.startswith("@search "):
            keyword = user_input[8:].strip()
            search_files_by_keyword(keyword, config)
            continue
        if user_input.startswith("@docs"):
            docs_content = load_docs_reference()
            user_input = f"Reference documentation:\n{docs_content[:2000]}\n\nUser question: {user_input[5:].strip()}"
        system_msg = config.get("system_prompt", "You are a helpful Django expert.")
        response = call_ollama(user_input, config["model"], system=system_msg,
                               temperature=config.get("temperature"), num_ctx=config.get("num_ctx"))
        print(f"\nAI: {response}")
        conversation.append({"user": user_input, "assistant": response, "timestamp": datetime.now().isoformat()})

def search_files_by_keyword(keyword: str, config: dict):
    """Search project files containing keyword, let user pick one, then feed its content to AI."""
    patterns = config.get("priority_patterns", ["*.py"])
    exclude = config.get("exclude_patterns", [])
    files = find_files_by_priority(patterns, exclude)
    matches = []
    for f in files:
        try:
            if keyword.lower() in f.read_text(encoding='utf-8', errors='ignore').lower():
                matches.append(f)
        except:
            continue
    if not matches:
        print(f"No files contain '{keyword}'.")
        return
    print(f"\n🔍 Found {len(matches)} files containing '{keyword}':")
    for i, m in enumerate(matches):
        print(f"  {i+1}. {m}")
    choice = input("Enter number to load file content into AI context (or 0 to cancel): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(matches):
        selected = matches[int(choice)-1]
        content = selected.read_text(encoding='utf-8')
        ctx_file = CONTEXT_DIR / f"temp_{selected.stem}.txt"
        ctx_file.write_text(f"File: {selected}\n\n```\n{content[:4000]}\n```")
        print(f"Loaded {selected} into context. Use '@context' in chat to include it.")
    else:
        print("Cancelled.")

def log_conversation(conversation: list, config: dict):
    """Save conversation as a markdown changelog with snake_case name."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    first_msg = conversation[0]["user"][:50].replace(" ", "_").replace("/", "_")
    slug = f"chat_{timestamp}_{first_msg}"
    slug = re.sub(r'[^a-z0-9_]', '', slug.lower())
    filename = CHANGELOG_DIR / f"{slug}.md"
    content = f"""# AI Conversation Log
**Model**: {config['model']}
**Date**: {datetime.now().isoformat()}
**System prompt**: {config.get('system_prompt', 'default')}

## Messages
"""
    for turn in conversation:
        content += f"\n### User ({turn['timestamp']})\n{turn['user']}\n\n### Assistant\n{turn['assistant']}\n\n"
    filename.write_text(content)
    print(f"Saved conversation to {filename}")

# ----------------------------------------------------------------------
# Main CLI with options
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AI Assistant Customizer for Django projects")
    parser.add_argument("--task", type=str, help="Single task to execute (e.g., 'explain models.py', 'refactor views')")
    parser.add_argument("--priority", action="store_true", help="Interactively select files by priority before task")
    parser.add_argument("--with-docs", action="store_true", help="Include documentation as context")
    args = parser.parse_args()

    setup_ai_directories()
    config = load_config()

    if args.task:
        context = ""
        if args.priority:
            files = find_files_by_priority(config["priority_patterns"], config["exclude_patterns"])
            selected = interactive_file_selection(files)
            for f in selected:
                context += f"\n--- File: {f} ---\n{f.read_text(encoding='utf-8')[:2000]}\n"
        if args.with_docs:
            docs = load_docs_reference()
            context += f"\n--- Documentation ---\n{docs[:2000]}\n"
        prompt = f"Context:\n{context}\n\nTask: {args.task}"
        response = call_ollama(prompt, config["model"], system=config.get("system_prompt"))
        print("\n🤖 AI Response:\n", response)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = f"task_{timestamp}_{args.task[:30].replace(' ', '_')}"
        slug = re.sub(r'[^a-z0-9_]', '', slug.lower())
        (CHANGELOG_DIR / f"{slug}.md").write_text(f"# Task: {args.task}\n\n{response}")
    else:
        chat_loop(config)

if __name__ == "__main__":
    import re
    main()
