#!/usr/bin/env python3
"""
Unified entry point for VResume website.

Supports:
1. Django management commands via uv
2. Direct server execution
3. Website-specific environment setup

Usage with uv:
  uv run vresume check
  uv run vresume migrate
  uv run vresume runserver
  uv run vresume server  # Start ASGI/WSGI server

Usage directly:
  python -m vresume check
  python -m vresume migrate
  python -m vresume server
"""
import os
import sys
import subprocess
from pathlib import Path

# Set website identifier
SITE = "vresume"
os.environ.setdefault("DJANGO_SITE", SITE)
os.environ.setdefault("DJANGO_WEBSITE", SITE)
os.environ.setdefault("WEBSITE", SITE)
os.environ.setdefault("PROJECT_PATH", SITE)

# Add workspace to path
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Add website directory to path
site_dir = Path(__file__).resolve().parent
if str(site_dir) not in sys.path:
    sys.path.insert(0, str(site_dir))

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")


def run_django_command(*args):
    """Run Django management command."""
    from django.core.management import execute_from_command_line
    # Prepend script name for Django
    django_args = [sys.argv[0]] + list(args)
    execute_from_command_line(django_args)


def run_server():
    """Start the ASGI/WSGI server."""
    from server import application
    
    server_type = os.environ.get("SERVER_TYPE", "asgi").lower()
    port = int(os.environ.get("PORT", 8002))
    host = os.environ.get("HOST", "0.0.0.0")
    
    if server_type == "asgi":
        import uvicorn
        uvicorn.run(
            application,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    else:
        # For WSGI, we would use a different server like gunicorn
        print(f"WSGI server mode not implemented directly. Use gunicorn instead.")
        sys.exit(1)


def run_uv_command(*args):
    """Run command via uv in the workspace context."""
    cmd = ["uv", "run", "--project", str(workspace_root)] + list(args)
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main():
    args = sys.argv[1:]
    
    if not args:
        print(f"Usage: python -m vresume <command> [args...]")
        print(f"       uv run vresume <command> [args...]")
        print("\nCommands:")
        print("  check, migrate, makemigrations, collectstatic, shell, test")
        print("  runserver [port]  - Django development server")
        print("  server            - Production ASGI/WSGI server")
        print("  manage <command>  - Any Django management command")
        print("  uv <command>      - Run any command via uv in workspace context")
        sys.exit(0)
    
    command = args[0]
    
    # Special commands
    if command == "server":
        run_server()
    elif command == "runserver":
        port = args[1] if len(args) > 1 else "8002"
        run_django_command("runserver", f"0.0.0.0:{port}")
    elif command == "uv":
        run_uv_command(*args[1:])
    elif command == "manage":
        run_django_command(*args[1:])
    else:
        # Standard Django commands
        run_django_command(command, *args[1:])


if __name__ == "__main__":
    main()