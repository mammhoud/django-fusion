"""
Management command to process pending items in the POS Cloud sync queue.

Processes ``SyncQueueItem`` rows whose ``next_retry_at`` has passed,
attempting delivery via the WebSocket broker with exponential backoff.

Usage::

    # One-shot: process up to 100 pending items
    python manage.py process_sync_queue

    # One-shot with custom batch limit
    python manage.py process_sync_queue --limit 200

    # Continuous loop (for supervisor/docker): process every 30 seconds
    python manage.py process_sync_queue --loop --interval 30
"""

from __future__ import annotations

import logging
import time

from django.core.management.base import BaseCommand

logger = logging.getLogger("pos.sync_queue.command")


class Command(BaseCommand):
    help = "Process pending items in the POS Cloud sync queue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum number of items to process per cycle (default: 50).",
        )
        parser.add_argument(
            "--loop",
            action="store_true",
            default=False,
            help="Run in a continuous loop instead of one-shot.",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Seconds between cycles in loop mode (default: 30).",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        loop = options["loop"]
        interval = options["interval"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync queue processor started (limit={limit}, "
                f"mode={'loop' if loop else 'one-shot'}"
                f"{f', interval={interval}s' if loop else ''})"
            )
        )

        if loop:
            self._run_loop(limit, interval)
        else:
            processed = self._process_once(limit)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Processed {processed} queue item(s) in one shot."
                )
            )

    def _run_loop(self, limit: int, interval: int) -> None:
        """Run the queue processor in a continuous loop."""
        import signal
        import sys

        running = True

        def _shutdown(signum, frame):
            nonlocal running
            running = False
            self.stdout.write(self.style.WARNING("Shutdown signal received — stopping..."))

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        total_processed = 0
        cycle = 0

        while running:
            cycle += 1
            try:
                processed = self._process_once(limit)
                total_processed += processed
                self.stdout.write(
                    f"  Cycle #{cycle}: processed {processed} items "
                    f"(total: {total_processed})"
                )
            except Exception as exc:
                logger.exception("Cycle #%d failed: %s", cycle, exc)
                self.stderr.write(
                    self.style.ERROR(f"Cycle #{cycle} failed: {exc}")
                )

            if not running:
                break

            # Sleep in short intervals so SIGINT is responsive
            for _ in range(interval):
                if not running:
                    break
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync queue processor stopped. "
                f"Total cycles: {cycle}, total processed: {total_processed}"
            )
        )

    def _process_once(self, limit: int) -> int:
        """Run one processing cycle and return the number of items processed."""
        from apps.domain.sync_queue import sync_queue

        processed = sync_queue.process_pending_items(limit=limit)

        # Log summary at INFO level
        if processed > 0:
            logger.info("Sync queue: processed %d item(s)", processed)

        return processed
