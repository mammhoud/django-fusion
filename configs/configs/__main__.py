#!/usr/bin/env python3
"""
🎯 Django Project CLI Entry Point
=================================
Command-line interface entry point for Django management and sync operations.
Supports both direct command execution and Fire-based CLI.
"""

import sys


# ====================================
# 🎯 Direct Command Support
# ====================================
def run_direct_command():
    """Run direct commands for backward compatibility."""
    if len(sys.argv) < 2:
        # No command, show help
        from configs.cli import MainCLI
        MainCLI().help()
        return
    
    command = sys.argv[1]
    
    # Django commands that need direct execution
    django_commands = ['dev', 'runserver', 'gunicorn', 'uvicorn', 'waitress']
    
    if command in django_commands:
        # Run Django command
        from configs.cli import DjangoCLI
        cli = DjangoCLI()
        
        if command == 'dev':
            cli.dev(*sys.argv[2:])
        elif hasattr(cli, command):
            getattr(cli, command)(*sys.argv[2:])
        else:
            print(f"❌ Unknown command: {command}")
    else:
        # Use Fire for other commands
        import fire

        from configs.cli import MainCLI
        fire.Fire(MainCLI)

# ====================================
# 🎯 Main Entry Point
# ====================================
if __name__ == "__main__":
    # Check if we should use direct execution or Fire
    if len(sys.argv) > 1 and sys.argv[1] in ['dev', 'runserver', 'gunicorn', 'uvicorn', 'waitress']:
        run_direct_command()
    else:
        # Use Fire CLI
        import fire

        from configs.cli import MainCLI
        fire.Fire(MainCLI)