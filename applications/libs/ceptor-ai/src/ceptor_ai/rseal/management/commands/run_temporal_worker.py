"""
Django management command to run Temporal worker.

Usage:
    python manage.py run_temporal_worker
"""

import asyncio
import warnings

from django.core.management.base import BaseCommand

logger = None


class Command(BaseCommand):
    """Run Temporal worker."""

    help = "Run Temporal worker for async workflow processing"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--task-queue",
            type=str,
            default="default-tasks",
            help="Temporal task queue name (default: default-tasks)",
        )
        parser.add_argument(
            "--temporal-address",
            type=str,
            default="localhost:7233",
            help="Temporal server address (default: localhost:7233)",
        )

    def handle(self, *args, **options):
        """Run the Temporal worker."""
        task_queue = options["task_queue"]
        temporal_address = options["temporal_address"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Temporal worker on queue '{task_queue}' "
                f"connecting to {temporal_address}"
            )
        )

        asyncio.run(self.run_worker(task_queue, temporal_address))

    async def run_worker(self, task_queue: str, temporal_address: str):
        """
        Run the worker asynchronously.

        Args:
            task_queue: Name of the task queue to listen to
            temporal_address: Address of the Temporal server
        """
        global logger
        import structlog

        logger = structlog.get_logger(__name__)

        # Import temporal components
        from temporalio.client import Client
        from temporalio.worker import Worker

        from ceptor_ai.workflows.temporal.activities import (
            process_user_activity,
            send_email_activity,
        )
        from ceptor_ai.workflows.temporal.workflows import (
            BatchProcessingWorkflow,
            UserOnboardingWorkflow,
        )

        # Connect to Temporal server
        client = await Client.connect(temporal_address)

        # Create worker with workflows and activities
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[
                UserOnboardingWorkflow,
                BatchProcessingWorkflow,
            ],
            activities=[
                send_email_activity,
                process_user_activity,
            ],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Worker started successfully. Listening on queue: {task_queue}"
            )
        )
        self.stdout.write("Press Ctrl+C to stop the worker...")

        # Run the worker
        await worker.run()
