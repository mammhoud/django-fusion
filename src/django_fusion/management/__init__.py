"""
Django Fusion management module.

This module provides base management command classes and utilities
for creating custom Django management commands with structured logging
and consistent output formatting.

Classes:
    BaseCommand: Extended management command with structured logging support.

Usage::

    from django_fusion.management import BaseCommand

    class Command(BaseCommand):
        help = "My custom command"

        def handle(self, *args, **options):
            self.log_info("Starting command...")
"""
