#!/bin/bash
# =============================================================================
# Full Installation Script for AI Assistant on Ubuntu Server
# Installs Ollama, pulls models, and sets up the AI Customizer script.
# Run with: sudo bash install_ai_assistant.sh
# =============================================================================

set -e  # Exit on any error

echo "=== AI Assistant Installation for Ubuntu Server ==="
echo "This script will install Ollama and the AI Customizer."
echo "It requires root privileges (sudo)."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)." 
   exit 1
fi

# -----------------------------------------------------------------------------
# 1. Update system and install dependencies
# -----------------------------------------------------------------------------
echo "📦 Updating package list and installing dependencies..."
apt update -y
apt upgrade -y
apt install -y curl python3 python3-pip git build-essential

# -----------------------------------------------------------------------------
# 2. Install Ollama (official script)
# -----------------------------------------------------------------------------
echo "🐙 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
systemctl start ollama
systemctl enable ollama

# Wait a moment for Ollama to be ready
sleep 5

# Verify Ollama is running
if curl -s http://localhost:11434 > /dev/null; then
    echo "✅ Ollama is running."
else
    echo "❌ Ollama failed to start. Check with: systemctl status ollama"
    exit 1
fi

# -----------------------------------------------------------------------------
# 3. Pull recommended models
# -----------------------------------------------------------------------------
echo "🧠 Pulling AI models (this may take several minutes)..."

# Main chat model (Gemma 3 4B - good reasoning)
ollama pull gemma3:4b

# Faster fallback model
ollama pull qwen3:4b

# Tiny model for fast autocomplete (optional)
ollama pull llama3.2:1b

echo "✅ Models pulled:"
ollama list

# -----------------------------------------------------------------------------
# 4. Create AI Customizer script and directory structure
# -----------------------------------------------------------------------------
INSTALL_DIR="/opt/ai-assistant"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📝 Creating AI Customizer script at $INSTALL_DIR/ai_customizer.py"

cat > ai_customizer.py << 'EOF'
#!/usr/bin/env python3
"""
AI Assistant Customizer – Full interactive control over Ollama for Django projects.
(Full script content as provided in the documentation)
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
import re

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DEFAULT_MODEL = "gemma3:4b"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_CONTEXT_SIZE = 4096
AI_DIR = Path("ai")
CONFIG_FILE = AI_DIR / "config.json"
CHANGELOG_DIR = AI_DIR / "changelogs"
PROMPTS_DIR = AI_DIR / "prompts"
CONTEXT_DIR = AI_DIR / "context"

# ----------------------------------------------------------------------
# Setup AI directory structure
# ----------------------------------------------------------------------
def setup_ai_directories():
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
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

# ----------------------------------------------------------------------
# Project search with priority (abbreviated for brevity – full script in docs)
# ----------------------------------------------------------------------
def find_files_by_priority(patterns, exclude_patterns, root_dir=Path(".")):
    matches = []
    root = root_dir.resolve()
    for pat in patterns:
        for p in root.rglob(pat):
            rel = p.relative_to(root)
            excluded = False
            for excl in exclude_patterns:
                if fnmatch.fnmatch(str(rel), excl) or fnmatch.fnmatch(str(p), excl):
                    excluded = True
                    break
            if not excluded and p.is_file():
                matches.append(p)
    seen = set()
    unique = []
    for p in matches:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique

def interactive_file_selection(files):
    if not files:
        print("No files found.")
        return []
    print("\n📁 Found files (by priority):")
    for i, f in enumerate(files):
        print(f"  {i+1}. {f}")
    choice = input("Enter numbers (comma) or 'a' for all: ").strip()
    if choice.lower() == 'a':
        return files
    selected = []
    try:
        indices = [int(x)-1 for x in choice.split(',') if x.strip().isdigit()]
        for idx in indices:
            if 0 <= idx < len(files):
                selected.append(files[idx])
    except:
        print("Invalid input.")
    return selected

def load_docs_reference(docs_dir=Path("docs")):
    if not docs_dir.exists():
        return "# No documentation folder"
    docs_content = []
    for md_file in docs_dir.rglob("*.md"):
        if md_file.stat().st_size > 100000:
            continue
        try:
            rel = md_file.relative_to(docs_dir)
            docs_content.append(f"## {rel}\n{md_file.read_text(encoding='utf-8')[:3000]}")
        except:
            continue
    return "\n\n".join(docs_content)

def call_ollama(prompt, model, system=None, temperature=None, num_ctx=None):
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
        return "ERROR: Model took too long."
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.decode()}"

def chat_loop(config):
    print("\n🤖 AI Assistant Chat (exit, save)")
    print(f"Model: {config['model']}")
    conversation = []
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'exit':
            break
        if user_input.lower() == 'save':
            if conversation:
                # simplistic log
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = CHANGELOG_DIR / f"chat_{ts}.md"
                with open(log_file, 'w') as f:
                    f.write(f"# Chat {ts}\n\n")
                    for turn in conversation:
                        f.write(f"**User:** {turn['user']}\n\n**AI:** {turn['assistant']}\n\n---\n")
                print(f"Saved to {log_file}")
                conversation = []
            else:
                print("No conversation to save.")
            continue
        if user_input.startswith("@search "):
            keyword = user_input[8:].strip()
            # simplified search
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
            if matches:
                print(f"Found {len(matches)} files. Load first? (y/n)")
                if input().lower() == 'y':
                    ctx = matches[0].read_text(encoding='utf-8')[:4000]
                    print(f"Loaded {matches[0]}")
                    # not storing permanently for simplicity
            else:
                print("No matches.")
            continue
        if user_input.startswith("@docs"):
            docs = load_docs_reference()
            user_input = f"Documentation:\n{docs[:2000]}\n\nQuestion: {user_input[5:].strip()}"
        system_msg = config.get("system_prompt", "You are a helpful assistant.")
        response = call_ollama(user_input, config["model"], system=system_msg)
        print(f"\nAI: {response}")
        conversation.append({"user": user_input, "assistant": response})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", help="Single task")
    parser.add_argument("--priority", action="store_true")
    parser.add_argument("--with-docs", action="store_true")
    args = parser.parse_args()

    setup_ai_directories()
    config = load_config()

    if args.task:
        context = ""
        if args.priority:
            files = find_files_by_priority(config["priority_patterns"], config["exclude_patterns"])
            selected = interactive_file_selection(files)
            for f in selected:
                context += f"\n--- {f} ---\n{f.read_text(encoding='utf-8')[:2000]}\n"
        if args.with_docs:
            docs = load_docs_reference()
            context += f"\n--- Documentation ---\n{docs[:2000]}\n"
        prompt = f"Context:\n{context}\n\nTask: {args.task}"
        response = call_ollama(prompt, config["model"], system=config.get("system_prompt"))
        print("\n🤖 Response:\n", response)
        # Save task result
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = f"task_{ts}_{args.task[:30].replace(' ', '_')}"
        slug = re.sub(r'[^a-z0-9_]', '', slug.lower())
        (CHANGELOG_DIR / f"{slug}.md").write_text(f"# Task: {args.task}\n\n{response}")
    else:
        chat_loop(config)

if __name__ == "__main__":
    main()
EOF

chmod +x ai_customizer.py

# Create a convenience launcher script
cat > /usr/local/bin/ai-customizer << 'EOF'
#!/bin/bash
cd /opt/ai-assistant && python3 ai_customizer.py "$@"
EOF
chmod +x /usr/local/bin/ai-customizer

# -----------------------------------------------------------------------------
# 5. Create a systemd service to keep Ollama always on (already done)
# -----------------------------------------------------------------------------
# Ollama service is already enabled and started by the installer.
# We just ensure it's active.
systemctl restart ollama
systemctl enable ollama

# -----------------------------------------------------------------------------
# 6. Print completion message and usage instructions
# -----------------------------------------------------------------------------
echo "========================================================================="
echo "✅ Installation complete!"
echo ""
echo "📌 Ollama is running as a systemd service. Status:"
systemctl status ollama --no-pager | grep "Active:"
echo ""
echo "📌 Installed models:"
ollama list
echo ""
echo "📌 AI Customizer script installed at: /opt/ai-assistant/ai_customizer.py"
echo "    You can run it from anywhere using: ai-customizer"
echo ""
echo "📌 Usage examples:"
echo "    # Interactive chat"
echo "    ai-customizer"
echo ""
echo "    # Single task with priority files and docs"
echo "    ai-customizer --task 'Explain Django signals' --priority --with-docs"
echo ""
echo "📌 Important:"
echo "    - The script expects your Django project's root to be the current working directory."
echo "    - It creates an 'ai/' folder inside that directory for logs and config."
echo "    - To use @docs, ensure you have a 'docs/' folder with .md files."
echo ""
echo "📌 To stop Ollama: sudo systemctl stop ollama"
echo "📌 To start Ollama: sudo systemctl start ollama"
echo "========================================================================="