"""Shared utilities for AI task runner."""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def load_env() -> dict:
    """Load .env from project root (two levels up)."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k] = v
    return env_vars

ENV = load_env()
AI_DIR = Path(ENV.get('AI_DIR', 'ai'))
DOCS_AI_DIR = Path(ENV.get('DOCS_AI_DIR', 'docs/ai'))
TASKS_DIR = DOCS_AI_DIR / 'tasks'
CHANGELOG_DIR = AI_DIR / 'changelogs'

def call_ollama(prompt: str, model: str = None, system: str = None) -> str:
    """Send a prompt to Ollama and return the response."""
    model = model or ENV.get('DEFAULT_MODEL', 'gemma3:4b')
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
    except Exception as e:
        return f"ERROR: {str(e)}"

def log_change(message: str, website: str = None):
    """Log a change to the daily changelog."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = CHANGELOG_DIR / f"sync_{today}.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(f"- {datetime.now().isoformat()} | {website or 'GLOBAL'}: {message}\n")