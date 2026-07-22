"""
run_campaign_worker management command
=======================================
Start the Temporal workflow worker for the campaigns task queue.

Ported from ``worker.py`` in the project base directory.

Usage:
    uv run python manage.py run_campaign_worker
    uv run python manage.py run_campaign_worker --task-queue my-queue
"""

import asyncio
import sys
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start the Temporal workflow worker for the campaigns task queue"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--task-queue",
            default="campaigns-task-queue",
            help="Temporal task queue name (default: campaigns-task-queue)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        task_queue: str = options["task_queue"]
        temporal_url: str = getattr(settings, "TEMPORAL_SERVER_URL", "localhost:7233")

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Temporal worker on queue '{task_queue}' "
                f"connecting to {temporal_url}"
            )
        )

        try:
            asyncio.run(self._run_worker(task_queue, temporal_url))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Worker stopped by user."))
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(self.style.ERROR(f"Worker failed: {exc}"))
            sys.exit(1)

    async def _run_worker(self, task_queue: str, temporal_url: str) -> None:
        """Connect to Temporal and run the campaigns worker."""
        try:
            from campaigns import activities, workflows
            from temporalio.client import Client
            from temporalio.worker import Worker
        except ImportError as exc:
            self.stderr.write(
                self.style.ERROR(
                    f"Required package not available: {exc}. "
                    "Ensure 'temporalio' and the 'campaigns' app are installed."
                )
            )
            sys.exit(1)

        client = await Client.connect(temporal_url)

        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[workflows.EmailCampaignWorkflow],
            activities=[
                activities.send_email_activity,
                activities.publish_progress_activity,
            ],
        )

        self.stdout.write(f"Worker starting (task queue: {task_queue})...")
        await worker.run()
