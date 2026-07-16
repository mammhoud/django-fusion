#!/usr/bin/env python3
"""Verify shared-worker processes tasks from each configured Dramatiq queue.

This script enqueues one Dramatiq message per queue
(default, shared, email, ctc-research, lms-demo, vresume) using the same
broker the running shared-worker consumes from. It bypasses loading the full
Django settings stack, which currently has a pre-existing import issue in
ctc-research/settings.py.

The worker must already know the actor (`shared.content.users_count`) from
its startup imports; we only need to enqueue a valid message with that
actor name and the right queue.
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid

import dramatiq
from dramatiq.brokers.redis import RedisBroker

REDIS_URL = os.environ.get("REDIS_URL", "redis://default-redis:6379/1")
QUEUES = [
    "default",
    "shared",
    "email",
    "ctc-research",
    "lms-demo",
    "vresume",
]


def main() -> int:
    print(f"Connecting to broker at {REDIS_URL}...")
    broker = RedisBroker(url=REDIS_URL)
    dramatiq.set_broker(broker)

    print("Enqueuing test tasks to shared-worker queues...")
    for queue in QUEUES:
        try:
            # Build a minimal Dramatiq message for the actor the worker knows.
            message = dramatiq.Message(
                queue_name=queue,
                actor_name="shared.content.users_count",
                args=[],
                kwargs={"website": "ctc-research"},
                options={},
                message_id=str(uuid.uuid4()),
                message_timestamp=int(time.time() * 1000),
            )
            broker.enqueue(message, delay=0)
            print(f"  ✓ queued on {queue}: {message.message_id}")
        except Exception as exc:
            print(f"  ✗ failed on {queue}: {exc}", file=sys.stderr)
            return 1

    print("\nAll test tasks enqueued. Check shared-worker logs for processing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
