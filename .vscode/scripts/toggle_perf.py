#!/usr/bin/env python
import json
import os

def toggle_performance_mode():
    """Toggle between normal and performance modes"""
    settings_file = ".vscode/settings.json"

    with open(settings_file, 'r') as f:
        settings = json.load(f)

    # Toggle key settings
    current_mode = settings.get("_performance_mode", "normal")

    if current_mode == "normal":
        print("🚀 Switching to PERFORMANCE mode...")
        # Performance optimizations
        settings.update({
            "_performance_mode": "performance",
            "editor.formatOnSave": false,
            "editor.codeActionsOnSave": {},
            "ruff.lint.run": "never",
            "python.analysis.typeCheckingMode": "off",
            "files.autoSave": "off",
            "editor.hover.enabled": false
        })
    else:
        print("🎨 Switching to NORMAL mode...")
        # Normal settings
        settings.update({
            "_performance_mode": "normal",
            "editor.formatOnSave": false,  # Still off for speed
            "editor.codeActionsOnSave": {
                "source.fixAll.ruff": "explicit",
                "source.organizeImports.ruff": "explicit"
            },
            "ruff.lint.run": "onSave",
            "python.analysis.typeCheckingMode": "basic",
            "files.autoSave": "off",
            "editor.hover.enabled": true
        })

    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

    print(f"✅ Switched to {settings['_performance_mode'].upper()} mode")

if __name__ == "__main__":
    toggle_performance_mode()