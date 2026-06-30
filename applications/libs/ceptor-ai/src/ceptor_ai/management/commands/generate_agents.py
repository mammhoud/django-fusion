from __future__ import annotations

from pathlib import Path
from django.core.management.base import BaseCommand
from ceptor_ai.agents import generate_agent_configs

class Command(BaseCommand):
    help = "Generate .kilo/agent component configs."
    def add_arguments(self, parser):
        parser.add_argument("--root", default=".")
        parser.add_argument("--model", default="gpt-5.5")
        parser.add_argument("--cache-ttl", type=int, default=300)
    def handle(self, *args, **options):
        written = generate_agent_configs(Path(options["root"]).resolve(), options["model"], options["cache_ttl"])
        self.stdout.write(self.style.SUCCESS(f"Generated {len(written)} agent configs."))
