# -*- coding: utf-8 -*-
"""
POS Full Server — Django-native entry point (django-bolt + django-fusion).

Single entry point serving the Django stack:

* Django management CLI — when launched with a Django subcommand
  (``runserver``, ``migrate``, ``makemigrations``, ``check``, ``shell``,
  ``collectstatic``, ``createsuperuser``, ``seed_demo``), it delegates to
  Django's management CLI.
* ASGI server (default) — launches ``daphne`` on ``asgi:application``,
  which serves Django HTTP, django-bolt, django-fusion components, and
  Django Channels WebSockets (replaces the former Robyn async server).

The former Robyn server (``routes/``, ``middleware/``, ``handlers.py``) is
deprecated and is no longer registered at startup; it is kept only for
reference and the django-fusion Robyn plugin.

Architecture:
    server.py  (thin entry point: manage() + daphne asgi:application)
        └── asgi.py                (ProtocolTypeRouter → HTTP + Channels WS)
            └── configs/urls.py    (Django views, django-bolt, ninja, admin)
                ├── views_django.py  (migrated Robyn routes → Django views)
                ├── bolt_api.py      (django-bolt high-performance API)
                └── fusion_views.py  (django-fusion fragment renders)

Database:  restaurant.db (Django ORM via ``configs``)

Usage:
    python server.py runserver 0.0.0.0:8766   # Django dev server
    python server.py --port 8766              # ASGI (daphne) server
    python server.py migrate                  # Apply migrations
    python server.py --version                # Show version
    daphne -b 0.0.0.0 -p 8766 asgi:application  # Direct ASGI

Full docs: projects/formints/docs/FORMINT_ARCHITECTURE.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Path setup — ensure server dir is importable
_PATH = Path(__file__).resolve().parent
if str(_PATH) not in sys.path:
    sys.path.insert(0, str(_PATH))

# Version metadata. Module-scope import so PyInstaller bundles it (PyInstaller's
# modulegraph silently drops dunder-named modules, so this is ``about``).
import about  # noqa: F401  (used below)

# Fast-path: --version does not require Django bootstrap
if "--version" in sys.argv:
    print(f"{about.__title_full__} v{about.__version__}")
    sys.exit(0)

# ── Django management entry (runserver, migrate, makemigrations, …) ──────────
_DJANGO_MANAGEMENT_SUBCOMMANDS = frozenset({
    "runserver",
    "migrate",
    "makemigrations",
    "showmigrations",
    "check",
    "shell",
    "collectstatic",
    "createsuperuser",
    "seed_demo",
})


def manage() -> None:
    """Run Django's management CLI (``runserver``, ``migrate``, …)."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
    from django.core.management import execute_from_command_line

    execute_from_command_line(["formint-backend", *sys.argv[1:]])


def _run_asgi(host: str, port: int) -> None:
    """Run the Django ASGI application via daphne (HTTP + Channels WS)."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
    from daphne.cli import CommandLineInterface

    # daphne's CommandLineInterface.run() parses the arg list directly (it is
    # invoked by the console entry point as ``run(sys.argv[1:])``), so the
    # program name must NOT be included — otherwise "daphne" is consumed as the
    # ``application`` positional and ``asgi:application`` is left unrecognized.
    CommandLineInterface().run(
        ["-b", host, "-p", str(port), "asgi:application"]
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="POS Full Server — Django (django-bolt + django-fusion)"
    )
    p.add_argument("--host", default=os.environ.get("POS_FULL_HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.environ.get("POS_FULL_PORT", "8766")))
    p.add_argument("--version", action="store_true")
    return p.parse_args()


def main() -> None:
    """Start the Django ASGI server (default) or show version."""
    args = _parse_args()
    if args.version:
        from about import __title_full__, __version__
        print(f"{__title_full__} v{__version__}")
        return
    _run_asgi(args.host, args.port)


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] in _DJANGO_MANAGEMENT_SUBCOMMANDS:
        manage()
        sys.exit(0)
    main()
